# Blueprint

## High-level code structure
- Single-file browser game in `index.html` containing:
  - HTML shell with a full-screen `<canvas>`, HUD, status chip, game-over overlay, and audio tags.
  - Embedded CSS defining a neon sci-fi presentation, responsive HUD, and overlay panels.
  - Embedded JavaScript implementing the full game loop, state transitions, input handling, spawning, rendering, particles, HUD updates, and audio control.
- Lightweight tuning surface via the `#game-config` JSON script block:
  - `heroSpeed`
  - `enemyBaseSpeed`
- No module system or asset pipeline is used at runtime; all gameplay logic is handled inside an IIFE.

## Game loop / state model
- Core state values:
  - `PLAYING`
  - `GAMEOVER`
- Main loop:
  - `requestAnimationFrame(loop)` drives the game continuously.
  - `update(dt)` advances score, difficulty, enemy spawning, input-follow movement, collision checks, particles, grid scrolling, and HUD timing.
  - `draw()` renders the scrolling grid, player courier, falling jammer obstacles, and explosion particles to canvas.
- Setup flow:
  - `DOMContentLoaded` initializes audio, attaches a `ResizeObserver`, and binds pointer input.
  - `initGame()` resets score, difficulty, enemies, particles, warnings, and player position.
  - `setState()` toggles HUD vs. game-over overlay visibility and final score output.
- Progression model:
  - Score rises over time as a survival-distance metric.
  - Difficulty increases in steps based on score.
  - Enemy spawn rate accelerates and enemy fall speed scales upward with difficulty.

## Player goals
- Stay alive as long as possible.
- Move the courier horizontally to avoid descending jammer blocks.
- Push distance score higher and survive into higher “zones.”

## Interaction pattern
- Primary input is pointer/touch.
- On pointer down or pointer move, the player sets a horizontal target position.
- The courier slides toward that X position with speed limited by configurable hero speed.
- On game-over, any pointer down or pressing the restart button restarts the run.
- Audio unlock is tied to first user interaction, making it mobile-browser friendly.

## Core systems
- **Survival scoring:** distance increases continuously over time.
- **Difficulty ramp:** zone count and spawn cadence scale with score.
- **Obstacle spawning:** square jammers spawn at random X positions above the screen and fall downward with slight rotation.
- **Collision detection:** axis-aligned overlap check between courier and jammers.
- **Feedback layer:** danger status chip appears when a jammer reaches the lower screen region; zone changes and death trigger SFX; game-over shows a reaction GIF and final distance.
- **Screen juice:** camera shake, glow, scrolling grid, and particle explosions reinforce collisions and speed.
- **Responsive presentation:** canvas fills viewport, HUD scales with clamps, and touch input is explicitly supported.

## Inferred genre / gameplay shape
- Arcade survival dodging game.
- Strongly resembles a minimalist lane-less runner / falling-obstacle avoidance game.
- Session structure is endless until collision, with score-chasing replayability rather than level completion.
- The tone is neon sci-fi / cyber-arcade, framed as piloting or guiding a courier through a hostile digital descent corridor.

## Gameplay heuristic
- The player is effectively managing horizontal positioning under increasing pressure.
- Danger spikes when obstacles enter the lower third of the screen, so good play means reading incoming lanes early and making small pre-emptive slides rather than last-second panic swerves.
- Difficulty comes from accumulating obstacle density and speed rather than from new rules.
- The game’s fun loop is: spawn into a run, drag left/right, survive longer, hear/see escalating warnings, crash, view distance, restart immediately.