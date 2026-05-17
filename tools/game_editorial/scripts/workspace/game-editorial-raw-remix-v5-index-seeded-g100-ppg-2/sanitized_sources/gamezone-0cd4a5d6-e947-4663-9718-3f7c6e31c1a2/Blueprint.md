# Blueprint

## High-level code structure
- **Single-file game application:** The entire game lives in `index.html`, combining HTML UI structure, embedded CSS styling, and a module script for gameplay logic.
- **Rendering stack:** Core gameplay is drawn on a full-screen HTML5 `<canvas>` using imperative 2D rendering.
- **UI layering:** The DOM provides menu and HUD overlays above the canvas:
  - start screen
  - in-run HUD with score and sound toggle
  - game-over screen with restart
  - animated feedback GIFs for successful passes and crashes
- **Audio subsystem:** A lightweight `AudioSystem` class manages looping background music, one-shot SFX, mute state, and browser audio unlocking.
- **Presentation model:** The game uses a neon sci-fi visual identity with glowing lane markings, skyline silhouettes, animated stars, futuristic typography, and stylized car sprites.

## Game loop / state model
### Main state
The game uses a small mutable state model:
- `gameState`
  - `active`: whether a run is live
  - `score`: distance / survival progress
  - `speed`: current run speed, scaled upward over time
  - `width`, `height`, `dpr`: viewport and rendering metrics
- `player`
  - current horizontal position
  - target horizontal position from pointer/touch input
  - size
  - tilt for steering feedback
- `enemies`
  - array of obstacle vehicles, each with lane position, speed, size, color
- environmental arrays
  - `stars`
  - `skyline`
- lane/road support state
  - `road`
  - `roadOffset`
  - `spawnTimer`

### Flow
1. **Attract mode**
   - Runs while the game is inactive.
   - Background stars and lane markers scroll to keep the scene alive.
2. **Start**
   - Clicking/tapping the launch button unlocks audio, resets state, clears enemies, restores HUD, and starts the main loop.
3. **Active run**
   - `requestAnimationFrame(gameLoop)` drives updates and draws.
   - Score rises continuously with speed.
   - Speed gradually increases with score.
   - Enemies spawn at intervals into one of three lanes.
   - Player horizontal movement eases toward the latest pointer/touch position.
4. **Collision**
   - A bounding-box collision with an enemy immediately ends the run.
   - BGM stops, crash SFX/GIF plays, and the game-over screen appears.
5. **Restart**
   - Restart button calls the same start routine and begins a fresh run.

## Player goals
- Stay alive as long as possible.
- Steer through open lanes and avoid incoming hostile traffic.
- Push for a higher distance score measured in meters.
- Endure increasing speed and denser obstacle timing.

## Interaction pattern
- **Primary interaction:** horizontal steering by touch-drag, touch, or mouse movement.
- **Control style:** direct pointer positioning rather than discrete taps or button presses.
- **Failure condition:** touching any enemy car.
- **Session shape:** short, replayable survival runs with immediate restart.

## Core systems
### 1. Lane-based traffic avoidance
- The road is visually divided into **three lanes**.
- Enemy vehicles spawn in a random lane and move downward toward the player.
- The player can move continuously across the road width, but the readable play pattern is lane selection and lane switching.

### 2. Survival scoring
- Score increases continuously over time and is framed as **meters cleared**.
- This makes progression survival-based rather than level-based.

### 3. Dynamic difficulty ramp
- Base speed starts around 12 and increases with score.
- Enemy spawn delay decreases as the run continues.
- The result is a steadily accelerating dodge challenge.

### 4. Collision and run termination
- Collision uses simple rectangular overlap with slight padding.
- Any collision is fatal and ends the attempt immediately.

### 5. Attract-mode presentation
- Even while inactive, the game animates the environment.
- This gives it an arcade cabinet / endless runner title-screen feel.

### 6. Audio and feedback reinforcement
- BGM plays during active runs.
- Separate SFX support:
  - start
  - pass / near-success feedback when an enemy leaves the screen
  - crash
  - sound toggle click
- Feedback GIFs emphasize successful passes and failures.

## Inferred genre / gameplay shape
- **Primary genre:** arcade lane-dodging survival runner
- **Secondary genre shape:** top-down endless traffic avoidance game
- **Player fantasy:** piloting a futuristic neon interceptor through a dangerous night corridor
- **Run structure:** endless until crash, score-chasing, reflex-focused, mobile-friendly
- **Closest gameplay reading:** an **endless runner / lane runner hybrid** rendered as a neon top-down car/hovercraft survival game

## Heuristic interpretation
This game is best understood as a compact arcade survival experience:
- one mechanic dominates: **steer to avoid obstacles**
- progression is **time-and-distance survival**
- challenge comes from **faster scrolling and shorter reaction windows**
- the UI and aesthetic present it as a cyberpunk interceptor chase, but the underlying rule set is deliberately simple and instantly readable on mobile

## Confidence notes
- **High confidence** in the core loop: survival lane-dodging with increasing speed.
- **High confidence** that score represents distance rather than points from collectibles or combat.
- **Moderate confidence** on thematic framing: the code mixes “interceptor,” “ship,” and car-like rendering, but mechanically it behaves most like neon traffic avoidance.
- **High confidence** that there are no hidden progression layers, upgrades, levels, or narrative branches in this implementation.