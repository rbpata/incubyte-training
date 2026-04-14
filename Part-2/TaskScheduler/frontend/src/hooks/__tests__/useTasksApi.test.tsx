import { describe, it, expect, vi, beforeEach } from 'vitest'
import { renderHook, act } from '@testing-library/react'
import { useTasksApi } from '../useTasksApi'
import { AuthProvider } from '../../contexts/AuthContext'
import { TasksProvider, useTasks } from '../../contexts/TasksContext'
import { apiClient } from '../../utils/api'
import type { Task, TaskFilters, TasksResponse } from '../../types/index'

vi.mock('../../utils/api', () => ({
  apiClient: { request: vi.fn() },
}))

const defaultFilters: TaskFilters = {
  search: '',
  status: 'all',
  sortBy: 'created_at',
  sortOrder: 'desc',
  page: 1,
  size: 10,
}

const mockTask: Task = {
  id: 1,
  user_id: 1,
  title: 'Test Task',
  description: 'A description',
  run_at: new Date().toISOString(),
  status: 'pending',
  priority: 'medium',
  max_retries: 3,
  retry_count: 0,
  created_at: new Date().toISOString(),
  updated_at: new Date().toISOString(),
}

const mockTasksResponse: TasksResponse = {
  items: [mockTask],
  total: 1,
  page: 1,
  size: 10,
  pages: 1,
}

function wrapper({ children }: { children: React.ReactNode }) {
  return (
    <AuthProvider>
      <TasksProvider>{children}</TasksProvider>
    </AuthProvider>
  )
}

function useCombined() {
  return { tasksApi: useTasksApi(), tasks: useTasks() }
}

describe('useTasksApi', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  describe('loadTasks', () => {
    it('calls correct URL with pagination params', async () => {
      vi.mocked(apiClient.request).mockResolvedValueOnce(mockTasksResponse)

      const { result } = renderHook(() => useTasksApi(), { wrapper })

      await act(async () => {
        await result.current.loadTasks(defaultFilters)
      })

      const [url] = vi.mocked(apiClient.request).mock.calls[0]
      expect(url).toContain('/api/v1/tasks')
      expect(url).toContain('page=1')
      expect(url).toContain('size=10')
      expect(url).toContain('sort_by=created_at')
      expect(url).toContain('sort_order=desc')
    })

    it('excludes status param when status is all', async () => {
      vi.mocked(apiClient.request).mockResolvedValueOnce(mockTasksResponse)

      const { result } = renderHook(() => useTasksApi(), { wrapper })

      await act(async () => {
        await result.current.loadTasks({ ...defaultFilters, status: 'all' })
      })

      const [url] = vi.mocked(apiClient.request).mock.calls[0]
      expect(url).not.toContain('status=all')
      expect(url).not.toContain('status=')
    })

    it('includes status param when status is not all', async () => {
      vi.mocked(apiClient.request).mockResolvedValueOnce(mockTasksResponse)

      const { result } = renderHook(() => useTasksApi(), { wrapper })

      await act(async () => {
        await result.current.loadTasks({ ...defaultFilters, status: 'pending' })
      })

      const [url] = vi.mocked(apiClient.request).mock.calls[0]
      expect(url).toContain('status=pending')
    })

    it('includes search param when search is non-empty', async () => {
      vi.mocked(apiClient.request).mockResolvedValueOnce(mockTasksResponse)

      const { result } = renderHook(() => useTasksApi(), { wrapper })

      await act(async () => {
        await result.current.loadTasks({ ...defaultFilters, search: 'hello world' })
      })

      const [url] = vi.mocked(apiClient.request).mock.calls[0]
      expect(url).toContain('search=hello+world')
    })

    it('returns tasks response data', async () => {
      vi.mocked(apiClient.request).mockResolvedValueOnce(mockTasksResponse)

      const { result } = renderHook(() => useTasksApi(), { wrapper })

      let data: TasksResponse | undefined
      await act(async () => {
        data = await result.current.loadTasks(defaultFilters)
      })

      expect(data).toEqual(mockTasksResponse)
    })
  })

  describe('createTask', () => {
    it('POSTs to /api/v1/tasks with task data', async () => {
      vi.mocked(apiClient.request).mockResolvedValueOnce(mockTask)

      const { result } = renderHook(() => useTasksApi(), { wrapper })
      const taskData = {
        title: 'New Task',
        description: 'desc',
        run_at: new Date().toISOString(),
        priority: 'high' as const,
        max_retries: 3,
      }

      await act(async () => {
        await result.current.createTask(taskData)
      })

      expect(apiClient.request).toHaveBeenCalledWith(
        '/api/v1/tasks',
        expect.objectContaining({
          method: 'POST',
          body: JSON.stringify(taskData),
        })
      )
    })

    it('calls addTask on context after creating', async () => {
      vi.mocked(apiClient.request).mockResolvedValueOnce(mockTask)

      const { result } = renderHook(() => useCombined(), { wrapper })

      await act(async () => {
        await result.current.tasksApi.createTask({
          title: 'New Task',
          description: null,
          run_at: new Date().toISOString(),
          priority: 'low',
          max_retries: 3,
        })
      })

      expect(result.current.tasks.items).toContainEqual(mockTask)
    })
  })

  describe('updateTaskStatus', () => {
    it('PATCHes correct endpoint with new status', async () => {
      const updatedTask = { ...mockTask, status: 'completed' as const }
      vi.mocked(apiClient.request).mockResolvedValueOnce(updatedTask)

      const { result } = renderHook(() => useTasksApi(), { wrapper })

      await act(async () => {
        await result.current.updateTaskStatus(1, 'completed')
      })

      expect(apiClient.request).toHaveBeenCalledWith(
        '/api/v1/tasks/1/status',
        expect.objectContaining({
          method: 'PATCH',
          body: JSON.stringify({ status: 'completed' }),
        })
      )
    })
  })

  describe('removeTask', () => {
    it('DELETEs the correct endpoint', async () => {
      vi.mocked(apiClient.request).mockResolvedValueOnce(undefined)

      const { result } = renderHook(() => useTasksApi(), { wrapper })

      await act(async () => {
        await result.current.removeTask(42)
      })

      expect(apiClient.request).toHaveBeenCalledWith(
        '/api/v1/tasks/42',
        expect.objectContaining({ method: 'DELETE' })
      )
    })

    it('calls deleteTask on context after removing', async () => {
      vi.mocked(apiClient.request)
        .mockResolvedValueOnce(mockTasksResponse)
        .mockResolvedValueOnce(undefined)

      const { result } = renderHook(() => useCombined(), { wrapper })

      await act(async () => {
        await result.current.tasksApi.loadTasks(defaultFilters)
      })
      await act(async () => {
        await result.current.tasksApi.removeTask(1)
      })

      expect(result.current.tasks.items).not.toContainEqual(mockTask)
    })
  })

  describe('processTask', () => {
    it('POSTs to /process endpoint', async () => {
      vi.mocked(apiClient.request).mockResolvedValueOnce(mockTask)

      const { result } = renderHook(() => useTasksApi(), { wrapper })

      await act(async () => {
        await result.current.processTask(1)
      })

      expect(apiClient.request).toHaveBeenCalledWith(
        '/api/v1/tasks/1/process',
        expect.objectContaining({ method: 'POST' })
      )
    })
  })

  describe('getTaskById', () => {
    it('GETs task from correct endpoint', async () => {
      vi.mocked(apiClient.request).mockResolvedValueOnce(mockTask)

      const { result } = renderHook(() => useTasksApi(), { wrapper })

      await act(async () => {
        await result.current.getTaskById(1)
      })

      expect(apiClient.request).toHaveBeenCalledWith(
        '/api/v1/tasks/1',
        expect.any(Object)
      )
    })
  })

  describe('loading and error state', () => {
    it('exposes isLoading state', () => {
      const { result } = renderHook(() => useTasksApi(), { wrapper })
      expect(result.current.isLoading).toBe(false)
    })

    it('exposes error state', () => {
      const { result } = renderHook(() => useTasksApi(), { wrapper })
      expect(result.current.error).toBeNull()
    })
  })
})
