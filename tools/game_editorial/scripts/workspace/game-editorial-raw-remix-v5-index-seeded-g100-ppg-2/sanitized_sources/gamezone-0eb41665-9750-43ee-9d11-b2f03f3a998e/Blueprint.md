# Blueprint

## High-level code structure
The game is implemented as a single self-contained HTML file with inline CSS, HTML UI, audio tags, and JavaScript gameplay logic. The codebase is organized conceptually into:

- **Presentation layer**: inline CSS styles for the full-screen canvas, glassmorphism HUD, start overlay, and reaction GIF feedback.
- **DOM/UI shell**: a canvas-based game container, a start screen, HUD score display, flux mode toggle button, reaction GIF layer, and HTML audio elements.
- **Audio system (`AudioSys`)**: lightweight audio manager that unlocks audio on first user input, starts looping background music, and clones sound effects for overlapping playback.
- **Game state (`Game`)**: a plain object storing canvas references, loop timing, score, mode toggles, orbital animation values, particles, floating messages, and tappable hit zones.
- **Runtime functions**:
  - initialization and resizing
  - start/toggle actions
  - input handling
  - spawning particles and messages
  - update step
  - render step
  - main animation loop

## Game loop / state model
The game uses a standard `requestAnimationFrame` loop:

1. **Initialize**
   - capture canvas/context
   - size canvas to viewport
   - bind pointer and button events
   - initialize audio
2. **Wait on start screen**
   - gameplay is visually running in the background, but interactions are ignored until `Game.isPlaying = true`
3. **Start shift**
   - hide modal
   - reveal HUD and flux button
   - reset score
   - begin music/sfx flow
4. **Per-frame update**
   - decrement short-lived feedback timers
   - advance orbital animation values for Earth, Moon, ISS, and drifting stars
   - update particles
   - update floating message bubbles
5. **Per-frame draw**
   - render either normal lounge view or flux wireframe mode
   - draw Earth, moon, ISS, orbital rings
   - draw three interactive desk/lounge objects
   - draw particles and floating message notifications
6. **Input resolution**
   - pointer taps test against three rectangular hit zones: TV, snack bowl, phone

State is lightweight and arcade-like rather than level-based. There is no fail state, no timer, and no explicit ending condition in code.

## Player goals
The player’s inferred goal is to perform a cozy orbital “shift” by interacting with lounge devices and repeatedly increasing the sync score. More specifically, the player is encouraged to:

- tap the **snack bowl** to gain score directly
- tap the **phone/comms device** to trigger playful incoming messages
- tap the **TV/lounge screen** to cycle ambient display channels
- optionally toggle **Flux Mode** for a stylized alternate visual state

The most direct progression vector is score accumulation, with the snack interaction acting as the main point-generating action.

## Interaction pattern
The interaction model is simple, tactile, and touch-friendly:

- **Start button** begins the session
- **Pointer/tap input on canvas** drives all gameplay
- Three spatially separated hotspots support “toy-like” repeated tapping
- Feedback is immediate through:
  - score gain
  - particles
  - message popups
  - sound effects
  - temporary hit flashes
  - animated reaction GIF overlays
- A dedicated **Flux Mode** button changes the audiovisual tone without changing the base loop dramatically

This creates a relaxed micro-sandbox rather than a challenge-heavy action game.

## Core systems
### 1. Ambient orbital scene
A continuously animated space backdrop with:
- drifting stars
- central Earth with rotating continents/clouds
- moon orbit
- ISS orbit
- glow, gradients, and orbit path rendering

### 2. Interactive lounge objects
Three core interaction stations:
- **TV**: cycles through stars, aurora, and static channels
- **Snack bowl**: grants score and celebratory particle bursts
- **Phone/comms**: spawns floating text messages from planets/station contacts

### 3. Score / sync system
A single visible numeric stat labeled **Sync** tracks progress. Only snack interaction reliably increases it, suggesting a light accumulation loop.

### 4. Flux Mode modifier
A toggleable alternate rendering mode that:
- swaps the scene into retro wireframe/grid visuals
- changes object styling and orbit lines
- slightly changes particle count/feel
- serves as a cosmetic/experiential modifier rather than a separate ruleset

### 5. Feedback layer
The game heavily emphasizes cozy positive feedback:
- background music loop
- UI and interaction sound effects
- floating comms text
- transient particle effects
- side GIF flashes for snack/message reactions

## Inferred genre / gameplay shape
The strongest inferred shape is a **casual relaxing interaction sandbox / toy** with clicker-lite qualities. It feels like:

- a **cozy space lounge simulator vignette**
- a **light clicker/incremental toy** because score rises through repeated snack taps
- a **micro life-sim / roleplay scene** because the player inhabits a soft fictional shift in orbital mission control
- a **meta ambient desktop toy** more than a challenge-oriented game

There is little evidence of obstacles, enemies, survival pressure, puzzle solving, or strict progression gates. The game is best understood as a short-form atmospheric interactive scene centered on repeated soothing interactions and score accumulation.

## Gameplay heuristic
A player likely succeeds by treating the game as a playful maintenance routine:

- start the shift
- alternate between the three touch targets
- use snack taps for score growth
- use TV taps to vary ambience
- use phone taps to trigger personality and world flavor
- optionally toggle Flux Mode for aesthetic variation
- continue interacting for mood, feedback, and score

The design priority appears to be **pleasant audiovisual reward and theme coherence** over mastery, difficulty, or strategic optimization.