# Delta Issue Ledger

## Candidate 1
- **Observed area**: index.html / audio system / looping background music volume
- **Static evidence**: `primeAudio(assets.bgm, 0.26);` sets looped BGM above the 20% cap.
- **Browser evidence**: observation log audio check recorded DOM volume 0.26, above the allowed 0.20 limit.
- **Confidence classification**: confirmed
- **Proposed action**: fix
- **Why**: hard safety guardrail requires looping audio at 20% volume or lower.

## Candidate 2
- **Observed area**: core choice flow / mobile interactions
- **Static evidence**: start, restart, and choice buttons use standard click handlers with touch-friendly styling.
- **Browser evidence**: start button and first story choice both responded in bounded mobile Playwright flow.
- **Confidence classification**: confirmed
- **Proposed action**: leave_as_is
- **Why**: bounded mobile interaction path functioned correctly.

