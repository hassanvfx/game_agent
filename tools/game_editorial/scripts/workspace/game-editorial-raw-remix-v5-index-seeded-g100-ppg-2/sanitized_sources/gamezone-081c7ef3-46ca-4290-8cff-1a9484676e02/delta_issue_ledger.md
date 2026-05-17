# Delta Issue Ledger

## Candidate 1
- **Observed area**: `index.html` audio asset map / startup-feedback flow
- **Static evidence**: `ASSETS.sfx` referenced approved remote URLs for `success_01`, `start_game_01`, `level_complete_01`, and `game_over_01`.
- **Browser evidence**: Initial Playwright pass captured six console resource failures; curl verification confirmed these four URLs returned HTTP 404 while catalog alternatives with `_02` existed and returned HTTP 200.
- **Confidence classification**: confirmed
- **Proposed action**: fix
- **Why**: Missing audio resources are a concrete runtime defect and the smallest safe fix is swapping to working approved catalog URLs.

## Candidate 2
- **Observed area**: `index.html` looping BGM volume
- **Static evidence**: `audio.unlock()` and `audio.playBGM()` set looping BGM volume to `0.22`.
- **Browser evidence**: No audible distortion was required to confirm; the issue is policy-based and source-grounded for a looping track.
- **Confidence classification**: confirmed
- **Proposed action**: fix
- **Why**: The audio safety guardrail requires long-running looped audio at 20% volume or lower.

## Candidate 3
- **Observed area**: core mobile gameplay flow
- **Static evidence**: Action handlers, HUD updates, and overlays are wired coherently in `advanceTurn()`, `updateUI()`, and start/restart listeners.
- **Browser evidence**: Start, Shift, and Train interactions all worked in the bounded 400x700 mobile Playwright pass with matching screenshots.
- **Confidence classification**: confirmed
- **Proposed action**: leave_as_is
- **Why**: The tested gameplay path behaved as expected and did not justify further edits.