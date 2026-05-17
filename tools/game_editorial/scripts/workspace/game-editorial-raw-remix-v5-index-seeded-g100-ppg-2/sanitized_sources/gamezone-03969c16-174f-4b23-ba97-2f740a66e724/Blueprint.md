# Blueprint

## High-level code structure
- Single-file HTML game with embedded CSS and one ES module script.
- The page is split into three main presentation layers:
  - **Lobby screen** for callsign entry, role selection, and deployment.
  - **HUD/gameplay layer** with canvas rendering, health/time/resources, chat log, mobile controls, notifications, and contextual feedback GIFs.
  - **Death screen** for end-of-run summary and restart.
- Core logic lives in a few plain objects and arrays:
  - `CONFIG` defines team archetypes and resource node data.
  - `STATE` tracks runtime flags, camera, frame count, build mode, and relic unlock state.
  - `PLAYER` stores the local avatar's role, stats, survival timer, inventory, and score-adjacent values.
  - `entities`, `particles`, and `floatText` hold all world actors and transient visual effects.
- Rendering is done manually on a full-screen canvas, while the UI is regular DOM.

## Game loop / state model
- The game starts in a **menu/lobby state**.
- Pressing **Deploy**:
  - applies the selected role stats,
  - resets player values and world entities,
  - generates resources, bots, and a single relic/key,
  - reveals HUD controls,
  - begins background music,
  - enters the active loop.
- The active loop is `requestAnimationFrame(loop)` and each frame:
  - updates movement and jump physics,
  - advances the survival timer,
  - updates camera follow,
  - runs simple AI for bots,
  - updates particles and floating text,
  - refreshes HUD bars and counts,
  - draws the world and entities to canvas.
- The run ends if:
  - the player HP reaches zero from zombie/raider attacks, or
  - the survival timer reaches its max age.
- The game then enters a **death/result state** showing cause of death and survived cycles.
- The menu button acts like a soft return to lobby rather than a true pause menu.

## Player goals
- Survive for as long as possible until the run naturally ends or enemies overwhelm you.
- Move around the frontier, harvest trees and rocks, and avoid or defeat hostile raiders.
- Optionally build barricades and beacons if using a builder-capable role.
- Search the field for the hidden relic/key that unlocks the stronger **Warden/Hero** role for future runs.
- Endurance is the primary score expression; the final result is based on survival time.

## Interaction pattern
- Mobile-first twin-stick-lite interaction:
  - left virtual joystick for movement,
  - jump button,
  - single action button for attack / gather / bite / contextual build placement.
- Role selection changes the action fantasy:
  - settlers/rangers/warden gather and strike,
  - raider/brute roles fight without building,
  - scout drone flies and effectively spectates.
- Building is modal:
  - open build menu,
  - choose barricade or beacon,
  - next action places the chosen structure if resources are sufficient.
- Resource gathering and combat use the same short-range frontal hit arc.
- Feedback is intentionally arcade-like: floating numbers, HUD notices, short chat barks, hit/relic GIF overlays, and sound effects.

## Core systems
- **Role/class system:** multiple selectable archetypes with distinct HP, speed, damage, and scale.
- **Survival timer:** age/time fills continuously and acts as a run-length clock plus loss condition.
- **Resource harvesting:** trees grant wood, rocks grant stone, relic grants unlock state.
- **Unlock progression:** finding the relic permanently enables selection of the Warden during the current session.
- **Construction system:** barricades cost wood, beacons cost stone and create a visible aura.
- **Enemy/bot system:** simple wandering bots with zombie raiders capable of chasing and damaging the player.
- **Health/combat system:** contact damage from enemies and melee-style frontal attacks from the player.
- **Family/crew event:** a timed mid-run event spawns an allied child/crew bot for flavor and light progression.
- **Die-and-redeploy loop:** short self-contained sessions with restart from lobby.
- **Audio/atmosphere layer:** remote SFX/music and animated overlay media reinforce combat and relic moments.

## Inferred genre / gameplay shape
- Closest overall shape: a **top-down survival action game** with light **resource gathering** and **base-building** elements.
- The game feels like a compact browser survival sandbox rather than a level-based action title.
- It blends:
  - arcade survival,
  - simple melee combat,
  - harvesting/crafting-lite building,
  - role-based replayability,
  - and a small unlock chase centered on the relic/Warden.
- The presentation suggests a post-collapse frontier with zombies/raiders, but the mechanics are intentionally streamlined and accessible rather than simulation-heavy.

## Gameplay heuristic
- Start as a role that can gather efficiently.
- Sweep outward from spawn to find trees and rocks while avoiding prolonged contact with zombie raiders.
- Use harvested materials to place barricades or beacons for a defensive fantasy, though survival movement remains more important than fortification.
- Keep exploring for the relic because the Warden appears to be the premium power fantasy and likely the intended long-term reward.
- Treat the experience as a looping survival vignette: move, gather, strike, survive, unlock, redeploy.
- Confidence is moderate: the code clearly defines the systems above, though some systems are lighter in practice than the theme text implies.
