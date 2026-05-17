# Delta Issue Ledger

## 1. Remote audio startup loading
- **Observed area** - `index.html` audio initialization on start flow
- **Static evidence** - non-BGM sound effects were fetched and decoded through `fetch(el.src)` and `decodeAudioData`, which requires CORS access for cross-origin media
- **Browser evidence** - Playwright console recorded cross-origin audio fetch failure during `GO LIVE`; the gameplay UI still opened, but startup audio loading emitted runtime errors
- **Confidence classification** - confirmed
- **Proposed action** - fix
- **Why** - direct HTML audio playback avoids the cross-origin fetch failure with a minimal localized patch

## 2. Mixed title naming
- **Observed area** - document title versus in-screen branding
- **Static evidence** - `<title>` is `Neon Signal Factory` while the hero text and identity artifact say `Signal Sprinter`
- **Browser evidence** - runtime identity still matched the workspace through both signals and did not create a broken flow
- **Confidence classification** - uncertain
- **Proposed action** - leave_as_is
- **Why** - naming mismatch is cosmetic and not clearly a confirmed defect in this bounded pass
