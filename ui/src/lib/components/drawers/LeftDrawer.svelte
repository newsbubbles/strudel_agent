<script lang="ts">
	/**
	 * LeftDrawer - Browse and load items (clips, songs, playlists)
	 *
	 * Features:
	 * - Project selector dropdown
	 * - Type selector tabs (Clips, Songs, Playlists)
	 * - Search/filter functionality
	 * - Recent items section
	 * - Scrollable item list
	 * - Click to load panel in carousel
	 */

	import type { PanelType } from '$lib/types/panel';
	import { carousel } from '$lib/stores/carousel';
	import { recent } from '$lib/stores/recent';
	import { apiService, type ProjectData } from '$lib/services/api';
	import { onMount } from 'svelte';

	// Project state
	let projects: ProjectData[] = [];
	let selectedProjectId: string = '';
	let isLoadingProjects = true;

	let selectedType: PanelType = 'clip';
	let searchQuery = '';
	let items: Array<{ id: string; label: string }> = [];
	let isLoading = false;
	let loadError: string | null = null;

	/** Filter recent items by selected type */
	$: recentItems = $recent.filter((item) => item.type === selectedType);

	/** Filter items by search query */
	$: filteredItems = items.filter((item) =>
		item.label.toLowerCase().includes(searchQuery.toLowerCase())
	);

	/** Load items when type or project changes */
	$: if (selectedType && selectedProjectId) loadItems();

	/** Extract item ID from panel ID (e.g., "clip:my-clip" -> "my-clip") */
	function extractItemId(panelId: string): string {
		const parts = panelId.split(':');
		return parts.length > 1 ? parts.slice(1).join(':') : panelId;
	}

	/** Load projects on mount */
	async function loadProjects() {
		isLoadingProjects = true;
		try {
			console.log('[LeftDrawer] Loading projects...');
			projects = await apiService.listProjects();
			console.log('[LeftDrawer] Loaded projects:', projects);
			// Select first project by default if available
			if (projects.length > 0 && !selectedProjectId) {
				selectedProjectId = projects[0].project_id;
			}
		} catch (error) {
			console.error('[LeftDrawer] Failed to load projects:', error);
			projects = [];
		} finally {
			isLoadingProjects = false;
		}
	}

	/** Load items from API */
	async function loadItems() {
		if (!selectedProjectId) return;

		isLoading = true;
		loadError = null;

		try {
			console.log(`[LeftDrawer] Loading ${selectedType}s for project:`, selectedProjectId);
			switch (selectedType) {
				case 'clip': {
					const clips = await apiService.listClips(selectedProjectId);
					console.log('[LeftDrawer] Loaded clips:', clips);
					items = clips.map((c) => ({ id: c.clip_id, label: c.name }));
					break;
				}
				case 'song': {
					const songs = await apiService.listSongs(selectedProjectId);
					console.log('[LeftDrawer] Loaded songs:', songs);
					items = songs.map((s) => ({ id: s.song_id, label: s.name }));
					break;
				}
				case 'playlist': {
					const playlists = await apiService.listPlaylists(selectedProjectId);
					console.log('[LeftDrawer] Loaded playlists:', playlists);
					items = playlists.map((p) => ({ id: p.playlist_id, label: p.name }));
					break;
				}
				// Packs disabled for now
				case 'pack': {
					items = [];
					break;
				}
			}
		} catch (error) {
			console.error('[LeftDrawer] Failed to load items:', error);
			loadError = error instanceof Error ? error.message : 'Failed to load items';
			items = [];
		} finally {
			isLoading = false;
		}
	}

	/** Handle item click - load panel in carousel */
	async function handleItemClick(itemId: string) {
		const panelId = `${selectedType}:${itemId}`;

		// Check if already loaded
		const existingIndex = $carousel.panels.findIndex((p) => p.id === panelId);
		if (existingIndex !== -1) {
			// Jump to existing panel
			carousel.goToPanel(existingIndex);
			return;
		}

		try {
			// Fetch data based on type
			let data: any;
			switch (selectedType) {
				case 'clip':
					data = await apiService.getClip(selectedProjectId, itemId);
					break;
				case 'song':
					data = await apiService.getSong(selectedProjectId, itemId);
					break;
				case 'playlist':
					data = await apiService.getPlaylist(selectedProjectId, itemId);
					break;
				// Packs disabled for now
				case 'pack':
					return;
			}

			// Create panel with proper properties from API data
			const panel: any = {
				id: panelId,
				type: selectedType,
				itemId: itemId,
				projectId: selectedProjectId,
				sessionId: `session_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
				isDirty: false,
				createdAt: new Date(data.created_at || Date.now()),
				updatedAt: new Date(data.updated_at || Date.now())
			};

			// Add type-specific properties
			if (selectedType === 'clip') {
				panel.title = data.name;
				panel.code = data.code;
			} else if (selectedType === 'song') {
				panel.title = data.name;
				panel.content = data.content;
				panel.clips = data.clips || [];
			} else if (selectedType === 'playlist') {
				panel.title = data.name;
				panel.content = data.content;
				panel.songs = data.songs || [];
			}

			carousel.loadPanel(panel);
		} catch (error) {
			console.error('[LeftDrawer] Failed to load panel:', error);
		}
	}

	/** Load projects on mount */
	onMount(() => {
		loadProjects();
	});
</script>

<div class="flex h-full flex-col overflow-hidden px-4 pb-4 pt-12">
	<!-- Project Selector -->
	<div class="mb-4 flex-shrink-0">
		<label class="mb-1.5 block text-xs font-medium text-muted-foreground" for="project-select">
			Project
		</label>
		{#if isLoadingProjects}
			<div class="flex h-10 items-center rounded-md border border-input bg-background px-3">
				<span class="animate-pulse text-sm text-muted-foreground">Loading projects...</span>
			</div>
		{:else if projects.length === 0}
			<div class="flex h-10 items-center rounded-md border border-destructive/50 bg-destructive/10 px-3">
				<span class="text-sm text-destructive">No projects found</span>
			</div>
		{:else}
			<select
				id="project-select"
				bind:value={selectedProjectId}
				class="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2"
			>
				{#each projects as project}
					<option value={project.project_id}>
						{project.name || project.project_id}
					</option>
				{/each}
			</select>
		{/if}
	</div>

	<!-- Type Selector Tabs -->
	<div class="mb-4 flex flex-shrink-0 gap-1 rounded-lg bg-muted p-1">
		<button
			onclick={() => (selectedType = 'clip')}
			class="flex-1 rounded-md px-2 py-1.5 text-sm font-medium transition-colors {selectedType ===
			'clip'
				? 'bg-background text-foreground shadow-sm'
				: 'text-muted-foreground hover:text-foreground'}"
		>
			🎹 Clips
		</button>
		<button
			onclick={() => (selectedType = 'song')}
			class="flex-1 rounded-md px-2 py-1.5 text-sm font-medium transition-colors {selectedType ===
			'song'
				? 'bg-background text-foreground shadow-sm'
				: 'text-muted-foreground hover:text-foreground'}"
		>
			🎵 Songs
		</button>
		<button
			onclick={() => (selectedType = 'playlist')}
			class="flex-1 rounded-md px-2 py-1.5 text-sm font-medium transition-colors {selectedType ===
			'playlist'
				? 'bg-background text-foreground shadow-sm'
				: 'text-muted-foreground hover:text-foreground'}"
		>
			💿 Lists
		</button>
	</div>

	<!-- Search Input -->
	<input
		type="text"
		bind:value={searchQuery}
		placeholder="Search {selectedType}s..."
		class="mb-4 flex h-10 w-full flex-shrink-0 rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background file:border-0 file:bg-transparent file:text-sm file:font-medium placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50"
	/>

	<!-- Recent Items Section -->
	{#if recentItems.length > 0}
		<div class="mb-4 flex-shrink-0">
			<h3 class="mb-2 text-xs font-semibold uppercase tracking-wide text-muted-foreground">
				Recent
			</h3>
			<div class="max-h-32 space-y-1 overflow-y-auto">
				{#each recentItems.slice(0, 5) as item}
					<button
						onclick={() => handleItemClick(extractItemId(item.id))}
						class="w-full rounded-md px-3 py-2 text-left text-sm transition-colors hover:bg-accent hover:text-accent-foreground"
					>
						<span class="mr-2 opacity-50">⏱️</span>
						{item.title}
					</button>
				{/each}
			</div>
		</div>

		<div class="my-4 flex-shrink-0 border-t"></div>
	{/if}

	<!-- All Items Section -->
	<div class="min-h-0 flex-1 overflow-hidden">
		<h3 class="mb-2 text-xs font-semibold uppercase tracking-wide text-muted-foreground">
			All {selectedType}s
		</h3>

		{#if !selectedProjectId}
			<div class="py-8 text-center text-sm text-muted-foreground">
				Select a project to browse {selectedType}s
			</div>
		{:else if isLoading}
			<div class="flex items-center justify-center py-8">
				<span class="animate-spin text-2xl">⏳</span>
			</div>
		{:else if loadError}
			<div class="rounded-lg bg-destructive/10 p-4 text-sm text-destructive">
				<p class="font-semibold">⚠️ Error loading {selectedType}s</p>
				<p class="mt-1 text-xs">{loadError}</p>
			</div>
		{:else if filteredItems.length === 0}
			<div class="py-8 text-center text-sm text-muted-foreground">
				{searchQuery ? `No ${selectedType}s matching "${searchQuery}"` : `No ${selectedType}s found`}
			</div>
		{:else}
			<div class="h-full space-y-1 overflow-y-auto">
				{#each filteredItems as item}
					<button
						onclick={() => handleItemClick(item.id)}
						class="w-full rounded-md px-3 py-2 text-left text-sm transition-colors hover:bg-accent hover:text-accent-foreground"
					>
						{item.label}
					</button>
				{/each}
			</div>
		{/if}
	</div>
</div>
