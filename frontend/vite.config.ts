// vite.config.ts
// Vite reads .env and .env.local automatically.
// Variables prefixed with VITE_ are exposed to client code via import.meta.env.

import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    // Proxy /api calls to the FastAPI backend during development.
    // This avoids CORS entirely — the browser talks only to Vite.
    proxy: {
      '/api': {
        target: 'http://127.0.0.1:8000',
        changeOrigin: true,
      },
    },
  },
  build: {
    outDir: 'dist',
    sourcemap: true,
  },
})
