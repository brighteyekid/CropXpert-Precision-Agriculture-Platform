/**
 * CropXpert — Dashboard aggregation API.
 */
import client from './client'

export async function getSummary() {
    const { data } = await client.get('/api/dashboard/summary')
    return data
}
