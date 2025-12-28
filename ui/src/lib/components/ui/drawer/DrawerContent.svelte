<script lang="ts">
	/**
	 * DrawerContent - Content wrapper for drawer
	 */

	import { cn } from '$lib/utils/cn';
	import type { Snippet } from 'svelte';

	interface Props {
		children?: Snippet;
		class?: string;
	}

	let { children, class: className }: Props = $props();
</script>

<div class={cn('flex flex-col gap-4', className)}>
	{#if children}
		{@render children()}
	{/if}
</div>
