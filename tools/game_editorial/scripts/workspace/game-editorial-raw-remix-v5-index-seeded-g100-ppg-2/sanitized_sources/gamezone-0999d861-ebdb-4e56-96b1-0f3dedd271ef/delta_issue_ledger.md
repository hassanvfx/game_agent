# Delta Issue Ledger

## Issue 1
- **Observed area**: `index.html` audio setup and playback flow
- **Static evidence**: one-shot SFX were loaded through `fetch(...).arrayBuffer()` and `decodeAudioData` against remote catalog URLs, and looping BGM volume was set above the required 20% cap.
- **Browser evidence**: the initial bounded Playwright pass produced CORS console errors for remote audio loading during startup and interaction.
- **Confidence classification**: confirmed
- **Proposed action**: fix
- **Why**: a minimal audio-path change removes the confirmed fetch/decode failure mode and brings looping audio down to the required safe volume.

## Issue 2
- **Observed area**: mobile layout and core interaction flow
- **Static evidence**: HUD, controls, safe-area spacing, and core tap handlers are all wired directly in `index.html`.
- **Browser evidence**: the bounded 400x700 mobile pass showed the start screen, HUD, controls, countdown, and fail-state feedback functioning without layout breakage.
- **Confidence classification**: confirmed
- **Proposed action**: leave_as_is
- **Why**: no visual or mechanics defect was confirmed in the observed mobile flow.