import {memo, useMemo} from 'react';
import {TaskItem} from './TaskItem';
import {Skeleton} from './ui';
import type {Task, TaskStatus} from '../types/index';

interface TaskListProps {
    tasks: Task[];
    isLoading: boolean;
    onStatusChange: (taskId: number, status: TaskStatus) => Promise<void>;
    onProcess: (taskId: number) => Promise<void>;
    onDelete: (taskId: number) => Promise<void>;
    virtualizeThreshold?: number;
}

function TaskListComponent({
    tasks,
    isLoading,
    onStatusChange,
    onProcess,
    onDelete
}: TaskListProps) {
    const taskElements = useMemo(() => {
        return tasks.map((task) => (
            <TaskItem
                key={task.id}
                task={task}
                onStatusChange={onStatusChange}
                onProcess={onProcess}
                onDelete={onDelete}
            />
        ));
    }, [tasks, onStatusChange, onProcess, onDelete]);

    if (isLoading) {
        return (
            <div className='space-y-4'>
                <Skeleton count={3} height='h-32' />
            </div>
        );
    }

    if (tasks.length === 0) {
        return (
            <div className='glass-card text-center py-12'>
                <p className='text-gray-500 text-lg'>
                    📭 No tasks yet. Create one to get started!
                </p>
            </div>
        );
    }

    return <div className='task-grid space-y-4'>{taskElements}</div>;
}

export const TaskList = memo(TaskListComponent);
TaskList.displayName = 'TaskList';
