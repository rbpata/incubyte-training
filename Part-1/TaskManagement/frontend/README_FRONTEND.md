# Task Management Frontend

A clean, straightforward React + TypeScript + Tailwind CSS frontend for the Task Management API.

## Features

- **Authentication**: Sign up and login with username, email, and password
- **Task Management**: Create, read, update, and delete tasks
- **Task Filtering**: Filter tasks by status (all, active, completed)
- **Persistent Auth**: Auth token stored in localStorage for session persistence
- **Clean UI**: Built with Tailwind CSS for a modern, responsive design

## Tech Stack

- **React 19** - UI library
- **TypeScript** - Type safety
- **Vite** - Build tool and dev server
- **React Router 7** - Client-side routing
- **Tailwind CSS 4** - Styling

## Project Structure

```
src/
├── components/        # Reusable UI components
│   ├── TaskCard.tsx       # Individual task display
│   ├── TaskList.tsx       # Task list with filtering
│   └── TaskForm.tsx       # Task creation form
├── pages/             # Page components (routes)
│   ├── LoginPage.tsx      # Login page
│   ├── SignupPage.tsx     # Sign up page
│   └── TasksPage.tsx      # Main tasks dashboard
├── hooks/             # Custom React hooks
│   ├── useAuth.ts         # Authentication logic
│   └── useTasks.ts        # Task management logic
├── lib/               # Utilities and API client
│   ├── api.ts             # API client with fetch wrapper
│   └── auth.ts            # Token management utilities
├── App.tsx            # Main app with routing
├── main.tsx           # Entry point
└── index.css          # Tailwind styles
```

## Setup & Running

### Prerequisites
- Node.js 18+ and pnpm

### Installation

1. Install dependencies:
```bash
pnpm install
```

2. Start the development server:
```bash
pnpm dev
```

The app will be available at `http://localhost:5174/` (or the next available port if 5174 is in use).

### Backend Requirements

The frontend expects the Task Management API to be running on `http://localhost:8000`. Make sure the backend is running before testing the auth flow.

The backend should have CORS enabled to allow requests from `http://localhost:5173` and `http://localhost:5174`.

## How It Works

### Authentication Flow

1. **Sign Up**: New users create an account with username, email, and password
2. **Redirect**: After signup, users are redirected to the login page
3. **Login**: Users authenticate with username and password
4. **Token Storage**: Access token is stored in localStorage for subsequent requests
5. **Session Persistence**: The app checks for an existing token on load and restores the user session

### Task Management

1. **Create**: Users fill out the task form with title and optional description
2. **Display**: All tasks are shown in a filterable list
3. **Toggle**: Click the checkbox to mark tasks as completed/active
4. **Delete**: Remove tasks with the delete button
5. **Filter**: Switch between viewing all, active, or completed tasks

### API Integration

All API calls go through the `apiClient` singleton in `src/lib/api.ts`, which handles:
- Token attachment to requests
- Error handling and user-friendly messages
- Type-safe request/response handling

## Development Notes

### Simple & Minimal Hooks

- **No Context API**: Uses simple `useState` for component-level state
- **No useReducer**: Task and auth state managed directly via `useState`
- **No complex libraries**: Raw fetch for API calls (no React Query, Swr, or Axios)
- **Hooks are focused**: `useAuth` for login/signup/logout, `useTasks` for CRUD operations

### Component Philosophy

- **Small & focused**: Each component has a single responsibility
- **Presentational**: UI components receive all data via props
- **No nested ternaries**: Early returns and clear conditional logic
- **Tailwind only**: No custom CSS (except Tailwind directives in index.css)

## Build & Production

Build for production:
```bash
pnpm build
```

The optimized bundle will be in the `dist/` directory.

Preview the production build locally:
```bash
pnpm preview
```
