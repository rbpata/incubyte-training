export type TaskStatus = 'pending' | 'running' | 'completed' | 'failed'
export type TaskPriority = 'low' | 'medium' | 'high'
export type AuthMode = 'login' | 'register'

export interface AuthUser {
  id: number
  email: string
  full_name: string
  role: string
  is_active: boolean
}

export interface TokenResponse {
  access_token: string
  refresh_token: string
}

export interface ApiKey {
  id: number
  name: string
  is_active: boolean
  created_at: string
}

export interface ApiKeyCreateResponse {
  id: number
  name: string
  plaintext_key: string
  created_at: string
}

export interface Task {
  id: number
  user_id: number
  title: string
  description: string | null
  run_at: string
  status: TaskStatus
  priority: TaskPriority
  max_retries: number
  retry_count: number
  created_at: string
  updated_at: string
}

export interface TasksResponse {
  items: Task[]
  total: number
  page: number
  size: number
  pages: number
}

export interface TaskFilters {
  search: string
  status: 'all' | TaskStatus
  sortBy: 'created_at' | 'run_at' | 'status' | 'priority'
  sortOrder: 'asc' | 'desc'
  page: number
  size: number
}

export interface ApiError {
  detail: string
}

export interface UseApiState<T> {
  data: T | null
  loading: boolean
  error: string | null
}
