/**
 * CropXpert — useApi hook.
 * Tries the backend first, gracefully falls back to mock data.
 * All dashboard pages use this for data fetching.
 */
import { useState, useEffect, useCallback } from 'react'
import client from '../api/client'

interface UseApiResult<T> {
    data: T
    loading: boolean
    error: string | null
    refetch: () => void
    isLive: boolean  // true if data came from backend
}

/**
 * Generic data-fetching hook with mock fallback.
 * @param endpoint  API path, e.g. '/api/dashboard/summary'
 * @param mockData  Fallback data when backend is unreachable
 * @param transform Optional transformer for API response → component shape
 */
export function useApi<T>(
    endpoint: string,
    mockData: T,
    transform?: (raw: unknown) => T,
): UseApiResult<T> {
    const [data, setData] = useState<T>(mockData)
    const [loading, setLoading] = useState(true)
    const [error, setError] = useState<string | null>(null)
    const [isLive, setIsLive] = useState(false)

    const fetch = useCallback(async () => {
        setLoading(true)
        setError(null)
        try {
            const resp = await client.get(endpoint)
            const result = transform ? transform(resp.data) : resp.data as T
            setData(result)
            setIsLive(true)
        } catch {
            // Backend unreachable — use mock data silently
            setData(mockData)
            setIsLive(false)
        } finally {
            setLoading(false)
        }
    }, [endpoint])

    useEffect(() => { fetch() }, [fetch])

    return { data, loading, error, refetch: fetch, isLive }
}

/**
 * Fire-and-forget POST with mock fallback return.
 */
export async function postApi<T>(
    endpoint: string,
    body: unknown,
    mockResponse: T,
): Promise<{ data: T; isLive: boolean }> {
    try {
        const resp = await client.post(endpoint, body)
        return { data: resp.data as T, isLive: true }
    } catch {
        return { data: mockResponse, isLive: false }
    }
}
