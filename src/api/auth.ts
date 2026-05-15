/**
 * CropXpert — Auth API calls.
 */
import client from './client'

export async function sendOTP(mobile: string) {
    const { data } = await client.post('/api/auth/send-otp', { mobile })
    return data
}

export async function verifyOTP(mobile: string, otp: string) {
    const { data } = await client.post('/api/auth/verify-otp', { mobile, otp })
    if (data.access_token) {
        localStorage.setItem('cropxpert_token', data.access_token)
        localStorage.setItem('cropxpert_farmer_id', String(data.farmer_id))
    }
    return data
}

export async function getMe() {
    const { data } = await client.get('/api/auth/me')
    return data
}

export function logout() {
    localStorage.removeItem('cropxpert_token')
    localStorage.removeItem('cropxpert_farmer_id')
}

export function isAuthenticated(): boolean {
    return !!localStorage.getItem('cropxpert_token')
}
