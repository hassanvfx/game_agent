# Blueprint

## High-level code structure
- Single-file HTML game with inline CSS and JavaScript.
- `index.html` contains:
  - a full-screen `canvas` for rendering the playfield,
  - layered DOM UI for start screen, HUD, game-over screen, feedback GIFs, and touch controls,
  - inline game logic handling state, physics, input, procedural platform generation, rendering, and audio.
- The code is organized around a few top-level objects/functions:
  - `CONFIG` for movement and visual constants,
  - `ASSETS` for remote audio/image sources,
  - `state` for the current run state,
  - `audio` helper for music and sound effects,
  - utility/gameplay functions such as `resize`, `resetGame`, `generatePlatforms`, `createParticles`, `update`, `draw`, `loop`, `startGame`, and `gameOver`.

## Game loop / state model
- Main loop uses `requestAnimationFrame(loop)`.
- `loop()` continuously calls:
  - `update()` to advance simulation while `state.screen === 'playing'`,
  - `draw()` to render background, platforms, player, and particles every frame.
- Screen states are simple and explicit:
  - `start`: title/instructions visible, gameplay inactive,
  - `playing`: HUD and controls visible, physics/platforming active,
  - `gameover`: fail overlay visible, waiting for restart.
- Core mutable state includes:
  - player position, velocity, grounded state,
  - camera x offset that follows the player,
  - score based on forward distance,
  - procedural platform list,
  - short-lived particles and feedback timers,
  - touch/mouse input flags for move and jump.

## Player goals
- Keep the signal courier robot online by traveling as far as possible.
- Hold movement to build/maintain forward momentum.
- Time jumps to clear gaps and land safely on upcoming platforms.
- Increase score by surviving and pushing farther right across the endless course.

## Interaction pattern
- Two-button mobile-first interaction:
  - hold `BOOST` to accelerate horizontally,
  - tap/press `JUMP` to jump when grounded.
- Mouse is also supported using the same on-screen buttons.
- There is no combat, inventory, or level selection; the entire loop is immediate survival platforming.

## Core systems
- **Movement system:** horizontal acceleration while boost is held, friction while released, gravity, and single grounded jump.
- **Collision/landing system:** player only lands when descending onto platform tops.
- **Procedural generation:** new platforms are appended ahead using randomized gaps, widths, and height variation within bounded vertical ranges.
- **Camera system:** side-following camera smooths toward a target x offset, keeping the player left-of-center.
- **Scoring system:** score is derived from distance traveled from the starting position; milestone sounds/feedback trigger periodically.
- **Failure condition:** falling below the bottom of the screen ends the run.
- **Feedback system:** looping background music, jump/land/score/fail SFX, celebratory/fail reaction badges, dust/emoji particles, neon HUD overlays.
- **Presentation system:** neon sci-fi aesthetic, robot courier iconography, “signal bars” framing, and futuristic typography.

## Inferred genre / gameplay shape
- Best described as a **mobile-first endless runner / endless platformer hybrid**.
- The avatar moves through a horizontally scrolling, endless obstacle course made of separated platforms.
- The main challenge is rhythmically managing forward boost and jump timing to survive for distance.
- It has arcade scoring, instant restart, and a lightweight “one more try” loop rather than level-based progression.

## Gameplay heuristic
- The player should almost always be boosting unless preparing for a landing adjustment.
- Success depends on reading gap spacing early, preserving enough horizontal speed, and jumping only when grounded.
- The game rewards stable forward flow more than precise exploration.
- Moment-to-moment feel is designed around quick retries, visible score gain, and sensory reinforcement for staying online.
