# Delta Issue Ledger

## Candidate 1
- **Observed area**: AudioController looping background music
- **Static evidence**: `this.bgm.volume = 0.2;` now satisfies the required 20% cap for looping audio after the minimal patch from 0.22.
- **Browser evidence**: Runtime identity verification passed and the normal Start flow reached the active game state where looping BGM is used.
- **Confidence classification**: confirmed
- **Proposed action**: fix
- **Why**: The only confirmed issue was the looping-audio safety cap, and it is now corrected with a one-line patch.

## Candidate 2
- **Observed area**: Start, paint, pause mobile flow
- **Static evidence**: Start button, pointer handlers, HUD, and pause handlers remain wired directly in code without extra edits.
- **Browser evidence**: Start screen, HUD, paint interaction, and pause overlay all behaved as expected in the bounded mobile pass.
- **Confidence classification**: confirmed
- **Proposed action**: leave_as_is
- **Why**: Browser evidence did not confirm any gameplay or layout defect in this flow.