/**
 * CropXpert — Government schemes API.
 */
import client from './client'

export async function getSchemes(state?: string) {
    const { data } = await client.get('/api/schemes', { params: state ? { state } : {} })
    return data
}

export async function getLoans(state?: string) {
    const { data } = await client.get('/api/schemes/loans', { params: state ? { state } : {} })
    return data
}

export async function calculateEMI(principal: number, rate: number, tenure_months: number) {
    const { data } = await client.post('/api/schemes/emi-calculate', {
        principal,
        rate,
        tenure_months,
    })
    return data
}
