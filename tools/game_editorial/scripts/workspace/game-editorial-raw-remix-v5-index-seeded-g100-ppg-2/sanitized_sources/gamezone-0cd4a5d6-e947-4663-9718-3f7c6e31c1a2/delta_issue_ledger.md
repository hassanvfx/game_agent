# Delta Issue Ledger

## Candidate 1
- **Observed area**: start screen launch button / mobile interaction flow
- **Static evidence**: start button sits inside `.panel-start` which continuously animates with `animation: float 3s ease-in-out infinite;`
- **Browser evidence**: initial Playwright click reported the button as unstable during the bounded pass; forced click launched the run successfully, HUD became visible, and score advanced.
- **Confidence classification**: uncertain
- **Proposed action**: leave_as_is
- **Why**: evidence points to automation sensitivity from continuous animation, not a confirmed user-facing gameplay defect.