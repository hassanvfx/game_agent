# Delta Issue Ledger

## Issue 1
- **Observed area**: `index.html` audio asset configuration for start BGM / start SFX / win SFX
- **Static evidence**: `ASSETS` referenced `arcade_loop_02.mp3`, `start_game_02.mp3`, and `level_complete_02.mp3`
- **Browser evidence**: initial Playwright pass captured remote 404 failures for configured audio URLs during the start flow; post-fix verification reported zero failed network requests
- **Confidence classification**: `confirmed`
- **Proposed action**: `fix`
- **Why**: broken runtime audio requests were directly observed and were corrected by swapping to working approved catalog URLs

## Issue 2
- **Observed area**: `index.html` looping victory audio volume
- **Static evidence**: `this.victoryLoop.volume = 0.24`
- **Browser evidence**: no audible distortion was required to confirm this; the configured value exceeded the node's explicit loop-volume safety cap
- **Confidence classification**: `confirmed`
- **Proposed action**: `fix`
- **Why**: looping audio above 20% violated the required safety guardrail, so it was reduced to `0.2`

## Issue 3
- **Observed area**: start overlay, HUD flow, first roll behavior, mobile layout
- **Static evidence**: layout and turn flow code were already compact and mobile-oriented
- **Browser evidence**: runtime identity passed; initial, after-start, and after-roll screenshots showed correct rendering and expected HUD behavior in the bounded mobile flow
- **Confidence classification**: `confirmed`
- **Proposed action**: `leave_as_is`
- **Why**: the bounded browser pass did not show a clearly justified gameplay or layout defect outside the broken audio URLs