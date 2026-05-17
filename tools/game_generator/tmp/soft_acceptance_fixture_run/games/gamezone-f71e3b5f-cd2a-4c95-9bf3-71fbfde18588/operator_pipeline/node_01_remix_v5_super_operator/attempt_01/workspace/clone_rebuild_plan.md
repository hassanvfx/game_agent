# Clone Rebuild Plan

## Old reference and mechanic surfaces
The preserved reference is `/workspace/index_old.html`. It contains inline CSS/JS and a local Three.js runtime script. Important mechanics are joystick movement, update loop, car entry/exit/summon, punch/gun attack, collision resolution, wanted escalation/decay, police AI, HP death, camera rotate, zoom, start, and restart.

## Blueprint mapping
The blueprint maps these mechanics to a GTA-like neon city chase without changing rules: HP becomes body armor, wanted stars remain stars, cars remain drivable/summonable rides, police remain pursuit pressure.

## Fragile surfaces
Pointer handling, module script boot, Three.js scene initialization, collision math, and button click/tap lifecycle are fragile and should not be broadly refactored.

## Easy safe surfaces
Title, copy, HUD terms, CSS chrome, generated canvas textures, material colors, lighting, fog, and compact feedback labels are safe to update.

## Do-not-touch conceptual surfaces
Do not change movement equations, collision resolution, attack damage/cooldown, police spawn probability, wanted timer semantics, HP death threshold, or restart behavior.

## Focal identity and authored world
The new public surface presents a neon overdrive district with emissive roads, nightlife tower textures, player as street runner/getaway driver, ride-summon feedback, wanted HUD, and mobile controls.

## Engine/library approach
Keep the existing stable Three.js path from local assets and inline application code. No heavier engine is introduced because the source already has a working 3D sandbox runtime.

## Reference checks
Use index_old.html to confirm controls, core loop, collision, wanted stars, death/restart, and mobile controls remain equivalent while presentation changes boldly.