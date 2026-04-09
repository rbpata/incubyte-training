/**
 * Main App component with:
 * - Context providers (Auth, Tasks)
 * - Error boundary with enhanced error handling
 * - Lazy loaded pages for code splitting
 * - Liquid glass UI with Tailwind CSS
 */

import {lazy, Suspense, useEffect} from 'react';
import {AuthProvider, useAuth} from './contexts/AuthContext';
import {TasksProvider} from './contexts/TasksContext';
import {ErrorBoundary, LoadingSpinner} from './components';
import {useAuthApi} from './hooks/useAuthApi';
import './App.css';

// Lazy load pages for code splitting
const LoginPage = lazy(() => import('./pages/LoginPage'));
const TasksPage = lazy(() => import('./pages/TasksPage'));

function AppContent() {
    const {isLoggedIn} = useAuth();
    const {restoreSession} = useAuthApi();

    // Restore session from localStorage on mount
    useEffect(() => {
        restoreSession();
    }, [restoreSession]);

    return (
        <main className='app-shell'>
            <header className='hero-glass relative before:absolute before:top-0 before:left-[-100%] before:w-[200%] before:h-0.5 before:bg-gradient-to-r before:from-transparent before:via-white/40 before:to-transparent before:animate-shimmer'>
                <div className='relative z-10'>
                    <h1 className='text-4xl md:text-5xl font-bold text-gradient mb-2'>
                        Task Scheduler
                    </h1>
                    <p className='text-gray-600 text-lg'>
                        Manage your tasks efficiently with liquid glass UI.
                    </p>
                </div>
            </header>

            <ErrorBoundary>
                <Suspense fallback={<LoadingSpinner />}>
                    {!isLoggedIn ? <LoginPage /> : <TasksPage />}
                </Suspense>
            </ErrorBoundary>
        </main>
    );
}

function App() {
    return (
        <ErrorBoundary>
            <AuthProvider>
                <TasksProvider>
                    <AppContent />
                </TasksProvider>
            </AuthProvider>
        </ErrorBoundary>
    );
}

export default App;
