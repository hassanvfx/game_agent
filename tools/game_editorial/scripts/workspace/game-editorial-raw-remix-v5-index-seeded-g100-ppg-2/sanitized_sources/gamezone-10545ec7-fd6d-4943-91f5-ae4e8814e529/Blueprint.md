# Blueprint

## High-level code structure
- Single-file browser game contained in `index.html`.
- HTML defines layered UI screens over a full-screen `<canvas>`:
  - main menu
  - style/customization screen
  - flight brief screen
  - pause/holding-pattern novelty screen
  - HUD
  - game over screen
  - cutscene prompt
- CSS provides a glossy arcade presentation, responsive mobile-safe layout, and style-dependent post-processing filters.
- JavaScript contains the full runtime:
  - configuration and mutable game state
  - audio loading and playback helpers
  - resize handling
  - procedural canvas rendering helpers
  - themed landmark renderer
  - a style/theme registry with alternate renderers for background, player, and obstacles
  - core game loop
  - cutscene/dialogue handling
  - UI/menu event wiring

## Game loop / state model
The game uses a continuously running `requestAnimationFrame` loop with a small explicit state machine.

### Main states
- `MENU`: player is in front-end UI and not actively flying
- `CUTSCENE`: a short pre-run dialogue sequence plays with tap-to-continue progression
- `PLAYING`: endless active run
- `GAMEOVER`: run has ended; score is shown and restart/menu options appear

### Per-frame update behavior
During play:
- gravity pulls the aircraft downward every frame
- tap/space input applies an upward lift impulse
- background and landmark scroll to imply forward movement
- clouds move independently for parallax flavor
- obstacle pillars spawn at intervals
- collectible score items spawn at shorter intervals
- all obstacles move left at `gameSpeed`
- collision with collectibles increments score and may increase speed every 5 points
- collision with hazard pillars or leaving vertical bounds triggers game over

## Player goals
- Keep the aircraft on-screen and away from top/bottom skyline obstacles.
- Collect floating pickups for points.
- Survive as long as possible while speed gradually rises.
- Optionally experiment with different cosmetic route “styles” and camera zoom levels.

## Interaction pattern
- Primary input is one-button/tap control.
- `pointerdown` on canvas or `Space` key both serve as the main action.
- In cutscenes, the same input advances or fast-forwards dialogue.
- In gameplay, that same input performs the climb/flap action.
- Menus are button-based and touch-friendly.

This is effectively an arcade “tap to stay airborne” loop.

## Core systems
### 1. Flight physics
- Simple vertical velocity model
- Constant gravity
- Fixed negative lift impulse on input
- Light sprite tilt based on vertical speed

### 2. Endless obstacle stream
- Procedurally spawned top or bottom rectangular hazards
- Constant leftward movement
- Collision by axis-aligned overlap

### 3. Collectible scoring
- Coin-like pickups spawn more frequently than hazards
- Touching one:
  - increments score
  - updates HUD
  - plays reward SFX
  - shows feedback GIF
  - slightly ramps difficulty every 5 pickups

### 4. Style remix system
A major wrapper system remaps the same mechanics into many visual jokes/themes:
- liberty/classic
- stone age
- lego
- bubbles
- among us parody
- sports/superbowl
- puppets
- daycare/crayon
- neon
- paper/sketch
- glitch
- clay
- christmas
- food
- noir/1930s
- gothic
- jelly
- lowpitch
- pixel

These styles alter:
- background rendering
- player vehicle appearance
- obstacle appearance
- landmark/statue presentation
- canvas filter mood

The obstacle course and rules stay the same across styles.

### 5. Presentation/cutscene layer
- Short intro dialogue gives the run a themed “flight brief”
- HUD shows only score during play
- game over screen presents final score and retry loop
- feedback GIFs reinforce success/failure moments

### 6. Audio system
- Remote approved audio URLs are used for:
  - looping gameplay music
  - pickup
  - fail/game over
  - dialogue tick
  - flap/jump
  - menu / confirm / resume UI sounds
- Audio unlock is deferred until first interaction for browser compatibility

## Inferred genre / gameplay shape
- Primary genre: endless runner / lane-free flyer hybrid
- Control feel: Flappy Bird-style tap flyer
- Camera/view: 2D side-view continuous scroll
- Session length: short-run arcade replay loop
- Structure: menu -> optional intro cutscene -> survival run -> game over -> retry/menu

## Gameplay heuristic
The game appears designed as a lightweight, fast-restart arcade toy:
- one-button accessibility
- immediate readability
- high replayability through short attempts
- novelty driven by cosmetic theme swaps rather than rules changes
- score chasing rather than level completion

## Confidence notes
High confidence:
- endless tap-to-fly survival structure
- score-through-collectibles loop
- obstacle avoidance core
- style-remix framing

Moderate confidence:
- the intended fantasy is more “tourist flyby over Liberty” than strict aviation simulation
- category fit leans toward endless runner/void runner/runner-adjacent rather than a formal flying genre because the provided taxonomy does not include “flappy flyer”