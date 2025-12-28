/**
 * API Service - Type-safe HTTP client for Strudel Agent backend
 * 
 * Features:
 * - Type-safe REST API calls
 * - Error handling
 * - Fetch clips, songs, playlists, packs
 * - Message history with pagination
 * - Session management
 */

import type { Message } from '$lib/types/message';
import type { Session, SessionStatus, SessionType } from '$lib/types/session';

/**
 * API configuration
 */
interface APIConfig {
	/** Base API URL */
	baseUrl: string;

	/** Request timeout (ms) */
	timeout: number;
}

/**
 * Default configuration
 */
const DEFAULT_CONFIG: APIConfig = {
	baseUrl: '', // Will be set based on window.location
	timeout: 30000 // 30 seconds
};

/**
 * API error class
 */
export class APIError extends Error {
	constructor(
		public status: number,
		public statusText: string,
		message: string
	) {
		super(message);
		this.name = 'APIError';
	}
}

/**
 * Project data from API
 */
export interface ProjectData {
	project_id: string;
	name: string;
	description?: string;
	clip_count?: number;
	song_count?: number;
	playlist_count?: number;
	created_at?: string;
	updated_at?: string;
	metadata?: Record<string, any>;
}

/**
 * Session creation request
 */
export interface CreateSessionRequest {
	agent_name: string;
	model_name: string;
	provider: string;
	session_type: SessionType;
	item_id: string;
	project_id: string;
	session_name?: string;
}

/**
 * Session response from API
 */
export interface SessionResponse {
	session_id: string;
	agent_name: string;
	model_name: string;
	provider: string;
	session_type: SessionType;
	item_id: string;
	project_id: string;
	created_at: string;
	last_activity: string;
	status: SessionStatus;
	message_count: number;
	session_name?: string;
}

/**
 * Message history response
 */
export interface MessageHistoryResponse {
	messages: Array<{
		role: 'user' | 'assistant';
		content: string;
		timestamp: string;
		message_index: number;
	}>;
}

/**
 * Clip request/response
 */
export interface ClipData {
	id?: number;
	clip_id: string;
	project_id: string;
	name: string;
	code: string;
	created_at?: string;
	updated_at?: string;
	metadata?: Record<string, any>;
}

/**
 * Song request/response
 */
export interface SongData {
	id?: number;
	song_id: string;
	project_id: string;
	name: string;
	clip_ids: string[];
	created_at?: string;
	updated_at?: string;
	metadata?: Record<string, any>;
}

/**
 * Playlist request/response
 */
export interface PlaylistData {
	id?: number;
	playlist_id: string;
	project_id: string;
	name: string;
	song_ids: string[];
	created_at?: string;
	updated_at?: string;
	metadata?: Record<string, any>;
}

/**
 * API Service Class
 */
class APIService {
	/** Service configuration */
	private config: APIConfig;

	constructor(config: Partial<APIConfig> = {}) {
		this.config = { ...DEFAULT_CONFIG, ...config };

		// Set base URL from window.location if not provided
		if (!this.config.baseUrl && typeof window !== 'undefined') {
			const protocol = window.location.protocol;
			const hostname = window.location.hostname;
			this.config.baseUrl = `${protocol}//${hostname}:8034/api`;
		}
	}

	/**
	 * Generic fetch method with error handling
	 */
	private async fetch<T>(
		path: string,
		options: RequestInit = {}
	): Promise<T> {
		const url = `${this.config.baseUrl}${path}`;

		// Create abort controller for timeout
		const controller = new AbortController();
		const timeoutId = setTimeout(() => controller.abort(), this.config.timeout);

		try {
			const response = await fetch(url, {
				...options,
				signal: controller.signal,
				headers: {
					'Content-Type': 'application/json',
					...options.headers
				}
			});

			clearTimeout(timeoutId);

			if (!response.ok) {
				const errorText = await response.text();
				let errorMessage = `HTTP ${response.status}: ${response.statusText}`;

				try {
					const errorJson = JSON.parse(errorText);
					if (errorJson.detail) {
						errorMessage = errorJson.detail;
					}
				} catch {
					// Use default error message
				}

				throw new APIError(response.status, response.statusText, errorMessage);
			}

			// Handle empty responses
			const text = await response.text();
			if (!text) {
				return {} as T;
			}

			return JSON.parse(text) as T;
		} catch (error) {
			clearTimeout(timeoutId);

			if (error instanceof APIError) {
				throw error;
			}

			if (error instanceof Error) {
				if (error.name === 'AbortError') {
					throw new APIError(0, 'Timeout', 'Request timeout');
				}
				throw new APIError(0, 'Network Error', error.message);
			}

			throw new APIError(0, 'Unknown Error', 'An unknown error occurred');
		}
	}

	// ==================== Projects ====================

	/**
	 * List all projects
	 */
	async listProjects(): Promise<ProjectData[]> {
		const response = await this.fetch<{ projects: ProjectData[]; total: number }>('/projects');
		return response.projects;
	}

	/**
	 * Get a specific project
	 */
	async getProject(projectId: string): Promise<ProjectData> {
		return this.fetch<ProjectData>(`/projects/${projectId}`);
	}

	// ==================== Sessions ====================

	/**
	 * Create a new session
	 */
	async createSession(request: CreateSessionRequest): Promise<SessionResponse> {
		return this.fetch<SessionResponse>('/sessions', {
			method: 'POST',
			body: JSON.stringify(request)
		});
	}

	/**
	 * List sessions with optional filters
	 */
	async listSessions(filters?: {
		status?: SessionStatus;
		project_id?: string;
	}): Promise<SessionResponse[]> {
		const params = new URLSearchParams();

		if (filters?.status) {
			params.append('status', filters.status);
		}
		if (filters?.project_id) {
			params.append('project_id', filters.project_id);
		}

		const query = params.toString();
		const path = query ? `/sessions?${query}` : '/sessions';

		return this.fetch<SessionResponse[]>(path);
	}

	/**
	 * Delete a session
	 */
	async deleteSession(sessionId: string): Promise<{ success: boolean }> {
		return this.fetch<{ success: boolean }>(`/sessions/${sessionId}`, {
			method: 'DELETE'
		});
	}

	/**
	 * Update session name
	 */
	async updateSessionName(
		sessionId: string,
		name: string | null
	): Promise<void> {
		return this.fetch<void>(`/sessions/${sessionId}/name`, {
			method: 'PATCH',
			body: JSON.stringify({ name })
		});
	}

	// ==================== Messages ====================

	/**
	 * Get paginated message history for a session
	 */
	async getMessages(
		sessionId: string,
		options?: {
			page_size?: number;
			before_index?: number;
		}
	): Promise<MessageHistoryResponse> {
		const params = new URLSearchParams();

		if (options?.page_size) {
			params.append('page_size', options.page_size.toString());
		}
		if (options?.before_index !== undefined) {
			params.append('before_index', options.before_index.toString());
		}

		const query = params.toString();
		const path = query ? `/messages/${sessionId}?${query}` : `/messages/${sessionId}`;

		return this.fetch<MessageHistoryResponse>(path);
	}

	// ==================== Clips ====================

	/**
	 * Create a new clip
	 */
	async createClip(clip: Omit<ClipData, 'id' | 'created_at' | 'updated_at'>): Promise<ClipData> {
		return this.fetch<ClipData>('/clips', {
			method: 'POST',
			body: JSON.stringify(clip)
		});
	}

	/**
	 * Get a specific clip
	 */
	async getClip(projectId: string, clipId: string): Promise<ClipData> {
		return this.fetch<ClipData>(`/clips/${projectId}/${clipId}`);
	}

	/**
	 * List all clips in a project
	 */
	async listClips(projectId: string): Promise<ClipData[]> {
		const response = await this.fetch<{ clips: ClipData[]; total: number; project_id: string }>(
			`/clips/${projectId}`
		);
		return response.clips;
	}

	/**
	 * Update a clip
	 */
	async updateClip(
		projectId: string,
		clipId: string,
		updates: Partial<Pick<ClipData, 'name' | 'code' | 'metadata'>>
	): Promise<ClipData> {
		return this.fetch<ClipData>(`/clips/${projectId}/${clipId}`, {
			method: 'PUT',
			body: JSON.stringify(updates)
		});
	}

	/**
	 * Delete a clip
	 */
	async deleteClip(projectId: string, clipId: string): Promise<{ success: boolean }> {
		return this.fetch<{ success: boolean }>(`/clips/${projectId}/${clipId}`, {
			method: 'DELETE'
		});
	}

	// ==================== Songs ====================

	/**
	 * Create a new song
	 */
	async createSong(song: Omit<SongData, 'id' | 'created_at' | 'updated_at'>): Promise<SongData> {
		return this.fetch<SongData>('/songs', {
			method: 'POST',
			body: JSON.stringify(song)
		});
	}

	/**
	 * Get a specific song
	 */
	async getSong(projectId: string, songId: string): Promise<SongData> {
		return this.fetch<SongData>(`/songs/${projectId}/${songId}`);
	}

	/**
	 * List all songs in a project
	 */
	async listSongs(projectId: string): Promise<SongData[]> {
		const response = await this.fetch<{ songs: SongData[]; total: number; project_id: string }>(
			`/songs/${projectId}`
		);
		return response.songs;
	}

	/**
	 * Update a song
	 */
	async updateSong(
		projectId: string,
		songId: string,
		updates: Partial<Pick<SongData, 'name' | 'clip_ids' | 'metadata'>>
	): Promise<SongData> {
		return this.fetch<SongData>(`/songs/${projectId}/${songId}`, {
			method: 'PUT',
			body: JSON.stringify(updates)
		});
	}

	/**
	 * Delete a song
	 */
	async deleteSong(projectId: string, songId: string): Promise<{ success: boolean }> {
		return this.fetch<{ success: boolean }>(`/songs/${projectId}/${songId}`, {
			method: 'DELETE'
		});
	}

	// ==================== Playlists ====================

	/**
	 * Create a new playlist
	 */
	async createPlaylist(
		playlist: Omit<PlaylistData, 'id' | 'created_at' | 'updated_at'>
	): Promise<PlaylistData> {
		return this.fetch<PlaylistData>('/playlists', {
			method: 'POST',
			body: JSON.stringify(playlist)
		});
	}

	/**
	 * Get a specific playlist
	 */
	async getPlaylist(projectId: string, playlistId: string): Promise<PlaylistData> {
		return this.fetch<PlaylistData>(`/playlists/${projectId}/${playlistId}`);
	}

	/**
	 * List all playlists in a project
	 */
	async listPlaylists(projectId: string): Promise<PlaylistData[]> {
		const response = await this.fetch<{ playlists: PlaylistData[]; total: number; project_id: string }>(
			`/playlists/${projectId}`
		);
		return response.playlists;
	}

	/**
	 * Update a playlist
	 */
	async updatePlaylist(
		projectId: string,
		playlistId: string,
		updates: Partial<Pick<PlaylistData, 'name' | 'song_ids' | 'metadata'>>
	): Promise<PlaylistData> {
		return this.fetch<PlaylistData>(`/playlists/${projectId}/${playlistId}`, {
			method: 'PUT',
			body: JSON.stringify(updates)
		});
	}

	/**
	 * Delete a playlist
	 */
	async deletePlaylist(projectId: string, playlistId: string): Promise<{ success: boolean }> {
		return this.fetch<{ success: boolean }>(`/playlists/${projectId}/${playlistId}`, {
			method: 'DELETE'
		});
	}

	// ==================== Health Check ====================

	/**
	 * Check API health
	 */
	async healthCheck(): Promise<{ status: string }> {
		// Health check is at root, not /api
		const baseUrl = this.config.baseUrl.replace('/api', '');
		const response = await fetch(`${baseUrl}/health`);

		if (!response.ok) {
			throw new APIError(response.status, response.statusText, 'Health check failed');
		}

		return response.json();
	}
}

/**
 * Singleton API service instance
 */
export const apiService = new APIService();

/**
 * Export the class for testing
 */
export { APIService };
