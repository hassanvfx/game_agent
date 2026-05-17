# Delta Issue Ledger

## Candidate 1
1. **Observed area** - `index.html` / `AudioManager.loadBuffer` remote SFX loading flow
2. **Static evidence** - `loadBuffer()` uses `fetch(el.src)` and `decodeAudioData()` on remote catalog audio URLs. During local serving from `http://127.0.0.1`, those remote audio responses do not provide permissive CORS headers, so Web Audio decoding is blocked.
3. **Browser evidence** - `playwright_console_errors.json` shows CORS failures for `start_game_01.mp3` and `game_over_02.mp3` plus `net::ERR_FAILED` entries during the bounded mobile Playwright pass.
4. **Confidence classification** - confirmed
5. **Proposed action** - fix
6. **Why** - Preventing the blocked fetch path is a minimal change that removes confirmed runtime errors without changing core gameplay.

## Candidate 2
1. **Observed area** - remote font/media requests during initial load
2. **Static evidence** - `index.html` references multiple remote font/media URLs; the bounded pass recorded two generic 404 resource errors but they were not tied to a clearly gameplay-critical asset from the current evidence.
3. **Browser evidence** - `playwright_console_errors.json` includes two generic `404` resource failures without a precise asset path; gameplay still loaded, identity verification passed, and the short interaction pass remained playable.
4. **Confidence classification** - uncertain
5. **Proposed action** - leave_as_is
6. **Why** - The bounded evidence does not identify a specific broken gameplay or UI dependency to patch safely.