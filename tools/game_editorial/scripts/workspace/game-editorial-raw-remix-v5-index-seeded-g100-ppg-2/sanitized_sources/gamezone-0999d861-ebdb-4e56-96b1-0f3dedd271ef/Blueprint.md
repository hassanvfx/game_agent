# Blueprint

## High-level code structure
- The entire game is implemented in a single `index.html` file.
- Structure is split into three practical layers:
  - **HTML UI layer**: start screen, HUD, controls, game-over screen, reaction GIF overlays, and the canvas container.
  - **CSS presentation layer**: a polished fantasy-neon visual theme using gradients, glassmorphism panels, responsive safe-area spacing, and decorative overlays.
  - **Vanilla JavaScript game layer**: asset/audio setup, central game state, rendering, UI synchronization, input handling, timer management, and the main animation loop.
- There is no module system, framework, or external gameplay engine beyond the browser canvas and DOM APIs.
- Rendering is hybrid:
  - **Canvas** draws the animated background and the witch avatar with its selected outfit parts.
  - **DOM** renders HUD elements, controls, buttons, menus, and animated GIF feedback.

## Game loop / state model
- The game uses a persistent `requestAnimationFrame` loop (`loop`) for visual updates.
- The loop:
  - stores frame timing,
  - updates temporary success/fail feedback timers,
  - redraws the entire scene every frame.
- A separate `setInterval` timer decreases the round timer once per second while the game is active.
- Core state lives in a single `STATE` object:
  - `active`: whether the run is live,
  - `score`: cumulative score,
  - `time`: remaining time,
  - `lastTime`: previous animation timestamp,
  - `current`: currently selected `head`, `body`, and `hand` item indices,
  - `target`: required target `head`, `body`, and `hand` indices,
  - `matchStatus` / `matchTimer`: transient success/fail feedback state.
- State flow:
  1. Start screen shown.
  2. `startGame()` resets the run and generates a target outfit.
  3. Player cycles outfit slots and presses the cast button.
  4. `checkMatch()` evaluates the current loadout.
  5. Success adds score and time, then generates a new target.
  6. Failure removes time and keeps the same target.
  7. When time reaches zero, `gameOver()` stops the run and shows the final score.

## Player goals
- Match the displayed target outfit exactly.
- Do this before the countdown reaches zero.
- Chain successful matches to accumulate score and extend the timer.
- Continue solving as many outfit combinations as possible in a timed survival-style score attack session.

## Interaction pattern
- Primary interaction is direct tap/click input.
- Each of the three equipment categories has left/right arrow buttons:
  - **Head**
  - **Body**
  - **Hand**
- Pressing arrows cycles through 5 options per category with wraparound behavior.
- After setting the outfit, the player presses **“CAST SPELL”** to submit.
- The game does not auto-check matches; submission is explicit.
- Feedback pattern:
  - target icons glow individually when matching,
  - success changes the button label/color, shows celebratory particles/GIF, plays positive audio, and grants score/time,
  - failure changes the button label/color, shakes the canvas, shows a fail GIF, plays failure audio, and removes time.

## Core systems
### 1. Outfit-combination system
- Three independently cycled categories.
- Each category has 5 symbolic variants.
- The actual rendered witch uses index-based visual variants rather than imported sprite sheets.
- The target is represented by emoji icons in the HUD.

### 2. Timed challenge system
- Each run starts with 60 seconds.
- Time decreases by 1 every second.
- Correct answer adds 12 seconds.
- Incorrect answer subtracts 8 seconds.
- This creates a high-pressure but recoverable loop.

### 3. Score system
- Successful matches award `150 + floor(time * 2)`.
- This incentivizes both accuracy and fast solving while the clock is high.
- There is no penalty to score on failure; the penalty is time loss.

### 4. Visual render system
- Canvas background includes gradients, stars, moon-glow, halo effects, and celebratory particles.
- The witch avatar is procedurally drawn using canvas primitives.
- Outfit variations are theme-driven:
  - hats/crowns/hood/horns/tiara,
  - robe/nature/royal/bone/starry body styles,
  - broom/wand/lantern/potion/book hand items.

### 5. Audio feedback system
- Uses a combination of:
  - looping background music through `Audio`,
  - short effects loaded through Web Audio API.
- Sound cues exist for:
  - start,
  - cycling,
  - casting,
  - success,
  - failure.

### 6. UI state/screen system
- Start screen introduces the fantasy dressing challenge.
- HUD shows:
  - required outfit icons,
  - score,
  - time.
- Bottom panel provides category controls and submit button.
- Game-over screen displays final score and restart button.

## Inferred genre / gameplay shape
- Strongest inferred shape: **dress-up matching game with timed arcade scoring**.
- It also behaves like a **memory/visual matching reflex game**, because the player must read symbolic target cues and configure the avatar accordingly under pressure.
- The pacing is short-session, replayable, and score-driven rather than progression-heavy.
- There are no levels, story branches, inventory systems, or exploration spaces.
- The fantasy witch theme is presentation-heavy, but the underlying mechanic is a compact outfit-combination puzzle loop.

## Gameplay heuristic
- The player likely succeeds by scanning the top-row target icons and mapping them to the current avatar parts quickly.
- Since each slot has only 5 states and each button wraps, the game encourages:
  - quick visual comparison,
  - rapid cycling,
  - immediate submission once all three target boxes glow.
- Optimal play pattern:
  1. identify unmatched categories,
  2. cycle only those categories,
  3. watch for matched highlight feedback,
  4. cast immediately,
  5. repeat before the timer drains.
- The time bonus on success means accurate fast play creates a positive loop, while repeated mistakes quickly collapse the run.

## Presentation and tone
- The game presents as whimsical, magical, slightly arcade-like, and kid-friendly.
- Tone combines:
  - enchanted wardrobe fantasy,
  - Halloween-lite witch motifs,
  - bright celebratory mobile UI polish.
- Visual language suggests a casual browser/mobile minigame intended for fast, accessible sessions.

## Confidence notes
- Confidence is high on the core mechanics because the entire game logic is visible in one file.
- Confidence is moderate on audience and genre labeling because the game mixes dress-up aesthetics with arcade score-attack structure.
- No hidden progression, persistence, or unlock systems are present in the inspected code.