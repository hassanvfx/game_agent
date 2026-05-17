# Delta Issue Ledger

## Candidate Issue 1
- **Observed area**: `index.html` / audio system / looping background music volume
- **Static evidence**: `soundVolumes.bgm` was set to `0.28`, which exceeds the required 20% maximum for looping or long-running audio.
- **Browser evidence**: The bounded Playwright pass verified runtime identity and normal play flow, but did not need to rely on audible playback to confirm this issue because the safety rule is explicit and code-visible.
- **Confidence classification**: `confirmed`
- **Proposed action**: `fix`
- **Why**: The looped BGM volume violated the explicit audio safety guardrail and could be corrected with a one-line minimal patch.

## Candidate Issue 2
- **Observed area**: start flow, HUD visibility, tap-to-jump mobile interaction, short run lifecycle
- **Static evidence**: The code wires the start button, HUD toggle, pointer input on the canvas, and game-over transitions in a coherent way.
- **Browser evidence**: Runtime identity passed; HUD became visible after start; score advanced; canvas tap was accepted; the bounded run later reached game-over without console errors.
- **Confidence classification**: `confirmed`
- **Proposed action**: `leave_as_is`
- **Why**: Browser-grounded evidence supported correct behavior, so no gameplay/application patch was justified.

## Candidate Issue 3
- **Observed area**: broader gameplay balance and platform generation feel
- **Static evidence**: Procedural gaps and heights are randomized, but nothing in the code alone proves unfairness or dead states.
- **Browser evidence**: The bounded pass was intentionally short and did not produce enough evidence for a fairness or progression defect.
- **Confidence classification**: `uncertain`
- **Proposed action**: `monitor_only`
- **Why**: The evidence-first policy does not support speculative gameplay tuning.