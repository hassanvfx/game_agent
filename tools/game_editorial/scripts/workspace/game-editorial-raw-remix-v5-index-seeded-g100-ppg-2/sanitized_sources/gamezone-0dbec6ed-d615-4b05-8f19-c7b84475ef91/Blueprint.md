# Blueprint

## High-level code structure
The game is implemented as a single self-contained `index.html` document with three major layers:

1. **Presentation layer**
   - HTML overlays for the start screen, HUD, game-over screen, and animated feedback panels.
   - Inline CSS that defines the neon sci-fi clinic visual identity, responsive layout, and UI styling.

2. **Canvas gameplay layer**
   - A full-screen `<canvas>` used for all real-time gameplay rendering.
   - Procedural drawing functions render the corridor background, player character, hazards, pickups, and floating text.

3. **JavaScript systems layer**
   - `AudioController` manages BGM and sound effects.
   - Global game state tracks score, speed, timers, player physics, obstacle lists, and transient feedback.
   - A requestAnimationFrame-driven update/render loop controls moment-to-moment play.

## Game loop / state model
The state model is lightweight and arcade-oriented.

### Core states
- **Start screen / idle**
  - Shows title, premise, and controls.
  - Waits for player input on the start button.
- **Active run**
  - HUD is visible.
  - The player auto-runs implicitly while the world scrolls left.
  - Obstacles and pickups spawn over time.
  - Score increases only when collecting bandages.
- **Game over**
  - Triggered when colliding with any hazard.
  - Displays final score and restart button.

### Runtime loop
During an active run, each animation frame:
1. Increments frame counter.
2. Gradually increases game speed over time.
3. Applies gravity and jump physics to the player.
4. Spawns incoming objects at intervals derived from game speed.
5. Moves hazards and pickups leftward.
6. Checks collisions with the player.
7. Awards score for bandage pickups or ends the run on hazard collision.
8. Draws background, obstacles, player, and floating feedback text.

This is effectively an **endless survival-runner loop** with collectible scoring.

## Player goals
The player’s immediate and ongoing goals appear to be:

- **Stay alive as long as possible**
- **Jump over or avoid animal hazards**
- **Collect bandages for “Poppy”**
- **Accumulate the highest possible score before failure**

There is no level completion or narrative ending in the code; progression is score- and survival-based.

## Interaction pattern
The interaction model is intentionally simple and accessible:

- **Single main action:** jump
- **Inputs:** tap, click, Space, or Arrow Up
- **Timing challenge:** the player must jump at the right moment to avoid ground and air hazards while also reaching collectible bandages
- **Auto-forward movement:** the character does not move horizontally under direct control; the world scrolls toward the player

This makes the game read as a one-button reflex runner.

## Core systems
### 1. Endless runner movement
The player is locked near the left side of the screen while the environment and objects scroll from right to left.

### 2. Jump and gravity physics
A basic platformer-style vertical motion system:
- fixed jump impulse
- constant gravity
- grounded check against the floor plane

### 3. Obstacle and pickup spawning
A shared spawn system randomly creates:
- hazards: ant, bear, leopard, eagle, bat
- pickups: bandages

Different object types occupy different heights and hitbox sizes, forcing varied jump timing.

### 4. Collision resolution
- **Bandage collision:** increments score, plays pickup feedback, shows floating text, may trigger milestone audio
- **Hazard collision:** ends the run immediately

### 5. Difficulty scaling
`gameSpeed` increases periodically, so:
- obstacles approach faster
- visual scrolling accelerates
- reaction windows shrink over time

### 6. Feedback and juice
The game includes:
- BGM and event SFX
- animated GIF feedback panels for success and failure
- floating speech bubbles on pickup
- glowing neon procedural background effects

These systems reinforce a playful arcade feel even though the game logic is simple.

## Inferred genre / gameplay shape
The strongest inferred genre is:

- **Endless runner / lane-less reflex runner**
- with **arcade survival scoring**
- and a **light collection objective**

More specifically, this is a **single-button endless runner set in a stylized hospital corridor**, where a cute character sprints automatically, dodges hazards, and collects medical pickups.

## Gameplay heuristic
A likely intended player heuristic is:

1. Start the run.
2. Watch the right side of the screen for incoming hazards and bandages.
3. Jump only when needed, since mistimed jumps can cause collisions with flying enemies or missed pickups.
4. Prioritize survival first, but route jumps to collect bandages whenever safe.
5. Adapt as speed rises and spacing becomes tighter.
6. Treat score as the main progression metric and replay for a better run.

## Confidence notes
Confidence is fairly high because the full game logic is present in one file and exposes:
- controls
- score logic
- object spawning
- win/fail conditions
- pacing and presentation rules

Uncertainty remains mainly in thematic intent:
- the title suggests a clinic setting
- the playable character reads as a cute patient or mascot
- hazards are stylized animals rather than medical objects, giving the game a surreal “clinic dash” theme rather than a realistic hospital simulation