# Blueprint

## High-level code structure
The game is implemented as a single-page HTML document with three main layers:

1. **Presentation and HUD layer**
   - Inline CSS defines a neon sci-fi visual theme, responsive HUD panels, a modal settings panel, and an animated feedback overlay.
   - The DOM contains a fullscreen canvas, a top HUD, action buttons, timescale controls, a settings modal, and audio elements for background music and sound effects.

2. **Configuration and state layer**
   - A JSON config block (`#game-config`) exposes tweakable values for gravity, friction, starting particle count, and theme color.
   - Global state stores canvas size, simulation speed, particle list, total mass/score, selected spawn color, audio/graphics toggles, and pointer input state.

3. **Simulation and interaction layer**
   - A `Particle` class models each spawned unit with position, velocity, glow animation state, and rendering behavior.
   - Core functions handle initialization, spawning, HUD refresh, field scattering, physics stepping, drawing, and the main animation loop.
   - Input and UI handlers connect pointer dragging to particle spawning and buttons to speed control, color cycling, field reset, scatter impulse, graphics quality, and sound settings.

## Game loop / state model
The game runs in a continuous `requestAnimationFrame` loop.

### Core loop flow
1. Compute frame delta time.
2. Advance simulation with `physicsStep`.
   - Spawn particles while the pointer is held down.
   - Apply pairwise gravitational attraction between all particles.
   - Apply friction damping.
   - Move particles.
   - Resolve particle-to-particle collisions and wall bounces.
   - Trigger audio, vibration, HUD updates, and feedback overlays from impacts and actions.
3. Render the field, overlays, particle links, input reticle, and all particles.
4. Queue the next frame.

### State model
There is no multi-scene progression structure; the game is essentially an always-live sandbox state with lightweight control toggles:
- **PLAYING** as the implied main mode.
- **Time scale states**: `0x`, `1x`, `2x`, `3x`.
- **Graphics states**: medium / high / ultra.
- **Audio states**: on / off.
- **Input active / inactive** for drag-spawning.
- **Settings modal open / closed**.

## Player goals
The code suggests an expressive, toy-like objective rather than a win/lose structure.

Primary inferred goals:
- Create a glowing swarm of particles by touching and dragging.
- Watch the swarm self-organize through gravity and collisions.
- Increase the on-screen swarm count / “Swarm Signal” score.
- Experiment with color, simulation speed, and scatter/reset actions to produce different motion patterns.
- Enjoy the audiovisual feedback of dense impacts and moving particle clusters.

## Interaction pattern
The interaction model is direct, tactile, and continuous:

- **Pointer/touch drag:** continuously spawns particles at the finger/cursor location at a very high rate.
- **Tap buttons:** change particle color, pause/unpause or speed up the simulation, scatter the swarm, reset the field, and open/close settings.
- **Settings panel:** toggles graphics quality and audio.
- **No keyboard dependency:** the game is designed around touch and pointer control, with mobile-safe layout and vibration support.

This creates a “paint the field with particles, then manipulate the simulation” loop.

## Core systems
### 1. Particle spawning system
Holding the pointer down emits many particles near the current pointer position with slight random offsets. Spawn color follows the currently selected palette color.

### 2. N-body gravity system
Every particle attracts every other particle using a simplified gravitational formula with configurable gravity and a minimum denominator clamp to avoid extreme forces.

### 3. Motion and damping system
Particles move using velocity integration and a configurable friction factor to gradually damp motion.

### 4. Collision system
Particles collide elastically with each other and bounce off the screen boundaries, with impact strength affecting feedback.

### 5. Visual rendering system
Particles have layered neon rendering, optional halos, pulse effects, crosshair details, orbiting satellite dots, and short-range connection lines in ultra mode.

### 6. HUD and control system
The HUD exposes:
- Swarm Signal (effectively total mass / count)
- Spark Drones (particle count)
- Color selection
- Simulation speed
- Scatter action
- Reset action
- Settings access

### 7. Audio / haptics feedback system
The game uses:
- looping sci-fi/action background music
- spawn, collision, reset, and UI sound effects
- vibration for touch feedback and heavier reactions to stronger impacts

### 8. Responsive/mobile system
The layout explicitly supports mobile screens, safe-area insets, and touch-safe scaling.

## Inferred genre / gameplay shape
This is best understood as a **physics sandbox / satisfying interaction toy** with strong overlap with:
- physics puzzle aesthetics
- ASMR / satisfying simulator sensibilities
- lightweight sandbox building / particle painting
- interactive audiovisual toy design

It is **not** a level-based puzzle or score-chasing arcade game in a strict sense. The score exists mostly as a live activity metric rather than a victory target. The experience centers on spawning, observing, and perturbing a neon particle swarm in a zero-pressure simulation field.

## Gameplay heuristic summary
If recreating or analyzing the moment-to-moment play, the dominant heuristic is:

1. Touch and drag to lay down a dense trail of glowing particles.
2. Let gravity pull the particles into moving clusters.
3. Speed up, pause, or scatter the field to create new formations.
4. Change colors for visual variety.
5. Reset and repeat.

The game rewards curiosity, pattern watching, and sensory feedback more than mastery or progression.