# Delta Issue Ledger

## Candidate Issue 1
- **Observed area**: Overall mobile start-to-play flow
- **Static evidence**: `index.html` wires start button, mobile pointer controls, HUD toggles, and victory/game-over overlays coherently.
- **Browser evidence**: Identity verification passed; start screen, gameplay HUD, and bounded touch interaction all behaved as expected across screenshots `playwright_initial.png`.
- **Confidence classification**: uncertain
- **Proposed action**: leave_as_is
- **Why**: No clearly confirmed gameplay, layout, or runtime defect was reproduced in the bounded pass.

## Candidate Issue 2
- **Observed area**: Looping background music volume safety
- **Static evidence**: `AudioController.soundProfiles.bgm_race` is set to `0.24`, which exceeds the required 20% cap for looping audio.
- **Browser evidence**: Audio playback was unlock-gated in the bounded pass, but the policy issue is directly confirmed by the configured loop volume value.
- **Confidence classification**: confirmed
- **Proposed action**: fix
- **Why**: The looped BGM volume is explicitly above the hard safety constraint and can be corrected with a one-line minimal patch.