# Delta Issue Ledger

## Candidate 1
1. **Observed area** - `index.html` / looped background music
2. **Static evidence** - `syncLoopAudio()` set `bgm.volume = 0.32`, which exceeds the node safety cap for looping audio
3. **Browser evidence** - bounded Playwright pass confirmed the correct runtime loaded and no stronger gameplay defect displaced this review; audio policy issue remains source-grounded
4. **Confidence classification** - `confirmed`
5. **Proposed action** - `fix`
6. **Why** - looped audio above 20% violates the required safety guardrail

## Candidate 2
1. **Observed area** - gameplay steering / main runner loop
2. **Static evidence** - pointer handlers, update loop, and HUD updates are wired correctly in `index.html`
3. **Browser evidence** - initial load plus two drag interactions completed without crash, game-over lock, or layout failure; title and HUD identity matched the workspace
4. **Confidence classification** - `uncertain`
5. **Proposed action** - `leave_as_is`
6. **Why** - bounded browser evidence did not confirm a gameplay defect

## Candidate 3
1. **Observed area** - vibration calls during Playwright pass
2. **Static evidence** - `vibrate()` falls back to `navigator.vibrate(...)` when bridge APIs are unavailable
3. **Browser evidence** - console reported blocked vibration because the browser did not treat the synthetic interaction as a user gesture
4. **Confidence classification** - `uncertain`
5. **Proposed action** - `monitor_only`
6. **Why** - this appears environment-specific and does not justify a gameplay code patch