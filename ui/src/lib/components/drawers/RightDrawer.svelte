<script lang="ts">
	/**
	 * RightDrawer - Chat history for current panel
	 *
	 * Features:
	 * - Display messages for active panel's session
	 * - Load older messages (pagination)
	 * - Message timestamps
	 * - Role indicators (user, agent, system)
	 * - Auto-scroll to bottom on new messages
	 * - Empty state when no panel active
	 */

	import { carousel, currentPanel } from '$lib/stores/carousel';
	import { history } from '$lib/stores/history';
	import { apiService } from '$lib/services/api';
	import { afterUpdate } from 'svelte';
	import type { AnyMessage } from '$lib/types';

	let scrollContainer: HTMLDivElement;
	let isLoadingOlder = false;
	let shouldAutoScroll = true;

	/** Consolidated reactive state from stores */
	$: sessionId = $currentPanel?.sessionId;
	$: messageHistory = sessionId ? $history.histories.get(sessionId) : null;
	$: messages = messageHistory?.messages ?? [];
	$: hasMore = messageHistory?.hasMore ?? false;

	/** Auto-scroll to bottom on new messages using afterUpdate */
	afterUpdate(() => {
		if (messages.length && shouldAutoScroll && scrollContainer) {
			scrollContainer.scrollTop = scrollContainer.scrollHeight;
		}
	});

	/** Load older messages (pagination) */
	async function loadOlderMessages() {
		if (!sessionId || !hasMore || isLoadingOlder) return;

		isLoadingOlder = true;

		try {
			const oldestIndex = messageHistory?.oldestIndex;
			const result = await apiService.getMessages(
				sessionId,
				oldestIndex !== undefined ? { before_index: oldestIndex } : undefined
			);

			// Convert API messages to our AnyMessage format
			const convertedMessages: AnyMessage[] = result.messages.map((msg) => ({
				id: `msg_${msg.message_index}`,
				sessionId: sessionId!,
				role: msg.role === 'assistant' ? 'assistant' : 'user',
				content: msg.content,
				timestamp: new Date(msg.timestamp),
				status: 'sent' as const
			}));

			// Get oldest index from the result for next pagination
			const newOldestIndex = result.messages.length > 0 
				? Math.min(...result.messages.map(m => m.message_index))
				: undefined;

			// API returns has_more but we need to check if it exists
			const apiHasMore = (result as any).has_more ?? false;

			history.prependMessages(sessionId, convertedMessages, apiHasMore, newOldestIndex);
		} catch (error) {
			console.error('[RightDrawer] Failed to load older messages:', error);
		} finally {
			isLoadingOlder = false;
		}
	}

	/** Format timestamp */
	function formatTimestamp(date: Date): string {
		const now = new Date();
		const diff = now.getTime() - date.getTime();
		const seconds = Math.floor(diff / 1000);
		const minutes = Math.floor(seconds / 60);
		const hours = Math.floor(minutes / 60);

		if (seconds < 60) return 'just now';
		if (minutes < 60) return `${minutes}m ago`;
		if (hours < 24) return `${hours}h ago`;

		return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
	}

	/** Handle scroll to detect if user scrolled up */
	function handleScroll() {
		if (!scrollContainer) return;

		const { scrollTop, scrollHeight, clientHeight } = scrollContainer;
		const isAtBottom = scrollHeight - scrollTop - clientHeight < 50;

		shouldAutoScroll = isAtBottom;
	}
</script>

<div class="flex h-full w-80 flex-col px-4 pb-4 pt-12">
	{#if !$currentPanel}
		<!-- Empty State -->
		<div class="flex flex-1 items-center justify-center text-center">
			<div>
				<p class="text-sm text-muted-foreground">💬</p>
				<p class="mt-2 text-sm text-muted-foreground">No panel selected</p>
				<p class="mt-1 text-xs text-muted-foreground">Open an item to view chat history</p>
			</div>
		</div>
	{:else}
		<!-- Header -->
		<div class="mb-4">
			<h3 class="text-sm font-semibold">Chat History</h3>
			<p class="mt-1 text-xs text-muted-foreground">
				{$currentPanel.type}: {$currentPanel.itemId}
			</p>
		</div>

		<!-- Messages Container -->
		<div
			bind:this={scrollContainer}
			onscroll={handleScroll}
			class="flex-1 space-y-4 overflow-y-auto"
		>
			<!-- Load Older Button -->
			{#if hasMore}
				<button
					onclick={loadOlderMessages}
					disabled={isLoadingOlder}
					class="w-full rounded-md border border-dashed border-muted-foreground/25 py-2 text-xs text-muted-foreground transition-colors hover:border-muted-foreground/50 hover:bg-accent disabled:cursor-not-allowed disabled:opacity-50"
				>
					{#if isLoadingOlder}
						<span class="animate-spin">⏳</span>
						<span class="ml-2">Loading...</span>
					{:else}
						↑ Load older messages
					{/if}
				</button>
			{/if}

			<!-- Messages -->
			{#if messages.length === 0}
				<div class="py-8 text-center text-sm text-muted-foreground">
					<p>👋</p>
					<p class="mt-2">No messages yet</p>
					<p class="mt-1 text-xs">Start chatting about this {$currentPanel.type}</p>
				</div>
			{:else}
				{#each messages as message (message.id)}
					<div class="rounded-lg border bg-card p-3 text-card-foreground">
						<!-- Message Header -->
						<div class="mb-2 flex items-center justify-between">
							<span
								class="inline-flex items-center rounded-md px-2 py-0.5 text-xs font-medium {message.role ===
								'user'
									? 'bg-primary/10 text-primary'
									: message.role === 'assistant'
										? 'bg-secondary text-secondary-foreground'
										: 'bg-muted text-muted-foreground'}"
							>
								{#if message.role === 'user'}
									👤 You
								{:else if message.role === 'assistant'}
									🤖 Agent
								{:else}
									ℹ️ System
								{/if}
							</span>
							<span class="text-xs text-muted-foreground" title={message.timestamp.toLocaleString()}>
								{formatTimestamp(message.timestamp)}
							</span>
						</div>

						<!-- Message Content -->
						<p class="whitespace-pre-wrap text-sm leading-relaxed">{message.content}</p>
					</div>
				{/each}
			{/if}
		</div>

		<!-- Scroll to Bottom Button (when not auto-scrolling) -->
		{#if !shouldAutoScroll && messages.length > 0}
			<button
				onclick={() => {
					shouldAutoScroll = true;
					if (scrollContainer) {
						scrollContainer.scrollTop = scrollContainer.scrollHeight;
					}
				}}
				class="mt-2 w-full rounded-md bg-primary px-3 py-2 text-xs font-medium text-primary-foreground transition-colors hover:bg-primary/90"
			>
				↓ Scroll to bottom
			</button>
		{/if}
	{/if}
</div>
