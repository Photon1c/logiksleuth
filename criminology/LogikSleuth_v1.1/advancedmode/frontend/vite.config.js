import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    proxy: {
      '/scan': 'http://127.0.0.1:8000',
      '/config': 'http://127.0.0.1:8000',
      '/test': 'http://127.0.0.1:8000'
    }
  }
})


