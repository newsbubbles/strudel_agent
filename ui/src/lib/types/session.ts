/**
 * Session type definitions for the Strudel Agent UI
 * 
 * Sessions represent active conversations with the AI agent.
 * Each panel can have its own session.
 */

import type { Panel } from './panel';

/**
 * Session type - matches panel type
 */
export type SessionType = 'clip' | 'song' | 'playlist' | 'pack';

/**
 * Session status values
 */
export type SessionStatus = 'idle' | 'connecting' | 'active' | 'error' | 'closed';

/**
 * Session interface
 * Represents an active conversation with the agent for a specific panel
 */
export interface Session {
	/** Unique identifier for the session */
	id: string;
	
	/** ID of the panel this session is attached to */
	panelId: string;
	
	/** Current status of the session */
	status: SessionStatus;
	
	/** When the session was created */
	createdAt: Date;
	
	/** When the session was last active */
	lastActiveAt: Date;
	
	/** WebSocket connection ID (if connected) */
	connectionId?: string;
	
	/** Optional error message if status is 'error' */
	error?: string;
	
	/** Optional metadata for the session */
	metadata?: Record<string, unknown>;
}

/**
 * Session with associated panel data
 * Used when you need both session and panel information together
 */
export interface SessionWithPanel extends Session {
	/** The panel associated with this session */
	panel: Panel;
}

/**
 * Helper to create a new session
 */
export function createSession(panelId: string, sessionId?: string): Session {
	const now = new Date();
	return {
		id: sessionId || crypto.randomUUID(),
		panelId,
		status: 'idle',
		createdAt: now,
		lastActiveAt: now
	};
}

/**
 * Type guard to check if a session is active
 */
export function isSessionActive(session: Session): boolean {
	return session.status === 'active' || session.status === 'connecting';
}

/**
 * Type guard to check if a session has an error
 */
export function isSessionError(session: Session): boolean {
	return session.status === 'error';
}
