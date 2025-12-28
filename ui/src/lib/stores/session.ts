/**
 * Session store - Manages active chat sessions per panel
 * 
 * Each panel can have its own session for chatting with the agent.
 * Sessions are created on-demand and cleaned up when panels close.
 * 
 * IMPORTANT: Uses immutable update patterns for Svelte reactivity.
 * Map objects must be replaced (not mutated) to trigger store updates.
 */

import { writable, derived, get } from 'svelte/store';
import type { Session } from '$lib/types';

/**
 * Session state interface
 */
interface SessionState {
	/** Map of panelId to Session */
	sessions: Map<string, Session>;
}

/**
 * Create a fresh initial state (new Map instance)
 */
function createInitialState(): SessionState {
	return {
		sessions: new Map()
	};
}

/**
 * Create the session store
 */
function createSessionStore() {
	const { subscribe, set, update } = writable<SessionState>(createInitialState());

	/**
	 * Helper to create a new state with updated session.
	 * Always creates new Map and Session objects for proper reactivity.
	 */
	function updateSession(
		state: SessionState,
		panelId: string,
		updater: (session: Session) => Session
	): SessionState {
		const existingSession = state.sessions.get(panelId);
		if (!existingSession) return state;
		
		const updatedSession = updater(existingSession);
		const newSessions = new Map(state.sessions);
		newSessions.set(panelId, updatedSession);
		
		return { sessions: newSessions };
	}

	return {
		subscribe,

		/**
		 * Get or create a session for a panel
		 * Returns existing session if one exists, otherwise creates new
		 */
		getOrCreate: (panelId: string): Session => {
			const state = get({ subscribe });

			// Return existing session if found
			const existing = state.sessions.get(panelId);
			if (existing) {
				return existing;
			}

			// Create new session
			const session: Session = {
				id: crypto.randomUUID(),
				panelId,
				status: 'idle',
				createdAt: new Date(),
				lastActiveAt: new Date()
			};

			// Add to store with immutable update
			update((state) => {
				const newSessions = new Map(state.sessions);
				newSessions.set(panelId, session);
				return { sessions: newSessions };
			});

			return session;
		},

		/**
		 * Get a session by panel ID
		 * Returns null if no session exists
		 */
		get: (panelId: string): Session | null => {
			const state = get({ subscribe });
			return state.sessions.get(panelId) ?? null;
		},

		/**
		 * Update a session's status
		 */
		updateStatus: (panelId: string, status: Session['status'], error?: string) => {
			update((state) => 
				updateSession(state, panelId, (session) => ({
					...session,
					status,
					lastActiveAt: new Date(),
					error: error !== undefined ? error : session.error
				}))
			);
		},

		/**
		 * Update session metadata
		 */
		updateMetadata: (panelId: string, metadata: Record<string, unknown>) => {
			update((state) => 
				updateSession(state, panelId, (session) => ({
					...session,
					metadata: { ...session.metadata, ...metadata },
					lastActiveAt: new Date()
				}))
			);
		},

		/**
		 * Set WebSocket connection ID for a session
		 */
		setConnectionId: (panelId: string, connectionId: string) => {
			update((state) => 
				updateSession(state, panelId, (session) => ({
					...session,
					connectionId,
					lastActiveAt: new Date()
				}))
			);
		},

		/**
		 * Touch a session (update last active time)
		 */
		touch: (panelId: string) => {
			update((state) => 
				updateSession(state, panelId, (session) => ({
					...session,
					lastActiveAt: new Date()
				}))
			);
		},

		/**
		 * Remove a session
		 */
		remove: (panelId: string) => {
			update((state) => {
				const newSessions = new Map(state.sessions);
				newSessions.delete(panelId);
				return { sessions: newSessions };
			});
		},

		/**
		 * Check if a session exists
		 */
		has: (panelId: string): boolean => {
			const state = get({ subscribe });
			return state.sessions.has(panelId);
		},

		/**
		 * Get all sessions
		 */
		getAll: (): Session[] => {
			const state = get({ subscribe });
			return Array.from(state.sessions.values());
		},

		/**
		 * Clear all sessions
		 */
		clear: () => {
			set(createInitialState());
		},

		/**
		 * Reset to initial state
		 */
		reset: () => {
			set(createInitialState());
		}
	};
}

/**
 * Session store instance
 */
export const sessions = createSessionStore();

/**
 * Derived store for session count
 */
export const sessionCount = derived(sessions, ($sessions) => $sessions.sessions.size);

/**
 * Derived store for active sessions (status = 'active')
 */
export const activeSessions = derived(sessions, ($sessions) =>
	Array.from($sessions.sessions.values()).filter((s) => s.status === 'active')
);

/**
 * Derived store for error sessions (status = 'error')
 */
export const errorSessions = derived(sessions, ($sessions) =>
	Array.from($sessions.sessions.values()).filter((s) => s.status === 'error')
);
