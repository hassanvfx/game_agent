# Delta Issue Ledger

## 1. AudioManager remote SFX preload path
- **Observed area** - `index.html` / `AudioManager.loadBuffer()` and `AudioManager.playSfx()`
- **Static evidence** - non-BGM sounds were preloaded with `fetch(src)` and decoded into Web Audio buffers even when the sources were approved remote URLs on another origin
- **Browser evidence** - baseline Playwright pass recorded a CORS console error when loading `https://gamezone-virid.vercel.app/assets/audios/ui/start_game_02.mp3`; post-fix pass no longer showed that audio CORS error
- **Confidence classification** - `confirmed`
- **Proposed action** - `fix`
- **Why** - cross-origin fetch-based SFX preload failed in the local served runtime and a minimal fallback path existed

## 2. Looping background music volume cap
- **Observed area** - `index.html` / `AudioManager.init()`
- **Static evidence** - looped BGM volume was set to `0.3`
- **Browser evidence** - bounded pass confirmed the looped BGM element exists and is used as continuous background audio; the node policy caps looped audio at `20%`
- **Confidence classification** - `confirmed`
- **Proposed action** - `fix`
- **Why** - policy-required safety correction with a one-line minimal patch

## 3. Remaining generic 404 console errors
- **Observed area** - runtime resource loading outside clearly identified gameplay code
- **Static evidence** - no bounded static source was identified from the workspace during this pass
- **Browser evidence** - post-fix Playwright pass still recorded two generic `404` console entries, but no visible gameplay, layout, or input regression was observed
- **Confidence classification** - `uncertain`
- **Proposed action** - `leave_as_is`
- **Why** - evidence was insufficient to justify a conservative in-workspace patch without risking unrelated changes