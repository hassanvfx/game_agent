# Blueprint

## High-level code structure
- Single-file HTML game with embedded CSS, DOM HUD, audio tags, JSON config, and a canvas-based JavaScript game loop.
- Presentation is split between:
  - a full-screen `canvas` for gameplay rendering,
  - DOM overlays for HUD, game-over modal, flavor caption, audio status pill, and reaction GIFs,
  - inline audio elements orchestrated by a small `AudioManager`.
- Runtime tuning values are exposed through `window.gameConfig`, populated from the inline `#game-config` JSON block.

## Game loop / state model
- Main states:
  - `BOOT`: startup before the first resize and initialization pass.
  - `PLAYING`: active endless run.
  - `GAMEOVER`: terminal state entered when the player collides with a bomb.
- Main loop uses `requestAnimationFrame(loop)` and performs:
  1. delta-time calculation,
  2. `update(dt)` for spawn timing, hero movement, collision checks, score changes, particles, and transient feedback timers,
  3. `draw()` for background, hero hoop, falling entities, and particles.
- `resize()` sizes the canvas and starts the first run by calling `initGame()` then `setState('PLAYING')`.
- `initGame()` resets round data, positions the hoop, clears entities and particles, and refreshes HUD values.

## Player goals
- Catch falling basketballs to increase score.
- Avoid bombs, since a single bomb collision ends the run instantly.
- Beat the persistent best score saved in local storage.
- Survive longer as the pace increases with score.

## Interaction pattern
- Pointer/touch controls set a horizontal target position for the hoop.
- The hoop smoothly eases toward the target x-coordinate instead of teleporting.
- `pointerdown` and `pointermove` both function as gameplay input.
- On game over, the next input restarts the session immediately.
- The game is designed for phones as well as desktop: safe-area-aware UI, disabled default touch gestures on the canvas, and optional vibration bridge calls.

## Core systems
- **Hero system:** a hoop-shaped catcher near the bottom of the screen, rendered as a cute neon rim.
- **Spawn system:** falling entities appear on a timer; each spawn is either a ball or a bomb based on `bombChance`.
- **Difficulty scaling:** entity fall speed is based on gravity and scaled upward by score.
- **Collision system:** simple circular distance checks between each falling entity and the hoop catch zone.
- **Score system:** each caught ball adds one point; best score persists via `localStorage`.
- **Failure system:** touching a bomb triggers game over, audio/visual fail feedback, screen shake, and the restart overlay.
- **Feedback system:** particles, reaction GIFs, HUD text changes, audio cues, and haptics reinforce events.
- **Rendering system:** the game draws its own background, hoop, balls, and bombs directly on canvas for a self-contained arcade presentation.

## Inferred genre / gameplay shape
- Arcade reflex score-chaser with catch-and-dodge gameplay.
- Closest overall shape is an endless survival runner/lane-dodger abstraction, even though the field is single-screen and objects fall vertically instead of the world scrolling.
- The presentation theme is a futuristic basketball micro-arcade.

## Gameplay heuristic
- Hover near likely ball trajectories and make compact side-to-side corrections.
- Prioritize survival over perfect collection because bombs cause instant loss while missed balls are not directly punished.
- Expect pressure to rise over time as falling speed accelerates.
- The intended feel is fast restart, short sessions, and repeated best-score attempts.
