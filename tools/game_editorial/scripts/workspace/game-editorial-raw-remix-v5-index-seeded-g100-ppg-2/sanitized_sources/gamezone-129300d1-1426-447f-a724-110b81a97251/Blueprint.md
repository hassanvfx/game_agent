# Blueprint

## High-level code structure
The game is implemented as a single self-contained `index.html` file with three main layers:

1. **Presentation / UI layer**
   - HTML overlays for the start screen, HUD, weapon selector, and game-over screen
   - CSS-driven neon sci-fi styling with responsive mobile-safe layout
   - Feedback GIF overlays for impact and danger states

2. **Canvas gameplay layer**
   - A full-screen `<canvas>` used for all active gameplay rendering
   - Draw routines for the scrolling starfield, perspective grid, enemies, particles, and aiming reticle

3. **Game logic layer**
   - JavaScript embedded in the page
   - State variables for score, lives, weapons, cooldowns, targets, particles, and pointer position
   - A lightweight audio controller for music and sound effects
   - An animation loop driven by `requestAnimationFrame`

## Game loop / state model
The state model is simple and arcade-oriented.

### Meta states
- **Start screen**
  - Displays title, premise, and start button
  - Game is inactive until the user clicks/taps to begin
- **Active play**
  - HUD and weapon bar are visible
  - Enemies spawn over time
  - Player can shoot by clicking/tapping the playfield
  - Score and lives update in real time
- **Game over**
  - Triggered when shields/lives reach zero
  - Final score is shown
  - Player can restart into a fresh run

### Per-frame loop during active play
Each animation frame:
- advances the frame counter
- reduces weapon cooldown when needed
- periodically attempts enemy spawning
- updates enemy behavior states
- updates particles
- scrolls background stars
- redraws the full scene

### Enemy state flow
Each target progresses through a short lifecycle:
- **rising**: enters from below the screen
- **floating**: hovers near the upper/middle play space for a limited time
- **fleeing**: descends away from the defended area
- if it escapes, the player loses one shield/life

This creates a “shoot before escape” pressure loop.

## Player goals
The player’s immediate goal is to destroy breach drones before they get away and weaken the defensive barrier.

The player’s broader goal is:
- survive as long as possible
- clear as many threats as possible
- maximize score in an endless run structure

There is no narrative progression or level completion system. Progression is survival-based and score-based.

## Interaction pattern
The interaction model is direct and minimal:

- **Pointer/touch aiming**
  - Mouse or touch position defines the targeting reticle
- **Tap/click to fire**
  - The player fires at the current pointer position
- **Weapon switching**
  - Three on-screen weapon buttons let the player swap between firing styles:
    - Pulse: balanced single shot
    - Burst: spread/scatter shot
    - Lance: heavy damage precision shot

This makes the game feel like a mobile-friendly tap shooter rather than a movement-based action game. The player does not move an avatar; they operate as a stationary defensive gun platform.

## Core systems
### 1. Target spawning and difficulty scaling
Targets spawn periodically based on frame count. Spawn likelihood increases with score, implying endless difficulty escalation. Enemy HP and movement speed also scale upward with score.

### 2. Weapon system
There are three weapons with distinct tradeoffs:
- **Pulse / pistol**
  - moderate damage
  - fast cooldown
  - precise
- **Burst / shotgun**
  - lower per-hit damage
  - multiple pellets
  - wider spread
  - effective for larger hit zones or close grouping
- **Lance / sniper**
  - very high damage
  - slow cooldown
  - precision oriented
  - can continue through checks without the non-sniper break behavior

This creates tactical choice around speed, coverage, and damage output.

### 3. Hit detection and combat resolution
Shots are resolved instantly at the clicked/tapped point rather than with traveling projectiles. Visual tracer particles and impact effects simulate gunfire. A target takes damage if the aimed shot point lands within its radius.

### 4. Survival / shield system
The player starts with 3 lives/shields. If a target completes its cycle and escapes off-screen, one shield is lost. Reaching zero ends the run.

### 5. Score system
Destroyed enemies award points. Score both measures performance and increases game pressure by scaling enemy durability and spawn rate.

### 6. Feedback systems
The game emphasizes responsiveness through:
- sound effects for firing, hit, kill, fail, warning, start, and weapon switch
- animated GIF overlays for impact and danger feedback
- particle bursts
- health bars above enemies
- a glowing reticle with cooldown arc
- red screen flash on shield loss

### 7. Audio system
A dedicated `AudioController` manages:
- looping background action music
- throttled sound effects
- browser audio unlock flow on first interaction

## Inferred genre / gameplay shape
Strongest inferred gameplay shape:

- **Arcade tap shooter**
- **Fixed-position defense shooter**
- **Survival score chaser**
- **Casual mobile-friendly reflex game**

The game resembles a hybrid of:
- a light shooting gallery
- a wave/survival defense game
- a score-attack arcade shooter

It is not a traditional first-person shooter because the player does not navigate a 3D space, and it is not a tower defense game in the strategic placement sense. Its actual loop is closer to a reactive target-defense shooter with endless escalation.

## Gameplay heuristic
The intended play pattern appears to be:

1. start a run immediately from a polished title card
2. watch for rising drones entering from the bottom
3. quickly tap/click threats before they finish hovering and escape
4. switch weapons depending on target density and urgency
5. preserve the final shields while score steadily climbs
6. restart after collapse for another higher-scoring attempt

The design prioritizes:
- fast readability
- short sessions
- responsive audiovisual feedback
- skill expression through timing and weapon choice
- repeatable endless replay

## Confidence notes
High confidence:
- endless score-attack survival structure
- click/tap-to-shoot defensive interaction
- three-weapon loadout with different tactical roles
- mobile-safe arcade presentation

Moderate confidence:
- lore framing around defending a skyline barrier with a “Prism Sentinel” is thematic dressing rather than deep narrative
- “drones” and “shield core” imply defense of a city or energy barrier, but the actual gameplay abstraction is intentionally lightweight