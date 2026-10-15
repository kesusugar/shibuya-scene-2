import { defineConfig } from 'vite';

export default defineConfig({
  base: process.env.VITE_BASE_PATH || "/",
  server: { host: '127.0.0.1', port: 5180 },
  build: { target: 'es2022', chunkSizeWarningLimit: 900 },
  test: { environment: 'node', include: ['tests/**/*.test.ts'] },
} as never);
