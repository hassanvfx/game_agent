# Blueprint

## High-level code structure
- Single-file HTML game in `index.html`.
- Inline CSS defines the full neon sci-fi presentation, HUD, start/pause overlays, brush controls, palette cards, and mobile-safe layout.
- Inline JavaScript contains the entire runtime:
  - asset URL configuration for remote audio
  - element definitions and color/density metadata
  - `AudioController` for BGM/SFX lifecycle
  - canvas/grid initialization and resize handling
  - cellular-automata update functions for materials
  - pixel renderer using `ImageData`
  - pointer-based painting input
  - UI construction for the element palette and brush selector
  - start/pause/resume/clear screen flow

## Game loop / state model
- The game starts on a title screen and becomes active only after pressing the start button.
- Core mutable state:
  - `grid`: flattened particle simulation board
  - `currentElement`: currently selected material/tool
  - `brushSize`: paint radius
  - `particleCount`: active non-empty/non-stone cells
  - `gameActive`: master pause/run flag
  - pointer state for drag painting
- Runtime loop is split into:
  - `updateLoop()` using `setTimeout` at roughly 60 FPS for simulation
  - `draw()` using `requestAnimationFrame` for rendering
- Pausing halts simulation by setting `gameActive = false`.
- Clearing resets the grid while preserving the stone floor boundary.

## Player goals
- Primary goal is expressive sandbox play rather than winning.
- The player paints different matter types into the chamber and watches interactions create “chaos.”
- Secondary self-directed goals include:
  - filling the chamber with moving particles
  - making satisfying chain reactions
  - combining materials for visual/audio feedback
  - experimenting with how each material behaves against the others

## Interaction pattern
- Press start to enter the lab.
- Select a material from the bottom palette.
- Select brush size from small/medium/large controls.
- Drag or tap on the canvas to stamp particles into the simulation.
- Open the pause menu to inspect current chaos count, resume, or purge the board.

## Core systems
- **Particle sandbox simulation:** sand falls diagonally, liquids flow sideways/downward, fire rises and burns out, acid corrodes some materials.
- **Material identity system:** Reset, Cringe/Sand, Hype/Water, Block/Stone, Vibe/Plant, Roast/Fire, Glitch/Acid.
- **Painting tool system:** circular brush with three radius presets.
- **Feedback system:** particle count HUD, pause summary, sound effects, reaction GIF popups for combos and purge moments.
- **Audio system:** looping arcade ambience plus SFX for start/select/paint/pause/resume/blocked/combo/clear.
- **Responsive HUD layout:** thumb-safe palette dock and button arrangement designed for touch devices.

## Inferred genre / gameplay shape
- Closest shape is a **physics sandbox / falling-sand toy** wrapped in a meme-neon arcade presentation.
- It behaves like a playful creation toy more than a level-based challenge game.
- The experience emphasizes tactile experimentation, emergent interactions, audiovisual reward, and freeform remixing rather than progression gates or failure states.

## Gameplay heuristic
- Best play comes from quickly switching between stable matter and reactive matter:
  - use **Block** to create barriers
  - pour **Hype** to spread liquid channels
  - drop **Cringe** to make piles and cascades
  - place **Vibe** as flammable structure
  - ignite with **Roast**
  - dissolve setups with **Glitch**
- The system rewards dense painting because large brush strokes can trigger combo feedback and visibly increase the chaos counter.
- There is no explicit scoring ladder, so player motivation is curiosity, spectacle, and experimentation.

## Confidence notes
- High confidence that the implementation is a restyled falling-sand sandbox because the update rules directly define particle interactions.
- Medium confidence on intended fantasy/theme framing because “meme chaos lab” is mostly aesthetic language layered over standard material simulation behavior.
