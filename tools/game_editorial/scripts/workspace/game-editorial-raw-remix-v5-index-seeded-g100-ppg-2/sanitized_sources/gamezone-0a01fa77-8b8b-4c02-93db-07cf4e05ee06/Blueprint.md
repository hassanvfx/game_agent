# Blueprint

## High-level code structure
This game is a single-file browser arcade game implemented entirely in `index.html` with three layers:

1. **Presentation layer**
   - Inline CSS defines a neon sci-fi visual language, glassmorphism menus, HUD chips, animation keyframes, and responsive mobile-safe layout.
   - HTML contains the canvas, start screen, game-over screen, HUD, and a small feedback GIF panel.

2. **Media/UI layer**
   - Remote audio elements provide looping music and discrete SFX for start, restart, warning, score, and crash moments.
   - DOM-driven UI toggles between start, active-play HUD, and game-over overlays.
   - GIF feedback is used as lightweight reward/failure reinforcement.

3. **Gameplay/runtime layer**
   - Inline JavaScript owns configuration, mutable game state, input handling, entity arrays, procedural obstacle generation, collision detection, audio orchestration, and the main animation loop.
   - Rendering is fully custom through a 2D canvas context.

## Game loop / state model
The runtime follows a classic requestAnimationFrame loop:

- `init()` sets up canvas sizing, input listeners, button handlers, and starts the animation loop.
- `loop(timestamp)` calculates delta time, then calls:
  - `update(dt)` for simulation/state changes
  - `draw()` for full-frame rendering
- `startGame()` initializes a fresh run.
- `resetGame()` returns the UI to pre-run state.
- `gameOver()` freezes play, triggers audio/particles/feedback, updates high score, and reveals the game-over screen after a short delay.

### State model
The central `state` object tracks:
- play/game-over flags
- score and high score
- current scroll speed
- tunnel gap size
- screen shake
- total distance
- current tunnel centerline (`tunnelY`)
- procedural obstacle mode (`normal`, `jagged`, `tight`)
- mode timer

Related runtime data:
- `input.holding` for press/hold flight control
- `player` object with position, vertical speed, angle, and trail
- `obstacles[]` for tunnel wall segments and later spikes
- `particles[]` for crash feedback
- milestone/warning buckets to debounce feedback events

## Player goals
The player’s goal is to keep a courier craft alive as long as possible while traveling through a hostile scrolling corridor.

Immediate goals:
- stay within the moving tunnel gap
- avoid touching top/bottom bounds
- dodge corridor wall segments and spike hazards
- keep up as speed increases and openings shrink

Longer-term goal:
- maximize packet score / distance
- beat the previous best run

## Interaction pattern
The interaction model is one-button continuous control:

- **Hold / press:** the craft climbs upward
- **Release:** the craft drops downward

Supported inputs:
- mouse press/release
- touch press/release
- start/restart buttons for run lifecycle

This creates a rhythmic altitude-control play pattern similar to “tap to stay in lane/gap” arcade survival games, but with sustained hold behavior instead of discrete flaps.

## Core systems
### 1. Procedural tunnel generation
Obstacle segments are generated ahead of the player as paired top/bottom blocks that define a safe passage gap. The tunnel center drifts according to procedural modes:

- **normal:** moderate random movement
- **jagged:** sharper zig-zag shifts
- **tight:** flatter movement with narrower openings

This creates a scrolling “firewall tunnel” rather than handcrafted levels.

### 2. Difficulty escalation
Difficulty rises continuously over a run through:
- increasing horizontal scroll speed
- shrinking safe gap size
- warning signals at higher speed tiers
- spike hazard injection after score threshold

The result is an endless survival curve rather than stage-based progression.

### 3. Collision and fail state
The player loses when:
- moving outside vertical screen bounds
- colliding with wall blocks
- colliding with a spike hazard

On failure, the game triggers:
- loop music stop
- crash SFX and synth burst
- shake and particle explosion
- fail GIF
- final score + best score display

### 4. Feedback and reward system
Positive and negative feedback is layered across several channels:
- HUD score counter
- “TRACE SPIKE!” warning banner
- reward/fail GIF flashes
- score milestone SFX
- warning SFX
- crash effects

### 5. Visual rendering system
The canvas renderer draws:
- animated gradient background
- parallax waveform bands
- moving grid overlays
- glowing tunnel walls
- rotating spike hazards
- the courier ship with tilt and thrust state
- player trail
- particles on destruction

## Inferred genre / gameplay shape
Strongest inferred genre shape:
- **Arcade endless runner / lane-avoidance survival hybrid**

More specifically, this feels like:
- a side-scrolling endless survival flyer
- a “hold to ascend, release to descend” dodge game
- a neon cyber-tunnel reflex challenge

It is not level-based or narrative-heavy. The primary loop is immediate skill execution, score chasing, and short-session retry play.

## Progression heuristic
Progression is run-based and intensity-based rather than content-unlock-based:

1. Start run
2. Survive early readable tunnel
3. Adjust to rising speed
4. React to sharper tunnel patterns
5. Handle narrower gaps
6. Encounter spike hazards after deeper progression
7. Fail, review score, restart instantly

This implies:
- very fast restarts
- short-to-medium session length
- replayability through procedural variance and personal score improvement

## Theme, tone, and fantasy
The game frames play as a cyberpunk data-delivery mission:
- you are a neon courier craft
- the corridor reads as a digital firewall/data stream
- scoring is expressed as “packets”
- failure is “link dropped”
- speed surges are “trace spike” warnings

Tone:
- urgent
- stylish
- futuristic
- high-contrast
- twitchy but readable

## Gameplay heuristic summary
If recreating this game, preserve these heuristics first:

- one-touch altitude control with instant response
- fixed horizontal player position and auto-scrolling world
- continuously generated top/bottom tunnel segments
- rising speed plus shrinking safe space
- clear audiovisual warning when intensity spikes
- score-chasing endless loop with immediate restart
- strong neon cyberpunk readability and feedback-driven polish