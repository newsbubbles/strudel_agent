# Strudel Sample Packs Index

**Research Date**: 2025-12-22  
**Total Packs Catalogued**: 30+  
**Primary Source**: https://github.com/terryds/awesome-strudel

## Overview

This directory contains documentation for all known Strudel-compatible sample packs available on GitHub. Each pack is documented with:
- GitHub URL and loading syntax
- Description and creator info
- Sound categories/types included
- Tags for search and filtering
- Usage examples
- License information (where available)

## Quick Reference

### Most Important Packs

1. **[Dirt-Samples](01_dirt_samples.md)** - `github:tidalcycles/Dirt-Samples`
   - The canonical TidalCycles sample library
   - 100+ sample categories
   - Drums, breaks, synths, effects, field recordings

2. **[Garden](02_garden.md)** - `github:mot4i/garden`
   - Curated DIY pack with analog warmth
   - Drums, percussion, effects
   - Re-amped through analog gear

3. **[Clean-Breaks](03_clean_breaks.md)** - `github:yaxu/clean-breaks`
   - Drum break samples
   - Properly sourced and licensed

## All Sample Packs

### Official/Well-Known Packs

| Pack Name | GitHub URL | Type | Tags |
|-----------|-----------|------|------|
| Dirt-Samples | `github:tidalcycles/Dirt-Samples` | Comprehensive | drums, breaks, synths, fx, classic |
| Clean-Samples | `github:tidalcycles/Clean-Samples` | Comprehensive | drums, licensed, clean |
| Garden | `github:mot4i/garden` | Drums/Perc | analog, warm, curated |
| Clean-Breaks | `github:yaxu/clean-breaks` | Breaks | drums, breaks, licensed |

### Community Packs

| Pack Name | GitHub URL | Creator | Notes |
|-----------|-----------|---------|-------|
| algorave-dave/samples | `github:algorave-dave/samples` | algorave-dave | Algorave performance samples |
| AuditeMarlow/samples | `github:AuditeMarlow/samples` | AuditeMarlow | Community samples |
| ms-teams-sounds | `github:AustinOliverHaskell/ms-teams-sounds-strudel` | AustinOliverHaskell | Microsoft Teams sounds |
| RepositorioDesonidos | `github:bruveping/RepositorioDesonidosParaExperimentar02` | bruveping | Experimental sounds |
| Dough-Amen | `github:Bubobubobubobubo/Dough-Amen` | Bubobubobubobubo | Amen break variations |
| Dough-Juj | `github:Bubobubobubobubo/Dough-Juj` | Bubobubobubobubo | Custom samples |
| crate | `github:eddyflux/crate` | eddyflux | Sample crate |
| EloMorelo/samples | `github:EloMorelo/samples` | EloMorelo | Community samples |
| strudelSamples | `github:emrexdeger/strudelSamples` | emrexdeger | Community samples |
| fjpolo-Strudel | `github:fjpolo/fjpolo-Strudel` | fjpolo | Personal collection |
| polifonia-samples | `github:fstiffo/polifonia-samples` | fstiffo | Polyphonic samples |
| cavlp-25p | `github:hvillase/cavlp-25p` | hvillase | Custom samples |
| k09/samples | `github:k09/samples` | k09 | Community samples |
| kaiye10/strudelSamples | `github:kaiye10/strudelSamples` | kaiye10 | Community samples |
| msl-strudel-samples | `github:mysinglelise/msl-strudel-samples` | mysinglelise | Custom samples |
| Nikeryms/Samples | `github:Nikeryms/Samples` | Nikeryms | Community samples |
| departure | `github:prismograph/departure` | prismograph | Custom pack |
| quantum-music | `github:QuantumVillage/quantum-music` | QuantumVillage | Quantum/experimental |
| RikyBac15/samples | `github:RikyBac15/samples` | RikyBac15 | Community samples |
| capoeira_strudel | `github:salsicha/capoeira_strudel` | salsicha | Capoeira music samples |
| rochormatic | `github:sonidosingapura/rochormatic` | sonidosingapura | Custom samples |
| terrorhank/samples | `github:terrorhank/samples` | terrorhank | Community samples |
| tesspilot/samples | `github:tesspilot/samples` | tesspilot | Community samples |
| TodePond/samples | `github:TodePond/samples` | TodePond | Community samples |
| mirus | `github:TristanCacqueray/mirus` | TristanCacqueray | Custom pack |
| vasilymilovidov/samples | `github:vasilymilovidov/samples` | vasilymilovidov | Beats, percussion, IR |
| graffathon25-demo | `github:Veikkosuhonen/graffathon25-demo` | Veikkosuhonen | Demo samples |
| livecoding-samples | `github:wyan/livecoding-samples` | wyan | Live coding optimized |

## Loading Sample Packs

### Basic Loading

```javascript
// Load from GitHub (shorthand)
samples('github:username/repository')

// Load from GitHub (full URL)
samples('https://raw.githubusercontent.com/username/repository/master/')

// Load specific strudel.json file
samples('https://example.com/path/to/strudel.json')
```

### Examples

```javascript
// Load Dirt-Samples (default in Strudel)
samples('github:tidalcycles/Dirt-Samples')

// Load Garden pack
samples('github:mot4i/garden')

// Load Clean-Breaks
samples('github:yaxu/clean-breaks')

// Use samples from loaded pack
s("garden_bd garden_sd garden_hh*4")
```

## Sample Pack Format

Strudel sample packs typically use a `strudel.json` file:

```json
{
  "sounds": {
    "kick": ["kick1.wav", "kick2.wav"],
    "snare": ["snare1.wav", "snare2.wav"],
    "hats": ["hh1.wav", "hh2.wav", "hh3.wav"]
  }
}
```

Or:

```json
{
  "samples": {
    "drums": ["bd.wav", "sd.wav"],
    "bass": ["bass1.wav", "bass2.wav"]
  }
}
```

## Tools & Resources

### Sample Pack Explorer
- **open-strudel-samples**: https://therebelrobot.github.io/open-strudel-samples/
  - React app for browsing and previewing GitHub sample packs
  - Searches for `strudel.json` files across GitHub
  - Allows testing samples before loading

### Sample Pack Registry
- **strudel-samples**: https://strudel-samples.alternet.site
  - Find and preview samples from known packs
  - Community-contributed sample discovery

## Tags Reference

Use these tags to filter and search sample packs:

### By Type
- `drums` - Drum samples (kicks, snares, hats, etc.)
- `breaks` - Drum breaks and loops
- `synths` - Synthesized sounds
- `bass` - Bass sounds
- `fx` - Sound effects
- `percussion` - Percussion instruments
- `melodic` - Melodic/pitched instruments
- `vocals` - Vocal samples
- `field-recording` - Field recordings/ambient

### By Character
- `analog` - Analog-processed sounds
- `digital` - Digital/clean sounds
- `lo-fi` - Lo-fi/degraded quality
- `vintage` - Vintage/retro sounds
- `modern` - Modern/contemporary sounds

### By Genre
- `techno` - Techno-oriented samples
- `house` - House music samples
- `hip-hop` - Hip-hop samples
- `ambient` - Ambient sounds
- `experimental` - Experimental/avant-garde
- `algorave` - Algorave/live coding specific

### By Quality
- `curated` - Hand-picked/quality-controlled
- `comprehensive` - Large, diverse collection
- `licensed` - Clear licensing info
- `clean` - Properly sourced and documented

## Contributing

To add a new sample pack to this index:

1. Create a new markdown file: `notes/known_packs/XX_packname.md`
2. Follow the template structure (see existing packs)
3. Update this index with pack information
4. Include:
   - GitHub URL and loading syntax
   - Description and sound types
   - Tags for categorization
   - Usage examples
   - License info (if available)

## License Notes

**Important**: Many community sample packs have unclear licensing. The Dirt-Samples pack specifically has unknown provenance for many samples. For production use:

1. Check individual pack licenses
2. Consider using Clean-Samples (properly licensed)
3. Create your own samples when possible
4. Respect creator attributions

## Next Steps

Detailed documentation for major packs:
- [01_dirt_samples.md](01_dirt_samples.md) - Complete Dirt-Samples reference
- [02_garden.md](02_garden.md) - Garden pack documentation
- [03_clean_breaks.md](03_clean_breaks.md) - Clean-Breaks reference
- More pack documentation coming...

---

**Last Updated**: 2025-12-22  
**Total Packs**: 30+  
**Status**: Active research
