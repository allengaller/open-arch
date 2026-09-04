/// <reference types="vitest/config" />
import react from '@vitejs/plugin-react'
import { defineConfig } from 'vite'

const API_TARGET = 'http://127.0.0.1:8000'
// 前缀与后端 OpenAPI 实测路由一致：agentscope 列表端点是单数 /agent/、/credential/。
const API_PREFIXES = [
  '/sessions',
  '/chat',
  '/workspace',
  '/agent',
  '/credential',
  '/model',
  '/openarch',
  '/health',
]

export default defineConfig({
  // Meoo CDN 为静态托管：相对 base 保证产物在任何子路径下资源可达
  base: './',
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
