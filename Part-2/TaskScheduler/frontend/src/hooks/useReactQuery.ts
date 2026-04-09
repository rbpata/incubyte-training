import {
  useQuery,
  useMutation,
  type UseQueryResult,
  type UseMutationResult,
  type QueryKey,
  type UseQueryOptions as RQUseQueryOptions,
  type UseMutationOptions as RQUseMutationOptions,
} from '@tanstack/react-query'
import { apiClient } from '../utils/api'

const DEFAULT_STALE_TIME_MS = 5 * 60 * 1000
const DEFAULT_CACHE_TIME_MS = 10 * 60 * 1000
const DEFAULT_RETRY_ATTEMPTS = 2

interface UseQueryOptions extends Omit<RQUseQueryOptions<any, any, any>, 'queryKey' | 'queryFn'> {
  staleTime?: number
  cacheTime?: number
}

interface UseMutationOptions<TData, TError, TVariables>
  extends Omit<RQUseMutationOptions<TData, TError, TVariables>, 'mutationFn'> {
  staleTime?: number
  cacheTime?: number
}

export function useReactQuery<T>(
  queryKey: QueryKey,
  fetchFunction: () => Promise<T>,
  options?: UseQueryOptions
): UseQueryResult<T, unknown> {
  return useQuery({
    queryKey,
    queryFn: fetchFunction,
    staleTime: options?.staleTime ?? DEFAULT_STALE_TIME_MS,
    gcTime: options?.cacheTime ?? DEFAULT_CACHE_TIME_MS,
    retry: options?.retry ?? DEFAULT_RETRY_ATTEMPTS,
    refetchOnWindowFocus: options?.refetchOnWindowFocus ?? true,
    ...options,
  }) as UseQueryResult<T, unknown>
}

export function useReactMutation<TData, TError = unknown, TVariables = unknown>(
  mutationFunction: (variables: TVariables) => Promise<TData>,
  options?: UseMutationOptions<TData, TError, TVariables>
): UseMutationResult<TData, TError, TVariables> {
  return useMutation({
    mutationFn: mutationFunction,
    ...options,
  })
}

export function useReactQueryGet<T>(
  url: string,
  options?: UseQueryOptions
): UseQueryResult<T, unknown> {
  return useReactQuery(
    [url],
    () => apiClient.request<T>(url),
    options
  )
}
