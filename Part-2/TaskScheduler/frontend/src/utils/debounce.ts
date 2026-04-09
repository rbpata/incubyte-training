export function debounce<T extends (...args: unknown[]) => unknown>(
  func: T,
  delayInMilliseconds: number
): (...args: Parameters<T>) => void {
  let pendingTimeoutId: ReturnType<typeof setTimeout> | null = null

  return function (...args: Parameters<T>) {
    if (pendingTimeoutId) {
      clearTimeout(pendingTimeoutId)
    }

    pendingTimeoutId = setTimeout(() => {
      func(...args)
      pendingTimeoutId = null
    }, delayInMilliseconds)
  }
}

export function throttle<T extends (...args: unknown[]) => unknown>(
  func: T,
  throttleIntervalMs: number
): (...args: Parameters<T>) => void {
  let hasRecentlyExecuted: boolean

  return function (...args: Parameters<T>) {
    if (!hasRecentlyExecuted) {
      func(...args)
      hasRecentlyExecuted = true
      setTimeout(() => {
        hasRecentlyExecuted = false
      }, throttleIntervalMs)
    }
  }
}
