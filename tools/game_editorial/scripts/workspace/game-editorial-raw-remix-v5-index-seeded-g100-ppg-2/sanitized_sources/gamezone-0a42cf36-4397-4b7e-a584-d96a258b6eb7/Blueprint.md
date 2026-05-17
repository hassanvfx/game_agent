# Blueprint

## High-level code structure
This game is implemented as a single self-contained HTML document with embedded CSS and JavaScript.

- **Presentation layer**
  - Full-screen `canvas` for the active playfield.
  - HUD overlays for score and lives.
  - Start and game-over overlays built with HTML/CSS panels.
  - Neon arcade styling with retro fonts, gradients, glass panels, and animated feedback GIFs.
- **Configuration layer**
  - Inline config definitions exposed on `window.gameConfigDefs` and `window.gameConfig`.
  - Tunable variables include chef movement speed, item spawn rate, and a theme color.
- **Audio layer**
  - `AudioManager` handles Web Audio setup, sound loading, playback, fallback synthesis, BGM volume, and unlock-on-input behavior.
- **Gameplay layer**
  - Canvas-based entity simulation for the player, falling items, particles, and floating score text.
  - Main functions: `resize`, `spawnItem`, `update`, `draw`, `gameLoop`, `startGame`, `endGame`, and `handleInput`.

## Game loop / state model
The game uses a lightweight arcade state machine:

- **START**
  - Start overlay is visible.
  - HUD is hidden.
  - The chef is centered and waiting for input.
- **PLAY**
  - `requestAnimationFrame(gameLoop)` drives updates and rendering.
  - Each frame:
    - player position eases toward the current pointer/touch x-position
    - spawn timer counts down
    - falling items move downward
    - collisions are checked
    - score, lives, combo timer, particles, and floating text are updated
    - HUD text is refreshed
    - scene is redrawn on canvas
- **GAMEOVER**
  - Triggered when lives reach zero.
  - HUD hides, results overlay appears, final score is shown, game-over audio plays, and a success/fail feedback GIF is shown based on final score.

This is an **end-on-failure score attack loop**, not a level-based progression structure.

## Player goals
The player’s immediate goal is to:

- move the chef horizontally
- catch valuable falling ingredients
- avoid harmful falling hazards

The player’s meta-goal is to:

- survive as long as possible with 3 lives
- accumulate the highest possible virtual dollar total
- maintain streaks by catching multiple good items in succession

The HUD suggests a **service goal of $1,000**, but the code’s hard fail condition is losing all lives rather than hitting a hard win state.

## Interaction pattern
The game is built around a simple one-axis real-time interaction model:

- **Input**
  - pointer or touch input
  - player drags/taps horizontally across the screen
- **Movement**
  - the chef smoothly follows `targetX`
  - no jumping, aiming, or multi-button actions
- **Collection / avoidance**
  - good falling objects increase score
  - bad falling objects reduce lives
- **Feedback**
  - floating score text
  - particles
  - screen shake on mistakes
  - reward/fail GIF flashes
  - retro arcade SFX and looping music

This creates a very accessible **pick-up-and-play dodge-and-collect pattern**.

## Core systems
### 1. Player movement system
- Horizontal-only movement.
- Smoothed interpolation toward pointer position.
- Clamped within screen bounds.

### 2. Falling item spawn system
- Items are chosen from a mixed pool of good and bad types.
- Good items are more common than hazards.
- Spawn cadence is controlled by `spawnRate`.

### 3. Scoring system
- Good items award fixed cash values:
  - tomato: 10
  - cheese: 20
  - steak: 50
- Score is displayed as money with two decimal places.

### 4. Health / fail-state system
- Player starts with 3 lives.
- Catching a bad item subtracts one life.
- Reaching 0 lives ends the run.

### 5. Combo / streak system
- Consecutive good catches increase `combo`.
- Combo expires after 2 seconds without continuing the streak.
- At combo 3+, the game plays a bonus sound and shows a combo floater.
- Combo does not appear to multiply score directly, but it affects feel and reward feedback.

### 6. Juice / feedback system
- Particle bursts on catches and mistakes.
- Floating text for points, misses, and combo.
- Screen shake after bad catches.
- Animated success/failure reaction GIFs.
- Audio warnings at low lives and a dedicated game-over cue.

### 7. Session/reset system
- Start button begins a run.
- Restart button fully resets score, lives, items, particles, combo, and UI visibility.
- BGM is re-used across sessions with volume changes by state.

## Inferred genre / gameplay shape
Strongest inferred shape:

- **Arcade catch-and-dodge game**
- **Single-screen survival score attack**
- **Casual reflex game with kitchen theme dressing**

Although the theme frames the player as a chef catching ingredients, the actual mechanic is not cooking simulation in a system-heavy sense. It is closer to:

- lane-lite or free-horizontal **catcher gameplay**
- **endless arcade survival**
- **reaction-based collection/avoidance**

## Heuristic gameplay summary
A neon-styled chef stands at the bottom of the screen while food and hazards rain down from above. The player swipes or moves the pointer left and right to catch profitable ingredients and avoid harmful junk. Each correct catch raises a virtual cash total, repeated catches build combo excitement, and mistakes cost lives. The run continues until all 3 lives are lost, then the player sees a final shift total and can instantly restart for another high-score attempt.

## Confidence notes
- **High confidence** in the real-time loop, player goal, score/lives structure, and interaction model because these are explicit in code.
- **Medium confidence** that the intended fantasy is “chef prep line” rather than full restaurant management because the UI language supports it, but mechanics stay abstract and arcade-focused.
- **High confidence** that this should be classified as an arcade collection/avoidance game rather than a deep cooking simulator.