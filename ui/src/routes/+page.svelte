<script lang="ts">
	/**
	 * Main App Page
	 *
	 * Features:
	 * - Initializes WebSocket connection
	 * - Renders main layout
	 * - Handles app-level lifecycle
	 */

	import { onMount, onDestroy } from 'svelte';
	import { browser } from '$app/environment';
	import { AppShell, MainLayout } from '$lib/components/layout';
	import { wsService } from '$lib/services/websocket';

	/** Generate UUID v4 session ID */
	function generateSessionId(): string {
		// Use crypto.randomUUID() if available (modern browsers)
		if (typeof crypto !== 'undefined' && crypto.randomUUID) {
			return crypto.randomUUID();
		}
		// Fallback for older browsers - generate UUID v4 manually
		return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, (c) => {
			const r = (Math.random() * 16) | 0;
			const v = c === 'x' ? r : (r & 0x3) | 0x8;
			return v.toString(16);
		});
	}

	/** Session ID for this app instance */
	let sessionId = '';

	onMount(() => {
		if (!browser) return;

		// Generate session ID (UUID format required by backend)
		sessionId = generateSessionId();
		console.log('[App] Session ID:', sessionId);

		// Connect WebSocket
		// Note: Connection will be established when first panel is loaded
		// For now, we'll connect immediately for testing
		try {
			wsService.connect(sessionId);
			console.log('[App] WebSocket connecting...');
		} catch (error) {
			console.error('[App] Failed to connect WebSocket:', error);
		}
	});

	onDestroy(() => {
		if (!browser) return;

		// Disconnect WebSocket
		try {
			wsService.disconnect();
			console.log('[App] WebSocket disconnected');
		} catch (error) {
			console.error('[App] Failed to disconnect WebSocket:', error);
		}
	});
</script>

<svelte:head>
	<title>Strudel Agent</title>
	<meta name="description" content="AI-powered Strudel live coding assistant" />
</svelte:head>

<AppShell>
	<MainLayout />
</AppShell>
