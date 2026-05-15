/**
 * CropXpert — Sensor data API.
 */
import client from './client'

export interface SensorReading {
    nitrogen: number
    phosphorus: number
    potassium: number
    ph: number
    moisture: number
    temperature: number
    humidity?: number
    latitude?: number
    longitude?: number
}

export async function postReading(reading: SensorReading) {
    const { data } = await client.post('/api/sensors/reading', reading)
    return data
}

export async function getHistory(days = 30) {
    const { data } = await client.get('/api/sensors/history', { params: { days } })
    return data
}

export async function getLatest() {
    const { data } = await client.get('/api/sensors/latest')
    return data
}

export function getExportUrl(): string {
    const base = import.meta.env.VITE_API_URL || 'http://localhost:8000'
    const token = localStorage.getItem('cropxpert_token')
    return `${base}/api/sensors/export?token=${token}`
}
