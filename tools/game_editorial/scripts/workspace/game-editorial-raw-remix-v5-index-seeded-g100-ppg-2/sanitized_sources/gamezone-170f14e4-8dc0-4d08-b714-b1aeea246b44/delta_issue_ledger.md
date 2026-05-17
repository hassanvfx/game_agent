# Delta Issue Ledger

## Candidate 1
1. **Observed area** - `index.html` / audio manager / looping background music safety
2. **Static evidence** - `AudioManager.getContext()` set `this.bgmGain.gain.value = 0.28`, which exceeds the required maximum of 20% for looping audio.
3. **Browser evidence** - bounded Playwright pass verified the game starts in mobile context and uses looping BGM on first interaction; this made the safety-cap violation actionable rather than theoretical.
4. **Confidence classification** - `confirmed`
5. **Proposed action** - `fix`
6. **Why** - the node rules require looped audio to stay at 20% volume or lower.

## Candidate 2
1. **Observed area** - `index.html` / audio manager / remote audio playback path
2. **Static evidence** - remote SFX and music were fetched and decoded through Web Audio only, with no playback fallback when cross-origin decode fails.
3. **Browser evidence** - `playwright_console_errors.json` captured a confirmed CORS failure for `success_02.mp3` plus `net::ERR_FAILED`, while the rest of the game still ran.
4. **Confidence classification** - `confirmed`
5. **Proposed action** - `fix`
6. **Why** - a minimal HTMLAudio fallback improves resilience without changing gameplay behavior.

## Candidate 3
1. **Observed area** - core prep → charge → completion interaction flow
2. **Static evidence** - `interact()` correctly transitions `empty -> prepped -> cooking`, and `update()` advances `cooking -> done`.
3. **Browser evidence** - post-fix Playwright run observed the expected status sequence: order beamed in, charge started, cabinet charged.
4. **Confidence classification** - `confirmed`
5. **Proposed action** - `leave_as_is`
6. **Why** - the primary gameplay loop functioned correctly in the bounded mobile pass.

## Candidate 4
1. **Observed area** - remote media hosting quality outside gameplay logic
2. **Static evidence** - catalog-backed remote assets are externally hosted and not controlled inside the workspace.
3. **Browser evidence** - console still showed a CORS complaint and one remote `404` after the local code fallback patch.
4. **Confidence classification** - `uncertain`
5. **Proposed action** - `monitor_only`
6. **Why** - the remaining noise appears to originate from remote asset hosting behavior, not a clearly patchable local gameplay defect.