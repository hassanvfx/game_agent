# Delta Issue Ledger

## Candidate 1
1. **Observed area** - `index.html` audio startup and local browser-grounded launch flow
2. **Static evidence** - `AUDIO_MAP` used remote audio URLs and `Sfx.init()` instantiated `Audio(...)` for startup sounds; looped `bgm` volume was set to `0.22`, above the allowed 20% cap
3. **Browser evidence** - initial Playwright pass reproduced console errors during `OPEN LOT`; prior `playwright_console_errors.json` recorded a CORS block for `start_game_02.mp3`; post-fix pass showed `consoleErrorsCount: 0`
4. **Confidence classification** - confirmed
5. **Proposed action** - fix
6. **Why** - a real browser-grounded local launch produced observable audio failure/noise, and the volume cap also required correction

## Candidate 2
1. **Observed area** - start screen, HUD reveal, spawn flow, and reset flow
2. **Static evidence** - `bootGame()`, spawn button handler, and reset button handler were internally consistent and already wired correctly
3. **Browser evidence** - Playwright verified title screen rendering, `WRECKS: 3` after start, `WRECKS: 4` after spawn, and `WRECKS: 0` after reset with no final console/runtime errors
4. **Confidence classification** - confirmed
5. **Proposed action** - leave_as_is
6. **Why** - bounded runtime evidence supported the existing mechanics and UI flow

## Candidate 3
1. **Observed area** - drag-and-throw touch interaction
2. **Static evidence** - touch listeners and drag handlers were present, but throw velocity calculation remains lightweight and was not deeply exercised in the final bounded pass
3. **Browser evidence** - the final pass focused on the clearly observed audio defect and core HUD actions; no strong broken-state evidence was gathered for touch dragging
4. **Confidence classification** - uncertain
5. **Proposed action** - monitor_only
6. **Why** - no confirmed defect was established, so conservative policy requires no gameplay edit