<script lang="ts">
	/**
	 * AppShell - Root layout wrapper
	 *
	 * Provides:
	 * - Global error boundary
	 * - Toast notifications
	 * - Connection status indicator
	 */

	import { onMount } from 'svelte';
	import { isConnected, isConnecting, hasError } from '$lib/stores/websocket';
	import { strudelService } from '$lib/services/strudel';

	/** Strudel initialization error (if any) */
	let strudelError: string | null = null;

	/** Initialize Strudel on mount */
	onMount(async () => {
		try {
			await strudelService.initialize();
			console.log('[AppShell] Strudel audio engine initialized');
		} catch (error) {
			console.error('[AppShell] Failed to initialize Strudel:', error);
			strudelError = error instanceof Error ? error.message : 'Unknown error';
		}
	});
</script>

<div class="relative h-screen w-screen overflow-hidden">
	<!-- Main Content -->
	<slot />

	<!-- Connection Status Indicator -->
	{#if !$isConnected}
		<div
			class="fixed bottom-4 left-1/2 z-50 flex -translate-x-1/2 items-center gap-2 rounded-lg border bg-background px-4 py-2 shadow-lg"
		>
			{#if $isConnecting}
				<div class="h-2 w-2 animate-pulse rounded-full bg-yellow-500"></div>
				<span class="text-sm text-muted-foreground">Connecting...</span>
			{:else if $hasError}
				<div class="h-2 w-2 rounded-full bg-red-500"></div>
				<span class="text-sm text-destructive">Connection error</span>
			{:else}
				<div class="h-2 w-2 rounded-full bg-muted"></div>
				<span class="text-sm text-muted-foreground">Disconnected</span>
			{/if}
		</div>
	{/if}

	<!-- Strudel Error Toast -->
	{#if strudelError}
		<div
			class="fixed right-4 top-20 z-50 max-w-md rounded-lg border border-destructive bg-background p-4 shadow-lg"
		>
			<div class="mb-2 flex items-center gap-2">
				<span class="text-destructive">⚠️</span>
				<h3 class="font-semibold text-destructive">Strudel Initialization Failed</h3>
			</div>
			<p class="text-sm text-muted-foreground">{strudelError}</p>
			<p class="mt-2 text-xs text-muted-foreground">
				Make sure @strudel/web CDN script is loaded in app.html
			</p>
			<button
				class="mt-3 text-xs text-primary hover:underline"
				onclick={() => (strudelError = null)}
			>
				Dismiss
			</button>
		</div>
	{/if}
</div>
