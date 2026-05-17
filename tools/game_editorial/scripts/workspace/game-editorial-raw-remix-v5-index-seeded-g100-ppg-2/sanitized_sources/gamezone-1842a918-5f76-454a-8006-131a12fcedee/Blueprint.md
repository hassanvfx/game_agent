# Blueprint

## High-level code structure
The game is implemented as a single self-contained HTML file with embedded CSS, HTML UI, audio elements, and JavaScript gameplay logic. The structure is divided into a few practical layers:

- **Presentation layer**
  - Fullscreen canvas used for all core gameplay rendering
  - Overlay UI for HUD, start screen, game over screen, and temporary zone title popups
  - Neon sci-fi styling with responsive mobile-safe layout
- **Configuration layer**
  - Inline JSON config defines tweakable variables such as hero speed, jump force, gravity, and theme color
  - A global `updateGameConfig` hook can update runtime values
- **Audio and feedback layer**
  - Background music loop plus jump, landing, zone-clear, fail, and UI sound effects
  - GIF-based visual feedback for jump success and fail states
  - Web Audio fallback synth tones if media playback fails
- **Game simulation layer**
  - Core player state (`hero`)
  - Platform list, particle list, camera position, score, shake, decorative sky objects
  - Zone progression table defining platform width, gap spacing, motion, color, and difficulty escalation
- **Loop and lifecycle layer**
  - `requestAnimationFrame` main loop
  - `update(dt)` for simulation
  - `draw()` for rendering
  - `resize()` for responsive canvas sizing
  - start/reset/game-over flow handlers

## Game loop / state model
The game uses a lightweight arcade state machine:

- **START**
  - Start screen is visible
  - Hero is positioned near the bottom of the screen
  - Loop is already running, but gameplay simulation is idle
- **PLAYING**
  - Gravity affects the hero
  - Hero moves horizontally automatically and bounces direction at screen edges
  - Player can jump only when grounded
  - Platforms are generated upward as the camera ascends
  - Score rises based on achieved altitude
  - Difficulty zones change according to score thresholds
- **GAMEOVER**
  - Triggered when the hero falls below the camera view
  - HUD hides, final score and final zone are shown
  - Fail audio/feedback plays
  - Player can restart

Main simulation pattern per frame:
1. Apply gravity and velocity
2. Move hero
3. Bounce hero at left/right screen bounds
4. Move any moving platforms
5. Resolve downward landing collisions with platforms
6. Move the upward camera when the hero climbs high enough
7. Update altitude score
8. Detect zone promotions and increase movement speed
9. Generate more platforms as needed
10. Trigger game over if the hero drops off-screen
11. Update particles, backdrop motion, screen shake, and HUD text

## Player goals
The immediate goal is to keep landing on platforms and continue climbing upward.

The broader goal is to:
- achieve the highest possible altitude
- survive through increasingly difficult sky/space zones
- adapt to narrower gaps, thinner platforms, and moving platforms
- push into later airspace tiers such as **Storm Edge**, **Night Void**, **Star Field**, and **Solar Gate**

This reads as a score-chasing endurance ascent rather than a finite level-completion game.

## Interaction pattern
The interaction model is deliberately simple:

- **Tap/click on the canvas** to jump
- **Press Space** to jump
- On start and game-over screens, **Space** can also start/restart the run
- Jumping is allowed only while grounded on a platform

The hero is not directly steered left/right. Horizontal motion is automatic, producing a timing-and-positioning challenge centered on jump cadence.

## Core systems
### 1. Auto-run traversal
The hero constantly moves horizontally and reverses when touching the screen edges. This creates a back-and-forth lane coverage pattern.

### 2. Precision jumping
Jump timing is the main skill test. Since the hero can only jump when grounded, the player must commit to each takeoff and aim landings through timing rather than steering.

### 3. Vertical camera ascent
The camera tracks upward progress once the hero reaches the upper play threshold, turning the game into a climbing survival loop.

### 4. Procedural platform generation
Platforms are spawned upward based on the current difficulty zone. Platform spacing and behavior escalate over time.

### 5. Difficulty zone progression
A defined zone table changes:
- platform width
- platform gap
- whether platforms move
- platform move speed
- visual palette and accent colors
- perceived intensity

A zone promotion also boosts hero speed, making later play faster and harder.

### 6. Score as altitude
Score is represented as meters climbed, reinforcing the aviation/airspace fantasy.

### 7. Juice/feedback
The game emphasizes arcade feedback through:
- music and SFX
- camera shake on death
- particle bursts on jump/fail
- animated zone title popups
- jump/fail reaction GIFs
- glowing neon platform and character rendering

## Inferred genre / gameplay shape
The strongest inferred genre is an **arcade vertical platformer / survival runner hybrid**.

More specifically, the game feels like:
- a **one-button vertical climbing platformer**
- with **endless survival score attack** structure
- and **auto-runner** behavior because the hero moves laterally on their own

It is not a traditional side-scrolling endless runner because the camera progression is vertical and the main challenge is chaining upward platform landings. It also is not a pure platformer in the exploration sense; it is a procedural high-score survival ascent.

## Gameplay heuristic
A player succeeds by internalizing a simple rhythm:

- wait for the auto-moving hero to line up with the next platform
- jump only when grounded
- preserve momentum by planning one landing ahead
- anticipate that later zones reduce landing safety
- survive the transition from static to moving platforms
- manage rising speed and tighter spacing without over-jumping

The intended emotional arc is:
- approachable start
- satisfying rhythm of repeated jumps
- escalating tension as airspace tiers intensify
- abrupt failure when a mistimed landing sends the hero below the camera

## Inference confidence
Confidence is fairly high because the game logic is explicit in source:
- title, UI copy, and zone names establish the aviation/neon theme
- scoring, camera logic, platform generation, and collision code clearly define a vertical ascent loop
- controls and state transitions are directly stated in the code

Minor uncertainty remains around whether the creator conceptually labels the hero as a pilot, drone, or abstract neon avatar, since the playable sprite is abstract while the UI uses plane/pilot language.