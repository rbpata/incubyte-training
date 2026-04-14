import { describe, it, expect, vi, beforeEach } from 'vitest'
import { renderHook, act, waitFor } from '@testing-library/react'
import { useAuthApi } from '../useAuthApi'
import { AuthProvider, useAuth } from '../../contexts/AuthContext'
import { apiClient } from '../../utils/api'
import { Storage, StorageKeys } from '../../utils/storage'
import type { TokenResponse, AuthUser } from '../../types/index'

vi.mock('../../utils/api', () => ({
  apiClient: { request: vi.fn() },
}))

vi.mock('../../utils/storage', () => ({
  Storage: {
    getItem: vi.fn(),
    setItem: vi.fn(),
    removeItem: vi.fn(),
    clear: vi.fn(),
  },
  StorageKeys: {
    ACCESS_TOKEN: 'access_token',
    REFRESH_TOKEN: 'refresh_token',
  },
}))

const mockTokens: TokenResponse = {
  access_token: 'access_abc',
  refresh_token: 'refresh_xyz',
}

const mockUser: AuthUser = {
  id: 1,
  email: 'test@example.com',
  full_name: 'Test User',
  role: 'user',
  is_active: true,
}

function wrapper({ children }: { children: React.ReactNode }) {
  return <AuthProvider>{children}</AuthProvider>
}

function useCombined() {
  return { authApi: useAuthApi(), auth: useAuth() }
}

describe('useAuthApi', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  describe('login', () => {
    it('calls login endpoint then me endpoint', async () => {
      vi.mocked(apiClient.request)
        .mockResolvedValueOnce(mockTokens)
        .mockResolvedValueOnce(mockUser)

      const { result } = renderHook(() => useCombined(), { wrapper })

      await act(async () => {
        await result.current.authApi.login('test@example.com', 'password123')
      })

      expect(apiClient.request).toHaveBeenNthCalledWith(
        1,
        '/api/v1/auth/login',
        expect.objectContaining({ method: 'POST' })
      )
      expect(apiClient.request).toHaveBeenNthCalledWith(
        2,
        '/api/v1/auth/me',
        expect.objectContaining({ headers: expect.objectContaining({ Authorization: 'Bearer access_abc' }) })
      )
    })

    it('stores tokens in Storage after successful login', async () => {
      vi.mocked(apiClient.request)
        .mockResolvedValueOnce(mockTokens)
        .mockResolvedValueOnce(mockUser)

      const { result } = renderHook(() => useAuthApi(), { wrapper })

      await act(async () => {
        await result.current.login('test@example.com', 'password123')
      })

      expect(Storage.setItem).toHaveBeenCalledWith(StorageKeys.ACCESS_TOKEN, 'access_abc')
      expect(Storage.setItem).toHaveBeenCalledWith(StorageKeys.REFRESH_TOKEN, 'refresh_xyz')
    })

    it('updates auth context with tokens and user', async () => {
      vi.mocked(apiClient.request)
        .mockResolvedValueOnce(mockTokens)
        .mockResolvedValueOnce(mockUser)

      const { result } = renderHook(() => useCombined(), { wrapper })

      await act(async () => {
        await result.current.authApi.login('test@example.com', 'password123')
      })

      expect(result.current.auth.accessToken).toBe('access_abc')
      expect(result.current.auth.user).toEqual(mockUser)
    })
  })

  describe('register', () => {
    it('calls register endpoint with correct payload', async () => {
      vi.mocked(apiClient.request).mockResolvedValueOnce(mockUser)

      const { result } = renderHook(() => useAuthApi(), { wrapper })

      await act(async () => {
        await result.current.register('new@example.com', 'password123', 'New User')
      })

      expect(apiClient.request).toHaveBeenCalledWith(
        '/api/v1/auth/register',
        expect.objectContaining({
          method: 'POST',
          body: JSON.stringify({
            email: 'new@example.com',
            password: 'password123',
            full_name: 'New User',
          }),
        })
      )
    })
  })

  describe('logout', () => {
    it('calls logout endpoint with refresh token', async () => {
      vi.mocked(apiClient.request).mockResolvedValueOnce(undefined)

      const { result } = renderHook(() => useAuthApi(), { wrapper })

      await act(async () => {
        await result.current.logout('refresh_xyz')
      })

      expect(apiClient.request).toHaveBeenCalledWith(
        '/api/v1/auth/logout',
        expect.objectContaining({
          method: 'POST',
          body: JSON.stringify({ refresh_token: 'refresh_xyz' }),
        })
      )
    })

    it('removes tokens from Storage after logout', async () => {
      vi.mocked(apiClient.request).mockResolvedValueOnce(undefined)

      const { result } = renderHook(() => useAuthApi(), { wrapper })

      await act(async () => {
        await result.current.logout('refresh_xyz')
      })

      expect(Storage.removeItem).toHaveBeenCalledWith(StorageKeys.ACCESS_TOKEN)
      expect(Storage.removeItem).toHaveBeenCalledWith(StorageKeys.REFRESH_TOKEN)
    })

    it('clears storage and calls logout even when API call fails', async () => {
      vi.mocked(apiClient.request).mockRejectedValueOnce(new Error('Server error'))

      const { result } = renderHook(() => useAuthApi(), { wrapper })

      await act(async () => {
        try {
          await result.current.logout('refresh_xyz')
        } catch {
          // expected - handleLogout re-throws via try/finally
        }
      })

      expect(Storage.removeItem).toHaveBeenCalledWith(StorageKeys.ACCESS_TOKEN)
      expect(Storage.removeItem).toHaveBeenCalledWith(StorageKeys.REFRESH_TOKEN)
    })
  })

  describe('refresh', () => {
    it('calls refresh endpoint and stores new tokens', async () => {
      const newTokens: TokenResponse = {
        access_token: 'new_access',
        refresh_token: 'new_refresh',
      }
      vi.mocked(apiClient.request).mockResolvedValueOnce(newTokens)

      const { result } = renderHook(() => useAuthApi(), { wrapper })

      await act(async () => {
        await result.current.refresh('old_refresh')
      })

      expect(apiClient.request).toHaveBeenCalledWith(
        '/api/v1/auth/refresh',
        expect.objectContaining({
          method: 'POST',
          body: JSON.stringify({ refresh_token: 'old_refresh' }),
        })
      )
      expect(Storage.setItem).toHaveBeenCalledWith(StorageKeys.ACCESS_TOKEN, 'new_access')
      expect(Storage.setItem).toHaveBeenCalledWith(StorageKeys.REFRESH_TOKEN, 'new_refresh')
    })

    it('updates auth context tokens after refresh', async () => {
      const newTokens: TokenResponse = {
        access_token: 'new_access',
        refresh_token: 'new_refresh',
      }
      vi.mocked(apiClient.request).mockResolvedValueOnce(newTokens)

      const { result } = renderHook(() => useCombined(), { wrapper })

      await act(async () => {
        await result.current.authApi.refresh('old_refresh')
      })

      expect(result.current.auth.accessToken).toBe('new_access')
      expect(result.current.auth.refreshToken).toBe('new_refresh')
    })
  })

  describe('restoreSession', () => {
    it('restores tokens from storage when both exist', async () => {
      vi.mocked(Storage.getItem)
        .mockReturnValueOnce('stored_access')
        .mockReturnValueOnce('stored_refresh')

      const { result } = renderHook(() => useCombined(), { wrapper })

      act(() => {
        result.current.authApi.restoreSession()
      })

      await waitFor(() => {
        expect(result.current.auth.accessToken).toBe('stored_access')
        expect(result.current.auth.refreshToken).toBe('stored_refresh')
      })
    })

    it('does nothing when tokens are missing from storage', () => {
      vi.mocked(Storage.getItem).mockReturnValue(null)

      const { result } = renderHook(() => useCombined(), { wrapper })

      act(() => {
        result.current.authApi.restoreSession()
      })

      expect(result.current.auth.accessToken).toBe('')
      expect(result.current.auth.refreshToken).toBe('')
    })

    it('does nothing when only access token exists', () => {
      vi.mocked(Storage.getItem)
        .mockReturnValueOnce('stored_access')
        .mockReturnValueOnce(null)

      const { result } = renderHook(() => useCombined(), { wrapper })

      act(() => {
        result.current.authApi.restoreSession()
      })

      expect(result.current.auth.accessToken).toBe('')
    })
  })

  describe('loading and error state', () => {
    it('exposes isLoading state', () => {
      const { result } = renderHook(() => useAuthApi(), { wrapper })
      expect(result.current.isLoading).toBe(false)
    })

    it('exposes error state', () => {
      const { result } = renderHook(() => useAuthApi(), { wrapper })
      expect(result.current.error).toBeNull()
    })
  })
})
