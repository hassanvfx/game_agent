# Delta Issue Ledger

## 1. Looping background music exceeds required safety cap
- **Observed area**: `index.html` / `AudioSys.init()` / looping background audio
- **Static evidence**: `bgm_main` is assigned `bgm.volume = 0.3`, which exceeds the required maximum of 20% volume for looping/continuous audio.
- **Browser evidence**: bounded Playwright pass did not require a failure state to confirm this; the issue is directly grounded by code inspection and applies to the runtime when background music starts after tapping `START DRILL`.
- **Confidence classification**: `confirmed`
- **Proposed action**: `fix`
- **Why**: hard audio safety rule requires looping audio at 20% volume or lower.

## 2. Remote audio prefetch requests are blocked by CORS
- **Observed area**: `index.html` / `AudioSys.load()` remote audio fetch path
- **Static evidence**: `AudioSys.load()` fetches remote audio URLs through Web Audio decoding, which is subject to cross-origin response headers.
- **Browser evidence**: `playwright_console_errors.json` records CORS failures for remote audio URLs such as `level_complete_01.mp3` and `start_game_01.mp3`.
- **Confidence classification**: `likely`
- **Proposed action**: `leave_as_is`
- **Why**: gameplay remained functional in the bounded pass and the conservative policy does not justify a broader audio-system rewrite here.

## 3. Some remote media requests return 404
- **Observed area**: remote media loading during initial and early runtime
- **Static evidence**: remote GIF/audio URLs are external dependencies and some resources may no longer resolve.
- **Browser evidence**: `playwright_console_errors.json` includes repeated `Failed to load resource: the server responded with a status of 404 ()`.
- **Confidence classification**: `uncertain`
- **Proposed action**: `monitor_only`
- **Why**: the exact failing URLs were not isolated in this bounded pass, so a conservative code edit is not justified.