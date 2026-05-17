# Blueprint

## High-level code structure
This game is a single-file browser game implemented entirely in `index.html` with three layers combined in one document:

1. **HTML UI structure**
   - A full-screen canvas for gameplay rendering.
   - Overlay UI panels for the start screen, HUD, and game-over screen.
   - Two reaction GIF elements for score/fail feedback.

2. **CSS presentation layer**
   - Neon-lit streetball visual theme with glassmorphism UI panels.
   - Responsive HUD and mobile-safe button sizing.
   - Stylized start and end overlays, plus animated feedback treatment.

3. **JavaScript game logic**
   - Audio controller for background music and sound effects.
   - Global game state for score, frame count, shot lifecycle, and activity flags.
   - Physics-driven basketball shot simulation.
   - Canvas rendering for skyline, court, hoop, ball, aiming guide, and particles.
   - Mouse and touch input handlers for drag-to-shoot play.

## Game loop / state model
The game uses a straightforward animation loop with `requestAnimationFrame`.

### Core runtime flow
- `DOMContentLoaded` initializes systems and event listeners.
- `resize()` sizes the canvas and prepares ball/hoop positions.
- Pressing **Play Ball**:
  - unlocks audio,
  - starts BGM,
  - hides the start screen,
  - shows the HUD,
  - resets score and entities,
  - starts `gameLoop()`.

### Per-frame loop
Each active frame:
1. clears the canvas,
2. draws the moving background skyline,
3. updates physics if the ball is flying,
4. updates particles,
5. draws court, hoop, ball, aura, and aiming/trajectory overlays,
6. increments frame counter,
7. schedules the next frame.

### State model
The game is effectively driven by:
- **global run state**
  - `gameActive`: whether the loop should continue
  - `score`: successful baskets
  - `frameCount`: background and pulse timing
- **ball state**
  - `idle`: waiting for input
  - `flying`: in motion after release
  - `aiming` is mentioned in comments/state conceptually, but active logic mainly uses `idle` and `flying`
- **shot state flags**
  - `hasScoredThisShot`
  - `landedThisShot`
- **input state**
  - whether pointer drag is active and the current drag coordinates

### Fail and reset conditions
- A score is detected when the falling ball crosses the rim line between left and right rim bounds.
- After a made basket, the game briefly celebrates, then resets the ball and randomizes the hoop for the next shot.
- A miss becomes terminal when the ball hits the ground, bounces, slows down, and comes to rest.
- Once the ball stops, the run ends and the game-over overlay appears with final basket count.

## Player goals
The player is trying to:
- launch the basketball into the hoop,
- chain together as many made baskets as possible,
- adapt to a newly randomized hoop position after every successful shot,
- avoid ending the run with a missed attempt that settles on the ground.

This makes the main goal a **high-score survival streak** based on repeated accurate shots.

## Interaction pattern
The interaction model is very simple and tactile:

- The ball begins in a ready position near the lower-left side of the screen.
- The player presses/touches near the ball area and **drags backward/downward or backward/upward** to set launch direction and power.
- Releasing the pointer fires the shot.
- An aiming line and predicted trajectory dots appear while dragging.
- The player then watches the shot resolve through physics.
- If they score, the next shot begins from a reset position.
- If they miss badly enough to end the shot, the run ends and they can restart.

This is essentially a **drag-and-release flick mechanic** built around one-shot physics attempts.

## Core systems
### 1. Audio system
- Background music loop for the active run.
- SFX for:
  - launch,
  - rim/backboard contact,
  - scoring,
  - landing,
  - game over,
  - UI clicks.
- Audio is user-gesture unlocked to satisfy browser autoplay rules.

### 2. Physics and shot simulation
- Gravity pulls the ball downward each frame.
- Launch velocity is derived from drag distance and direction.
- Launch force is capped by `MAX_POWER`.
- Wall bounces and floor bounce/friction create some forgiving but arcade-like physics.
- Backboard collision is approximated with a simple vertical hit zone.

### 3. Scoring system
- Score increments only when the ball crosses the rim while descending.
- HUD updates immediately.
- Score feedback includes particles, SFX, and a celebratory GIF.
- Successful shots automatically transition to a new attempt.

### 4. Failure/game-over system
- Missing does not instantly fail; the ball can bounce and settle.
- The run ends only after the missed shot has fully resolved and stopped moving.
- A fail GIF and fail sound emphasize the lost run.

### 5. Presentation and atmosphere
- Neon night-city skyline with parallax motion.
- Glowing court and hoop visuals.
- Stylized basketball, aura ring when idle, and futuristic HUD typography.
- Overall presentation suggests an arcade street-court fantasy rather than simulation realism.

### 6. Responsive/mobile support
- Full-screen canvas scales with viewport.
- Touch events mirror mouse controls.
- UI is sized for small screens and avoids intrusive layouts.

## Inferred genre / gameplay shape
The best high-level interpretation is:

- **Arcade basketball skill game**
- **Physics-based flick shooter**
- **Score-attack survival loop**

It is not a full sports simulation or team basketball game. Instead, it is a compact, replayable, single-action experience focused on:
- aim,
- arc judgment,
- timing of release,
- adapting to randomized hoop placement,
- chasing a better basket streak each run.

## Gameplay heuristic
A player succeeds by learning a repeatable shot feel:
- pull farther for more power,
- release with enough upward arc to clear the rim,
- compensate for changing hoop height and horizontal placement,
- use the trajectory preview to judge the shot before release.

The design rewards quick experimentation and short repeat sessions. Each score creates a small burst of positive feedback and a fresh setup, while each miss threatens the end of the run, producing light tension and a “one more try” loop.

## Confidence notes
Confidence is high on the core loop and interaction because they are explicit in code:
- drag-release input,
- scoring by rim crossing,
- randomized hoop placement,
- game over on shot failure.

Confidence is moderate on thematic intent beyond the explicit visuals. The game strongly reads as **streetball neon arcade**, but narrative framing is minimal and mostly conveyed through title, palette, skyline, and UI language.