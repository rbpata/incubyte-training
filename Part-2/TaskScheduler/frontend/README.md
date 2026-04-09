# Task Scheduler Frontend

Modern React frontend for the Task Scheduler application built with advanced UI patterns, clean code principles, and test-driven development.

## Features

- ✅ **React Context API** - Global state management for Auth and Tasks
- ✅ **Custom Hooks** - Reusable API logic and utilities
- ✅ **useReducer** - Predictable state updates
- ✅ **Code Splitting** - Lazy loading pages for smaller bundle
- ✅ **Debouncing** - Optimized search input
- ✅ **React.memo** - Performance optimizations
- ✅ **useMemo** - Computed values caching
- ✅ **Error Boundaries** - Graceful error handling
- ✅ **TDD** - Unit tests with Vitest
- ✅ **Clean Code** - Single responsibility, DRY, separation of concerns

## Tech Stack

- **React 19** - UI framework
- **TypeScript** - Type safety
- **Vite** - Fast build tool
- **Vitest** - Unit testing
- **@testing-library/react** - Component testing

## Project Structure

See [ARCHITECTURE.md](./ARCHITECTURE.md) for detailed structure and patterns.

```
src/
├── types/      # TypeScript definitions
├── contexts/   # Global state (Auth, Tasks)
├── hooks/      # Custom hooks
├── utils/      # Utilities (API, storage, debounce)
├── components/ # React components
├── pages/      # Page components (lazy loaded)
└── App.tsx     # Main component
```

## Getting Started

### Installation

```bash
# Install dependencies
pnpm install
```

### Development

```bash
# Start dev server (http://localhost:5173)
pnpm dev
```

### Build

```bash
# Production build
pnpm build

# Preview production build
pnpm preview
```

### Testing

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

### Linting

```bash
# Run ESLint
pnpm lint
```

## Environment Variables

Create a `.env` file:

```env
VITE_API_BASE_URL=http://localhost:8000
```

## API Conventions

All API calls go through `apiClient` singleton in `src/utils/api.ts`.

## State Management

### Auth Context
```typescript
const { isLoggedIn, user, login, logout } = useAuth()
```

### Tasks Context
```typescript
const { items, filters, updateFilters } = useTasks()
```

## Custom Hooks

- `useApi<T>()` - Generic API calls
- `useDebounce(value, delay)` - Debounce any value
- `useAuthApi()` - Auth operations
- `useTasksApi()` - Task operations

## Performance & Clean Code

- **Memoization**: React.memo, useMemo, useCallback
- **Debouncing**: Optimized search with useDebounce
- **Code Splitting**: Pages lazy loaded
- **Error Handling**: Error Boundary + try-catch
- **No Over-Engineering**: Context API instead of Redux

## See Also

- [ARCHITECTURE.md](./ARCHITECTURE.md) - Detailed architecture and patterns
- Backend: `../backend/README.md`
import reactDom from 'eslint-plugin-react-dom'

export default defineConfig([
  globalIgnores(['dist']),
  {
    files: ['**/*.{ts,tsx}'],
    extends: [
      // Other configs...
      // Enable lint rules for React
      reactX.configs['recommended-typescript'],
      // Enable lint rules for React DOM
      reactDom.configs.recommended,
    ],
    languageOptions: {
      parserOptions: {
        project: ['./tsconfig.node.json', './tsconfig.app.json'],
        tsconfigRootDir: import.meta.dirname,
      },
      // other options...
    },
  },
])
```
