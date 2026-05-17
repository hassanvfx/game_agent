# Blueprint

## High-level code structure
The game is implemented as a single self-contained `index.html` file with four main layers:

1. **Presentation / DOM layer**
   - A full-screen `<canvas>` used for all main gameplay rendering.
   - HUD elements for distance and health.
   - A game-over overlay with restart button.
   - Audio tags for background music and sound effects.
   - Two feedback GIF elements for collection and crash reactions.

2. **Styling layer**
   - Embedded CSS defines a bright sky-storm arcade aesthetic with glassmorphism HUD panels, strong gradients, and responsive mobile-safe layout rules.

3. **Configuration layer**
   - A small JSON config block (`#game-config`) exposes tweakable values such as steer speed, run speed, and sky color.
   - `window.updateGameConfig()` suggests the game can be externally tuned without rewriting core logic.

4. **Gameplay / simulation layer**
   - A JavaScript loop driven by `requestAnimationFrame`.
   - State variables for hero position, obstacles, particles, clouds, score/distance, health, and audio state.
   - Procedural spawning, collision handling, rendering, feedback effects, and restart flow.

## Game loop / state model
The game uses a lightweight real-time arcade loop.

- **States**
  - `BOOT`: implied initialization state before play begins.
  - `PLAYING`: active gameplay; movement, spawning, collisions, scoring, and health updates run continuously.
  - `GAMEOVER`: gameplay stops updating, a results card appears, and restart becomes available.

- **Loop flow**
  1. `DOMContentLoaded` initializes canvas, input, resize handling, audio setup, and initial entities.
  2. The game immediately enters `PLAYING`.
  3. Each animation frame:
     - Compute `dt`
     - Update player steering and world speed
     - Increase distance over time
     - Spawn hazards and pickups
     - Move clouds, particles, and obstacles
     - Check collisions
     - Regenerate a small amount of health
     - Trigger danger effects when health is low
     - Enter `GAMEOVER` when health reaches zero
  4. Draw the sky corridor, lane markers, clouds, collectibles, hazards, hero craft, and particles.
  5. Restart resets data and returns to `PLAYING`.

## Player goals
The player’s inferred goal is to survive as long as possible while piloting a sky courier through a storm route.

Primary goals:
- Stay alive by avoiding damaging hazards.
- Extend the run distance meter.
- Collect energy rings to recover health and maintain momentum.
- Endure increasing speed and obstacle pressure.

Secondary implied goal:
- Beat your previous distance by surviving longer on each run.

## Interaction pattern
The interaction model is simple and mobile-first:

- **Pointer / touch steering**
  - Press and drag horizontally to move the courier left or right.
  - The hero smoothly lerps toward the current pointer position.
- **Single-button restart**
  - Tap the restart button after losing.
- **Passive forward motion**
  - The character automatically advances; the player only steers laterally.

This creates an accessible one-input avoidance/collection loop suited for touch devices.

## Core systems
### 1. Endless forward-runner progression
Distance increases automatically based on a base speed multiplied by a slowly rising speed multiplier. This creates escalating challenge without introducing stages or levels.

### 2. Health / survival economy
Health acts as a survivability buffer:
- Slowly regenerates over time.
- Gains a large boost from collecting rings.
- Loses a large chunk on hazard collision.
- When low, warning visuals and warning audio activate.
- At zero, the run ends.

This makes the game more forgiving than a pure one-hit endless runner.

### 3. Hazard system
There are two major damage sources:
- **Barriers**: direct solid obstacles moving downward into the player path.
- **Lightning strikes**: telegraphed hazards with a warning phase followed by an active damaging strike.

Lightning is notable because it adds anticipation and reaction timing rather than simple contact avoidance.

### 4. Pickup system
“Donuts” in code, narratively remapped as **energy rings**, function as beneficial pickups:
- restore health
- give positive feedback via sound/GIF/particles
- support longer survival

### 5. Feedback and juice
The game uses several arcade feedback channels:
- particle explosions
- haptic vibration
- low-health warning overlay
- collect/crash reaction GIFs
- BGM and event SFX
- glowing HUD and character rendering

### 6. Responsive canvas presentation
The game fills the screen, disables scroll/zoom interference, and adapts HUD spacing for smaller screens, indicating a browser-mobile play target.

## Inferred genre / gameplay shape
Strongest inferred genre shape:

- **Endless runner**, specifically a **lane-like / steering survival runner**
- Arcade dodge-and-collect game
- Reflex-based score chase with survival buffer management

The game is not a strict discrete-lane runner mechanically, because steering is continuous across the play field. However, its road layout, central striping, forward-scroll illusion, and obstacle funneling make it feel adjacent to lane runner / train runner design.

## Gameplay heuristic
A player succeeds by following this rhythm:

1. Keep the courier near safe gaps instead of over-correcting.
2. Watch for lightning telegraphs and avoid their eventual strike line.
3. Collect energy rings when the path is safe, especially to recover from previous hits.
4. Preserve health above the warning threshold to avoid cascading failure.
5. Adapt to rising speed as hazard density and reaction demands increase.

The practical mastery pattern is “survive first, collect opportunistically, and steer smoothly.”

## Presentation and theme inference
The title, copy, and rendering suggest:
- a stylized sky-delivery route
- storm hazards and aerial danger
- bright arcade sci-fi visuals rather than simulation realism
- short-session, replayable score attack structure

## Confidence notes
High confidence:
- endless survival loop
- horizontal steering controls
- health-based survival objective
- collectible + hazard structure
- game-over and restart flow

Moderate confidence:
- intended fantasy is a flying courier drone/ship rather than a person
- “runner” framing versus pure avoidance arcade game

Low uncertainty areas:
- whether score beyond distance was meant to matter more in a future version, since `score` exists but distance is the main visible metric.