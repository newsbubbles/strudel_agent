# Community Sample Packs - Quick Reference

**Research Date**: 2025-12-22  
**Source**: https://github.com/terryds/awesome-strudel

This document provides quick reference information for community-contributed Strudel sample packs. For detailed documentation on major packs, see individual files.

## How to Use

All packs listed here can be loaded using:

```javascript
samples('github:username/repository')
```

## Featured Community Packs

### Clean-Breaks
**GitHub**: `github:yaxu/clean-breaks`  
**Creator**: Alex McLean (yaxu)  
**Type**: Drum breaks  
**License**: Properly sourced and licensed  
**Tags**: `breaks`, `drums`, `licensed`, `clean`

**Description**: Collection of drum break samples with clear provenance and licensing. A cleaner alternative to unlicensed break collections.

**Usage**:
```javascript
samples('github:yaxu/clean-breaks')
s("break").n("0 1 2 3").chop(8)
```

---

### Dough-Amen
**GitHub**: `github:Bubobubobubobubo/Dough-Amen`  
**Creator**: Bubobubobubobubo  
**Type**: Amen break variations  
**Tags**: `breaks`, `amen`, `jungle`, `dnb`

**Description**: Variations and processing of the iconic Amen break. Essential for jungle, drum & bass, and breakcore.

**Usage**:
```javascript
samples('github:Bubobubobubobubo/Dough-Amen')
s("amen").n(irand(16)).fast(2)
```

---

### Dough-Juj
**GitHub**: `github:Bubobubobubobubo/Dough-Juj`  
**Creator**: Bubobubobubobubo  
**Type**: Custom samples  
**Tags**: `custom`, `experimental`

**Description**: Custom sample collection from Bubobubobubobubo.

**Usage**:
```javascript
samples('github:Bubobubobubobubo/Dough-Juj')
```

---

### Livecoding-Samples
**GitHub**: `github:wyan/livecoding-samples`  
**Creator**: wyan  
**Type**: Live coding optimized  
**Tags**: `live-coding`, `performance`, `algorave`

**Description**: Sample pack specifically designed for live coding performances. Optimized for real-time use.

**Usage**:
```javascript
samples('github:wyan/livecoding-samples')
```

---

### Capoeira Strudel
**GitHub**: `github:salsicha/capoeira_strudel`  
**Creator**: salsicha  
**Type**: Capoeira music  
**Tags**: `capoeira`, `percussion`, `world`, `brazilian`

**Description**: Samples from capoeira music - Brazilian martial art with rich percussion tradition.

**Usage**:
```javascript
samples('github:salsicha/capoeira_strudel')
// Berimbau, atabaque, pandeiro, agogô samples
```

---

### MS Teams Sounds
**GitHub**: `github:AustinOliverHaskell/ms-teams-sounds-strudel`  
**Creator**: AustinOliverHaskell  
**Type**: Microsoft Teams sounds  
**Tags**: `meme`, `corporate`, `notification`, `fun`

**Description**: Microsoft Teams notification and UI sounds. Great for ironic/humorous compositions.

**Usage**:
```javascript
samples('github:AustinOliverHaskell/ms-teams-sounds-strudel')
// Join sound, leave sound, notifications, etc.
```

---

### Quantum Music
**GitHub**: `github:QuantumVillage/quantum-music`  
**Creator**: QuantumVillage  
**Type**: Quantum/experimental  
**Tags**: `experimental`, `quantum`, `algorithmic`

**Description**: Experimental samples with quantum/scientific theme.

**Usage**:
```javascript
samples('github:QuantumVillage/quantum-music')
```

---

### Vasilymilovidov Samples
**GitHub**: `github:vasilymilovidov/samples`  
**Creator**: vasilymilovidov  
**Type**: Beats, percussion, impulse responses  
**Tags**: `drums`, `percussion`, `ir`, `reverb`

**Description**: Collection including:
- `b1`, `b2`, `b3` - Beat/bass samples
- `ir` - Impulse responses for reverb
- `kik` - Kick drums
- `prc` - Percussion
- `ky1`, `ns1` - Additional categories

**Usage**:
```javascript
samples('github:vasilymilovidov/samples')
s("kik*4, prc*8")
```

---

### Polifonia Samples
**GitHub**: `github:fstiffo/polifonia-samples`  
**Creator**: fstiffo  
**Type**: Polyphonic samples  
**Tags**: `melodic`, `polyphonic`, `harmonic`

**Description**: Samples with polyphonic/harmonic content.

**Usage**:
```javascript
samples('github:fstiffo/polifonia-samples')
```

---

### Algorave Dave Samples
**GitHub**: `github:algorave-dave/samples`  
**Creator**: algorave-dave  
**Type**: Algorave performance samples  
**Tags**: `algorave`, `live-coding`, `performance`

**Description**: Samples used in algorave performances.

**Usage**:
```javascript
samples('github:algorave-dave/samples')
```

---

## Generic Community Packs

These packs don't have detailed descriptions but are available for exploration:

| Pack | GitHub | Creator |
|------|--------|--------|
| AuditeMarlow | `github:AuditeMarlow/samples` | AuditeMarlow |
| Crate | `github:eddyflux/crate` | eddyflux |
| EloMorelo | `github:EloMorelo/samples` | EloMorelo |
| emrexdeger | `github:emrexdeger/strudelSamples` | emrexdeger |
| fjpolo | `github:fjpolo/fjpolo-Strudel` | fjpolo |
| cavlp-25p | `github:hvillase/cavlp-25p` | hvillase |
| k09 | `github:k09/samples` | k09 |
| kaiye10 | `github:kaiye10/strudelSamples` | kaiye10 |
| msl-strudel | `github:mysinglelise/msl-strudel-samples` | mysinglelise |
| Nikeryms | `github:Nikeryms/Samples` | Nikeryms |
| departure | `github:prismograph/departure` | prismograph |
| RikyBac15 | `github:RikyBac15/samples` | RikyBac15 |
| rochormatic | `github:sonidosingapura/rochormatic` | sonidosingapura |
| terrorhank | `github:terrorhank/samples` | terrorhank |
| tesspilot | `github:tesspilot/samples` | tesspilot |
| TodePond | `github:TodePond/samples` | TodePond |
| mirus | `github:TristanCacqueray/mirus` | TristanCacqueray |
| graffathon25 | `github:Veikkosuhonen/graffathon25-demo` | Veikkosuhonen |
| RepositorioDesonidos | `github:bruveping/RepositorioDesonidosParaExperimentar02` | bruveping |

## Loading Multiple Packs

```javascript
// Load multiple packs in sequence
samples('github:tidalcycles/Dirt-Samples')
samples('github:mot4i/garden')
samples('github:yaxu/clean-breaks')

// Now all samples are available
stack(
  sound("bd*4"),              // Dirt-Samples
  sound("garden_sd*2"),       // Garden
  s("break:0").chop(8)        // Clean-Breaks
)
```

## Combining Packs Creatively

### Layering Different Packs

```javascript
// Layer Garden warmth with 808 punch
stack(
  sound("garden_bd*4").lpf(1000),
  sound("808bd*4").gain(0.6).hpf(100)
)
```

### Using Breaks from Multiple Sources

```javascript
// Alternate between break sources
s("<amencutup break>").n("0 1 2 3").chop(8)
```

### Thematic Mixing

```javascript
// Corporate dystopia theme
stack(
  s("ms-teams").n("<0 1 2>").slow(4),  // Teams sounds
  sound("glitch*8").gain(0.4),          // Glitchy texture
  sound("808bd*4")                      // Driving beat
)
```

## Discovery Tools

### Open Strudel Samples Explorer
**URL**: https://therebelrobot.github.io/open-strudel-samples/

React app for:
- Searching GitHub for `strudel.json` files
- Previewing samples before loading
- Exploring community packs

### Strudel Samples Registry
**URL**: https://strudel-samples.alternet.site

Community registry for:
- Finding known sample packs
- Previewing samples
- Adding your own packs

## Creating Your Own Pack

### Basic Structure

1. Create a GitHub repository
2. Add sample files (wav, mp3, ogg)
3. Create `strudel.json`:

```json
{
  "sounds": {
    "kick": ["kick1.wav", "kick2.wav"],
    "snare": ["snare1.wav", "snare2.wav"],
    "hats": ["hh1.wav", "hh2.wav"]
  }
}
```

4. Load in Strudel:
```javascript
samples('github:yourusername/yourrepo')
sound("kick snare hats*4")
```

### Best Practices

- **Organize by type**: Separate folders for drums, bass, melody, etc.
- **Consistent naming**: Use clear, descriptive names
- **Include README**: Document what's in your pack
- **Add license info**: Specify usage rights
- **Keep files small**: Optimize for web loading
- **Test thoroughly**: Verify all samples load correctly

## License Considerations

**Important**: Many community packs have unclear licensing. Before using in production:

1. ✅ Check repository README for license info
2. ✅ Contact creator if unclear
3. ✅ Use packs with explicit licenses (like Garden, Clean-Breaks)
4. ✅ Create your own samples when possible
5. ❌ Don't assume "on GitHub" = "free to use commercially"

### Packs with Clear Licenses

- **Garden**: Free with attribution
- **Clean-Breaks**: Properly licensed
- **Clean-Samples**: Creative Commons (check metadata)

## See Also

- [00_SAMPLE_PACKS_INDEX.md](00_SAMPLE_PACKS_INDEX.md) - Complete index
- [01_dirt_samples.md](01_dirt_samples.md) - Dirt-Samples reference
- [02_garden.md](02_garden.md) - Garden pack reference
- [awesome-strudel](https://github.com/terryds/awesome-strudel) - Community resources

---

**Last Updated**: 2025-12-22  
**Total Packs**: 30+  
**Status**: Active documentation
