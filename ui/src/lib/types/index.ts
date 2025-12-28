/**
 * Type definitions barrel export
 *
 * Re-exports all type definitions for convenient importing.
 * Usage: import { Panel, Session, Message } from '$lib/types';
 */

// Panel types
export type {
	PanelType,
	BasePanel,
	ClipPanel,
	SongPanel,
	PlaylistPanel,
	PackPanel,
	Panel,
	ClipReference,
	SongReference
} from './panel';

export {
	isClipPanel,
	isSongPanel,
	isPlaylistPanel,
	isPackPanel,
	createClipPanel,
	createSongPanel,
	createPlaylistPanel,
	createPackPanel
} from './panel';

// Session types
export type { SessionStatus, Session, SessionWithPanel } from './session';

export { createSession, isSessionActive, isSessionError } from './session';

// Message types
export type {
	MessageRole,
	MessageStatus,
	Message,
	UserMessage,
	AssistantMessage,
	SystemMessage,
	AnyMessage,
	ChatHistory
} from './message';

export {
	isUserMessage,
	isAssistantMessage,
	isSystemMessage,
	createUserMessage,
	createAssistantMessage,
	createSystemMessage,
	createChatHistory
} from './message';

// WebSocket types
export type {
	WebSocketState,
	// Client messages
	HandshakeMessage,
	UserMessagePayload,
	ToolResponseMessage,
	ClientMessage,
	// Server messages
	HandshakeAckMessage,
	TypingIndicatorMessage,
	ToolReportMessage,
	ToolResultMessage,
	ToolRequestMessage,
	AgentResponseMessage,
	ClipUpdatedMessage,
	SongUpdatedMessage,
	PlaylistUpdatedMessage,
	PlayerStateUpdateMessage,
	ErrorMessage,
	NotificationMessage,
	FormRequestMessage,
	FileDownloadMessage,
	SessionStatusMessage,
	ServerMessage,
	WSMessage
} from './websocket';

export {
	isServerMessage,
	isErrorMessage,
	isHandshakeAck,
	isAgentResponse,
	isTypingIndicator,
	createHandshakeMessage,
	createUserMessage as createWSUserMessage,
	createToolResponse
} from './websocket';

// Strudel types
export type {
	PlayerState,
	StrudelPattern,
	GlobalPlayerState,
	EvaluationResult
} from './strudel';

export {
	createDefaultPlayerState,
	isPlayerActive,
	canStartPlayer,
	canStopPlayer
} from './strudel';
