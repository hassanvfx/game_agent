# Blueprint

## High-level code structure
- Single-file web game implemented entirely in `index.html`.
- Presentation layers are split into:
  - HTML HUD/start screen/chat/feedback overlays
  - CSS for neon cyberpunk styling, responsive layout, and mobile joystick treatment
  - Inline JavaScript for state, audio, input, Three.js scene setup, NPC logic, and the animation loop
- Rendering uses Three.js with:
  - a scene, perspective camera, and WebGL renderer
  - dynamic lights and a shader-driven floor in high-quality mode
  - simple procedural character models for the player and NPC couriers
- UI controls include:
  - start screen with color selection
  - HUD score display
  - quality toggle
  - camera mode toggle
  - mobile virtual joystick
  - transient feedback toast/GIF overlays
  - floating chat bubbles above NPCs

## Game loop / state model
### Core state
A small mutable `gameState` object drives the session:
- `active`: whether play has started
- `score`: number of successful proximity-based deliveries/syncs
- `playerColor`: selected suit color
- `quality`: `HIGH` or `LOW`
- `camMode`: `ISO` or `TOP`

### Loop shape
Once the player presses **Start Route**:
1. audio is unlocked and BGM starts
2. start screen hides and HUD appears
3. `gameState.active` becomes true
4. `gameLoop()` begins with `requestAnimationFrame`

Per frame the loop:
- updates shader/light ambience
- updates player movement and camera follow
- updates NPC wandering and interaction checks
- renders the scene
- schedules the next frame

### Interaction state
- Keyboard: WASD movement
- Mobile: virtual joystick movement
- Buttons: quality mode and camera mode toggles
- Start state includes only cosmetic suit-color selection; it does not alter mechanics

## Player goals
- Move around a neon city-grid plaza
- Approach roaming courier NPCs closely enough to trigger a “drop-off synced” event
- Accumulate as many successful contacts/deliveries as possible
- Maintain flow by continuously seeking the next nearby target

There is no explicit fail state, timer, or finite level completion in code. The game behaves like a score-chasing free-play arcade session.

## Interaction pattern
- Start on a themed intro card
- Choose one of four runner suit colors
- Press **Start Route**
- Navigate a bounded square arena
- Contact NPC couriers by entering a short interaction radius
- Receive audiovisual feedback:
  - score increase
  - success toast/GIF
  - delivery-style chat bubble
- Re-contacting the same NPC requires leaving the radius first because each NPC toggles a `met` flag while nearby
- Attempting conflicting axis movement on keyboard can trigger “Lane lock” blocked feedback

## Core systems
### 1. Movement system
- Free 2D plane movement across X/Z axes
- Keyboard and joystick inputs are combined
- Diagonal keyboard movement is normalized
- Player rotation faces movement direction
- Position is clamped within arena bounds

### 2. Camera system
Two viewpoints:
- `ISO`: lower isometric chase-like perspective
- `TOP`: higher overhead tracking perspective

### 3. NPC roaming system
- 15 NPC couriers are spawned
- Each NPC wanders toward random targets
- On reaching a target, it picks another
- NPCs have floating emissive markers and minor bobbing to stay readable

### 4. Delivery/contact scoring system
- If player comes within distance `< 3` of an NPC and that NPC is not currently flagged as met:
  - score increments
  - delivery feedback is shown
  - sounds play
  - NPC chat appears
- When player leaves the radius, the NPC becomes available to score again later

### 5. Feedback/polish system
- Background music and multiple SFX cues
- Success/fail toast messaging
- Success/fail animated GIF overlays
- Floating NPC speech bubbles
- Pulsing player ring, emissive visor/boosters, neon lane grid, fog and lighting pulses

### 6. Performance/options system
- High/low quality toggle swaps:
  - shader floor vs simpler material
  - fog on/off
  - shadows on/off
  - light intensity adjustments

## Inferred genre / gameplay shape
Strongest inference: a lightweight **arcade exploration / collection runner** with social-delivery flavor.
- Not a literal endless runner because the player moves freely in a bounded arena
- Structurally closest to a casual **collectathon / score-chase runner** with mobile-friendly controls
- Theme framing suggests being a futuristic courier tagging roaming contacts rather than combat or puzzle play

## Gameplay heuristic
The intended play fantasy appears to be:
- glide around a neon sci-fi plaza
- feel stylish and fast
- “deliver” or “sync” with as many wandering couriers as possible
- enjoy positive feedback bursts and ambient cyber-audio/visual polish
- optionally adjust viewpoint and quality for comfort/device performance

## Confidence notes
- High confidence on the code structure, controls, scoring behavior, NPC interaction radius, and audiovisual systems
- Medium confidence on the exact fiction of “delivery” versus “social sync/tagging,” because code and UI use both courier-delivery and contact-tagging language
- High confidence that progression is endless/free-play score accumulation rather than staged levels
