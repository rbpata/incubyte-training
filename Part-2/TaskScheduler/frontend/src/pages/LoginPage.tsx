import {useState, useCallback} from 'react';
import {useAuthApi} from '../hooks/useAuthApi';
import {Feedback, Button, Card} from '../components/ui';
import type {AuthMode} from '../types/index';

export function LoginPage() {
    const [mode, setMode] = useState<AuthMode>('login');
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [fullName, setFullName] = useState('');
    const [localError, setLocalError] = useState('');
    const [localMessage, setLocalMessage] = useState('');
    const [showPassword, setShowPassword] = useState(false);

    const {login, register, isLoading, error} = useAuthApi();

    const handleSubmit = useCallback(
        async (e: React.FormEvent<HTMLFormElement>) => {
            e.preventDefault();
            setLocalError('');
            setLocalMessage('');

            if (!email.includes('@')) {
                setLocalError('Please enter a valid email address');
                return;
            }

            if (password.length < 8) {
                setLocalError('Password must be at least 8 characters');
                return;
            }

            try {
                if (mode === 'register') {
                    if (!fullName.trim()) {
                        setLocalError('Full name is required');
                        return;
                    }
                    await register(email, password, fullName);
                    setLocalMessage('✓ Registration successful. Please login.');
                    setMode('login');
                    setEmail('');
                    setPassword('');
                    setFullName('');
                } else {
                    await login(email, password);
                    setLocalMessage('✓ Login successful!');
                }
            } catch (err) {
                setLocalError(
                    err instanceof Error ? err.message : 'An error occurred'
                );
            }
        },
        [email, password, fullName, mode, login, register]
    );

    const displayError = error || localError;
    const displayMessage = localMessage;

    return (
        <div className='min-h-screen flex items-center justify-center px-4 py-8'>
            <Card className='w-full max-w-md' variant='default'>
                <div className='text-center mb-8'>
                    <div className='text-5xl mb-3'>🔐</div>
                    <h2 className='text-3xl font-bold text-gray-900 mb-2'>
                        {mode === 'login' ? 'Welcome Back' : 'Create Account'}
                    </h2>
                    <p className='text-gray-600'>
                        {mode === 'login'
                            ? 'Sign in to manage your tasks'
                            : 'Join us to get started with task scheduling'}
                    </p>
                </div>

                <form className='space-y-5' onSubmit={handleSubmit}>
                    <div>
                        <label className='block text-sm font-medium text-gray-900 mb-2'>
                            Email Address
                        </label>
                        <input
                            type='email'
                            value={email}
                            onChange={(e) => setEmail(e.target.value)}
                            placeholder='you@example.com'
                            className='input-glass w-full'
                            required
                            aria-label='Email'
                        />
                    </div>

                    <div>
                        <label className='block text-sm font-medium text-gray-900 mb-2'>
                            Password
                        </label>
                        <div className='relative'>
                            <input
                                type={showPassword ? 'text' : 'password'}
                                value={password}
                                onChange={(e) => setPassword(e.target.value)}
                                placeholder='••••••••'
                                className='input-glass w-full pr-10'
                                required
                                minLength={8}
                                aria-label='Password'
                            />
                            <button
                                type='button'
                                onClick={() => setShowPassword(!showPassword)}
                                className='absolute right-3 top-1/2 transform -translate-y-1/2 text-gray-400 hover:text-gray-600'
                                aria-label={
                                    showPassword
                                        ? 'Hide password'
                                        : 'Show password'
                                }
                            >
                                {showPassword ? '👁️' : '👁️‍🗨️'}
                            </button>
                        </div>
                        {mode === 'login' && (
                            <p className='text-xs text-gray-500 mt-1'>
                                Password must be at least 8 characters
                            </p>
                        )}
                    </div>

                    {mode === 'register' && (
                        <div>
                            <label className='block text-sm font-medium text-gray-900 mb-2'>
                                Full Name
                            </label>
                            <input
                                type='text'
                                value={fullName}
                                onChange={(e) => setFullName(e.target.value)}
                                placeholder='John Doe'
                                className='input-glass w-full'
                                required
                                aria-label='Full name'
                            />
                        </div>
                    )}

                    <Button
                        type='submit'
                        variant='primary'
                        isLoading={isLoading}
                        className='w-full justify-center'
                    >
                        {isLoading
                            ? 'Processing...'
                            : mode === 'login'
                              ? 'Sign In'
                              : 'Create Account'}
                    </Button>
                </form>

                <div className='mt-6 text-center border-t border-gray-200 pt-6'>
                    <p className='text-sm text-gray-600 mb-4'>
                        {mode === 'login'
                            ? "Don't have an account?"
                            : 'Already have an account?'}
                    </p>
                    <Button
                        type='button'
                        variant='ghost'
                        onClick={() => {
                            setMode(mode === 'login' ? 'register' : 'login');
                            setLocalError('');
                            setLocalMessage('');
                        }}
                        className='w-full justify-center'
                    >
                        {mode === 'login' ? '📝 Create one' : '🔑 Sign In'}
                    </Button>
                </div>

                <div className='mt-6 space-y-3'>
                    {displayError && (
                        <Feedback
                            type='error'
                            message={displayError}
                            onDismiss={() => setLocalError('')}
                        />
                    )}
                    {displayMessage && (
                        <Feedback
                            type='success'
                            message={displayMessage}
                            onDismiss={() => setLocalMessage('')}
                        />
                    )}
                </div>
            </Card>
        </div>
    );
}

export default LoginPage;
