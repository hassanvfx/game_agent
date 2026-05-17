# Blueprint

## High-level code structure
- The game is a self-contained single-page browser project in `index.html`.
- HTML defines the full-screen canvas, HUD, start/game-over overlays, audio elements, config script, and animated GIF feedback nodes.
- CSS establishes the neon streamer/chat aesthetic, responsive layout rules, glass panels, HUD styling, and overlay animation behavior.
- JavaScript contains all runtime systems: audio management, config loading, input handling, state management, spawning, update/draw loop, particles, and UI transitions.

## Game loop / state model
- Core states:
  - `START`
  - `PLAYING`
  - `GAMEOVER`
- `DOMContentLoaded` initializes config, audio, resizing, input, and launches `requestAnimationFrame(gameLoop)`.
- `gameLoop(timestamp)` computes delta time, runs `update(dt)`, then `draw()`.
- `startGame()` resets score, hype, combo, entities, and speed, swaps UI visibility, starts BGM, and spawns the first message.
- `gameOver()` stops BGM, shows the fail overlay, stores the final score, and moves the game into the game-over state.

## Player goals
- Clear as many incoming chat posts as possible.
- Match each falling post to the correct action before it reaches the bottom action line.
- Maintain the hype meter, which acts as the survival resource.
- Build score and combo while surviving increasing speed and feed density.

## Interaction pattern
- Real-time single-screen input via pointer/touch/click.
- Three large bottom buttons represent actions mapped to message categories:
  - `BLOCK` for troll/spam posts
  - `BOOST` for positive fan posts
  - `RIDE` for meme/joke posts
- Pressing a button acts on the lowest active message nearest the bottom, so play is about timing and rapid classification rather than selecting arbitrary targets.
- Correct matches grant score, combo, hype recovery, particles, SFX, and success GIF feedback.
- Wrong matches or ignored posts reduce hype, break combo, shake the screen, and trigger fail feedback.

## Core systems
- **Spawn system:** falling chat bubbles are generated on a timer with randomized text pulled from type-specific pools.
- **Classification mechanic:** every message belongs to one of three fixed categories with a matching button/action.
- **Priority targeting rule:** input always resolves against the lowest active message, making the experience feel like a streamer-themed reaction lane game.
- **Score/combo system:** score increases on success, with combo adding extra reward.
- **Pressure meter:** hype continuously decays and is further damaged by mistakes and misses.
- **Difficulty scaling:** `gameSpeed` rises with score, increasing movement speed and spawn pressure.
- **Feedback system:** BGM, SFX, warning tone, particles, floating score text, canvas shake, bar color changes, and reaction GIFs.
- **Responsive/mobile layout:** canvas fills the viewport and action buttons resize to screen width, indicating mobile-safe intent.

## Inferred genre / gameplay shape
- Casual arcade survival game centered on reflex classification.
- Strong rhythm/timing-adjacent feel because inputs are tied to the lowest approaching item and three persistent bottom actions.
- Theme is modern streamer/chat moderation rather than literal music rhythm or realistic simulation.
- Session loop is score attack: start a run, survive as long as possible, lose when hype empties, and retry immediately.
