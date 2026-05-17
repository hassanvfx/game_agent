# Blueprint

## High-level code structure
The game is implemented as a single self-contained HTML document with three main layers:

1. **Presentation layer**
   - Inline CSS defines a neon sci-fi visual style, glassmorphism HUD panels, responsive layout rules, and game-over modal styling.
   - Tailwind is loaded, but the core look and game-specific behavior are handled with custom CSS.

2. **DOM/UI layer**
   - A full-screen `<canvas>` renders the active playfield.
   - Overlay UI elements show score, lives, floating reaction cards, and the game-over screen.
   - Audio elements are declared in the DOM and triggered by JavaScript for music and SFX.

3. **Game logic layer**
   - Inline JavaScript manages config, state, entities, spawning, scoring, lives, particles, feedback, input, and the requestAnimationFrame loop.
   - The code uses lightweight object-oriented entities (`Target`, `Particle`, `FloatingText`) plus global arrays and state variables.

## Game loop / state model
The state model is simple and arcade-oriented:

- **BOOT**
  - Initial transient setup state before active play.
- **PLAYING**
  - Main gameplay state.
  - Targets spawn over time.
  - Falling targets update each frame.
  - Input is accepted and collisions are checked against pointer taps.
  - Score, particles, floating text, and lives are updated continuously.
- **GAMEOVER**
  - Triggered when lives reach zero.
  - Background music stops, game-over SFX plays, and a retry modal appears.
  - Restart resets score, lives, difficulty, entities, and feedback.

### Main loop behavior
The `gameLoop()` function:
- Computes delta time
- Updates spawn timing and difficulty while playing
- Updates targets, particles, and floating texts
- Applies camera shake decay
- Calls `draw()`
- Schedules the next frame with `requestAnimationFrame`

This is a classic real-time arcade loop rather than turn-based or level-based flow.

## Player goals
The player’s goal is to survive as long as possible and earn a high score by tapping the correct falling shapes before they reach the bottom.

Specific goals:
- **Destroy normal targets** for steady points
- **Hit bonus targets** for larger score gains
- **Avoid dangerous red hazard targets**, because tapping them costs a life
- **Prevent non-hazard targets from falling off-screen**, because missed safe/bonus targets also cost a life

The session ends after three mistakes.

## Interaction pattern
The interaction model is direct and minimal:

- **Primary input:** pointer/tap anywhere on the canvas
- The player taps falling objects to resolve them instantly
- Hit detection checks whether the tap falls within a target’s radius
- There is no movement avatar, no drag interaction, and no aiming reticle beyond direct touch/click

This makes the game feel like a reflex-heavy **tap-to-pop arcade survival game**.

## Core systems
### 1. Target spawning system
Targets are spawned at intervals from the top of the screen with randomized:
- size
- horizontal position
- vertical speed
- rotation
- target type

Spawn rate tightens over time through a rising difficulty multiplier.

### 2. Target type system
There are three inferred gameplay object classes:

- **Normal target**
  - Most common
  - Cyan neon styling
  - Worth 10 points
  - Safe and desirable to hit

- **Bonus target**
  - Less common
  - Yellow/gold styling
  - Worth 50 points
  - Safe and highly valuable to hit

- **Hazard target**
  - Red triangular styling
  - Dangerous to tap
  - Does not penalize the player if it falls off-screen
  - Costs a life if clicked

This creates a fast friend/bonus/foe recognition loop.

### 3. Life and fail-state system
The player begins with three lives.
A life is lost when:
- a safe target reaches the bottom, or
- the player taps a hazard target

When lives reach zero:
- state changes to `GAMEOVER`
- the final score is shown
- the player can restart immediately

### 4. Scoring and progression system
Scoring is endless-session based:
- normal targets: +10
- bonus targets: +50

Progression comes from increasing intensity rather than new stages:
- spawn cadence accelerates
- falling pressure increases
- more simultaneous threat recognition is required

### 5. Juice/feedback system
The game strongly emphasizes arcade feedback:
- particle explosions on hits
- floating score text
- screen shake
- vibration/haptics
- layered hit/bonus/fail/game-over audio
- animated reaction cards with remote GIFs
- glowing neon canvas rendering

This reinforces a punchy “shatter” fantasy even though the mechanics are simple.

### 6. Responsive/mobile-safe system
The layout is designed for phones and touch devices:
- fullscreen canvas
- safe-area-aware padding
- touch-action suppression on the canvas only during play
- HUD and reaction cards adapt to smaller widths
- pointer input works for both mouse and touch-style interactions

## Inferred genre / gameplay shape
Strongest inferred shape:
- **Arcade reflex tap game**
- **Endless survival score attack**
- **Hazard discrimination / reaction game**

Closest abstract genre reading:
- a minimalist **clicker-style arcade action game**, not an idle clicker
- visually adjacent to neon arcade/mobile score chasers
- mechanically similar to “tap the good targets, avoid the bad ones” survival loops

## Gameplay heuristic
The player constantly evaluates three questions in a short time window:

1. **Is this target worth tapping?**
   - cyan = yes
   - gold = definitely yes
   - red triangle = no

2. **Can I clear it before it escapes the bottom?**
   - missing safe targets is punished

3. **Can I maintain rhythm as spawn pressure increases?**
   - the game becomes a stress test of speed and recognition

This makes the experience feel like a high-tempo, neon-skinned target triage game where fast recognition matters more than precise movement.

## Inference confidence
Confidence is **high** on:
- overall loop
- state model
- scoring/lives
- object roles
- endless arcade survival framing
- touch-first interaction style

Confidence is **moderate** on:
- narrative fiction, because the “system fail / breach / stabilize the lane” language implies a digital-grid defense premise but does not define a full story world

## Abstracted vision
“Neon Shatter” appears to be a polished single-screen mobile arcade game where glowing geometric objects rain down a cyber-grid. The player rapidly taps safe and bonus targets to score while avoiding hazardous red traps. Pressure escalates endlessly through faster spawning, with failure measured in three lives. The overall feel is a compact, replayable, audio-reactive score attack built for quick sessions and strong visual feedback.