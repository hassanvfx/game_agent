# Mechanics Complexity Decomposition

## Complexity profile
This is a multi-state 3D arcade sandbox, not a mission-heavy open world. Complexity comes from simultaneous movement, vehicles, NPC pursuit, shooting, wanted escalation, camera state, and health/failure management.

## Protected modules
- Input: WASD, D-pad, shoot, enter/exit, camera, character buttons.
- Movement: walking vector movement and car acceleration/friction/turning.
- Collision: building contact and bullet/NPC contact.
- Pressure: rival and police pursuit behavior.
- State: wanted/heat, health, gameActive, isGameOver, restart.

## Themable modules
HUD vocabulary, overlay copy, palette, mesh materials, car/player decoration, background props, billboards, icons, GIF feedback, and audio labels.

## Safe escalation
Use visual pressure, denser neon motifs, heat vocabulary, and HUD feedback rather than adding new mechanics.
