# Clone Rebuild Test Plan

## Checks
- Boot/load the canonical `index.html` through the assigned URL.
- Capture before evidence from `index_old.html`.
- Start from intro overlay and confirm it fades.
- Verify active 3D city renders in mobile portrait.
- Exercise D-pad movement, shoot button, camera toggle, and vehicle entry action.
- Confirm HUD shows STREET HEALTH and HEAT stars.
- Confirm console has no blocking errors.
- Capture after entry, spawn/play, and interaction evidence.

## Expected pass
The game boots, starts, renders the remixed city, keeps controls tappable, and preserves the free-roam/pursuit loop.

## Remaining risk
Automated QA may not force a full health-depletion failure without intrusive state manipulation; failure logic is preserved by direct source comparison and restart path remains present.
