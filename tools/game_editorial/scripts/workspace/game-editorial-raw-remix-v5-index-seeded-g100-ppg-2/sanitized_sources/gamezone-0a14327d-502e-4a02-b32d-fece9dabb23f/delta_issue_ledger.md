# Delta Issue Ledger

## Candidate 1
- **Observed area** - `index.html` / mobile canvas layout / gameplay interaction region
- **Static evidence** - `#game-container` relied on utility sizing only and had no explicit viewport-height rule, while the canvas depended on its observed container size.
- **Browser evidence** - Initial mobile Playwright pass recorded canvas bounds of `400 x 200` in `playwright_runtime_evidence.json`; `playwright_initial_state.png` showed constrained gameplay space; after the minimal CSS fix, the canvas measured `400 x 700` and the room interaction probe succeeded with modal title `CLINIC 1` in `playwright_probe.json`.
- **Confidence classification** - `confirmed`
- **Proposed action** - `fix`
- **Why** - The mobile playfield was clearly undersized and directly affected reliable room interaction.

## Candidate 2
- **Observed area** - `index.html` / looping background audio level
- **Static evidence** - `audioLevels.bgm` was `0.22`, exceeding the required 20% cap for looping audio.
- **Browser evidence** - No contradictory runtime behavior; this is a direct code-level compliance issue tied to a hard safety rule.
- **Confidence classification** - `confirmed`
- **Proposed action** - `fix`
- **Why** - The project must keep looped background audio at `0.2` or lower.

## Candidate 3
- **Observed area** - `index.html` / room tap targeting during automated probing
- **Static evidence** - The first scripted tap used a coarse position that was not centered on the left-side room after the first build.
- **Browser evidence** - The early bounded pass reported `modalVisible: false`, but the refined in-canvas probe later opened the modal successfully without further gameplay code changes.
- **Confidence classification** - `uncertain`
- **Proposed action** - `leave_as_is`
- **Why** - The negative result was attributable to probe targeting rather than a confirmed gameplay defect after the viewport fix.