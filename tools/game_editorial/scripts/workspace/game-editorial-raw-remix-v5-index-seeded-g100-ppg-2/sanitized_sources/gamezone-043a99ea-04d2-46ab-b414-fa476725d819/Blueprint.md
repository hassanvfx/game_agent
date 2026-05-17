# Blueprint

## High-level code structure
The game is implemented as a single self-contained HTML file with three main layers:

1. **Presentation layer**
   - Inline CSS defines the retro neon aesthetic, overlay cards, HUD, and responsive/mobile-safe layout.
   - A full-screen `<canvas>` is used for all gameplay visuals.
   - DOM overlays handle the start screen, game-over screen, HUD, and animated feedback GIF/caption.

2. **Game logic layer**
   - A DOMContentLoaded bootstrap sets up state, canvas references, input handlers, audio, and the main loop.
   - Core logic lives in plain functions for spawning, updating, drawing, collision checks, HUD sync, and state transitions.

3. **Audio/feedback layer**
   - `AudioController` manages background music, sound effects, unlock-on-interaction behavior, and simple anti-spam cooldowns.
   - Visual feedback for success/failure is handled with a GIF + caption overlay.

## Game loop / state model
The game uses a standard `requestAnimationFrame` loop while `gameActive` is true.

### Primary states
- **Start screen / idle**
  - Start overlay visible
  - No gameplay simulation running
- **Active run**
  - HUD visible
  - Game loop continuously updates movement, spawns content, checks collisions, and renders
- **Game over**
  - Loop stops via `gameActive = false`
  - Final score shown
  - Restart returns to a fresh run

### Runtime state variables
- `score`: increased by heart collection
- `frame`: drives spawn timing and animation motion
- `gameSpeed`: slowly ramps up over time for difficulty scaling
- `player`
  - fixed horizontal position
  - dynamic vertical separation (`gap`) between two avatars
  - hugging/split boolean derived from gap
- `obstacles`: mixed array containing hazards and collectibles
- `particles`: transient visual reward/fx particles
- `isPointerDown`: core input flag controlling hug/split mode

## Player goals
The player’s goal is to survive as long as possible while collecting hearts for score.

More specifically, the player must:
- **hold input to bring the two characters together** so they can fit through center tunnels
- **release input to split them apart** so they can avoid central blocking hazards
- collect hearts positioned either in the center lane or in split top/bottom lanes
- react quickly as speed increases

This creates a score-chasing survival loop with light pattern recognition.

## Interaction pattern
The interaction model is extremely simple and binary:
- **Press / hold** mouse or touch: characters hug together
- **Release**: characters separate into upper and lower lanes

The player does not steer horizontally. The game scrolls hazards from right to left while the pair stays at a fixed x-position, making this a one-button lane-shape switching game.

## Core systems
### 1. Dual-character formation system
The central mechanic is the pair of characters changing formation:
- **Split mode**: top and bottom avatars are separated vertically
- **Hug mode**: the gap collapses until they effectively overlap into the center lane

This is the key system that all hazards and pickups are designed around.

### 2. Obstacle generation
Two main hazard types appear:
- **middle_block**
  - occupies the central region
  - punishes hugging / center positioning
- **tunnel**
  - leaves a safe center passage
  - punishes staying too separated

This creates alternating “invert your state” demands.

### 3. Collectible placement logic
Hearts spawn in positions that often correspond to the nearby obstacle pattern:
- center heart for hugging/center alignment
- paired top/bottom hearts for split alignment

This means scoring is not separate from survival; collectibles reinforce the same formation-reading mechanic.

### 4. Collision and scoring
- Colliding with hazards ends the run immediately
- Collecting hearts grants `+10`
- Hearts can be collected by either avatar, depending on formation and placement

### 5. Difficulty escalation
- `gameSpeed` increases continuously over time
- obstacles/collectibles spawn on a regular frame cadence
- reaction pressure rises the longer the run continues

### 6. Juice / feedback systems
- particles on heart pickup and hugging pulses
- reactive GIF/caption feedback
- BGM plus SFX for start, toggle, collect, and fail
- pixel-art character rendering and parallax skyline/sparkle background

## Inferred genre / gameplay shape
This appears to be a **one-button arcade avoidance runner** with strong overlap across:
- endless runner
- lane/formation switching game
- score attack survival arcade game

It is not a traditional platformer or racer. The player is effectively reading upcoming patterns and toggling between two body configurations to survive and optimize pickups.

## Gameplay heuristic
The core heuristic is:

1. Watch the next obstacle shape.
2. If the safe route is the center lane, **hold** to hug.
3. If the center is blocked, **release** to split.
4. Collect hearts when their placement matches the required formation.
5. Maintain rhythm as the game speeds up.

The game rewards anticipation over precision steering. Success depends on correctly mapping each incoming pattern to the required pair formation.

## Presentation and tone
The presentation suggests:
- neon pixel romance theme
- playful melodrama rather than serious challenge framing
- arcade cabinet energy with humorous “clingy love” framing
- cute but slightly chaotic relationship comedy

Key presentation cues:
- neon pink/cyan palette
- pixel-art characters and hearts
- skyline and sparkle background
- dramatic labels like “Drama Alert” and “Heartbroken!”

## Confidence notes
Confidence is **high** on the basic mechanics because they are explicit in code and UI copy.

Confidence is **moderate to high** on genre interpretation:
- clearly an endless survival runner variant
- specifically a binary state-switching / lane-shape timing game rather than a broad runner with free movement

Confidence is **high** that the romance framing is thematic rather than narrative:
- there is no story progression, dialogue, or level structure
- the game is score-based and arcade-first