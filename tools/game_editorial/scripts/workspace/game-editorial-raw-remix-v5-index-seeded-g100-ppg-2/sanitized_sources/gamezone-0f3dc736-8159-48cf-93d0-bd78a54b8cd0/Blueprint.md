# Blueprint

## High-level code structure
This game is implemented as a single self-contained HTML document with three main layers:

1. **Presentation / layout**
   - Inline CSS defines the full-screen sci-fi presentation, HUD, menu overlays, mobile-safe spacing, and feedback GIF placements.
   - The DOM contains a canvas for gameplay, a HUD for score, a mute button, feedback image slots, and two modal-style screens for start and game over.

2. **Asset and audio setup**
   - A top-level `ASSETS` object defines remote image, audio, and GIF sources.
   - An `AudioManager` class handles preload, mute state, background music looping, UI sounds, and cooldown-limited SFX playback.

3. **Core game logic**
   - Global state tracks the current phase (`START`, `PLAY`, `GAMEOVER`), score, grid layout, projectile, particles, and aim direction.
   - `Bubble`, `Projectile`, and `Particle` classes represent the board pieces, launcher shot, and pop feedback effects.
   - Helper functions handle setup, collision resolution, neighbor lookup on a staggered hex grid, match detection, floating-cluster drops, resizing, drawing, and the animation loop.
   - Mouse and touch listeners convert drag-and-release input into aiming and firing.

## Game loop / state model
The runtime follows a simple arcade state machine:

- **START**
  - Start screen is visible.
  - The player can begin the session with the start button.
- **PLAY**
  - `requestAnimationFrame` drives `loop()`, which calls `update()` then `draw()`.
  - `update()` moves the active projectile, checks wall bounces, resolves collisions with the ceiling or placed bubbles, and updates particles.
  - `draw()` renders the background, atmospheric sky overlay, placed bubbles, launcher base, projectile, particles, and aim guide.
- **GAMEOVER**
  - Triggered when a newly placed bubble reaches the lower danger threshold near the bottom rows.
  - BGM stops, fail feedback plays, the game-over screen appears, and the final score is shown.

The game can also soft-reset into a new round after the player clears the entire field, effectively looping instead of showing a distinct victory screen.

## Player goals
The player is trying to keep the relay field clear by:
- shooting colored signal orbs upward,
- connecting at least 3 matching colors to pop them,
- causing unsupported clusters to fall for bonus points,
- preventing the stack from advancing too low on the screen.

The practical goal is score maximization and survival rather than narrative completion.

## Interaction pattern
The interaction model is a direct, touch-friendly launcher loop:

1. Player presses/drags on the playfield to aim.
2. The launcher angle updates in real time, clamped to upward shots only.
3. On release, a projectile orb fires.
4. The orb bounces off side walls and snaps into the nearest valid grid slot on impact.
5. The game checks for color matches and detached clusters.
6. Score, particles, audio, and animated feedback update instantly.
7. A new projectile spawns and the cycle repeats.

This is optimized for both mouse and mobile touch input.

## Core systems
### 1. Staggered bubble grid
- The board uses an offset-row / hex-neighbor layout rather than a simple square grid.
- Row parity changes the neighbor directions and horizontal offset.
- Bubble positions are recalculated on resize for responsive play.

### 2. Projectile shooting and snapping
- A single active projectile launches from the bottom center.
- It travels with constant velocity, rebounds from left/right walls, and snaps into the grid on impact with the ceiling or existing bubbles.

### 3. Match detection
- Breadth-first search is used to find contiguous same-color bubbles after a landing.
- A group of 3 or more is removed.

### 4. Floating cluster drop logic
- Another BFS starts from the roof-connected top row to determine which bubbles remain anchored.
- Any non-anchored cluster is removed and awards extra points.

### 5. Score and feedback
- Standard matches award `10` points per bubble.
- Detached drops award `20` points per bubble.
- Particles, combo/fail audio, HUD score changes, and celebratory or warning GIFs reinforce outcomes.

### 6. Session flow and fail state
- The board initializes with 5 filled rows of random colors.
- Loss occurs when a newly placed bubble lands at or below the bottom danger band.
- Clearing the board immediately starts a fresh round, making the game feel endless and score-driven.

## Inferred genre / gameplay shape
The code strongly indicates a **bubble-shooter style arcade puzzle game** with:
- color matching,
- bounce-bank shots,
- falling detached clusters,
- endless round looping,
- lightweight score chasing.

Despite the custom fiction wrapper (“Sky Signal Relay” / aurora beacon theme), the mechanical identity is closest to a classic match-and-pop bubble shooter presented with a futuristic sky-relay aesthetic.

## Heuristic reading of the game's fantasy
The game reframes bubble shooter mechanics as a sci-fi communications task:
- colored bubbles become **signal orbs**,
- the playfield becomes a **clouded relay grid**,
- combos feel like restoring or stabilizing an aerial communications network,
- failure is framed as **storm interference** overwhelming the beacon system.

This thematic layer is mostly cosmetic, but it is consistently supported by the naming, UI copy, colors, audio mood, and atmospheric visuals.

## Confidence notes
Confidence is **high** on the core mechanic classification because the code explicitly implements:
- projectile launching,
- wall bounces,
- hex-grid attachment,
- 3+ same-color popping,
- detached-cluster dropping,
- score feedback,
- survival loss threshold.

Confidence is **medium** on narrative framing because the sci-fi “relay” premise is expressed mainly through text, palette, and presentation rather than deeper game systems.