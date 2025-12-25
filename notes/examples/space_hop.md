# A Spacey hip hop loop with some swing

```javascript
setcpm(90/4)
$: sound(`
[-  -  oh - ] [-  -  -  - ] [-  -  -  - ] [-  -  -  - ],
[hh hh -  - ] [hh -  hh - ] [hh -  hh - ] [hh -  hh - ],
[-  -  -  - ] [cp -  -  - ] [-  -  -  - ] [cp -  -  - ],
[bd -  -  - ] [-  -  -  bd] [-  -  bd - ] [-  -  -  bd]
`).bank("RolandTR808")

// Basic up arpeggio
$: n("0 2 4 7").scale("C4:minor")
  .s("square")
  .release(.5).gain(.7)

// Up and down / up and down
$: n("0 2 4 7 4 2").scale("<C2:minor C3:minor C4:minor <C3:minor C4:minor>>")
  .s("square")
  .lpf(2000).gain(.7)

// Complex arpeggio
$: n("<[0 2 4 7]*2 [0 3 5 8]*2>").late("[0 .02]*4")
  .scale("C4:minor")
  .s("sawtooth")
  .lpf(1500)
  .delay(.25).gain(.7)
```