# Blueprint

## High-level code structure
This project is a single-file browser game implemented entirely in `index.html`. The file contains:

- HTML for the playfield, overlay UI, start screen, HUD, score display, and feedback badges
- Embedded CSS for the retro scrapyard / CRT visual theme and mobile-safe layout
- Embedded JavaScript for rendering, input handling, audio playback, game state, particle effects, and collision logic

The code is organized into several practical sections:

1. **Configuration and theme constants**
   - `CONFIG` controls friction, bounce, and spawn padding
   - `THEME` defines the visual palette
   - `ITEMS` defines the draggable junk object catalog

2. **Audio and feedback systems**
   - `AUDIO_MAP` points to remote audio assets
   - `Sfx` manages sound effects, background loop, and lightweight synthesized crash noise
   - `Feedback` controls temporary animated HUD badges such as combo and reset callouts

3. **Rendering and entity model**
   - A fullscreen canvas is the main game surface
   - `Entity` represents each scrap object with position, velocity, dimensions, type, and drawing behavior
   - `Particle` represents impact debris or splash effects

4. **Game logic and loop**
   - `spawnItem`, `explode`, `checkCollisions`, `updateUI`, `drawBackground`, and `loop`
   - The main loop updates entities, resolves collisions, renders the background, draws items, and advances particles

5. **Input and boot flow**
   - Mouse and touch dragging are unified through helper functions
   - Buttons handle start, spawn, and reset
   - `bootGame()` initializes audio, reveals the HUD, spawns starter junk, and begins the animation loop

## Game loop / state model
The game uses a lightweight real-time loop driven by `requestAnimationFrame`.

### Core runtime state
- `entities`: all active junk items currently in the yard
- `particles`: active visual effect fragments from collisions or resets
- `running`: whether the game has started
- `activeDrag`: the currently grabbed item, if any
- `dragOffset`: relative pointer offset while dragging
- `collisionBurstCount`: rough collision chain counter for feedback messaging

### State phases
1. **Pre-start**
   - Start panel is visible
   - Canvas background is present, but gameplay is inactive

2. **Active sandbox play**
   - Player can spawn junk
   - Player can drag and throw items around the lot
   - Items slide with friction and bounce off screen bounds
   - Overlapping items are removed in destructive collisions

3. **Reset / clear event**
   - Player hits clear lot
   - All current items explode into particles
   - Field is emptied, but the session continues

This is not a level-based structure. It behaves more like an open-ended toy or arcade sandbox with continuous interaction.

## Player goals
The immediate player goal is to create satisfying collisions by dragging spawned junk into other junk until both objects are destroyed.

Inferred goals:
- make the lot noisy and chaotic
- trigger amusing crashes and particle bursts
- experiment with different object shapes and visual reactions
- maintain a sense of momentum by repeatedly spawning and smashing scrap

There is no win state, score target, timer, enemy pressure, or campaign progression. The game is primarily about playful interaction and self-directed spectacle.

## Interaction pattern
The interaction model is direct manipulation:

- press/click/touch an object to pick it up
- drag it across the yard
- release to leave it in motion
- spawn additional objects with a HUD button
- clear everything with a reset button

This creates a tactile loop:
1. spawn junk
2. grab junk
3. slam junk into other junk
4. watch both disappear in sparks or splashes
5. repeat

The game is fully readable on desktop and touch devices, with touch listeners, disabled passive scrolling during drag, and safe-area-aware HUD placement.

## Core systems
### 1. Scrap spawning
Random item types are chosen from a fixed list:
- door
- bus
- wood/log
- ball
- milk carton
- pencil

Each item has custom dimensions, color, label, and bespoke canvas art.

### 2. Drag-and-throw physics
Items are not simulated with full rigid-body physics. Instead, they use:
- direct pointer repositioning while dragged
- stored velocity
- friction decay
- wall bounce

This produces a loose top-down “crash toy” feeling rather than simulation-grade physics.

### 3. Destructive collision handling
Collision is simplified to a radius-distance check between item centers. When two items overlap closely enough:
- both are marked for removal
- both explode into particles
- impact sounds play
- optional combo feedback can appear

Milk collisions receive a distinct audiovisual treatment.

### 4. Particle feedback
Destroyed items create particle bursts:
- regular junk makes fiery debris
- milk makes brighter splash-like fragments

This enhances the “impact toy” fantasy.

### 5. Arcade presentation feedback
The UI supports:
- start-screen framing
- “WRECKS” live counter showing active objects in the yard
- combo / chaos animated badge overlays
- background music loop and punchy sound effects
- retro CRT and neon scrapyard styling

## Inferred genre / gameplay shape
Strongest genre inference:
- **physics toy / arcade sandbox / destruction click-and-drag game**

Shape of play:
- short-session
- score-light
- spectacle-driven
- tactile and casual
- toy-like rather than strategic
- highly replayable through repeated self-directed chaos

It loosely resembles:
- a mini destruction sandbox
- a direct-manipulation physics playground
- a casual crash toy with arcade presentation

## Gameplay heuristic summary
The intended experience appears to be:
- instantly understandable
- funny and loud
- visually readable
- satisfying to poke at for a few minutes
- centered on spawning goofy objects and making them collide

The design prioritizes:
- quick feedback
- low friction controls
- readable object silhouettes
- repeated crash payoff
- casual mobile-friendly interaction over depth or progression

## Confidence notes
High confidence:
- single-screen arcade sandbox structure
- drag-to-crash interaction loop
- no formal win condition
- collision removal and particle spectacle as the main reward

Moderate confidence:
- “magnet chaos” and “wreck lot sim” language suggest a fictional scrapyard fantasy, but the actual implementation is simpler than a true magnet simulator
- combo messaging exists, but the game does not deeply track score combos as a structured progression system

Low confidence:
- whether future versions were intended to add more mechanical depth, because the current code is intentionally compact and toy-like