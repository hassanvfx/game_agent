# Delta Issue Ledger

## Candidate 1

1. **Observed area** - `index.html` / audio initialization
2. **Static evidence** - `AudioSys.makeAudio()` set `audio.crossOrigin = 'anonymous'` on approved remote audio URLs.
3. **Browser evidence** - The initial Playwright pass produced CORS failures for approved remote audio URLs. After removing that assignment, the bounded replay no longer showed those audio CORS failures and core gameplay interactions still worked.
4. **Confidence classification** - confirmed
5. **Proposed action** - fix
6. **Why** - Removing the unnecessary cross-origin setting is the smallest targeted patch for the confirmed audio loading issue.

## Candidate 2

1. **Observed area** - `index.html` / core mobile controls
2. **Static evidence** - Pointer tap and drag logic are present and consistent with the intended interaction model.
3. **Browser evidence** - The bounded replay showed successful transition into `PLAYING`, successful tap-shot with projectile creation and cooldown, and successful drag movement with updated player position.
4. **Confidence classification** - uncertain
5. **Proposed action** - leave_as_is
6. **Why** - The replay failed to confirm a gameplay defect, so conservative policy requires no gameplay edit.

## Candidate 3

1. **Observed area** - remote media loading during replay
2. **Static evidence** - Some remote media requests still depend on external URLs outside the local workspace.
3. **Browser evidence** - The bounded replay still recorded two generic `404` console resource failures.
4. **Confidence classification** - uncertain
5. **Proposed action** - monitor_only
6. **Why** - The failing resources were not identified with strong enough evidence in this pass, and the observed gameplay path remained functional.