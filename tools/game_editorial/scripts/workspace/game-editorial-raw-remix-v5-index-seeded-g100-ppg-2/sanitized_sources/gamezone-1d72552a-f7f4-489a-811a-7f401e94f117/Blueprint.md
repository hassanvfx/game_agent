# Blueprint

## High-level code structure
The game is implemented as a single self-contained `index.html` file with three major layers:

1. **Presentation / UI layer**
   - Start screen with class selection for three guardian shells: Fury, Winter, and Lighting.
   - In-game HUD showing score and wave.
   - Game-over overlay with final score and retry button.
   - Animated feedback GIF layer for hit and defeat moments.

2. **Rendering layer**
   - A fullscreen HTML5 canvas renders the arena, player, enemies, projectiles, particles, grid lines, cooldown ring, and menu background animation.
   - Visual style is neon sci-fi with glowing gradients, holographic panels, and abstract geometric entities rather than detailed sprites.

3. **Gameplay / systems layer**
   - A requestAnimationFrame loop updates and draws the game.
   - Global state variables track score, wave, game mode, timers, enemies, projectiles, particles, and pointer input.
   - Audio is managed by a lightweight `AudioSys` helper that preloads and plays approved remote sounds and a looping action track.

## Game loop / state model
The game uses a simple finite state flow:

- **MENU**
  - Animated background runs.
  - Player chooses one of three classes.
- **PLAYING**
  - Pointer drag controls movement.
  - Pointer tap fires toward the tap location.
  - Enemies spawn from screen edges and home toward the player.
  - Projectiles apply class-specific effects on hit.
  - Score increases on kills and wave increments every 200 score.
- **GAMEOVER**
  - Triggered instantly when any enemy reaches the player.
  - Shows defeat overlay and final score.
  - Retry returns to menu instead of resuming mid-run.

The main loop:
- computes delta time,
- updates gameplay only during `PLAYING`,
- draws menu ambience during `MENU`,
- continuously requests the next animation frame.

## Player goals
The immediate goal is survival against continuously spawning enemies in a confined arena.

The practical goals are:
- avoid enemy contact,
- aim taps to eliminate approaching threats,
- choose a guardian shell whose attack pattern matches the player's preferred risk profile,
- accumulate score,
- reach higher waves as the spawn pressure escalates.

There is no narrative ending or victory state; progression is score-based survival endurance.

## Interaction pattern
Primary interaction is designed for mobile-first pointer input:

- **Drag and hold**: move the player using a virtual joystick anchored at touch start.
- **Quick tap**: fire one projectile toward the tap point.
- **Menu tap**: choose a class or retry after defeat.

This creates a one-thumb / two-action action loop:
- reposition,
- tap-shot,
- kite enemies,
- repeat.

## Core systems
### 1. Class / loadout system
Three selectable archetypes alter cooldown, projectile size, damage, speed, and special behavior:

- **Fury**
  - heavy damage,
  - long cooldown,
  - explosive area damage.
- **Winter**
  - low damage,
  - rapid fire,
  - slows enemies on hit.
- **Lighting**
  - medium damage,
  - medium cooldown,
  - chain lightning that jumps between nearby enemies.

This is the main source of strategic variety.

### 2. Enemy pressure system
Enemies:
- spawn from random screen edges,
- scale health and speed upward with score,
- move directly toward the player,
- kill on contact.

This produces mounting pressure without complex AI.

### 3. Projectile and hit-resolution system
Each shot:
- travels linearly toward the tap target,
- expires by time or screen bounds,
- checks circle collision against enemies,
- applies direct damage plus status/effect logic.

Impact effects include:
- slow debuff,
- radial explosion splash,
- recursive chain damage.

### 4. Score / wave progression system
- Each kill grants 10 score.
- Wave increases every time score reaches a multiple of 200.
- Spawn interval decreases as score rises, clamped to a minimum threshold.

Wave is therefore more of a pacing indicator than a distinct round structure.

### 5. Feedback system
The game emphasizes arcade readability through:
- glowing color coding per class,
- particle bursts on hits and deaths,
- ring expansion for explosions,
- line bolts for chain attacks,
- hit/defeat GIF popups,
- arcade HUD and defeat stinger audio.

### 6. Audio system
The audio layer supports:
- start-game cue,
- shot sound,
- enemy-hit sound,
- explosion sound,
- chain power sound,
- defeat sound,
- looping combat music.

This reinforces the game's fast arcade tone.

## Inferred genre / gameplay shape
Strongest inferred genre shape:
- **top-down arena survival shooter**

Secondary shape:
- **light wave defense / score attack arcade game**

Why:
- The player survives in a single room-like arena.
- Enemies spawn endlessly and converge from boundaries.
- Player mobility and directional firing define skill expression.
- The run ends on contact, making it feel like a dodge-heavy survival score chase.
- Distinct character kits create soft class-based combat variation without RPG infrastructure.

## Gameplay heuristic
A skilled play heuristic likely looks like this:

1. Select a class based on preferred control rhythm.
2. Stay near open space rather than corners.
3. Drag to maintain distance from converging enemies.
4. Tap only when lined up for efficient hits.
5. Use class strengths deliberately:
   - Fury for burst clearing clustered enemies,
   - Winter for constant kiting and crowd control,
   - Lighting for multi-target cleanup.
6. Preserve spacing as spawns accelerate.
7. Optimize survival duration and score rather than pursuing objectives beyond endurance.

## Confidence notes
Confidence is moderately high because the full gameplay code is visible in one file and clearly names systems, classes, UI states, and attack types. Some ambiguity remains around intended audience framing and whether “wave” is meant as a real round system or just a milestone counter, but the survival arena shooter identity is clear.