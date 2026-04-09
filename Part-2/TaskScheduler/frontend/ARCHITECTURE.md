# Task Scheduler Frontend Architecture

This frontend follows official React patterns and clean code principles.

## Project Structure

```
src/
├── types/              # Centralized TypeScript types
│   └── index.ts
├── contexts/           # React Context API for global state
│   ├── AuthContext.tsx # Authentication state with reducer
│   └── TasksContext.tsx # Tasks state with reducer
├── hooks/              # Custom hooks for reusable logic
│   ├── useApi.ts       # Generic API call hook
│   ├── useDebounce.ts  # Debouncing hook
│   ├── useAuthApi.ts   # Auth-specific API operations
│   ├── useTasksApi.ts  # Tasks-specific API operations
│   ├── index.ts        # Centralized exports
│   └── __tests__/      # Hook tests
├── utils/              # Utility functions
│   ├── api.ts          # API client (singleton)
│   ├── debounce.ts     # Debounce and throttle utilities
│   ├── storage.ts      # Localstorage wrapper
│   └── __tests__/      # Utility tests
├── components/         # Reusable React components
│   ├── ErrorBoundary.tsx    # Error handling
│   ├── TaskItem.tsx         # Memoized task item
│   ├── TaskList.tsx         # Memoized task list with useMemo
│   ├── SearchInput.tsx      # Debounced search input
│   ├── ui.tsx              # Basic UI components
│   └── index.ts            # Centralized exports
├── pages/              # Page components (lazy loaded)
│   ├── LoginPage.tsx   # Authentication page
│   └── TasksPage.tsx   # Tasks management page
├── App.tsx             # Main app component with providers
├── main.tsx            # Entry point
└── App.css             # Global styles
```

## Key Concepts & Patterns

### 1. **Context API + useReducer**
- **AuthContext**: Manages authentication state (tokens, user)
- **TasksContext**: Manages tasks state (list, filters, selected task)
- Uses reducer pattern for predictable state updates
- Exported custom hooks (`useAuth`, `useTasks`) for easy consumption

### 2. **Custom Hooks** (Reusable Logic)
- **useApi**: Generic hook for any API endpoint
- **useDebounce**: Hook for debouncing values
- **useAuthApi**: Auth-specific operations (login, register, logout, refresh)
- **useTasksApi**: Tasks-specific operations (create, update, delete, filter)

### 3. **Component Optimization**
- **React.memo**: Prevents unnecessary re-renders (_TaskItem_, _TaskList_)
- **useMemo**: Optimizes expensive calculations in _TaskList_
- **useCallback**: Memoizes functions to prevent cascading re-renders

### 4. **Code Splitting & Lazy Loading**
- Pages are lazy loaded using `React.lazy()` and `Suspense`
- Reduces initial bundle size
- Only loads code when needed

```tsx
const LoginPage = lazy(() => import('./pages/LoginPage'))
const TasksPage = lazy(() => import('./pages/TasksPage'))
```

### 5. **Debouncing & Throttling**
- **SearchInput** uses `useDebounce` hook to delay API calls
- Prevents excessive network requests while typing
- Configurable delay (default 300ms)

### 6. **Error Handling**
- **ErrorBoundary**: Catches React errors and displays fallback UI
- **Try-catch blocks**: In async operations
- **Error states** in contexts for component-level error handling

### 7. **API Client Pattern**
- Singleton `ApiClient` class in `utils/api.ts`
- Handles base URL, headers, error parsing
- Type-safe generic methods

### 8. **Storage Wrapper**
- Safe localStorage access in `utils/storage.ts`
- Handles private browsing and quota errors
- Exported constants for storage keys

## Clean Code Principles Applied

### Single Responsibility Principle
- Each file has a single, well-defined purpose
- Components are small and focused
- Hooks are single-concern

### Don't Repeat Yourself (DRY)
- Utilities extracted (`debounce.ts`, `storage.ts`, `api.ts`)
- Custom hooks for common patterns
- Centralized type definitions

### Separation of Concerns
- UI components in `components/`
- Business logic in `hooks/` and `contexts/`
- Utilities in `utils/`
- Page layout in `pages/`

### No Over-Engineering
- Used built-in Context API instead of Redux
- Simple reducer pattern (not complex)
- Only memoize where it matters
- Linear, straightforward data flow

## Testing Strategy (TDD)

### Test Files Location
Hash all tests in `__tests__/` folders near the code they test:
- `src/hooks/__tests__/` - Hook tests
- `src/utils/__tests__/` - Utility tests

### Tools
- **Vitest**: Fast unit test runner
- **@testing-library/react**: React component testing
- **jsdom**: DOM environment for tests

### Running Tests
```bash
# Run all tests
pnpm test

# Watch mode
pnpm test -- --watch

# UI dashboard
pnpm test:ui

# Coverage report
pnpm test:coverage
```

## Flow Example: Loading Tasks

1. User navigates to TasksPage
2. `useTasksApi()` hook initializes with API operations
3. `useEffect` calls `loadTasks()` with initial filters
4. `useTasksApi` calls `apiClient.request()` to fetch from backend
5. Response updates `TasksContext` via dispatch
6. `TaskList` component reads from context and renders tasks
7. Each task is wrapped in memoized `TaskItem` for optimization
8. Search input is debounced via `useDebounce` hook

## Performance Optimizations

1. **Code Splitting**: Pages loaded on-demand
2. **Memoization**: Components prevent unnecessary re-renders
3. **Debouncing**: Search doesn't create API spam
4. **Custom Hooks**: Reusable, testable logic
5. **Singleton API Client**: Single instance, shared configuration

## Not Over-Engineered

- No Redux (Context API is sufficient)
- No state machine (simple reducer pattern)
- No GraphQL (REST is adequate)
- No complex composition (simple, readable)
- No virtual scrolling (unless needed for huge lists)

This architecture is scalable, maintainable, and easy to understand.
