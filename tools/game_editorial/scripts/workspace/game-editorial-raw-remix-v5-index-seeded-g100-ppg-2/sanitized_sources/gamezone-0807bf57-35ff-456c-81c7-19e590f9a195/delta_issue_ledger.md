# Delta Issue Ledger

## Candidate 1
- **Observed area** - `index.html` startup / Three.js player geometry initialization
- **Static evidence** - The code instantiated `new THREE.CapsuleGeometry(...)` while the page loads Three.js r128, where that constructor is unavailable in this runtime.
- **Browser evidence** - First bounded Playwright pass recorded `TypeError: THREE.CapsuleGeometry is not a constructor`, and the HUD remained hidden after Start Route because script execution aborted before start-flow handlers completed.
- **Confidence classification** - confirmed
- **Proposed action** - fix
- **Why** - Minimal geometry fallback restores startup without redesigning gameplay.

## Candidate 2
- **Observed area** - `index.html` looping background music volume
- **Static evidence** - Background music volume was set to `0.23`, above the node safety cap for looping audio.
- **Browser evidence** - Audio was not audibly inspected in headless Playwright, but this is a direct code-level safety violation under the task guardrail.
- **Confidence classification** - confirmed
- **Proposed action** - fix
- **Why** - Reducing loop volume to `0.2` is a minimal safety-only correction.

## Candidate 3
- **Observed area** - remote font / media requests
- **Static evidence** - The page references external font/media URLs that can return non-200 responses depending on environment.
- **Browser evidence** - Playwright observed HTTP 404 failures for remote resources, but the final bounded pass still launched the game and accepted mobile HUD input.
- **Confidence classification** - uncertain
- **Proposed action** - leave_as_is
- **Why** - The bounded evidence did not show a clearly confirmed gameplay defect caused by these requests.
