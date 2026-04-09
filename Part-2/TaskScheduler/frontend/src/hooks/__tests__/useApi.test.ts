/**
 * Unit tests for useApi hook.
 */

import { renderHook, waitFor } from '@testing-library/react'
import { useApi } from '../useApi'
import { apiClient } from '../../utils/api'
import { describe, it, expect, vi, beforeEach } from 'vitest'

vi.mock('../../utils/api')

describe('useApi', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('initializes with null data and no loading', () => {
    const { result } = renderHook(() => useApi())

    expect(result.current.data).toBeNull()
    expect(result.current.loading).toBe(false)
    expect(result.current.error).toBeNull()
  })

  it('sets loading state during API call', async () => {
    const mockResponse = { id: 1, name: 'test' }
    vi.mocked(apiClient.request).mockResolvedValue(mockResponse)

    const { result } = renderHook(() => useApi())

    const promise = result.current.execute('/test')

    expect(result.current.loading).toBe(true)

    await waitFor(() => {
      expect(result.current.loading).toBe(false)
    })

    await promise
  })

  it('updates data on success', async () => {
    const mockResponse = { id: 1, name: 'test' }
    vi.mocked(apiClient.request).mockResolvedValue(mockResponse)

    const { result } = renderHook(() => useApi())

    await result.current.execute('/test')

    await waitFor(() => {
      expect(result.current.data).toEqual(mockResponse)
      expect(result.current.error).toBeNull()
    })
  })

  it('sets error on failure', async () => {
    const mockError = new Error('API Error')
    vi.mocked(apiClient.request).mockRejectedValue(mockError)

    const { result } = renderHook(() => useApi())

    try {
      await result.current.execute('/test')
    } catch {
      // Expected
    }

    await waitFor(() => {
      expect(result.current.error).toBe('API Error')
      expect(result.current.data).toBeNull()
    })
  })
})
