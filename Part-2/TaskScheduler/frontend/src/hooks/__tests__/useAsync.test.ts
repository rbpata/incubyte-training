import { describe, it, expect, vi, beforeEach } from 'vitest'
import { renderHook, waitFor, act } from '@testing-library/react'
import { useAsync, useAsyncCallback } from '../useAsync'

describe('useAsync', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  describe('immediate execution', () => {
    it('executes immediately when shouldExecuteImmediately is true', async () => {
      const asyncFn = vi.fn().mockResolvedValue('result')

      renderHook(() => useAsync(asyncFn, true))

      await waitFor(() => {
        expect(asyncFn).toHaveBeenCalledOnce()
      })
    })

    it('does not execute immediately when shouldExecuteImmediately is false', () => {
      const asyncFn = vi.fn().mockResolvedValue('result')

      renderHook(() => useAsync(asyncFn, false))

      expect(asyncFn).not.toHaveBeenCalled()
    })

    it('executes immediately by default', async () => {
      const asyncFn = vi.fn().mockResolvedValue('result')

      renderHook(() => useAsync(asyncFn))

      await waitFor(() => {
        expect(asyncFn).toHaveBeenCalledOnce()
      })
    })
  })

  describe('state transitions', () => {
    it('starts in idle state when not executing immediately', () => {
      const asyncFn = vi.fn().mockResolvedValue('result')
      const { result } = renderHook(() => useAsync(asyncFn, false))

      expect(result.current.status).toBe('idle')
      expect(result.current.isIdle).toBe(true)
      expect(result.current.data).toBeNull()
      expect(result.current.error).toBeNull()
    })

    it('transitions to success state with data on successful execution', async () => {
      const asyncFn = vi.fn().mockResolvedValue('test_data')
      const { result } = renderHook(() => useAsync(asyncFn, false))

      await act(async () => {
        await result.current.execute()
      })

      expect(result.current.status).toBe('success')
      expect(result.current.isSuccess).toBe(true)
      expect(result.current.data).toBe('test_data')
      expect(result.current.error).toBeNull()
    })

    it('transitions to error state with error on failed execution', async () => {
      const error = new Error('Something went wrong')
      const asyncFn = vi.fn().mockRejectedValue(error)
      const { result } = renderHook(() => useAsync(asyncFn, false))

      await act(async () => {
        try {
          await result.current.execute()
        } catch {
          // expected to throw
        }
      })

      expect(result.current.status).toBe('error')
      expect(result.current.isError).toBe(true)
      expect(result.current.error).toEqual(error)
      expect(result.current.data).toBeNull()
    })

    it('isLoading is true during pending state', async () => {
      let resolvePromise: (value: string) => void
      const asyncFn = vi.fn().mockReturnValue(
        new Promise<string>((resolve) => {
          resolvePromise = resolve
        })
      )
      const { result } = renderHook(() => useAsync(asyncFn, false))

      act(() => {
        void result.current.execute()
      })

      expect(result.current.isLoading).toBe(true)
      expect(result.current.status).toBe('pending')

      await act(async () => {
        resolvePromise!('done')
      })

      expect(result.current.isLoading).toBe(false)
    })
  })

  describe('callbacks', () => {
    it('calls onSuccess callback with data on success', async () => {
      const onSuccess = vi.fn()
      const asyncFn = vi.fn().mockResolvedValue('result_data')

      const { result } = renderHook(() =>
        useAsync(asyncFn, false, { onSuccess })
      )

      await act(async () => {
        await result.current.execute()
      })

      expect(onSuccess).toHaveBeenCalledWith('result_data')
    })

    it('calls onError callback with error on failure', async () => {
      const onError = vi.fn()
      const error = new Error('Failed')
      const asyncFn = vi.fn().mockRejectedValue(error)

      const { result } = renderHook(() =>
        useAsync(asyncFn, false, { onError })
      )

      await act(async () => {
        try {
          await result.current.execute()
        } catch {
          // expected
        }
      })

      expect(onError).toHaveBeenCalledWith(error)
    })

    it('calls onSettled after successful execution', async () => {
      const onSettled = vi.fn()
      const asyncFn = vi.fn().mockResolvedValue('data')

      const { result } = renderHook(() =>
        useAsync(asyncFn, false, { onSettled })
      )

      await act(async () => {
        await result.current.execute()
      })

      expect(onSettled).toHaveBeenCalledOnce()
    })

    it('calls onSettled after failed execution', async () => {
      const onSettled = vi.fn()
      const asyncFn = vi.fn().mockRejectedValue(new Error('fail'))

      const { result } = renderHook(() =>
        useAsync(asyncFn, false, { onSettled })
      )

      await act(async () => {
        try {
          await result.current.execute()
        } catch {
          // expected
        }
      })

      expect(onSettled).toHaveBeenCalledOnce()
    })
  })

  describe('reset', () => {
    it('returns to idle state after reset', async () => {
      const asyncFn = vi.fn().mockResolvedValue('data')
      const { result } = renderHook(() => useAsync(asyncFn, false))

      await act(async () => {
        await result.current.execute()
      })

      expect(result.current.status).toBe('success')

      act(() => {
        result.current.reset()
      })

      expect(result.current.status).toBe('idle')
      expect(result.current.data).toBeNull()
      expect(result.current.error).toBeNull()
    })
  })
})

describe('useAsyncCallback', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('does not execute immediately', () => {
    const asyncFn = vi.fn().mockResolvedValue('result')

    const { result } = renderHook(() => useAsyncCallback(asyncFn))

    expect(asyncFn).not.toHaveBeenCalled()
    expect(result.current.status).toBe('idle')
  })

  it('executes when execute is called manually', async () => {
    const asyncFn = vi.fn().mockResolvedValue('manual_data')
    const { result } = renderHook(() => useAsyncCallback(asyncFn))

    await act(async () => {
      await result.current.execute()
    })

    expect(asyncFn).toHaveBeenCalledOnce()
    expect(result.current.data).toBe('manual_data')
    expect(result.current.status).toBe('success')
  })

  it('handles error state correctly', async () => {
    const error = new Error('callback error')
    const asyncFn = vi.fn().mockRejectedValue(error)
    const { result } = renderHook(() => useAsyncCallback(asyncFn))

    await act(async () => {
      try {
        await result.current.execute()
      } catch {
        // expected
      }
    })

    expect(result.current.isError).toBe(true)
    expect(result.current.error).toEqual(error)
  })

  it('calls onSuccess callback with data', async () => {
    const onSuccess = vi.fn()
    const asyncFn = vi.fn().mockResolvedValue('callback_data')

    const { result } = renderHook(() => useAsyncCallback(asyncFn, { onSuccess }))

    await act(async () => {
      await result.current.execute()
    })

    expect(onSuccess).toHaveBeenCalledWith('callback_data')
  })

  it('resets to idle state', async () => {
    const asyncFn = vi.fn().mockResolvedValue('data')
    const { result } = renderHook(() => useAsyncCallback(asyncFn))

    await act(async () => {
      await result.current.execute()
    })

    act(() => {
      result.current.reset()
    })

    expect(result.current.status).toBe('idle')
  })
})
