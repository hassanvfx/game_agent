# Delta Issue Ledger

## Candidate 1
1. **Observed area** - `index.html` audio asset mapping for start/fail/win SFX
2. **Static evidence** - `ASSETS.sfx.start`, `ASSETS.sfx.fail`, and `ASSETS.sfx.win` pointed at catalog-approved `*_02` URLs.
3. **Browser evidence** - Playwright captured repeated 404 responses for `start_game_02.mp3`, `game_over_02.mp3`, and `level_complete_02.mp3` while starting the run.
4. **Confidence classification** - confirmed
5. **Proposed action** - fix
6. **Why** - The SFX failed to load at runtime and broke intended audio feedback.

## Candidate 2
1. **Observed area** - `index.html` looping BGM volume
2. **Static evidence** - `this.bgm.volume` was set to `0.24`.
3. **Browser evidence** - No audible distortion was measured in-headless, but the configured loop volume exceeded the stage safety cap.
4. **Confidence classification** - confirmed
5. **Proposed action** - fix
6. **Why** - Looping audio must not exceed 20% volume under the node safety guardrail.

## Candidate 3
1. **Observed area** - Gameplay loss during bounded interaction
2. **Static evidence** - Hazards intentionally cause instant loss on collision.
3. **Browser evidence** - The bounded mobile run ended in game over after one food pickup and later hazard contact.
4. **Confidence classification** - uncertain
5. **Proposed action** - leave_as_is
6. **Why** - The observed loss matches the intended rules and does not independently prove a gameplay defect.
