# Strudel Visualizers Reference

**Research Date**: 2025-12-23  
**Source**: https://strudel.cc/learn/visual-feedback/

---

## Overview

Strudel provides several visualization functions that give visual feedback for your patterns. These can be chained to the end of patterns, similar to effects. Visualizers help you understand your patterns and create engaging audiovisual live coding performances.

---

## Global vs Inline Visuals

All visualizers come in **two variants**:

| Variant | Syntax | Behavior |
|---------|--------|----------|
| **Global** | `.visualizer()` | Renders to the background of the page |
| **Inline** | `._visualizer()` | Renders inside the code, allowing for multiple visuals |

### Example

```javascript
// Global visual (background)
note("c a f e").color("white").punchcard()

// Inline visual (in code)
note("c a f e").color("white")._punchcard()
```

---

## Mini Notation Highlighting

### What It Does

Built-in feature that highlights active parts of mini notation when using double quotes or backticks.

### Basic Usage

```javascript
n("<0 2 1 3 2>*8")
.scale("<A1 D2>/4:minor:pentatonic")
.s("supersaw").lpf(300).lpenv("<4 3 2>*4")
```

### With Custom Colors

You can change the highlight color, even pattern it:

```javascript
n("<0 2 1 3 2>*8")
.scale("<A1 D2>/4:minor:pentatonic")
.s("supersaw").lpf(300).lpenv("<4 3 2>*4")
.color("cyan magenta")
```

---

## Punchcard / Pianoroll

### What They Do

Render pianoroll-style visualizations showing notes over time.

**Key Difference**:
- **`pianoroll`**: Renders the pattern directly without considering subsequent transformations
- **`punchcard`**: Takes transformations into account that occur after the visualizer

### Syntax

```javascript
// Global
note("c a f e").punchcard()

// Inline
note("c a f e")._pianoroll()
```

### Options

Both functions accept the same options object:

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `cycles` | integer | 4 | Number of cycles to display |
| `playhead` | number | 0.5 | Location of active notes (0-1) |
| `vertical` | boolean | 0 | Display roll vertically |
| `labels` | boolean | 0 | Show labels on notes |
| `flipTime` | boolean | 0 | Reverse direction of roll |
| `flipValues` | boolean | 0 | Reverse note location on value axis |
| `overscan` | number | 1 | Lookup cycles outside window |
| `hideNegative` | boolean | 0 | Hide notes with negative time |
| `smear` | boolean | 0 | Notes leave solid trace |
| `fold` | boolean | 0 | Notes take full value axis width |
| `active` | string | #FFCA28 | Color of active notes |
| `inactive` | string | #7491D2 | Color of inactive notes |
| `background` | string | transparent | Background color |
| `playheadColor` | string | white | Color of playhead line |
| `fill` | boolean | 0 | Notes filled with color |
| `fillActive` | boolean | 0 | Active notes filled |
| `stroke` | boolean | 0 | Notes with colored borders |
| `strokeActive` | boolean | 0 | Active notes with borders |
| `hideInactive` | boolean | 0 | Only show active notes |
| `colorizeInactive` | boolean | 1 | Use note color for inactive notes |
| `fontFamily` | string | 'monospace' | Font for labels |
| `minMidi` | integer | 10 | Minimum note value to display |
| `maxMidi` | integer | 90 | Maximum note value to display |
| `autorange` | boolean | 0 | Auto-calculate min/max MIDI |

### Examples

```javascript
// Basic pianoroll
note("c2 a2 eb2")
.euclid(5,8)
.s('sawtooth')
.lpenv(4).lpf(300)
.pianoroll()
```

```javascript
// Pianoroll with labels
note("c2 a2 eb2")
.euclid(5,8)
.s('sawtooth')
.lpenv(4).lpf(300)
.pianoroll({ labels: 1 })
```

```javascript
// Vertical punchcard with custom colors
note("c a f e")
.color("cyan")
._punchcard({ 
  vertical: 1, 
  active: "#00FFFF",
  inactive: "#004444"
})
```

---

## Scope (Oscilloscope)

### What It Does

Renders an oscilloscope showing the time domain of the audio signal. Essential for visualizing waveforms.

### Syntax

```javascript
// Global
s("sawtooth").scope()

// Inline
s("sawtooth")._scope()
```

### Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `align` | boolean | 1 | Align to first zero crossing |
| `color` | string | white | Line color |
| `thickness` | number | 3 | Line thickness |
| `scale` | number | 0.25 | Y-axis scale |
| `pos` | number | 0 | Y-position (0=top, 1=bottom) |
| `trigger` | number | 0 | Amplitude value for alignment |

### Examples

```javascript
// Basic scope
s("sawtooth")._scope()
```

```javascript
// Scope with custom color and thickness
note("c2 eb2 g2")
.s("square")
.lpf(800)
._scope({ color: "cyan", thickness: 5 })
```

```javascript
// Multiple scopes with different positions
stack(
  note("c2").s("sine")._scope({ pos: 0, color: "red" }),
  note("g2").s("sawtooth")._scope({ pos: 0.5, color: "blue" })
)
```

---

## Spiral

### What It Does

Displays a spiral visualization of your pattern, showing cyclical structure.

### Syntax

```javascript
// Global
note("c2 a2 eb2").spiral()

// Inline
note("c2 a2 eb2")._spiral()
```

### Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `stretch` | number | - | Controls rotations per cycle ratio |
| `size` | number | - | Diameter of the spiral |
| `thickness` | number | - | Line thickness |
| `cap` | string | "butt" | Style of line ends: butt, round, square |
| `inset` | string | 3 | Rotations before spiral starts |
| `playheadColor` | string | white | Color of playhead |
| `playheadLength` | number | 0.02 | Length of playhead in rotations |
| `playheadThickness` | number | thickness | Thickness of playhead |
| `padding` | number | - | Space around spiral |
| `steady` | number | - | Steadyness of spiral vs playhead |
| `activeColor` | number | theme foreground | Color of active segment |
| `inactiveColor` | number | theme gutter | Color of inactive segments |
| `colorizeInactive` | boolean | 0 | Colorize inactive segments |
| `fade` | boolean | 1 | Fade past and future |
| `logSpiral` | boolean | 0 | Use logarithmic spiral |

### Example

```javascript
note("c2 a2 eb2")
.euclid(5,8)
.s('sawtooth')
.lpenv(4).lpf(300)
._spiral({ steady: .96 })
```

---

## Pitchwheel

### What It Does

Renders a pitch circle to visualize frequencies within one octave. Shows harmonic relationships.

### Syntax

```javascript
// Global
n("0 .. 12").scale("C:chromatic").pitchwheel()

// Inline
n("0 .. 12").scale("C:chromatic")._pitchwheel()
```

### Options

| Option | Type | Description |
|--------|------|-------------|
| `hapcircles` | number | - |
| `circle` | number | - |
| `edo` | number | - |
| `root` | string | - |
| `thickness` | number | - |
| `hapRadius` | number | - |
| `mode` | string | - |
| `margin` | number | - |

### Example

```javascript
n("0 .. 12").scale("C:chromatic")
.s("sawtooth")
.lpf(500)
._pitchwheel()
```

---

## Spectrum

### What It Does

Renders a spectrum analyzer for the incoming audio signal. Shows frequency content over time.

### Syntax

```javascript
// Global
n("<0 4 <2 3> 1>*3").spectrum()

// Inline
n("<0 4 <2 3> 1>*3")._spectrum()
```

### Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `thickness` | integer | 3 | Line thickness in px |
| `speed` | integer | 1 | Scroll speed |
| `min` | integer | -80 | Minimum dB |
| `max` | integer | 0 | Maximum dB |

### Example

```javascript
n("<0 4 <2 3> 1>*3")
.off(1/8, add(n(5)))
.off(1/5, add(n(7)))
.scale("d3:minor:pentatonic")
.s('sine')
.dec(.3).room(.5)
._spectrum()
```

---

## markcss

### What It Does

Overrides the CSS of highlighted events in mini-notation.

**Note**: Use single quotes for CSS properties.

### Syntax

```javascript
note("c a f e").markcss('text-decoration:underline')
```

### Examples

```javascript
// Underline highlighted notes
note("c a f e")
.markcss('text-decoration:underline')
```

```javascript
// Custom background color
note("c a f e")
.markcss('background-color:rgba(255,0,0,0.3)')
```

---

## Quick Reference Table

| Visualizer | Purpose | Best For |
|------------|---------|----------|
| `punchcard` / `pianoroll` | Note grid over time | Melodies, chords, rhythmic patterns |
| `scope` | Waveform oscilloscope | Synth timbres, audio signal shape |
| `spiral` | Cyclical pattern view | Understanding pattern structure |
| `pitchwheel` | Pitch circle | Harmonic relationships, scales |
| `spectrum` | Frequency analyzer | Frequency content, mixing |
| `markcss` | Custom CSS styling | Highlighting specific events |

---

## Usage Tips

### 1. Chain at the End

Visuralizers are typically chained at the end of patterns, similar to effects:

```javascript
note("c e g")
.s("piano")
.room(0.5)
._pianoroll() // Visualizer at the end
```

### 2. Use Inline for Multiple Visuals

When you want multiple visualizers, use the inline variants (`_visualizer()`):

```javascript
stack(
  note("c2 eb2").s("sine")._scope({ color: "red" }),
  note("g3 bb3").s("sawtooth")._pianoroll({ vertical: 1 })
)
```

### 3. Use Global for Background

Use global variants (`.visualizer()`) for a single background visualization:

```javascript
note("c a f e")
.s("piano")
.pianoroll() // Global - fills background
```

### 4. Combine with .color()

Many visualizers respond to the `.color()` function:

```javascript
note("c e g")
.color("cyan")
._punchcard()
```

### 5. Performance Considerations

- Inline visualizers use more CPU than global ones
- Limit the number of simultaneous visualizers for performance
- Use `cycles` option to limit pianoroll/punchcard rendering

---

## Common Use Cases

### Debugging Rhythms

Use punchcard to see if your rhythm is what you expect:

```javascript
s("bd*4, hh*8, ~ sd")
._punchcard({ labels: 1 })
```

### Visualizing Synth Waveforms

Use scope to see the actual waveform:

```javascript
note("c2")
.s("<sine sawtooth square triangle>")
._scope({ thickness: 5 })
```

### Live Performance Visuals

Combine multiple visualizers for engaging visuals:

```javascript
stack(
  note("c2 eb2 g2")
    .s("sawtooth")
    .lpf(800)
    ._scope({ pos: 0, color: "cyan" }),
  note("c4 eb4 g4 bb4")
    .s("sine")
    ._pianoroll({ vertical: 1, labels: 1 })
)
```

### Understanding Frequency Content

Use spectrum to see what frequencies are present:

```javascript
note("c2 eb2 g2 bb2")
.s("sawtooth")
.lpf("<200 800 1600>")
._spectrum({ thickness: 5 })
```

---

## Example Combinations

### Techno with Scope and Punchcard

```javascript
stack(
  s("bd*4").gain(0.9)._scope({ color: "red", pos: 0 }),
  s("hh*8").lpf(800).gain(0.4),
  note("c2 ~ c2 ~").s("sawtooth").lpf(400)
)._punchcard({ labels: 1 })
```

### Ambient with Spiral

```javascript
note("<c3 eb3 f3 g3>")
.s("sawtooth")
.lpf(600)
.room(0.9)
.slow(4)
._spiral({ steady: 0.95, fade: 1 })
```

### Melody with Pianoroll and Spectrum

```javascript
note("c4 e4 g4 b4 c5")
.s("sine")
.delay(0.25)
._pianoroll({ labels: 1, vertical: 0 })
._spectrum({ thickness: 3 })
```

---

## Summary

- **Visualizers are chained** like effects at the end of patterns
- **Global variants** (`.visualizer()`) render to background
- **Inline variants** (`._visualizer()`) render in code
- **Options customize** appearance and behavior
- **Multiple visualizers** can be used together with inline variants
- **Essential for live coding** - helps understand patterns and creates engaging performances

### Most Commonly Used

1. **`._scope()`** - See waveforms, great for synths
2. **`._punchcard()`** - See note patterns over time
3. **`._pianoroll()`** - Same as punchcard but different rendering
4. **`._spectrum()`** - See frequency content

Experiment with different visualizers to find what works best for your performance style!
