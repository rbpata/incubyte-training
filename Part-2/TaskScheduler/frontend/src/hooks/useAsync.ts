import { useCallback, useReducer, useEffect } from 'react'

type AsyncStatus = 'idle' | 'pending' | 'success' | 'error'

interface AsyncState<T, E> {
  status: AsyncStatus
  data: T | null
  error: E | null
}

type AsyncAction<T, E> =
  | { type: 'PENDING' }
  | { type: 'SUCCESS'; payload: T }
  | { type: 'ERROR'; payload: E }
  | { type: 'RESET' }

function createAsyncReducer<T, E>(
  state: AsyncState<T, E>,
  action: AsyncAction<T, E>
): AsyncState<T, E> {
  switch (action.type) {
    case 'PENDING':
      return { status: 'pending', data: null, error: null }
    case 'SUCCESS':
      return { status: 'success', data: action.payload, error: null }
    case 'ERROR':
      return { status: 'error', data: null, error: action.payload }
    case 'RESET':
      return { status: 'idle', data: null, error: null }
  }
}

interface UseAsyncOptions<T, E> {
  onSuccess?: (data: T) => void
  onError?: (error: E) => void
  onSettled?: () => void
}

export function useAsync<T, E = Error>(
  asyncFunction: () => Promise<T>,
  shouldExecuteImmediately = true,
  options?: UseAsyncOptions<T, E>
) {
  const [state, dispatch] = useReducer(createAsyncReducer<T, E>, {
    status: 'idle' as AsyncStatus,
    data: null,
    error: null,
  })

  const execute = useCallback(async () => {
    dispatch({ type: 'PENDING' })
    try {
      const data = await asyncFunction()
      dispatch({ type: 'SUCCESS', payload: data })
      options?.onSuccess?.(data)
      return data
    } catch (err) {
      dispatch({ type: 'ERROR', payload: err as E })
      options?.onError?.(err as E)
      throw err
    } finally {
      options?.onSettled?.()
    }
  }, [asyncFunction, options])

  useEffect(() => {
    if (shouldExecuteImmediately) {
      void execute()
    }
  }, [execute, shouldExecuteImmediately])

  return {
    ...state,
    execute,
    reset: () => dispatch({ type: 'RESET' }),
    isLoading: state.status === 'pending',
    isError: state.status === 'error',
    isSuccess: state.status === 'success',
    isIdle: state.status === 'idle',
  }
}

export function useAsyncCallback<T, E = Error>(
  asyncFunction: () => Promise<T>,
  options?: UseAsyncOptions<T, E>
) {
  const [state, dispatch] = useReducer(createAsyncReducer<T, E>, {
    status: 'idle' as AsyncStatus,
    data: null,
    error: null,
  })

  const execute = useCallback(async () => {
    dispatch({ type: 'PENDING' })
    try {
      const data = await asyncFunction()
      dispatch({ type: 'SUCCESS', payload: data })
      options?.onSuccess?.(data)
      return data
    } catch (err) {
      dispatch({ type: 'ERROR', payload: err as E })
      options?.onError?.(err as E)
      throw err
    } finally {
      options?.onSettled?.()
    }
  }, [asyncFunction, options])

  return {
    ...state,
    execute,
    reset: () => dispatch({ type: 'RESET' }),
    isLoading: state.status === 'pending',
    isError: state.status === 'error',
    isSuccess: state.status === 'success',
  }
}