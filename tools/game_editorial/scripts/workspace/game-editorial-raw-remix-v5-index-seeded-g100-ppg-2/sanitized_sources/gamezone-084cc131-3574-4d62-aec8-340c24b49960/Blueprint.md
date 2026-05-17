# Blueprint

## High-level code structure
- Single-file HTML game with embedded CSS, UI markup, configuration JSON, and JavaScript gameplay logic.
- Rendering is handled through one full-screen `<canvas>` for the animated playfield.
- HUD, tutorial text, fail/celebration GIF reactions, and game-over overlay are regular DOM elements layered above the canvas.
- Audio uses one looping background-music `<audio>` element plus cloned `Audio` instances for sound effects.
- Runtime configuration is exposed through a small JSON block for scrub speed and dish freshness/patience duration.

## Game loop / state model
- The game uses `requestAnimationFrame(loop)` as a continuous render/update loop.
- Core state:
  - `PLAYING`
  - `GAMEOVER`
- Main runtime entities:
  - `ingredients`: active dish/food targets to clean
  - `particles`: scrub, dirt, and celebration particle effects
  - `tool`: the player-controlled bubble scrub buddy
  - scalar stats: `score`, `streak`, timers, cooldowns, audio state
- Loop flow:
  1. Update pointer-following movement for the scrub tool.
  2. Determine whether player motion counts as active scrubbing.
  3. Decrease active dish timer.
  4. If the tool is scrubbing over the dish, increase cleanliness.
  5. On full cleanliness, increment score/streak, play clean feedback, replace with a new dish.
  6. If timer reaches zero before cleaning, switch to `GAMEOVER`.
  7. Draw background, counter, decorative bubbles, dish, timer bar, tool, and particles.

## Player goals
- Clean each presented dish before its freshness/patience timer expires.
- Build the highest possible saved-dish count.
- Maintain a streak by repeatedly clearing dishes without letting one spoil.

## Interaction pattern
- Primary interaction is pointer/touch swiping across the screen.
- The scrub buddy trails the player input with smoothing, so the player is effectively steering and agitating the tool.
- Cleaning only happens when the tool is moving fast enough to count as “scrubbing” and overlaps the current dish.
- Restart interaction is handled through a large game-over button for immediate replay.

## Core systems
- **Canvas renderer:** draws environment, food icons, scrub buddy, bars, and particles.
- **Input system:** pointerdown/pointermove/pointerup updates target position; motion delta determines scrubbing.
- **Dish cleaning system:** each dish has `cleanliness`, `maxClean`, `timer`, `maxTimer`, and a `dirty/clean` state.
- **Failure pressure system:** each dish has a countdown; low-time warning audio plays before failure.
- **Scoring system:** score and streak increment on successful cleans.
- **Spawn system:** only one target dish is meaningfully active at a time; a new dish appears after a cleaned one is removed.
- **Feedback system:** particles, haptics, SFX, GIF reactions, HUD counters, and game-over panel reinforce success/failure.
- **Audio management:** background loop, scrub ticks, warning cue, fail sting, UI and start sounds.
- **Responsive presentation:** canvas resizes to viewport; HUD uses safe-area padding and mobile-friendly cards.

## Inferred genre / gameplay shape
- Arcade reflex game with casual swipe controls.
- Time-pressure “clean before expiry” loop.
- Closest shape is a light cooking/cleaning microgame rather than a full restaurant simulator.
- Session structure is endless survival-by-performance: the run continues until a single missed dish ends it.

## Gameplay heuristic
- The player should keep the bubble buddy in near-constant motion, immediately move onto the active dish, and scrub rapidly enough to fill the cleaning meter before the countdown bar empties.
- Success depends more on fast, steady swiping accuracy than on strategic planning.
- The game escalates tension through short timers, warning audio, streak framing, and sudden-death failure.
- Presentation aims for a cute, energetic kitchen-cleanup fantasy with neon-arcade polish and playful food illustrations.