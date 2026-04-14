import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, fireEvent } from '@testing-library/react'
import { TaskItem } from '../TaskItem'
import type { Task } from '../../types/index'

const mockTask: Task = {
  id: 1,
  user_id: 1,
  title: 'Test Task',
  description: 'A test description',
  run_at: new Date().toISOString(),
  status: 'pending',
  priority: 'medium',
  max_retries: 3,
  retry_count: 0,
  created_at: new Date().toISOString(),
  updated_at: new Date().toISOString(),
}

describe('TaskItem', () => {
  let onStatusChange: ReturnType<typeof vi.fn>
  let onProcess: ReturnType<typeof vi.fn>
  let onDelete: ReturnType<typeof vi.fn>

  beforeEach(() => {
    vi.clearAllMocks()
    onStatusChange = vi.fn().mockResolvedValue(undefined)
    onProcess = vi.fn().mockResolvedValue(undefined)
    onDelete = vi.fn().mockResolvedValue(undefined)
  })

  describe('rendering', () => {
    it('renders the task title', () => {
      render(
        <TaskItem
          task={mockTask}
          onStatusChange={onStatusChange}
          onProcess={onProcess}
          onDelete={onDelete}
        />
      )

      expect(screen.getByText('Test Task')).toBeDefined()
    })

    it('renders the task description', () => {
      render(
        <TaskItem
          task={mockTask}
          onStatusChange={onStatusChange}
          onProcess={onProcess}
          onDelete={onDelete}
        />
      )

      expect(screen.getByText('A test description')).toBeDefined()
    })

    it('renders "No description provided" when description is null', () => {
      const taskWithoutDesc = { ...mockTask, description: null }
      render(
        <TaskItem
          task={taskWithoutDesc}
          onStatusChange={onStatusChange}
          onProcess={onProcess}
          onDelete={onDelete}
        />
      )

      expect(screen.getByText('No description provided')).toBeDefined()
    })

    it('renders the priority badge', () => {
      render(
        <TaskItem
          task={mockTask}
          onStatusChange={onStatusChange}
          onProcess={onProcess}
          onDelete={onDelete}
        />
      )

      expect(screen.getByText('medium')).toBeDefined()
    })

    it('renders the status badge', () => {
      render(
        <TaskItem
          task={mockTask}
          onStatusChange={onStatusChange}
          onProcess={onProcess}
          onDelete={onDelete}
        />
      )

      expect(screen.getByText('pending')).toBeDefined()
    })

    it('renders task id', () => {
      render(
        <TaskItem
          task={mockTask}
          onStatusChange={onStatusChange}
          onProcess={onProcess}
          onDelete={onDelete}
        />
      )

      expect(screen.getByText('#1')).toBeDefined()
    })

    it('renders high priority task', () => {
      const highPriorityTask = { ...mockTask, priority: 'high' as const }
      render(
        <TaskItem
          task={highPriorityTask}
          onStatusChange={onStatusChange}
          onProcess={onProcess}
          onDelete={onDelete}
        />
      )

      expect(screen.getByText('high')).toBeDefined()
    })
  })

  describe('status select', () => {
    it('select has the current task status as value', () => {
      render(
        <TaskItem
          task={mockTask}
          onStatusChange={onStatusChange}
          onProcess={onProcess}
          onDelete={onDelete}
        />
      )

      const select = screen.getByRole('combobox', { name: 'Task status' }) as HTMLSelectElement
      expect(select.value).toBe('pending')
    })

    it('calls onStatusChange with task id and new status when changed', () => {
      render(
        <TaskItem
          task={mockTask}
          onStatusChange={onStatusChange}
          onProcess={onProcess}
          onDelete={onDelete}
        />
      )

      const select = screen.getByRole('combobox', { name: 'Task status' })
      fireEvent.change(select, { target: { value: 'completed' } })

      expect(onStatusChange).toHaveBeenCalledWith(1, 'completed')
    })

    it('select has all status options', () => {
      render(
        <TaskItem
          task={mockTask}
          onStatusChange={onStatusChange}
          onProcess={onProcess}
          onDelete={onDelete}
        />
      )

      const select = screen.getByRole('combobox', { name: 'Task status' }) as HTMLSelectElement
      const optionValues = Array.from(select.options).map((o) => o.value)
      expect(optionValues).toContain('pending')
      expect(optionValues).toContain('running')
      expect(optionValues).toContain('completed')
      expect(optionValues).toContain('failed')
    })
  })

  describe('Process button', () => {
    it('renders a Process button', () => {
      render(
        <TaskItem
          task={mockTask}
          onStatusChange={onStatusChange}
          onProcess={onProcess}
          onDelete={onDelete}
        />
      )

      expect(screen.getByText('▶ Process')).toBeDefined()
    })

    it('calls onProcess with task id when Process button is clicked', () => {
      render(
        <TaskItem
          task={mockTask}
          onStatusChange={onStatusChange}
          onProcess={onProcess}
          onDelete={onDelete}
        />
      )

      fireEvent.click(screen.getByText('▶ Process'))

      expect(onProcess).toHaveBeenCalledWith(1)
    })
  })

  describe('Delete button', () => {
    it('renders a Delete button', () => {
      render(
        <TaskItem
          task={mockTask}
          onStatusChange={onStatusChange}
          onProcess={onProcess}
          onDelete={onDelete}
        />
      )

      expect(screen.getByText('🗑 Delete')).toBeDefined()
    })

    it('calls onDelete with task id when confirmed', () => {
      vi.spyOn(window, 'confirm').mockReturnValueOnce(true)

      render(
        <TaskItem
          task={mockTask}
          onStatusChange={onStatusChange}
          onProcess={onProcess}
          onDelete={onDelete}
        />
      )

      fireEvent.click(screen.getByText('🗑 Delete'))

      expect(window.confirm).toHaveBeenCalledWith(
        'Are you sure you want to delete this task?'
      )
      expect(onDelete).toHaveBeenCalledWith(1)
    })

    it('does not call onDelete when confirm is cancelled', () => {
      vi.spyOn(window, 'confirm').mockReturnValueOnce(false)

      render(
        <TaskItem
          task={mockTask}
          onStatusChange={onStatusChange}
          onProcess={onProcess}
          onDelete={onDelete}
        />
      )

      fireEvent.click(screen.getByText('🗑 Delete'))

      expect(window.confirm).toHaveBeenCalled()
      expect(onDelete).not.toHaveBeenCalled()
    })
  })
})
