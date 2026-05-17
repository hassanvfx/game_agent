# Delta Issue Ledger

## Candidate 1
1. **Observed area** - `index.html` / audio preload and SFX playback flow
2. **Static evidence** - `AudioManager.loadSound()` used `fetch(src)` plus `decodeAudioData()` for remote approved audio URLs, which causes cross-origin fetch failure when served from localhost; `playBgm()` also set looping ambience volume to `0.24`, above the required 20% cap.
3. **Browser evidence** - Pre-fix Playwright console output showed CORS blocks for remote audio files and fallback activation conditions; post-fix verification removed those CORS errors while gameplay still advanced correctly on mobile.
4. **Confidence classification** - `confirmed`
5. **Proposed action** - `fix`
6. **Why** - Confirmed runtime audio integration defect with a small, targeted remedy and a required audio safety adjustment.

## Candidate 2
1. **Observed area** - `index.html` / mobile start-to-play flow
2. **Static evidence** - Canvas pointer handling is scoped to the playfield and start/restart actions are attached to explicit buttons.
3. **Browser evidence** - In the bounded mobile pass, tapping start hid the menu and a hold on the canvas increased progress to `22%`.
4. **Confidence classification** - `confirmed`
5. **Proposed action** - `leave_as_is`
6. **Why** - Mobile gameplay mechanics were preserved and no interaction break was confirmed.

## Candidate 3
1. **Observed area** - runtime resource loading / remaining generic `404` console messages
2. **Static evidence** - The bounded review did not isolate a specific in-workspace source line causing the four remaining generic `404` messages.
3. **Browser evidence** - Post-fix console output still showed four non-specific `404` resource failures, but no correlated gameplay or UI breakage appeared in the bounded pass.
4. **Confidence classification** - `uncertain`
5. **Proposed action** - `monitor_only`
6. **Why** - The remaining errors were not sufficiently source-grounded to justify additional edits.