# Delta Issue Ledger

## Candidate 1
1. **Observed area** - `index.html` / looping background music safety
2. **Static evidence** - `unlockAudio()` and `initGame()` both set `bgm.volume = 0.22`, which exceeds the node's 20% maximum for looping or continuous audio.
3. **Browser evidence** - Runtime identity was verified in the bounded mobile pass, and the post-fix verification recorded `bgm.volumeAfterUnlock = 0.2`.
4. **Confidence classification** - confirmed
5. **Proposed action** - fix
6. **Why** - This is a direct policy violation with a minimal one-line-per-call correction.

## Candidate 2
1. **Observed area** - `index.html` / mobile chat input and send flow
2. **Static evidence** - Input handlers, safe-area layout, and guarded global pointer handling already appear mobile-oriented and bounded.
3. **Browser evidence** - The textarea accepted focus and text entry, the send button remained visible, and the reply flow completed with no runtime errors.
4. **Confidence classification** - uncertain
5. **Proposed action** - leave_as_is
6. **Why** - Observed behavior matched expectations, so no break was confirmed.

## Candidate 3
1. **Observed area** - `index.html` / tap-to-reroute field interaction
2. **Static evidence** - Pointer handling only acts when the canvas is targeted and updates the courier target position plus route feedback.
3. **Browser evidence** - The bounded route tap produced the expected post-interaction state without visible breakage or console errors.
4. **Confidence classification** - uncertain
5. **Proposed action** - leave_as_is
6. **Why** - The interaction worked during the bounded pass, so there is no confirmed defect to patch.
