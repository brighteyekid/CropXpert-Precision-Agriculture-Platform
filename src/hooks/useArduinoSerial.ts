import { useState, useRef, useCallback } from 'react'

export function useArduinoSerial() {
    const portRef = useRef<SerialPort | null>(null)
    const readerRef = useRef<ReadableStreamDefaultReader<Uint8Array> | null>(null)
    const [connected, setConnected] = useState(false)
    const [reading, setReading] = useState(false)
    const bufferRef = useRef('')

    const parseSerialLine = useCallback((line: string): Record<string, string> | null => {
        try {
            const data = JSON.parse(line.trim())
            const result: Record<string, string> = {}
            if (data.N !== undefined || data.n !== undefined) result.n = String(data.N ?? data.n)
            if (data.P !== undefined || data.p !== undefined) result.p = String(data.P ?? data.p)
            if (data.K !== undefined || data.k !== undefined) result.k = String(data.K ?? data.k)
            if (data.ph !== undefined || data.pH !== undefined) result.ph = String(data.ph ?? data.pH)
            if (data.moisture !== undefined || data.moist !== undefined) result.moisture = String(data.moisture ?? data.moist)
            if (data.temp !== undefined || data.temperature !== undefined) result.temp = String(data.temp ?? data.temperature)
            if (data.humidity !== undefined) result.humidity = String(data.humidity)
            return Object.keys(result).length > 0 ? result : null
        } catch {
            return null
        }
    }, [])

    const connect = useCallback(async (): Promise<boolean> => {
        if (!('serial' in navigator)) return false
        try {
            const port = await (navigator as any).serial.requestPort({
                filters: [
                    { usbVendorId: 0x2341 },
                    { usbVendorId: 0x1A86 },
                    { usbVendorId: 0x10C4 },
                ],
            })
            await port.open({ baudRate: 9600 })
            portRef.current = port
            setConnected(true)
            return true
        } catch {
            return false
        }
    }, [])

    const startLiveRead = useCallback(async (onData: (values: Record<string, string>) => void) => {
        if (!portRef.current?.readable) return
        setReading(true)
        const decoder = new TextDecoderStream()
        const readableStreamClosed = portRef.current.readable.pipeTo(decoder.writable as any)
        const reader = decoder.readable.getReader()
        readerRef.current = reader as any
        bufferRef.current = ''

        try {
            while (true) {
                const { value, done } = await reader.read()
                if (done) break
                bufferRef.current += value
                const lines = bufferRef.current.split('\n')
                bufferRef.current = lines.pop() || ''
                for (const line of lines) {
                    if (line.trim()) {
                        const parsed = parseSerialLine(line)
                        if (parsed) {
                            onData(parsed)
                        }
                    }
                }
            }
        } catch { /* stream cancelled */ }
        setReading(false)
        try { await readableStreamClosed.catch(() => { }) } catch { /* ignore */ }
    }, [parseSerialLine])

    const stopRead = useCallback(async () => {
        try {
            readerRef.current?.cancel()
            setReading(false)
        } catch { }
    }, [])

    const disconnect = useCallback(async () => {
        try {
            readerRef.current?.cancel()
            await portRef.current?.close()
        } catch { }
        portRef.current = null
        setConnected(false)
    }, [])

    return { connected, reading, connect, startLiveRead, stopRead, disconnect, supported: 'serial' in navigator }
}
