# Delta Issue Ledger

## Candidate 1
1. **Observed area** - `index.html` / sleep interaction / HUD stat refresh
2. **Static evidence** - In the sleep button timeout, `stats.hunger` and `stats.fun` were reduced but `updateStatsUI()` was not called before returning to the hub flow.
3. **Browser evidence** - `playwright_sleep_overlay.png` and `playwright_observation_log.md` captured the sleep flow. After the overlay closed, the HUD bar widths still read 50% for hunger and fun instead of dropping to 40%, confirming a visible desync.
4. **Confidence classification** - confirmed
5. **Proposed action** - fix
6. **Why** - The UI failed to reflect the already-applied stat change until a later unrelated update.

## Candidate 2
1. **Observed area** - `index.html` / launch and state transitions
2. **Static evidence** - Start screen, pet selection, hub controls, and race entry flows are wired directly through button handlers and `setGameState`.
3. **Browser evidence** - `playwright_initial.png`, `playwright_after_pet_select.png`, and `playwright_race_state.png` showed the expected title screen, hub transition, and race instruction state.
4. **Confidence classification** - confirmed
5. **Proposed action** - leave_as_is
6. **Why** - The bounded mobile pass did not reveal a defect in those flows.