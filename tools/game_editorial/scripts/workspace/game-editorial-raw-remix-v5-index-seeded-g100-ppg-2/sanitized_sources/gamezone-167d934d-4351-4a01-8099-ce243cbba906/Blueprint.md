# Blueprint

## High-level code structure
The game is a single-file HTML application with all systems embedded in `index.html`.

- **Presentation layer**
  - Inline CSS defines the sky-themed visual identity, HUD, start screen, game-over panel, feedback cards, and responsive behavior.
  - The DOM includes a full-screen `<canvas>` for gameplay plus overlay UI panels for title, score, restart flow, and animated feedback.
- **Config layer**
  - A JSON blob in the `#game-config` script tag exposes editable runtime values for scroll speed, jump force, gravity, and theme color.
  - `window.gameConfigDefs`, `window.gameConfig`, and `window.updateGameConfig()` form a lightweight live-tuning interface.
- **Asset layer**
  - Player, platform, and collectible visuals are embedded as inline SVG data URIs.
  - Audio uses remote approved URLs for background music and SFX.
  - Feedback overlays use remote GIFs for pickup/failure reactions.
- **Runtime/gameplay layer**
  - A `DOMContentLoaded` boot function initializes canvas rendering, UI references, audio, input, state variables, entities, resize handling, the main loop, and button events.
  - Core functions include `initGame`, `generatePlatform`, `gameOver`, `update`, `draw`, and `loop`.

## Game loop / state model
The game uses a continuous `requestAnimationFrame` loop.

### States
- **START**
  - Start panel visible
  - Gameplay input ignored
  - Waiting for button click
- **PLAYING**
  - World scrolls horizontally at a constant speed
  - Player physics, collisions, scoring, particles, collectibles, and audio all update every frame
- **GAMEOVER**
  - Motion effectively stops because `update()` exits unless state is `PLAYING`
  - Final score and best score are displayed
  - Restart button resets the run

### Per-frame flow
1. Compute `dt` from frame timing.
2. If in `PLAYING`, update:
   - camera/world scroll
   - score
   - player gravity and movement
   - platform collisions
   - death check
   - procedural platform generation and old platform cleanup
   - collectible detection
   - particle simulation
3. Draw:
   - themed sky background
   - parallax-style clouds
   - platforms
   - floating collectible icons
   - rotating/squashing player sprite
   - particles
4. Queue next animation frame.

## Player goals
The immediate goal is to survive by chaining jumps across floating platforms while the camera auto-scrolls forward.

The scoring goal is to collect as many floating package-tag/coin pickups as possible and stay alive long enough to increase the route score. The game frames these pickups as “packages saved,” making successful traversal and collectible collection the shared objective.

## Interaction pattern
- **Primary input:** pointer/tap on canvas or keyboard Space
- **Action:** jump
- **Mobility rule:** the player can jump twice before landing
- **Failure condition:** fall below the bottom of the screen
- **Session structure:** start run → traverse platforms and collect pickups → fail → view score/best → restart

This is a one-button timing game centered on jump rhythm, gap judgment, and air-control through double jump.

## Core systems
### 1. Endless runner scroll system
- The camera advances automatically using `scrollSpeed`.
- The player stays roughly fixed horizontally on screen while the world moves relative to `cameraX`.

### 2. Platform traversal system
- Platforms are generated ahead with randomized gaps, widths, and heights.
- Old platforms are removed once they leave the view behind the player.
- Collision only resolves when landing from above, reinforcing precision platforming.

### 3. Double-jump player controller
- The player has gravity, vertical velocity, grounded state, jump count, rotation, and squash/stretch feedback.
- A jump resets upward velocity and increments `jumps`.
- Landing restores jump availability.

### 4. Collectible scoring system
- Floating collectible objects spawn near many platforms.
- Proximity pickup grants a large score bonus.
- Pickup triggers sound, particles, and celebratory feedback UI.

### 5. Score and persistence system
- Score increases gradually with forward distance and sharply with collectible pickups.
- Best score is saved in `localStorage` under `skyhopper_best`.

### 6. Juice/feedback system
- Particle bursts on jump, pickup, and death
- Rotation and squash/stretch on movement
- Screen shake on failure
- HUD and animated feedback cards
- Layered SFX plus looping BGM, with Web Audio fallbacks if media playback fails

### 7. Responsive/mobile-safe canvas shell
- Fullscreen canvas adapts to device pixel ratio and window size
- Mobile-safe UI spacing and touch input support are built in
- Canvas disables default touch behavior to preserve direct input

## Inferred genre / gameplay shape
Strongest inference: **endless auto-scrolling platform runner** with arcade score-chasing structure.

It combines:
- endless runner pacing
- platformer jump timing
- collectible route optimization
- short replayable arcade sessions
- light presentation framing around courier deliveries in the sky

## Gameplay heuristic
The intended play feel is:
- read the next floating platform quickly
- time the first jump to clear the gap
- use the second jump as correction or to reach elevated pickups
- land cleanly to refresh jumps
- collect bonus tags when safe, but prioritize survival
- replay repeatedly to push the best route/package score

The difficulty comes less from enemies and more from:
- randomized platform spacing/height
- auto-scroll pressure
- limited jump budget before landing
- greed-vs-safety decisions around collectibles

## Confidence notes
Confidence is fairly high on the underlying mechanics because the implementation is explicit:
- one-button/double-jump traversal
- endless forward scroll
- procedural platforms
- score-based arcade loop

Some thematic framing is slightly softer:
- the code calls collectibles `coins`, but all user-facing text reframes them as package tags/packages saved
- the title and UI imply a courier fantasy rather than literal coin collection

Overall inference: a polished sky-delivery endless platform runner with double-jump movement and collectible-based scoring.