/**
 * CropXpert — WebSocket hook for live sensor data.
 * Reconnects automatically on disconnect.
 */
import { useEffect, useRef, useCallback, useState } from 'react'

const WS_BASE = (import.meta.env.VITE_API_URL || 'http://localhost:8000')
    .replace('http://', 'ws://')
    .replace('https://', 'wss://')

export interface WSMessage {
    type: 'sensor_update' | 'recommendation_ready' | 'pong'
    data?: Record<string, unknown>
}

export function useWebSocket(onMessage: (msg: WSMessage) => void) {
    const wsRef = useRef<WebSocket | null>(null)
    const reconnectTimerRef = useRef<ReturnType<typeof setTimeout> | undefined>(undefined)
    const [connected, setConnected] = useState(false)

    const connect = useCallback(() => {
        const token = localStorage.getItem('cropxpert_token')
        if (!token) return

        const ws = new WebSocket(`${WS_BASE}/ws/live?token=${token}`)

        ws.onopen = () => {
            setConnected(true)
            // Ping every 30 seconds
            const interval = setInterval(() => {
                if (ws.readyState === WebSocket.OPEN) ws.send('ping')
            }, 30000)
            ws.addEventListener('close', () => clearInterval(interval))
        }

        ws.onmessage = (event) => {
            try {
                const msg = JSON.parse(event.data) as WSMessage
                onMessage(msg)
            } catch {
                // ignore non-JSON messages
            }
        }

        ws.onclose = () => {
            setConnected(false)
            // Auto-reconnect after 3 seconds
            reconnectTimerRef.current = setTimeout(connect, 3000)
        }

        ws.onerror = () => {
            ws.close()
        }

        wsRef.current = ws
    }, [onMessage])

    useEffect(() => {
        connect()
        return () => {
            if (reconnectTimerRef.current) clearTimeout(reconnectTimerRef.current)
            wsRef.current?.close()
        }
    }, [connect])

    return { connected }
}
