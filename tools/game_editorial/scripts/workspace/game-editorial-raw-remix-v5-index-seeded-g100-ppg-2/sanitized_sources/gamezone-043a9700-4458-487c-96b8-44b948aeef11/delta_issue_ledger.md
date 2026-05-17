# Delta Issue Ledger

| Observed area | Static evidence | Browser evidence | Confidence classification | Proposed action | Why |
|---|---|---|---|---|---|
| Core start and jump flow in `index.html` | Start button initializes game state and canvas pointerdown triggers `jump()` | Start button worked and canvas tap produced a jump in mobile Playwright | confirmed | leave_as_is | Browser evidence shows expected behavior |
| Quiz gate flow in `index.html` | Quiz modal is triggered when `score % 1000 === 0` and answer buttons are generated dynamically | Bounded threshold setup did not surface the modal reliably | uncertain | leave_as_is | Evidence is insufficient for a safe gameplay patch |
| Looping background audio volume in `index.html` | `this.bgm = this.createAudio(ASSETS.bgm, 0.34, true)` exceeds the 20% cap for continuous looped audio | No browser playback defect observed, but static policy violation is explicit | confirmed | fix | Hard safety guardrail requires loop volume at 20% or lower |
