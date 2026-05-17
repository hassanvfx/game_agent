# Blueprint

## High-level code structure
The game is implemented as a single self-contained `index.html` file with four major layers:

1. **Presentation layer**
   - Inline CSS defines the full visual identity: dark sci-fi gradients, glowing HUD cards, feedback strip, animated game-over panel, and mobile-safe layout.
   - The DOM contains a canvas for gameplay plus lightweight HUD and overlay elements for score, story text, feedback messaging, GIF reactions, and restart UI.

2. **Configuration layer**
   - A JSON-like config block inside the HTML exposes tunable parameters such as player speed, obstacle speed, and theme color.
   - `parseConfig()` reads those values into `window.gameConfig`.

3. **Systems layer**
   - **Audio system**: background music, UI/collect/warning/fail SFX, plus Web Audio fallback tones if media playback fails.
   - **Feedback media system**: HUD text changes and temporary GIF overlays for success/failure moments.
   - **Input system**: pointer/touch steering with drag or tap positioning, plus restart click handling.
   - **State system**: `INIT`, `PLAYING`, `GAMEOVER`.
   - **Responsive lifecycle system**: `ResizeObserver`, visibility handling, audio unlock, DPR-aware canvas sizing.

4. **Simulation/render layer**
   - Canvas update/render loop driven by `requestAnimationFrame`.
   - Runtime entities include:
     - player relay/core
     - falling obstacles array
     - particle effects
     - background starfield
     - timed story/status text progression

## Game loop / state model
### State flow
- **INIT**
  - canvas is sized
  - game entities are initialized
  - game immediately transitions into `PLAYING`

- **PLAYING**
  - pointer input updates `player.targetX`
  - game loop updates player smoothing, distance, spawn rate, obstacle movement, collisions, particles, and story text progression
  - score increments when collectible signals are captured
  - collision with hazard ends the run

- **GAMEOVER**
  - HUD fades
  - game-over overlay activates
  - final score is displayed
  - background music pauses
  - restart returns to fresh `PLAYING`

### Frame loop heuristic
Each frame:
1. compute `dt`
2. if playing, run `update(dt)`
3. always run `draw()`
4. request next frame

### Difficulty/progression heuristic
- Obstacles fall faster as `distance` rises
- Spawn chance gradually increases with distance
- Story text updates at milestone distances to imply journey deeper into a debris field
- Run structure is therefore an **increasing-pressure survival dodge-and-collect loop**

## Player goals
Primary player goals appear to be:
- steer the relay/core horizontally
- collect falling **signal shards** for score
- avoid falling **debris**
- survive as long as possible while accumulating recovered signals

Failure condition:
- one impact with an avoid-type obstacle ends the run immediately

Reward structure:
- +10 score per collectible
- visual/audio/vibration feedback on successful collection
- short-term satisfaction from score growth and survival under rising density

## Interaction pattern
- **Input style**: direct pointer/touch control
- **Movement model**: player only moves left/right, following the pointer x-position with smoothing
- **Interaction grammar**:
  - move into glowing diamond-like objects to collect
  - shift away from spiky debris objects
  - react to warning feedback when dangerous objects align with the player lane

This creates a simple one-axis arcade pattern suited for mobile play.

## Core systems
### 1. Player control system
- Player is rendered as a glowing circular sci-fi “relay core”
- Horizontal target-following makes control forgiving rather than twitchy
- Vertical position is fixed near the lower portion of the screen

### 2. Obstacle/content spawning
- Objects spawn above the screen
- Two semantic types:
  - `COLLECT`: beneficial signal shards
  - `AVOID`: harmful debris
- Most spawns are hazards; collectibles are less frequent

### 3. Collision system
- Circular distance-based collision checks
- Collect collision:
  - removes collectible
  - adds score
  - plays collect SFX
  - shows collect GIF
  - spawns particles
- Hazard collision:
  - vibrates
  - plays fail SFX
  - shows fail GIF
  - spawns larger explosion
  - switches to game over

### 4. Feedback/juice system
- HUD messages communicate tutorial and threat states
- Warning SFX triggers when debris approaches dangerously
- Particle bursts reinforce collection/failure
- GIF overlays add exaggerated emotional feedback
- Audio and vibration strengthen the arcade feel

### 5. Ambient progression system
- Story snippets advance by traveled distance
- Starfield drift and lane lines imply forward movement through space despite the player being fixed near the bottom

## Inferred genre / gameplay shape
Strongest inferred shape:
- **Arcade survival dodger with collection**
- Also resembles a **lane runner / endless runner variant** even though movement is smooth rather than lane-locked

The game presents itself as a compact mobile-friendly sci-fi reflex game:
- short runs
- immediate restart loop
- one-touch/one-axis control
- increasing difficulty
- score chasing rather than level completion

## Presentation and thematic heuristic
- Title and text suggest a drifting communications/signal-recovery mission in space
- Visuals imply:
  - dark deep-space field
  - glowing tech relay core
  - signal fragments vs debris
  - minimalist holographic HUD
- Tone is tense but readable rather than chaotic
- Mood mixes:
  - isolation
  - sleek sci-fi calm
  - mounting danger

## Inferred design summary
“Signal Drift” is a minimalist mobile-first sci-fi survival collector where the player drags a glowing relay core left and right near the bottom of the screen to catch signal shards, avoid debris, survive an increasingly dense field, and chase a higher recovered-signal score.