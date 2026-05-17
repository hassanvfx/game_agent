# Blueprint

## High-level code structure
The game is implemented as a single self-contained `index.html` document with three main layers:

1. **Presentation / UI layer**
   - CSS defines a neon sci-fi HUD, crosshair, damage vignette, mobile virtual stick display, reaction GIF cards, and a game-over overlay.
   - HTML contains the canvas, HUD counters, audio tags, reaction media, and restart button.

2. **Configuration / assets layer**
   - Inline JSON config (`#game-config`) exposes three tunable values: movement speed, turn sensitivity, and fog density.
   - Remote audio is attached through `<audio>` elements for gameplay loop, defeat loop, damage, enemy hit, pickup, miss, restart, and death.
   - Reaction GIF cards are shown as UI feedback for successful purges and failure moments.

3. **Game logic / rendering layer**
   - JavaScript handles initialization, state transitions, pointer input, audio unlock, procedural map generation, entity spawning, update loop, raycast rendering, sprite rendering, HUD refresh, and feedback effects.
   - Rendering uses a classic pseudo-3D raycaster approach with simple colored walls and billboard sprites rather than true 3D models.

## Game loop / state model
The runtime uses a continuous `requestAnimationFrame` loop.

### Main states
- **BOOT**
  - Initial placeholder before setup completes.
- **PLAYING**
  - Core active gameplay.
  - Updates movement, enemy pursuit, damage, interactions, and rendering each frame.
- **GAMEOVER**
  - Freezes active gameplay updates.
  - Displays final gem count and a restart button.

### Loop shape
Each animation frame:
1. Compute delta time.
2. If state is `PLAYING`:
   - Update player movement from pointer drag input.
   - Update nearby enemy chase behavior.
   - Apply damage if enemies reach the player.
   - Render walls, floor, ceiling, and sprites.
3. Queue next frame.

## Player goals
Primary inferred goals:
- Survive as long as possible in a maze while avoiding or purging hostile glitch entities.
- Collect “reaction gems” to increase the score-like diamond count.
- Maintain health (“Signal”) and prevent the stream from crashing.

Failure condition:
- Health reaches zero, triggering the “STREAM DOWN” game-over screen.

There is no explicit win condition, so the structure reads as survival-score play rather than a level-based completion game.

## Interaction pattern
The game is designed mainly for touch/mobile, though it can also work with pointer input on desktop.

### Controls
- **Drag vertically**: move forward or backward.
- **Drag horizontally**: rotate view left or right.
- **Tap**: interact in front of the player.

### Tap interaction behavior
If a valid entity is close and roughly in front of the player:
- **Glitch enemy**: removed in one hit.
- **Reaction gem**: collected and increments gem count.

If nothing valid is hit:
- Plays a miss/block sound and a brief visual swing effect.

This makes the interaction model feel like a simplified first-person melee/action-survival loop with close-range pickup collection.

## Core systems
### 1. Procedural maze generation
- Map is a 24x24 grid.
- Outer border is always walls.
- Interior tiles are randomly assigned walls with a low density.
- This creates a lightweight, replayable labyrinth each restart.

### 2. Player movement and facing
- Player has raycaster-style position, direction vector, and camera plane.
- Collision checks prevent walking through walls.
- Control scheme behaves like a hybrid of tank controls and first-person touch steering.

### 3. Enemy chase system
- Enemies of type `2` activate within an aggro radius.
- They move directly toward the player with simple wall-aware stepping.
- Contact deals repeated damage.

### 4. Collectible loop
- Gems of type `3` can be collected at close range.
- Collected gems increment the diamond counter.
- Gems respawn after a delay, reinforcing endless survival scoring.

### 5. Combat / purge interaction
- Combat is short-range and proximity-based rather than projectile-based.
- A target must be close and generally in front of the player.
- Glitches are instantly cleared on successful interaction.

### 6. HUD and feedback
- Health displayed as “Signal.”
- Gem total displayed as “Gems.”
- Damage overlay, shake, vibration, SFX, and meme reaction cards reinforce hits, pickups, and defeat.

### 7. Audio state handling
- Audio is unlocked on first interaction.
- Gameplay loop and defeat loop swap based on game state.
- SFX playback uses cooldown protection and oscillator fallback.

## Inferred genre / gameplay shape
Strongest gameplay reading:
- **First-person maze survival action game**
- **Light raycast shooter / close-range action survival**
- **Arcade survival score chaser with meme-streamer theming**

The game is not a traditional shooter because attacks are proximity-based and there are no projectiles or firearms, but it borrows first-person shooter presentation and pressure structure:
- first-person camera
- enemies approaching in real time
- tap-to-attack interaction
- survival through navigation and combat

## Presentation and fantasy
The presentation suggests a parody of streamer culture and meme-chaos aesthetics:
- Title: **Meme Maze Panic 3D**
- Player fantasy: guide a “streamer” avatar through a hostile glitch maze
- Enemy fantasy: glitch swarm / corrupt stream entities
- Reward fantasy: collect reaction gems / reactions
- UI language: “Signal,” “Stream Down,” “Requeue,” “glitch swarm crashed your run”

This creates a humorous techno-chaotic wrapper around a compact survival maze game.

## Progression model
Progression is run-based rather than level-based:
- Restart creates a fresh random map.
- Health pressure escalates naturally through enemy contact and navigation mistakes.
- Gem count increases through continued survival and collection.
- No meta-progression, upgrades, stages, or unlock trees are visible in code.

## Confidence notes
High confidence:
- Single-file raycast survival maze structure
- Touch drag movement + tap interaction
- Health survival + gem collection loop
- Endless/run-based game-over restart loop

Moderate confidence:
- Intended player fantasy as “streamer navigating glitch swarm”
- The exact emotional tone as meme-chaotic satire rather than pure horror

Lower confidence:
- Whether the game should be classified more as a shooter or as a survival/action maze game, because attacks are not projectile-based
- Whether gems are intended as score only or as an implied resource, since they only affect displayed score in the current implementation