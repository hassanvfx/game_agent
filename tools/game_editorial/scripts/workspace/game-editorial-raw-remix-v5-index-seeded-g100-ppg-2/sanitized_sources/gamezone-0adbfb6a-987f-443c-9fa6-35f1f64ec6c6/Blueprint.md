# Blueprint

## High-level code structure
- **Single-file web game** contained in `index.html`.
- **Inline CSS** defines the entire visual identity: neon sci-fi HUD, modal screens, responsive mobile-safe layout, and animated decorative effects.
- **Inline HTML** provides:
  - the full-screen canvas playfield,
  - a start / game-over / victory UI layer,
  - HUD widgets for current node and difficulty state,
  - control hints,
  - audio elements using approved remote sources.
- **Inline JavaScript** contains all runtime logic, split conceptually into:
  - `AudioController` for background music, SFX playback, unlock flow, and fallback synthesized sounds,
  - global configuration/state objects,
  - input setup for touch / pointer controls,
  - level generation,
  - update loop / physics / collisions,
  - canvas-based pseudo-3D rendering.

## Game loop / state model
The game runs on a classic `requestAnimationFrame` loop:
1. `loop(timestamp)` computes delta time.
2. `update(dt)` advances movement, gravity, collisions, camera follow, win/lose checks, and particles.
3. `render()` redraws the scene, player, platforms, effects, and virtual joystick.

### Inferred state machine
- `MENU` — title screen visible, gameplay inactive.
- `PLAYING` — player movement, jumping, collision checks, rendering, and HUD all active.
- `GAMEOVER` — triggered when the player falls off the route.
- `VICTORY` — triggered when the player reaches the finish platform for the current node.

### Progression state
- `level` starts at 1.
- `nextLevel()` increments the level and regenerates a new route.
- From level 6 onward, the game enters a harder “Red Alert” difficulty band with larger gaps, narrower platforms, and stronger lateral drift in generated routes.

## Player goals
- Control a “courier signal” avatar across floating route segments.
- Stay on the generated path and avoid falling into the void.
- Reach the finish platform to stabilize the current node.
- Continue to subsequent nodes as the route gets longer and more unstable.

## Interaction pattern
- **Mobile-first touch controls**:
  - drag on the left side of the screen to steer movement with a virtual joystick,
  - tap on the right side to jump when grounded.
- The movement model rewards:
  - preserving momentum,
  - lining up jumps,
  - correcting drift in mid-run.
- UI messaging frames actions as cyber-network traversal rather than literal platforming.

## Core systems
### 1. Procedural lane / platform generation
- A large starting platform is created first.
- A chain of rectangular platforms is generated forward on the Z axis.
- Each platform has variable:
  - forward gap,
  - width,
  - depth,
  - horizontal offset.
- Difficulty scaling increases route instability after node 5.
- A large finish platform ends each level.

### 2. Movement and jump physics
- The player has velocity on X, Y, and Z axes.
- Left-side drag input applies acceleration in world space.
- Friction dampens motion every frame.
- A max speed cap limits runaway velocity.
- Gravity pulls the player down continuously.
- Jumping applies an upward impulse only when grounded.

### 3. Collision and fail/win checks
- Collision checks test whether the player overlaps any platform footprint.
- Grounding occurs when the avatar is within landing height and descending.
- Reaching the finish platform triggers victory.
- Falling below a threshold triggers game over.

### 4. Camera and pseudo-3D projection
- The world is represented in simple 3D coordinates.
- A custom `project()` function converts world positions to screen space.
- The camera follows behind the player for a forward sprint perspective.
- Platforms are rendered with top faces and side faces to simulate depth.

### 5. Feedback systems
- Background music during play.
- Jump, land, win, loss, and UI click sounds.
- Particle bursts on jump.
- Fail/win GIF reactions.
- HUD level readout and difficulty badge.
- Strong color shift in harder stages to signal danger escalation.

## Inferred genre / gameplay shape
This is best described as a **mobile-friendly 3D platform runner / obstacle route game** with endless-runner-adjacent structure, but organized into discrete procedural levels rather than a continuous infinite run. The strongest gameplay identity is:
- forward route traversal,
- jumping across gaps,
- steering on narrow platforms,
- escalating difficulty through more hazardous platform spacing.

## Gameplay heuristic
The intended play heuristic appears to be:
- build forward momentum,
- keep the avatar centered on each platform,
- anticipate lateral offsets in upcoming platforms,
- tap to clear gaps only when the landing line is stable,
- treat higher levels as precision movement challenges rather than speed-only runs.

## Confidence notes
High confidence in the control model, win/loss conditions, and progression shape because they are explicit in code. Moderate confidence on genre labeling because the game mixes runner language (“Signal Sprint”) with platformer traversal, but the presence of discrete nodes, direct steering, jumping, and gap-based failure makes “platformer runner” the most grounded interpretation.
