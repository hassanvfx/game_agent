# Prompt Surface Map — 3d gta game

## Mechanic meaning and preserved truth
- Preserve the existing 3D free-roam loop: third-person walking, D-pad/WASD movement, collision with block buildings, drivable cars, vehicle entry/exit, shooting while on foot, camera toggle, health, wanted/heat escalation, rival/patrol pursuit, failure/restart.
- Reinterpret the protected loop as a compact GTA-like neon city chase rather than archive retrieval. No score, collision, input, damage, spawn-count, or fail-state semantics were intentionally changed.

## Narrative/world semantics and HUD vocabulary
- World: Palm City after dark, a neon street grid where the player is a street runner surviving rivals and police heat.
- HUD vocabulary: STREET HEALTH, HEAT stars, PALM CITY LOOP, BUSTED, RESTART RUN.
- Tone: arcade crime-chase, urban chaos, high-contrast neon, readable mobile controls.

## Focal actor or central identity
- Focal actor: a stylized street runner/driver with visor, cap, bright jacket colors, and a visible heat-fantasy role.
- Secondary identity: muscle cars with wheels and underglow that become the player vessel when entered.

## Hazard, reward, goal, score, and failure role mapping
- Hazards: rivals and police patrols chase/contact the player exactly as old gang/cop NPCs did.
- Reward/fantasy: stay mobile, grab nearby cars, survive the pursuit, and push back with shots.
- Progress/pressure: HEAT stars are the preserved wanted value.
- Failure: health reaches zero and the player is BUSTED; restart restores health, wanted, visibility, and NPCs.

## Visual/focal identity, scene language, motif system, background ownership
- Procedural motifs: neon billboards, palm props, grid streets, skyline blocks, underglow cars, amber/pink police-heat palette, arcade HUD panels.
- The Three.js city remains the scene foundation but is visually regenerated away from the archive identity with new signs, palette, car silhouettes, character cap/visor, and GTA-like HUD language.

## Media/mood choices and catalog-backed enrichment
- Fonts remain catalog-approved Google fonts: Orbitron for title, Press Start 2P for HUD, Rajdhani for readable body copy.
- Existing catalog-style remote SFX/GIF wiring remains failure-tolerant and subordinate to gameplay.

## QA judgement criteria and before/after expectations
- Runtime must boot at http://127.0.0.1:43137/, start from the intro, show playable city, accept mobile controls, fire/enter/camera actions, and maintain restart path.
- Screenshots should show old archive framing before and new neon GTA-like city framing after, beyond title/color changes.
