import { defineConfig } from 'vitest/config';
import react from '@vitejs/plugin-react';

const target = process.env.API_PROXY_TARGET || 'http://localhost:8000';
export default defineConfig({
  plugins: [react()],
  server: {
    host: '0.0.0.0',
    proxy: Object.fromEntries(
      ['/api-auth', '/api', '/core', '/django-admin', '/media', '/static2'].map(
        (path) => [path, { target, changeOrigin: false }],
      ),
    ),
  },
  test: {
    environment: 'jsdom',
    globals: true,
    setupFiles: ['./src/test/setup.ts'],
  },
});
