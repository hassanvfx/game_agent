# Blueprint

## High-level code structure
The game is implemented as a single self-contained `index.html` file with three main layers:

1. **HTML structure**
   - A full-screen `<canvas>` used for all in-game rendering.
   - HUD elements for score, wave/sector, hull, and charge.
   - A bottom upgrade dock that displays draggable tool cards.
   - Start and game-over overlay screens.
   - Audio elements for music and sound effects.
   - Decorative feedback GIF containers.

2. **CSS presentation**
   - A sci-fi neon UI with glass panels, scanlines, glowing bars, and responsive layout rules.
   - Mobile-first sizing, safe-area padding, and large touch-friendly cards/buttons.
   - Distinct visual styling for upgrade card families: repair, offense, utility, and metal/reinforce.

3. **JavaScript systems**
   - `AudioSys` manages unlock, BGM, pooled SFX playback, and a couple of synthesized impact sounds.
   - A single `DOMContentLoaded` bootstrap sets up canvas rendering, state, input, UI references, and the animation loop.
   - Core gameplay is handled through `resetGame()`, `loop()`, `update(dt)`, and `draw()` plus helper functions for spawning cards, drag/drop upgrades, particles, and barricade initialization.

## Game loop / state model
The game uses a classic browser animation loop with `requestAnimationFrame`.

### Main states
- `MENU`: start screen is visible, no gameplay running yet.
- `PLAYING`: update and draw execute continuously.
- `GAMEOVER`: draw still renders the scene, but active gameplay stops and the game-over overlay is shown.

### Per-frame flow
- `loop(timestamp)` computes delta time.
- If the game is in `PLAYING`, `update(dt)` runs:
  - turret aiming and autofire while pointer is held
  - enemy spawning
  - bullet movement and hit detection
  - enemy movement/attacks
  - barricade damage and breakage
  - scrap/charge accumulation
  - card spawning and buff timers
  - particle/casing/scrap effect updates
- `draw()` then renders:
  - background grid and space atmosphere
  - drop target hints during card dragging
  - barricade ring
  - particles, enemies, bullets, turret/core
  - low-health vignette feedback

## Player goals
The player is trying to keep the central beacon/core alive for as long as possible while clearing incoming drones. The immediate goals are:

- aim the central turret by touching/dragging
- destroy incoming enemies before they break through
- preserve or restore the circular outer defense panels
- build charge from kills
- spend that charge through upgrade cards at the right moment
- survive long enough to push into higher threat sectors/waves and increase score

## Interaction pattern
The interaction model is a hybrid of **touch aiming shooter** and **drag-and-drop tactical upgrade deployment**.

### Primary interaction
- Press/hold on the play area to aim the turret.
- While holding, the turret tracks the pointer and fires repeatedly.
- Releasing stops firing.

### Secondary interaction
- Destroyed enemies grant charge.
- Full charge prints a random card into the dock.
- The player drags cards from the dock into valid target zones:
  - **CENTER** cards target the core/turret area.
  - **PERIMETER** cards target the outer barricade ring.
- Incorrect placement fails and returns the card.

This creates a layered loop: real-time shooting pressure plus short tactical decisions about when and where to use limited upgrades.

## Core systems
### 1. Central turret / player core
- The player avatar is effectively a stationary central defense node.
- It has hull HP, aim angle, cooldown/heat, and temporary buffs.
- Rapid-fire modifies shot cadence and projectile color.

### 2. Enemy swarm pressure
- Enemies spawn outside the screen and move inward.
- Their health and speed scale with wave number.
- They can be stunned by an upgrade.
- If not blocked, they reach the center and damage the player core directly.

### 3. Perimeter barricade ring
- Six barricade segments form a circular outer shield.
- Enemies striking an active segment damage that segment instead of the core.
- Segments can be repaired or restored.
- A reinforce/alloy upgrade converts all segments into much stronger metal panels.

### 4. Projectile combat
- Bullets travel rapidly outward from the turret barrel.
- Hits deal fixed damage and remove bullets.
- Enemy kills create particles, score increases, and charge gain.

### 5. Charge / upgrade economy
- Each enemy kill grants charge.
- Reaching max charge generates a random upgrade card.
- Dock capacity is capped at three cards.
- If the dock is full when a card would spawn, the player instead gains bonus score.

### 6. Upgrade cards
There are four observed card types:
- **Field Patch**: repairs or restores barricade panels.
- **Overdrive**: temporary rapid-fire buff.
- **Ion Burst**: stuns and damages all enemies.
- **Alloy Skin**: upgrades all barricades into stronger metal panels.

### 7. Feedback / juice systems
- Music and layered SFX support action, impact, damage, pickup, start, and failure states.
- Temporary GIF overlays reinforce alert and danger moments.
- Particles, screen shake, muzzle flashes, casing ejections, health vignette, and glowing UI reinforce arcade intensity.

## Inferred genre / gameplay shape
Strongest inferred gameplay shape:
- **Wave defense game**
- with elements of **arena shooter / top-down survival defense**
- and a **drag-to-deploy card ability layer**

Although enemies are stored in a variable named `zombies`, the fiction and UI present them more like drones or swarm attackers in a sci-fi orbital-defense setting. The player does not move through space; instead, the experience is about holding a fixed position under escalating pressure.

## Gameplay heuristic
The intended play rhythm appears to be:

1. hold and sweep aim around the arena to intercept enemies early
2. use barricades as a damage buffer rather than letting enemies reach the core
3. prioritize continuous kills to fill charge quickly
4. bank or sequence cards based on pressure:
   - repair/reinforce when the perimeter is collapsing
   - overdrive when enemy density rises
   - ion burst as a panic reset tool
5. survive long enough to increase sectors/waves every 50 kills

This makes the game feel like a compact survival holdout: a stationary turret-defense survival loop with tactile drag-and-drop power cards and escalating enemy pressure.

## Confidence notes
Confidence is high on the core interaction loop because the game logic is explicit in the code. Confidence is moderate on thematic labeling because the code mixes terms like beacon, drones, barricades, and an internal `zombies` variable, suggesting the presentation was adapted from a survival/shooter template into a sci-fi last-stand wrapper.