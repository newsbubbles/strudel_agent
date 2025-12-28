/**
 * Recent items store - Manages recently closed panels with LocalStorage persistence
 * 
 * Tracks items that were recently closed so users can quickly reopen them.
 * Persists to LocalStorage for cross-session availability.
 */

import { writable, derived, get } from 'svelte/store';
import { browser } from '$app/environment';
import type { PanelType } from '$lib/types';

/**
 * Recent item interface
 */
export interface RecentItem {
	/** Panel ID (e.g., "clip-123") */
	id: string;

	/** Panel type */
	type: PanelType;

	/** Display title */
	title: string;

	/** When the item was closed */
	closedAt: Date;

	/** Optional metadata */
	metadata?: Record<string, unknown>;
}

/**
 * LocalStorage key for recent items
 */
const STORAGE_KEY = 'strudel_agent_recent_items';

/**
 * Maximum number of recent items to keep
 */
const MAX_RECENT_ITEMS = 20;

/**
 * Load recent items from LocalStorage
 */
function loadFromStorage(): RecentItem[] {
	if (!browser) return [];

	try {
		const stored = localStorage.getItem(STORAGE_KEY);
		if (!stored) return [];

		const items = JSON.parse(stored) as RecentItem[];

		// Convert closedAt strings back to Date objects
		return items.map((item) => ({
			...item,
			closedAt: new Date(item.closedAt)
		}));
	} catch (error) {
		console.error('Failed to load recent items from storage:', error);
		return [];
	}
}

/**
 * Save recent items to LocalStorage
 */
function saveToStorage(items: RecentItem[]) {
	if (!browser) return;

	try {
		localStorage.setItem(STORAGE_KEY, JSON.stringify(items));
	} catch (error) {
		console.error('Failed to save recent items to storage:', error);
	}
}

/**
 * Create the recent items store
 */
function createRecentStore() {
	const { subscribe, set, update } = writable<RecentItem[]>(loadFromStorage());

	return {
		subscribe,

		/**
		 * Add an item to recent items
		 * If item already exists, removes old entry and adds to front
		 */
		add: (item: Omit<RecentItem, 'closedAt'>) => {
			update((items) => {
				// Remove existing entry if present
				const filtered = items.filter((i) => i.id !== item.id);

				// Add to front with current timestamp
				const newItem: RecentItem = {
					...item,
					closedAt: new Date()
				};

				const updated = [newItem, ...filtered].slice(0, MAX_RECENT_ITEMS);

				// Persist to storage
				saveToStorage(updated);

				return updated;
			});
		},

		/**
		 * Remove an item from recent items
		 */
		remove: (itemId: string) => {
			update((items) => {
				const updated = items.filter((i) => i.id !== itemId);
				saveToStorage(updated);
				return updated;
			});
		},

		/**
		 * Clear all recent items
		 */
		clear: () => {
			set([]);
			saveToStorage([]);
		},

		/**
		 * Get recent items of a specific type
		 */
		getByType: (type: PanelType): RecentItem[] => {
			const items = get({ subscribe });
			return items.filter((i) => i.type === type);
		},

		/**
		 * Check if an item is in recent items
		 */
		has: (itemId: string): boolean => {
			const items = get({ subscribe });
			return items.some((i) => i.id === itemId);
		},

		/**
		 * Get the most recent item
		 */
		getMostRecent: (): RecentItem | null => {
			const items = get({ subscribe });
			return items.length > 0 ? items[0] : null;
		},

		/**
		 * Get recent items up to a limit
		 */
		getRecent: (limit: number = 10): RecentItem[] => {
			const items = get({ subscribe });
			return items.slice(0, limit);
		},

		/**
		 * Manually refresh from storage
		 * Useful if storage was modified externally
		 */
		refresh: () => {
			set(loadFromStorage());
		}
	};
}

/**
 * Recent items store instance
 */
export const recent = createRecentStore();

/**
 * Derived store for recent item count
 */
export const recentCount = derived(recent, ($recent) => $recent.length);

/**
 * Derived store for recent clips
 */
export const recentClips = derived(recent, ($recent) =>
	$recent.filter((item) => item.type === 'clip')
);

/**
 * Derived store for recent songs
 */
export const recentSongs = derived(recent, ($recent) =>
	$recent.filter((item) => item.type === 'song')
);

/**
 * Derived store for recent playlists
 */
export const recentPlaylists = derived(recent, ($recent) =>
	$recent.filter((item) => item.type === 'playlist')
);

/**
 * Derived store for recent packs
 */
export const recentPacks = derived(recent, ($recent) =>
	$recent.filter((item) => item.type === 'pack')
);

/**
 * Derived store for items closed today
 */
export const recentToday = derived(recent, ($recent) => {
	const today = new Date();
	today.setHours(0, 0, 0, 0);

	return $recent.filter((item) => item.closedAt >= today);
});

/**
 * Derived store for items closed this week
 */
export const recentThisWeek = derived(recent, ($recent) => {
	const weekAgo = new Date();
	weekAgo.setDate(weekAgo.getDate() - 7);
	weekAgo.setHours(0, 0, 0, 0);

	return $recent.filter((item) => item.closedAt >= weekAgo);
});
