/**
 * Strudel Player Service - Headless @strudel/web integration
 *
 * Features:
 * - Initialize Strudel player (audio engine only)
 * - Combine multiple clips into stack() pattern
 * - Control playback (play, stop)
 * - Update player with new code
 * - Integration with player store
 * - Error forwarding to active chat session
 *
 * Note: Sample loading is handled by Strudel patterns themselves via samples() function.
 * The UI only manages playback control - Strudel does all the heavy lifting.
 */

import { player } from '$lib/stores/player';
import { currentPanel } from '$lib/stores/carousel';
import { sessions } from '$lib/stores/session';
import { history } from '$lib/stores/history';
import { wsService } from '$lib/services/websocket';
import { get } from 'svelte/store';
import { createUserMessage } from '$lib/types/message';
import type { Panel } from '$lib/types';
import type { GlobalPlayerState } from '$lib/types';

/**
 * Strudel global functions (loaded via CDN)
 */
declare global {
	/**
	 * Initialize Strudel (call once on app load)
	 */
	function initStrudel(options?: {
		autostart?: boolean;
	}): Promise<void>;

	/**
	 * Evaluate Strudel code and optionally start playback
	 */
	function evaluate(code: string, autostart?: boolean): void;

	/**
	 * Stop all playing patterns
	 */
	function hush(): void;
}

/**
 * Strudel error information
 */
export interface StrudelError {
	/** Error message */
	message: string;

	/** The code that caused the error */
	code?: string;

	/** Line number if available */
	line?: number;

	/** Column number if available */
	column?: number;

	/** Error type (syntax, runtime, etc.) */
	errorType?: 'syntax' | 'runtime' | 'sample' | 'unknown';
}

/**
 * Strudel Player Service Class
 */
class StrudelService {
	/** Whether Strudel has been initialized */
	private initialized = false;

	/** Current code loaded in player */
	private currentCode = '';

	/** Original console.error for restoration */
	private originalConsoleError: typeof console.error | null = null;

	/**
	 * Initialize Strudel player
	 * Just sets up the audio engine - no sample loading.
	 * Samples are loaded by patterns themselves via samples() function.
	 */
	async initialize(): Promise<void> {
		if (this.initialized) {
			console.warn('[Strudel] Already initialized');
			return;
		}

		try {
			// Check if @strudel/web is loaded
			if (typeof initStrudel === 'undefined') {
				throw new Error(
					'@strudel/web not loaded. Add <script src="https://unpkg.com/@strudel/web@latest"></script> to app.html'
				);
			}

			console.log('[Strudel] Initializing audio engine...');

			// Set up error interception before initializing
			this.setupErrorInterception();

			// Initialize Strudel - just the audio engine, no prebaking
			await initStrudel({
				autostart: false // We control playback manually
			});

			this.initialized = true;
			
			// Update the player store so UI components react
			player.setInitialized(true);
			
			console.log('[Strudel] Audio engine initialized successfully');
		} catch (error) {
			console.error('[Strudel] Initialization failed:', error);
			throw error;
		}
	}

	/**
	 * Set up error interception to catch Strudel errors
	 *
	 * Strudel's evaluate() catches errors internally and logs them via console.error.
	 * We intercept console.error to catch these and forward to the agent.
	 */
	private setupErrorInterception(): void {
		// Store original console.error
		this.originalConsoleError = console.error;

		// Override console.error to intercept Strudel errors
		console.error = (...args: unknown[]) => {
			// Call original first
			this.originalConsoleError?.apply(console, args);

			// Check if this looks like a Strudel error
			const errorString = args.map((a) => String(a)).join(' ');

			// Strudel errors typically include these patterns
			if (
				errorString.includes('[eval]') ||
				errorString.includes('SyntaxError') ||
				errorString.includes('ReferenceError') ||
				errorString.includes('TypeError') ||
				errorString.includes('pattern') ||
				errorString.includes('strudel') ||
				errorString.includes('mini notation')
			) {
				this.handleStrudelError(this.parseError(args));
			}
		};
	}

	/**
	 * Parse error arguments into StrudelError
	 */
	private parseError(args: unknown[]): StrudelError {
		let message = '';
		let errorType: StrudelError['errorType'] = 'unknown';
		let line: number | undefined;
		let column: number | undefined;

		for (const arg of args) {
			if (arg instanceof Error) {
				message = arg.message;

				// Try to extract line/column from stack
				const stackMatch = arg.stack?.match(/:([0-9]+):([0-9]+)/);
				if (stackMatch) {
					line = parseInt(stackMatch[1], 10);
					column = parseInt(stackMatch[2], 10);
				}

				// Determine error type
				if (arg.name === 'SyntaxError') {
					errorType = 'syntax';
				} else if (arg.name === 'ReferenceError' || arg.name === 'TypeError') {
					errorType = 'runtime';
				}
			} else if (typeof arg === 'string') {
				if (!message) {
					message = arg;
				} else {
					message += ' ' + arg;
				}

				// Check for sample loading errors
				if (arg.includes('sample') || arg.includes('load')) {
					errorType = 'sample';
				}
			}
		}

		return {
			message: message || 'Unknown Strudel error',
			code: this.currentCode,
			line,
			column,
			errorType
		};
	}

	/**
	 * Handle a Strudel error by forwarding to the active session
	 */
	private handleStrudelError(error: StrudelError): void {
		console.log('[Strudel] Caught error:', error);

		// Update player store with error state
		player.setError(error.message);

		// Get the current panel to find the active session
		const panel = get(currentPanel) as Panel | null;
		if (!panel) {
			console.warn('[Strudel] No active panel to send error to');
			return;
		}

		// Get or create session for this panel
		const session = sessions.getOrCreate(panel.id);

		// Format error message for the agent
		const errorMessageText = this.formatErrorMessage(error);

		// Create a user message with the error
		const message = createUserMessage(session.id, errorMessageText);

		// Add to local history
		history.addMessage(session.id, message);

		// Send to backend via WebSocket using the correct flat format
		// Only send if WebSocket is ready
		if (wsService.isReady()) {
			wsService.sendMessage(errorMessageText, {
				error_type: error.errorType,
				code: error.code,
				line: error.line,
				column: error.column
			});
			console.log('[Strudel] Error sent to session:', session.id);
		} else {
			console.warn('[Strudel] WebSocket not ready, error not sent to agent');
		}
	}

	/**
	 * Format error message for the agent
	 */
	private formatErrorMessage(error: StrudelError): string {
		let message = `🔴 **Strudel Error**\n\n`;

		// Error type badge
		const typeLabel = {
			syntax: 'Syntax Error',
			runtime: 'Runtime Error',
			sample: 'Sample Loading Error',
			unknown: 'Error'
		}[error.errorType || 'unknown'];

		message += `**Type:** ${typeLabel}\n`;
		message += `**Message:** ${error.message}\n`;

		if (error.line !== undefined) {
			message += `**Location:** Line ${error.line}`;
			if (error.column !== undefined) {
				message += `, Column ${error.column}`;
			}
			message += '\n';
		}

		if (error.code) {
			message += `\n**Code:**\n\`\`\`javascript\n${error.code}\n\`\`\`\n`;
		}

		message += `\nPlease help me fix this error.`;

		return message;
	}

	/**
	 * Combine multiple clip codes into single Strudel pattern
	 *
	 * Strategy:
	 * - 0 clips: return empty string
	 * - 1 clip: return code as-is
	 * - 2+ clips: wrap in stack() to play simultaneously
	 *
	 * @param clipCodes Array of Strudel code strings
	 * @returns Combined code string
	 */
	combineClips(clipCodes: string[]): string {
		// Filter out empty clips
		const validCodes = clipCodes.filter((code) => code.trim().length > 0);

		if (validCodes.length === 0) {
			return '';
		}

		if (validCodes.length === 1) {
			return validCodes[0];
		}

		// Multiple clips: use stack() to play simultaneously
		// Format for readability:
		// stack(
		//   <clip1>,
		//   <clip2>,
		//   <clip3>
		// )
		const stackedCode = `stack(\n  ${validCodes.join(',\n  ')}\n)`;

		console.log('[Strudel] Combined clips:', {
			count: validCodes.length,
			code: stackedCode
		});

		return stackedCode;
	}

	/**
	 * Update player with new code
	 * Does NOT start playback - call play() separately
	 *
	 * @param combinedCode Strudel code to load
	 */
	updatePlayer(combinedCode: string): void {
		if (!this.initialized) {
			console.error('[Strudel] Not initialized. Call initialize() first.');
			return;
		}

		if (!combinedCode || combinedCode.trim().length === 0) {
			console.warn('[Strudel] Empty code, stopping player');
			this.stop();
			return;
		}

		try {
			console.log('[Strudel] Updating code:', combinedCode);

			// Store code before evaluating (for error context)
			this.currentCode = combinedCode;

			// Clear any previous error
			player.clearError();

			// Evaluate code without autostarting
			// This parses and prepares the pattern but doesn't play it
			evaluate(combinedCode, false);
		} catch (error) {
			console.error('[Strudel] Failed to update code:', error);
			throw error;
		}
	}

	/**
	 * Start playback
	 */
	play(): void {
		if (!this.initialized) {
			console.error('[Strudel] Not initialized. Call initialize() first.');
			return;
		}

		if (!this.currentCode) {
			console.warn('[Strudel] No code loaded. Call updatePlayer() first.');
			return;
		}

		try {
			console.log('[Strudel] Starting playback');

			// Clear any previous error
			player.clearError();

			// Evaluate with autostart
			evaluate(this.currentCode, true);

			// Update store
			player.setPlaying(true);
		} catch (error) {
			console.error('[Strudel] Failed to start playback:', error);
			throw error;
		}
	}

	/**
	 * Stop playback
	 */
	stop(): void {
		if (!this.initialized) {
			console.error('[Strudel] Not initialized. Call initialize() first.');
			return;
		}

		try {
			console.log('[Strudel] Stopping playback');

			// Stop all patterns
			hush();

			// Update store
			player.setPlaying(false);
		} catch (error) {
			console.error('[Strudel] Failed to stop playback:', error);
			throw error;
		}
	}

	/**
	 * Check if currently playing
	 * @returns true if playing, false otherwise
	 */
	isPlaying(): boolean {
		const state = get(player) as GlobalPlayerState;
		return state.state === 'playing';
	}

	/**
	 * Get current code
	 */
	getCurrentCode(): string {
		return this.currentCode;
	}

	/**
	 * Check if initialized
	 */
	isInitialized(): boolean {
		return this.initialized;
	}

	/**
	 * Cleanup - restore original console.error
	 */
	destroy(): void {
		if (this.originalConsoleError) {
			console.error = this.originalConsoleError;
			this.originalConsoleError = null;
		}
	}
}

/**
 * Singleton instance
 */
export const strudelService = new StrudelService();

/**
 * Export the class for testing
 */
export { StrudelService };
