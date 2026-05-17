# Blueprint

## High-level code structure
The game is a single-file browser game implemented entirely in `index.html` with three major layers:

1. **Presentation layer**
   - Inline CSS defines a neon arcade visual theme with pixel-panel UI, mobile-safe layout rules, scanlines, HUD cards, and modal overlays.
   - The DOM contains a full-screen `<canvas>` for gameplay plus HTML overlays for the start screen, quiz modal, game-over screen, HUD, and GIF feedback.

2. **Media / feedback layer**
   - `AudioController` manages one looping background track plus one-shot effects for jump, quiz open, success, failure, hit, and game start.
   - `GifController` briefly shows approved remote reaction images for success/failure states.

3. **Gameplay layer**
   - A DOMContentLoaded script defines assets, game state, player state, obstacle arrays, cloud/background entities, quiz generation logic, update/draw functions, input handlers, and the main animation loop.

The project is intentionally lightweight and self-contained: no external gameplay framework, no module system, and no persistence layer.

## Game loop / state model
The runtime follows a straightforward arcade state model:

- **Start state**
  - Player chooses between two runner avatars.
  - Start button unlocks audio, begins music, initializes state, hides menus, and starts the loop.

- **Active run state**
  - `requestAnimationFrame(loop)` repeatedly calls:
    - `update()` for physics, score growth, obstacle spawning/movement, collision checks, and quiz triggers
    - `draw()` for sky, skyline, track, player sprite, spikes, and HUD refresh

- **Paused quiz gate state**
  - Every time score reaches a 1000-point boundary, gameplay pauses.
  - A two-choice arithmetic quiz modal appears.
  - Correct answer resumes the run and grants rewards.
  - Wrong answer ends the run immediately.

- **Game over state**
  - Triggered by hitting a spike or failing a quiz.
  - Music stops, failure SFX plays, HUD hides, final distance is shown, and restart becomes available.

Key mutable state variables:
- `gameActive`
- `isPaused`
- `frame`
- `score`
- `rings`
- `speed`
- `mathCounter`
- `player`
- `obstacles`
- `clouds`

## Player goals
The player's immediate and longer-term goals appear to be:

- survive by jumping over spikes
- maintain momentum through an endless auto-run
- answer quiz gates correctly to keep the run alive
- accumulate distance score
- collect “tokens”/“rings” awarded through quiz success
- push speed higher as a reward for correct answers

This creates a hybrid goal structure: reflex survival plus quick knowledge validation.

## Interaction pattern
Core interaction is intentionally simple and accessible:

- **Character selection on start screen**
  - Choose one of two cosmetic runner archetypes.

- **Primary in-run input**
  - Tap/click on the canvas, press Space, or press Arrow Up to jump.

- **Quiz interaction**
  - Tap/click one of two answer buttons when the run pauses.

This means the overall interaction loop is:
1. start run
2. auto-sprint forward
3. time jumps over hazards
4. stop at quiz gate
5. choose answer
6. resume faster if correct, or lose if wrong
7. repeat until failure

## Core systems
### 1. Endless runner locomotion
The character is fixed near the left side while the world scrolls toward them. Obstacles spawn at the right edge and move left based on current speed.

### 2. Jump physics
A simple gravity/jump model drives the player:
- `jumpForce` launches upward
- `GRAVITY` pulls back down
- grounded check prevents midair spam

### 3. Obstacle hazard system
Spike obstacles spawn on an interval that tightens as speed increases. Collision with any spike causes instant defeat.

### 4. Score and pacing system
- Score rises continuously during active play.
- Distance display is derived from score (`score / 10`).
- Correct quiz answers add a bonus chunk of score and raise movement speed.

### 5. Quiz gate system
This is the defining mechanic:
- triggered every 1000 score units
- pauses the action
- presents one arithmetic problem and two answer buttons
- correct answer grants progression reward
- incorrect answer ends the run

Difficulty is light at first and becomes somewhat broader later, but the game remains casual rather than educationally rigorous.

### 6. Character skin variation
Two selectable runners alter silhouette, dimensions, and palette:
- a short blue speedster style runner
- a tall green “tower mind” runner

This appears mostly cosmetic, though the changed hitbox dimensions may subtly affect feel.

### 7. Audio-visual reinforcement
The game uses:
- looping action music
- jump, hit, start, success/fail, and menu-style SFX
- celebratory or failure GIF stingers
- glowing HUD and modal panels

These systems strongly reinforce an arcade-reaction tone.

## Inferred genre / gameplay shape
The game is best understood as a:

**casual endless runner fused with a quiz gate / arithmetic challenge layer**

Its gameplay shape is:
- short-session
- fail-fast
- score-chasing
- one-button action during live play
- modal decision test at regular intervals
- arcade presentation with lightweight edutainment flavor

It is not a pure quiz title and not a pure runner. The runner framework carries the session, while quizzes act as mandatory checkpoints and progression gates.

## Heuristic summary
From the code, the intended fantasy is:
- a neon retro sprint through a futuristic lane
- dodging spike traps at increasing speed
- periodically proving focus with quick math answers
- earning a feeling of “momentum maintained” when a gate is cleared

The game likely targets players who want immediate action with a simple mental challenge layered into the run.