# Blueprint

## High-level code structure
This game is implemented as a single self-contained `index.html` file with three major layers:

1. **Presentation layer**
   - HTML defines a full-screen canvas, HUD labels, feedback GIF overlays, and a game-over panel.
   - CSS establishes a sci-fi neon control-room aesthetic with responsive HUD panels, safe-area awareness, and portrait/mobile-first layout choices.

2. **Asset/config layer**
   - Remote audio assets are declared in hidden `<audio>` elements.
   - A JSON-like configuration block defines tunable gameplay parameters:
     - base memorize time
     - time per tile
     - tile movement speed
     - theme color

3. **Gameplay logic layer**
   - Canvas rendering loop
   - Core game state variables
   - `Tile` class for interactive numbered tiles
   - `Particle` class for small celebratory visual effects
   - Audio loading / playback helpers
   - State transitions and level generation
   - Pointer-based input handling

The game is structurally simple and highly centralized: almost all behavior is orchestrated by global state plus a continuous animation loop.

## Game loop / state model
The state machine is explicit:

- `LOADING`
- `MEMORIZE`
- `INPUT`
- `CHECK`
- `GAMEOVER`

### Main loop behavior
A `requestAnimationFrame` loop:
- computes delta time
- updates countdowns during memorize phase
- updates tile interpolation and particle effects
- redraws the entire scene every frame

### State flow
1. **Game start / level init**
   - Score resets
   - Level starts at 1
   - A sequence of unique numbers is generated
   - Tiles appear in ordered top slots

2. **MEMORIZE**
   - Player studies the ordered sequence for a limited time
   - A timer bar shrinks across the top
   - After the timer expires, the state advances automatically

3. **INPUT**
   - Tiles are shuffled into a bottom “pool”
   - Empty ghost slots remain at the top
   - Player taps tiles to rebuild the original order

4. **CHECK**
   - Once all slots are filled, the game verifies the player’s sequence
   - Success advances to the next level and awards score
   - Failure triggers a fail response, then game over

5. **GAMEOVER**
   - Overlay panel appears
   - Final score is shown
   - Restart returns to a fresh run

## Player goals
The player’s immediate goal is to:
- memorize the displayed number sequence before it disappears into a shuffled pool
- reconstruct that sequence in the original order by tapping tiles into the empty slots

The larger goal is to:
- survive as many waves as possible
- increase score by clearing rounds
- handle gradually longer sequences as level count rises

## Interaction pattern
The interaction model is direct and touch-friendly:

- **Tap a tile in the pool** to place it into the next open top slot
- **Tap a tile already placed in a slot** to remove it and return it to the pool
- When all slots are filled, validation triggers automatically

There is no dragging; the game simulates ordering through discrete taps.

## Core systems
### 1. Sequence generation
- Each level generates a sequence of unique digits chosen from 1–9
- Sequence length scales with level
- Difficulty tops out at 6 tiles

### 2. Memory challenge timing
- Memorization window is based on:
  - fixed base time
  - extra time per tile
- This creates a readable but tightening cognitive challenge

### 3. Tile placement system
- Tiles transition between:
  - `SLOT`
  - `POOL`
  - `MOVING`
- Slot occupancy is tracked independently from tile rendering positions
- Placement order matters because the first empty slot is always used

### 4. Verification system
- Player-entered tile order is compared against the original generated sequence
- Full completion triggers a short verification pause before success/failure feedback

### 5. Difficulty / progression system
- Score reward increases with level
- Sequence length increases every few levels
- The main progression is endurance-based wave advancement rather than story or content unlocks

### 6. Juice / feedback system
- Success and fail sounds
- Haptic feedback
- Animated GIF overlays
- Particle burst on success
- Screen shake behavior on failure
- Continuous sci-fi background music while active

## Inferred genre / gameplay shape
This is primarily a **memory puzzle game** with a **sequence reconstruction** mechanic and a light **arcade survival / wave progression** wrapper.

The overall gameplay shape is:
- short cognitive challenge
- rapid retry loop
- escalating rounds
- score chase
- one mistake ends the run

It resembles a minimalist mobile arcade memory title: part Simon-style recall, part order-restoration puzzle, framed as a futuristic “signal decoding” challenge.

## Gameplay heuristic
A player succeeds by:
- chunking the numbers into a memorable pattern
- quickly locating the needed digits in the shuffled pool
- correcting mistakes before all slots are committed
- treating each level as a faster mental scan-and-rebuild loop

The strongest learned skill is not dexterity but short-term recall under light time pressure and visual scrambling.

## Presentation and thematic read
The game presents itself as a:
- sci-fi signal decoder
- holographic terminal puzzle
- cyber-memory challenge

Theme cues include:
- “Mind Stone Sequence” title
- “SCAN THE CODE” and “REBUILD THE ORDER” messaging
- “SIGNAL LOST” failure framing
- neon blues, violets, and golds
- clean futuristic typography
- HUD labels like `DATA` and `WAVE`

## Confidence notes
Confidence is high on the main gameplay loop because the full game logic is visible in source.
Confidence is moderate on intended narrative flavor because the thematic framing is lightweight and mostly cosmetic.