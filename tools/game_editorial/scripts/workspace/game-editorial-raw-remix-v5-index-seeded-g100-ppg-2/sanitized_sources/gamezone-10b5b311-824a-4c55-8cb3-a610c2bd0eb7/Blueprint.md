# Blueprint

## High-level code structure
The game is implemented as a single self-contained `index.html` document with:
- inline CSS for all visual styling, HUD, overlays, and responsive layout
- inline JSON configuration embedded in a `<script type="application/x-game-config">` block
- inline JavaScript for state management, rendering, input, audio, UI transitions, and the main loop
- a single `<canvas>` used for all gameplay rendering
- layered DOM UI for the start screen, HUD, game-over screen, and small animated feedback cards

The structure is effectively split into these runtime concerns:
1. **Configuration**: gravity, jump strength, scroll speed, obstacle gap, and spawn cadence
2. **State model**: a central `state` object containing screen mode, score, timing, player physics, obstacles, particles, trail history, and background motion
3. **UI references**: cached DOM nodes for ribbons and feedback cards
4. **Audio manager**: simple catalog-backed sound pool plus looping background music
5. **Game systems**: reset, spawn obstacle, spawn particles, update, draw, game over, input handling
6. **Main loop**: `requestAnimationFrame` with delta-time based updating and drawing

## Game loop / state model
The game uses a continuous animation loop:
- `requestAnimationFrame(loop)` drives the frame cycle
- each frame computes a clamped `dt`
- `update(dt)` advances gameplay when the screen is `PLAYING`
- `draw()` renders the scene every frame, including background, player, obstacles, trail, and particles

### Screen states
The game has a very small explicit state machine:
- `START`: title screen visible, game waiting for launch
- `PLAYING`: physics, obstacle spawning, scoring, audio loop, and collision checks active
- `GAMEOVER`: final score displayed, restart available

### Persistent gameplay state
The central state includes:
- `score`: treated as altitude/distance climbed
- `player`: x, y, vertical velocity, radius
- `obstacles`: scrolling hazard columns with a single passable gap
- `particles`: floating text feedback after successful passes or boosts
- `trail`: historical player positions, rendered as a glowing flight path
- `obstacleTimer`: countdown to next hazard spawn
- `speed`: scrolling velocity that gradually increases over time
- `shake`: temporary screen shake intensity
- `bgOffset`: moving background grid offset
- `lastScoreChimeAt`: used to pace reward audio cues

## Player goals
The player’s immediate goal is to:
- keep the flying lunar beacon/core airborne
- thread through vertical hazard gaps
- avoid touching the top boundary, bottom boundary, or obstacle bands

The larger goal is to:
- survive as long as possible
- reach the highest possible altitude score
- maintain control as the scroll speed ramps upward and gaps become harder to navigate at pace

## Interaction pattern
Interaction is intentionally minimal and arcade-like:
- **tap / pointer press** on mobile or desktop
- **Space bar** on keyboard

Each input applies an immediate upward impulse by setting the player’s vertical velocity negative. Gravity then pulls the player downward again. This creates a rhythmic flap/thrust pattern.

Important interaction properties:
- one-button control scheme
- timing-based survival
- repeated micro-corrections instead of sustained movement
- game only starts or restarts through explicit launch/retry buttons
- once playing, any pointer press acts as a thrust input

## Core systems

### 1. Vertical flight physics
The player behaves like a thrusting orb/ship hybrid:
- gravity constantly increases downward velocity
- input applies a strong upward velocity impulse
- sprite rotation is derived from vertical velocity for readable motion feedback

This is the core mechanical system and strongly resembles flap-based obstacle threading.

### 2. Obstacle generation
Obstacles are spawned at a regular interval from the right side:
- each obstacle pair has a top band and bottom band
- a randomly positioned vertical gap is left between them
- they move leftward based on current scroll speed
- collision is checked against the player circle and the solid top/bottom hazard sections

### 3. Score and progression
Progression is endless survival:
- score rises continuously from movement/survival time
- passing an obstacle grants a large bonus
- speed increases slowly over time, raising difficulty
- there are no levels, shops, unlock trees, or narrative branches

### 4. Feedback and juice
The game uses layered presentation feedback:
- glowing trail under the player’s path
- floating text particles for successful maneuvers
- feedback cards with GIF reactions
- start/game-over ribbons
- screen shake on jump/crash moments
- altitude HUD and final score readout
- looped music plus jump/score/crash sound effects

### 5. Presentation theme system
Although mechanically abstract, the wrapper theme frames the run as a lunar navigation mission:
- title: **Moon Run**
- score displayed as **ALTITUDE**
- obstacle bands described as storm lanes / hazard bands
- player represented as a glowing mission core marked with “M”
- UI language references mission control, signal loss, recalibration, and launch

## Inferred genre / gameplay shape
Strongest inferred genre shape:
- **endless one-button obstacle-dodging runner/flyer**
- functionally closest to a **Flappy Bird-style endless runner / lane-threading survival game**
- visually wrapped in a **neon sci-fi lunar arcade** presentation

It is not a true platformer with terrain, nor a shooter, nor a lane-switcher. The most accurate abstraction is:
- endless survival
- rising difficulty
- continuous score chase
- tap-to-thrust aerial control
- obstacle gap threading

## Heuristic reading of the intended experience
The code suggests the intended player experience is:
- immediate start and fast retry
- accessible on mobile and desktop
- readable in a single glance
- focused on “just one more run” score chasing
- polished through neon HUD styling, animated reactions, and audio cues rather than mechanical complexity

## Confidence notes
Confidence is high on the core mechanics because the entire gameplay implementation is visible in one file. Confidence is moderate on thematic intent beyond the visible wrapper text, since the lunar mission framing is mostly aesthetic and could be re-skinned without changing the mechanics.