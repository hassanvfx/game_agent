# Delta Issue Ledger

## Candidate 1
1. **Observed area** - `index.html` / looping background music safety
2. **Static evidence** - `syncBgmState()` and `boot()` both set `bgm.volume` to 0.48 for the looped BGM
3. **Browser evidence** - bounded mobile Playwright pass measured `#bgm.volume` at 0.48 after unlock; post-fix verification measured 0.2; screenshots: `playwright_after_unlock_tap.png`, `playwright_postfix_audio_check.png`
4. **Confidence classification** - confirmed
5. **Proposed action** - fix
6. **Why** - looped audio exceeded the explicit 20% safety cap

## Candidate 2
1. **Observed area** - mobile interaction loop / swap handling
2. **Static evidence** - pointerdown plus pointermove handlers support tap-select and drag-to-adjacent swap flows
3. **Browser evidence** - bounded swipe produced a live rejected move path with toast and fail GIF rather than a dead interaction; screenshot: `playwright_after_swipe.png`
4. **Confidence classification** - uncertain
5. **Proposed action** - leave_as_is
6. **Why** - bounded pass did not confirm a mechanics failure
