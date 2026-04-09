/**
 * ErrorBoundary - Advanced error boundary component
 * - Catches errors in the component tree
 * - Displays helpful error UI with recovery options
 * - Logs errors for debugging
 * - Styled with Tailwind CSS and liquid glass effect
 */

import {Component, type ReactNode} from 'react';
import {Button} from './ui';

interface Props {
    children: ReactNode;
    fallback?: (error: Error, reset: () => void) => ReactNode;
    onError?: (error: Error, errorInfo: {componentStack: string}) => void;
}

interface State {
    hasError: boolean;
    error: Error | null;
    errorCount: number;
}

export class ErrorBoundary extends Component<Props, State> {
    constructor(props: Props) {
        super(props);
        this.state = {hasError: false, error: null, errorCount: 0};
    }

    static getDerivedStateFromError(error: Error): Omit<State, 'errorCount'> {
        return {hasError: true, error};
    }

    componentDidCatch(error: Error, errorInfo: {componentStack: string}) {
        // Log error for debugging
        console.error('🚨 Error caught by ErrorBoundary:', {
            message: error.message,
            stack: error.stack,
            componentStack: errorInfo.componentStack,
            timestamp: new Date().toISOString()
        });

        // Call custom error handler if provided
        this.props.onError?.(error, errorInfo);

        // Update error count for progressive error UI
        this.setState((prev) => ({
            errorCount: prev.errorCount + 1
        }));
    }

    reset = () => {
        this.setState({hasError: false, error: null});
    };

    render() {
        if (this.state.hasError && this.state.error) {
            const {fallback} = this.props;
            const {error, errorCount} = this.state;

            if (fallback) {
                return fallback(error, this.reset);
            }

            const isDevelopment = process.env.NODE_ENV === 'development';
            const isRepeatingError = errorCount > 3;

            return (
                <div className='min-h-screen flex items-center justify-center px-4 py-8'>
                    <div className='glass-card max-w-md w-full space-y-6 text-center'>
                        {/* Error Icon */}
                        <div className='text-6xl'>⚠️</div>

                        {/* Error Title */}
                        <div>
                            <h2 className='text-2xl font-bold text-red-600 mb-2'>
                                Oops! Something went wrong
                            </h2>
                            <p className='text-gray-600'>
                                {isRepeatingError
                                    ? "We're experiencing repeated issues. Please refresh the page."
                                    : 'An error occurred, but we can help you recover.'}
                            </p>
                        </div>

                        {/* Error Details (Dev Only) */}
                        {isDevelopment && (
                            <div className='bg-red-50 border border-red-200 rounded-lg p-4 text-left max-h-40 overflow-auto'>
                                <p className='text-xs font-mono text-red-900 whitespace-pre-wrap'>
                                    {error.message}
                                </p>
                            </div>
                        )}

                        {/* Error Stats */}
                        <div className='flex justify-around text-sm'>
                            <div className='glass-effect-sm p-3 rounded-lg'>
                                <span className='text-gray-500 block text-xs'>
                                    Error Count
                                </span>
                                <p className='font-semibold text-gray-900'>
                                    {errorCount}
                                </p>
                            </div>
                            <div className='glass-effect-sm p-3 rounded-lg'>
                                <span className='text-gray-500 block text-xs'>
                                    Environment
                                </span>
                                <p className='font-semibold text-gray-900'>
                                    {process.env.NODE_ENV}
                                </p>
                            </div>
                        </div>

                        {/* Action Buttons */}
                        <div className='flex gap-3'>
                            <Button
                                variant='primary'
                                onClick={this.reset}
                                className='flex-1'
                            >
                                🔄 Try Again
                            </Button>
                            <Button
                                variant='secondary'
                                onClick={() => (window.location.href = '/')}
                                className='flex-1'
                            >
                                🏠 Home
                            </Button>
                        </div>

                        {/* Additional Help */}
                        <p className='text-xs text-gray-500'>
                            If the problem persists, please{' '}
                            <a
                                href='mailto:support@example.com'
                                className='text-blue-500 hover:underline'
                            >
                                contact support
                            </a>
                        </p>
                    </div>
                </div>
            );
        }

        return this.props.children;
    }
}
