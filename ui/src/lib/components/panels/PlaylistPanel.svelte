<script lang="ts">
	/**
	 * PlaylistPanel - Markdown viewer for playlists with song references
	 *
	 * Features:
	 * - Markdown rendering
	 * - Song references (clickable to load song panels)
	 * - Message input for chat
	 * - Read-only content (agent edits via chat)
	 */

	import type { PlaylistPanel as PlaylistPanelType } from '$lib/types/panel';
	import MarkdownViewer from './MarkdownViewer.svelte';
	import MessageInput from './MessageInput.svelte';
	import { carousel } from '$lib/stores/carousel';
	import { apiService } from '$lib/services/api';
	import { wsService } from '$lib/services/websocket';

	export let panel: PlaylistPanelType;

	/** Load referenced song */
	async function loadSong(songId: string) {
		try {
			// Check if song is already loaded
			const panelId = `song:${songId}`;
			const existing = $carousel.panels.find((p) => p.id === panelId);

			if (existing) {
				// Jump to existing panel
				const index = $carousel.panels.indexOf(existing);
				carousel.goToPanel(index);
				return;
			}

			// Get the WebSocket session ID - all panels share the same chat session
			const sessionId = wsService.getSessionId();
			if (!sessionId) {
				console.error('[PlaylistPanel] No WebSocket session ID available');
				return;
			}

			// Fetch song data
			const songData = await apiService.getSong(panel.projectId, songId);

			// Create new panel
			const songPanel = {
				id: panelId,
				type: 'song' as const,
				itemId: songId,
				projectId: panel.projectId,
				sessionId: sessionId,
				title: songData.name,
				content: songData.content,
				clips: songData.clips,
				isDirty: false,
				createdAt: new Date(songData.created_at || Date.now()),
				updatedAt: new Date(songData.updated_at || Date.now())
			};

			carousel.loadPanel(songPanel);
		} catch (error) {
			console.error('[PlaylistPanel] Failed to load song:', error);
		}
	}
</script>

<div class="flex h-full flex-col px-4 pb-4 pt-14">
	<!-- Header (minimal - title is in top bar now) -->
	<div class="mb-2 flex items-center justify-end">
		<span class="text-xs text-muted-foreground">Read-only</span>
	</div>

	<!-- Markdown Content -->
	<div class="mb-4 flex-1 overflow-y-auto rounded-lg border bg-background p-4">
		<MarkdownViewer content={panel.content || ''} />

		<!-- Song References -->
		{#if panel.songs && panel.songs.length > 0}
			<div class="mt-6 border-t pt-4">
				<h3 class="mb-3 text-sm font-semibold">Songs in Playlist</h3>
				<div class="flex flex-col gap-2">
					{#each panel.songs as songRef, index}
						<button
							onclick={() => loadSong(songRef.songId)}
							class="flex items-center gap-3 rounded-md border border-input bg-background px-4 py-3 text-left ring-offset-background transition-colors hover:bg-accent hover:text-accent-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2"
						>
							<span class="text-sm font-medium text-muted-foreground">{index + 1}.</span>
							<span class="mr-2">🎵</span>
							<span class="flex-1 font-medium">{songRef.songId}</span>
							<span class="text-xs text-muted-foreground">→</span>
						</button>
					{/each}
				</div>
			</div>
		{/if}
	</div>

	<!-- Message Input -->
	<MessageInput panelId={panel.id} sessionId={panel.sessionId} />
</div>
