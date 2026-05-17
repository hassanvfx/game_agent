# Blueprint

## High-level code structure
- Single-file browser game in `index.html`.
- Three main layers:
  - HTML structure for canvas, HUD, feedback GIF overlays, hidden audio assets, and game-over panel.
  - Embedded CSS defining a neon sci-fi HUD, full-screen canvas layout, responsive/mobile-safe scaling, and overlay effects.
  - Embedded JavaScript implementing the full game loop, entity model, input, audio, collision handling, spawning, rendering, and lifecycle hooks.
- Rendering is done directly with the Canvas 2D API rather than a framework or engine.
- State is mostly held in module-level variables and a few lightweight classes.

## Game loop / state model
- Main states:
  - `PLAYING`
  - `GAMEOVER`
- Core loop:
  - `requestAnimationFrame(loop)` drives the simulation continuously.
  - `updateGame(dt)` runs only while in `PLAYING`.
  - `drawGame()` runs every frame.
- Important mutable state:
  - `score` counts collected signal wisps.
  - `hp` starts at 100 and drops by 20 per hazard collision.
  - `gameTime` advances visual scan-line motion.
  - pooled entity arrays for `dusts`, `hazards`, and `particles`.
- Restart flow:
  - reset counters/state
  - reactivate initial collectibles
  - clear hazards/particles
  - return to `PLAYING`

## Player goals
- Move the pulse drone around the arena.
- Collect glowing signal wisps to increase score.
- Avoid red jammer hazards to preserve shield/health.
- Survive as hazard pressure rises and push for a higher score.

## Interaction pattern
- Pointer/touch-driven movement.
- The drone steers toward the current pointer position while touch/press is active.
- No complex buttons during play; the primary loop is movement, collection, and avoidance.
- On loss, the only explicit UI action is restart.

## Core systems
- **Player movement system**: smooth pointer-chase movement with clamped arena bounds.
- **Collectible system**: drifting signal wisps spawn over time and are lightly attracted when the player is nearby.
- **Hazard system**: jammer enemies spawn off-screen and move toward the current hero position.
- **Collision system**:
  - hero + collectible => score gain, particles, SFX, GIF feedback
  - hero + hazard => health loss, screen shake, particles, warning logic, danger feedback
- **Difficulty/progression system**:
  - collectible spawn governed by configurable spawn rate
  - hazard spawn interval shrinks as score increases, creating survival escalation
- **Feedback system**:
  - HUD for score and shield
  - animated collect/danger GIF callouts
  - particle bursts
  - camera shake
  - vibration hooks
  - layered sci-fi audio with fallback tones
- **Responsive system**:
  - `ResizeObserver`
  - device-pixel-ratio aware canvas sizing
  - mobile-safe HUD and full-screen interaction surface

## Inferred genre / gameplay shape
- Arcade survival-collection game.
- Best described as a touch-friendly arena dodger where the player gathers pickups while avoiding homing threats.
- Structurally close to a minimalist survival/avoidance arcade game rather than a level-based action game.
- Endless/high-score oriented rather than narrative or stage-clear focused.

## Gameplay heuristic
- Early play is about sweeping the field efficiently for easy pickups.
- Mid-game skill expression comes from route planning: stay mobile, cut across incoming wisps, and avoid getting cornered by hazards entering from off-screen.
- Since hazards accelerate pressure through more frequent spawns, optimal play likely means balancing greed and safety instead of chasing every nearby collectible.
- Damage is chunky at 20 HP per hit, so avoiding repeated contact matters more than tiny optimizations.
- The audiovisual framing suggests a “signal relay under interference” fantasy, but the mechanical heart is a score-chase survival loop.
