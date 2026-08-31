/// <reference types="vitest/config" />
import react from '@vitejs/plugin-react'
import { defineConfig } from 'vite'

const API_TARGET = 'http://127.0.0.1:8000'
const API_PREFIXES = [
  '/sessions',
  '/chat',
  '/workspace',
  '/agents',
  '/credentials',
  '/model',
  '/openarch',
  '/health',
]

export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    proxy: Object.fromEntries(
      API_PREFIXES.map((p) => [p, { target: API_TARGET, changeOrigin: true }]),
    ),
  },
  test: {
    environment: 'node',
    include: ['src/**/*.test.ts'],
  },
})
