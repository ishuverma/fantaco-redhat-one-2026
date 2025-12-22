import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

const port = parseInt(process.env.VITE_PORT) || 3002;
console.log('VITE_PORT:', process.env.VITE_PORT);
console.log('Server port (resolved):', port);

export default defineConfig({
  plugins: [react()],
  server: {
    port,
  },
});
