# Clone Rebuild Plan

## Legacy references
- `index_old.html`: preserved source runtime and reference-only mechanic truth.

## Mechanic surfaces that matter most
- Player input/control handling: preserve WASD and D-pad bindings.
- Movement/update loop: preserve requestAnimationFrame, `movePlayerLogic`, `moveCarLogic`, `updateNPCs`, `updateBullets`, `updateCamera`.
- Collision/hit detection: preserve building collision radius and bullet-to-NPC contact.
- Scoring/progression signals: preserve wanted numeric thresholds, renamed to HEAT.
- Fail/win state: source has no win state; preserve health depletion leading to restart overlay.

## Fragile surfaces
- Three.js importmap path, mobile pointer/click lifecycle, audio user gesture unlocking, and button z-index/pointer-events.

## Easy safe updates
- Title, HUD copy, colors, fonts, procedural props, mesh materials, player/car decorative geometry, sign canvases, intro/failure wording.

## Do-not-touch conceptual surfaces
Do not change input semantics, movement speeds, collision logic, spawn counts, damage rules, wanted thresholds, or restart state reset.

## Focal identity and authored-world plan
The player is a street runner in Palm City. Cars are rideable muscle cars with underglow. Rivals and patrols provide pressure. HUD terms use STREET HEALTH, HEAT, BUSTED, and RESTART RUN.

## Engine/library rationale
Use the existing local Three.js module via importmap because the source already depends on it and it is the most stable path for preserving 3D mechanics. All new game CSS/JS remains inline in `index.html`.

## Reference checks required
Check `index_old.html` before any change that touches controls, collision, shooting, vehicle entry, camera, health/failure, or restart.
