import { describe, it, expect, beforeEach } from 'vitest'
import { renderHook, act } from '@testing-library/react'
import { TasksProvider, useTasks } from '../../contexts/TasksContext'
import type { Task, TasksResponse } from '../../types/index'

const makeTask = (overrides: Partial<Task> = {}): Task => ({
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
  ...overrides,
})

function wrapper({ children }: { children: React.ReactNode }) {
  return <TasksProvider>{children}</TasksProvider>
}

describe('TasksContext', () => {
  describe('initial state', () => {
    it('has empty items array', () => {
      const { result } = renderHook(() => useTasks(), { wrapper })
      expect(result.current.items).toEqual([])
    })

    it('has null selectedTask', () => {
      const { result } = renderHook(() => useTasks(), { wrapper })
      expect(result.current.selectedTask).toBeNull()
    })

    it('has total of 0', () => {
      const { result } = renderHook(() => useTasks(), { wrapper })
      expect(result.current.total).toBe(0)
    })

    it('is not loading initially', () => {
      const { result } = renderHook(() => useTasks(), { wrapper })
      expect(result.current.isLoading).toBe(false)
    })

    it('has no error initially', () => {
      const { result } = renderHook(() => useTasks(), { wrapper })
      expect(result.current.error).toBeNull()
    })

    it('has default filters', () => {
      const { result } = renderHook(() => useTasks(), { wrapper })
      expect(result.current.filters.status).toBe('all')
      expect(result.current.filters.page).toBe(1)
      expect(result.current.filters.sortBy).toBe('created_at')
      expect(result.current.filters.sortOrder).toBe('desc')
    })
  })

  describe('addTask', () => {
    it('prepends task to items and increments total', () => {
      const { result } = renderHook(() => useTasks(), { wrapper })
      const task = makeTask({ id: 1, title: 'First Task' })

      act(() => {
        result.current.addTask(task)
      })

      expect(result.current.items).toHaveLength(1)
      expect(result.current.items[0]).toEqual(task)
      expect(result.current.total).toBe(1)
    })

    it('prepends new task to front of items list', () => {
      const { result } = renderHook(() => useTasks(), { wrapper })
      const task1 = makeTask({ id: 1, title: 'Task 1' })
      const task2 = makeTask({ id: 2, title: 'Task 2' })

      act(() => {
        result.current.addTask(task1)
      })
      act(() => {
        result.current.addTask(task2)
      })

      expect(result.current.items[0]).toEqual(task2)
      expect(result.current.items[1]).toEqual(task1)
    })
  })

  describe('updateTask', () => {
    it('updates task matching by id', () => {
      const { result } = renderHook(() => useTasks(), { wrapper })
      const task = makeTask({ id: 1, status: 'pending' })

      act(() => {
        result.current.addTask(task)
      })

      const updatedTask = makeTask({ id: 1, status: 'completed' })
      act(() => {
        result.current.updateTask(updatedTask)
      })

      expect(result.current.items[0].status).toBe('completed')
    })

    it('does not change items count when updating existing task', () => {
      const { result } = renderHook(() => useTasks(), { wrapper })
      const task = makeTask({ id: 1 })

      act(() => {
        result.current.addTask(task)
      })
      act(() => {
        result.current.updateTask({ ...task, title: 'Updated' })
      })

      expect(result.current.items).toHaveLength(1)
    })
  })

  describe('deleteTask', () => {
    it('removes task by id and decrements total', () => {
      const { result } = renderHook(() => useTasks(), { wrapper })
      const task = makeTask({ id: 1 })

      act(() => {
        result.current.addTask(task)
      })
      act(() => {
        result.current.deleteTask(1)
      })

      expect(result.current.items).toHaveLength(0)
      expect(result.current.total).toBe(0)
    })

    it('only removes the task with matching id', () => {
      const { result } = renderHook(() => useTasks(), { wrapper })
      const task1 = makeTask({ id: 1, title: 'Task 1' })
      const task2 = makeTask({ id: 2, title: 'Task 2' })

      act(() => {
        result.current.addTask(task1)
        result.current.addTask(task2)
      })
      act(() => {
        result.current.deleteTask(1)
      })

      expect(result.current.items).toHaveLength(1)
      expect(result.current.items[0].id).toBe(2)
    })
  })

  describe('updateFilters', () => {
    it('merges partial filter updates', () => {
      const { result } = renderHook(() => useTasks(), { wrapper })

      act(() => {
        result.current.updateFilters({ status: 'pending', page: 2 })
      })

      expect(result.current.filters.status).toBe('pending')
      expect(result.current.filters.page).toBe(2)
      expect(result.current.filters.sortBy).toBe('created_at')
    })
  })

  describe('clearError', () => {
    it('clears the error field', () => {
      const { result } = renderHook(() => useTasks(), { wrapper })

      act(() => {
        result.current.dispatch({ type: 'LOAD_FAILURE', payload: 'Load failed' })
      })

      expect(result.current.error).toBe('Load failed')

      act(() => {
        result.current.clearError()
      })

      expect(result.current.error).toBeNull()
    })
  })

  describe('resetFilters', () => {
    it('resets filters back to defaults', () => {
      const { result } = renderHook(() => useTasks(), { wrapper })

      act(() => {
        result.current.updateFilters({ status: 'completed', page: 5, sortBy: 'run_at' })
      })

      act(() => {
        result.current.resetFilters()
      })

      expect(result.current.filters.status).toBe('all')
      expect(result.current.filters.page).toBe(1)
      expect(result.current.filters.sortBy).toBe('created_at')
    })
  })

  describe('LOAD_SUCCESS action', () => {
    it('updates items, total, and pages from response', () => {
      const { result } = renderHook(() => useTasks(), { wrapper })
      const task = makeTask({ id: 1 })
      const response: TasksResponse = {
        items: [task],
        total: 10,
        page: 1,
        size: 10,
        pages: 1,
      }

      act(() => {
        result.current.dispatch({ type: 'LOAD_SUCCESS', payload: response })
      })

      expect(result.current.items).toEqual([task])
      expect(result.current.total).toBe(10)
      expect(result.current.pages).toBe(1)
      expect(result.current.isLoading).toBe(false)
    })
  })

  describe('useTasks outside provider', () => {
    it('throws when used outside TasksProvider', () => {
      expect(() => renderHook(() => useTasks())).toThrow(
        'useTasks must be used within a TasksProvider'
      )
    })
  })
})
