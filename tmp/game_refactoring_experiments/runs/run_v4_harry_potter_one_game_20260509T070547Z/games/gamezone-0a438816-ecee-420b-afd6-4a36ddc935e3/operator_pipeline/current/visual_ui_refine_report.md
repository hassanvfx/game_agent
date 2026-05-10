# Visual UI Refine Report

## Runtime evidence used

Validation target:
- `http://127.0.0.1:43100/index.html`

Browser grounding:
- Playwright mobile context via `capture_baseline.js`
- Mobile size: `400x700`

Screenshots captured in workspace:
- `previsual_screen_01_title_or_entry.png`
- `previsual_screen_02_live_play.png`
- `previsual_screen_03_menu_or_modal.png`

Additional runtime note:
- `previsual_runtime_observation.json` recorded one existing page error: `TypeError: Cannot read properties of undefined (reading 'catch')`
- This refinement pass did not alter mechanics/audio flow to avoid risky logic changes.

## UI / HUD repairs

- Tightened the top HUD into a slimmer spellbook-style panel to preserve more gameplay space.
- Added a compact rune marker and a short HUD guidance line: `Drag pixies off the ward`.
- Reduced HUD label sizing and bar height for better small-screen balance.
- Moved the tier badge into the upper-right safe area so it reads as a secondary status, not a competing panel.
- Added a concise tier helper line: `Castle threat rising`.
- Kept the health bar, score display, tier progression, start flow, and restart flow intact.

## Mobile layout repairs

- Reduced top padding and panel mass on the title and fail cards.
- Kept start/restart controls full-width and comfortably tappable.
- Reserved right-side space for the progress badge on small screens.
- Reduced reaction card footprint and bottom-right spacing to avoid covering too much of the live play area.
- Preserved the current interaction model and above-the-fold CTA reachability at `400x700`.

## Visual hierarchy repairs

- Shifted cards and buttons from generic capsule styling toward arched spellbook shapes.
- Shortened onboarding and fail-state copy for faster scan speed.
- Refined button treatment with a more brass-and-parchment magical finish.
- Increased distinction between primary HUD information and secondary tier information.
- Preserved the animated castle backdrop, floating candles, house banners, mist, and magical crest so the procedural Harry Potter identity remains intact.

## Mechanics preserved

Preserved without rule changes:
- drag-to-banish input behavior
- score progression
- health / ward integrity behavior
- endless-loop progression semantics
- start / restart behavior
- canvas-driven rendering and gameplay loop

## Remaining risks for final mobile repair

- The existing runtime page error remains present and appears upstream of this visual pass.
- Live score text may still be overwritten by gameplay JS with generic wording during play.
- Further runtime polish should stay conservative unless the upstream script can be safely decoded and verified.