# Blueprint

## High-level code structure
- Single-file browser game implemented entirely in `index.html`.
- Structure is split into:
  - HTML UI shell: start screen, HUD, game-over panel, feedback GIF elements, and canvas.
  - CSS presentation layer: neon sci-fi styling, responsive HUD/panels, mobile-safe layout.
  - Inline JavaScript gameplay layer:
    - `AudioController` for BGM and SFX playback
    - `Particle` for ambient background motion
    - `Explosion` for hit feedback
    - `Target` for spawned clickable threats
    - global state variables and game control functions (`initGame`, `spawnTarget`, `loseLife`, `updateHUD`, `handleInput`, `gameLoop`, `gameOver`)

## Game loop / state model
- The game uses a simple real-time animation loop driven by `requestAnimationFrame`.
- Main states:
  - **Idle / attract mode**: animated background particles render before play starts.
  - **Start screen**: overlay panel introduces the game and waits for player input.
  - **Active play**: targets spawn over time, move around the screen, expire on timers, and can be tapped/clicked for points.
  - **Game over**: triggered when lives reach zero; final score is shown and restart is available.
- Core runtime state is maintained through global variables:
  - `gameActive`
  - `score`
  - `lives`
  - `spawnTimer`
  - `spawnInterval`
  - `difficultyMultiplier`
  - arrays for `targets`, `particles`, `explosions`

## Player goals
- Protect the “grid” / shield lattice by clearing breach markers before they expire.
- Score as many points as possible before all shields are lost.
- Prioritize faster, smaller amber targets because they award more points and escalate intensity.

## Interaction pattern
- Primary interaction is direct pointer input:
  - mouse down on desktop
  - touch start on mobile
- Player taps/clicks targets on the canvas.
- Hitting a target:
  - removes it
  - grants points
  - creates an explosion effect
  - may trigger bonus audio for hard targets
  - slightly increases difficulty
- Missing a click/tap:
  - immediately costs one life
- Letting a target time out:
  - also costs one life

## Core systems
- **Spawn system**: periodic target spawning controlled by `spawnInterval`.
- **Difficulty scaling**:
  - successful hits increment `difficultyMultiplier`
  - spawn interval shrinks over time
  - hard-target chance rises with score (`score / 500`, capped at 0.5)
- **Life / failure system**:
  - three starting lives
  - lives are lost on misses and expired targets
  - low-life warning audio at one life remaining
- **Scoring system**:
  - normal cyan target: 10 points
  - hard amber target: 50 points
- **Feedback system**:
  - HUD score and heart lives
  - hit/fail reaction GIFs
  - particle explosions
  - danger flash on HUD
  - layered audio cues
- **Presentation system**:
  - neon grid backdrop
  - animated particles
  - glowing target rendering with lifetime ring indicators
  - sci-fi control panel UI

## Inferred genre / gameplay shape
- Arcade reflex game with strong overlap between:
  - **click/tap target shooter**
  - **wave / survival pressure loop**
  - **score attack arcade defense**
- It is not a tower defense in the strategic placement sense; rather, it thematically frames rapid target elimination as “defense.”
- The closest gameplay shape is a real-time reaction-based target-clearing survival score chase.

## Gameplay heuristic
- Survive by balancing accuracy and speed.
- Prioritize every visible target, especially smaller/faster amber ones.
- Avoid panic taps because misses are directly punished.
- As the board fills faster, the player’s skill expression comes from target acquisition, timing, and precision under pressure.

## Confidence notes
- Confidence is high on the core loop because the entire game logic is visible in a single file.
- Narrative framing is light and mostly cosmetic; “sentinel core” and “grid defense” are presentation wrappers around a tap-to-clear arcade loop.
