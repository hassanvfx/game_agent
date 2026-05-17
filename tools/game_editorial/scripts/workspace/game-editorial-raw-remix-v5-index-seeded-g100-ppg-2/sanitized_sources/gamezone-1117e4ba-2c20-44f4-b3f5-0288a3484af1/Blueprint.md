# Blueprint

## High-level code structure
The game is implemented as a single self-contained `index.html` file with three major layers:

1. **Presentation / UI layer**
   - Full-screen HTML overlays for start, pause, and game-over states.
   - HUD for score, best score, status prompts, pause control, joystick, and action button.
   - CSS establishes a neon cyber-sports visual identity with mobile-safe layout, large touch targets, and animated feedback cards.

2. **Rendering / scene layer**
   - Uses Three.js as an ES module loaded directly from CDN.
   - Builds a compact 3D arena with:
     - floor and glowing lane strip
     - hoop / uplink structure
     - player avatar
     - floating collectible core
     - roaming drone hazards
   - Camera is third-person and elevated, following the player during play.

3. **Game logic layer**
   - Central `state` object tracks screen mode, score, input, player physics flags, active collectible, obstacle list, and hoop position.
   - Procedural spawn functions place the collectible core and hazards.
   - A requestAnimationFrame loop updates physics, gameplay checks, camera, and scene flavor.
   - Audio is handled with pooled HTMLAudio elements and gesture-based unlock logic.

## Game loop / state model
The runtime state is small and explicit.

### Screen states
- `start`
- `playing`
- `paused`
- `gameover`

### Core loop while playing
Each animation frame:
1. Compute delta time.
2. Update player motion and jump/dunk behavior.
3. Update collectible bobbing and pickup checks.
4. Move drone hazards and check collisions.
5. Update context-sensitive action button state (`JUMP` vs `JACK IN`).
6. Move the camera toward a trailing overhead follow position.
7. Render the scene.

### Progression state
- Score increases by 1 per successful dunk.
- Best score persists only for the current session/runtime.
- Every second successful score spawns an additional drone, increasing pressure.
- Game ends immediately on collision with a drone while near ground level.

## Player goals
The player goal is a repeating three-step loop:

1. **Move through the arena to reach the floating core**
2. **Collect the core**
3. **Reach the hoop/uplink zone and trigger a dunk/jack-in**
4. **Repeat while avoiding drones for as long as possible**

This makes the game score-chasing and survival-based rather than level-completion based.

## Interaction pattern
The interaction model is optimized for touch/mobile play:

- **Virtual joystick** on the lower left controls movement across the arena.
- **Single action button** on the lower right is context-sensitive:
  - jumps when empty-handed
  - attempts a dunk/jack-in when carrying the core near the hoop
- **Pause button** in the HUD toggles pause state.
- Start, resume, retry, quit, and menu interactions are button-driven overlays.

The action pattern is therefore:
- steer
- collect
- reposition
- time action input
- avoid hazards
- repeat faster under growing obstacle density

## Core systems
### 1. Movement and physics
- Player velocity uses smoothing/friction toward joystick target velocity.
- Gravity and grounded checks create simple arcade jumping.
- Arena bounds clamp player movement within the court.

### 2. Collectible objective system
- A glowing floating object is spawned at a random forward-side position.
- Touching it while not carrying one marks the player as holding the objective.
- The held-core visual appears attached to the player.

### 3. Goal / scoring system
- The hoop is the scoring destination.
- If the player is carrying the objective and is within dunk range, the action input triggers a successful dunk.
- Dunking:
  - increases score
  - removes held core
  - creates particle burst
  - respawns a new collectible
  - sometimes adds another hazard

### 4. Hazard system
- Drone-like obstacles spawn and roam with randomized velocities.
- Hazards bounce off arena limits.
- Collision with a drone causes immediate game over.

### 5. Feedback system
- HUD status text tells the player whether to fetch the core or reach the uplink.
- Animated GIF cards reinforce success/failure moments.
- Audio cues support start, jump, pickup, dunk, pause/resume, blocked action, landing, and game over.

### 6. Camera and spectacle
- Camera is a smooth elevated chase camera during gameplay.
- Start screen uses a rotating showcase camera orbit around the arena.
- Scene flavor includes pulsing hoop halo, rotating player accents, bobbing collectibles, and particles.

## Inferred genre / gameplay shape
This is best understood as a **mobile-friendly 3D arcade sports runner/dunk survival game** with a cyberpunk wrapper.

It blends:
- **arcade basketball dunking**
- **hazard avoidance / survival pressure**
- **arena movement with touch controls**
- **score attack loop**

It is not a realistic basketball simulation. It is a stylized, abstract, score-driven action game where “basketball dunking” is reframed as stealing a data core and slamming it into an uplink.

## Gameplay heuristic
The intended player rhythm appears to be:

- scan arena for core spawn
- take shortest safe path to collect it
- quickly reposition toward the hoop
- decide whether to jump normally or conserve movement
- dunk before drones cut off the lane
- adapt to increased hazard count as score rises

Optimal play likely involves:
- staying mobile and avoiding tight turns near drones
- approaching the hoop only after lining up a safe lane
- minimizing time spent carrying the core
- treating each score as a survival-risk spike because obstacle density grows

## Confidence notes
Confidence is high on the main loop and systems because they are directly expressed in the code. Confidence is moderate on the intended thematic framing because the title text mixes “Cyber Hoops: Dunk Drift” in the document title with “Cyber Heist: Data Run Edition” in the visible start screen, suggesting presentation/theme iteration during development.