<script lang="ts">
	/**
	 * DrawerTitle - Title component for drawer
	 */

	import { cn } from '$lib/utils/cn';
	import type { Snippet } from 'svelte';

	interface Props {
		children?: Snippet;
		class?: string;
	}

	let { children, class: className }: Props = $props();
</script>

<h2 class={cn('text-lg font-semibold', className)}>
	{#if children}
		{@render children()}
	{/if}
</h2>
