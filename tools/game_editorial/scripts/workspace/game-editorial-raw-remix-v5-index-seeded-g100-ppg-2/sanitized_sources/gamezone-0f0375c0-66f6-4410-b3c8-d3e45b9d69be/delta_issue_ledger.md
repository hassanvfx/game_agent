# Delta Issue Ledger

## Candidate 1
1. **Observed area** - `index.html` / looping background music volume
2. **Static evidence** - `this.bgm = make(ASSETS.bgm, 0.28);` exceeded the required maximum for looping audio.
3. **Browser evidence** - The bounded mobile pass verified the start-to-play flow that invokes `audio.playBGM()`, so the audited looped music path is part of the observed runtime.
4. **Confidence classification** - confirmed
5. **Proposed action** - fix
6. **Why** - Hard audio safety constraint requires looping audio at 20% volume or lower.

## Candidate 2
1. **Observed area** - start screen to play-state transition
2. **Static evidence** - `startGame()` hides the start overlay and reveals the controls.
3. **Browser evidence** - Runtime identity passed and the controls became visible after tapping **Stay Online** in the bounded mobile pass.
4. **Confidence classification** - uncertain
5. **Proposed action** - leave_as_is
6. **Why** - The short pass did not reveal a reproducible interaction or layout failure.
