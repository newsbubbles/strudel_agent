/**
 * Carousel store - Manages loaded panels and navigation
 * 
 * Handles the main carousel state including:
 * - Loading/closing panels
 * - Panel navigation
 * - Panel updates
 * - Current panel tracking
 */

import { writable, derived, get } from 'svelte/store';
import type { Panel } from '$lib/types';

/**
 * Carousel state interface
 */
interface CarouselState {
	/** All loaded panels in the carousel */
	panels: Panel[];
	
	/** Index of the currently visible panel */
	currentIndex: number;
}

/**
 * Initial carousel state
 */
const initialState: CarouselState = {
	panels: [],
	currentIndex: 0
};

/**
 * Create the carousel store
 */
function createCarouselStore() {
	const { subscribe, set, update } = writable<CarouselState>(initialState);

	return {
		subscribe,

		/**
		 * Load a panel into the carousel
		 * If panel already exists, navigates to it instead
		 */
		loadPanel: (panel: Panel) => {
			update((state) => {
				// Check if panel already loaded
				const existingIndex = state.panels.findIndex((p) => p.id === panel.id);

				if (existingIndex !== -1) {
					// Panel already loaded - just navigate to it
					return {
						...state,
						currentIndex: existingIndex
					};
				}

				// Add new panel and navigate to it
				return {
					panels: [...state.panels, panel],
					currentIndex: state.panels.length
				};
			});
		},

		/**
		 * Close a panel by ID
		 * Adjusts current index if necessary
		 */
		closePanel: (panelId: string) => {
			update((state) => {
				const index = state.panels.findIndex((p) => p.id === panelId);

				// Panel not found
				if (index === -1) {
					return state;
				}

				// Remove the panel
				const newPanels = state.panels.filter((p) => p.id !== panelId);

				// Adjust current index
				let newIndex = state.currentIndex;

				if (index < state.currentIndex) {
					// Closed panel was before current - shift index left
					newIndex = state.currentIndex - 1;
				} else if (index === state.currentIndex) {
					// Closed current panel - stay at same index (shows next panel)
					// But clamp to valid range
					newIndex = Math.min(state.currentIndex, newPanels.length - 1);
				}

				// Ensure index is valid
				newIndex = Math.max(0, newIndex);

				return {
					panels: newPanels,
					currentIndex: newIndex
				};
			});
		},

		/**
		 * Update a panel's data
		 * Merges the updates with existing panel data
		 */
		updatePanel: (panelId: string, updates: Partial<Panel>) => {
			update((state) => ({
				...state,
				panels: state.panels.map((p) =>
					p.id === panelId
						? {
								...p,
								...updates,
								updatedAt: new Date()
							}
						: p
				)
			}));
		},

		/**
		 * Navigate to a specific panel by index
		 */
		goToPanel: (index: number) => {
			update((state) => {
				// Clamp index to valid range
				const clampedIndex = Math.max(0, Math.min(index, state.panels.length - 1));

				return {
					...state,
					currentIndex: clampedIndex
				};
			});
		},

		/**
		 * Navigate to the next panel (with wrapping)
		 */
		next: () => {
			update((state) => {
				if (state.panels.length === 0) return state;

				const nextIndex = (state.currentIndex + 1) % state.panels.length;

				return {
					...state,
					currentIndex: nextIndex
				};
			});
		},

		/**
		 * Navigate to the previous panel (with wrapping)
		 */
		previous: () => {
			update((state) => {
				if (state.panels.length === 0) return state;

				const prevIndex =
					state.currentIndex === 0 ? state.panels.length - 1 : state.currentIndex - 1;

				return {
					...state,
					currentIndex: prevIndex
				};
			});
		},

		/**
		 * Get a panel by ID
		 */
		getPanel: (panelId: string): Panel | null => {
			const state = get({ subscribe });
			return state.panels.find((p) => p.id === panelId) || null;
		},

		/**
		 * Check if a panel is loaded
		 */
		hasPanel: (panelId: string): boolean => {
			const state = get({ subscribe });
			return state.panels.some((p) => p.id === panelId);
		},

		/**
		 * Clear all panels
		 */
		clear: () => {
			set(initialState);
		},

		/**
		 * Reset to initial state
		 */
		reset: () => {
			set(initialState);
		}
	};
}

/**
 * Carousel store instance
 */
export const carousel = createCarouselStore();

/**
 * Derived store for the current panel
 * Returns null if no panels are loaded
 */
export const currentPanel = derived(carousel, ($carousel) =>
	$carousel.panels.length > 0 ? $carousel.panels[$carousel.currentIndex] : null
);

/**
 * Derived store for panel count
 */
export const panelCount = derived(carousel, ($carousel) => $carousel.panels.length);

/**
 * Derived store for current panel index
 */
export const currentIndex = derived(carousel, ($carousel) => $carousel.currentIndex);

/**
 * Derived store for all panels
 */
export const panels = derived(carousel, ($carousel) => $carousel.panels);
