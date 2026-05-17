# Delta Issue Ledger

## 1. HUD hidden after starting a run
- **Observed area** - `index.html` / HUD visibility / start-to-play transition
- **Static evidence** - `.hud` sets `display: none;` and `startRun()` only removes the `hidden` class, so the HUD can remain invisible even when gameplay starts
- **Browser evidence** - pre-fix Playwright pass showed `hud visible=false, score visible=false` after pressing Start; post-fix pass showed `hud visible=true, score visible=true`
- **Confidence classification** - `confirmed`
- **Proposed action** - `fix`
- **Why** - directly blocked visible gameplay status on mobile runtime

## 2. Looping background music above safety cap
- **Observed area** - `index.html` / `AudioController` / looping BGM configuration
- **Static evidence** - `this.bgm.loop = true;` and `this.bgm.volume = 0.22;`, which exceeds the required 20% maximum for looping audio
- **Browser evidence** - not required for this policy-only safety issue; audio guardrail explicitly applies on static inspection
- **Confidence classification** - `confirmed`
- **Proposed action** - `fix`
- **Why** - required compliance adjustment with a minimal one-line change

## 3. Generic remote resource 404 errors
- **Observed area** - remote media/font/audio loading
- **Static evidence** - page depends on multiple external URLs for fonts, GIFs, and audio
- **Browser evidence** - `playwright_console_errors.json` recorded 5 generic `404` resource errors, but the console text did not expose the exact failing URLs
- **Confidence classification** - `uncertain`
- **Proposed action** - `monitor_only`
- **Why** - evidence was insufficient to identify a specific safe minimal replacement in this pass