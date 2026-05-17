# Delta Issue Ledger

## Issue 1
1. **Observed area** - `index.html` audio loading for start/game-over UI one-shots
2. **Static evidence** - `audio.load()` fetched remote audio into Web Audio buffers only; if decode fetch fails, `audio.play()` returned early with no fallback path.
3. **Browser evidence** - Playwright run on http://127.0.0.1:49155/index.html captured console errors showing CORS failures for `game_over_02.mp3` and `start_game_02.mp3`, while the rest of the UI loaded and interacted normally.
4. **Confidence classification** - confirmed
5. **Proposed action** - fix
6. **Why** - a minimal fallback preserves intended one-shot audio when Web Audio buffer loading is blocked.

## Issue 2
1. **Observed area** - mobile start screen, HUD, controls, and initial attack flow
2. **Static evidence** - touch controls, state transitions, and HUD toggles are wired directly in `startGame()` and the input setup.
3. **Browser evidence** - start screen rendered, ENTER ARCHIVE exposed HUD/controls, and a bounded STRIKE tap produced no gameplay-blocking failure.
4. **Confidence classification** - uncertain
5. **Proposed action** - leave_as_is
6. **Why** - the bounded pass did not confirm a defect in core flow or layout.
