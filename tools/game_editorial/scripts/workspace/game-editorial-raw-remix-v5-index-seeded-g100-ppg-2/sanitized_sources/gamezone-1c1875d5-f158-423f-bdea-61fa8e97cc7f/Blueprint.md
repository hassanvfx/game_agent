# Blueprint

## High-level code structure
The game is implemented as a single self-contained `index.html` document with three main layers:

1. **Presentation layer**
   - Inline CSS defines a sci-fi neon visual language, responsive layout rules, menu cards, HUD pills, and animated feedback overlays.
   - The DOM contains:
     - a full-screen `<canvas>` for gameplay rendering,
     - a start screen,
     - a game-over / upgrade shop screen,
     - a score HUD,
     - two reaction overlays for collection and failure feedback.

2. **Systems layer**
   - A lightweight `AudioController` class manages background music, sound effects, pooling, cooldowns, and browser audio unlock behavior.
   - Core game state is stored in top-level variables for score, persistent currency, player stats, and active entities.

3. **Gameplay layer**
   - Input handlers update the player target position from mouse/touch input.
   - Spawner, draw, and update functions manage dust pickups, sludge hazards, floating particles, player rendering, shop UI, and run transitions.
   - The game loop is driven by `requestAnimationFrame`.

## Game loop / state model
The game uses a simple arcade run structure with persistent upgrades between runs.

### Primary states
- **Start screen**
  - Shows the title, premise, and start button.
- **Active run**
  - Canvas renders the arena.
  - The player-controlled cleaning bot follows cursor/touch position with easing.
  - Dust credits spawn and can be vacuumed for money.
  - Mud/sludge spills act as instant-fail hazards.
- **Game over / shop**
  - The run ends on contact with a sludge spill.
  - Total earned currency persists.
  - The player can spend currency on permanent upgrades.
  - Restart begins a new run with upgraded stats.

### Frame loop behavior
On each animation frame during an active run:
1. Clear and redraw the floor/background.
2. Update and draw ambience particles.
3. Move the bot toward the current input target using speed-based interpolation.
4. Animate and draw sludge hazards; check collision with the bot.
5. Randomly spawn new dust and occasional new hazards.
6. Update dust drift, apply suction attraction within vacuum radius, award currency on collection.
7. Draw the player bot and request the next animation frame.

## Player goals
The player's immediate goal is to survive while collecting as many floating dust credits as possible.

The medium-term goal is to accumulate currency across repeated runs.

The long-term goal is to improve the cleaning bot through permanent upgrades:
- **Suction Range** increases pickup radius.
- **Motor Speed** increases how quickly the bot follows input.

This creates a risk-reward loop where the player tries to harvest more pickups before eventually colliding with a hazard.

## Interaction pattern
- **Mouse / touch drag / hover guidance:** the bot does not move with direct velocity controls; instead it homes toward the latest cursor/finger position.
- **Arcade avoidance:** the player steers around expanding/pulsing sludge hazards.
- **Area collection:** pickups are pulled inward once they enter the suction radius, then convert into currency when fully collected.
- **Menu/shop tapping:** after failure, the player buys upgrades and launches another run.

This is a very pick-up-and-play, single-screen survival-collection interaction model.

## Core systems
### 1. Player movement system
- Player position eases toward `targetX` / `targetY`.
- Upgradeable speed modifies the responsiveness of movement.
- The player is visually represented as a rotating robot vacuum core with a visible suction radius circle.

### 2. Pickup / vacuum system
- Dust nodes spawn across the arena and drift slowly.
- When dust enters the suction radius, it is pulled toward the player.
- When dust gets close enough, it is removed and awards cash.
- Collection triggers sound and a positive visual reaction overlay.

### 3. Hazard system
- Sludge spills spawn at intervals and pulse visually.
- They are placed away from the player when spawned initially.
- Collision with a spill immediately ends the run.
- Failure triggers a sound and failure reaction overlay.

### 4. Upgrade economy
- Currency is persistent across runs via `totalCash`.
- Two upgrade tracks raise collection efficiency and mobility.
- Upgrade prices scale upward by a 1.5x multiplier.
- Buttons disable when the player lacks funds.

### 5. UI / feedback system
- Start and game-over states are DOM-driven overlays.
- The HUD shows persistent currency during play.
- Reaction cards reinforce success and failure events.
- Audio provides start, pickup, buy, blocked, and fail feedback.

### 6. Audio system
- Background loop during runs.
- Pooled SFX playback to avoid overlap issues.
- Cooldown on repeated collection sounds to reduce spam.

## Inferred genre / gameplay shape
The game most strongly resembles a:
- **casual survival-collection arcade game**
- with **mouse/touch guided movement**
- plus **light meta progression through permanent upgrades**

It sits between:
- an **avoidance survival game**,
- a **pickup collector / score attack game**,
- and a **very light arcade upgrade loop**.

It is not level-based and not narrative-driven. The design is endless until failure, with progression expressed through higher earnings and post-run stat growth.

## Gameplay heuristic summary
A typical session likely feels like this:
1. Start a run in a single-screen neon room.
2. Sweep around the field collecting glowing dust credits.
3. Avoid sludge patches that instantly end the run.
4. Use earned credits to improve suction radius and movement speed.
5. Restart and last longer while collecting more efficiently.

The core fantasy is being a futuristic cleaning bot optimizing messy-room sweeps under arcade pressure.