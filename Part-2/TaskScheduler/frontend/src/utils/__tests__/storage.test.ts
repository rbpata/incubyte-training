import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { Storage, StorageKeys } from '../../utils/storage'

describe('StorageKeys', () => {
  it('has correct ACCESS_TOKEN value', () => {
    expect(StorageKeys.ACCESS_TOKEN).toBe('access_token')
  })

  it('has correct REFRESH_TOKEN value', () => {
    expect(StorageKeys.REFRESH_TOKEN).toBe('refresh_token')
  })
})

describe('Storage', () => {
  beforeEach(() => {
    localStorage.clear()
  })

  afterEach(() => {
    vi.restoreAllMocks()
  })

  describe('getItem', () => {
    it('returns null when key does not exist', () => {
      expect(Storage.getItem('nonexistent')).toBeNull()
    })

    it('returns the stored value', () => {
      localStorage.setItem('test_key', 'test_value')
      expect(Storage.getItem('test_key')).toBe('test_value')
    })

    it('returns null when localStorage throws', () => {
      vi.spyOn(window.localStorage.__proto__, 'getItem').mockImplementationOnce(() => {
        throw new Error('storage unavailable')
      })

      expect(Storage.getItem('test_key')).toBeNull()
    })
  })

  describe('setItem', () => {
    it('stores value that can be retrieved', () => {
      Storage.setItem('my_key', 'my_value')
      expect(localStorage.getItem('my_key')).toBe('my_value')
    })

    it('is silent when localStorage throws', () => {
      vi.spyOn(window.localStorage.__proto__, 'setItem').mockImplementationOnce(() => {
        throw new Error('storage full')
      })

      expect(() => Storage.setItem('key', 'value')).not.toThrow()
    })
  })

  describe('removeItem', () => {
    it('removes stored value', () => {
      localStorage.setItem('to_remove', 'value')
      Storage.removeItem('to_remove')
      expect(localStorage.getItem('to_remove')).toBeNull()
    })

    it('does not throw when key does not exist', () => {
      expect(() => Storage.removeItem('nonexistent')).not.toThrow()
    })
  })

  describe('clear', () => {
    it('removes all stored items', () => {
      localStorage.setItem('key1', 'val1')
      localStorage.setItem('key2', 'val2')

      Storage.clear()

      expect(localStorage.getItem('key1')).toBeNull()
      expect(localStorage.getItem('key2')).toBeNull()
    })
  })

  describe('StorageKeys integration', () => {
    it('stores and retrieves access token using StorageKeys constant', () => {
      Storage.setItem(StorageKeys.ACCESS_TOKEN, 'my_access_token')
      expect(Storage.getItem(StorageKeys.ACCESS_TOKEN)).toBe('my_access_token')
    })

    it('stores and retrieves refresh token using StorageKeys constant', () => {
      Storage.setItem(StorageKeys.REFRESH_TOKEN, 'my_refresh_token')
      expect(Storage.getItem(StorageKeys.REFRESH_TOKEN)).toBe('my_refresh_token')
    })
  })
})
