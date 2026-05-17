# Blueprint

## High-level code structure
The game is implemented as a single self-contained `index.html` document with three main layers:

1. **Presentation layer**
   - Inline CSS defines a neon, futuristic street-racing interface.
   - A full-screen `<canvas>` renders the road, player car, traffic cars, skyline, particles, skid marks, and floating feedback text.
   - DOM overlays provide HUD, touch controls, game-over modal, and garage/shop UI.

2. **Data/config layer**
   - A small embedded JSON config block exposes tunable values such as base speed and traffic density.
   - Persistent progression is stored in `localStorage` under `realRacingData`.
   - Static arrays define:
     - purchasable car roster
     - environment/biome themes
     - saved unlock state and selected car

3. **Gameplay/system layer**
   - JavaScript manages the state machine, physics-lite driving model, enemy traffic spawning, scoring economy, shop flow, audio playback, haptics, and rendering.
   - A `requestAnimationFrame` loop updates simulation and redraws every frame.

## Game loop / state model
The game runs on a continuous animation loop:

- `PLAYING`
  - reads input flags
  - updates acceleration, braking, drifting/handbrake behavior, turbo use, steering, distance, money, biome changes, particles, roadside scenery, and traffic
  - checks collisions and near misses
  - updates HUD
  - renders the current scene

- `CRASHING`
  - triggered immediately on collision
  - plays crash effects, vibration, particles, and camera shake
  - temporarily freezes meaningful progression before transitioning to game over

- `GAMEOVER`
  - converts session earnings into total saved money
  - displays run summary
  - offers replay or garage access

- `SHOP`
  - pauses the run loop’s active gameplay progression
  - displays unlocked/locked cars
  - allows purchasing and equipping faster vehicles
  - returns to the game-over screen rather than directly resuming a live run

The overall structure is an **arcade run → crash/end → reward payout → garage upgrade/equip → new run** cycle.

## Player goals
The player’s immediate goal is to survive as long as possible while driving through traffic at high speed.

Secondary goals:
- travel farther to increase score/value
- perform near misses to gain large bonus cash and refill turbo
- conserve and spend money on faster cars
- improve future runs through vehicle upgrades/unlocks

Longer-term progression goal:
- earn enough total money to buy the full garage lineup, culminating in the fastest high-end cars.

## Interaction pattern
Primary interaction is mobile-first touch control with large on-screen buttons:
- **Left / Right**: steer across lanes
- **Gas**: accelerate
- **Brake**: reduce speed
- **Drift / Handbrake**: sharper turning with speed loss and skid-mark feedback
- **NOS / Turbo**: temporary speed burst that consumes a regenerating boost meter

The same logic is framed as a tactile arcade control scheme rather than a simulation dashboard.

Player input feeds a simplified driving model:
- acceleration and friction determine current speed
- steering is smoothed through lerp
- turbo temporarily raises top speed and acceleration
- handbrake increases turning responsiveness while slowing the vehicle

## Core systems
### 1. Endless traffic-dodging driving
Enemy cars spawn into one of four lanes and move relative to player speed. The player avoids direct collisions while maintaining pace.

### 2. Risk-reward near miss system
When the player grazes another vehicle at sufficient speed without colliding:
- bonus money is awarded
- turbo meter is restored
- audiovisual reward feedback is triggered

This system encourages aggressive weaving rather than safe passive driving.

### 3. Session-to-meta economy
Distance steadily converts into money during a run, and that money is banked on game over. Persistent total funds support garage progression.

### 4. Vehicle progression / garage
Cars differ mostly by `speedMult` and cost. Unlocking better vehicles improves max performance for future attempts.

### 5. Turbo resource management
Turbo starts full, drains during use, and slowly recharges when inactive. Near misses provide additional recharge, tying performance driving to resource recovery.

### 6. Biome rotation / visual progression
The road trip cycles through multiple lighting palettes and skyline moods based on distance, creating perceived progression without discrete levels.

### 7. Audio/haptic feedback
The game combines:
- gameplay BGM
- shop BGM
- near-miss, crash, turbo, purchase, and UI sound effects
- synthetic engine tone
- vibration calls through a bridge API

This reinforces an arcade highway-rush feel.

## Inferred genre / gameplay shape
This is best described as an **arcade endless traffic racer / lane-based survival driving game** with light progression.

Genre shape:
- not a realistic simulator
- not a lap-based circuit racer
- closer to a score-chasing endless runner translated into car form
- built around dodging traffic, chaining near misses, using boost, and unlocking faster vehicles

The strongest mental model is:
**“an endless neon highway dodging game with arcade car handling, near-miss rewards, and garage upgrades.”**

## Gameplay heuristic
A strong player strategy is likely:
1. hold gas to build speed
2. weave through traffic with short steering corrections
3. use drift for sharper emergency repositioning
4. trigger turbo when lanes are open or after gaining recharge from near misses
5. intentionally skim close to cars for bonus cash without colliding
6. spend earnings on faster vehicles to push longer and riskier future runs

This creates a feedback loop where confidence and aggressive driving directly increase both score and progression speed.