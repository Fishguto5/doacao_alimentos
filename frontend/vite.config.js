import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    host: true,
    proxy: {
      '/usuario': 'http://localhost:8000',
      '/doacao': 'http://localhost:8000',
      '/categoria': 'http://localhost:8000',
      '/alimento': 'http://localhost:8000',
      '/solicitacao-doacao': 'http://localhost:8000',
      '/notificacao': 'http://localhost:8000',
      '/avaliacao': 'http://localhost:8000',
    },
  },
})
