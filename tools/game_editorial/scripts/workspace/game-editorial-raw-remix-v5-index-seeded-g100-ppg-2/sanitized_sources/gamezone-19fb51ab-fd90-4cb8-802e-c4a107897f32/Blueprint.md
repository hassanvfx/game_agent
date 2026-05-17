# Blueprint

## High-level code structure
- The entire game is contained in a single `index.html` file.
- Structure is split into:
  - inline CSS for the neon sci-fi presentation, HUD, start overlay, and responsive layout
  - HTML for the canvas, HUD, start screen, audio tags, and reaction-card overlays
  - inline JavaScript for config parsing, audio handling, input, state, rendering, and the main loop
- There is no framework, module system, or external game engine. The game is a custom canvas scene with DOM-based UI overlays.

## Game loop / state model
- Core state is minimal and arcade-like:
  - `isPlaying` gates whether the canvas accepts input and whether the loop has begun
  - `glitchTimer` and `glitchActive` control the temporary glitch effect state
  - `activeChats` stores currently visible floating dialogue bubbles
  - `particles` stores short-lived ripple particles from tapping empty space
  - `cameraShake` stores temporary screen shake during glitches
- `requestAnimationFrame(loop)` drives the game.
- Each frame:
  - updates glitch timing and shake
  - clears and redraws the background
  - draws the tree/perch scene
  - draws each drone character
  - updates and renders ripple particles
  - updates and renders floating chat bubbles
  - draws temporary glitch overlays when active

## Player goals
- The immediate player goal is expressive discovery rather than winning.
- The player is encouraged to tap each perched drone to reveal randomized chatter lines.
- The standout interaction is tapping Sitrus specifically to trigger a brief audiovisual glitch event.
- Empty-space taps produce a quieter ripple reward, so the player is softly encouraged to probe the whole scene.

## Interaction pattern
- Start screen introduces the interaction rules directly.
- Single-pointer/tap input is the only gameplay verb.
- Tapping near a character:
  - spawns a speech bubble
  - plays a chat sound
  - shows a reaction card
- Tapping Sitrus additionally:
  - activates a short glitch state
  - changes the HUD mood indicator
  - adds shake, red signal styling, and glitch lines
  - plays the glitch sound and glitch reaction card
- Tapping empty snow:
  - spawns particles
  - plays a softer reward-like sound

## Core systems
- **Canvas renderer:** draws environment, characters, labels, particles, and chat bubbles.
- **Character interaction system:** hit-tests pointer distance against five static character anchor points.
- **Dialogue system:** each character has a small bank of randomized quotes.
- **Glitch feedback system:** temporary state swap for visuals, HUD text, camera shake, and sound.
- **Audio manager:** unlocks audio after user interaction, plays looped ambience plus event SFX, and falls back to synthesized sounds if decoding fails.
- **Responsive UI layer:** DOM HUD and start screen sit above the canvas and remain mobile-safe.

## Inferred genre / gameplay shape
- Best described as a **micro interactive character scene** or **ambient tap-to-react toy**.
- It behaves more like a lightweight exploratory interaction piece than a progression-heavy game.
- From the provided category universe, it overlaps most with clicker/tapping interaction, chat-style interaction, and meta/novelty toy experiences rather than action, strategy, or simulation loops.

## Heuristic read of the experience
- Theme and names point to a fan-inspired or fandom-adjacent sci-fi character perch vignette.
- The experience centers on mood, reactions, and personality snippets instead of challenge escalation.
- The game loop is intentionally shallow but polished:
  1. start session
  2. tap drones to hear lines
  3. trigger Sitrus glitch moments
  4. tap around for ambient ripple effects
  5. continue sampling dialogue and presentation feedback
- There is no score, failure condition, level progression, or unlock structure visible in code.
- Replayability comes from randomized lines, audiovisual feedback, and character/fandom appeal rather than systemic depth.
