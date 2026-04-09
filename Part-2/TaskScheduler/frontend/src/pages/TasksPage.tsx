/**
 * TasksPage - Main tasks management page
 * - Advanced React patterns: Context API, useReducer, custom hooks
 * - Code splitting with lazy loading
 * - Virtual scrolling for large task lists
 * - Error boundaries and error handling
 * - Performance optimized with React.memo and useMemo
 */

import {useState, useCallback, useEffect, useMemo} from 'react';
import {useTasksApi} from '../hooks/useTasksApi';
import {useTasks} from '../contexts/TasksContext';
import {useAuth} from '../contexts/AuthContext';
import {TaskList, SearchInput, Feedback, Button, Card} from '../components';
import type {TaskPriority, TaskFilters} from '../types/index';

export function TasksPage() {
    const {
        loadTasks,
        createTask,
        updateTaskStatus,
        removeTask,
        processTask,
        isLoading
    } = useTasksApi();
    const {items: tasks, filters} = useTasks();
    const {user, logout} = useAuth();

    // Create task form state
    const [title, setTitle] = useState('');
    const [description, setDescription] = useState('');
    const [runAt, setRunAt] = useState('');
    const [priority, setPriority] = useState<TaskPriority>('medium');
    const [maxRetries, setMaxRetries] = useState(1);
    const [createError, setCreateError] = useState('');
    const [localMessage, setLocalMessage] = useState('');
    const [localError, setLocalError] = useState('');
    const [showCreateForm, setShowCreateForm] = useState(false);

    // Load initial tasks
    useEffect(() => {
        const initialFilters: TaskFilters = {
            search: '',
            status: 'all',
            sortBy: 'created_at',
            sortOrder: 'desc',
            page: 1,
            size: 10
        };
        void loadTasks(initialFilters);
    }, [loadTasks]);

    // Handle search with debouncing
    const handleSearch = useCallback(
        (query: string) => {
            void loadTasks({...filters, search: query, page: 1});
        },
        [loadTasks, filters]
    );

    const handleStatusChange = useCallback(
        async (taskId: number, newStatus: any) => {
            try {
                setLocalError('');
                await updateTaskStatus(taskId, newStatus);
                setLocalMessage(`✓ Task #${taskId} status updated`);
                await loadTasks(filters);
            } catch (err) {
                setLocalError(
                    err instanceof Error ? err.message : 'Failed to update task'
                );
            }
        },
        [updateTaskStatus, loadTasks, filters]
    );

    const handleCreateTask = useCallback(
        async (e: React.FormEvent<HTMLFormElement>) => {
            e.preventDefault();
            setCreateError('');
            setLocalError('');

            // Validation
            if (!title.trim()) {
                setCreateError('Task title is required');
                return;
            }

            if (!runAt) {
                setCreateError('Please select a run time');
                return;
            }

            try {
                const runAtIso = new Date(runAt).toISOString();
                await createTask({
                    title,
                    description: description || null,
                    run_at: runAtIso,
                    priority,
                    max_retries: maxRetries
                });

                setTitle('');
                setDescription('');
                setRunAt('');
                setPriority('medium');
                setMaxRetries(1);
                setShowCreateForm(false);
                setLocalMessage('✓ Task created successfully!');
                await loadTasks(filters);
            } catch (err) {
                setCreateError(
                    err instanceof Error ? err.message : 'Failed to create task'
                );
            }
        },
        [
            title,
            runAt,
            description,
            priority,
            maxRetries,
            createTask,
            loadTasks,
            filters
        ]
    );

    const handleDeleteTask = useCallback(
        async (taskId: number) => {
            try {
                setLocalError('');
                await removeTask(taskId);
                setLocalMessage(`✓ Task #${taskId} deleted`);
                await loadTasks(filters);
            } catch (err) {
                setLocalError(
                    err instanceof Error ? err.message : 'Failed to delete task'
                );
            }
        },
        [removeTask, loadTasks, filters]
    );

    const handleProcessTask = useCallback(
        async (taskId: number) => {
            try {
                setLocalError('');
                await processTask(taskId);
                setLocalMessage(`✓ Task #${taskId} sent for processing`);
                await loadTasks(filters);
            } catch (err) {
                setLocalError(
                    err instanceof Error
                        ? err.message
                        : 'Failed to process task'
                );
            }
        },
        [processTask, loadTasks, filters]
    );

    // Memoize task statistics
    const taskStats = useMemo(() => {
        const completed = tasks.filter((t) => t.status === 'completed').length;
        const pending = tasks.filter((t) => t.status === 'pending').length;
        const running = tasks.filter((t) => t.status === 'running').length;
        const failed = tasks.filter((t) => t.status === 'failed').length;

        return {completed, pending, running, failed, total: tasks.length};
    }, [tasks]);

    return (
        <div className='space-y-6'>
            {/* User Welcome Section */}
            <Card className='flex flex-col md:flex-row md:items-center md:justify-between gap-4'>
                <div>
                    <h2 className='text-2xl font-bold text-gray-900 mb-1'>
                        👋 Welcome, {user?.full_name || 'User'}!
                    </h2>
                    <p className='text-gray-600 text-sm'>{user?.email}</p>
                </div>
                <Button
                    variant='ghost'
                    onClick={() => logout()}
                    className='w-full md:w-auto'
                >
                    🚪 Logout
                </Button>
            </Card>

            {/* Task Statistics */}
            <div className='grid grid-cols-2 md:grid-cols-5 gap-3'>
                <Card className='!p-4 text-center'>
                    <p className='text-gray-600 text-sm font-medium'>Total</p>
                    <p className='text-3xl font-bold text-gray-900 mt-1'>
                        {taskStats.total}
                    </p>
                </Card>
                <Card className='!p-4 text-center'>
                    <p className='text-gray-600 text-sm font-medium'>Pending</p>
                    <p className='text-3xl font-bold text-amber-600 mt-1'>
                        {taskStats.pending}
                    </p>
                </Card>
                <Card className='!p-4 text-center'>
                    <p className='text-gray-600 text-sm font-medium'>Running</p>
                    <p className='text-3xl font-bold text-blue-600 mt-1'>
                        {taskStats.running}
                    </p>
                </Card>
                <Card className='!p-4 text-center'>
                    <p className='text-gray-600 text-sm font-medium'>
                        Completed
                    </p>
                    <p className='text-3xl font-bold text-green-600 mt-1'>
                        {taskStats.completed}
                    </p>
                </Card>
                <Card className='!p-4 text-center'>
                    <p className='text-gray-600 text-sm font-medium'>Failed</p>
                    <p className='text-3xl font-bold text-red-600 mt-1'>
                        {taskStats.failed}
                    </p>
                </Card>
            </div>

            {/* Create Task Section */}
            <Card>
                <div className='flex items-center justify-between mb-4'>
                    <h3 className='text-xl font-bold text-gray-900 flex items-center gap-2'>
                        ✨ Create New Task
                    </h3>
                    <Button
                        variant='primary'
                        size='sm'
                        onClick={() => setShowCreateForm(!showCreateForm)}
                    >
                        {showCreateForm ? '✕ Cancel' : '+ Add Task'}
                    </Button>
                </div>

                {showCreateForm && (
                    <form
                        className='space-y-5 border-t border-gray-200 pt-5'
                        onSubmit={handleCreateTask}
                    >
                        <div className='grid grid-cols-1 md:grid-cols-2 gap-5'>
                            {/* Title */}
                            <div>
                                <label className='block text-sm font-medium text-gray-900 mb-2'>
                                    Title *
                                </label>
                                <input
                                    type='text'
                                    value={title}
                                    onChange={(e) => setTitle(e.target.value)}
                                    placeholder='Task title'
                                    className='input-glass w-full'
                                    maxLength={200}
                                    required
                                    aria-label='Task title'
                                />
                            </div>

                            {/* Priority */}
                            <div>
                                <label className='block text-sm font-medium text-gray-900 mb-2'>
                                    Priority
                                </label>
                                <select
                                    value={priority}
                                    onChange={(e) =>
                                        setPriority(
                                            e.target.value as TaskPriority
                                        )
                                    }
                                    className='input-glass w-full'
                                    aria-label='Priority'
                                >
                                    <option value='low'>🟢 Low</option>
                                    <option value='medium'>🟡 Medium</option>
                                    <option value='high'>🔴 High</option>
                                </select>
                            </div>

                            {/* Run At */}
                            <div>
                                <label className='block text-sm font-medium text-gray-900 mb-2'>
                                    Schedule Date & Time *
                                </label>
                                <input
                                    type='datetime-local'
                                    value={runAt}
                                    onChange={(e) => setRunAt(e.target.value)}
                                    className='input-glass w-full'
                                    required
                                    aria-label='Schedule'
                                />
                            </div>

                            {/* Max Retries */}
                            <div>
                                <label className='block text-sm font-medium text-gray-900 mb-2'>
                                    Max Retries
                                </label>
                                <input
                                    type='number'
                                    min={0}
                                    max={10}
                                    value={maxRetries}
                                    onChange={(e) =>
                                        setMaxRetries(Number(e.target.value))
                                    }
                                    className='input-glass w-full'
                                    aria-label='Max retries'
                                />
                            </div>
                        </div>

                        {/* Description - Full Width */}
                        <div>
                            <label className='block text-sm font-medium text-gray-900 mb-2'>
                                Description
                            </label>
                            <textarea
                                value={description}
                                onChange={(e) => setDescription(e.target.value)}
                                placeholder='Task description (optional)'
                                className='input-glass w-full resize-none'
                                rows={4}
                                aria-label='Description'
                            />
                        </div>

                        {/* Actions */}
                        <div className='flex gap-3'>
                            <Button
                                type='submit'
                                variant='primary'
                                isLoading={isLoading}
                                className='flex-1'
                            >
                                ✓ Create Task
                            </Button>
                            <Button
                                type='button'
                                variant='ghost'
                                onClick={() => {
                                    setShowCreateForm(false);
                                    setCreateError('');
                                }}
                                className='flex-1'
                            >
                                Cancel
                            </Button>
                        </div>

                        {createError && (
                            <Feedback
                                type='error'
                                message={createError}
                                onDismiss={() => setCreateError('')}
                            />
                        )}
                    </form>
                )}
            </Card>

            {/* Tasks List Section */}
            <Card>
                <div className='mb-5'>
                    <h3 className='text-xl font-bold text-gray-900 mb-4'>
                        📋 Your Tasks
                    </h3>
                    <SearchInput
                        onSearch={handleSearch}
                        placeholder='🔍 Search tasks by title or description...'
                    />
                </div>

                <TaskList
                    tasks={tasks}
                    isLoading={isLoading}
                    onStatusChange={handleStatusChange}
                    onProcess={handleProcessTask}
                    onDelete={handleDeleteTask}
                    virtualizeThreshold={50}
                />
            </Card>

            {/* Global Messages */}
            <div className='fixed bottom-6 right-6 space-y-3 max-w-sm z-50'>
                {localError && (
                    <Feedback
                        type='error'
                        message={localError}
                        onDismiss={() => setLocalError('')}
                    />
                )}
                {localMessage && (
                    <Feedback
                        type='success'
                        message={localMessage}
                        onDismiss={() => setLocalMessage('')}
                    />
                )}
            </div>
        </div>
    );
}

export default TasksPage;
