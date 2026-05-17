# Delta Issue Ledger

## Candidate 1
1. **Observed area** - `index.html` / looping background music volume
2. **Static evidence** - `AudioSys.resume()` set `bgm.volume = 0.34` for the looping `#bgm_main` element.
3. **Browser evidence** - Mobile Playwright pass confirmed the game runs normally after start, and the post-fix runtime summary recorded looping BGM volume `0.2`.
4. **Confidence classification** - confirmed
5. **Proposed action** - fix
6. **Why** - Looping audio above 20% violated the stated audio safety guardrail.

## Candidate 2
1. **Observed area** - remote media loading / console 404s
2. **Static evidence** - The page references multiple remote media URLs for audio, fonts, and GIF feedback.
3. **Browser evidence** - Playwright captured two console messages: "Failed to load resource: the server responded with a status of 404 ()".
4. **Confidence classification** - uncertain
5. **Proposed action** - monitor_only
6. **Why** - The bounded pass did not isolate which exact resource failed, so a targeted code change would be speculative.
