import { useCallback, useMemo } from 'react'
import { useApi } from './useApi'
import { useTasks } from '../contexts/TasksContext'
import { useAuth } from '../contexts/AuthContext'
import type { Task, TasksResponse, TaskFilters, TaskStatus } from '../types/index'

export function useTasksApi() {
  const tasksApi = useApi<TasksResponse>()
  const taskApi = useApi<Task>()
  const { addTask, updateTask, deleteTask, updateFilters } = useTasks()
  const { accessToken } = useAuth()

  const authHeaders = useMemo(
    () => ({ Authorization: `Bearer ${accessToken}` }),
    [accessToken]
  )

  const tasksApiExecute = tasksApi.execute
  const taskApiExecute = taskApi.execute

  const loadTasks = useCallback(
    async (filters: TaskFilters) => {
      const params = new URLSearchParams({
        page: String(filters.page),
        size: String(filters.size),
        sort_by: filters.sortBy,
        sort_order: filters.sortOrder,
      })

      if (filters.status !== 'all') {
        params.set('status', filters.status)
      }

      if (filters.search.trim()) {
        params.set('search', filters.search.trim())
      }

      const data = await tasksApiExecute(`/api/v1/tasks?${params.toString()}`, {
        headers: authHeaders,
      })

      updateFilters(filters)
      return data
    },
    [tasksApiExecute, authHeaders, updateFilters]
  )

  const createTask = useCallback(
    async (taskData: {
      title: string
      description: string | null
      run_at: string
      priority: 'low' | 'medium' | 'high'
      max_retries: number
    }) => {
      const task = await taskApiExecute('/api/v1/tasks', {
        method: 'POST',
        headers: authHeaders,
        body: JSON.stringify(taskData),
      })

      addTask(task)
      return task
    },
    [taskApiExecute, authHeaders, addTask]
  )

  const updateTaskStatus = useCallback(
    async (taskId: number, status: TaskStatus) => {
      const task = await taskApiExecute(`/api/v1/tasks/${taskId}/status`, {
        method: 'PATCH',
        headers: authHeaders,
        body: JSON.stringify({ status }),
      })

      updateTask(task)
      return task
    },
    [taskApiExecute, authHeaders, updateTask]
  )

  const removeTask = useCallback(
    async (taskId: number) => {
      await taskApiExecute(`/api/v1/tasks/${taskId}`, {
        method: 'DELETE',
        headers: authHeaders,
      })

      deleteTask(taskId)
    },
    [taskApiExecute, authHeaders, deleteTask]
  )

  const getTaskById = useCallback(
    async (taskId: string | number) => {
      return await taskApiExecute(`/api/v1/tasks/${taskId}`, {
        headers: authHeaders,
      })
    },
    [taskApiExecute, authHeaders]
  )

  const processTask = useCallback(
    async (taskId: number) => {
      return await taskApiExecute(`/api/v1/tasks/${taskId}/process`, {
        method: 'POST',
        headers: authHeaders,
      })
    },
    [taskApiExecute, authHeaders]
  )

  return {
    loadTasks,
    createTask,
    updateTaskStatus,
    removeTask,
    getTaskById,
    processTask,
    isLoading: tasksApi.loading || taskApi.loading,
    error: tasksApi.error || taskApi.error,
  }
}
