# Strudel Audio Effects Reference

**Research Date**: 2025-12-22  
**Source**: https://strudel.cc/learn/effects/

## Signal Chain Order

1. Sound generation (sample or oscillator)
2. Detune-based effects
3. Sequential effects:
   - Gain (`gain`)
   - Lowpass filter (`lpf`)
   - Highpass filter (`hpf`)
   - Bandpass filter (`bandpass`)
   - Vowel filter (`vowel`)
   - Sample rate reduction (`coarse`)
   - Bit crushing (`crush`)
   - Waveshape distortion (`shape`)
   - Normal distortion (`distort`)
   - Tremolo (`tremolo`)
   - Compressor (`compressor`)
   - Panning (`pan`)
   - Phaser (`phaser`)
   - Postgain (`post`)
4. Splitting to delay/reverb
5. Mixing in orbits

## Filters

### lpf() - Low-Pass Filter
**Synonyms**: `cutoff`, `ctf`, `lp`  
**Range**: 0-20000 Hz

```javascript
s("bd sd [~ bd] sd,hh*6").lpf("<4000 2000 1000 500>")
s("bd*16").lpf("1000:0 1000:10 1000:20")  // With resonance
```

### lpq() - Low-Pass Resonance
**Synonyms**: `resonance`  
**Range**: 0-50

```javascript
s("bd sd,hh*8").lpf(2000).lpq("<0 10 20 30>")
```

### hpf() - High-Pass Filter
**Synonyms**: `hp`, `hcutoff`  
**Range**: 0-20000 Hz

```javascript
s("bd sd,hh*8").hpf("<4000 2000 1000 500>")
```

### hpq() - High-Pass Resonance
**Synonyms**: `hresonance`  
**Range**: 0-50

```javascript
s("bd sd,hh*8").hpf(2000).hpq("<0 10 20 30>")
```

### bpf() - Band-Pass Filter
**Synonyms**: `bandf`, `bp`

```javascript
s("bd sd,hh*6").bpf("<1000 2000 4000 8000>")
```

### bpq() - Band-Pass Resonance
**Synonyms**: `bandq`

```javascript
s("bd sd").bpf(500).bpq("<0 1 2 3>")
```

### vowel() - Formant Filter
**Vowels**: a, e, i, o, u, ae, aa, oe, ue, y, uh, un, en, an, on

```javascript
note("[c2 <eb2 <g2 g1>>]*2").s('sawtooth').vowel("<a e i o u>")
s("bd sd mt ht").vowel("[a|e|i|o|u]")  // Random choice
```

### ftype() - Filter Type
**Types**: 12db (0), ladder (1), 24db (2)

```javascript
note("c f g a").s("sawtooth")
  .lpf(200).lpenv(3).lpq(1)
  .ftype("<ladder 12db 24db>")
```

## ADSR Envelope

### attack() / att()
**Range**: Time in seconds

```javascript
note("c3 e3 f3 g3").attack("<0 .1 .5>")
```

### decay() / dec()
**Range**: Time in seconds

```javascript
note("c3 e3 f3 g3").decay("<.1 .2 .3 .4>").sustain(0)
```

### sustain() / sus()
**Range**: 0-1 (amplitude level)

```javascript
note("c3 e3 f3 g3").decay(.2).sustain("<0 .1 .4 .6 1>")
```

### release() / rel()
**Range**: Time in seconds

```javascript
note("c3 e3 g3 c4").release("<0 .1 .4 .6 1>/2")
```

### adsr()
**Format**: `"attack:decay:sustain:release"`

```javascript
note("[c3 bb2 f3 eb3]*2")
  .sound("sawtooth").lpf(600)
  .adsr(".1:.1:.5:.2")
```

## Filter Envelope

### lpenv() / lpe()
**Range**: Depth of modulation (0 to n semitones)

```javascript
note("c2 e2 f2 g2").sound('sawtooth')
  .lpf(300).lpa(.5)
  .lpenv("<4 2 1 0 -1 -2 -4>/4")
```

### lpattack() / lpa()
```javascript
note("c2 e2 f2 g2").sound('sawtooth')
  .lpf(300).lpa("<.5 .25 .1 .01>/4").lpenv(4)
```

### lpdecay() / lpd()
```javascript
note("c2 e2 f2 g2").sound('sawtooth')
  .lpf(300).lpd("<.5 .25 .1 0>/4").lpenv(4)
```

### lpsustain() / lps()
```javascript
note("c2 e2 f2 g2").sound('sawtooth')
  .lpf(300).lpd(.5).lps("<0 .25 .5 1>/4").lpenv(4)
```

### lprelease() / lpr()
```javascript
note("c2 e2 f2 g2").sound('sawtooth')
  .lpf(300).lpenv(4).lpr("<.5 .25 .1 0>/4")
```

## Pitch Envelope

### penv()
**Range**: Semitones to modulate

```javascript
note("c").penv("<12 7 1 .5 0 -1 -7 -12>")
```

### pattack() / patt()
```javascript
note("c eb g bb").pattack("0 .1 .25 .5").slow(2)
```

### pdecay() / pdec()
```javascript
note("<c eb g bb>").pdecay("<0 .1 .25 .5>")
```

### prelease() / prel()
```javascript
note("<c eb g bb> ~").release(.5).prelease("<0 .1 .25 .5>")
```

### pcurve()
**Types**: 0 = linear, 1 = exponential

```javascript
note("g1*4").s("sine").pdec(.5).penv(32).pcurve("<0 1>")
```

### panchor()
**Range**: Anchor offset (0-1)

```javascript
note("c c4").penv(12).panchor("<0 .5 1 .5>")
```

## Time-Based Effects

### delay()
**Format**: `"level"` or `"level:time:feedback"`  
**Range**: 0-1

```javascript
s("bd bd").delay("<0 .25 .5 1>")
s("bd bd").delay("0.65:0.25:0.9")  // With time and feedback
```

### delaytime()
**Range**: Time in cycles

```javascript
s("bd sd").delay(.5).delaytime(.25)
```

### delayfeedback() / delayfb() / dfb()
**Range**: 0-1

```javascript
s("bd").delay(.25).delayfeedback("<.25 .5 .75 1>")
```

### room()
**Format**: `"level"` or `"level:size"`  
**Range**: 0-1

```javascript
s("bd sd [~ bd] sd").room("<0 .2 .4 .6 .8 1>")
s("bd sd").room("<0.9:1 0.9:4>")  // With size
```

### roomsize() / rsize() / sz() / size()
**Range**: 0-10

```javascript
s("bd sd").room(.8).rsize(1)  // Small room
s("bd sd").room(.8).rsize(4)  // Large room
```

### roomfade() / rfade()
**Range**: Seconds for reverb to fade

```javascript
s("bd sd").room(0.5).rfade(0.5)  // Quick fade
s("bd sd").room(0.5).rfade(4)    // Long fade
```

### roomlp() / rlp()
**Range**: 0-20000 Hz (reverb low-pass)

```javascript
s("bd sd").room(0.5).rlp(10000)  // Bright reverb
s("bd sd").room(0.5).rlp(5000)   // Dark reverb
```

### roomdim() / rdim()
**Range**: 0-20000 Hz (reverb damping)

```javascript
s("bd sd").room(0.5).rlp(10000).rdim(8000)
```

## Modulation Effects

### phaser() / ph()
**Range**: Speed of modulation

```javascript
n(run(8)).scale("D:pentatonic").s("sawtooth")
  .release(0.5).phaser("<1 2 4 8>")
```

### phaserdepth() / phd() / phasdp()
**Range**: 0-1

```javascript
n(run(8)).scale("D:pentatonic").s("sawtooth")
  .phaser(2).phaserdepth("<0 .5 .75 1>")
```

### phasercenter() / phc()
**Range**: Center frequency in Hz

```javascript
n(run(8)).scale("D:pentatonic").s("sawtooth")
  .phaser(2).phasercenter("<800 2000 4000>")
```

### phasersweep() / phs()
**Range**: 0-4000 (most useful)

```javascript
n(run(8)).scale("D:pentatonic").s("sawtooth")
  .phaser(2).phasersweep("<800 2000 4000>")
```

## Amplitude Modulation

### tremolo()
See tremolosync() for cycle-based control

### tremolosync() / tremsync()
**Range**: Modulation speed in cycles

```javascript
note("d d d# d".fast(4)).s("supersaw")
  .tremolosync("4").tremoloskew("<1 .5 0>")
```

### tremolodepth() / tremdepth()
**Range**: Depth of modulation

```javascript
note("a1".fast(4)).s("pulse")
  .tremsync(4).tremolodepth("<1 2 .7>")
```

### tremoloskew() / tremskew()
**Range**: 0-1

```javascript
note("{f a c e}%16").s("sawtooth")
  .tremsync(4).tremoloskew("<.5 0 1>")
```

### tremolophase() / tremphase()
**Range**: Offset in cycles

```javascript
note("{f a c e}%16").s("sawtooth")
  .tremsync(4).tremolophase("<0 .25 .66>")
```

### tremoloshape() / tremshape()
**Shapes**: tri, square, sine, saw, ramp

```javascript
note("{f g c d}%16").tremsync(4)
  .tremoloshape("<sine tri square>").s("sawtooth")
```

## Dynamics

### gain()
**Range**: Volume multiplier

```javascript
s("hh*8").gain(".4!2 1 .4!2 1 .4 1").fast(2)
s("bd*4").gain(perlin.range(.6, .9))
```

### velocity()
**Range**: 0-1 (multiplied with gain)

```javascript
s("hh*8").gain(".4!2 1").velocity(".4 1")
```

### compressor()
**Format**: `"threshold:ratio:knee:attack:release"`

```javascript
s("bd sd [~ bd] sd,hh*8")
  .compressor("-20:20:10:.002:.02")
```

### postgain()
**Range**: Gain after all effects

```javascript
s("bd sd,hh*8")
  .compressor("-20:20:10:.002:.02")
  .postgain(1.5)
```

## Panning

### pan()
**Range**: 0 (left) to 1 (right)

```javascript
s("[bd hh]*2").pan("<.5 1 .5 0>")
s("bd rim sd rim").pan(sine.slow(2))
```

### jux()
Applies function to right channel only

```javascript
s("bd lt [~ ht] mt cp").jux(rev)
s("bd sd").jux(fast(2))
```

### juxBy() / juxby()
**Range**: 0 (mono) to 1 (full stereo)

```javascript
s("bd lt [~ ht] mt").juxBy("<0 .5 1>/2", rev)
```

## Waveshaping

### coarse()
**Range**: Sample rate reduction factor (1 = original)

```javascript
s("bd sd,hh*8").coarse("<1 4 8 16 32>")
```

### crush()
**Range**: 1 (drastic) to 16 (minimal)

```javascript
s("<bd sd>,hh*3").fast(2).crush("<16 8 7 6 5 4 3 2>")
```

### distort() / dist()
**Format**: `"amount"` or `"amount:volume:type"`  
**Types**: diode, etc.

```javascript
s("bd sd,hh*8").distort("<0 2 3 10:.5>")
note("d1!8").s("sine").penv(36).distort("8:.4")
s("bd:4*4").distort("3:0.5:diode")
```

### shape()
**Range**: Waveshape amount

```javascript
note("c2 eb2").s("sawtooth").shape(.3)
```

### clip() / legato()
**Range**: Duration multiplier

```javascript
note("c a f e").s("piano").clip("<.5 1 2>")
```

## Orbits

### orbit() / o()
**Range**: Orbit number (for independent effect chains)

```javascript
stack(
  s("hh*6").delay(.5).orbit(1),
  s("~ sd ~ sd").delay(.5).orbit(2)
)
```

### duckorbit() / duck()
Ducks (reduces volume of) specified orbit(s)

**Format**: `"orbit"` or `"orbit1:orbit2"`

```javascript
$: n(run(16)).scale("c:minor:pentatonic")
   .s("sawtooth").orbit(2)
$: s("bd:4!4").duckorbit(2).duckattack(0.2).duckdepth(1)
```

### duckattack() / duckatt()
**Range**: Attack time in seconds

```javascript
s("bd:4!4").duckorbit(2).duckattack("<0.2 0 0.4>")
```

### duckdepth()
**Range**: 0-1

```javascript
s("bd:4!4").duckorbit(2).duckdepth("<1 .9 .6 0>")
```
