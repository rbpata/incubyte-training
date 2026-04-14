import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { ApiClient, apiClient } from '../../utils/api'

describe('ApiClient', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    global.fetch = vi.fn()
  })

  afterEach(() => {
    vi.restoreAllMocks()
  })

  describe('getInstance', () => {
    it('returns the same instance on multiple calls', () => {
      const instance1 = ApiClient.getInstance()
      const instance2 = ApiClient.getInstance()
      expect(instance1).toBe(instance2)
    })

    it('exported apiClient is the same singleton instance', () => {
      const instance = ApiClient.getInstance()
      expect(instance).toBe(apiClient)
    })
  })

  describe('request', () => {
    it('returns parsed JSON on successful response', async () => {
      const mockData = { id: 1, name: 'test' }
      vi.mocked(global.fetch).mockResolvedValueOnce({
        ok: true,
        status: 200,
        json: vi.fn().mockResolvedValueOnce(mockData),
      } as unknown as Response)

      const result = await apiClient.request('/api/test')

      expect(result).toEqual(mockData)
    })

    it('sends Content-Type and X-Correlation-ID headers', async () => {
      vi.mocked(global.fetch).mockResolvedValueOnce({
        ok: true,
        status: 200,
        json: vi.fn().mockResolvedValueOnce({}),
      } as unknown as Response)

      await apiClient.request('/api/test')

      const [, init] = vi.mocked(global.fetch).mock.calls[0]
      const headers = init?.headers as Record<string, string>
      expect(headers['Content-Type']).toBe('application/json')
      expect(headers['X-Correlation-ID']).toBeDefined()
      expect(typeof headers['X-Correlation-ID']).toBe('string')
    })

    it('merges caller-provided headers with defaults', async () => {
      vi.mocked(global.fetch).mockResolvedValueOnce({
        ok: true,
        status: 200,
        json: vi.fn().mockResolvedValueOnce({}),
      } as unknown as Response)

      await apiClient.request('/api/test', {
        headers: { Authorization: 'Bearer token123' },
      })

      const [, init] = vi.mocked(global.fetch).mock.calls[0]
      const headers = init?.headers as Record<string, string>
      expect(headers['Authorization']).toBe('Bearer token123')
      expect(headers['Content-Type']).toBe('application/json')
    })

    it('returns undefined for 204 No Content response', async () => {
      vi.mocked(global.fetch).mockResolvedValueOnce({
        ok: true,
        status: 204,
        json: vi.fn(),
      } as unknown as Response)

      const result = await apiClient.request('/api/test')

      expect(result).toBeUndefined()
    })

    it('throws with error detail when response is not ok and body has detail field', async () => {
      vi.mocked(global.fetch).mockResolvedValueOnce({
        ok: false,
        status: 400,
        json: vi.fn().mockResolvedValueOnce({ detail: 'Validation failed' }),
      } as unknown as Response)

      await expect(apiClient.request('/api/test')).rejects.toThrow('Validation failed')
    })

    it('throws with default message when response is not ok and body has no detail', async () => {
      vi.mocked(global.fetch).mockResolvedValueOnce({
        ok: false,
        status: 404,
        json: vi.fn().mockResolvedValueOnce({ message: 'not found' }),
      } as unknown as Response)

      await expect(apiClient.request('/api/test')).rejects.toThrow('Request failed (404)')
    })

    it('throws with default message when response is not ok and JSON parsing fails', async () => {
      vi.mocked(global.fetch).mockResolvedValueOnce({
        ok: false,
        status: 500,
        json: vi.fn().mockRejectedValueOnce(new Error('invalid json')),
      } as unknown as Response)

      await expect(apiClient.request('/api/test')).rejects.toThrow('Request failed (500)')
    })

    it('throws timeout message when fetch is aborted (AbortError)', async () => {
      const abortError = new Error('The operation was aborted')
      abortError.name = 'AbortError'
      vi.mocked(global.fetch).mockRejectedValueOnce(abortError)

      await expect(apiClient.request('/api/test')).rejects.toThrow(
        'Request timeout - backend may be unavailable'
      )
    })

    it('re-throws non-abort errors', async () => {
      const networkError = new Error('Network error')
      vi.mocked(global.fetch).mockRejectedValueOnce(networkError)

      await expect(apiClient.request('/api/test')).rejects.toThrow('Network error')
    })

    it('passes method and body from init options', async () => {
      vi.mocked(global.fetch).mockResolvedValueOnce({
        ok: true,
        status: 200,
        json: vi.fn().mockResolvedValueOnce({}),
      } as unknown as Response)

      await apiClient.request('/api/test', {
        method: 'POST',
        body: JSON.stringify({ name: 'test' }),
      })

      const [, init] = vi.mocked(global.fetch).mock.calls[0]
      expect(init?.method).toBe('POST')
      expect(init?.body).toBe(JSON.stringify({ name: 'test' }))
    })
  })
})
