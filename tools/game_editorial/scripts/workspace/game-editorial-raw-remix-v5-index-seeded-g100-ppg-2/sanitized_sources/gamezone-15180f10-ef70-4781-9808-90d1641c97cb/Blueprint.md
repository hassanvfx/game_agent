# Blueprint

## High-level code structure
- Single-file browser game implemented entirely in `index.html`.
- Structure is split into:
  - HTML layout for the start screen, HUD, game-over panel, main play canvas, and next-piece preview canvas.
  - CSS for a neon sci-fi presentation with glassmorphism UI, responsive HUD, animated overlays, and ambient space-like background treatment.
  - Inline JavaScript containing:
    - asset declarations
    - audio controller
    - render helpers
    - physics simulation
    - merge / scoring logic
    - UI state transitions
    - input handling
    - the main animation loop

## Game loop / state model
- The game waits on a start screen until the player launches the run.
- Once started:
  - `gameActive = true`
  - score resets to zero
  - the ball list is emptied
  - a next-piece type is prepared
  - background music starts
  - `requestAnimationFrame(gameLoop)` begins
- Each active frame:
  - decrements drop cooldown
  - updates physics in multiple substeps for stability
  - checks collisions between all balls
  - merges equal-type balls into the next type
  - checks loss condition against a top danger line
  - redraws the scene and HUD preview
- End state:
  - game stops when a ball settles above the danger threshold
  - music stops, fail SFX/GIF play, final score is shown
  - restart returns to a fresh run with the same gameplay loop

## Player goals
- Drop small orbiting drones / spheres into a bounded vertical chamber.
- Combine two matching units into a larger unit.
- Keep the stack from reaching and stabilizing near the top danger line.
- Accumulate as much score as possible through successive merges and longer survival.

## Interaction pattern
- Cursor or touch position controls the horizontal drop lane.
- Click / tap drops the currently queued sphere.
- The current piece is previewed both in the HUD and as a ghost at the drop point.
- Inputs are throttled by a short cooldown, so play alternates between aiming and dropping.
- There is no character movement; interaction is direct placement timing and positioning.

## Core systems
- **Spawn system:** only low-tier pieces spawn randomly from the first three types.
- **Physics system:** gravity, wall bounce, floor damping, friction, overlap resolution, and simple impulse response.
- **Merge system:** equal-size collisions create the next size up, remove old pieces, and add score.
- **Scoring system:** score value comes from the newly formed higher-tier piece.
- **Failure system:** loss occurs when a piece remains essentially stationary above the danger line.
- **Presentation system:** neon boundary lines, floating star particles, glowing spheres, preview UI, and reaction GIF feedback.
- **Audio system:** looping BGM plus start, drop, collide, merge, and fail SFX with unlock handling for browser autoplay restrictions.

## Inferred genre / gameplay shape
- Primary shape: physics-based merge puzzle.
- Closest commercial pattern: a Suika-style drop-and-merge stacking game, reskinned as a futuristic orbital chamber.
- Secondary traits:
  - score attack / survival arcade loop
  - dexterity placement game
  - casual one-screen replayable browser game

## Gameplay heuristic
- Early game is about keeping the floor organized by clustering identical small pieces.
- Mid game becomes a space-management problem as larger merged units consume more room and create awkward rebounds.
- Strong play likely involves:
  - dropping near matching targets rather than random columns
  - using walls to settle spheres gently
  - avoiding uneven towers under the danger line
  - planning around the next preview
- Failure pressure comes from vertical accumulation rather than time, making this a tension-building stack management game.
