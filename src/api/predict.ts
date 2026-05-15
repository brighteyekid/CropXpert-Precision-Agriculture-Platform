/**
 * CropXpert — Prediction API.
 */
import client from './client'

export interface PredictByReading {
    reading_id: number
}

export interface PredictDirect {
    nitrogen: number
    phosphorus: number
    potassium: number
    ph: number
    moisture: number
    temperature: number
    rainfall: number
}

export async function getPrediction(body: PredictByReading | PredictDirect) {
    const { data } = await client.post('/api/predict', body)
    return data
}
