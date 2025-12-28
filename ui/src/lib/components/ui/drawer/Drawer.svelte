<script lang="ts">
	/**
	 * Drawer Component
	 *
	 * Side drawer with overlay
	 */

	import { cn } from '$lib/utils/cn';
	import type { Snippet } from 'svelte';

	interface Props {
		open?: boolean;
		side?: 'left' | 'right';
		onOpenChange?: (open: boolean) => void;
		children?: Snippet;
		class?: string;
	}

	let { open = $bindable(false), side = 'left', onOpenChange, children, class: className }: Props =
		$props();

	function handleClose() {
		open = false;
		onOpenChange?.(false);
	}

	function handleOverlayClick() {
		handleClose();
	}

	function handleKeyDown(e: KeyboardEvent) {
		if (e.key === 'Escape' && open) {
			handleClose();
		}
	}
</script>

<svelte:window onkeydown={handleKeyDown} />

{#if open}
	<!-- Overlay -->
	<div
		class="fixed inset-0 z-50 bg-black/80"
		aria-hidden="true"
		onclick={handleOverlayClick}
		role="button"
		tabindex="-1"
	></div>

	<!-- Drawer -->
	<div
		class={cn(
			'fixed z-50 flex flex-col bg-background shadow-lg transition-transform duration-300',
			side === 'left'
				? 'left-0 top-0 h-full w-80 border-r'
				: 'right-0 top-0 h-full w-80 border-l',
			className
		)}
		role="dialog"
		aria-modal="true"
	>
		<!-- Close Button -->
		<button
			class={cn(
				'absolute top-3 z-10 flex h-8 w-8 items-center justify-center rounded-md text-muted-foreground transition-colors hover:bg-accent hover:text-foreground',
				side === 'left' ? 'right-3' : 'left-3'
			)}
			onclick={handleClose}
			aria-label="Close drawer"
		>
			<svg
				xmlns="http://www.w3.org/2000/svg"
				width="18"
				height="18"
				viewBox="0 0 24 24"
				fill="none"
				stroke="currentColor"
				stroke-width="2"
				stroke-linecap="round"
				stroke-linejoin="round"
			>
				<line x1="18" y1="6" x2="6" y2="18"></line>
				<line x1="6" y1="6" x2="18" y2="18"></line>
			</svg>
		</button>

		<!-- Content -->
		<div class="flex-1 overflow-hidden">
			{#if children}
				{@render children()}
			{/if}
		</div>
	</div>
{/if}
