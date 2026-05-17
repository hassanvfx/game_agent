# Delta Issue Ledger

## Candidate 1
1. **Observed area** - `index.html` audio bootstrap and start/game-over audio flow
2. **Static evidence** - `ASSETS.bgm`, `ASSETS.sfx.start`, and `ASSETS.sfx.fail` referenced remote URLs that were used by the initial runtime.
3. **Browser evidence** - Initial Playwright pass recorded `404` responses for `music_loop_02.mp3`, `start_game_01.mp3`, and `game_over_02.mp3`; post-fix verification recorded zero failed responses and zero console/runtime errors.
4. **Confidence classification** - `confirmed`
5. **Proposed action** - `fix`
6. **Why** - broken remote audio requests were directly observed and a minimal approved-URL swap resolved them.

## Candidate 2
1. **Observed area** - `index.html` looping background music volume
2. **Static evidence** - `this.bgm.volume = 0.24;` exceeded the required 20% cap for continuous looping audio.
3. **Browser evidence** - BGM is configured as a loop and starts from the main gameplay flow, so the cap applies at runtime.
4. **Confidence classification** - `confirmed`
5. **Proposed action** - `fix`
6. **Why** - the rule is explicit and the one-line volume reduction is minimal.

## Candidate 3
1. **Observed area** - mobile touch drawing and scoring flow
2. **Static evidence** - touch listeners were already wired for `touchstart`, `touchmove`, and `touchend`.
3. **Browser evidence** - Post-fix mobile pass successfully started the game, drew a rail, and advanced score from `0` to `1`.
4. **Confidence classification** - `uncertain`
5. **Proposed action** - `leave_as_is`
6. **Why** - the bounded browser pass did not confirm a defect in the touch gameplay loop.
