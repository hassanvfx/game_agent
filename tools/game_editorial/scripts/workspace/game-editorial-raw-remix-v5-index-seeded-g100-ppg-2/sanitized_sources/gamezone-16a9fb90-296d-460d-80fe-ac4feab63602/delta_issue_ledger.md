# Delta Issue Ledger

## Candidate Issue 1
- **Observed area**: index.html / looping background music volume
- **Static evidence**: initAudio() now sets bgm_main volume to 0.2, matching the looping-audio safety cap.
- **Browser evidence**: post-fix mobile verification pass reported bgm volume 0.2 after loading the local runtime.
- **Confidence classification**: confirmed
- **Proposed action**: fix
- **Why**: the minimal patch satisfies the hard looping-audio volume guardrail without changing gameplay flow
