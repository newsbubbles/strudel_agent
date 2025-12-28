<script lang="ts">
	/**
	 * GlobalPlayer - Simple play/stop/update controls for current clip
	 *
	 * Features:
	 * - Play/Stop button
	 * - Update button (re-fetch current clip after agent edits)
	 * - Playing state indicator
	 * - Strudel playback controls
	 * - Only plays the currently focused clip in carousel
	 *
	 * NOTE: Strudel initialization happens in AppShell.svelte
	 * This component only controls playback.
	 *
	 * NO CLIP COMBINING - Agent handles that automatically
	 */

	import { onDestroy } from 'svelte';
	import { currentPanel } from '$lib/stores/carousel';
	import { player } from '$lib/stores/player';
	import { strudelService } from '$lib/services/strudel';
	import { apiService } from '$lib/services/api';

	let isUpdating = false;

	/** Get current clip panel (only clip panels can be played) */
	$: currentClip = $currentPanel?.type === 'clip' ? $currentPanel : null;

	/** Check if Strudel is ready (initialized in AppShell) */
	$: isInitialized = strudelService.isInitialized();

	/** Check if we can play (clip panel + Strudel initialized) */
	$: canPlay = currentClip !== null && isInitialized;

	/** Check if playing */
	$: isPlaying = $player.state === 'playing';

	/** Cleanup on unmount */
	onDestroy(() => {
		if (isPlaying) {
			strudelService.stop();
		}
	});

	/** Handle Play/Stop toggle */
	async function handlePlayStop() {
		if (!currentClip) return;

		if (isPlaying) {
			// Stop playback
			console.log('[GlobalPlayer] Stopping playback...');
			strudelService.stop();
		} else {
			// Start playback with current clip code
			const code = currentClip.code || '';
			if (!code.trim()) {
				console.warn('[GlobalPlayer] No code to play');
				return;
			}

			try {
				console.log('[GlobalPlayer] Starting playback...');
				// Load code into player first
				strudelService.updatePlayer(code);
				// Then start playback
				strudelService.play();
			} catch (error) {
				console.error('[GlobalPlayer] Failed to play clip:', error);
			}
		}
	}

	/** Handle Update - Re-fetch current clip data and update player */
	async function handleUpdate() {
		if (!currentClip) return;

		isUpdating = true;

		try {
			console.log('[GlobalPlayer] Updating clip:', currentClip.itemId);

			// Re-fetch clip data from backend
			const updatedData = await apiService.getClip(currentClip.projectId, currentClip.itemId);

			// Update panel data in carousel
			const { carousel } = await import('$lib/stores/carousel');
			carousel.updatePanel(currentClip.id, {
				code: updatedData.code,
				updatedAt: new Date(updatedData.updated_at || Date.now())
			});

			console.log('[GlobalPlayer] Clip updated successfully');

			// Update the Strudel player with new code
			const code = updatedData.code || '';
			if (code.trim()) {
				strudelService.updatePlayer(code);
				
				// If currently playing, restart with new code
				if (isPlaying) {
					strudelService.play();
				}
			}
		} catch (error) {
			console.error('[GlobalPlayer] Failed to update clip:', error);
		} finally {
			isUpdating = false;
		}
	}

	/** Auto-stop when switching away from clip panel */
	$: if (!currentClip && isPlaying) {
		strudelService.stop();
	}
</script>

<div class="flex h-16 items-center justify-between border-t bg-background px-6">
	<!-- Left: Current Item Info -->
	<div class="flex items-center gap-3">
		{#if currentClip}
			<div class="flex items-center gap-2">
				<span class="text-2xl">🎹</span>
				<div>
					<p class="text-sm font-medium">{currentClip.title || currentClip.itemId}</p>
					<p class="text-xs text-muted-foreground">
						{isPlaying ? '▶️ Playing' : 'Ready to play'}
					</p>
				</div>
			</div>
		{:else}
			<div class="flex items-center gap-2 text-muted-foreground">
				<span class="text-2xl">🎵</span>
				<p class="text-sm">No clip selected</p>
			</div>
		{/if}
	</div>

	<!-- Center: Player Controls -->
	<div class="flex items-center gap-2">
		{#if !isInitialized}
			<!-- Initializing (handled by AppShell) -->
			<div class="flex items-center gap-2 text-sm text-muted-foreground">
				<span class="animate-spin">⏳</span>
				<span>Initializing Strudel...</span>
			</div>
		{:else}
			<!-- Play/Stop Button -->
			<button
				onclick={handlePlayStop}
				disabled={!canPlay}
				class="inline-flex h-10 items-center justify-center gap-2 rounded-md px-6 text-sm font-medium transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50 {isPlaying
					? 'bg-destructive text-destructive-foreground hover:bg-destructive/90'
					: 'bg-primary text-primary-foreground hover:bg-primary/90'}"
			>
				{#if isPlaying}
					<span class="text-base">⏹️</span>
					<span>Stop</span>
				{:else}
					<span class="text-base">▶️</span>
					<span>Play</span>
				{/if}
			</button>

			<!-- Update Button -->
			<button
				onclick={handleUpdate}
				disabled={!currentClip || isUpdating}
				class="inline-flex h-10 items-center justify-center gap-2 rounded-md border border-input bg-background px-4 text-sm font-medium transition-colors hover:bg-accent hover:text-accent-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50"
			>
				{#if isUpdating}
					<span class="animate-spin text-base">⏳</span>
					<span>Updating...</span>
				{:else}
					<span class="text-base">🔄</span>
					<span>Update</span>
				{/if}
			</button>
		{/if}
	</div>

	<!-- Right: Status Info -->
	<div class="flex items-center gap-2 text-xs text-muted-foreground">
		{#if isPlaying}
			<div class="flex items-center gap-1">
				<span class="h-2 w-2 animate-pulse rounded-full bg-green-500"></span>
				<span>Live</span>
			</div>
		{:else if isInitialized}
			<span>Ready</span>
		{/if}
	</div>
</div>
