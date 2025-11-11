import { defineConfig } from 'vitest/config';
import react from '@vitejs/plugin-react';

export default defineConfig({
  plugins: [react()],
  test: {
    globals: true,
    environment: 'jsdom',
    setupFiles: './src/setup.js',
    // Limit worker threads to prevent CPU overload
    pool: 'forks',
    poolOptions: {
      forks: {
        maxForks: 1,  // Limit to 1 worker to minimize CPU usage
        minForks: 1
      }
    },
    coverage: {
      provider: 'v8',
      reporter: ['text', 'json', 'html'],
      exclude: [
        'node_modules/',
        '**/*.config.js',
        '**/mockServiceWorker.js',
        'src/setup.js',
        'src/test-utils.jsx'
      ],
      thresholds: {
        lines: 80,
        functions: 80,
        branches: 80,
        statements: 80
      }
    }
  }
});
