<script lang="ts">
	/**
	 * ClipPanel - Code editor panel for Strudel clips
	 *
	 * Features:
	 * - CodeMirror editor with JavaScript syntax highlighting
	 * - Save button (disabled when not dirty)
	 * - Dirty state indicator
	 * - Message input for chat with agent
	 */

	import type { ClipPanel as ClipPanelType } from '$lib/types/panel';
	import CodeEditor from './CodeEditor.svelte';
	import MessageInput from './MessageInput.svelte';
	import { carousel } from '$lib/stores/carousel';
	import { apiService } from '$lib/services/api';

	export let panel: ClipPanelType;

	let code = panel.code;
	let isSaving = false;
	let saveError: string | null = null;

	/** Handle code changes */
	function handleCodeChange(event: CustomEvent<string>) {
		code = event.detail;

		// Mark as dirty
		carousel.updatePanel(panel.id, {
			code,
			isDirty: true,
			updatedAt: new Date()
		} as any);
	}

	/** Save clip to backend */
	async function handleSave() {
		if (isSaving) return;

		isSaving = true;
		saveError = null;

		try {
			await apiService.updateClip(panel.projectId, panel.itemId, { code });

			// Mark as clean
			carousel.updatePanel(panel.id, {
				isDirty: false
			} as any);

			console.log('[ClipPanel] Saved successfully:', panel.itemId);
		} catch (error) {
			console.error('[ClipPanel] Failed to save:', error);
			saveError = error instanceof Error ? error.message : 'Failed to save';
		} finally {
			isSaving = false;
		}
	}

	/** Keyboard shortcut for save (Cmd/Ctrl+S) */
	function handleKeyDown(e: KeyboardEvent) {
		if ((e.metaKey || e.ctrlKey) && e.key === 's') {
			e.preventDefault();
			if (panel.isDirty) {
				handleSave();
			}
		}
	}
</script>

<svelte:window onkeydown={handleKeyDown} />

<div class="flex h-full flex-col px-4 pb-4 pt-14">
	<!-- Header (minimal - title is in top bar now) -->
	<div class="mb-2 flex items-center justify-end gap-2">
		{#if panel.isDirty}
			<span class="text-xs text-muted-foreground">● Unsaved</span>
		{/if}

		{#if saveError}
			<span class="text-sm text-destructive" title={saveError}>⚠️ Save failed</span>
		{/if}

		<button
			onclick={handleSave}
			disabled={!panel.isDirty || isSaving}
			class="inline-flex h-8 items-center justify-center rounded-md bg-primary px-3 py-1.5 text-xs font-medium text-primary-foreground ring-offset-background transition-colors hover:bg-primary/90 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50"
			aria-label="Save clip"
		>
			{#if isSaving}
				<span class="animate-spin">⏳</span>
				<span class="ml-1">Saving...</span>
			{:else}
				<span>⌘S Save</span>
			{/if}
		</button>
	</div>

	<!-- Code Editor -->
	<div class="mb-4 flex-1 overflow-hidden rounded-lg border">
		<CodeEditor value={code} on:change={handleCodeChange} />
	</div>

	<!-- Message Input -->
	<MessageInput panelId={panel.id} sessionId={panel.sessionId} />
</div>
