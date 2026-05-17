# Blueprint

## Source identity
The preserved source (`index_old.html`) is a browser-native Three.js 3D free-roam action sandbox. The player moves around a blocky city, can enter nearby cars, drive with acceleration/steering, shoot on foot, trigger wanted escalation, take damage from hostile NPCs/police, and restart after a health-based failure state.

## Protected mechanics
- Intro tap/click starts the game.
- WASD and mobile D-pad map to cardinal walking movement.
- Walking speed, car acceleration/friction/turning, and camera follow/top-down modes remain intact.
- Building collision blocks player/car movement.
- Vehicle entry requires proximity; exiting places the player beside the car.
- Shooting only works on foot and increases wanted/heat.
- Bullets hide NPCs on contact and increase wanted/heat.
- Rival/patrol contact damages health; zero health opens failure overlay; restart restores core state.

## Transformable surfaces
Copy, HUD labels, palette, player/car/NPC silhouettes, procedural city props, signs, title screen, failure wording, fonts, GIF/SFX accents, and CSS overlay treatment are safe theming surfaces.

## Target remix
Regenerate the public surface as **Metro Heat 3D**, a compact GTA-inspired neon city chase that keeps all protected mechanics while making the player role, heat meter, cars, cops, street grid, and failure language visually coherent.
