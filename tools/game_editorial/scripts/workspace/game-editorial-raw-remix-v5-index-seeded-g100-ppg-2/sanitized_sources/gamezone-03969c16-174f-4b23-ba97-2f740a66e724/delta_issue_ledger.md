# Delta Issue Ledger

## 1. HUD age bar color utility
- **Observed area** - `index.html` / HUD time bar styling
- **Static evidence** - `#age-bar` used class `bg-yellow-600`, but the utility CSS did not define `.bg-yellow-600`.
- **Browser evidence** - Playwright runtime logged: `Failed to execute 'addColorStop' on 'CanvasGradient': The value provided ('undefined') could not be parsed as a color.`
- **Confidence classification** - confirmed
- **Proposed action** - fix
- **Why** - Missing utility class directly caused runtime color resolution failure.

## 2. Looping background music volume
- **Observed area** - `index.html` / audio initialization
- **Static evidence** - Looping BGM was initialized with `audio.volume = 0.3`.
- **Browser evidence** - No gameplay breakage required to confirm; this violated the explicit audio safety rule for looping audio.
- **Confidence classification** - confirmed
- **Proposed action** - fix
- **Why** - Required safety guardrail caps looping audio at 20%.

## 3. Remote audio CORS failures
- **Observed area** - remote audio fetches from approved catalog URLs
- **Static evidence** - Audio uses approved remote URLs hosted on `gamezone-virid.vercel.app`.
- **Browser evidence** - Browser console reported CORS blocking for several audio files when served from localhost.
- **Confidence classification** - likely
- **Proposed action** - leave_as_is
- **Why** - Root cause is remote host CORS headers outside the editable workspace.

## 4. Action button click interception during automation
- **Observed area** - mobile HUD controls
- **Static evidence** - Joystick and action controls occupy separate visual regions.
- **Browser evidence** - Playwright pointer click retries were intercepted by the joystick subtree, but a DOM-dispatched action click succeeded.
- **Confidence classification** - uncertain
- **Proposed action** - monitor_only
- **Why** - Evidence suggests an automation hit-target artifact rather than a confirmed player-facing mobile failure.
