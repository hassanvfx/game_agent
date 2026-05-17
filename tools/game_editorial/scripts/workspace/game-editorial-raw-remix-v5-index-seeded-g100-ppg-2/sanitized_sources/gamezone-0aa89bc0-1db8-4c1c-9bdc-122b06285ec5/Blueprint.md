# Blueprint

## High-level code structure
- Single-file HTML game with embedded CSS and JavaScript.
- Tailwind CDN is used for layout utility classes, while most visual identity comes from custom CSS variables and handcrafted styles.
- The DOM contains:
  - a full-screen canvas for gameplay rendering
  - a HUD for score display
  - a start screen and game-over screen
  - hidden media elements for image/audio swapping and editor integration
  - GIF overlays for collection and failure feedback
- The JavaScript is organized informally into:
  - configuration bootstrap (`initConfig`, `updateGameConfig`)
  - audio management (`AudioManager`)
  - lifecycle/init (`DOMContentLoaded`, `resize`, `startGame`, `gameOver`)
  - input handling (`handleInput`)
  - main loop (`loop`, `update`, `draw`)
  - helper systems (`checkCollision`, `createParticles`, `showGifBurst`)

## Game loop / state model
- Core state is held in globals:
  - booleans: `isPlaying`, `isGameOver`
  - scalar progression: `score`, `gameSpeedMultiplier`, `frames`
  - entity collections: `obstacles`, `collectibles`, `particles`, `clouds`
  - player physics object: position, size, vertical velocity, grounded state, rotation
- The render/update cycle runs through `requestAnimationFrame(loop)`.
- `loop()` computes `dt`, calls `update(dt)`, then `draw()`.
- `update(dt)` only advances gameplay while `isPlaying` is true.
- The state flow is:
  1. Idle attract/start screen visible
  2. `startGame()` resets everything and begins active play
  3. Endless survival/collection run continues until obstacle collision
  4. `gameOver()` freezes play, stops BGM, shows result screen
  5. Restart returns to a fresh run

## Player goals
- Survive as long as possible in an endless side-scrolling run.
- Collect as many floating snacks/bones as possible to increase score.
- Avoid ground obstacles/crates/hydrant-like hazards that instantly end the run.
- Manage jump timing because the player has a single leap action and can only jump while grounded.

## Interaction pattern
- One-button / one-tap control scheme.
- Inputs:
  - pointer/tap anywhere in the game area
  - spacebar on keyboard
- Interaction rule:
  - if the run is active and the dog is grounded, a tap triggers a jump
  - buttons for start and restart are separate UI interactions
- This creates a simple rhythm of:
  - watch scrolling hazards and pickup arcs
  - tap once to hop
  - land, recover, and prepare the next leap

## Core systems
### 1. Runner movement and physics
- The world scrolls left while the player remains near the left side of the screen.
- Gravity and jump force come from a config block.
- The player only moves vertically; forward movement is simulated by world scrolling.

### 2. Spawn system
- Spawns occur on a frame cadence scaled by `gameSpeedMultiplier`.
- Each spawn event creates either:
  - an obstacle on the ground
  - or a collectible at a variable airborne height
- This makes the run feel like a mix of dodge timing and reward chasing.

### 3. Collision system
- Axis-aligned collision with slightly shrunken hitboxes for forgiveness.
- Obstacle collision triggers instant game over.
- Collectible collision increments score, removes the item, emits particles, and increases speed slightly.

### 4. Difficulty ramp
- `gameSpeedMultiplier` starts at 1 and increases by `0.01` per collectible.
- Faster speed increases pressure over time and effectively raises spawn throughput.
- Progression is score-driven rather than level-based.

### 5. Juice / feedback
- Score pulse animation on collection
- Particle bursts for jump/collect moments
- GIF overlays for collection streak feeling and fail reaction
- Canvas shake on game over
- BGM plus separate jump/land/collect/fail/UI sounds

### 6. Presentation layer
- Canvas draws a stylized skyline, sun glow, clouds, road, grass, player, obstacles, collectibles, and particles.
- The menus use arcade-glass UI styling with bold display fonts and emoji iconography.
- Visual theming suggests a cheerful urban rooftop sprint rather than realism.

## Inferred genre / gameplay shape
- Primary shape: endless runner
- Secondary shape: lane-less one-button action platformer
- It plays like a lightweight arcade survival runner where collectible chasing also drives difficulty.
- The closest mental model is a casual “tap to jump over hazards and grab pickups” mobile/web runner.

## Gameplay heuristic
- Stay low-risk when hazards cluster; only jump when the landing window is readable.
- Chase collectibles when they align with safe jump arcs, since score gain also increases speed.
- The optimal loop is controlled, single-jump timing rather than aggressive pickup greed.
- Because collision is forgiving but failure is instant, the game rewards reaction timing and rhythm over precision platform routing.
