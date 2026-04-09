import { useEffect, useRef, useCallback } from 'react'

export function useThrottle<T>(value: T, throttleIntervalMs: number = 500): T {
  const throttledValueRef = useRef<T>(value)
  const lastExecutionTimeRef = useRef<number>(Date.now())

  useEffect(() => {
    const currentTime = Date.now()
    if (currentTime >= lastExecutionTimeRef.current + throttleIntervalMs) {
      lastExecutionTimeRef.current = currentTime
      throttledValueRef.current = value
    }
  }, [value, throttleIntervalMs])

  return throttledValueRef.current
}

export function useThrottleCallback<T extends (...args: any[]) => any>(
  callback: T,
  throttleIntervalMs: number = 500
): T {
  const pendingTimeoutRef = useRef<NodeJS.Timeout | null>(null)
  const lastExecutionTimeRef = useRef<number>(0)

  return useCallback(
    ((...args: Parameters<T>) => {
      const currentTime = Date.now()
      const timeSinceLastExecution = currentTime - lastExecutionTimeRef.current

      if (timeSinceLastExecution >= throttleIntervalMs) {
        callback(...args)
        lastExecutionTimeRef.current = currentTime
      } else {
        if (pendingTimeoutRef.current) clearTimeout(pendingTimeoutRef.current)
        pendingTimeoutRef.current = setTimeout(() => {
          callback(...args)
          lastExecutionTimeRef.current = Date.now()
        }, throttleIntervalMs - timeSinceLastExecution)
      }
    }) as T,
    [callback, throttleIntervalMs]
  )
}