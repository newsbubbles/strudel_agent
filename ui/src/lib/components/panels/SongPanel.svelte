<script lang="ts">
	/**
	 * SongPanel - Markdown viewer for songs with clip references
	 *
	 * Features:
	 * - Markdown rendering
	 * - Clip references (clickable to load clip panels)
	 * - Message input for chat
	 * - Read-only content (agent edits via chat)
	 */

	import type { SongPanel as SongPanelType } from '$lib/types/panel';
	import MarkdownViewer from './MarkdownViewer.svelte';
	import MessageInput from './MessageInput.svelte';
	import { carousel } from '$lib/stores/carousel';
	import { apiService } from '$lib/services/api';

	export let panel: SongPanelType;

	/** Load referenced clip */
	async function loadClip(clipId: string) {
		try {
			// Check if clip is already loaded
			const panelId = `clip:${clipId}`;
			const existing = $carousel.panels.find((p) => p.id === panelId);

			if (existing) {
				// Jump to existing panel
				const index = $carousel.panels.indexOf(existing);
				carousel.goToPanel(index);
				return;
			}

			// Fetch clip data
			const clipData = await apiService.getClip(panel.projectId, clipId);

			// Create new panel
			const clipPanel = {
				id: panelId,
				type: 'clip' as const,
				itemId: clipId,
				projectId: panel.projectId,
				sessionId: `session_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
				title: clipData.name,
				code: clipData.code,
				isDirty: false,
				createdAt: new Date(clipData.created_at || Date.now()),
				updatedAt: new Date(clipData.updated_at || Date.now())
			};

			carousel.loadPanel(clipPanel);
		} catch (error) {
			console.error('[SongPanel] Failed to load clip:', error);
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

		<!-- Clip References -->
		{#if panel.clips && panel.clips.length > 0}
			<div class="mt-6 border-t pt-4">
				<h3 class="mb-3 text-sm font-semibold">Referenced Clips</h3>
				<div class="flex flex-wrap gap-2">
					{#each panel.clips as clipRef}
						<button
							onclick={() => loadClip(clipRef.clipId)}
							class="inline-flex items-center rounded-md border border-input bg-background px-3 py-1.5 text-sm font-medium ring-offset-background transition-colors hover:bg-accent hover:text-accent-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2"
						>
							<span class="mr-1.5">🎹</span>
							{clipRef.clipId}
						</button>
					{/each}
				</div>
			</div>
		{/if}
	</div>

	<!-- Message Input -->
	<MessageInput panelId={panel.id} sessionId={panel.sessionId} />
</div>
