/**
 * Stores barrel export
 *
 * Re-exports all stores for convenient importing.
 * Usage: import { carousel, currentPanel, sessions } from '$lib/stores';
 */

// Carousel store
export { carousel, currentPanel, panelCount, currentIndex, panels } from './carousel';

// Session store
export { sessions, sessionCount, activeSessions, errorSessions } from './session';

// WebSocket store
export {
	websocket,
	connectionState,
	isConnected,
	isConnecting,
	hasError,
	errorMessage,
	queuedMessageCount,
	reconnectAttempts
} from './websocket';

// History store
export { history, totalMessageCount, sessionWithMessagesCount } from './history';

// Player store
export {
	player,
	isStrudelInitialized,
	playerState,
	isPlaying,
	isStopped,
	isLoading,
	hasPlayerError,
	playerError,
	volume,
	cps,
	loadedClips,
	loadedClipCount
} from './player';

// Recent items store
export {
	recent,
	recentCount,
	recentClips,
	recentSongs,
	recentPlaylists,
	recentPacks,
	recentToday,
	recentThisWeek
} from './recent';

export type { RecentItem } from './recent';
