# Delta Issue Ledger

## Candidate 1
- **Observed area**: `index.html` / mobile playfield interaction / HUD overlay
- **Static evidence**: `#ui-layer > * { pointer-events: auto; }` allowed the full-screen `#ui-main` wrapper to receive pointer events across the entire playfield, while the global input handler expected non-button taps to pass through to the canvas.
- **Browser evidence**: Pre-fix Playwright mobile click on `canvas#gameCanvas` timed out with `#ui-main` reported as intercepting pointer events; after setting `#ui-main { pointer-events: none; }`, bounded mobile taps completed and score increased from `0` to `360` then `560`.
- **Confidence classification**: confirmed
- **Proposed action**: fix
- **Why**: It directly blocked primary gameplay input on mobile.

## Candidate 2
- **Observed area**: `index.html` / looping background audio safety
- **Static evidence**: `playBgm()` set looping track volume to `0.34` at night and `0.42` in calamity mode, exceeding the required 20% cap for continuous looped audio.
- **Browser evidence**: No runtime failure was required for confirmation because the safety rule is explicit and code-level values were above the allowed threshold.
- **Confidence classification**: confirmed
- **Proposed action**: fix
- **Why**: Continuous audio above the required cap violates the hard safety constraint.

## Candidate 3
- **Observed area**: `index.html` / bounded gameplay pass after minimal fix
- **Static evidence**: Weapon selection and global pointer input routing remained otherwise intact after the minimal pointer-event change.
- **Browser evidence**: Post-fix mobile pass showed runtime identity match, successful first tap feedback, successful CLUSTER selection, second tap resolution, and no console/page errors.
- **Confidence classification**: confirmed
- **Proposed action**: leave_as_is
- **Why**: The bounded pass did not support further defects that justified additional edits.