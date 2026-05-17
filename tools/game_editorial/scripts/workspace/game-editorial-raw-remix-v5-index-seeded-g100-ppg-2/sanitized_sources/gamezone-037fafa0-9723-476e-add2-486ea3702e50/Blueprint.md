# Blueprint

## High-level code structure
The game is implemented as a single self-contained `index.html` file with three major layers:

1. **Presentation / UI layer**
   - Inline CSS defines the full visual identity: neon night palette, glassmorphism overlays, HUD chips, animated badges, and responsive sizing.
   - HTML contains:
     - a full-screen `<canvas>` for gameplay rendering
     - a start overlay
     - a game-over overlay
     - HUD feedback elements for score, status badge, and reaction GIFs
     - embedded editable configuration and asset declarations

2. **Runtime systems layer**
   - Inline JavaScript manages all gameplay.
   - Global state tracks canvas references, timing, game state, score, speed, lane width, shake, particles, and entity lists.
   - A small `AudioManager` loads and plays BGM/SFX with Web Audio fallbacks.

3. **Entity / rendering layer**
   - Player, enemy trains, and particles are plain objects stored in arrays or globals.
   - Rendering is done manually with Canvas 2D drawing functions:
     - `draw()`
     - `drawCityBackdrop()`
     - `drawPlayer()`
     - `drawTrain()`

## Game loop / state model
The game uses a conventional `requestAnimationFrame` loop:

- `loop(timestamp)`
  - calculates capped delta time
  - calls `update(dt)`
  - calls `draw()`
  - schedules the next animation frame

### State model
A string-based finite state machine drives flow:

- `START`
  - title overlay visible
  - track/background still draws
  - waiting for first input
- `PLAYING`
  - player can change lanes
  - trains spawn and move downward
  - score increments when trains pass off-screen
  - speed ramps upward over time
- `GAMEOVER`
  - collision has occurred
  - crash effects play
  - after a short delay, game-over overlay appears

## Player goals
The player’s goal is to survive as long as possible by dodging oncoming trains and clearing as many obstacles as possible.

Success is measured by:
- **score / cleared count**
- maintaining survival while speed gradually increases
- making clean lane changes at the right moment

Failure occurs when:
- the player collides with an incoming train

## Interaction pattern
The interaction model is very simple and mobile-first:

- **Tap/click start screen** to begin
- During play:
  - tap/click the **left half** of the screen to move left
  - tap/click the **right half** of the screen to move right
- On game over:
  - tap/click **Run Again** to restart

There is no acceleration, braking, or free movement; the player only swaps among **three fixed lanes**.

## Core systems
### 1. Lane switching
- The player occupies one of three lanes.
- Input changes the `player.lane` index.
- `player.targetX` updates immediately.
- Actual horizontal motion lerps smoothly toward the target lane, with a slight tilt effect.

### 2. Endless obstacle spawning
- Enemy trains spawn in random lanes.
- Spawning becomes slightly more aggressive as score rises.
- A basic safety check prevents immediate stacking in the same lane near the spawn region.

### 3. Endless survival scoring
- When a train moves beyond the screen, it is removed.
- Score increments by one per cleared train.
- Clearing trains also triggers badge/gif feedback and score SFX.

### 4. Difficulty escalation
- `gameSpeed` increases continuously over time.
- Spawn chance scales with both base spawn rate and score.
- This creates an endless-runner difficulty curve rather than level-based progression.

### 5. Collision / fail state
- Axis-aligned bounding box checks detect player/train overlap.
- On collision:
  - state changes to `GAMEOVER`
  - crash SFX plays
  - shake and particles trigger
  - crash feedback GIF is shown
  - final score is displayed after a delay

### 6. Juice / feedback systems
The code strongly emphasizes reactive arcade feedback:
- lane-shift particles
- HUD status badge text
- dodge/crash GIF flashes
- screen shake
- score and lane SFX
- glowing gradients and pulsing overlays

## Inferred genre / gameplay shape
This is best understood as a:

- **lane-based endless runner / dodge game**
- with a **neon sci-fi rail theme**
- rendered as a **2D canvas arcade survival experience**

Although the code refers to the player’s vehicle with car-like variables, the presentation frames the experience more like piloting a futuristic rail runner or express on train tracks. Mechanically, it behaves like a three-lane dodge runner where hazards stream toward the player and the only verb is lane swapping.

## Gameplay heuristic
A player succeeds by following this loop:

1. Start the run
2. Watch incoming trains and identify safe lanes
3. Make short, deliberate lane changes instead of constant weaving
4. Survive each near-miss and let obstacles pass off-screen
5. Build score while speed and density increase
6. Eventually fail from a mistimed dodge, then restart for a better run

The intended feel is:
- fast
- readable
- reflex-driven
- arcade-like
- stylish rather than simulation-heavy

## Presentation and tone
The presentation suggests:
- midnight city skyline
- glowing rails and synthwave color palette
- futuristic transport fantasy
- high-contrast HUD readability
- short-session score chase gameplay

The tone is:
- energetic
- sleek
- slightly tense
- accessible for casual play
- optimized for touch devices and quick retries

## Confidence notes
High confidence:
- three-lane endless dodge structure
- collision-based fail state
- score-by-survival/clearing obstacles
- mobile/touch-first controls

Moderate confidence:
- whether the player avatar is intended as a train, hover-car, or rail vehicle fictionally, because variable names and presentation cues are slightly mixed

Low ambiguity impact:
- the exact fiction is less important than the mechanic, which is clearly an endless lane-based dodging runner.