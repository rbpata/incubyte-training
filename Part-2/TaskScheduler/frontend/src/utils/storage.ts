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
      return
    }
  }

  static removeItem(key: string): void {
    try {
      localStorage.removeItem(key)
    } catch {
      return
    }
  }

  static clear(): void {
    try {
      localStorage.clear()
    } catch {
      return
    }
  }
}
