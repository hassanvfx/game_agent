# Delta Issue Ledger

## Candidate 1
1. **Observed area** - audio / start and win SFX fetches
2. **Static evidence** - `ASSETS.sfx.start` and `ASSETS.sfx.win` pointed to URLs that returned 404 in browser/runtime checks.
3. **Browser evidence** - Playwright response tracing captured 404s for `/assets/audios/ui/start_game_01.mp3` and `/assets/audios/ui/level_complete_01.mp3`; after patching to approved catalog URLs, the bounded replay produced no 404 responses.
4. **Confidence classification** - confirmed
5. **Proposed action** - fix
6. **Why** - broken audio fetches were directly observed and the smallest safe fix was replacing only the failing URLs with approved reachable catalog sources.

## Candidate 2
1. **Observed area** - mobile gameplay interaction / touch steering
2. **Static evidence** - touch handlers are attached directly to `#gameCanvas` with passive suppression disabled on touchstart.
3. **Browser evidence** - mobile Playwright taps on the canvas worked, active run remained visible, and no interaction failure was confirmed.
4. **Confidence classification** - uncertain
5. **Proposed action** - leave_as_is
6. **Why** - bounded browser evidence did not confirm a real defect.
