<script lang="ts">
	/**
	 * PanelRenderer - Renders the appropriate panel type
	 *
	 * Routes to specific panel components based on panel type:
	 * - ClipPanel: Code editor for Strudel clips
	 * - SongPanel: Markdown viewer for songs
	 * - PlaylistPanel: Markdown viewer for playlists
	 * - PackPanel: Documentation viewer for sample packs
	 */

	import type { Panel } from '$lib/types/panel';
	import ClipPanel from './ClipPanel.svelte';
	import SongPanel from './SongPanel.svelte';
	import PlaylistPanel from './PlaylistPanel.svelte';
	import PackPanel from './PackPanel.svelte';

	export let panel: Panel;
	export let active: boolean = false;
</script>

<div class="h-full w-full" data-panel-id={panel.id} data-active={active}>
	{#if panel.type === 'clip'}
		<ClipPanel {panel} />
	{:else if panel.type === 'song'}
		<SongPanel {panel} />
	{:else if panel.type === 'playlist'}
		<PlaylistPanel {panel} />
	{:else if panel.type === 'pack'}
		<PackPanel {panel} />
	{:else}
		<!-- Fallback for unknown panel types -->
		<div class="flex h-full items-center justify-center">
			<div class="text-center">
				<p class="text-lg font-semibold text-destructive">Unknown panel type</p>
				<p class="text-sm text-muted-foreground">Type: {panel.type}</p>
			</div>
		</div>
	{/if}
</div>
