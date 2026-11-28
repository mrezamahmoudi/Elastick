import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// The UI is served under /ui by the FastAPI backend (see app/main.py).
export default defineConfig({
  base: '/ui/',
  plugins: [react()],
  server: {
    port: 5173,
    // In development, forward every non-/ui request to the FastAPI backend
    // so the UI can call /diagnostics/... directly.
    proxy: {
      '^/(?!ui(@|/|$))': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
    },
  },
})
