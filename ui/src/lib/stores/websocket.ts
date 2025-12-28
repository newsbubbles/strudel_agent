/**
 * WebSocket store - Manages WebSocket connection state
 *
 * Tracks connection status, errors, and message queue.
 * Works with the WebSocket service to manage connectivity.
 *
 * States:
 * - disconnected: Not connected
 * - connecting: WebSocket connecting
 * - handshaking: Connected, waiting for handshake_ack
 * - ready: Handshake complete, can send messages
 * - reconnecting: Attempting to reconnect
 * - error: Connection error
 */

import { writable, derived, get } from 'svelte/store';
import type { WebSocketState, ClientMessage } from '$lib/types';

/**
 * WebSocket store state interface
 */
interface WSStoreState {
	/** Current connection state */
	state: WebSocketState;

	/** Error message if state is 'error' */
	error: string | null;

	/** Messages queued while disconnected */
	messageQueue: ClientMessage[];

	/** Number of reconnection attempts */
	reconnectAttempts: number;

	/** Last connection timestamp */
	lastConnectedAt: Date | null;

	/** Last disconnection timestamp */
	lastDisconnectedAt: Date | null;

	/** Current session ID */
	sessionId: string | null;

	/** Connection ID from server */
	connectionId: string | null;
}

/**
 * Initial WebSocket state
 */
const initialState: WSStoreState = {
	state: 'disconnected',
	error: null,
	messageQueue: [],
	reconnectAttempts: 0,
	lastConnectedAt: null,
	lastDisconnectedAt: null,
	sessionId: null,
	connectionId: null
};

/**
 * Create the WebSocket store
 */
function createWebSocketStore() {
	const { subscribe, set, update } = writable<WSStoreState>(initialState);

	return {
		subscribe,

		/**
		 * Set the connection state
		 */
		setState: (state: WebSocketState, error: string | null = null) => {
			update((s) => {
				const updates: Partial<WSStoreState> = { state, error };

				// Track connection/disconnection times
				if (state === 'ready') {
					updates.lastConnectedAt = new Date();
					updates.reconnectAttempts = 0;
				} else if (state === 'disconnected' || state === 'error') {
					updates.lastDisconnectedAt = new Date();
				}

				return { ...s, ...updates };
			});
		},

		/**
		 * Set session and connection IDs
		 */
		setConnection: (sessionId: string, connectionId: string) => {
			update((s) => ({
				...s,
				sessionId,
				connectionId
			}));
		},

		/**
		 * Queue a message to be sent when connection is established
		 */
		queueMessage: (message: ClientMessage) => {
			update((s) => ({
				...s,
				messageQueue: [...s.messageQueue, message]
			}));
		},

		/**
		 * Clear the message queue
		 * Returns the messages that were queued
		 */
		clearQueue: (): ClientMessage[] => {
			const state = get({ subscribe });
			const messages = [...state.messageQueue];

			update((s) => ({
				...s,
				messageQueue: []
			}));

			return messages;
		},

		/**
		 * Increment reconnection attempt counter
		 */
		incrementReconnectAttempts: () => {
			update((s) => ({
				...s,
				reconnectAttempts: s.reconnectAttempts + 1
			}));
		},

		/**
		 * Reset reconnection attempt counter
		 */
		resetReconnectAttempts: () => {
			update((s) => ({
				...s,
				reconnectAttempts: 0
			}));
		},

		/**
		 * Get current state
		 */
		getState: (): WebSocketState => {
			const state = get({ subscribe });
			return state.state;
		},

		/**
		 * Check if ready to send messages
		 */
		isReady: (): boolean => {
			const state = get({ subscribe });
			return state.state === 'ready';
		},

		/**
		 * Check if connected (socket open, may or may not have handshake)
		 */
		isConnected: (): boolean => {
			const state = get({ subscribe });
			return state.state === 'connected' || state.state === 'handshaking' || state.state === 'ready';
		},

		/**
		 * Check if connecting
		 */
		isConnecting: (): boolean => {
			const state = get({ subscribe });
			return state.state === 'connecting' || state.state === 'reconnecting' || state.state === 'handshaking';
		},

		/**
		 * Clear all state
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
 * WebSocket store instance
 */
export const websocket = createWebSocketStore();

/**
 * Derived store for connection state
 */
export const connectionState = derived(websocket, ($ws) => $ws.state);

/**
 * Derived store for ready status (can send messages)
 */
export const isReady = derived(websocket, ($ws) => $ws.state === 'ready');

/**
 * Derived store for connected status (socket open)
 */
export const isConnected = derived(
	websocket,
	($ws) => $ws.state === 'connected' || $ws.state === 'handshaking' || $ws.state === 'ready'
);

/**
 * Derived store for connecting status
 */
export const isConnecting = derived(
	websocket,
	($ws) => $ws.state === 'connecting' || $ws.state === 'reconnecting' || $ws.state === 'handshaking'
);

/**
 * Derived store for error status
 */
export const hasError = derived(websocket, ($ws) => $ws.state === 'error');

/**
 * Derived store for error message
 */
export const errorMessage = derived(websocket, ($ws) => $ws.error);

/**
 * Derived store for queued message count
 */
export const queuedMessageCount = derived(websocket, ($ws) => $ws.messageQueue.length);

/**
 * Derived store for reconnect attempts
 */
export const reconnectAttempts = derived(websocket, ($ws) => $ws.reconnectAttempts);
