# Delta Issue Ledger

## Candidate 1
- **Observed area** - AudioManager looping background music volume
- **Static evidence** - `configureLevels()` and `startLoop()` originally set `bgm.volume = 0.24`, above the 20% safety cap for looping audio; they were reduced to `0.2` in the minimal patch.
- **Browser evidence** - The bounded Playwright pass confirmed runtime identity, reproduced the game on mobile, and the pre-fix observation recorded looping audio volume above the cap.
- **Confidence classification** - confirmed
- **Proposed action** - fix
- **Why** - Looping audio exceeded the required hard cap and was corrected with a two-line change.

## Candidate 2
- **Observed area** - General gameplay flow
- **Static evidence** - Input, spawn, collision, HUD, and restart flow appear internally consistent in the inspected code.
- **Browser evidence** - Bounded mobile passes showed the game loading, responding to tap input, and entering ordinary gameplay/game-over states without a separate clearly reproducible logic defect.
- **Confidence classification** - uncertain
- **Proposed action** - leave_as_is
- **Why** - No clearly confirmed gameplay defect beyond the audio safety violation.