# Delta Issue Ledger

## 1. Broken remote UI audio sources
- **Observed area** - `index.html` audio asset map for fail/talk UI sounds
- **Static evidence** - `ASSETS.sfx.fail` referenced `.../ui/game_over_01.mp3` and `ASSETS.sfx.talk` referenced `.../ui/ui_hover_01.mp3`
- **Browser evidence** - initial Playwright pass logged four `404` resource failures; targeted URL checks confirmed both referenced files returned `404`
- **Confidence classification** - `confirmed`
- **Proposed action** - `fix`
- **Why** - broken media URLs created real runtime resource failures

## 2. Looping background music above safety cap
- **Observed area** - `index.html` audio initialization
- **Static evidence** - `this.bgm.loop = true` and `this.bgm.volume = 0.22`
- **Browser evidence** - no direct audible inspection in headless mode, but the configured value is explicit and exceeds the node's hard limit for looped audio
- **Confidence classification** - `confirmed`
- **Proposed action** - `fix`
- **Why** - policy requires looped audio at 20% volume or lower

## 3. Cutscene progression did not reach visible HUD during bounded taps
- **Observed area** - start-run to gameplay transition
- **Static evidence** - cutscene progression logic in `handleInput()` should eventually switch from `CUTSCENE` to `PLAYING` after the short `STORY_SCRIPT`
- **Browser evidence** - bounded mobile tap sequence kept the run in a cutscene-visible state and did not produce a HUD-visible gameplay screenshot
- **Confidence classification** - `uncertain`
- **Proposed action** - `leave_as_is`
- **Why** - browser evidence did not isolate a clear code defect, so a gameplay patch would be speculative