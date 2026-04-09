export const StorageKeys = {
  ACCESS_TOKEN: 'access_token',
  REFRESH_TOKEN: 'refresh_token',
} as const

export class Storage {
  static getItem(key: string): string | null {
    try {
      return localStorage.getItem(key)
    } catch {
      return null
    }
  }

  static setItem(key: string, value: string): void {
    try {
      localStorage.setItem(key, value)
    } catch {
      // Silently fail on quota exceeded or private browsing mode
    }
  }

  static removeItem(key: string): void {
    try {
      localStorage.removeItem(key)
    } catch {
      // Silently fail on storage errors
    }
  }

  static clear(): void {
    try {
      localStorage.clear()
    } catch {
      // Silently fail on storage errors
    }
  }
}
