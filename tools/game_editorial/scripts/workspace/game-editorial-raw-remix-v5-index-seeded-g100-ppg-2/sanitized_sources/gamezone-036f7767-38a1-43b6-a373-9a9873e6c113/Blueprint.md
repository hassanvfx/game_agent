# Blueprint

## High-level code structure
This game is implemented as a single self-contained `index.html` file with three major layers:

1. **Presentation layer**
   - Inline CSS defines a neon-horror interface with glass panels, scanlines, grain, vignette effects, HUD pills, and responsive mobile-safe sizing.
   - The DOM includes menu, game-over, and victory overlays; a HUD; a feedback GIF overlay; hidden audio elements; and a full-screen `<canvas>` used for active play rendering.

2. **Configuration layer**
   - A small editable JSON config block exposes:
     - `difficulty` for watcher aggression
     - `playerSpeed` for forward speed
     - `gameTitle` for UI/title text
   - Matching runtime config objects are attached to `window`, including an `updateGameConfig` helper.

3. **Runtime/game layer**
   - An `AudioManager` handles audio-context unlock, preloading, BGM playback, SFX playback, and oscillator-based fallbacks.
   - A `DOMContentLoaded` bootstrap sets up canvas rendering, UI references, state variables, input handling, button listeners, and the main animation loop.
   - All gameplay, state transitions, AI timing, win/loss checks, and rendering live in one script block.

## Game loop and state model
The game runs on `requestAnimationFrame(loop)` and uses a lightweight finite-state model.

### Top-level game states
- `MENU`
- `PLAYING`
- `GAMEOVER`
- `VICTORY`

### Entity / threat states
- `IDLE`
- `WARNING`
- `ATTACK`

### Core loop behavior
Each frame:
1. Compute `dt` from the current animation timestamp.
2. Clear and redraw the full canvas scene.
3. If `PLAYING`:
   - Advance the watcher timer.
   - Transition the watcher between `IDLE -> WARNING -> ATTACK -> IDLE`.
   - If the player is moving during `ATTACK`, trigger immediate failure.
   - If the player is moving outside `ATTACK`, advance `progress`.
   - Trigger progress audio pings and update HUD percentage.
   - Trigger victory when `progress >= 1000`.
   - Update vignette, flicker, and status text based on watcher state.
4. Update transient feedback systems:
   - particles
   - floating text
   - feedback GIF timer
   - screen shake/flicker
5. Render corridor line, player spark, goal marker, and watcher visuals.

This is essentially a **timing-based hold/release survival sprint** presented as a one-dimensional corridor escape.

## Player goals
The player goal is simple and immediate:

- **Reach the exit by filling the run meter from 0% to 100%.**
- Move only when it is safe.
- Stop instantly when the watcher fully locks on.

The game communicates this explicitly in the start briefing:
- hold to run
- release to freeze
- do not move when the watcher locks on

## Interaction pattern
The interaction model is minimal and readable:

- **Pointer/touch hold on the canvas** to move
- **Release** to stop
- **Spacebar hold/release** as the keyboard equivalent
- **Buttons** to start or restart a run

This produces a highly compressed “red light, green light” loop:
- safe phase: hold to advance
- danger phase: release and wait
- overcommitment during attack: instant loss

## Core systems
### 1. Progression system
- `progress` ranges from `0` to `1000`
- HUD displays it as a percentage (`Math.floor(progress / 10)`)
- Progress grows while the player is actively moving
- Reaching the end triggers `victory()`

### 2. Watcher AI / pressure system
- The watcher cycles through timed phases
- `difficulty` changes attack duration/aggression
- `WARNING` acts as telegraphing
- `ATTACK` is the hard stop state where movement is forbidden

### 3. Input gating system
- The game differentiates between UI button interactions and playfield input
- Pointer suppression is scoped so mobile menu buttons remain usable
- Movement is binary: moving or frozen

### 4. Feedback system
The game strongly emphasizes readable state feedback through:
- HUD text (`STATIC RISING`, `WATCHER LOCKED ON - DO NOT MOVE`)
- vignette color shifts
- red glitch bars and eye graphics
- scanline/grain/CRT flicker
- warning and victory GIF overlays
- progress, warning, win, fail, and BGM audio cues
- particles and floating creepy environmental words

### 5. Audio system
- Ambient loop for tension
- start/restart SFX
- periodic progress pings
- warning sting
- win/fail cues
- synthesis fallback if fetch/decode fails

### 6. Rendering system
The active playfield is not a spatial world to navigate freely. Instead it renders:
- a horizontal corridor/progress line
- a glowing player spark/light
- an exit marker at the far end
- a watcher “eye” and glitch overlays during threat phases

This reinforces that the game is more about **timing and nerve control** than navigation.

## Inferred genre / gameplay shape
Best abstract description:

- **Arcade survival timing game**
- **Reaction game**
- **Lane/line escape runner**
- **Horror-themed stop-and-go challenge**

It resembles a compressed endless/runner-style structure, but it is not about dodging obstacles or lane swapping. The actual dominant mechanic is **advance during safe windows, freeze during danger windows**.

## Gameplay heuristic
A likely optimal strategy inferred from the code:

1. Hold immediately during `IDLE` to build distance.
2. Treat `WARNING` as a pre-alert and prepare to release quickly.
3. Never continue holding once the watcher enters `ATTACK`.
4. Use the HUD/status text and red vignette escalation as the main survival cues.
5. Win by accumulating enough safe movement cycles rather than by mastering complex movement.

## Presentation and tone
The game presents as:
- neon horror
- sci-fi surveillance nightmare
- minimalist corridor panic
- arcade UI with spooky text styling

The visual identity mixes:
- cyan/cold tech glow
- amber progress accents
- red threat overlays
- scanlines, grain, glitch columns, and a looming eye motif

## Confidence notes
Confidence is fairly high because the full gameplay logic is visible in a single file. The only mild ambiguity is genre naming: the game visually resembles a runner, but mechanically it is more specifically a **timing-based freeze-or-move survival game** rather than a traditional obstacle runner.