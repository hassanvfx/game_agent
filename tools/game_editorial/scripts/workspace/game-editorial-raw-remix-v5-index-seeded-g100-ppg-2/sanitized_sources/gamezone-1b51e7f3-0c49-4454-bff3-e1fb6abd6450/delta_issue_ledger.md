# Delta Issue Ledger

## Candidate 1
- **Observed area**: `index.html` / AudioSys looping background music setup
- **Static evidence**: `AudioSys.init()` sets `bgm.volume = 0.24` for a looping background track.
- **Browser evidence**: Runtime check observed looping BGM volume at 0.24 during the bounded Playwright pass; screenshots are trusted after identity verification passed.
- **Confidence classification**: confirmed
- **Proposed action**: fix
- **Why**: Looping background audio exceeds the required 20% maximum volume.

## Candidate 2
- **Observed area**: Core interaction flow / Shift and Shop buttons
- **Static evidence**: Button handlers are wired on `DOMContentLoaded` and call `handleAction(...)` / `toggleShop()`.
- **Browser evidence**: After tapping Shift, money drops count was 4. After tapping Shop, modal visible=true, food=3, money=50.
- **Confidence classification**: confirmed
- **Proposed action**: leave_as_is
- **Why**: Bounded pass showed expected behavior for these interactions and no minimal fix is justified.