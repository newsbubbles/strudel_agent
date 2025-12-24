# Known Sample Packs Directory

**Last Updated**: 2025-12-22

This directory contains comprehensive documentation of all known Strudel-compatible sample packs available on GitHub.

## Contents

### Index & Overview
- **[00_SAMPLE_PACKS_INDEX.md](00_SAMPLE_PACKS_INDEX.md)** - Master index of all 30+ sample packs with quick reference

### Detailed Pack Documentation
- **[01_dirt_samples.md](01_dirt_samples.md)** - Complete reference for TidalCycles Dirt-Samples (100+ categories)
- **[02_garden.md](02_garden.md)** - Garden pack by mot4i (analog warmth, curated drums)
- **[03_community_packs_quick_reference.md](03_community_packs_quick_reference.md)** - Quick reference for 30+ community packs

## Quick Start

### Load a Sample Pack

```javascript
// Load Dirt-Samples (default)
samples('github:tidalcycles/Dirt-Samples')

// Load Garden pack
samples('github:mot4i/garden')

// Load Clean-Breaks
samples('github:yaxu/clean-breaks')
```

### Use Samples

```javascript
// Dirt-Samples
sound("bd*4, [~ sd]*2, hh*8")

// Garden pack
sound("garden_bd*4, [~ garden_sd]*2, garden_hh*8")

// Clean-Breaks
s("break:0").chop(8)
```

## Research Summary

### Sources Analyzed
- awesome-strudel repository (30+ packs)
- TidalCycles Dirt-Samples (100+ categories)
- Garden pack (detailed)
- Community pack repositories
- Sample pack explorer tools

### Total Packs Documented
- **30+** GitHub repositories
- **100+** sample categories in Dirt-Samples
- **13** categories in Garden pack
- **Multiple** specialized packs (breaks, capoeira, MS Teams, etc.)

### Key Findings

1. **Dirt-Samples is canonical** - Default pack with 100+ categories
2. **Garden offers quality** - Curated, analog-processed samples with clear license
3. **Clean packs exist** - Clean-Samples and Clean-Breaks have proper licensing
4. **Community is active** - 30+ community-contributed packs
5. **Licensing varies** - Many packs have unclear provenance
6. **Discovery tools available** - open-strudel-samples and strudel-samples.alternet.site

## By Use Case

### For Production Work
**Use these** (clear licensing):
- Garden (`github:mot4i/garden`) - Free with attribution
- Clean-Breaks (`github:yaxu/clean-breaks`) - Properly licensed
- Clean-Samples (`github:tidalcycles/Clean-Samples`) - CC licensed

### For Experimentation
**Use these** (comprehensive):
- Dirt-Samples (`github:tidalcycles/Dirt-Samples`) - 100+ categories
- Community packs - Variety and exploration

### For Live Coding
**Use these** (performance-optimized):
- livecoding-samples (`github:wyan/livecoding-samples`)
- algorave-dave/samples (`github:algorave-dave/samples`)
- Garden (`github:mot4i/garden`) - Punchy and responsive

### For Specific Genres

**Breaks/Jungle/DnB**:
- Dough-Amen (`github:Bubobubobubobubo/Dough-Amen`)
- Clean-Breaks (`github:yaxu/clean-breaks`)
- Dirt-Samples breaks (breaks125, breaks152, etc.)

**House/Techno**:
- Dirt-Samples (808, 909)
- Garden (analog warmth)

**Hip-Hop**:
- Dirt-Samples (808)
- Garden (punchy drums)

**World Music**:
- capoeira_strudel (`github:salsicha/capoeira_strudel`)

**Experimental**:
- quantum-music (`github:QuantumVillage/quantum-music`)
- Dirt-Samples (glitch, experimental categories)

## Tags Reference

Packs are tagged by:
- **Type**: drums, breaks, synths, bass, fx, percussion, melodic, vocals, field-recording
- **Character**: analog, digital, lo-fi, vintage, modern
- **Genre**: techno, house, hip-hop, ambient, experimental, algorave
- **Quality**: curated, comprehensive, licensed, clean

## Tools & Resources

### Sample Pack Explorers
- **open-strudel-samples**: https://therebelrobot.github.io/open-strudel-samples/
- **strudel-samples**: https://strudel-samples.alternet.site

### Community Resources
- **awesome-strudel**: https://github.com/terryds/awesome-strudel
- **Strudel Discord**: https://discord.com/invite/HGEdXmRkzT
- **TidalCycles Club**: https://club.tidalcycles.org/

## Creating Your Own Pack

See [03_community_packs_quick_reference.md](03_community_packs_quick_reference.md#creating-your-own-pack) for:
- Repository structure
- strudel.json format
- Best practices
- License considerations

## License Warning

⚠️ **Important**: Many community packs have unclear licensing. For commercial use:

1. Use packs with explicit licenses (Garden, Clean-Breaks, Clean-Samples)
2. Contact creators for permission
3. Create your own samples
4. Check individual repository READMEs

Do not assume "on GitHub" means "free to use commercially."

## Contributing

To add documentation for a new pack:

1. Research the pack (GitHub, README, samples)
2. Create markdown file: `XX_packname.md`
3. Include: URL, description, categories, usage examples, tags, license
4. Update index and this README

## Statistics

- **Total Packs**: 30+
- **Documented in Detail**: 3 (Dirt-Samples, Garden, Community Quick Ref)
- **Sample Categories**: 100+ (Dirt-Samples alone)
- **Discovery Tools**: 2
- **Community Resources**: 3+

## See Also

- [../research/](../research/) - Strudel core functionality research
- [../examples/](../examples/) - Example compositions
- [../../agents/StrudelCoder.md](../../agents/StrudelCoder.md) - Agent blueprint

---

**Research Date**: 2025-12-22  
**Status**: Comprehensive  
**Next Steps**: Continue documenting individual community packs as needed
