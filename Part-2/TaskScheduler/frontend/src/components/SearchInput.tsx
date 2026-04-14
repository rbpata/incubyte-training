import {memo, useState, useCallback, useEffect, useRef} from 'react';
import {useDebounce} from '../hooks/useDebounce';

interface SearchInputProps {
    onSearch: (query: string) => void;
    placeholder?: string;
    debounceDelay?: number;
    icon?: React.ReactNode;
}

function SearchInputComponent({
    onSearch,
    placeholder = 'Search tasks...',
    debounceDelay = 300,
    icon = '🔍'
}: SearchInputProps) {
    const [inputValue, setInputValue] = useState('');
    const debouncedValue = useDebounce(inputValue, debounceDelay);
    const onSearchRef = useRef(onSearch);

    useEffect(() => {
        onSearchRef.current = onSearch;
    });

    useEffect(() => {
        onSearchRef.current(debouncedValue);
    }, [debouncedValue]);

    const handleChange = useCallback(
        (e: React.ChangeEvent<HTMLInputElement>) => {
            setInputValue(e.target.value);
        },
        []
    );

    const handleClear = useCallback(() => {
        setInputValue('');
    }, []);

    return (
        <div className='relative'>
            <div className='absolute left-4 top-1/2 transform -translate-y-1/2 text-gray-400 pointer-events-none'>
                {icon}
            </div>
            <input
                type='text'
                value={inputValue}
                onChange={handleChange}
                placeholder={placeholder}
                className='input-glass w-full pl-12 pr-10'
                aria-label='Search'
            />
            {inputValue && (
                <button
                    type='button'
                    onClick={handleClear}
                    aria-label='Clear search'
                    className='absolute right-3 top-1/2 transform -translate-y-1/2 text-gray-400 hover:text-gray-600 transition-colors'
                >
                    ✕
                </button>
            )}
        </div>
    );
}

export const SearchInput = memo(SearchInputComponent);
SearchInput.displayName = 'SearchInput';
