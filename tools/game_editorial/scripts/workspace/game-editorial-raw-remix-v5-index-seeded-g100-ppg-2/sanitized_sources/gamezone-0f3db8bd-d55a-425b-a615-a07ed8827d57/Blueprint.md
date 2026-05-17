# Blueprint Ballistics

## High-level code structure
The game is implemented as a single self-contained `index.html` file with three major layers:

1. **Presentation layer**
   - Full-screen canvas for gameplay rendering.
   - HTML overlay panels for the start screen, HUD, tutorial hint, animated feedback strip, and game-over screen.
   - CSS-driven sci-fi neon styling with responsive/mobile-safe layout rules.

2. **Runtime systems**
   - `AudioController` manages background music, one-shot sound effects, basic cooldowns, and browser audio unlocking.
   - Canvas rendering functions draw the background grid, drifting parallax symbols, the player orb, the beacon goal, rails, and particles.
   - Physics/update logic handles gravity, wall bounces, rail collisions, scoring, and fail-state detection.

3. **Input/game flow**
   - Mouse and touch events let the player drag to define line segments ("rails").
   - Start/restart buttons transition between menu states and begin the active loop.
   - A `requestAnimationFrame` loop advances the game only while `gameActive` is true.

## Game loop / state model
The runtime follows a lightweight arcade state model:

- **Pre-game / title**
  - Start panel visible.
  - Canvas is present but gameplay is inactive.
- **Active run**
  - `gameActive = true`
  - Per frame:
    1. Clear canvas
    2. Draw animated grid and parallax background
    3. Update ball physics
    4. Update particles
    5. Draw ball, goal, rails, and effects
  - Player can add permanent rails at any time by dragging.
- **Game over**
  - Triggered when the orb falls below the playfield.
  - BGM stops, fail sound/feedback play, HUD hides, final score is shown.
- **Restart**
  - Resets score, rails, particles, ball, goal, and loop state.

The model is score-attack and endless until failure rather than level-based.

## Player goals
The player is trying to:
- guide a falling/ricocheting energy orb,
- draw rails that redirect it,
- hit glowing beacon targets,
- score as many beacon captures as possible before the orb drops out of bounds.

The short-term goal is route correction. The long-term goal is score maximization and survival.

## Interaction pattern
Core interaction is extremely direct:
- press/tap **Begin Test**,
- watch the orb fall under gravity,
- drag with mouse or touch to sketch a line segment,
- use the created segment like a bumper/ramp to deflect the orb,
- continue placing rails to chain successful redirects toward newly spawned beacons.

Important inferred interaction behavior:
- rails are created from drag start to drag end as straight segments,
- rails remain in the arena after being placed,
- there is no actual ink depletion despite the HUD showing "Rail Ink ∞",
- the player does not directly move the orb; they influence motion indirectly through geometry placement.

## Core systems
### 1. Ballistic physics system
- Constant downward acceleration simulates gravity.
- Velocity damping softens motion slightly over time.
- Side-wall rebounds reflect horizontal momentum.
- Rail collision reflects the orb across a segment normal and reduces speed, creating a controlled ricochet feel.

### 2. Player-authored rail system
- Each drag gesture creates one straight line segment if long enough.
- Segments persist and collectively form a player-built navigation layout.
- Current in-progress line is previewed with a dashed stroke.

### 3. Goal / scoring system
- A rotating beacon goal spawns in the lower half of the screen.
- Touching it increases score by 1.
- On score, the beacon relocates and celebratory effects/audio play.

### 4. Failure system
- The run ends if the orb falls below the visible area.
- This creates constant tension between improvisation and cleanup of a bad trajectory.

### 5. Juice / feedback system
- Audio: start, draw, bounce, score, fail, plus looping music.
- Visual effects: particles on impacts and scores, glowing rails, animated beacon, celebratory/failure GIFs, floating tutorial, neon HUD.
- These systems make a simple ruleset feel energetic and polished.

### 6. Responsive/mobile support
- Touch events mirror mouse input.
- UI scales down for smaller viewports.
- The game appears designed to function on phones/tablets as well as desktop.

## Inferred genre / gameplay shape
Best abstract genre reading:

- **Primary shape:** physics-guided drawing arcade game
- **Secondary shape:** survival score attack
- **Tertiary shape:** minimalist sandbox routing toy

It feels like a hybrid of:
- a **drawing puzzle game** because the player solves trajectory problems by drawing lines,
- a **physics puzzle** because gravity, reflection, and angle control matter,
- a **survival/endless arcade** game because the session continues until the orb escapes.

## Gameplay heuristic
A player succeeds by learning a few consistent heuristics:

- draw rails **ahead of the orb**, not directly on top of it;
- use shallow angles to preserve horizontal travel and avoid sending the orb straight downward;
- build a loose funnel or recovery lane in the lower half of the arena;
- exploit persistent rails to create repeatable scoring loops;
- avoid overcommitting clutter near the center if it produces chaotic rebounds.

The game likely becomes more skillful through self-imposed mastery rather than explicit content progression.

## Inferred strengths of the design
- Immediately readable one-input concept.
- Strong "one more try" score-chasing loop.
- Works well on both mouse and touch.
- Distinct visual identity despite simple mechanics.
- Emergent play from persistent line placement.

## Confidence notes
High confidence:
- single-screen arcade structure,
- drag-to-draw redirect mechanic,
- score-until-fall fail loop,
- physics-driven ricochet gameplay.

Moderate confidence:
- intended genre labels across the provided category universe, since the game mixes puzzle and arcade survival elements.

Lower confidence:
- whether "Rail Ink ∞" hints at a removed resource system or merely flavor text, because no ink limit is implemented in code.