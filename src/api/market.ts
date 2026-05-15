/**
 * CropXpert — Market data API.
 */
import client from './client'

export async function getMSP(crop: string) {
    const { data } = await client.get('/api/market/msp', { params: { crop } })
    return data
}

export async function getMandiPrices(crop: string, district = 'Pune') {
    const { data } = await client.get('/api/market/mandi-prices', { params: { crop, district } })
    return data
}

export async function getMandiTrend(crop: string, days = 90) {
    const { data } = await client.get('/api/market/trend', { params: { crop, days } })
    return data
}

export async function getAllCrops() {
    const { data } = await client.get('/api/market/all-crops')
    return data
}
