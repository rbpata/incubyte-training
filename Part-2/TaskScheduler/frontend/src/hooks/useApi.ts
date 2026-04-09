import { useState, useCallback } from 'react'
import { apiClient } from '../utils/api'
import type { UseApiState } from '../types/index'

export function useApi<T>() {
  const [state, setState] = useState<UseApiState<T>>({
    data: null,
    loading: false,
    error: null,
  })

  const execute = useCallback(
    async (
      path: string,
      init?: RequestInit & { headers?: Record<string, string> }
    ) => {
      setState({ data: null, loading: true, error: null })

      try {
        const data = await apiClient.request<T>(path, init)
        setState({ data, loading: false, error: null })
        return data
      } catch (err) {
        const errorMessage = err instanceof Error ? err.message : 'An error occurred'
        setState({ data: null, loading: false, error: errorMessage })
        throw err
      }
    },
    []
  )

  return { ...state, execute }
}
