# Delta Issue Ledger

## Issue 1
- **Observed area** - `index.html` audio start/run feedback
- **Static evidence** - audio bootstrap fetched remote audio buffers and audio tags declared cross-origin media, while the served game runs from localhost
- **Browser evidence** - Playwright console showed blocked start audio requests by CORS policy during the bounded mobile pass; runtime identity verification passed
- **Confidence classification** - confirmed
- **Proposed action** - fix
- **Why** - start SFX should not fail at runtime in the observed local browser flow

## Issue 2
- **Observed area** - `index.html` looping background music volume
- **Static evidence** - `playBgm()` set `el.volume = 0.6`, exceeding the 20% looping-audio safety cap
- **Browser evidence** - bounded pass exercised start flow that triggers BGM playback
- **Confidence classification** - confirmed
- **Proposed action** - fix
- **Why** - looped audio must stay at or below 20% volume per task safety guardrail

## Issue 3
- **Observed area** - mobile gameplay start and lane-switch flow
- **Static evidence** - start overlay, HUD, and pointer handlers were already wired for touch flow
- **Browser evidence** - start tap showed HUD and a right-side tap updated the badge to "Lane shift"
- **Confidence classification** - confirmed
- **Proposed action** - leave_as_is
- **Why** - core mobile interaction worked in the bounded pass
