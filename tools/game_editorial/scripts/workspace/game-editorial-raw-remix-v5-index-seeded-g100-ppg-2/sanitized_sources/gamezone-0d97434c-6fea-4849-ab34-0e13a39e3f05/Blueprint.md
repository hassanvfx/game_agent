# Cash Flow Rush Blueprint

## High-level code structure
- Single-file HTML game with embedded CSS, configuration JSON, audio tags, UI markup, and all JavaScript logic in `index.html`.
- Rendering is handled through one full-screen `<canvas>` for gameplay visuals.
- HUD and overlays are regular DOM elements layered above the canvas for score, lives, animated feedback cards, and the game-over screen.
- The code is organized informally into sections:
  - visual theme and responsive layout styles
  - runtime config parsing from an embedded JSON block
  - audio initialization and playback helpers
  - game state and entity storage
  - update logic for spawning, movement, collision, scoring, and failure
  - drawing routines for background, player avatar, hazards, rewards, particles, and floating text
  - pointer input and lifecycle bootstrapping

## Game loop / state model
- Main state machine uses three string states: `BOOT`, `PLAYING`, and `GAMEOVER`.
- On `DOMContentLoaded`, the game:
  1. parses config values,
  2. initializes audio,
  3. sizes the canvas,
  4. initializes gameplay values,
  5. switches to `PLAYING`,
  6. starts a `requestAnimationFrame` loop.
- Each frame:
  - computes a capped delta time,
  - updates only if the state is `PLAYING`,
  - redraws the full scene,
  - schedules the next frame.
- `initGame()` resets score, lives, speed scaling, spawn timing, hero position, and transient entities.
- `setState('GAMEOVER')` reveals the fail overlay, freezes gameplay updates, shows final earnings, lowers or pauses music, and plays fail feedback.

## Player goals
- Move the wallet-like player avatar to collect falling money items.
- Prioritize regular cash bills for steady score gains and gold coins for large bonus payouts.
- Avoid falling tax/fine hazards that remove lives.
- Survive as long as possible while increasing total money collected.

## Interaction pattern
- Input is pointer/touch driven.
- The player presses or drags on the canvas to move the avatar target position.
- The avatar eases toward the touch location instead of snapping instantly, making the feel closer to a smooth dodge/catch arcade game.
- Restart is handled through a single button on the game-over overlay.

## Core systems
- **Player controller:** wallet mascot constrained within the visible playfield, with tunable movement sensitivity.
- **Spawner:** periodically creates falling objects, with spawn cadence accelerating as the run continues.
- **Entity system:** stores active falling items, particles, and floating text in arrays.
- **Collision resolution:** radial overlap test between the player and each falling object.
- **Scoring system:** regular money gives +1000, gold gives +5000.
- **Lives system:** player starts with 3 lives; tax hazards remove one life per hit.
- **Difficulty ramp:** `gameSpeed` increases over time, affecting spawn cadence and object fall speed.
- **Feedback system:** particles, floating text, vibration, sound effects, and celebratory/failure GIF cards reinforce outcomes.
- **HUD system:** DOM-based score readout and three life indicators update after each meaningful event.
- **Audio state sync:** looping music during play, event SFX for pickups, damage, UI click, and game over.

## Inferred genre / gameplay shape
- Arcade score-chasing avoidance-and-collection game.
- Closest overall shape: a touch-friendly catch/dodge survival game with casual endless-runner pacing, even though movement is freeform rather than lane-based.
- Session structure is short, replayable, and failure-driven: earn as much as possible before losing all lives.

## Presentation and theme
- Futuristic neon-finance presentation with glowing cyan, mint, and gold accents over a dark city-night backdrop.
- The player avatar is stylized as an animated wallet character with a face, reinforcing a playful money theme.
- Hazards are framed as “TAX” badges and failure as a “market shock,” suggesting light satire around personal finance or money collection.
- HUD typography and gradients give the game a sci-fi arcade look rather than a realistic simulation tone.

## Gameplay heuristic
- The intended player behavior is to stay mobile, track multiple falling items, and make quick risk/reward decisions.
- Regular cash is the baseline target, while gold coins create high-value moments worth path adjustment.
- Tax hazards punish greedy movement and encourage reading trajectories before committing.
- Since speed rises over time and lives are limited, the game is fundamentally about maximizing score under increasing pressure rather than reaching a defined ending.

## Confidence notes
- High confidence on the core mechanic: collect rewards, avoid hazards, survive, and post a score.
- Medium confidence on genre labeling because the game blends free movement with endless arcade survival rather than matching one exact catalog genre.
- High confidence that this node should describe the game as an arcade cash-collection survival experience rather than a tycoon or clicker game.