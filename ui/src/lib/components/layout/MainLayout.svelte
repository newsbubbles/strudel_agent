<script lang="ts">
	/**
	 * MainLayout - Primary app layout with carousel and drawers
	 *
	 * Features:
	 * - CSS scroll-snap carousel for panel navigation
	 * - Left drawer for browsing items
	 * - Right drawer for chat history
	 * - Global player controls at bottom
	 * - Drawer toggle buttons
	 */

	import { onMount } from 'svelte';
	import { carousel, currentPanel } from '$lib/stores/carousel';
	import { Drawer } from '$lib/components/ui/drawer';
	import { Button } from '$lib/components/ui/button';
	import LeftDrawer from '$lib/components/drawers/LeftDrawer.svelte';
	import RightDrawer from '$lib/components/drawers/RightDrawer.svelte';
	import GlobalPlayer from '$lib/components/player/GlobalPlayer.svelte';
	import PanelRenderer from '$lib/components/panels/PanelRenderer.svelte';

	/** Drawer state */
	let leftDrawerOpen = false;
	let rightDrawerOpen = false;

	/** Reactive carousel state */
	$: panels = $carousel.panels;
	$: currentIndex = $carousel.currentIndex;

	/** Carousel element ref */
	let carouselElement: HTMLDivElement;

	/** Track if we're programmatically scrolling */
	let isScrolling = false;

	/** Handle carousel scroll */
	function handleCarouselScroll() {
		if (!carouselElement || isScrolling) return;

		const scrollLeft = carouselElement.scrollLeft;
		const panelWidth = carouselElement.offsetWidth;
		const newIndex = Math.round(scrollLeft / panelWidth);

		if (newIndex !== currentIndex && newIndex >= 0 && newIndex < panels.length) {
			carousel.goToPanel(newIndex);
		}
	}

	/** Navigate to panel by index */
	function goToPanel(index: number) {
		if (!carouselElement || index < 0 || index >= panels.length) return;

		isScrolling = true;
		const panelWidth = carouselElement.offsetWidth;
		carouselElement.scrollTo({
			left: index * panelWidth,
			behavior: 'smooth'
		});

		// Reset scrolling flag after animation
		setTimeout(() => {
			isScrolling = false;
		}, 350);
	}

	/** Watch currentIndex changes and scroll carousel */
	$: if (carouselElement && currentIndex !== undefined && panels.length > 0) {
		goToPanel(currentIndex);
	}

	/** Open left drawer (for Browse button) */
	function openLeftDrawer() {
		leftDrawerOpen = true;
	}

	/** Keyboard shortcuts */
	function handleKeyDown(e: KeyboardEvent) {
		// Left/Right arrows for panel navigation
		if (e.key === 'ArrowLeft' && currentIndex > 0) {
			e.preventDefault();
			carousel.goToPanel(currentIndex - 1);
		} else if (e.key === 'ArrowRight' && currentIndex < panels.length - 1) {
			e.preventDefault();
			carousel.goToPanel(currentIndex + 1);
		}

		// Cmd/Ctrl + B for left drawer
		if ((e.metaKey || e.ctrlKey) && e.key === 'b') {
			e.preventDefault();
			leftDrawerOpen = !leftDrawerOpen;
		}

		// Cmd/Ctrl + H for right drawer (history)
		if ((e.metaKey || e.ctrlKey) && e.key === 'h') {
			e.preventDefault();
			rightDrawerOpen = !rightDrawerOpen;
		}

		// Cmd/Ctrl + W to close current panel
		if ((e.metaKey || e.ctrlKey) && e.key === 'w' && panels.length > 0) {
			e.preventDefault();
			const panel = panels[currentIndex];
			if (panel) {
				carousel.closePanel(panel.id);
			}
		}
	}

	onMount(() => {
		// Add keyboard listener
		window.addEventListener('keydown', handleKeyDown);

		return () => {
			window.removeEventListener('keydown', handleKeyDown);
		};
	});
</script>

<svelte:head>
	<title>Strudel Agent</title>
</svelte:head>

<div class="flex h-screen w-screen overflow-hidden bg-background">
	<!-- Left Drawer -->
	<Drawer bind:open={leftDrawerOpen} side="left">
		<LeftDrawer />
	</Drawer>

	<!-- Main Content Area -->
	<div class="flex flex-1 flex-col overflow-hidden">
		<!-- Carousel Container -->
		<div class="relative flex-1 overflow-hidden">
			{#if panels.length === 0}
				<!-- Empty State -->
				<div class="flex h-full flex-col items-center justify-center text-muted-foreground">
					<img 
						src="/favicon.png" 
						alt="Strudel" 
						class="mb-4 h-32 w-32 object-contain"
					/>
					<h2 class="mb-2 text-xl font-semibold">No items loaded</h2>
					<p class="mb-4 text-center text-sm">
						Open the left drawer to browse clips, songs, and playlists.
					</p>
					<Button onclick={openLeftDrawer}>
						<span class="mr-2">☰</span>
						Browse Items
					</Button>
					<div class="mt-8 text-xs text-muted-foreground">
						<p>Keyboard shortcuts:</p>
						<p>⌘/Ctrl + B - Toggle left drawer</p>
						<p>⌘/Ctrl + H - Toggle right drawer</p>
					</div>
				</div>
			{:else}
				<!-- Panel Title Bar (centered, above carousel) -->
				<div class="absolute left-0 right-0 top-0 z-10 flex h-12 items-center justify-center bg-gradient-to-b from-background via-background/80 to-transparent">
					<h1 class="text-sm font-medium text-foreground/80">
						{$currentPanel?.title || 'Untitled'}
					</h1>
				</div>

				<!-- Carousel -->
				<div
					bind:this={carouselElement}
					class="carousel-container flex h-full w-full snap-x snap-mandatory overflow-x-auto scroll-smooth"
					onscroll={handleCarouselScroll}
				>
					{#each panels as panel, index (panel.id)}
						<div class="h-full w-full flex-shrink-0 snap-center">
							<PanelRenderer {panel} active={index === currentIndex} />
						</div>
					{/each}
				</div>

				<!-- Panel Indicators (Dots) - positioned above message input -->
				{#if panels.length > 1}
					<div class="absolute bottom-24 left-1/2 z-20 flex -translate-x-1/2 gap-2 rounded-full bg-background/80 px-3 py-2 shadow-md backdrop-blur-sm">
						{#each panels as panel, index}
							<button
								class="h-2 rounded-full transition-all {index === currentIndex
									? 'w-6 bg-primary'
									: 'w-2 bg-muted-foreground/30 hover:bg-muted-foreground/50'}"
								onclick={() => carousel.goToPanel(index)}
								aria-label="Go to panel {index + 1}: {panel.title}"
							/>
						{/each}
					</div>
				{/if}

				<!-- Close Button (Top Right) -->
				<button
					class="absolute right-4 top-2 z-10 rounded-md bg-background/80 p-2 text-foreground shadow-md backdrop-blur-sm hover:bg-background"
					onclick={() => {
						const panel = panels[currentIndex];
						if (panel) carousel.closePanel(panel.id);
					}}
					aria-label="Close panel"
				>
					✕
				</button>
			{/if}
		</div>

		<!-- Global Player Controls -->
		<GlobalPlayer />
	</div>

	<!-- Right Drawer -->
	<Drawer bind:open={rightDrawerOpen} side="right">
		<RightDrawer />
	</Drawer>

	<!-- Drawer Toggle Buttons (hidden when respective drawer is open) -->
	{#if !leftDrawerOpen}
		<button
			class="fixed left-4 top-4 z-40 rounded-md bg-background p-3 text-xl shadow-lg hover:bg-accent"
			onclick={() => (leftDrawerOpen = true)}
			aria-label="Open left drawer"
		>
			☰
		</button>
	{/if}

	{#if !rightDrawerOpen}
		<button
			class="fixed right-4 top-4 z-40 rounded-md bg-background p-3 text-xl shadow-lg hover:bg-accent"
			onclick={() => (rightDrawerOpen = true)}
			aria-label="Open right drawer"
		>
			💬
		</button>
	{/if}
</div>

<style>
	/* Hide scrollbar for carousel */
	.carousel-container {
		-webkit-overflow-scrolling: touch;
		scrollbar-width: none;
		-ms-overflow-style: none;
	}

	.carousel-container::-webkit-scrollbar {
		display: none;
	}
</style>
