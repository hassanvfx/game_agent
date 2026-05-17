# Delta Issue Ledger

## Issue 1
1. **Observed area** - `index.html` / start-screen styling bootstrap
2. **Static evidence** - The page referenced `../../../../../../../../../../../games_top_gameplays/assets/cdn.tailwindcss.com/3.4.17.js`, which is outside the served workspace path.
3. **Browser evidence** - Pre-fix Playwright pass recorded `404 http://127.0.0.1:57224/games_top_gameplays/assets/cdn.tailwindcss.com/3.4.17.js`.
4. **Confidence classification** - confirmed
5. **Proposed action** - fix
6. **Why** - The utility CSS bootstrap could not load from the workspace server.

## Issue 2
1. **Observed area** - `index.html` / looping background music
2. **Static evidence** - `playBgm()` set `bgm.volume = 0.32`.
3. **Browser evidence** - Post-fix verification measured `bgm_main.volume` during play; this is a hard safety rule rather than a visual defect.
4. **Confidence classification** - confirmed
5. **Proposed action** - fix
6. **Why** - Looping audio exceeded the required 20% maximum.

## Issue 3
1. **Observed area** - `index.html` / UI click and fail audio sources
2. **Static evidence** - `sfx_ui` and `sfx_fail` used URLs that returned 404 in browser and HEAD checks.
3. **Browser evidence** - Pre-fix Playwright pass recorded 404s for `start_game_01.mp3` and `game_over_02.mp3`; final pass recorded no failed requests after replacement.
4. **Confidence classification** - confirmed
5. **Proposed action** - fix
6. **Why** - These sounds could not load at runtime.

## Issue 4
1. **Observed area** - core runner flow / start, HUD, touch jump
2. **Static evidence** - Input and HUD state logic in `startGame()` and `handleInput()` looked coherent.
3. **Browser evidence** - Runtime identity passed, HUD appeared after start, and touch input executed in the bounded mobile pass.
4. **Confidence classification** - confirmed
5. **Proposed action** - leave_as_is
6. **Why** - The bounded pass did not show a gameplay regression in these core interactions.
