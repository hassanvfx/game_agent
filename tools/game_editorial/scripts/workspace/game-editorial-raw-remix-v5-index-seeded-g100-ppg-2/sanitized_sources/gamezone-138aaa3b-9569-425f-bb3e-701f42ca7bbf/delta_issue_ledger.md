# Delta Issue Ledger

## Candidate 1
- **Observed area**: `index.html` / looping background music volume safety
- **Static evidence**: `AudioController` initialized `this.bgm.volume = 0.26`, which exceeded the node guardrail cap for looping audio.
- **Browser evidence**: Bounded Playwright pass confirmed the game starts successfully in mobile mode; this issue is safety-related rather than a visible flow break.
- **Confidence classification**: confirmed
- **Proposed action**: fix
- **Why**: Looping audio must not exceed 20% volume.

## Candidate 2
- **Observed area**: `index.html` / remote audio asset loading
- **Static evidence**: `ASSETS.bgm`, `ASSETS.sfx.uiStart`, and `ASSETS.sfx.fail` point to approved catalog-style remote URLs under `gamezone-virid.vercel.app`.
- **Browser evidence**: Playwright captured repeated `404` responses for `music_loop_02.mp3`, `start_game_02.mp3`, and `game_over_01.mp3` in `playwright_network_failures.json` and matching console errors in `playwright_console_errors.json`.
- **Confidence classification**: confirmed
- **Proposed action**: monitor_only
- **Why**: The failure is real, but no alternate approved reachable remote audio URL was established during this bounded pass, so a compliant minimal replacement could not be justified.

## Candidate 3
- **Observed area**: start flow / mobile gameplay interaction
- **Static evidence**: Start and restart controls already include click and touchend handlers, and gameplay tap/drop flow is directly wired on `#game-container`.
- **Browser evidence**: Runtime identity verification passed, the start button entered gameplay, HUD became visible, and a first drop succeeded in the required mobile context.
- **Confidence classification**: confirmed
- **Proposed action**: leave_as_is
- **Why**: The bounded mobile pass supported the existing interaction flow.