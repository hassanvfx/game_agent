# Blueprint: Zero Contact

## High-level code structure
- A single-file HTML game with inline CSS and JavaScript.
- Presentation is split into:
  - **Canvas playfield** for all gameplay rendering.
  - **DOM UI layer** for start screen, game-over screen, HUD, mute button, and animated feedback overlay.
  - **AudioManager** class for background music, UI sounds, warning cues, and defeat sounds.
- The code is organized around a small set of global state variables and plain objects instead of modules.

## Game loop / state model
- The game uses `requestAnimationFrame(loop)` as the main loop.
- Main states:
  - **MENU**: player is centered, start panel visible.
  - **PLAY**: score increases over time, enemies spawn, player movement updates, collisions are checked.
  - **GAMEOVER**: play stops, final survival score is shown, restart becomes available.
- `update(dt)` handles simulation:
  - survival score increments over time
  - difficulty multiplier rises with score
  - player position eases toward the latest pointer/touch location
  - enemies spawn faster over time
  - warning state triggers when enemies get too close
  - collision with any enemy ends the run
- `draw()` handles all rendering:
  - sci-fi background gradients and grid
  - player core and motion trail
  - pulsing hostile shapes
  - explosion particles

## Player goals
- Keep the glowing central core alive as long as possible.
- Avoid all incoming red breach objects.
- Maximize survival time, which acts as the score.

## Interaction pattern
- Primary interaction is **drag / move pointer to steer**.
- Mouse movement continuously updates the target location on desktop.
- Touch movement and touch start update the same target on mobile.
- The player object does not teleport; it drifts smoothly toward the input point, making movement feel inertial and evasive rather than grid-based or instantaneous.

## Core systems
- **Survival scoring**: score rises continuously based on elapsed time.
- **Difficulty scaling**: enemy spawn rate and enemy speed increase with score.
- **Enemy spawning**: enemies appear from random screen edges and travel inward with slight lateral variation.
- **Proximity warning**: close enemies trigger audio plus a temporary animated warning overlay.
- **Collision defeat**: any direct contact between player core and enemy ends the run.
- **Visual juice**: trail echoes, pulsing enemies, particle bursts, neon gradients, and scanline/grid effects.
- **Audio feedback**: BGM during play; warning, impact, and defeat sounds for state transitions.
- **Simple replay loop**: start, survive, lose, immediately retry.

## Inferred genre / gameplay shape
- Strongly reads as a **survival dodge / arena avoidance game**.
- Structurally closest to a minimalist **wave survival** or **arcade survival** experience with no attacks, only movement and evasion.
- It is not level-driven; progression is endurance-based and score-driven.
- The presentation leans neon sci-fi, abstract cyber-defense, and “hold out as long as possible” arcade play.

## Gameplay heuristic
- Early play is about establishing smooth circular movement and keeping distance from edges where enemies emerge.
- Mid-run pressure comes from rising spawn density rather than new mechanics.
- Optimal play likely favors constant motion, broad arcs, and avoiding overcorrection because the player drifts toward input instead of snapping instantly.
- The game’s tension comes from near-miss management, warning anticipation, and gradually shrinking safe space.

## Inference confidence
- **High confidence** on the game loop, controls, scoring, and failure condition because these are explicit in code.
- **Moderate confidence** on intended fantasy/theme language (“radiant core,” “breach containment”) because that framing comes from UI copy and visual treatment rather than deep narrative systems.