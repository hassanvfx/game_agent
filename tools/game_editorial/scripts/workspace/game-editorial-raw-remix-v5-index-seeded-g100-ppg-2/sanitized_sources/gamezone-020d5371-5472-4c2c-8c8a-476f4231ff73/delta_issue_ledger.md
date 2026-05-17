# Delta Issue Ledger

## Candidate 1
1. **Observed area** - index.html / looping background music safety
2. **Static evidence** - AudioManager.playBgm set `bgm_battle` volume to `0.22`, which exceeded the required 20% cap for continuous looping audio.
3. **Browser evidence** - The bounded Playwright pass confirmed the runtime identity and normal start/pause flow, so this safety issue was evaluated against the actual served workspace build rather than an unrelated runtime.
4. **Confidence classification** - confirmed
5. **Proposed action** - fix
6. **Why** - A hard policy violation had a one-line minimal fix.

## Candidate 2
1. **Observed area** - index.html / start and pause flow
2. **Static evidence** - Event handlers wire Deploy and Pause directly to `startGame()` and `togglePause()`.
3. **Browser evidence** - `playwright_after_start.png` showed the HUD after Deploy, and `playwright_pause_state.png` showed the pause overlay with the expected Paused title.
4. **Confidence classification** - confirmed
5. **Proposed action** - leave_as_is
6. **Why** - The bounded mobile pass did not reproduce a gameplay or UI break in these flows.
