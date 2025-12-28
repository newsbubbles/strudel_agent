/**
 * WebSocket Service - Manages WebSocket connection to backend
 *
 * Features:
 * - Handshake protocol (REQUIRED by backend)
 * - Automatic reconnection with exponential backoff
 * - Message queueing while disconnected or handshaking
 * - Event-based message handling
 * - Integration with stores (websocket, history, sessions)
 *
 * Protocol: See notes/debug_chat/backend_protocol_spec.md
 */

import { websocket } from '$lib/stores/websocket';
import { history } from '$lib/stores/history';
import { sessions } from '$lib/stores/session';
import type {
	ClientMessage,
	ServerMessage,
	HandshakeAckMessage,
	AgentResponseMessage,
	TypingIndicatorMessage,
	ToolReportMessage,
	ToolResultMessage,
	ToolRequestMessage,
	ClipUpdatedMessage,
	ErrorMessage,
	NotificationMessage,
	FormRequestMessage,
	FileDownloadMessage,
	SessionStatusMessage
} from '$lib/types/websocket';
import {
	isServerMessage,
	isErrorMessage,
	createHandshakeMessage,
	createUserMessage
} from '$lib/types/websocket';
import { createAssistantMessage, createSystemMessage } from '$lib/types/message';

/**
 * Event handler function type
 */
type EventHandler<T = ServerMessage> = (message: T) => void;

/**
 * WebSocket service configuration
 */
interface WebSocketConfig {
	/** WebSocket URL */
	url: string;

	/** Maximum reconnection attempts */
	maxReconnectAttempts: number;

	/** Initial reconnection delay (ms) */
	reconnectDelay: number;

	/** Client version for handshake */
	clientVersion: string;
}

/**
 * Default configuration
 */
const DEFAULT_CONFIG: WebSocketConfig = {
	url: '', // Will be set based on window.location
	maxReconnectAttempts: 5,
	reconnectDelay: 1000,
	clientVersion: '1.0.0'
};

/**
 * WebSocket Service Class
 */
class WebSocketService {
	/** WebSocket instance */
	private ws: WebSocket | null = null;

	/** Service configuration */
	private config: WebSocketConfig;

	/** Event handlers by message type */
	private handlers = new Map<string, EventHandler[]>();

	/** Reconnection attempt counter */
	private reconnectAttempts = 0;

	/** Reconnection timeout ID */
	private reconnectTimeout: number | null = null;

	/** Whether service is intentionally disconnected */
	private intentionalDisconnect = false;

	/** Current session ID for handshake */
	private currentSessionId: string | null = null;

	/** Connection ID from handshake_ack */
	private connectionId: string | null = null;

	/** Whether handshake is complete */
	private handshakeComplete = false;

	/** Message queue for messages sent before handshake completes */
	private messageQueue: ClientMessage[] = [];

	constructor(config: Partial<WebSocketConfig> = {}) {
		this.config = { ...DEFAULT_CONFIG, ...config };

		// Set URL based on current location if not provided
		if (!this.config.url && typeof window !== 'undefined') {
			const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
			this.config.url = `${protocol}//${window.location.hostname}:8034/ws`;
		}
	}

	/**
	 * Connect to WebSocket server with a session ID
	 * Session must be created via REST API first: POST /api/sessions
	 */
	connect(sessionId: string): void {
		if (!sessionId) {
			console.error('[WS] Cannot connect without session ID');
			return;
		}

		if (this.ws?.readyState === WebSocket.OPEN && this.currentSessionId === sessionId) {
			console.log('[WS] Already connected to this session');
			return;
		}

		if (this.ws?.readyState === WebSocket.CONNECTING) {
			console.log('[WS] Connection already in progress');
			return;
		}

		// If switching sessions, disconnect first
		if (this.ws && this.currentSessionId !== sessionId) {
			this.disconnect();
		}

		this.currentSessionId = sessionId;
		this.intentionalDisconnect = false;
		this.handshakeComplete = false;
		websocket.setState(this.reconnectAttempts > 0 ? 'reconnecting' : 'connecting');

		try {
			console.log(`[WS] Connecting to ${this.config.url} for session ${sessionId}`);
			this.ws = new WebSocket(this.config.url);

			this.ws.onopen = this.handleOpen.bind(this);
			this.ws.onmessage = this.handleMessage.bind(this);
			this.ws.onerror = this.handleError.bind(this);
			this.ws.onclose = this.handleClose.bind(this);
		} catch (error) {
			const message = error instanceof Error ? error.message : 'Unknown error';
			console.error('[WS] Connection failed:', message);
			websocket.setState('error', message);
		}
	}

	/**
	 * Disconnect from WebSocket server
	 */
	disconnect(): void {
		this.intentionalDisconnect = true;
		this.clearReconnectTimeout();
		this.handshakeComplete = false;
		this.connectionId = null;

		if (this.ws) {
			this.ws.close();
			this.ws = null;
		}

		websocket.setState('disconnected');
		console.log('[WS] Disconnected');
	}

	/**
	 * Send a user message to the agent
	 * This is the main method for sending chat messages
	 */
	sendMessage(message: string, context?: Record<string, unknown>): void {
		if (!this.currentSessionId) {
			console.error('[WS] Cannot send message without session');
			return;
		}

		const payload = createUserMessage(this.currentSessionId, message, context);
		this.send(payload);
	}

	/**
	 * Send a message to the server
	 * Queues message if not connected or handshake not complete
	 */
	send(message: ClientMessage): void {
		// Don't queue handshake messages
		if (message.type === 'handshake') {
			if (this.ws?.readyState === WebSocket.OPEN) {
				const json = JSON.stringify(message);
				this.ws.send(json);
				console.log('[WS] Sent handshake');
			}
			return;
		}

		// Queue if not ready
		if (!this.isReady()) {
			console.log('[WS] Not ready, queueing message:', message.type);
			this.messageQueue.push(message);
			return;
		}

		if (this.ws?.readyState === WebSocket.OPEN) {
			const json = JSON.stringify(message);
			this.ws.send(json);
			console.log('[WS] Sent:', message.type);
		} else {
			console.warn('[WS] Socket not open, queueing message:', message.type);
			this.messageQueue.push(message);
		}
	}

	/**
	 * Register an event handler for a message type
	 */
	on<T extends ServerMessage = ServerMessage>(
		messageType: T['type'],
		handler: EventHandler<T>
	): void {
		if (!this.handlers.has(messageType)) {
			this.handlers.set(messageType, []);
		}
		this.handlers.get(messageType)!.push(handler as EventHandler);
	}

	/**
	 * Unregister an event handler
	 */
	off<T extends ServerMessage = ServerMessage>(
		messageType: T['type'],
		handler: EventHandler<T>
	): void {
		const handlers = this.handlers.get(messageType);
		if (handlers) {
			const index = handlers.indexOf(handler as EventHandler);
			if (index !== -1) {
				handlers.splice(index, 1);
			}
		}
	}

	/**
	 * Get current connection state
	 */
	getState(): 'disconnected' | 'connecting' | 'connected' | 'handshaking' | 'ready' | 'reconnecting' | 'error' {
		return websocket.getState();
	}

	/**
	 * Check if connected (socket open)
	 */
	isConnected(): boolean {
		return this.ws?.readyState === WebSocket.OPEN;
	}

	/**
	 * Check if ready to send messages (connected + handshake complete)
	 */
	isReady(): boolean {
		return this.isConnected() && this.handshakeComplete;
	}

	/**
	 * Get current session ID
	 */
	getSessionId(): string | null {
		return this.currentSessionId;
	}

	/**
	 * Get connection ID (assigned by server)
	 */
	getConnectionId(): string | null {
		return this.connectionId;
	}

	/**
	 * Handle WebSocket open event
	 */
	private handleOpen(): void {
		console.log('[WS] Connected, sending handshake...');
		websocket.setState('handshaking');

		// MUST send handshake immediately!
		if (this.currentSessionId) {
			const handshake = createHandshakeMessage(
				this.currentSessionId,
				this.config.clientVersion
			);
			this.send(handshake);
		} else {
			console.error('[WS] No session ID for handshake');
			this.disconnect();
		}
	}

	/**
	 * Handle incoming WebSocket message
	 */
	private handleMessage(event: MessageEvent): void {
		try {
			const message = JSON.parse(event.data);

			// Validate it's a server message
			if (!isServerMessage(message)) {
				console.warn('[WS] Received unknown message type:', message.type);
				return;
			}

			console.log('[WS] Received:', message.type);

			// Handle error messages
			if (isErrorMessage(message)) {
				console.error('[WS] Server error:', message);
				websocket.setState('error', message.message);
			}

			// Emit to registered handlers
			const handlers = this.handlers.get(message.type) || [];
			handlers.forEach((handler) => handler(message));

			// Handle built-in message types
			this.handleBuiltInMessage(message);
		} catch (error) {
			console.error('[WS] Failed to parse message:', error);
		}
	}

	/**
	 * Handle built-in message types
	 */
	private handleBuiltInMessage(message: ServerMessage): void {
		switch (message.type) {
			case 'handshake_ack':
				this.handleHandshakeAck(message);
				break;

			case 'typing_indicator':
				this.handleTypingIndicator(message);
				break;

			case 'tool_report':
				this.handleToolReport(message);
				break;

			case 'tool_result':
				this.handleToolResult(message);
				break;

			case 'tool_request':
				this.handleToolRequest(message);
				break;

			case 'agent_response':
				this.handleAgentResponse(message);
				break;

			case 'clip_updated':
				this.handleClipUpdated(message);
				break;

			case 'notification':
				this.handleNotification(message);
				break;

			case 'form_request':
				this.handleFormRequest(message);
				break;

			case 'file_download':
				this.handleFileDownload(message);
				break;

			case 'session_status':
				this.handleSessionStatus(message);
				break;

			case 'error':
				// Already handled above
				break;

			default:
				// Other message types handled by registered handlers
				break;
		}
	}

	/**
	 * Handle handshake acknowledgment
	 */
	private handleHandshakeAck(message: HandshakeAckMessage): void {
		console.log('[WS] Handshake complete:', message.connection_id);
		this.connectionId = message.connection_id;
		this.handshakeComplete = true;

		websocket.setState('ready');
		websocket.resetReconnectAttempts();
		this.reconnectAttempts = 0;

		// Update session store with connection info
		if (message.session_info) {
			console.log('[WS] Session info:', message.session_info);
		}

		// Send any queued messages
		this.sendQueuedMessages();
	}

	/**
	 * Handle typing indicator
	 */
	private handleTypingIndicator(message: TypingIndicatorMessage): void {
		// Update UI to show/hide typing indicator
		if (this.currentSessionId) {
			if (message.is_typing) {
				sessions.updateStatus(this.currentSessionId, 'active');
			} else {
				sessions.updateStatus(this.currentSessionId, 'idle');
			}
		}
		console.log('[WS] Agent typing:', message.is_typing, message.text || '');
	}

	/**
	 * Handle tool report (agent started using a tool)
	 */
	private handleToolReport(message: ToolReportMessage): void {
		console.log('[WS] Agent using tool:', message.tool_name);
		// Could show tool usage indicator in UI
	}

	/**
	 * Handle tool result
	 */
	private handleToolResult(message: ToolResultMessage): void {
		console.log('[WS] Tool result:', message.tool_name);
		// Could show tool result in UI
	}

	/**
	 * Handle tool request (server asking client to execute a tool)
	 */
	private handleToolRequest(message: ToolRequestMessage): void {
		console.log('[WS] Tool request:', message.tool_name, message.parameters);
		// TODO: Implement client-side tool execution
		// For now, respond with error
		this.send({
			type: 'tool_response',
			request_id: message.request_id,
			success: false,
			error: 'Client-side tools not implemented'
		});
	}

	/**
	 * Handle agent response
	 */
	private handleAgentResponse(message: AgentResponseMessage): void {
		// DEBUG: Log full response object for inspection
		console.log('[WS] Agent response FULL:', JSON.stringify(message, null, 2));
		console.log('[WS] Agent response content:', message.content);
		console.log('[WS] Agent response is_final:', message.is_final);
		console.log('[WS] Current session ID:', this.currentSessionId);

		if (!this.currentSessionId) {
			console.error('[WS] No current session ID, cannot add agent response to history!');
			return;
		}

		// Add to history
		const assistantMessage = createAssistantMessage(
			this.currentSessionId,
			message.content
		);
		console.log('[WS] Created assistant message:', assistantMessage);
		
		history.addMessage(this.currentSessionId, assistantMessage);
		console.log('[WS] Added message to history for session:', this.currentSessionId);

		// Update session status
		if (message.is_final) {
			sessions.updateStatus(this.currentSessionId, 'idle');
			sessions.touch(this.currentSessionId);
		}

		console.log('[WS] Agent response:', message.is_final ? '(final)' : '(streaming)');
	}

	/**
	 * Handle clip updated
	 */
	private handleClipUpdated(message: ClipUpdatedMessage): void {
		console.log('[WS] Clip updated:', message.clip_id);
		// TODO: Update clip in carousel/editor
	}

	/**
	 * Handle notification
	 */
	private handleNotification(message: NotificationMessage): void {
		console.log('[WS] Notification:', message.notification_type, message.message);
		// TODO: Show toast notification
	}

	/**
	 * Handle form request
	 */
	private handleFormRequest(message: FormRequestMessage): void {
		console.log('[WS] Form request:', message.form_id, message.title);
		// TODO: Show form dialog
	}

	/**
	 * Handle file download
	 */
	private handleFileDownload(message: FileDownloadMessage): void {
		console.log('[WS] File download:', message.filename, message.download_url);
		// TODO: Show download card
	}

	/**
	 * Handle session status update
	 */
	private handleSessionStatus(message: SessionStatusMessage): void {
		if (!this.currentSessionId) return;
		console.log('[WS] Session status:', message.status, message.message || '');
		// Map backend status to frontend session status
		const statusMap: Record<string, 'idle' | 'active' | 'error'> = {
			'active': 'active',
			'idle': 'idle',
			'working': 'active',
			'error': 'error',
			'complete': 'idle'
		};
		sessions.updateStatus(this.currentSessionId, statusMap[message.status] || 'idle');
	}

	/**
	 * Handle WebSocket error event
	 */
	private handleError(event: Event): void {
		console.error('[WS] Error:', event);
		websocket.setState('error', 'Connection error');
	}

	/**
	 * Handle WebSocket close event
	 */
	private handleClose(): void {
		console.log('[WS] Connection closed');
		this.handshakeComplete = false;
		this.connectionId = null;

		if (this.intentionalDisconnect) {
			websocket.setState('disconnected');
			return;
		}

		// Attempt reconnection
		if (this.reconnectAttempts < this.config.maxReconnectAttempts) {
			this.reconnectAttempts++;
			websocket.incrementReconnectAttempts();

			// Exponential backoff
			const delay = this.config.reconnectDelay * Math.pow(2, this.reconnectAttempts - 1);

			console.log(
				`[WS] Reconnecting in ${delay}ms (attempt ${this.reconnectAttempts}/${this.config.maxReconnectAttempts})`
			);

			this.reconnectTimeout = window.setTimeout(() => {
				if (this.currentSessionId) {
					this.connect(this.currentSessionId);
				}
			}, delay);
		} else {
			console.error('[WS] Max reconnection attempts reached');
			websocket.setState('error', 'Failed to reconnect');
		}
	}

	/**
	 * Send queued messages
	 */
	private sendQueuedMessages(): void {
		if (this.messageQueue.length > 0) {
			console.log(`[WS] Sending ${this.messageQueue.length} queued messages`);
			const queue = [...this.messageQueue];
			this.messageQueue = [];
			queue.forEach((message) => this.send(message));
		}
	}

	/**
	 * Clear reconnection timeout
	 */
	private clearReconnectTimeout(): void {
		if (this.reconnectTimeout !== null) {
			clearTimeout(this.reconnectTimeout);
			this.reconnectTimeout = null;
		}
	}
}

/**
 * Singleton WebSocket service instance
 */
export const wsService = new WebSocketService();

/**
 * Export the class for testing
 */
export { WebSocketService };
