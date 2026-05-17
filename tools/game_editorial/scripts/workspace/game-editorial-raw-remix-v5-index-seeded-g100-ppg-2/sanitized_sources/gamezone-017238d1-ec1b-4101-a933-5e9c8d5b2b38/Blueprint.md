# Signal Sweep Blueprint

## High-level code structure
- A single `index.html` file contains the entire game: HTML UI, CSS presentation, audio tags, and JavaScript gameplay logic.
- The HTML structure is split into:
  - a start screen
  - an in-game HUD
  - a game-over screen
  - lightweight animated feedback overlays
  - a full-screen `<canvas>` used for all world rendering
- The JavaScript is organized as a compact arcade game script with:
  - a `CONFIG` object for tuning movement, camera, timing, collection radius, and render distance
  - an `AudioSys` object handling music, sound effects, mute state, warning pulses, and simple synthesized tones
  - two small classes: `Camera` and `Entity`
  - an `Input` object for drag-based steering and movement
  - global game state variables for score, timer, entities, and play state
  - lifecycle functions for init, reset, start, restart, update, draw, and game over
  - a pseudo-3D projection/rendering pipeline for floor tiles and collectible entities

## Game loop / state model
The game runs on `requestAnimationFrame(loop)`.

### Core loop phases
1. Compute delta time.
2. If the game is active:
   - update player movement from drag input
   - reduce the countdown timer
   - trigger low-time warning behavior when near failure
   - animate collectible entities
   - detect collection by proximity
   - respawn more entities when the field gets sparse
3. Redraw the scene:
   - sky gradient and haze
   - projected floor tile grid
   - projected collectible objects sorted back-to-front
4. Continue requesting the next frame.

### State model
- **Pre-game / attract state**
  - Start screen visible
  - Canvas already rendered with an idle scene
- **Active play**
  - HUD visible
  - Timer counts down from 30 seconds
  - Player steers continuously by dragging on the canvas
  - Collecting nodes increases score and adds time
- **Failure / end state**
  - Triggered when timer reaches zero
  - HUD hides
  - Game-over screen shows final score
  - Failure audio/visual feedback plays
- **Restart**
  - Rebuilds the initial play state without reloading the page

## Player goals
- Pilot the drone across the grid-like world.
- Reach floating signal nodes before the countdown expires.
- Extend survival by collecting nodes, since each pickup adds time.
- Maximize total recovered nodes before eventual timeout.

## Interaction pattern
- Primary interaction is **touch/pointer drag on the canvas**.
- Horizontal drag controls turning.
- Vertical drag controls forward/backward movement intensity.
- Releasing input stops movement.
- UI buttons handle start, restart, and mute.
- There is no combat, shooting, puzzle solving, or direct enemy interaction.

## Core systems
### 1. Timer-pressure survival system
- The run begins with a short countdown.
- Time decreases continuously.
- Each collected node grants a fixed time bonus.
- The entire session revolves around converting pickups into more remaining time.

### 2. Free-roaming collection system
- Collectibles spawn around the player in a circular radius band.
- The player collects automatically by entering a distance threshold.
- The world keeps replenishing nodes when the count becomes too low.

### 3. Mobile drag locomotion system
- Input behaves like an invisible virtual joystick.
- The game emphasizes smooth analog movement rather than tap-to-move.
- A visual joystick hint appears at the drag origin.

### 4. Pseudo-3D rendering system
- The game fakes 3D via manual projection math on a 2D canvas.
- A checkerboard floor and floating objects create a retro first-person scanner-flight feel.
- Objects are depth-sorted and faded by distance fog.

### 5. Feedback and juice system
- Score pop scaling on collection
- Warning sound behavior when time is low
- Music loop during play
- Collect/fail animated GIF overlays
- Distinct start/game-over panels with sci-fi styling

## Inferred genre / gameplay shape
- Strongest genre shape: **endless time-attack collection runner / survival scavenging arcade game**
- Presentation evokes a **light first-person exploration runner** rather than a shooter.
- It plays like a minimalist **survival collection game** where navigation efficiency is the core skill.
- The game loop is short-session, score-chasing, arcade-oriented, and mobile-first.

## Gameplay heuristic
A likely intended player strategy is:
1. Start moving immediately after the run begins.
2. Sweep in broad arcs rather than stopping often.
3. Use nearby nodes to keep the timer stable.
4. Prioritize momentum and smooth turns over precise micro-adjustments.
5. Treat each node as both score and fuel, because every pickup buys more survival time.

## Confidence notes
- High confidence that the central mechanic is survival-through-collection under time pressure.
- High confidence that the experience is designed primarily for mobile touch play.
- Moderate confidence on whether the collectible objects are narratively “nodes” or “drones”; UI text says “recover signal nodes,” while the rendered object is labeled visually like an echo-drone motif.
- Low uncertainty about genre fit: this is not a shooter or puzzle game despite the 3D viewpoint.