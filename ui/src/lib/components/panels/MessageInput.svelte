<script lang="ts">
	/**
	 * MessageInput - Chat input for sending messages to agent
	 *
	 * Features:
	 * - Textarea with auto-resize
	 * - Enter to send (Shift+Enter for newline)
	 * - Send button
	 * - Disabled when not connected
	 * - Loading state while sending
	 *
	 * Protocol: Uses flat message structure per backend spec
	 * See: notes/debug_chat/backend_protocol_spec.md
	 */

	import { wsService } from '$lib/services/websocket';
	import { history } from '$lib/stores/history';
	import { websocket } from '$lib/stores/websocket';
	import { createUserMessage as createUserMessageType } from '$lib/types/message';

	export let panelId: string;
	export let sessionId: string;

	let message = '';
	let isSending = false;
	let textareaElement: HTMLTextAreaElement;

	/** Check if WebSocket is ready to send messages */
	$: isReady = $websocket.state === 'ready';

	/** Auto-resize textarea */
	function autoResize() {
		if (!textareaElement) return;

		textareaElement.style.height = 'auto';
		textareaElement.style.height = textareaElement.scrollHeight + 'px';
	}

	/** Handle send button */
	async function handleSend() {
		if (!message.trim() || isSending || !isReady) return;

		isSending = true;

		try {
			// Add to local history immediately (optimistic update)
			const userMessage = createUserMessageType(sessionId, message);
			history.addMessage(sessionId, {
				...userMessage,
				panelId,
				index: -1 // Backend will assign proper index
			});

			// Send via WebSocket using the correct flat format
			// Backend expects: { type: 'user_message', session_id, message, context? }
			wsService.sendMessage(message, {
				// Optional context - could include current code, selection, etc.
				panel_id: panelId
			});

			// Clear input
			message = '';
			autoResize();
		} catch (error) {
			console.error('[MessageInput] Failed to send message:', error);
		} finally {
			isSending = false;
		}
	}

	/** Handle keyboard shortcuts */
	function handleKeyDown(e: KeyboardEvent) {
		// Enter to send (Shift+Enter for newline)
		if (e.key === 'Enter' && !e.shiftKey) {
			e.preventDefault();
			handleSend();
		}
	}

	/** Auto-resize on input */
	$: if (message !== undefined) {
		autoResize();
	}
</script>

<div class="flex gap-2">
	<!-- Textarea -->
	<textarea
		bind:this={textareaElement}
		bind:value={message}
		onkeydown={handleKeyDown}
		oninput={autoResize}
		placeholder={isReady
			? 'Ask about this item... (Enter to send, Shift+Enter for newline)'
			: 'Connecting...'}
		disabled={isSending || !isReady}
		class="flex-1 resize-none rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50"
		rows="1"
		style="min-height: 40px; max-height: 200px;"
	></textarea>

	<!-- Send Button -->
	<button
		onclick={handleSend}
		disabled={!message.trim() || isSending || !isReady}
		class="inline-flex h-10 items-center justify-center rounded-md bg-primary px-4 py-2 text-sm font-medium text-primary-foreground ring-offset-background transition-colors hover:bg-primary/90 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50"
		aria-label="Send message"
	>
		{#if isSending}
			<span class="animate-spin">⏳</span>
		{:else if !isReady}
			<span class="text-muted-foreground">...</span>
		{:else}
			<span>Send</span>
		{/if}
	</button>
</div>
