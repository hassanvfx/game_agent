<!-- Seeded blueprint filled. Keep headings stable. -->
# Blueprint

## Current implemented game identity
- genre: mobile-first 3D free-roam urban chase sandbox built with Three.js.
- objective: move around the city, enter or summon cars, switch weapons, survive collisions and pursuit pressure.
- input model: virtual joystick for camera-relative movement/driving, tap buttons for enter/summon/exit, attack, weapon switch, camera rotate, and zoom slider.
- core loop: start run, traverse on foot or in vehicle, interact with cars, attack NPCs, trigger wanted escalation, avoid police cars and collisions, continue until player HP reaches zero.
- fail/friction state: collisions and hostile/police pressure reduce HP; zero HP shows BUSTED and restart.

## Protected mechanics
- Camera-relative joystick movement and driving are preserved.
- Enter nearby car, exit current car, and summon car when no nearby car are preserved.
- Attack button, fist/gun switch, shooting cooldown, punch/raycast damage, and wanted escalation on player takedown are preserved.
- Building collision, car collision damage, police AI pursuit spawning, wanted decay, death, and restart semantics are preserved.
- Zoom slider and camera rotation behavior are preserved.

## Remixed target
Neon Felony: Overdrive District reframes the same 3D GTA-like sandbox loop as a neon night pursuit through an open downtown grid. The player is a street runner in a glowing crime-chase district; cars are overdrive rides, police cars are wanted heat, HP is body armor, the wanted display is the star pressure meter, and the authored scene uses procedural neon asphalt, high-rise window textures, nightclub colors, and mobile-readable HUD chrome.