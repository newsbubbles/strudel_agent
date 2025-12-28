<script lang="ts">
	/**
	 * GlobalPlayer - Simple play/stop/update controls for current clip
	 *
	 * Features:
	 * - Play/Stop button
	 * - Update button (sync editor code to Strudel player)
	 * - Playing state indicator
	 * - Strudel playback controls
	 * - Only plays the currently focused clip in carousel
	 *
	 * NOTE: Strudel initialization happens in AppShell.svelte
	 * This component only controls playback.
	 *
	 * Update Flow:
	 * - User edits code in editor -> clicks Update -> reads from panel.code -> updates Strudel
	 * - Agent edits code (saves to backend) -> sends WS signal -> frontend fetches & updates panel
	 *
	 * NO CLIP COMBINING - Agent handles that automatically
	 */

	import { onDestroy } from 'svelte';
	import { currentPanel } from '$lib/stores/carousel';
	import { player, isStrudelInitialized } from '$lib/stores/player';
	import { strudelService } from '$lib/services/strudel';

	/** Get current clip panel (only clip panels can be played) */
	$: currentClip = $currentPanel?.type === 'clip' ? $currentPanel : null;

	/** Check if we can play (clip panel + Strudel initialized) */
	$: canPlay = currentClip !== null && $isStrudelInitialized;

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

	/**
	 * Handle Update - Read code from editor (panel.code) and update Strudel player
	 * 
	 * This does NOT fetch from backend - it reads the current editor state.
	 * The panel.code is kept in sync with the editor via carousel.updatePanel().
	 */
	function handleUpdate() {
		if (!currentClip) return;

		// Read code directly from the panel (reflects editor state)
		const code = currentClip.code || '';
		
		if (!code.trim()) {
			console.warn('[GlobalPlayer] No code to update');
			return;
		}

		console.log('[GlobalPlayer] Updating Strudel with editor code:', code.substring(0, 50) + '...');
		
		// Update the Strudel player with current editor code
		strudelService.updatePlayer(code);
		
		// If currently playing, the update will take effect on next cycle
		// Strudel handles hot-reloading automatically
		if (isPlaying) {
			console.log('[GlobalPlayer] Code updated while playing - changes will apply');
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
		{#if !$isStrudelInitialized}
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
				disabled={!currentClip}
				class="inline-flex h-10 items-center justify-center gap-2 rounded-md border border-input bg-background px-4 text-sm font-medium transition-colors hover:bg-accent hover:text-accent-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50"
			>
				<span class="text-base">🔄</span>
				<span>Update</span>
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
		{:else if $isStrudelInitialized}
			<span>Ready</span>
		{/if}
	</div>
</div>
