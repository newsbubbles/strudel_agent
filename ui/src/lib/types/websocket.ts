/**
 * WebSocket message protocol definitions for the Strudel Agent UI
 *
 * Defines the message format for bidirectional communication
 * between the UI and the backend agent.
 *
 * IMPORTANT: This file matches the backend protocol defined in:
 * - backend/src/models/messages.py
 * - notes/debug_chat/backend_protocol_spec.md
 */

import type { Message } from './message';

/**
 * WebSocket connection state
 */
export type WebSocketState = 'disconnected' | 'connecting' | 'connected' | 'handshaking' | 'ready' | 'reconnecting' | 'error';

// ============================================================================
// Client -> Server Message Types
// ============================================================================

/**
 * Handshake message - MUST be sent immediately after WebSocket connects
 */
export interface HandshakeMessage {
	type: 'handshake';
	session_id: string;
	client_type: 'pwa' | 'mcp';
	client_version?: string;
}

/**
 * User message to the agent
 */
export interface UserMessagePayload {
	type: 'user_message';
	session_id: string;
	message: string;
	context?: Record<string, unknown>;
}

/**
 * Tool response from client (for client-side tools)
 */
export interface ToolResponseMessage {
	type: 'tool_response';
	request_id: string;
	success: boolean;
	data?: unknown;
	error?: string;
}

/**
 * Union of all client message types
 */
export type ClientMessage = HandshakeMessage | UserMessagePayload | ToolResponseMessage;

// ============================================================================
// Server -> Client Message Types
// ============================================================================

/**
 * Handshake acknowledgment from server
 */
export interface HandshakeAckMessage {
	type: 'handshake_ack';
	session_id: string;
	connection_id: string;
	is_reconnect: boolean;
	session_info?: {
		session_id: string;
		session_type: string;
		item_id: string;
		project_id: string;
		agent: string;
		last_activity: string;
		message_count: number;
	};
}

/**
 * Typing indicator - agent is thinking
 */
export interface TypingIndicatorMessage {
	type: 'typing_indicator';
	is_typing: boolean;
	text?: string;
}

/**
 * Tool report - agent started using a tool
 */
export interface ToolReportMessage {
	type: 'tool_report';
	tool_name: string;
	tool_call_id?: string;
}

/**
 * Tool result - tool execution completed
 */
export interface ToolResultMessage {
	type: 'tool_result';
	tool_name: string;
	content: unknown;
}

/**
 * Tool request - server asking client to execute a tool
 */
export interface ToolRequestMessage {
	type: 'tool_request';
	request_id: string;
	tool_name: string;
	parameters: Record<string, unknown>;
	timeout_ms: number;
}

/**
 * Agent response - the agent's text reply
 */
export interface AgentResponseMessage {
	type: 'agent_response';
	content: string;
	is_final: boolean;
}

/**
 * Clip updated by agent
 */
export interface ClipUpdatedMessage {
	type: 'clip_updated';
	clip_id: string;
	new_code: string;
	metadata?: Record<string, unknown>;
}

/**
 * Song updated by agent
 */
export interface SongUpdatedMessage {
	type: 'song_updated';
	song_id: string;
	metadata?: Record<string, unknown>;
}

/**
 * Playlist updated by agent
 */
export interface PlaylistUpdatedMessage {
	type: 'playlist_updated';
	playlist_id: string;
	metadata?: Record<string, unknown>;
}

/**
 * Player state update
 */
export interface PlayerStateUpdateMessage {
	type: 'player_state_update';
	is_playing: boolean;
	loaded_clips: string[];
	current_bpm: number;
}

/**
 * Error message from server
 */
export interface ErrorMessage {
	type: 'error';
	code: string;
	message: string;
	details?: unknown;
}

/**
 * Notification from server
 */
export interface NotificationMessage {
	type: 'notification';
	title?: string;
	message: string;
	notification_type: 'info' | 'warning' | 'error' | 'success';
	duration?: number;
	persistent?: boolean;
}

/**
 * Form request from server
 */
export interface FormRequestMessage {
	type: 'form_request';
	form_id: string;
	title: string;
	fields: Array<{
		name: string;
		label: string;
		type: string;
		required?: boolean;
		options?: string[];
		default_value?: string;
	}>;
	timeout_seconds?: number;
}

/**
 * File download available
 */
export interface FileDownloadMessage {
	type: 'file_download';
	file_path: string;
	filename: string;
	description: string;
	download_url: string;
}

/**
 * Session status update
 */
export interface SessionStatusMessage {
	type: 'session_status';
	status: 'active' | 'idle' | 'working' | 'error' | 'complete';
	message?: string;
	progress?: number;
}

/**
 * Union of all server message types
 */
export type ServerMessage =
	| HandshakeAckMessage
	| TypingIndicatorMessage
	| ToolReportMessage
	| ToolResultMessage
	| ToolRequestMessage
	| AgentResponseMessage
	| ClipUpdatedMessage
	| SongUpdatedMessage
	| PlaylistUpdatedMessage
	| PlayerStateUpdateMessage
	| ErrorMessage
	| NotificationMessage
	| FormRequestMessage
	| FileDownloadMessage
	| SessionStatusMessage;

/**
 * All message types
 */
export type WSMessage = ClientMessage | ServerMessage;

// ============================================================================
// Type Guards
// ============================================================================

/**
 * All server message types for validation
 */
const SERVER_MESSAGE_TYPES = [
	'handshake_ack',
	'typing_indicator',
	'tool_report',
	'tool_result',
	'tool_request',
	'agent_response',
	'clip_updated',
	'song_updated',
	'playlist_updated',
	'player_state_update',
	'error',
	'notification',
	'form_request',
	'file_download',
	'session_status'
] as const;

/**
 * Type guard to check if a message is from the server
 */
export function isServerMessage(message: { type: string }): message is ServerMessage {
	return SERVER_MESSAGE_TYPES.includes(message.type as (typeof SERVER_MESSAGE_TYPES)[number]);
}

/**
 * Type guard to check if a message is an error
 */
export function isErrorMessage(message: WSMessage): message is ErrorMessage {
	return message.type === 'error';
}

/**
 * Type guard for handshake ack
 */
export function isHandshakeAck(message: WSMessage): message is HandshakeAckMessage {
	return message.type === 'handshake_ack';
}

/**
 * Type guard for agent response
 */
export function isAgentResponse(message: WSMessage): message is AgentResponseMessage {
	return message.type === 'agent_response';
}

/**
 * Type guard for typing indicator
 */
export function isTypingIndicator(message: WSMessage): message is TypingIndicatorMessage {
	return message.type === 'typing_indicator';
}

// ============================================================================
// Helper Functions
// ============================================================================

/**
 * Create a handshake message
 */
export function createHandshakeMessage(
	sessionId: string,
	clientVersion?: string
): HandshakeMessage {
	return {
		type: 'handshake',
		session_id: sessionId,
		client_type: 'pwa',
		client_version: clientVersion
	};
}

/**
 * Create a user message
 */
export function createUserMessage(
	sessionId: string,
	message: string,
	context?: Record<string, unknown>
): UserMessagePayload {
	return {
		type: 'user_message',
		session_id: sessionId,
		message,
		context
	};
}

/**
 * Create a tool response message
 */
export function createToolResponse(
	requestId: string,
	success: boolean,
	data?: unknown,
	error?: string
): ToolResponseMessage {
	return {
		type: 'tool_response',
		request_id: requestId,
		success,
		data,
		error
	};
}
