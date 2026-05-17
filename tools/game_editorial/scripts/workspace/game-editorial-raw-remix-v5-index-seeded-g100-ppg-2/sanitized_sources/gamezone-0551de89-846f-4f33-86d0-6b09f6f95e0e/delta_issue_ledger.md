# Delta Issue Ledger

## Candidate 1
- **Observed area**: Mobile tap progression on game canvas
- **Static evidence**: `attachKickBallLogic` attached only a `click` listener to `app.canvas`, with no dedicated pointer/touch listener.
- **Browser evidence**: Initial Playwright mobile pass used a proper mobile touch context and the three tap sequence did not progress to a result or expose restart UI; after adding `pointerdown`, the bounded mobile tap flow advanced through start, power lock, and launch.
- **Confidence classification**: confirmed
- **Proposed action**: fix
- **Why**: Mobile interaction was not reliably wired to touch-first input events.

## Candidate 2
- **Observed area**: Remote media loading
- **Static evidence**: Some media URLs point to external resources and two 404 resource failures were observed during browser execution.
- **Browser evidence**: `playwright_console_errors.json` recorded two failed resource requests, but core game launch flow still ran after the mobile input fix.
- **Confidence classification**: uncertain
- **Proposed action**: monitor_only
- **Why**: The failing resources were not isolated strongly enough in this bounded pass to justify broader media edits.
