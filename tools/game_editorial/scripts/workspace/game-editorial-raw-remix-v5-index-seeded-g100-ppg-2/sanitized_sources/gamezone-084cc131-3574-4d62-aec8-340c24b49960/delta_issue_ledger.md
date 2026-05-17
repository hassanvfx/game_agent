# Delta Issue Ledger

## 1. Looping background music volume cap
- **Observed area** - `index.html` / AudioManager background loop handling
- **Static evidence** - `bgm.volume` was set to `0.32` in both initialization and playback paths.
- **Browser evidence** - No direct audible verification in headless mode, but the code path was exercised during launch and unlock flow.
- **Confidence classification** - confirmed
- **Proposed action** - fix
- **Why** - Node policy requires looping or long-running audio to stay at 20% volume or lower.

## 2. Remote one-shot audio CORS failures
- **Observed area** - `index.html` / remote SFX playback from approved catalog URLs
- **Static evidence** - Sound effects are instantiated from remote `gamezone-virid.vercel.app` URLs using `new Audio(url)`.
- **Browser evidence** - Playwright console captured CORS-blocked audio requests and `net::ERR_FAILED` during playback attempts.
- **Confidence classification** - confirmed
- **Proposed action** - leave_as_is
- **Why** - The failure is caused by remote server response headers; no minimal compliant workspace-only patch could restore those cross-origin files without violating the conservative edit policy.

## 3. Bounded swipe attempt did not score
- **Observed area** - gameplay interaction / scrub overlap during automated pass
- **Static evidence** - Cleaning requires both movement above threshold and dish overlap, which the short scripted path may not satisfy.
- **Browser evidence** - Score stayed at 0 during the bounded automated swipe, but the game continued and then reached normal game over.
- **Confidence classification** - uncertain
- **Proposed action** - monitor_only
- **Why** - The automated path was not source-grounded enough to prove a gameplay defect.
