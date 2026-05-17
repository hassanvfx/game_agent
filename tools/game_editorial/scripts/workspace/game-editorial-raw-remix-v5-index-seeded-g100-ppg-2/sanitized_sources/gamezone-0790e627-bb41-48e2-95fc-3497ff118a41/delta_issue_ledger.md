# Delta Issue Ledger

## Candidate 1
1. **Observed area** - `index.html` audio asset mapping and audio controller loop settings
2. **Static evidence** - Several UI SFX URLs referenced `start_game_02`, `success_02`, `game_over_02`, and `level_complete_02`; loop volumes were set to `0.22` and `0.34`, exceeding the 20% cap for continuous audio.
3. **Browser evidence** - Initial bounded Playwright pass produced repeated 404 failures for those audio URLs in `playwright_failed_requests.json`; post-fix pass reported `consoleErrors: []` and `failed: []` in `playwright_runtime_summary.json`.
4. **Confidence classification** - `confirmed`
5. **Proposed action** - `fix`
6. **Why** - Missing approved audio resources and over-cap loop volumes were directly evidenced and could be corrected with a minimal audio-only patch.

## Candidate 2
1. **Observed area** - Start, roam, summon, and parry interaction flow
2. **Static evidence** - Core state transitions and control bindings were present in `index.html`.
3. **Browser evidence** - Runtime identity passed; controls became visible after `Begin Run`, boss HUD/parry became visible after `BREACH`, and the parry cooldown overlay updated after tapping `Parry`.
4. **Confidence classification** - `confirmed`
5. **Proposed action** - `leave_as_is`
6. **Why** - The bounded mobile pass supported the existing mechanics and did not reveal a confirmed gameplay or layout break in those flows.