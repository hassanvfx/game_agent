# Delta Issue Ledger

| Observed area | Static evidence | Browser evidence | Confidence classification | Proposed action | Why |
|---|---|---|---|---|---|
| Start/game-over overlays in `index.html` | `.screen` used `pointer-events: auto`; hidden overlays stayed in layout and Playwright click was intercepted by the hidden game-over card. | Initial Playwright run timed out clicking `#btn-start` because the hidden `#game-over-screen` subtree intercepted pointer events. Post-fix run showed `startHidden=true` and `hudVisible=true`. | confirmed | fix | Hidden overlay blocked the primary start interaction on mobile. |
| Looping background music volume in `index.html` | `AudioSys.preload()` set looping BGM volume to `0.22`, above the required 20% cap. | Static-policy issue; browser pass did not contradict it. | confirmed | fix | Required audio safety guardrail caps looping audio at 20%. |
| Start/win/lose audio URLs in `index.html` | Selected approved catalog URLs returned 404 during preload. | Playwright captured 404 responses for start/win/lose audio during the first verification pass. Verified replacements were switched to approved working catalog URLs. | confirmed | fix | Broken audio fetches caused runtime console errors and missing cues. |
