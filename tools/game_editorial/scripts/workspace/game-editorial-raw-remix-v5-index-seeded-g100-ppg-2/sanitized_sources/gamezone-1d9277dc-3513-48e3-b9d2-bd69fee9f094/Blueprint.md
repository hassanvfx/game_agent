# Blueprint

## High-level code structure
- Single-file HTML game with inline CSS, HTML UI, configuration JSON, audio asset declarations, and all gameplay logic in one embedded script.
- Rendering is handled with a full-screen HTML5 canvas.
- UI overlays are regular DOM elements layered above the canvas for HUD, feedback banners, reaction GIFs, and the game-over modal.
- The game uses lightweight class-based entities (`Particle`, `Ingredient`) plus global state variables for score, lives, timers, difficulty, and current mode.

## Game loop / state model
- Main states are `INIT`, `PLAYING`, and `GAMEOVER`.
- `resize()` initializes the canvas, starts the game once, and kicks off `requestAnimationFrame(loop)`.
- `loop()` computes delta time, updates simulation only while in `PLAYING`, always redraws the scene, and self-recovers from loop errors.
- `update()` handles timed spawning, falling ingredient motion, missed-item penalties, and particle cleanup.
- `draw()` renders the kitchen-themed background, counter, decorative lights/grid, then ingredients and particles.
- State transitions are centralized through `setState()`, which toggles HUD visibility, game-over screen, and music playback.

## Player goals
- Tap falling fresh ingredients before they leave the bottom of the screen.
- Avoid tapping rotten ingredients.
- Survive as long as possible with 3 lives while increasing the order count/score.
- Maintain streaks for positive feedback and a feeling of kitchen momentum.

## Interaction pattern
- Primary interaction is single-pointer tapping/clicking on falling circular targets.
- A hit checks collision against the top-most ingredient under the pointer.
- Good taps remove fresh food, play chop/score feedback, spawn celebratory particles, and add score.
- Bad taps on rotten items or allowing fresh items to fall off-screen cost a life.
- Tapping empty space does not remove life, but it breaks combo momentum and triggers warning feedback.

## Core systems
- **Spawn system:** Ingredients appear on a timer, with spawn interval clamped and sped up by difficulty.
- **Difficulty ramp:** `difficultyMultiplier = 1 + score / 500`, increasing fall speed pressure and effective spawn pace over time.
- **Entity system:** Falling ingredient objects and short-lived particle effects.
- **Scoring/combo system:** Fresh hits give 10 points; combo streak messaging starts at 3 consecutive successes.
- **Life/failure system:** The player starts with 3 mistakes; life loss comes from missed fresh items or tapping rotten ones.
- **Audio/haptics system:** Background loop plus SFX for chop, score, warning, fail, and UI; vibration hooks exist for supported environments.
- **Presentation feedback:** Banner callouts, shake effect, success/failure GIF overlays, HUD counters, and a restart modal.

## Inferred genre / gameplay shape
- Arcade reflex game centered on rapid target tapping.
- Best described as a casual cooking-themed click/tap action game with survival scoring pressure.
- Structurally similar to “fruit slicing / ingredient chopping” lane-less tap survival games, but without swipe slicing; it is discrete tap-to-hit gameplay.
- Session shape is short, score-chasing, and endless until mistakes are exhausted.

## Gameplay heuristic
- The player visually scans the whole screen for descending ingredients.
- Priority is to quickly identify safe targets (fresh items) and ignore hazards (rotten items).
- Higher scores imply faster reaction speed and stronger discrimination under increasing spawn density.
- The intended feel is a busy prep line: quick correct taps, accumulating streak hype, and sudden collapse after repeated kitchen mistakes.
