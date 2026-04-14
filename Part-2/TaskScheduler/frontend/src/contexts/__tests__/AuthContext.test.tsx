import { describe, it, expect, beforeEach } from 'vitest'
import { renderHook, act } from '@testing-library/react'
import { AuthProvider, useAuth } from '../../contexts/AuthContext'
import type { AuthUser, TokenResponse } from '../../types/index'

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

describe('AuthContext', () => {
  describe('initial state', () => {
    it('has empty tokens and null user', () => {
      const { result } = renderHook(() => useAuth(), { wrapper })

      expect(result.current.accessToken).toBe('')
      expect(result.current.refreshToken).toBe('')
      expect(result.current.user).toBeNull()
    })

    it('is not loading initially', () => {
      const { result } = renderHook(() => useAuth(), { wrapper })
      expect(result.current.isLoading).toBe(false)
    })

    it('has no error initially', () => {
      const { result } = renderHook(() => useAuth(), { wrapper })
      expect(result.current.error).toBeNull()
    })

    it('isLoggedIn is false when no accessToken', () => {
      const { result } = renderHook(() => useAuth(), { wrapper })
      expect(result.current.isLoggedIn).toBe(false)
    })
  })

  describe('login', () => {
    it('updates tokens and user after login', () => {
      const { result } = renderHook(() => useAuth(), { wrapper })

      act(() => {
        result.current.login(mockTokens, mockUser)
      })

      expect(result.current.accessToken).toBe('access_abc')
      expect(result.current.refreshToken).toBe('refresh_xyz')
      expect(result.current.user).toEqual(mockUser)
    })

    it('sets isLoggedIn to true after login', () => {
      const { result } = renderHook(() => useAuth(), { wrapper })

      act(() => {
        result.current.login(mockTokens, mockUser)
      })

      expect(result.current.isLoggedIn).toBe(true)
    })

    it('clears loading and error after login', () => {
      const { result } = renderHook(() => useAuth(), { wrapper })

      act(() => {
        result.current.login(mockTokens, mockUser)
      })

      expect(result.current.isLoading).toBe(false)
      expect(result.current.error).toBeNull()
    })
  })

  describe('logout', () => {
    it('resets state to initial values', () => {
      const { result } = renderHook(() => useAuth(), { wrapper })

      act(() => {
        result.current.login(mockTokens, mockUser)
      })
      act(() => {
        result.current.logout()
      })

      expect(result.current.accessToken).toBe('')
      expect(result.current.refreshToken).toBe('')
      expect(result.current.user).toBeNull()
      expect(result.current.isLoggedIn).toBe(false)
    })
  })

  describe('setUser', () => {
    it('updates user without changing tokens', () => {
      const { result } = renderHook(() => useAuth(), { wrapper })

      act(() => {
        result.current.login(mockTokens, mockUser)
      })

      const updatedUser: AuthUser = { ...mockUser, full_name: 'Updated Name' }
      act(() => {
        result.current.setUser(updatedUser)
      })

      expect(result.current.user?.full_name).toBe('Updated Name')
      expect(result.current.accessToken).toBe('access_abc')
    })
  })

  describe('refreshTokens', () => {
    it('updates both tokens', () => {
      const { result } = renderHook(() => useAuth(), { wrapper })

      act(() => {
        result.current.login(mockTokens, mockUser)
      })

      const newTokens: TokenResponse = {
        access_token: 'new_access',
        refresh_token: 'new_refresh',
      }
      act(() => {
        result.current.refreshTokens(newTokens)
      })

      expect(result.current.accessToken).toBe('new_access')
      expect(result.current.refreshToken).toBe('new_refresh')
    })
  })

  describe('clearError', () => {
    it('clears the error field', () => {
      const { result } = renderHook(() => useAuth(), { wrapper })

      act(() => {
        result.current.dispatch({ type: 'LOGIN_FAILURE', payload: 'Login failed' })
      })

      expect(result.current.error).toBe('Login failed')

      act(() => {
        result.current.clearError()
      })

      expect(result.current.error).toBeNull()
    })
  })

  describe('restoreTokens', () => {
    it('sets both token fields', () => {
      const { result } = renderHook(() => useAuth(), { wrapper })

      act(() => {
        result.current.restoreTokens('restored_access', 'restored_refresh')
      })

      expect(result.current.accessToken).toBe('restored_access')
      expect(result.current.refreshToken).toBe('restored_refresh')
    })

    it('sets isLoggedIn to true when access token is restored', () => {
      const { result } = renderHook(() => useAuth(), { wrapper })

      act(() => {
        result.current.restoreTokens('restored_access', 'restored_refresh')
      })

      expect(result.current.isLoggedIn).toBe(true)
    })
  })

  describe('useAuth outside provider', () => {
    it('throws when used outside AuthProvider', () => {
      expect(() => renderHook(() => useAuth())).toThrow(
        'useAuth must be used within an AuthProvider'
      )
    })
  })
})
