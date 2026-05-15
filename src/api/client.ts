/**
 * CropXpert — Axios HTTP client with JWT interceptor.
 */
import axios from 'axios'

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

const client = axios.create({
    baseURL: API_URL,
    headers: { 'Content-Type': 'application/json' },
})

// JWT interceptor
client.interceptors.request.use((config) => {
    const token = localStorage.getItem('cropxpert_token')
    if (token) {
        config.headers.Authorization = `Bearer ${token}`
    }
    return config
})

// Auto-logout on 401
client.interceptors.response.use(
    (response) => response,
    (error) => {
        if (error.response?.status === 401) {
            localStorage.removeItem('cropxpert_token')
            localStorage.removeItem('cropxpert_farmer_id')
        }
        return Promise.reject(error)
    }
)

export default client
