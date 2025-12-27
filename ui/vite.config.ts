import { sveltekit } from '@sveltejs/kit/vite';
import { defineConfig } from 'vite';

export default defineConfig({
	plugins: [sveltekit()],
	server: {
		port: 5173,
		proxy: {
			// Proxy API requests to backend
			'/api': {
				target: 'http://localhost:8034',
				changeOrigin: true
			},
			// Proxy WebSocket connections
			'/ws': {
				target: 'ws://localhost:8034',
				ws: true
			}
		}
	}
});
