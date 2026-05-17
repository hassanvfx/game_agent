# Delta Issue Ledger

## Candidate Issue 1
1. **Observed area** - `index.html` / audio preload flow in `AudioManager.loadSound()`
2. **Static evidence** - the function attempted `fetch(src)` for remote audio asset URLs before decoding them into Web Audio buffers.
3. **Browser evidence** - initial Playwright pass logged a CORS console error for `https://gamezone-virid.vercel.app/assets/audios/ui/start_game_01.mp3` and related failed resource noise during startup.
4. **Confidence classification** - `confirmed`
5. **Proposed action** - `fix`
6. **Why** - cross-origin buffer preloading was producing avoidable runtime errors without being required for the core gameplay loop.

## Candidate Issue 2
1. **Observed area** - gameplay cooking/stock increase flow
2. **Static evidence** - `cookSpeed` is `20` and `COOK_MAX` is `100`, so five taps should complete one cooking cycle in principle.
3. **Browser evidence** - one bounded screenshot captured stock still at `0` after a five-tap burst, but the same pass later showed cash increasing to `15`, indicating the overall flow still functions.
4. **Confidence classification** - `uncertain`
5. **Proposed action** - `leave_as_is`
6. **Why** - bounded evidence was inconclusive and insufficient to justify a gameplay patch.

## Candidate Issue 3
1. **Observed area** - generic missing resource noise during runtime
2. **Static evidence** - no direct code-level source was isolated during the bounded pass.
3. **Browser evidence** - post-fix console output still contained one generic `404` resource message with no confirmed visible or mechanical break.
4. **Confidence classification** - `uncertain`
5. **Proposed action** - `monitor_only`
6. **Why** - the remaining message was not traced to a player-facing defect within the allowed conservative pass.