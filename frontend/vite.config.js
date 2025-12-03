import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    port: 5000,
    host: true, // 允许外部访问
    open: true, // 自动打开浏览器
    hmr: {
      overlay: true, // 在浏览器中显示错误覆盖层
    },
          proxy: {
            '/api': {
              target: 'http://localhost:5001',
              changeOrigin: true,
            },
          },
  },
});
