import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { render, screen, fireEvent, act } from '@testing-library/react'
import { SearchInput } from '../SearchInput'

describe('SearchInput', () => {
  beforeEach(() => {
    vi.useFakeTimers()
  })

  afterEach(() => {
    vi.useRealTimers()
    vi.clearAllMocks()
  })

  describe('rendering', () => {
    it('renders input with default placeholder', () => {
      const onSearch = vi.fn()
      render(<SearchInput onSearch={onSearch} />)

      expect(screen.getByRole('textbox', { name: 'Search' })).toBeDefined()
      expect(screen.getByPlaceholderText('Search tasks...')).toBeDefined()
    })

    it('renders input with custom placeholder', () => {
      const onSearch = vi.fn()
      render(<SearchInput onSearch={onSearch} placeholder='Find items...' />)

      expect(screen.getByPlaceholderText('Find items...')).toBeDefined()
    })

    it('does not show clear button when input is empty', () => {
      const onSearch = vi.fn()
      render(<SearchInput onSearch={onSearch} />)

      expect(screen.queryByRole('button', { name: 'Clear search' })).toBeNull()
    })

    it('shows clear button when input has value', () => {
      const onSearch = vi.fn()
      render(<SearchInput onSearch={onSearch} />)

      const input = screen.getByRole('textbox', { name: 'Search' })
      fireEvent.change(input, { target: { value: 'hello' } })

      expect(screen.getByRole('button', { name: 'Clear search' })).toBeDefined()
    })
  })

  describe('clear button', () => {
    it('clears input value when clear button is clicked', () => {
      const onSearch = vi.fn()
      render(<SearchInput onSearch={onSearch} />)

      const input = screen.getByRole('textbox', { name: 'Search' })
      fireEvent.change(input, { target: { value: 'some text' } })

      const clearButton = screen.getByRole('button', { name: 'Clear search' })
      fireEvent.click(clearButton)

      expect((input as HTMLInputElement).value).toBe('')
    })

    it('hides clear button after clearing input', () => {
      const onSearch = vi.fn()
      render(<SearchInput onSearch={onSearch} />)

      const input = screen.getByRole('textbox', { name: 'Search' })
      fireEvent.change(input, { target: { value: 'some text' } })
      fireEvent.click(screen.getByRole('button', { name: 'Clear search' }))

      expect(screen.queryByRole('button', { name: 'Clear search' })).toBeNull()
    })
  })

  describe('debounced search', () => {
    it('calls onSearch with empty string on mount', () => {
      const onSearch = vi.fn()
      render(<SearchInput onSearch={onSearch} debounceDelay={300} />)

      expect(onSearch).toHaveBeenCalledWith('')
    })

    it('does not call onSearch immediately on typing', () => {
      const onSearch = vi.fn()
      render(<SearchInput onSearch={onSearch} debounceDelay={300} />)

      onSearch.mockClear()

      const input = screen.getByRole('textbox', { name: 'Search' })
      fireEvent.change(input, { target: { value: 'hello' } })

      expect(onSearch).not.toHaveBeenCalled()
    })

    it('calls onSearch after debounce delay', () => {
      const onSearch = vi.fn()
      render(<SearchInput onSearch={onSearch} debounceDelay={300} />)

      onSearch.mockClear()

      const input = screen.getByRole('textbox', { name: 'Search' })
      fireEvent.change(input, { target: { value: 'hello' } })

      act(() => {
        vi.advanceTimersByTime(300)
      })

      expect(onSearch).toHaveBeenCalledWith('hello')
    })

    it('only fires once for rapid typing within delay window', () => {
      const onSearch = vi.fn()
      render(<SearchInput onSearch={onSearch} debounceDelay={300} />)

      onSearch.mockClear()

      const input = screen.getByRole('textbox', { name: 'Search' })
      fireEvent.change(input, { target: { value: 'h' } })
      fireEvent.change(input, { target: { value: 'he' } })
      fireEvent.change(input, { target: { value: 'hel' } })
      fireEvent.change(input, { target: { value: 'hell' } })
      fireEvent.change(input, { target: { value: 'hello' } })

      act(() => {
        vi.advanceTimersByTime(300)
      })

      expect(onSearch).toHaveBeenCalledOnce()
      expect(onSearch).toHaveBeenCalledWith('hello')
    })

    it('respects custom debounceDelay', () => {
      const onSearch = vi.fn()
      render(<SearchInput onSearch={onSearch} debounceDelay={500} />)

      onSearch.mockClear()

      const input = screen.getByRole('textbox', { name: 'Search' })
      fireEvent.change(input, { target: { value: 'query' } })

      act(() => {
        vi.advanceTimersByTime(499)
      })

      expect(onSearch).not.toHaveBeenCalled()

      act(() => {
        vi.advanceTimersByTime(1)
      })

      expect(onSearch).toHaveBeenCalledWith('query')
    })

    it('calls onSearch with empty string after clearing input via clear button', () => {
      const onSearch = vi.fn()
      render(<SearchInput onSearch={onSearch} debounceDelay={300} />)

      const input = screen.getByRole('textbox', { name: 'Search' })
      fireEvent.change(input, { target: { value: 'hello' } })

      act(() => {
        vi.advanceTimersByTime(300)
      })

      onSearch.mockClear()

      fireEvent.click(screen.getByRole('button', { name: 'Clear search' }))

      act(() => {
        vi.advanceTimersByTime(300)
      })

      expect(onSearch).toHaveBeenCalledWith('')
    })
  })
})
