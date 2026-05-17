# Blueprint

## High-level code structure

The game is implemented as a single self-contained HTML document with three main layers:

1. **Presentation / UI layer**
   - Start screen with title, instructions, and start button
   - In-run HUD showing distance traveled
   - Game-over overlay with final distance and restart button
   - Small reaction badges that briefly animate during jumps, checkpoints, and crashes

2. **Canvas rendering layer**
   - A full-screen `<canvas>` handles all runtime visuals
   - The game draws:
     - a neon night-sky gradient backdrop
     - moving stars and a stylized skyline parallax
     - glowing floating rail/platform segments
     - the runner avatar and its motion trail
     - particle effects for jumps and landings

3. **Runtime / systems layer**
   - `AudioController` manages background music and sound effects
   - Global game state tracks activity, score, speed, gravity, frame count, and world objects
   - `Platform` objects represent the traversable rails
   - Core functions handle spawning, movement, collision, jump logic, scoring, game-over flow, and the animation loop

The project is effectively a lightweight arcade web game built in plain HTML/CSS/JavaScript without an external game engine.

## Game loop / state model

The game uses a simple screen-state model:

- **Start state**
  - Start overlay visible
  - Player receives instructions
  - No gameplay simulation running

- **Active run state**
  - HUD visible
  - Background music starts
  - `requestAnimationFrame` drives the loop
  - Each frame:
    - background and skyline render
    - score increases with forward motion
    - game speed gradually accelerates
    - platforms scroll left
    - new platforms spawn as needed
    - player physics update with gravity
    - collision/landing checks run
    - particles and trail effects update
    - checkpoint reactions trigger at score thresholds

- **Game-over state**
  - Triggered when the player falls below the bottom of the screen
  - Music stops, fail sound plays
  - Crash reaction appears
  - Final distance is shown
  - Restart resumes a fresh run state

This is a run-based loop with immediate restarts and no meta-progression stored in code.

## Player goals

The player's immediate and only explicit goal is to:

- survive as long as possible
- keep the courier on the glowing rails
- use single and double jumps to clear gaps
- maximize traveled distance before falling into the void

Distance is the core success metric.

## Interaction pattern

The interaction model is extremely simple and reaction-based:

- **Tap / click / Space / Up Arrow** = jump
- The character supports **double jump**
- Input is one-button timing rather than directional movement
- Horizontal motion is automatic; the world scrolls toward the player

This creates a low-complexity, high-timing arcade loop suitable for both desktop and mobile.

## Core systems

### 1. Endless runner traversal
Platforms continuously move left while the player remains near a fixed x-position. Survival depends on landing on incoming rails.

### 2. Jump and double-jump system
The player can jump twice before touching ground again. The second jump is visually emphasized by a temporary color shift.

### 3. Platform generation
New platforms spawn with randomized:
- horizontal gap
- platform width
- platform height within safe bounds

Generation includes a vertical fairness constraint to keep jumps generally possible.

### 4. Physics and collision
The player is affected by gravity and vertical velocity. Landing is detected only while falling, against the top surfaces of platforms.

### 5. Speed escalation
Run speed gradually increases over time, causing:
- faster scrolling
- harder gap timing
- steadily rising challenge

### 6. Scoring / checkpoints
The score increments as the run continues, then displays as distance in meters. Audio/visual checkpoint feedback occurs in 100-meter buckets.

### 7. Juice and feedback
The game is highly presentation-driven:
- neon glow styling
- trail effects
- landing/jump particles
- animated reaction badges
- layered music and SFX

These systems reinforce fast, stylish arcade play.

## Inferred genre / gameplay shape

Strongest inferred shape:

- **Endless runner**
- **Lane-less / platform survival runner**
- **One-button arcade platformer**
- **Neon sci-fi reflex game**

Although the player is technically platforming, the structure is much closer to an endless runner than a level-based platformer because:
- the world auto-scrolls
- the run is endless
- difficulty ramps over time
- scoring is distance-based
- failure resets the entire run

## Gameplay heuristic

A player succeeds by developing a rhythm for:
- reading upcoming platform gaps early
- using the first jump conservatively
- saving the second jump as a correction tool
- landing cleanly to reset jumps
- adapting to faster speeds over time

The likely intended feel is “easy to understand, hard to sustain,” with neon spectacle, responsive one-button controls, and short repeatable runs.

## Presentation and fantasy

The fiction is light but clear:
- The avatar is a futuristic courier or “Pulse Rider”
- The setting is a midnight skyline above a void
- Platforms resemble glowing rails or rooftops
- The tone is energetic, stylish, and arcade-forward rather than narrative-heavy

The game sells speed, flow, and survival more than story.