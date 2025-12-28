<script lang="ts">
	/**
	 * PackPanel - Documentation viewer for sample packs
	 *
	 * Features:
	 * - Markdown rendering
	 * - Read-only (official pack documentation)
	 * - Message input for questions about pack
	 * - Pack metadata display
	 */

	import type { PackPanel as PackPanelType } from '$lib/types/panel';
	import MarkdownViewer from './MarkdownViewer.svelte';
	import MessageInput from './MessageInput.svelte';

	export let panel: PackPanelType;
</script>

<div class="flex h-full flex-col px-4 pb-4 pt-14">
	<!-- Header (minimal - title is in top bar now) -->
	<div class="mb-2 flex items-center justify-end">
		<span
			class="rounded-md bg-primary/10 px-2 py-0.5 text-xs font-medium text-primary"
			title="Official pack documentation"
		>
			Official Pack
		</span>
	</div>

	<!-- Pack Documentation -->
	<div class="mb-4 flex-1 overflow-y-auto rounded-lg border bg-background p-4">
		<MarkdownViewer content={panel.content || ''} />

		<!-- Pack Info Footer -->
		<div class="mt-6 border-t pt-4">
			<div class="flex items-center gap-2 text-xs text-muted-foreground">
				<span>📚</span>
				<span>This is official documentation for the <strong>{panel.title}</strong> sample pack.</span>
			</div>
			<div class="mt-2 text-xs text-muted-foreground">
				<span>🤖</span>
				<span>Ask the agent questions about this pack using the chat below.</span>
			</div>
		</div>
	</div>

	<!-- Message Input -->
	<MessageInput panelId={panel.id} sessionId={panel.sessionId} />
</div>
