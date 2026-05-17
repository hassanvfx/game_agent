# Prompt Surface Map — “3d gta game”

## Mechanic meaning and preserved truth
The source already implements a 3D open-city chase: free-roam movement, drivable/summonable cars, weapon switching, attacks, wanted level escalation, police pursuit, HP loss, and restart. These are protected exactly as the GTA-like mechanic truth.

## Narrative/world semantics and HUD vocabulary
The remixed world is a neon crime-chase district. HP is BODY ARMOR, police pressure is WANTED stars, melee is STREET, gun is SIDEARM, start is ENTER DISTRICT, and restart is RESPAWN DOWNTOWN.

## Focal actor or central identity
The focal actor is a street runner / getaway driver moving between on-foot street action and overdrive cars. The player identity is supported by neon player material, ride summon feedback, wanted HUD, and chase-camera controls.

## Hazard, reward, goal, score, and failure role mapping
- Hazards: buildings block movement, moving cars can damage the player, armed NPC/police pressure threatens survival.
- Rewards/tools: cars provide speed, summoned rides create escape options, sidearm/street attacks enable escalation.
- Goal: survive and roam while managing wanted pressure.
- Score/progress: wanted stars communicate escalation and decay.
- Failure: BUSTED means body armor reached zero.

## Visual/focal identity, scene language, motif system, and background ownership
The playfield is owned by procedural neon asphalt, emissive towers, magenta/cyan fog, glowing vehicle glass, sirens, scanline overlay, and a district brand badge. Color is paired with shape/material changes so the result is not only a label swap.

## Media/mood choices and catalog-backed enrichment
Approved Google fonts Audiowide and Rajdhani provide arcade/action identity. Existing approved remote audio/GIF hooks remain failure-tolerant and compact, supporting chase, summon, warning, and fail states without blocking controls.

## QA judgement criteria and before/after expectations
After screenshots should show a mobile-readable 3D night pursuit interface distinct from the preserved original. Runtime checks must prove start, canvas boot, HUD, weapon switch, camera/action taps, screenshots, and console status.