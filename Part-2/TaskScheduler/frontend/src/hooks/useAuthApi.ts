import { useCallback } from 'react'
import { useApi } from './useApi'
import { useAuth } from '../contexts/AuthContext'
import { Storage, StorageKeys } from '../utils/storage'
import type { TokenResponse, AuthUser } from '../types/index'

export function useAuthApi() {
  const authApi = useApi<TokenResponse>()
  const userApi = useApi<AuthUser>()
  const { login, logout, refreshTokens, restoreTokens } = useAuth()

  const handleLogin = useCallback(
    async (email: string, password: string) => {
      const tokens = await authApi.execute('/api/v1/auth/login', {
        method: 'POST',
        body: JSON.stringify({ email, password }),
      })

      Storage.setItem(StorageKeys.ACCESS_TOKEN, tokens.access_token)
      Storage.setItem(StorageKeys.REFRESH_TOKEN, tokens.refresh_token)

      const user = await userApi.execute('/api/v1/auth/me', {
        headers: { Authorization: `Bearer ${tokens.access_token}` },
      })

      login(tokens, user)
    },
    [authApi, userApi, login]
  )

  const handleRegister = useCallback(
    async (email: string, password: string, fullName: string) => {
      await userApi.execute('/api/v1/auth/register', {
        method: 'POST',
        body: JSON.stringify({
          email,
          password,
          full_name: fullName,
        }),
      })
    },
    [userApi]
  )

  const handleLogout = useCallback(
    async (refreshToken: string) => {
      try {
        await authApi.execute('/api/v1/auth/logout', {
          method: 'POST',
          body: JSON.stringify({ refresh_token: refreshToken }),
        })
      } finally {
        Storage.removeItem(StorageKeys.ACCESS_TOKEN)
        Storage.removeItem(StorageKeys.REFRESH_TOKEN)
        logout()
      }
    },
    [authApi, logout]
  )

  const handleRefresh = useCallback(
    async (refreshToken: string) => {
      const tokens = await authApi.execute('/api/v1/auth/refresh', {
        method: 'POST',
        body: JSON.stringify({ refresh_token: refreshToken }),
      })

      Storage.setItem(StorageKeys.ACCESS_TOKEN, tokens.access_token)
      Storage.setItem(StorageKeys.REFRESH_TOKEN, tokens.refresh_token)
      refreshTokens(tokens)
    },
    [authApi, refreshTokens]
  )

  const restoreSession = useCallback(() => {
    const accessToken = Storage.getItem(StorageKeys.ACCESS_TOKEN) ?? ''
    const refreshToken = Storage.getItem(StorageKeys.REFRESH_TOKEN) ?? ''
    if (accessToken && refreshToken) {
      restoreTokens(accessToken, refreshToken)
    }
  }, [restoreTokens])

  return {
    login: handleLogin,
    register: handleRegister,
    logout: handleLogout,
    refresh: handleRefresh,
    restoreSession,
    isLoading: authApi.loading || userApi.loading,
    error: authApi.error || userApi.error,
  }
}
