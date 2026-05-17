# Delta Issue Ledger

## Issue 1
1. **Observed area** - `index.html` / audio preload flow
2. **Static evidence** - `AudioManager` used `fetch(el.src)` for remote SFX assets, which forces cross-origin fetches before playback.
3. **Browser evidence** - Pre-fix Playwright console showed CORS blocks for multiple remote audio URLs during the bounded mobile run.
4. **Confidence classification** - confirmed
5. **Proposed action** - fix
6. **Why** - minimal change can avoid the confirmed cross-origin failure path while preserving audio playback behavior.

## Issue 2
1. **Observed area** - remote non-audio resources
2. **Static evidence** - page references external font/GIF resources that may emit generic missing-resource noise depending on runtime availability.
3. **Browser evidence** - bounded pass still showed generic 404-style resource messages without a clear gameplay break.
4. **Confidence classification** - uncertain
5. **Proposed action** - leave_as_is
6. **Why** - evidence did not isolate a gameplay or application defect strong enough to justify more edits.
