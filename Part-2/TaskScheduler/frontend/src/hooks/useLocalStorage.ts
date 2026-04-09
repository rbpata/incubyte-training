import { useState, useCallback, useEffect } from 'react'

interface UseLocalStorageOptions {
  serializer?: (value: any) => string
  deserializer?: (value: string) => any
  initializeFromUrl?: boolean
  syncData?: boolean
}

export function useLocalStorage<T>(
  key: string,
  initialValue?: T,
  options?: UseLocalStorageOptions
): [T, (value: T | ((val: T) => T)) => void, () => void] {
  const {
    serializer = JSON.stringify,
    deserializer = JSON.parse,
    syncData = true,
  } = options || {}

  const [storedValue, setStoredValue] = useState<T>(() => {
    if (typeof window === 'undefined') {
      return initialValue as T
    }

    try {
      const item = window.localStorage.getItem(key)
      return item ? deserializer(item) : initialValue
    } catch (error) {
      console.warn(`useLocalStorage error for key "${key}":`, error)
      return initialValue as T
    }
  })

  const setValue = useCallback(
    (value: T | ((val: T) => T)) => {
      try {
        const valueToStore = value instanceof Function ? value(storedValue) : value
        setStoredValue(valueToStore)
        
        if (typeof window !== 'undefined') {
          window.localStorage.setItem(key, serializer(valueToStore))
          window.dispatchEvent(
            new StorageEvent('storage', {
              key,
              newValue: serializer(valueToStore),
              oldValue: null,
              storageArea: window.localStorage,
            })
          )
        }
      } catch (error) {
        console.warn(`useLocalStorage error for key "${key}":`, error)
      }
    },
    [key, storedValue, serializer]
  )

  useEffect(() => {
    if (!syncData || typeof window === 'undefined') return

    const handleStorageChange = (storageChangeEvent: StorageEvent) => {
      if (storageChangeEvent.key === key && storageChangeEvent.newValue) {
        try {
          setStoredValue(deserializer(storageChangeEvent.newValue))
        } catch (error) {
          console.warn(`useLocalStorage sync error for key "${key}":`, error)
        }
      }
    }

    window.addEventListener('storage', handleStorageChange)
    return () => window.removeEventListener('storage', handleStorageChange)
  }, [key, deserializer, syncData])

  const removeValue = useCallback(() => {
    try {
      setStoredValue(initialValue as T)
      if (typeof window !== 'undefined') {
        window.localStorage.removeItem(key)
      }
    } catch (error) {
      console.warn(`useLocalStorage remove error for key "${key}":`, error)
    }
  }, [key, initialValue])

  return [storedValue, setValue, removeValue]
}