# Delta Issue Ledger

## Candidate 1
1. **Observed area** - `index.html` / `AudioManager.loadSound()` / start and fail audio flow
2. **Static evidence** - The loader used `fetch(el.src)` plus `decodeAudioData()` for remote audio sources served from another origin, which is incompatible with remote media that does not send permissive CORS headers to a localhost page.
3. **Browser evidence** - Initial Playwright pass logged CORS failures and fallback warnings for `game_over_02.mp3` and `start_game_01.mp3`.
4. **Confidence classification** - `confirmed`
5. **Proposed action** - `fix`
6. **Why** - Runtime evidence directly matched the static cause and the minimal fix was to avoid cross-origin fetch/decode for those remote assets.

## Candidate 2
1. **Observed area** - `index.html` / looping background music volume
2. **Static evidence** - `playBgm()` set looping background music volume to `0.4`.
3. **Browser evidence** - No playback fault, but this violates the explicit node audio safety rule for looping audio above 20%.
4. **Confidence classification** - `confirmed`
5. **Proposed action** - `fix`
6. **Why** - A direct rule-based safety correction was required and was minimized to a single volume change.

## Candidate 3
1. **Observed area** - unresolved remote resource loading during bounded browser pass
2. **Static evidence** - No specific broken path was isolated from source during the bounded pass.
3. **Browser evidence** - Verification pass still showed three generic `404` console messages without source detail.
4. **Confidence classification** - `uncertain`
5. **Proposed action** - `leave_as_is`
6. **Why** - The remaining evidence was too weak to justify another application edit.