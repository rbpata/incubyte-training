import {
    createContext,
    useContext,
    useReducer,
    useCallback,
    useMemo
} from 'react';
import type {Task, TaskFilters, TasksResponse} from '../types/index';

interface TasksState {
    items: Task[];
    selectedTask: Task | null;
    filters: TaskFilters;
    total: number;
    isLoading: boolean;
    error: string | null;
    pages: number;
}

export type TasksAction =
    | {type: 'LOAD_START'}
    | {type: 'LOAD_SUCCESS'; payload: TasksResponse}
    | {type: 'LOAD_FAILURE'; payload: string}
    | {type: 'SELECT_TASK'; payload: Task | null}
    | {type: 'UPDATE_FILTERS'; payload: Partial<TaskFilters>}
    | {type: 'ADD_TASK'; payload: Task}
    | {type: 'UPDATE_TASK'; payload: Task}
    | {type: 'DELETE_TASK'; payload: number}
    | {type: 'CLEAR_ERROR'}
    | {type: 'RESET_FILTERS'};

interface TasksContextType extends TasksState {
    dispatch: (action: TasksAction) => void;
    loadTasks: (filters: TaskFilters) => void;
    selectTask: (task: Task | null) => void;
    updateFilters: (filters: Partial<TaskFilters>) => void;
    addTask: (task: Task) => void;
    updateTask: (task: Task) => void;
    deleteTask: (taskId: number) => void;
    clearError: () => void;
    resetFilters: () => void;
}

const TasksContext = createContext<TasksContextType | undefined>(undefined);

const defaultFilters: TaskFilters = {
    search: '',
    status: 'all',
    sortBy: 'created_at',
    sortOrder: 'desc',
    page: 1,
    size: 10
};

const initialState: TasksState = {
    items: [],
    selectedTask: null,
    filters: defaultFilters,
    total: 0,
    isLoading: false,
    error: null,
    pages: 0
};

function tasksReducer(state: TasksState, action: TasksAction): TasksState {
    switch (action.type) {
        case 'LOAD_START':
            return {...state, isLoading: true, error: null};

        case 'LOAD_SUCCESS':
            return {
                ...state,
                items: action.payload.items,
                total: action.payload.total,
                pages: action.payload.pages,
                isLoading: false,
                error: null
            };

        case 'LOAD_FAILURE':
            return {...state, isLoading: false, error: action.payload};

        case 'SELECT_TASK':
            return {...state, selectedTask: action.payload};

        case 'UPDATE_FILTERS':
            return {
                ...state,
                filters: {...state.filters, ...action.payload}
            };

        case 'ADD_TASK':
            return {
                ...state,
                items: [action.payload, ...state.items],
                total: state.total + 1
            };

        case 'UPDATE_TASK':
            return {
                ...state,
                items: state.items.map((item) =>
                    item.id === action.payload.id ? action.payload : item
                )
            };

        case 'DELETE_TASK':
            return {
                ...state,
                items: state.items.filter((item) => item.id !== action.payload),
                total: state.total - 1
            };

        case 'CLEAR_ERROR':
            return {...state, error: null};

        case 'RESET_FILTERS':
            return {...state, filters: defaultFilters};

        default:
            return state;
    }
}

interface TasksProviderProps {
    children: React.ReactNode;
}

export function TasksProvider({children}: TasksProviderProps) {
    const [state, dispatch] = useReducer(tasksReducer, initialState);

    const loadTasks = useCallback((filters: TaskFilters) => {
        dispatch({type: 'UPDATE_FILTERS', payload: filters});
        dispatch({type: 'LOAD_START'});
    }, []);

    const selectTask = useCallback((task: Task | null) => {
        dispatch({type: 'SELECT_TASK', payload: task});
    }, []);

    const updateFilters = useCallback((filters: Partial<TaskFilters>) => {
        dispatch({type: 'UPDATE_FILTERS', payload: filters});
    }, []);

    const addTask = useCallback((task: Task) => {
        dispatch({type: 'ADD_TASK', payload: task});
    }, []);

    const updateTask = useCallback((task: Task) => {
        dispatch({type: 'UPDATE_TASK', payload: task});
    }, []);

    const deleteTask = useCallback((taskId: number) => {
        dispatch({type: 'DELETE_TASK', payload: taskId});
    }, []);

    const clearError = useCallback(() => {
        dispatch({type: 'CLEAR_ERROR'});
    }, []);

    const resetFilters = useCallback(() => {
        dispatch({type: 'RESET_FILTERS'});
    }, []);

    const value: TasksContextType = useMemo(
        () => ({
            ...state,
            dispatch,
            loadTasks,
            selectTask,
            updateFilters,
            addTask,
            updateTask,
            deleteTask,
            clearError,
            resetFilters
        }),
        [
            state,
            loadTasks,
            selectTask,
            updateFilters,
            addTask,
            updateTask,
            deleteTask,
            clearError,
            resetFilters
        ]
    );

    return (
        <TasksContext.Provider value={value}>{children}</TasksContext.Provider>
    );
}

export function useTasks() {
    const context = useContext(TasksContext);
    if (context === undefined) {
        throw new Error('useTasks must be used within a TasksProvider');
    }
    return context;
}
