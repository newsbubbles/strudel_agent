# Phase 6: Strudel Player Integration - Detailed Implementation

**Date**: 2025-12-25  
**Purpose**: Detailed guide for integrating @strudel/web headless player  
**Related**: `ui_implementation.md`, `strudel_reference/embedding_guide.md`  
**Status**: Ready for implementation  

---

## Overview

Based on comprehensive research in `notes/interface/strudel_reference/`, we're using **`@strudel/web`** for headless Strudel integration.

**Why `@strudel/web`:**
- ✅ No editor UI (we have our own CodeMirror)
- ✅ Full programmatic control
- ✅ Lightweight bundle
- ✅ Perfect for custom carousel UI
- ✅ Direct access to all Strudel functions

**Alternative considered:** `<strudel-editor>` component (rejected - has built-in editor we don't need)

---

## Architecture Decision

### Loading Strategy: CDN vs npm

**Option A: CDN (Recommended for MVP)**
```html
<script src="https://unpkg.com/@strudel/web@latest"></script>
```

**Pros:**
- Zero build configuration
- Works immediately in SvelteKit
- Easy to get started
- Can pin version later for stability

**Cons:**
- External dependency
- Slightly larger bundle (not tree-shakeable)

**Option B: npm (Future optimization)**
```bash
npm install @strudel/core @strudel/webaudio @strudel/transpiler
```

**Pros:**
- Full control over imports
- Tree-shaking
- TypeScript support

**Cons:**
- More complex setup
- Requires understanding Strudel's module structure

**Decision: Start with CDN (Option A), migrate to npm later if needed**

---

## Implementation Files

### File 1: `src/lib/types/strudel.ts`

Complete TypeScript definitions for Strudel:

```typescript
/**
 * Strudel Web API Types
 * Based on @strudel/web CDN bundle
 */

// Global functions exposed by @strudel/web
declare global {
  /**
   * Initialize Strudel (call once on app load)
   * @param options Configuration options
   */
  function initStrudel(options?: StrudelInitOptions): Promise<void>;
  
  /**
   * Evaluate Strudel code and optionally start playback
   * @param code Strudel pattern code
   * @param autostart Whether to start playing immediately (default: true)
   */
  function evaluate(code: string, autostart?: boolean): void;
  
  /**
   * Stop all playing patterns
   */
  function hush(): void;
  
  /**
   * Load sample pack
   * @param source Sample pack URL or object
   */
  function samples(source: string | SampleMap): Promise<void>;
  
  // Pattern creation functions
  function note(pattern: string): Pattern;
  function s(pattern: string): Pattern;
  function sound(pattern: string): Pattern;
  function stack(...patterns: Pattern[]): Pattern;
  
  // More Strudel functions available...
}

export interface StrudelInitOptions {
  /**
   * Function to run before Strudel is ready (e.g., load samples)
   */
  prebake?: () => Promise<void> | void;
  
  /**
   * Whether to start scheduler automatically
   */
  autostart?: boolean;
}

export interface SampleMap {
  [packName: string]: {
    [sampleName: string]: string; // URL to sample file
  };
}

export interface Pattern {
  // Strudel pattern methods
  s(sound: string): Pattern;
  note(note: string): Pattern;
  lpf(freq: number | string): Pattern;
  fast(factor: number): Pattern;
  slow(factor: number): Pattern;
  // ... many more pattern methods
}

/**
 * Strudel player instance interface
 * (For future direct REPL access if needed)
 */
export interface StrudelREPL {
  scheduler: {
    started: boolean;
    start(): void;
    stop(): void;
  };
  evaluate(code: string, autostart?: boolean): void;
  setCode(code: string): void;
}

/**
 * Our wrapper around Strudel player
 */
export interface StrudelPlayerService {
  initialize(): Promise<void>;
  combineClips(clipCodes: string[]): string;
  updatePlayer(combinedCode: string): void;
  play(): void;
  stop(): void;
  isPlaying(): boolean;
}
```

---

### File 2: `src/lib/services/strudel.ts`

Complete service implementation:

```typescript
import type { StrudelPlayerService } from '$lib/types/strudel';
import { playerStore } from '$lib/stores/player';
import { carouselStore } from '$lib/stores/carousel';
import { get } from 'svelte/store';
import type { ClipPanel } from '$lib/types/panel';

/**
 * Strudel Player Service
 * 
 * Manages headless Strudel player integration:
 * - Initializes @strudel/web
 * - Combines multiple clip panels into single pattern
 * - Updates player with new code
 * - Controls playback (play/stop)
 */
class StrudelService implements StrudelPlayerService {
  private initialized = false;
  private currentCode = '';
  
  /**
   * Initialize Strudel player
   * Must be called once before using evaluate()
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
      
      console.log('[Strudel] Initializing...');
      
      // Initialize with sample loading
      await initStrudel({
        prebake: async () => {
          // Load default Dirt samples
          await samples('github:tidalcycles/dirt-samples');
          console.log('[Strudel] Samples loaded');
        },
        autostart: false // We control playback manually
      });
      
      this.initialized = true;
      console.log('[Strudel] Initialized successfully');
      
    } catch (error) {
      console.error('[Strudel] Initialization failed:', error);
      throw error;
    }
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
    const validCodes = clipCodes.filter(code => code.trim().length > 0);
    
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
   * Get all loaded clip panels from carousel and combine their code
   * @returns Combined code string
   */
  private getCombinedClipsFromCarousel(): string {
    const carousel = get(carouselStore);
    
    // Filter for clip panels only
    const clipPanels = carousel.panels.filter(
      panel => panel.type === 'clip'
    ) as ClipPanel[];
    
    if (clipPanels.length === 0) {
      console.warn('[Strudel] No clip panels loaded');
      return '';
    }
    
    // Extract code from each clip
    const clipCodes = clipPanels.map(panel => panel.data.code);
    
    return this.combineClips(clipCodes);
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
      
      // Evaluate code without autostarting
      // This parses and prepares the pattern but doesn't play it
      evaluate(combinedCode, false);
      
      this.currentCode = combinedCode;
      
    } catch (error) {
      console.error('[Strudel] Failed to update code:', error);
      throw error;
    }
  }
  
  /**
   * Update player with current carousel clips
   * Convenience method that combines clips and updates player
   */
  updateFromCarousel(): void {
    const combinedCode = this.getCombinedClipsFromCarousel();
    this.updatePlayer(combinedCode);
  }
  
  /**
   * Start playback
   * If code hasn't been updated, uses current carousel clips
   */
  play(): void {
    if (!this.initialized) {
      console.error('[Strudel] Not initialized. Call initialize() first.');
      return;
    }
    
    try {
      // If no code loaded, get from carousel
      if (!this.currentCode) {
        this.updateFromCarousel();
      }
      
      // If still no code, can't play
      if (!this.currentCode) {
        console.warn('[Strudel] No code to play');
        return;
      }
      
      console.log('[Strudel] Starting playback');
      
      // Evaluate with autostart
      evaluate(this.currentCode, true);
      
      // Update store
      playerStore.setPlaying(true);
      
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
      playerStore.setPlaying(false);
      
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
    // Get from store
    return get(playerStore).isPlaying;
  }
  
  /**
   * Get current code
   */
  getCurrentCode(): string {
    return this.currentCode;
  }
}

// Singleton instance
export const strudelService = new StrudelService();
```

---

### File 3: `src/lib/stores/player.ts` (Updated)

Simplified player store (Strudel handles the heavy lifting):

```typescript
import { writable } from 'svelte/store';

interface PlayerState {
  isPlaying: boolean;
  loadedClipIds: string[];
  error: string | null;
}

function createPlayerStore() {
  const { subscribe, set, update } = writable<PlayerState>({
    isPlaying: false,
    loadedClipIds: [],
    error: null
  });

  return {
    subscribe,
    
    setPlaying: (isPlaying: boolean) => {
      update(s => ({ ...s, isPlaying }));
    },
    
    setLoadedClips: (clipIds: string[]) => {
      update(s => ({ ...s, loadedClipIds: clipIds }));
    },
    
    setError: (error: string | null) => {
      update(s => ({ ...s, error }));
    },
    
    reset: () => {
      set({
        isPlaying: false,
        loadedClipIds: [],
        error: null
      });
    }
  };
}

export const playerStore = createPlayerStore();
```

---

### File 4: `src/lib/components/player/GlobalPlayer.svelte` (Updated)

Player controls component:

```svelte
<script lang="ts">
  import { Button } from '$lib/components/ui/button';
  import { playerStore } from '$lib/stores/player';
  import { carouselStore } from '$lib/stores/carousel';
  import { strudelService } from '$lib/services/strudel';
  import { onMount } from 'svelte';
  
  $: isPlaying = $playerStore.isPlaying;
  $: error = $playerStore.error;
  $: clipCount = $carouselStore.panels.filter(p => p.type === 'clip').length;
  
  let initializing = true;
  
  onMount(async () => {
    try {
      await strudelService.initialize();
      initializing = false;
    } catch (err) {
      console.error('Failed to initialize Strudel:', err);
      playerStore.setError(err.message);
      initializing = false;
    }
  });
  
  function handlePlay() {
    try {
      strudelService.play();
    } catch (err) {
      console.error('Failed to play:', err);
      playerStore.setError(err.message);
    }
  }
  
  function handleStop() {
    try {
      strudelService.stop();
    } catch (err) {
      console.error('Failed to stop:', err);
      playerStore.setError(err.message);
    }
  }
  
  function handleUpdate() {
    try {
      strudelService.updateFromCarousel();
      // If playing, restart with new code
      if (isPlaying) {
        strudelService.play();
      }
    } catch (err) {
      console.error('Failed to update:', err);
      playerStore.setError(err.message);
    }
  }
</script>

<div class="border-t bg-background p-4">
  <div class="flex items-center justify-center gap-4">
    <!-- Play/Stop Button -->
    {#if initializing}
      <Button disabled variant="outline">
        <span class="animate-pulse">Loading Strudel...</span>
      </Button>
    {:else if isPlaying}
      <Button 
        variant="destructive" 
        size="lg"
        on:click={handleStop}
        disabled={clipCount === 0}
      >
        <span class="mr-2">⏹️</span>
        Stop
      </Button>
    {:else}
      <Button 
        variant="default" 
        size="lg"
        on:click={handlePlay}
        disabled={clipCount === 0}
      >
        <span class="mr-2">▶️</span>
        Play {clipCount > 0 ? `(${clipCount} clip${clipCount > 1 ? 's' : ''})` : ''}
      </Button>
    {/if}
    
    <!-- Update Button -->
    <Button 
      variant="outline" 
      size="lg"
      on:click={handleUpdate}
      disabled={initializing || clipCount === 0}
    >
      <span class="mr-2">↻</span>
      Update
    </Button>
    
    <!-- Status Info -->
    <div class="text-sm text-muted-foreground">
      {#if clipCount === 0}
        No clips loaded
      {:else if clipCount === 1}
        1 clip ready
      {:else}
        {clipCount} clips (stacked)
      {/if}
    </div>
  </div>
  
  <!-- Error Display -->
  {#if error}
    <div class="mt-2 text-center text-sm text-destructive">
      Error: {error}
      <button 
        class="ml-2 underline"
        on:click={() => playerStore.setError(null)}
      >
        Dismiss
      </button>
    </div>
  {/if}
</div>

<style>
  /* Optional: Add animations */
  @keyframes pulse {
    0%, 100% { opacity: 1; }
    50% { opacity: 0.5; }
  }
  
  .animate-pulse {
    animation: pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite;
  }
</style>
```

---

### File 5: `src/app.html` (Updated)

Add Strudel CDN script to HTML head:

```html
<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="utf-8" />
    <link rel="icon" href="%sveltekit.assets%/favicon.png" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    
    <!-- Load Strudel before app initialization -->
    <script src="https://unpkg.com/@strudel/web@latest"></script>
    
    %sveltekit.head%
  </head>
  <body data-sveltekit-preload-data="hover">
    <div style="display: contents">%sveltekit.body%</div>
  </body>
</html>
```

---

## Usage Examples

### Example 1: Basic Playback

```typescript
import { strudelService } from '$lib/services/strudel';

// Initialize once on app load
await strudelService.initialize();

// Play single clip
strudelService.updatePlayer('note("c e g").s("piano")');
strudelService.play();

// Stop
strudelService.stop();
```

### Example 2: Multiple Clips (Stack)

```typescript
const clip1 = 's("bd sd hh sd")';
const clip2 = 'note("c e g").s("piano")';
const clip3 = 'note("c2 e2").s("sawtooth").lpf(500)';

const combined = strudelService.combineClips([clip1, clip2, clip3]);
// Result: stack(
//   s("bd sd hh sd"),
//   note("c e g").s("piano"),
//   note("c2 e2").s("sawtooth").lpf(500)
// )

strudelService.updatePlayer(combined);
strudelService.play();
```

### Example 3: Update While Playing

```typescript
// Start playing
strudelService.updatePlayer('note("c e g").s("piano")');
strudelService.play();

// Update code (will restart with new pattern)
strudelService.updatePlayer('note("<c e g b>").s("sawtooth")');
strudelService.play();
```

### Example 4: Automatic Carousel Integration

```typescript
// Just play whatever clips are loaded in carousel
strudelService.updateFromCarousel();
strudelService.play();
```

---

## Real-Time Updates from Agent

When agent updates a clip via WebSocket:

```typescript
// In WebSocket message handler
function handleClipUpdated(message: ClipUpdatedMessage) {
  // Update panel in carousel
  carouselStore.updatePanel(`clip:${message.clip_id}`, {
    data: { code: message.new_code }
  } as any);
  
  // If currently playing, update player
  if (strudelService.isPlaying()) {
    strudelService.updateFromCarousel();
    strudelService.play(); // Restart with new code
  }
}
```

---

## Error Handling

### Common Errors

**Error: `@strudel/web not loaded`**
- **Cause**: Script tag missing or not loaded yet
- **Fix**: Add `<script src="https://unpkg.com/@strudel/web@latest"></script>` to `app.html`

**Error: `samples not found`**
- **Cause**: Sample pack failed to load
- **Fix**: Check network connection, try different sample pack

**Error: `Invalid pattern syntax`**
- **Cause**: Strudel code has syntax error
- **Fix**: Validate code before calling `evaluate()`

### Error Recovery

```typescript
try {
  strudelService.play();
} catch (error) {
  console.error('Playback failed:', error);
  
  // Show error to user
  playerStore.setError(error.message);
  
  // Try to recover
  strudelService.stop();
  playerStore.setPlaying(false);
}
```

---

## Testing Strategy

### Unit Tests

```typescript
import { describe, it, expect, beforeEach } from 'vitest';
import { strudelService } from '$lib/services/strudel';

describe('StrudelService', () => {
  describe('combineClips', () => {
    it('returns empty string for no clips', () => {
      expect(strudelService.combineClips([])).toBe('');
    });
    
    it('returns single clip as-is', () => {
      const code = 'note("c e g").s("piano")';
      expect(strudelService.combineClips([code])).toBe(code);
    });
    
    it('wraps multiple clips in stack()', () => {
      const clips = [
        's("bd sd")',
        'note("c e g").s("piano")'
      ];
      const result = strudelService.combineClips(clips);
      expect(result).toContain('stack(');
      expect(result).toContain('s("bd sd")');
      expect(result).toContain('note("c e g").s("piano")');
    });
    
    it('filters out empty clips', () => {
      const clips = ['s("bd")', '', '  ', 'note("c")'];
      const result = strudelService.combineClips(clips);
      expect(result).toContain('s("bd")');
      expect(result).toContain('note("c")');
      expect(result).not.toContain('""');
    });
  });
});
```

### Integration Tests

```typescript
import { describe, it, expect, beforeAll } from 'vitest';
import { strudelService } from '$lib/services/strudel';

describe('Strudel Integration', () => {
  beforeAll(async () => {
    // Mock @strudel/web globals
    global.initStrudel = vi.fn().mockResolvedValue(undefined);
    global.evaluate = vi.fn();
    global.hush = vi.fn();
    global.samples = vi.fn().mockResolvedValue(undefined);
    
    await strudelService.initialize();
  });
  
  it('initializes successfully', async () => {
    expect(global.initStrudel).toHaveBeenCalled();
  });
  
  it('updates player with code', () => {
    const code = 'note("c e g").s("piano")';
    strudelService.updatePlayer(code);
    expect(global.evaluate).toHaveBeenCalledWith(code, false);
  });
  
  it('starts playback', () => {
    const code = 'note("c e g").s("piano")';
    strudelService.updatePlayer(code);
    strudelService.play();
    expect(global.evaluate).toHaveBeenCalledWith(code, true);
  });
  
  it('stops playback', () => {
    strudelService.stop();
    expect(global.hush).toHaveBeenCalled();
  });
});
```

---

## Performance Considerations

### Sample Loading

**Problem**: Loading samples can take 5-10 seconds

**Solution**: Load in background during app initialization

```typescript
// In +layout.svelte or app initialization
onMount(async () => {
  // Start loading immediately (non-blocking)
  strudelService.initialize().catch(err => {
    console.error('Failed to initialize Strudel:', err);
  });
});
```

### Code Evaluation

**Problem**: Complex patterns can cause audio glitches when evaluated

**Solution**: Use `evaluate(code, false)` to prepare pattern without starting, then `play()` separately

```typescript
// Prepare pattern (doesn't start audio)
strudelService.updatePlayer(complexCode);

// Start playback when ready
strudelService.play();
```

### Memory Management

**Problem**: Strudel keeps patterns in memory

**Solution**: Call `hush()` when stopping to clear patterns

```typescript
strudelService.stop(); // Already calls hush() internally
```

---

## Future Enhancements

### 1. Pattern Validation

Validate Strudel code before playing:

```typescript
function validatePattern(code: string): { valid: boolean; error?: string } {
  try {
    evaluate(code, false);
    return { valid: true };
  } catch (err) {
    return { valid: false, error: err.message };
  }
}
```

### 2. Recording/Export

Record Strudel output to audio file (requires additional library):

```typescript
// Future: Use Web Audio API to record output
// See: https://developer.mozilla.org/en-US/docs/Web/API/MediaRecorder
```

### 3. MIDI Output

Send Strudel patterns to external MIDI devices:

```typescript
// Strudel supports MIDI output
const midiPattern = 'note("c e g").midi("IAC Driver Bus 1")';
```

### 4. Pattern Library

Store and recall common patterns:

```typescript
const patternLibrary = {
  'basic-drums': 's("bd sd hh sd")',
  'piano-chords': 'note("<c e g b>").s("piano")',
  // ...
};
```

---

## Troubleshooting Guide

### Player Won't Start

1. Check browser console for errors
2. Verify `@strudel/web` script loaded (check `window.initStrudel`)
3. Ensure `initialize()` was called and completed
4. Check if code is valid Strudel syntax

### Audio Glitches

1. Reduce pattern complexity
2. Use `slow()` to reduce event rate
3. Check CPU usage (Strudel is CPU-intensive)

### Samples Won't Load

1. Check network connection
2. Try different sample pack
3. Use custom samples with direct URLs

### Multiple Clips Not Stacking

1. Verify `combineClips()` output
2. Check `stack()` syntax
3. Ensure all clips have valid code

---

## Resources

- **Strudel Docs**: https://strudel.cc/learn
- **Pattern Reference**: https://strudel.cc/learn/patterns
- **@strudel/web CDN**: https://unpkg.com/@strudel/web@latest
- **Sample Packs**: https://github.com/tidalcycles/Dirt-Samples
- **Research Notes**: `notes/interface/strudel_reference/`

---

## Summary

✅ **Use `@strudel/web` via CDN**  
✅ **Initialize once on app load**  
✅ **Combine clips with `stack()`**  
✅ **Control playback with service layer**  
✅ **Handle errors gracefully**  
✅ **Load samples in background**  

**Ready to implement!** 🎵
