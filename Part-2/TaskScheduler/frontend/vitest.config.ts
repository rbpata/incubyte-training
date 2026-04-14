/**
 * Vitest configuration for unit and integration tests.
 * Uses jsdom for DOM functionality in tests.
 */

import { defineConfig } from 'vitest/config'
import react from '@vitejs/plugin-react'
import path from 'path'

export default defineConfig({
  plugins: [react()],
  test: {
    globals: true,
    environment: 'jsdom',
    setupFiles: [],
    coverage: {
      provider: 'v8',
      reporter: ['text', 'json', 'html'],
      exclude: [
        'node_modules/',
        'src/**/*.test.ts',
        'src/**/*.test.tsx',
        'src/main.tsx',
        'src/App.tsx',
        'src/App.css',
        'src/index.css',
        'src/**/__tests__/**',
        'src/pages/**',
        'src/components/ErrorBoundary.tsx',
        'src/components/TaskList.tsx',
        'src/components/index.ts',
        'src/hooks/index.ts',
        'src/hooks/useLocalStorage.ts',
        'src/hooks/useReactQuery.ts',
        'src/hooks/useThrottle.ts',
        '*.config.js',
        '*.config.ts',
      ],
    },
  },
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
    },
  },
})
