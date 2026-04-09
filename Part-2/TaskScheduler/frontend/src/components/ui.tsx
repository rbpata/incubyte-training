import {memo} from 'react';

export const LoadingSpinner = memo(
    ({size = 'md'}: {size?: 'sm' | 'md' | 'lg'}) => {
        const sizeClasses = {
            sm: 'w-6 h-6 border-2',
            md: 'w-10 h-10 border-4',
            lg: 'w-16 h-16 border-4'
        };

        return (
            <div
                className={`${sizeClasses[size]} inline-block border-gray-300 border-t-blue-500 rounded-full animate-spin`}
                role='status'
                aria-label='Loading'
            />
        );
    }
);
LoadingSpinner.displayName = 'LoadingSpinner';

interface FeedbackProps {
    type: 'error' | 'success' | 'info' | 'warning';
    message: string;
    onDismiss?: () => void;
    icon?: React.ReactNode;
}

export const Feedback = memo(
    ({type, message, onDismiss, icon}: FeedbackProps) => {
        const baseClasses = 'feedback-' + type;

        const defaultIcons: Record<typeof type, string> = {
            error: '⚠️',
            success: '✓',
            info: 'ℹ️',
            warning: '⚡'
        };

        return (
            <div
                className={`${baseClasses} px-4 py-3 rounded-lg backdrop-blur border flex items-center gap-3 animate-slide-in`}
                role='alert'
            >
                <span className='text-lg'>{icon || defaultIcons[type]}</span>
                <p className='flex-1'>{message}</p>
                {onDismiss && (
                    <button
                        onClick={onDismiss}
                        aria-label='Dismiss'
                        className='ml-2 text-lg hover:opacity-70 transition-opacity'
                    >
                        ✕
                    </button>
                )}
            </div>
        );
    }
);
Feedback.displayName = 'Feedback';

interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
    variant?: 'primary' | 'secondary' | 'ghost' | 'danger';
    size?: 'sm' | 'md' | 'lg';
    isLoading?: boolean;
    icon?: React.ReactNode;
}

export const Button = memo(
    ({
        variant = 'primary',
        size = 'md',
        isLoading = false,
        disabled,
        icon,
        children,
        className,
        ...props
    }: ButtonProps) => {
        const baseClasses = {
            primary:
                'bg-blue-500/90 text-white hover:bg-blue-600 hover:shadow-lg shadow-md active:translate-y-0 hover:translate-y-[-1px]',
            secondary:
                'glass-effect-sm text-gray-900 border-gray-300/50 hover:bg-white/70 hover:border-blue-500/30',
            ghost: 'bg-transparent text-gray-900 border border-gray-300 hover:bg-white/40 hover:border-gray-400',
            danger: 'bg-red-500/90 text-white hover:bg-red-600 hover:shadow-lg shadow-md'
        };

        const sizeClasses = {
            sm: 'px-3 py-2 text-sm',
            md: 'px-5 py-3 text-base',
            lg: 'px-6 py-4 text-lg'
        };

        const finalClassName = `
      ${baseClasses[variant]}
      ${sizeClasses[size]}
      font-medium rounded-xl
      inline-flex items-center justify-center gap-2
      transition-all duration-200
      disabled:opacity-50 disabled:cursor-not-allowed disabled:transform-none
      ${className || ''}
    `.trim();

        return (
            <button
                disabled={disabled || isLoading}
                className={finalClassName}
                {...props}
            >
                {icon && <span className='flex-shrink-0'>{icon}</span>}
                <span>{isLoading ? 'Loading...' : children}</span>
            </button>
        );
    }
);
Button.displayName = 'Button';

interface CardProps extends React.HTMLAttributes<HTMLDivElement> {
    variant?: 'default' | 'minimal' | 'interactive';
}

export const Card = memo(
    ({variant = 'default', className, children, ...props}: CardProps) => {
        const baseClasses = {
            default: 'glass-card p-6 md:p-8',
            minimal: 'glass-effect-sm p-4',
            interactive: 'glass-card-interactive p-6 md:p-8 cursor-pointer'
        };

        return (
            <div
                className={`${baseClasses[variant]} ${className || ''}`}
                {...props}
            >
                {children}
            </div>
        );
    }
);
Card.displayName = 'Card';

interface BadgeProps extends React.HTMLAttributes<HTMLSpanElement> {
    variant?: 'default' | 'success' | 'warning' | 'danger' | 'info';
    size?: 'sm' | 'md';
}

export const Badge = memo(
    ({variant = 'default', size = 'sm', className, children}: BadgeProps) => {
        const variantClasses = {
            default: 'bg-gray-100 text-gray-800',
            success: 'bg-green-100 text-green-800',
            warning: 'bg-amber-100 text-amber-800',
            danger: 'bg-red-100 text-red-800',
            info: 'bg-blue-100 text-blue-800'
        };

        const sizeClasses = {
            sm: 'px-2.5 py-0.5 text-xs',
            md: 'px-3 py-1 text-sm'
        };

        return (
            <span
                className={`${variantClasses[variant]} ${sizeClasses[size]} rounded-full font-medium inline-flex items-center gap-1 ${className || ''}`}
            >
                {children}
            </span>
        );
    }
);
Badge.displayName = 'Badge';

interface SkeletonProps extends React.HTMLAttributes<HTMLDivElement> {
    count?: number;
    height?: string;
}

export const Skeleton = memo(
    ({count = 1, height = 'h-4', className}: SkeletonProps) => (
        <div className='space-y-2'>
            {Array.from({length: count}).map((_, i) => (
                <div
                    key={i}
                    className={`${height} bg-gray-200 rounded animate-pulse ${className || ''}`}
                />
            ))}
        </div>
    )
);
Skeleton.displayName = 'Skeleton';
