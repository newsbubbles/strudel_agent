/**
 * Player store - Manages global Strudel player state
 *
 * This store tracks playback state for the @strudel/web REPL.
 * Actual playback control is handled by strudelService using:
 * - evaluate(code, autoplay) - to play/update patterns
 * - hush() - to stop all patterns
 *
 * This store is for UI state synchronization only.
 */

import { writable, derived, get } from 'svelte/store';
import type { GlobalPlayerState, PlayerState } from '$lib/types';

/**
 * Initial player state
 */
const initialState: GlobalPlayerState = {
	initialized: false,
	state: 'stopped',
	volume: 0.7,
	cps: 0.5,
	loadedClips: []
};

/**
 * Create the player store
 */
function createPlayerStore() {
	const { subscribe, set, update } = writable<GlobalPlayerState>(initialState);

	return {
		subscribe,

		/**
		 * Set initialized state (called by strudelService after init)
		 */
		setInitialized: (initialized: boolean) => {
			update((s) => ({ ...s, initialized }));
		},

		/**
		 * Set player state
		 */
		setState: (state: PlayerState, error?: string) => {
			update((s) => ({ ...s, state, error }));
		},

		/**
		 * Set playing state (called by strudelService)
		 */
		setPlaying: (isPlaying: boolean) => {
			update((s) => ({ ...s, state: isPlaying ? 'playing' : 'stopped', error: undefined }));
		},

		/**
		 * Set error state with message
		 */
		setError: (error: string) => {
			update((s) => ({ ...s, state: 'error', error }));
		},

		/**
		 * Clear error state
		 */
		clearError: () => {
			update((s) => {
				if (s.state === 'error') {
					return { ...s, state: 'stopped', error: undefined };
				}
				return { ...s, error: undefined };
			});
		},

		/**
		 * Set volume (0-1) - UI state only
		 */
		setVolume: (volume: number) => {
			const clampedVolume = Math.max(0, Math.min(1, volume));
			update((s) => ({ ...s, volume: clampedVolume }));
		},

		/**
		 * Set tempo (cycles per second) - UI state only
		 */
		setCPS: (cps: number) => {
			const clampedCPS = Math.max(0.1, Math.min(10, cps));
			update((s) => ({ ...s, cps: clampedCPS }));
		},

		/**
		 * Add a clip to the loaded clips list
		 */
		addClip: (clipId: string) => {
			update((s) => {
				if (!s.loadedClips.includes(clipId)) {
					return {
						...s,
						loadedClips: [...s.loadedClips, clipId]
					};
				}
				return s;
			});
		},

		/**
		 * Remove a clip from the loaded clips list
		 */
		removeClip: (clipId: string) => {
			update((s) => ({
				...s,
				loadedClips: s.loadedClips.filter((id) => id !== clipId)
			}));
		},

		/**
		 * Set all loaded clips
		 */
		setLoadedClips: (clipIds: string[]) => {
			update((s) => ({ ...s, loadedClips: clipIds }));
		},

		/**
		 * Clear all loaded clips
		 */
		clearClips: () => {
			update((s) => ({ ...s, loadedClips: [] }));
		},

		/**
		 * Get current state
		 */
		getState: (): PlayerState => {
			const state = get({ subscribe });
			return state.state;
		},

		/**
		 * Check if player is playing
		 */
		isPlaying: (): boolean => {
			const state = get({ subscribe });
			return state.state === 'playing';
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
 * Player store instance
 */
export const player = createPlayerStore();

/**
 * Derived store for initialized status
 */
export const isStrudelInitialized = derived(player, ($player) => $player.initialized);

/**
 * Derived store for player state
 */
export const playerState = derived(player, ($player) => $player.state);

/**
 * Derived store for playing status
 */
export const isPlaying = derived(player, ($player) => $player.state === 'playing');

/**
 * Derived store for stopped status
 */
export const isStopped = derived(player, ($player) => $player.state === 'stopped');

/**
 * Derived store for loading status
 */
export const isLoading = derived(player, ($player) => $player.state === 'loading');

/**
 * Derived store for error status
 */
export const hasPlayerError = derived(player, ($player) => $player.state === 'error');

/**
 * Derived store for error message
 */
export const playerError = derived(player, ($player) => $player.error);

/**
 * Derived store for volume
 */
export const volume = derived(player, ($player) => $player.volume);

/**
 * Derived store for tempo (CPS)
 */
export const cps = derived(player, ($player) => $player.cps);

/**
 * Derived store for loaded clips
 */
export const loadedClips = derived(player, ($player) => $player.loadedClips);

/**
 * Derived store for loaded clip count
 */
export const loadedClipCount = derived(player, ($player) => $player.loadedClips.length);
