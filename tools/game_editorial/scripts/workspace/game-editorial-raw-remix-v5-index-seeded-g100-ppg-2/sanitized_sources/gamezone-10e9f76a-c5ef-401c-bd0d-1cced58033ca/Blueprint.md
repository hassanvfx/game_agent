# Blueprint

## High-level code structure
This game is implemented as a single self-contained HTML document with three main layers:

1. **Presentation layer**
   - Inline CSS defines the entire visual identity: neon sci-fi gradients, glassmorphism UI cards, HUD pills, animated hints, and responsive/mobile-safe layout.
   - HTML contains a full-screen canvas, overlay feedback GIF containers, a start screen, a game-over screen, the HUD, and a short tutorial prompt.

2. **Runtime/game systems**
   - A small `AudioController` manages background music plus UI, pickup, streak, and fail sound effects.
   - A `FeedbackController` shows temporary pickup/failure animated overlays.
   - Global game state stores canvas sizing, score, frame count, player position, enemies, vents, stars, and pointer/touch input.

3. **Gameplay/render loop**
   - A continuous `requestAnimationFrame` loop updates movement, spawns/collects objectives, checks collisions, and renders the background plus all entities each frame.

## Game loop / state model
The state model is lightweight and arcade-oriented.

### Main states
- **Start screen / idle**
  - Title card and CTA button are visible.
  - Background is already drawn, but the run is inactive.
- **Active run**
  - HUD is shown.
  - Player continuously drifts toward the current pointer/touch position.
  - One collectible vent is active at a time.
  - Enemies move around the arena and bounce off screen bounds.
  - Score increases when a vent is touched.
- **Game over**
  - Triggered on collision with an enemy.
  - Music stops, fail feedback appears, final score is displayed, and restart becomes available.

### Frame-by-frame loop
Each active frame:
1. Increment frame counter.
2. Clear and redraw the animated sci-fi background/grid/stars.
3. Move the player toward the latest input position using smooth easing.
4. Clamp player inside the screen bounds.
5. Render vents and resolve vent pickup.
6. Update/render enemies and resolve collision loss.
7. Render the player avatar.
8. Request the next animation frame.

## Player goals
The immediate goal is to survive while collecting as many vents as possible.

The player is effectively trying to:
- sweep vents one by one,
- avoid colliding with roaming patrol characters,
- keep the run going long enough to build a high score,
- survive rising pressure as more enemies are added over time.

## Interaction pattern
The interaction model is direct and minimal:
- **Mouse move** on desktop steers the character.
- **Touch drag / touch placement** on mobile steers the character.
- The avatar does not jump, attack, or stop on command; it glides toward the current input target.
- Start/restart are button-based UI interactions.

This creates a “kite the hazards while pathing to pickups” style of play rather than lane-based or platform-based movement.

## Core systems
### 1. Player follow movement
The player does not snap to the cursor. Instead, position lerps toward the input point using a low speed factor, creating slippery, evasive motion.

### 2. Objective spawning
A single vent pickup exists at a time. Collecting it:
- removes the current vent,
- increments score,
- spawns a new vent at a random location.

### 3. Escalation / difficulty ramp
Each collected vent increases tension by spawning at least one new enemy, with a chance for an extra one.
Enemy speed also scales upward using current score.

### 4. Enemy hazard system
Enemies:
- spawn from screen edges,
- move on fixed velocity vectors,
- bounce off arena boundaries,
- kill the run on contact with the player.

### 5. Feedback systems
- Score HUD updates in real time.
- Pickup and fail GIF overlays reinforce success/failure moments.
- Audio layers add start, pickup, streak, failure, and looping action music.
- A short “Drag to Drift” tutorial helps first-time onboarding.

### 6. Responsive full-screen canvas playfield
The game is designed as a full-screen arena and includes mobile-safe viewport handling, touch suppression on the game surface, and safe-area-aware HUD placement.

## Inferred genre / gameplay shape
Strongest inferred shape:
- **Arcade survival dodger / collect-and-avoid game**

Secondary genre signals:
- top-down arena survival
- score-attack action game
- evasive movement challenge
- casual one-button/one-input mobile arcade game

The “impostor/vent” theme is cosmetic and presentation-driven, while the actual mechanic loop is a survival collection game: move through an open arena, pick up objectives, and avoid growing enemy density until inevitable failure.