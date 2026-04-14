import type { ApiError } from '../types/index'

const API_BASE = import.meta.env.VITE_API_BASE_URL ?? ''
const REQUEST_TIMEOUT_MS = 30000

function generateCorrelationId(): string {
  return crypto.randomUUID()
}

export class ApiClient {
  private static instance: ApiClient

  private constructor() {}

  static getInstance(): ApiClient {
    if (!ApiClient.instance) {
      ApiClient.instance = new ApiClient()
    }
    return ApiClient.instance
  }

  async request<T>(
    path: string,
    init?: RequestInit & { headers?: Record<string, string> }
  ): Promise<T> {
    const controller = new AbortController()
    const timeoutId = setTimeout(() => controller.abort(), REQUEST_TIMEOUT_MS)

    try {
      const response = await fetch(`${API_BASE}${path}`, {
        ...init,
        headers: {
          'Content-Type': 'application/json',
          'X-Correlation-ID': generateCorrelationId(),
          ...(init?.headers ?? {}),
        },
        signal: controller.signal,
      })

      clearTimeout(timeoutId)

      if (!response.ok) {
        const error = await this.parseError(response)
        throw new Error(error)
      }

      if (response.status === 204) {
        return undefined as T
      }

      return (await response.json()) as T
    } catch (err) {
      clearTimeout(timeoutId)
      if (err instanceof Error && err.name === 'AbortError') {
        throw new Error('Request timeout - backend may be unavailable')
      }
      throw err
    }
  }

  private async parseError(response: Response): Promise<string> {
    const defaultErrorMessage = `Request failed (${response.status})`

    try {
      const body = (await response.json()) as ApiError
      return body.detail ?? defaultErrorMessage
    } catch {
      return defaultErrorMessage
    }
  }
}

export const apiClient = ApiClient.getInstance()
