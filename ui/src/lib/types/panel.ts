/**
 * Panel type definitions for the Strudel Agent UI
 * 
 * Panels are the main content containers in the carousel interface.
 * Each panel type has specific content and behavior.
 */

/**
 * Base panel types supported by the UI
 */
export type PanelType = 'clip' | 'song' | 'playlist' | 'pack';

/**
 * Base interface for all panel types
 * Contains common properties shared across all panels
 */
export interface BasePanel {
	/** Unique identifier for the panel (frontend carousel ID) */
	id: string;
	
	/** Type of panel content */
	type: PanelType;
	
	/** Display title for the panel */
	title: string;
	
	/** When the panel was created */
	createdAt: Date;
	
	/** When the panel was last modified */
	updatedAt: Date;
	
	/** Optional metadata for the panel */
	metadata?: Record<string, unknown>;
	
	// Backend integration properties
	
	/** Backend item identifier (clip_id, song_id, playlist_id, pack_id) */
	itemId: string;
	
	/** Project context for API calls */
	projectId: string;
	
	/** Associated chat session ID */
	sessionId: string;
}

/**
 * Clip panel - Contains editable Strudel code
 * Used for creating and editing individual patterns
 */
export interface ClipPanel extends BasePanel {
	type: 'clip';
	
	/** Strudel code content */
	code: string;
	
	/** Whether the clip is currently playing */
	isPlaying?: boolean;
	
	/** Track unsaved changes */
	isDirty?: boolean;
	
	/** Optional description of what the clip does */
	description?: string;
	
	/** Tags for categorization */
	tags?: string[];
}

/**
 * Reference to a clip within a song or playlist
 */
export interface ClipReference {
	/** ID of the referenced clip */
	clipId: string;
	
	/** Display name for the reference */
	name?: string;
	
	/** Order/position in the parent */
	order?: number;
}

/**
 * Song panel - Contains markdown content with clip references
 * Represents a composition made up of multiple clips
 */
export interface SongPanel extends BasePanel {
	type: 'song';
	
	/** Markdown content describing the song */
	content: string;
	
	/** Clips referenced in this song */
	clips: ClipReference[];
	
	/** Track unsaved changes */
	isDirty?: boolean;
	
	/** Optional author information */
	author?: string;
	
	/** Optional genre/style tags */
	genre?: string[];
}

/**
 * Reference to a song within a playlist
 */
export interface SongReference {
	/** ID of the referenced song */
	songId: string;
	
	/** Display name for the reference */
	name?: string;
	
	/** Order/position in the playlist */
	order?: number;
}

/**
 * Playlist panel - Contains list of songs
 * Represents a collection of songs
 */
export interface PlaylistPanel extends BasePanel {
	type: 'playlist';
	
	/** Description of the playlist */
	description?: string;
	
	/** Songs in this playlist */
	songs: SongReference[];
	
	/** Track unsaved changes */
	isDirty?: boolean;
	
	/** Optional playlist cover image URL */
	coverImage?: string;
	
	/** Optional curator/creator name */
	curator?: string;
}

/**
 * Pack panel - Read-only documentation/tutorial content
 * Contains educational or reference material
 */
export interface PackPanel extends BasePanel {
	type: 'pack';
	
	/** Markdown content for the pack */
	content: string;
	
	/** Optional table of contents */
	toc?: Array<{
		title: string;
		anchor: string;
		level: number;
	}>;
	
	/** Optional related resources */
	resources?: Array<{
		title: string;
		url: string;
		type?: 'docs' | 'video' | 'example' | 'external';
	}>;
	
	/** Version of the pack content */
	version?: string;
}

/**
 * Union type of all panel types
 * Use this for variables that can hold any panel type
 */
export type Panel = ClipPanel | SongPanel | PlaylistPanel | PackPanel;

/**
 * Type guard to check if a panel is a ClipPanel
 */
export function isClipPanel(panel: Panel): panel is ClipPanel {
	return panel.type === 'clip';
}

/**
 * Type guard to check if a panel is a SongPanel
 */
export function isSongPanel(panel: Panel): panel is SongPanel {
	return panel.type === 'song';
}

/**
 * Type guard to check if a panel is a PlaylistPanel
 */
export function isPlaylistPanel(panel: Panel): panel is PlaylistPanel {
	return panel.type === 'playlist';
}

/**
 * Type guard to check if a panel is a PackPanel
 */
export function isPackPanel(panel: Panel): panel is PackPanel {
	return panel.type === 'pack';
}

/**
 * Helper to create a new clip panel
 */
export function createClipPanel(partial: Partial<ClipPanel> & Pick<ClipPanel, 'id' | 'title' | 'itemId' | 'projectId' | 'sessionId'>): ClipPanel {
	const now = new Date();
	return {
		type: 'clip',
		code: '',
		createdAt: now,
		updatedAt: now,
		...partial
	};
}

/**
 * Helper to create a new song panel
 */
export function createSongPanel(partial: Partial<SongPanel> & Pick<SongPanel, 'id' | 'title' | 'itemId' | 'projectId' | 'sessionId'>): SongPanel {
	const now = new Date();
	return {
		type: 'song',
		content: '',
		clips: [],
		createdAt: now,
		updatedAt: now,
		...partial
	};
}

/**
 * Helper to create a new playlist panel
 */
export function createPlaylistPanel(partial: Partial<PlaylistPanel> & Pick<PlaylistPanel, 'id' | 'title' | 'itemId' | 'projectId' | 'sessionId'>): PlaylistPanel {
	const now = new Date();
	return {
		type: 'playlist',
		songs: [],
		createdAt: now,
		updatedAt: now,
		...partial
	};
}

/**
 * Helper to create a new pack panel
 */
export function createPackPanel(partial: Partial<PackPanel> & Pick<PackPanel, 'id' | 'title' | 'itemId' | 'projectId' | 'sessionId'>): PackPanel {
	const now = new Date();
	return {
		type: 'pack',
		content: '',
		createdAt: now,
		updatedAt: now,
		...partial
	};
}
