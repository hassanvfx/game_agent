# Blueprint

## High-level code structure
The game is implemented as a single self-contained HTML document that embeds styling, React UI code, and PixiJS rendering logic.

Primary layers:

1. **Shell / presentation layer**
   - CSS variables and responsive layout create a futuristic neon HUD look.
   - `FullScreen` wraps the game in a branded full-viewport shell.
   - Overlay cards and feedback GIFs provide result-state presentation.

2. **React application layer**
   - `App` renders `KickBallGame` inside `FullScreen`.
   - `I18nProvider` supplies localized strings and a distance formatter.
   - `KickBallGame` owns top-level session state such as current game phase, measured distance, restart key, and viewport size.
   - `KickBallCanvas` bridges React and Pixi by mounting/destroying the Pixi scene.

3. **Pixi scene / gameplay layer**
   - `setupKickBallScene` builds the visual world, loads sprites, creates audio objects, and constructs UI widgets.
   - `createKickBallUi` builds in-canvas prompts, power meter, angle arc, and distance display.
   - `createMilestoneManager` generates checkpoint obstacles/boost pads and handles collision logic.
   - `attachKickBallLogic` contains the main interaction flow and frame-by-frame simulation.

## Game loop / state model
The game uses a simple finite-state interaction loop:

- **idle**
  - Waiting for first tap.
  - Start prompt is visible.
- **power**
  - A power meter oscillates automatically.
  - Player taps to lock launch power.
- **angle**
  - An aiming arc oscillates automatically.
  - Player taps again to lock launch angle.
- **flying**
  - Projectile motion begins.
  - Gravity, ground bounce, friction, milestone collisions, launcher boosts, scrolling camera, and distance accumulation all update each frame.
- **result**
  - Motion has ended after the projectile settles.
  - Final distance and cleared checkpoint count are shown in an overlay.
  - Restart returns the game to `idle`.

The simulation is ticker-driven through Pixi's `app.ticker`, with all active physics happening only in the `flying` state.

## Player goals
The player's goal is to launch the relay object as far as possible across a neon track.

Secondary inferred goals:
- Time the power lock close to the highlighted perfect zone.
- Time the angle lock for a favorable trajectory.
- Reach and pass as many checkpoints as possible.
- Bounce into special launcher checkpoints for additional forward momentum.
- Improve final distance on repeated attempts.

## Interaction pattern
The input model is intentionally minimal and mobile-friendly:

- **Tap/click 1:** start the run and begin power calibration.
- **Tap/click 2:** lock current power and begin angle calibration.
- **Tap/click 3:** lock current angle and launch.

There is no free movement after launch. The core skill comes from timing taps against oscillating meters/angles. Restart happens through a single button on the result overlay.

## Core systems
### 1. Launch calibration system
Power and angle both sweep automatically between bounds. This creates a timing challenge instead of free aiming.

### 2. Projectile physics system
The launched object uses:
- horizontal and vertical velocity
- gravity
- ground bounce elasticity
- rolling friction
- minimum bounce threshold to transition into a stop

### 3. Distance/progression system
Distance is measured from the launch point and displayed in meters. Checkpoints are generated every 100 meters, extending dynamically as the object travels farther.

### 4. Checkpoint collision system
The track contains two milestone types:
- **normal checkpoints** that act as physical blockers/bumpers
- **launcher checkpoints** at every 200 meters that redirect and boost the projectile

This turns the run into a hybrid of launch game and obstacle ricochet game.

### 5. Camera follow system
The world scrolls by shifting the game container so the launched object stays near center screen during travel.

### 6. Feedback/audio juice system
The game includes:
- start/calibration/launch/result sounds
- bounce, bonus, and power-up sounds
- vibration cues on supported devices
- impact and celebration GIF overlays
- branded neon UI overlays and stat readouts

## Inferred genre / gameplay shape
Strongest inferred shape:
- **one-button / few-tap timing launch game**
- **distance-chasing arcade game**
- **projectile physics score attack**

It presents like a futuristic sports-launch mini-game: a runner/avatar sends a relay signal/object down a neon lane, and the player optimizes timing to maximize travel distance.

## Heuristic summary
This game is best understood as a compact arcade distance launcher with a three-tap flow:
1. begin the relay,
2. stop the power meter,
3. stop the angle meter,
then watch a physics-driven run unfold across boost-enabled checkpoints.

The pleasure loop is fast restart, readable performance feedback, and repeated attempts to beat a longer distance through better timing and favorable rebounds.