import { defineConfig, loadEnv } from 'vite'
import react from '@vitejs/plugin-react'

// https://vitejs.dev/config/
export default ({ mode }) => {
  const env = loadEnv(mode, process.cwd(), '')
  const apiUrl = env.VITE_API_URL || 'http://localhost:8000'
  const staticUrl = env.VITE_STATIC_URL || 'http://localhost:5000'

  return defineConfig({
    plugins: [react()],
    server: {
      proxy: {
        '/api': {
          target: apiUrl,
          changeOrigin: true,
          secure: false,
        },
        '/viewer': {
          target: apiUrl,
          changeOrigin: true,
          secure: false,
        },
        '/static': {
          target: staticUrl,
          changeOrigin: true,
          secure: false,
        }
      }
    }
  })
}