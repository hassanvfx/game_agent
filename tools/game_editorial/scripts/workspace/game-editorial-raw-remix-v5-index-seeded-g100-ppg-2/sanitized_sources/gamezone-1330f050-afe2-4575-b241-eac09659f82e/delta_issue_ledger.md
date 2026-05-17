# Delta Issue Ledger

## Candidate 1
- **Observed area**: `index.html` select-state starting hub tap flow
- **Static evidence**: `Game.onDown()` assigns `Game.selection` and `UI.update()` enables `#btn-start` when a valid node polygon is hit during `SELECT`.
- **Browser evidence**: Runtime identity passed. In the bounded mobile pass, the initial screen rendered correctly, but one tap attempt did not enable the start button. No console/runtime errors were observed. The evidence does not prove that the tap landed on a valid node polygon.
- **Confidence classification**: `uncertain`
- **Proposed action**: `leave_as_is`
- **Why**: The observed behavior is inconclusive and does not justify a gameplay/application code edit.

## Candidate 2
- **Observed area**: `index.html` looping audio configuration
- **Static evidence**: `CATALOG_MEDIA.loops` sets loop volumes to `0.22`, `0.18`, and `0.2`.
- **Browser evidence**: The bounded pass did not establish a confirmed runtime audio failure, but the first loop entry exceeds the required 20% cap for looping audio.
- **Confidence classification**: `confirmed`
- **Proposed action**: `fix`
- **Why**: Looping audio above the hard 20% safety cap must be reduced.