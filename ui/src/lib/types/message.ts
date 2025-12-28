/**
 * Message type definitions for the Strudel Agent UI
 * 
 * Messages represent chat interactions between the user and the AI agent.
 */

/**
 * Message role - who sent the message
 */
export type MessageRole = 'user' | 'assistant' | 'system';

/**
 * Message status - delivery/processing state
 */
export type MessageStatus = 'pending' | 'sending' | 'sent' | 'error';

/**
 * Base message interface
 */
export interface Message {
	/** Unique identifier for the message */
	id: string;
	
	/** Session this message belongs to */
	sessionId: string;
	
	/** Who sent the message */
	role: MessageRole;
	
	/** Message content (markdown supported) */
	content: string;
	
	/** When the message was created */
	timestamp: Date;
	
	/** Message delivery status */
	status: MessageStatus;
	
	/** Optional error message if status is 'error' */
	error?: string;
	
	/** Optional metadata */
	metadata?: Record<string, unknown>;
}

/**
 * User message - sent by the user
 */
export interface UserMessage extends Message {
	role: 'user';
}

/**
 * Assistant message - sent by the AI agent
 */
export interface AssistantMessage extends Message {
	role: 'assistant';
	
	/** Optional code blocks extracted from the message */
	codeBlocks?: Array<{
		language: string;
		code: string;
	}>;
	
	/** Optional panel updates triggered by this message */
	panelUpdates?: Array<{
		panelId: string;
		updateType: 'code' | 'content' | 'metadata';
	}>;
}

/**
 * System message - automated system notifications
 */
export interface SystemMessage extends Message {
	role: 'system';
	
	/** Type of system message */
	systemType?: 'info' | 'warning' | 'error' | 'success';
}

/**
 * Union type of all message types
 */
export type AnyMessage = UserMessage | AssistantMessage | SystemMessage;

/**
 * Chat history for a session
 */
export interface ChatHistory {
	/** Session ID this history belongs to */
	sessionId: string;
	
	/** All messages in chronological order */
	messages: AnyMessage[];
	
	/** When the history was last updated */
	updatedAt: Date;
	
	/** Whether more older messages are available (pagination) */
	hasMore?: boolean;
	
	/** Index of the oldest loaded message (for pagination) */
	oldestIndex?: number;
}

/**
 * Type guard to check if a message is from the user
 */
export function isUserMessage(message: AnyMessage): message is UserMessage {
	return message.role === 'user';
}

/**
 * Type guard to check if a message is from the assistant
 */
export function isAssistantMessage(message: AnyMessage): message is AssistantMessage {
	return message.role === 'assistant';
}

/**
 * Type guard to check if a message is a system message
 */
export function isSystemMessage(message: AnyMessage): message is SystemMessage {
	return message.role === 'system';
}

/**
 * Helper to create a new user message
 */
export function createUserMessage(
	sessionId: string,
	content: string,
	messageId?: string
): UserMessage {
	return {
		id: messageId || crypto.randomUUID(),
		sessionId,
		role: 'user',
		content,
		timestamp: new Date(),
		status: 'pending'
	};
}

/**
 * Helper to create a new assistant message
 */
export function createAssistantMessage(
	sessionId: string,
	content: string,
	messageId?: string
): AssistantMessage {
	return {
		id: messageId || crypto.randomUUID(),
		sessionId,
		role: 'assistant',
		content,
		timestamp: new Date(),
		status: 'sent'
	};
}

/**
 * Helper to create a new system message
 */
export function createSystemMessage(
	sessionId: string,
	content: string,
	systemType: SystemMessage['systemType'] = 'info',
	messageId?: string
): SystemMessage {
	return {
		id: messageId || crypto.randomUUID(),
		sessionId,
		role: 'system',
		content,
		timestamp: new Date(),
		status: 'sent',
		systemType
	};
}

/**
 * Helper to create an empty chat history
 */
export function createChatHistory(sessionId: string): ChatHistory {
	return {
		sessionId,
		messages: [],
		updatedAt: new Date(),
		hasMore: false,
		oldestIndex: undefined
	};
}
