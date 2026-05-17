# Delta Issue Ledger

| Observed area | Static evidence | Browser evidence | Confidence classification | Proposed action | Why |
|---|---|---|---|---|---|
| `index.html` audio asset mapping (`ASSETS.sfx.start`, `ASSETS.sfx.fail`) | The file referenced `.../ui/start_game_01.mp3` and `.../ui/game_over_02.mp3`. | Playwright recorded repeated 404 request failures for those exact URLs in `playwright_console_errors.json`. | confirmed | fix | Broken remote audio requests were directly observed at runtime. |
| `index.html` looping BGM volume | `AudioController` created looped BGM with `volume: 0.24`. | Static-only policy check; no runtime error needed because the node requires looped audio at or below 20%. | confirmed | fix | The configured loop volume exceeded the required 20% ceiling. |
| HUD visibility / rapid post-start failure | `startRun()` removes `hidden` from HUD before `initGame()` and `gameLoop()`, with no obvious single-line regression. | After the bounded pass, `hudVisible=false` and one jump later `gameOverVisible=true`, but the run was not investigated beyond the bounded interaction script. | uncertain | leave_as_is | Evidence was insufficient to justify a gameplay logic patch under the conservative policy. |
