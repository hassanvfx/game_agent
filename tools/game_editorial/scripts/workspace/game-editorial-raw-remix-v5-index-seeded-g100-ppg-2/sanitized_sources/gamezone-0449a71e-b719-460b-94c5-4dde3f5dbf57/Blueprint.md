# Blueprint

## High-level code structure
This project is a single-file HTML game with all presentation, logic, and rendering embedded directly in `index.html`.

Primary layers:
- **HTML structure**: canvas for the game scene, overlay cards for start/end screens, a HUD score pill, two GIF feedback images, and a reveal message.
- **CSS styling**: neon-glass UI, responsive mobile-safe layout, full-screen canvas, and animated UI visibility states.
- **JavaScript runtime**:
  - `CONFIG`: target score, color palette, audio URLs, GIF URLs, and letter scale.
  - `state`: round state, score, win flag, camera values, seal animation values, particles, and GIF timers.
  - `audio`: lightweight audio manager for BGM and one-shot SFX.
  - rendering helpers: background, giant hidden letter, seal, and particles.
  - loop/update/gameplay functions: start, restart, tap handling, win trigger, render loop, and input listeners.

## Game loop / state model
The game uses a simple animation loop driven by `requestAnimationFrame`.

### Main state phases
1. **Start screen / idle**
   - Start overlay visible.
   - Game inactive.
   - First interaction unlocks audio.

2. **Active tapping round**
   - HUD visible with `score / targetScore`.
   - Every non-button pointer press increments score.
   - Seal plays squash/bounce feedback.
   - Particle burst spawns.
   - Tap GIF appears briefly.
   - Camera starts zoomed toward the seal, hiding the larger reveal beneath it.

3. **Win / reveal**
   - Triggered when `score >= targetScore` (50).
   - Active play stops.
   - Win sound plays, BGM pauses.
   - Camera zooms/pans out to frame the whole hidden giant “YO” / `Ё`.
   - Reveal text and victory GIF appear.
   - End screen appears after delay with replay button.

4. **Restart**
   - Score, particles, reveal state, and camera reset.
   - Another identical round begins.

### Update model
Each frame:
- Camera interpolates toward `targetCam`.
- Seal deformation animates back to rest.
- Particles update position, gravity, and lifetime.
- Win condition is checked.

## Player goals
The immediate player goal is to **tap repeatedly until the score reaches 50**.

The thematic goal is to:
- “hype up” or pet the cute neon seal,
- cause a reveal,
- uncover the hidden giant glowing “YO” letter underneath the seal.

This is not a strategic challenge-heavy game; it is a short novelty satisfaction loop centered on repeated interaction and payoff.

## Interaction pattern
Core interaction is extremely simple:
- **Start button** begins the round.
- **Tap/click/pointer down anywhere except buttons** to score.
- **Restart button** replays after the reveal.

Interaction style:
- one-input, single-screen, arcade-like clicker/tapper
- works for mouse and touch
- includes mobile-friendly input guards (`touchmove` prevention while active, disabled gesture zooming)

## Core systems
### 1. Tap scoring system
Each tap increments score by exactly one and updates the HUD.

### 2. Seal feedback animation
Taps cause:
- squash/stretch on the seal
- slight bounce offset
- tactile visual response

### 3. Particle feedback
Each tap emits a small burst of glowing particles around the seal.

### 4. Camera reveal system
The hidden structure of the scene is the main gimmick:
- the seal initially sits over a much larger glyph
- the camera is zoomed in during tapping
- on win, the camera zooms out to expose the giant letter composition

### 5. Audio system
Includes:
- looping ambient arcade BGM
- tap/pulse SFX
- start SFX
- win SFX
- visibility pause/resume handling for background audio

### 6. UI state transitions
Start card, HUD, reveal message, GIF badges, and end card are shown/hidden according to round state.

## Inferred genre / gameplay shape
Strongest inferred genre shape:
- **clicker / tapper microgame**
- **toy-like reveal experience**
- **short-form casual novelty interaction**

The play pattern is:
1. enter a bright themed screen,
2. repeatedly tap for immediate juicy feedback,
3. reach a fixed threshold,
4. receive a reveal animation and celebratory ending,
5. optionally replay.

## Presentation and aesthetic heuristic
The game aims for:
- cute absurd humor
- neon arcade polish
- meme-adjacent animal charm
- quick payoff and satisfying audiovisual feedback

Visual cues:
- cyan/pink neon palette
- glassmorphism UI cards
- oversized cartoon seal
- giant hidden letter as the punchline/reward
- GIF overlays as celebratory reaction inserts

## Confidence notes
Confidence is high on the game loop and interaction model because they are explicit in the code and UI text.
Confidence is moderate on deeper intent beyond the novelty reveal because the game is very minimal and does not contain broader content systems, narrative, or progression beyond replay.