/**
 * TaskItem - Individual task component with liquid glass effect
 * - Memoized to prevent unnecessary re-renders
 * - Uses Tailwind CSS for styling
 * - Performance optimized with useCallback
 */

import {memo, useCallback} from 'react';
import {Badge, Button} from './ui';
import type {Task, TaskStatus} from '../types/index';

interface TaskItemProps {
    task: Task;
    onStatusChange: (taskId: number, status: TaskStatus) => Promise<void>;
    onProcess: (taskId: number) => Promise<void>;
    onDelete: (taskId: number) => Promise<void>;
}

function TaskItemComponent({
    task,
    onStatusChange,
    onProcess,
    onDelete
}: TaskItemProps) {
    const handleStatusChange = useCallback(
        (e: React.ChangeEvent<HTMLSelectElement>) => {
            void onStatusChange(task.id, e.target.value as TaskStatus);
        },
        [task.id, onStatusChange]
    );

    const handleProcess = useCallback(() => {
        void onProcess(task.id);
    }, [task.id, onProcess]);

    const handleDelete = useCallback(() => {
        if (confirm('Are you sure you want to delete this task?')) {
            void onDelete(task.id);
        }
    }, [task.id, onDelete]);

    const priorityColors = {
        low: 'success',
        medium: 'info',
        high: 'danger'
    } as const;

    const statusColors = {
        pending: 'warning',
        running: 'info',
        completed: 'success',
        failed: 'danger'
    } as const;

    return (
        <article
            className={`glass-card-interactive p-5 md:p-6 space-y-4 ${
                task.priority === 'high'
                    ? 'priority-high'
                    : task.priority === 'medium'
                      ? 'priority-medium'
                      : 'priority-low'
            }`}
        >
            {/* Task Header */}
            <div className='flex items-start justify-between gap-4'>
                <div className='flex-1 min-w-0'>
                    <h3 className='text-lg font-semibold text-gray-900 truncate mb-1'>
                        {task.title}
                    </h3>
                    <p className='text-sm text-gray-600 line-clamp-2'>
                        {task.description || 'No description provided'}
                    </p>
                </div>
                <Badge variant={priorityColors[task.priority]} size='md'>
                    {task.priority}
                </Badge>
            </div>

            {/* Task Metadata */}
            <div className='grid grid-cols-2 md:grid-cols-4 gap-3 text-xs md:text-sm'>
                <div className='glass-effect-sm p-3 rounded-lg'>
                    <span className='text-gray-500'>ID</span>
                    <p className='font-semibold text-gray-900'>#{task.id}</p>
                </div>
                <div className='glass-effect-sm p-3 rounded-lg'>
                    <span className='text-gray-500'>Status</span>
                    <Badge
                        variant={statusColors[task.status]}
                        size='sm'
                        className='mt-1 inline-block'
                    >
                        {task.status}
                    </Badge>
                </div>
                <div className='glass-effect-sm p-3 rounded-lg'>
                    <span className='text-gray-500'>Created</span>
                    <p className='font-mono text-gray-900'>
                        {new Date(task.created_at).toLocaleDateString()}
                    </p>
                </div>
                <div className='glass-effect-sm p-3 rounded-lg'>
                    <span className='text-gray-500'>Run At</span>
                    <p className='font-mono text-gray-900'>
                        {new Date(task.run_at).toLocaleTimeString()}
                    </p>
                </div>
            </div>

            {/* Status Control & Actions */}
            <div className='flex flex-col md:flex-row gap-3 items-stretch md:items-center'>
                <select
                    value={task.status}
                    onChange={handleStatusChange}
                    className='input-glass flex-1 text-sm md:text-base'
                    aria-label='Task status'
                >
                    <option value='pending'>⏳ Pending</option>
                    <option value='running'>🔄 Running</option>
                    <option value='completed'>✓ Completed</option>
                    <option value='failed'>✗ Failed</option>
                </select>

                <div className='flex gap-2'>
                    <Button
                        variant='primary'
                        size='sm'
                        onClick={handleProcess}
                        className='flex-1 md:flex-none'
                    >
                        ▶ Process
                    </Button>
                    <Button
                        variant='ghost'
                        size='sm'
                        onClick={handleDelete}
                        className='flex-1 md:flex-none'
                    >
                        🗑 Delete
                    </Button>
                </div>
            </div>
        </article>
    );
}

export const TaskItem = memo(TaskItemComponent);
TaskItem.displayName = 'TaskItem';
