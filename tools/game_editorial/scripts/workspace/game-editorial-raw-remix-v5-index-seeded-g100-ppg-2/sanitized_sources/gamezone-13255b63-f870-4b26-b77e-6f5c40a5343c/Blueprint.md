# Blueprint

## High-level code structure
- **Single-file HTML game:** The entire game is implemented in `index.html` with inline CSS, HTML UI, audio tags, a config blob, and all gameplay JavaScript in one script block.
- **Rendering split:** DOM is used for menus, HUD, feedback GIF overlays, and audio elements, while the actual gameplay is drawn on an HTML5 `<canvas>`.
- **Config layer:** A JSON config block (`#game-config`) exposes tweakable values for courier handling speed, player color, and obstacle color.
- **Entity model:** The runtime is organized around lightweight classes for `Player`, `Enemy`, `Particle`, and `RoadMark`.
- **Systems:** Major systems include audio unlock/playback, state management, pointer input routing, procedural spawning, collision detection, score/rush progression, resize handling, and the animation loop.

## Game loop / state model
- **States:** `INIT`, `PLAYING`, and `GAMEOVER`.
- **Boot flow:** On `DOMContentLoaded`, the game parses config, initializes audio, binds pointer/restart events, observes canvas size, and starts the `requestAnimationFrame` loop.
- **Initialization:** `initGame()` resets score, speed multiplier, timers, entity arrays, spawns initial road marks, creates the player, updates the HUD, and enters `PLAYING`.
- **Per-frame loop:**
  1. Clamp delta time.
  2. Update scrolling road marks and particles regardless of state.
  3. If playing, increase survival time and rush multiplier.
  4. Add passive score over time.
  5. Move the player toward the current pointer x-position.
  6. Spawn falling obstacles on a timer that accelerates as rush increases.
  7. Move enemies downward and clean up off-screen entities.
  8. Check for pass-by scoring and collisions.
  9. Draw backdrop, road, entities, particles, and screen shake.
- **Failure:** On collision, the player explodes into particles, crash effects trigger, the player is removed, and the game switches to `GAMEOVER`.
- **Restart:** The restart button reinitializes the whole run.

## Player goals
- Survive as long as possible on a narrowing road.
- Dodge descending road barriers/cones.
- Build score by both staying alive and letting hazards pass safely.
- Push into higher-speed “rush” play, where the game becomes faster and denser.

## Interaction pattern
- **Primary input:** Pointer/touch drag on the canvas.
- The courier vehicle does not snap instantly; it eases toward the pointer horizontally, creating a slippery lane-weaving feel.
- There is no shooting, jumping, braking, or menu complexity during play.
- The only post-failure interaction is pressing the restart button.

## Core systems
- **Endless avoidance driving:** Obstacles spawn from the top and travel downward toward the player.
- **Score model:** Score rises continuously over time and also jumps when an obstacle is successfully passed.
- **Difficulty ramp:** `speedMultiplier` scales with survival time up to a capped increase, affecting obstacle speed, road mark speed, spawn pacing, and scoring.
- **Collision model:** Simple axis-aligned overlap tuned smaller than visual sizes for slightly forgiving hits.
- **Feedback system:** Success and failure GIF overlays plus short captions reinforce positive streaks and crashes.
- **Audio system:** Background loop, collect/rush/crash/restart sounds, plus oscillator fallback if media playback is unavailable.
- **Haptics:** Light vibration on successful passes and heavy vibration on crash when the host bridge exists.
- **Responsive layout:** Canvas resizes with `ResizeObserver`, HUD is mobile-conscious, and the viewport is locked for full-screen handheld play.

## Inferred genre / gameplay shape
- **Strongest genre read:** endless runner / lane-dodging avoidance game with arcade driving flavor.
- **Secondary read:** lightweight casual survival score-chaser framed as a newspaper/paper-delivery courier run.
- **Session shape:** short runs, immediate restart loop, escalating intensity, simple one-touch controls, leaderboard-style self-improvement energy even without a formal leaderboard.

## Presentation and theme
- Bright cartoon city delivery aesthetic.
- The player is a stylized courier car with an envelope emblem.
- Obstacles are traffic-cone-like road barriers.
- UI language (“Paper Courier,” “Route Live,” “Route Blocked,” “Dispatch Again”) frames the run as a hectic delivery route.
- Mood is playful, punchy, mobile-friendly, and arcade-like rather than realistic.

## Gameplay heuristic
The game is best understood as a **single-screen vertical dodge run**: the road scrolls toward the player, hazards descend faster over time, and the player continuously makes small left-right corrections to thread through openings. Success is not reaching a destination but maintaining control under increasing speed pressure. The design rewards steady survival, near-miss rhythm, and quick restarts after failure.