/**
 * History store - Manages chat message history per session
 * 
 * Stores messages for each session with support for:
 * - Adding new messages
 * - Loading older messages (pagination)
 * - Clearing history
 * 
 * IMPORTANT: Uses immutable update patterns for Svelte reactivity.
 * Map objects must be replaced (not mutated) to trigger store updates.
 */

import { writable, derived, get } from 'svelte/store';
import type { ChatHistory, AnyMessage } from '$lib/types';

/**
 * History state interface
 */
interface HistoryState {
	/** Map of sessionId to ChatHistory */
	histories: Map<string, ChatHistory>;
}

/**
 * Create a fresh initial state (new Map instance)
 */
function createInitialState(): HistoryState {
	return {
		histories: new Map()
	};
}

/**
 * Create the history store
 */
function createHistoryStore() {
	const { subscribe, set, update } = writable<HistoryState>(createInitialState());

	/**
	 * Helper to create a new state with updated history.
	 * Always creates new Map and ChatHistory objects for proper reactivity.
	 */
	function updateHistory(
		state: HistoryState,
		sessionId: string,
		updater: (history: ChatHistory) => ChatHistory
	): HistoryState {
		const existingHistory = state.histories.get(sessionId);
		const baseHistory: ChatHistory = existingHistory ?? {
			sessionId,
			messages: [],
			updatedAt: new Date(),
			hasMore: false,
			oldestIndex: undefined
		};
		
		const updatedHistory = updater(baseHistory);
		const newHistories = new Map(state.histories);
		newHistories.set(sessionId, updatedHistory);
		
		return { histories: newHistories };
	}

	return {
		subscribe,

		/**
		 * Get or create a chat history for a session
		 */
		getOrCreate: (sessionId: string): ChatHistory => {
			const state = get({ subscribe });

			// Return existing history if found
			const existing = state.histories.get(sessionId);
			if (existing) {
				return existing;
			}

			// Create new history
			const history: ChatHistory = {
				sessionId,
				messages: [],
				updatedAt: new Date(),
				hasMore: false,
				oldestIndex: undefined
			};

			// Add to store with immutable update
			update((state) => {
				const newHistories = new Map(state.histories);
				newHistories.set(sessionId, history);
				return { histories: newHistories };
			});

			return history;
		},

		/**
		 * Get a chat history by session ID
		 * Returns null if no history exists
		 */
		get: (sessionId: string): ChatHistory | null => {
			const state = get({ subscribe });
			return state.histories.get(sessionId) ?? null;
		},

		/**
		 * Add a message to a session's history
		 */
		addMessage: (sessionId: string, message: AnyMessage) => {
			update((state) => 
				updateHistory(state, sessionId, (history) => ({
					...history,
					messages: [...history.messages, message],
					updatedAt: new Date()
				}))
			);
		},

		/**
		 * Add multiple messages to a session's history
		 */
		addMessages: (sessionId: string, messages: AnyMessage[]) => {
			update((state) => 
				updateHistory(state, sessionId, (history) => ({
					...history,
					messages: [...history.messages, ...messages],
					updatedAt: new Date()
				}))
			);
		},

		/**
		 * Prepend older messages to the beginning of history
		 * Used for pagination when loading older messages
		 */
		prependMessages: (sessionId: string, messages: AnyMessage[], hasMore: boolean = false, oldestIndex?: number) => {
			update((state) => {
				const existingHistory = state.histories.get(sessionId);
				if (!existingHistory) return state;

				const updatedHistory: ChatHistory = {
					...existingHistory,
					messages: [...messages, ...existingHistory.messages],
					updatedAt: new Date(),
					hasMore,
					oldestIndex
				};

				const newHistories = new Map(state.histories);
				newHistories.set(sessionId, updatedHistory);
				return { histories: newHistories };
			});
		},

		/**
		 * Update pagination state for a history
		 */
		updatePagination: (sessionId: string, hasMore: boolean, oldestIndex?: number) => {
			update((state) => {
				const existingHistory = state.histories.get(sessionId);
				if (!existingHistory) return state;

				const updatedHistory: ChatHistory = {
					...existingHistory,
					hasMore,
					oldestIndex
				};

				const newHistories = new Map(state.histories);
				newHistories.set(sessionId, updatedHistory);
				return { histories: newHistories };
			});
		},

		/**
		 * Update a specific message
		 */
		updateMessage: (sessionId: string, messageId: string, updates: Partial<AnyMessage>) => {
			update((state) => {
				const existingHistory = state.histories.get(sessionId);
				if (!existingHistory) return state;

				const messageIndex = existingHistory.messages.findIndex((m) => m.id === messageId);
				if (messageIndex === -1) return state;

				// Create new messages array with updated message
				const newMessages = [...existingHistory.messages];
				newMessages[messageIndex] = {
					...newMessages[messageIndex],
					...updates
				};

				const updatedHistory: ChatHistory = {
					...existingHistory,
					messages: newMessages,
					updatedAt: new Date()
				};

				const newHistories = new Map(state.histories);
				newHistories.set(sessionId, updatedHistory);
				return { histories: newHistories };
			});
		},

		/**
		 * Remove a message from history
		 */
		removeMessage: (sessionId: string, messageId: string) => {
			update((state) => {
				const existingHistory = state.histories.get(sessionId);
				if (!existingHistory) return state;

				const updatedHistory: ChatHistory = {
					...existingHistory,
					messages: existingHistory.messages.filter((m) => m.id !== messageId),
					updatedAt: new Date()
				};

				const newHistories = new Map(state.histories);
				newHistories.set(sessionId, updatedHistory);
				return { histories: newHistories };
			});
		},

		/**
		 * Clear a session's history
		 */
		clearHistory: (sessionId: string) => {
			update((state) => {
				const existingHistory = state.histories.get(sessionId);
				if (!existingHistory) return state;

				const updatedHistory: ChatHistory = {
					...existingHistory,
					messages: [],
					updatedAt: new Date(),
					hasMore: false,
					oldestIndex: undefined
				};

				const newHistories = new Map(state.histories);
				newHistories.set(sessionId, updatedHistory);
				return { histories: newHistories };
			});
		},

		/**
		 * Remove a session's history entirely
		 */
		remove: (sessionId: string) => {
			update((state) => {
				const newHistories = new Map(state.histories);
				newHistories.delete(sessionId);
				return { histories: newHistories };
			});
		},

		/**
		 * Get message count for a session
		 */
		getMessageCount: (sessionId: string): number => {
			const state = get({ subscribe });
			const history = state.histories.get(sessionId);
			return history ? history.messages.length : 0;
		},

		/**
		 * Check if a session has history
		 */
		has: (sessionId: string): boolean => {
			const state = get({ subscribe });
			return state.histories.has(sessionId);
		},

		/**
		 * Get all histories
		 */
		getAll: (): ChatHistory[] => {
			const state = get({ subscribe });
			return Array.from(state.histories.values());
		},

		/**
		 * Clear all histories
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
 * History store instance
 */
export const history = createHistoryStore();

/**
 * Derived store for total message count across all sessions
 */
export const totalMessageCount = derived(history, ($history) => {
	let count = 0;
	for (const chatHistory of $history.histories.values()) {
		count += chatHistory.messages.length;
	}
	return count;
});

/**
 * Derived store for session count with messages
 */
export const sessionWithMessagesCount = derived(
	history,
	($history) => $history.histories.size
);
