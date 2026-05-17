# Delta Issue Ledger

## Issue 1
1. **Observed area** - `index.html` / startup playback flow / `vn2_scenes` media references
2. **Static evidence** - The page references `vn2_scenes/poster.jpg` in CSS and video poster markup, initializes the video with `src="vn2_scenes/scene1.mp4"`, and later advances through `vn2_scenes/scene2.mp4` through `vn2_scenes/scene6.mp4`.
3. **Browser evidence** - Runtime identity verification passed, but after tapping the start gate the first choice never appeared. Playwright evidence showed `#V.currentSrc` resolving to `http://127.0.0.1:56894/vn2_scenes/scene1.mp4`, `#V.currentTime` staying at `0`, `HEAD /vn2_scenes/scene1.mp4` returning `404`, and the local server log showing `GET /vn2_scenes/poster.jpg` and `GET /vn2_scenes/scene1.mp4` returning `404`. Supporting screenshots: `playwright_initial.png`, `playwright_broken_state.png`.
4. **Confidence classification** - `confirmed`
5. **Proposed action** - `leave_as_is`
6. **Why** - The defect is real, but the missing story media cannot be conservatively repaired from the approved catalog sources because no approved replacement video set exists in the workspace catalogs.

## Issue 2
1. **Observed area** - `index.html` / looping ambience safety
2. **Static evidence** - `audioBank.ambience.loop = true;` and `audioBank.ambience.volume = 0.22;`
3. **Browser evidence** - The bounded pass did not produce an audio-specific runtime failure, but the looped ambience volume exceeds the required 20% cap in code.
4. **Confidence classification** - `confirmed`
5. **Proposed action** - `fix`
6. **Why** - This is a minimal, isolated, policy-required adjustment with no dependency on the missing scene media.