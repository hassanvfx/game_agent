# Blueprint

## High-level code structure
This game is a single-file HTML application with three major layers embedded in `index.html`:

1. **Presentation layer**
   - Inline CSS defines the retro-futuristic HUD, glass panels, responsive layout, scanlines, glitch effects, day/night variants, and feedback overlays.
   - DOM UI includes score, district/weather labels, energy meter, weapon buttons, time controls, mode toggles, rebuild toggle, battery/energy-rule toggle, reaction GIFs, feedback banner, and a game-over modal.

2. **Simulation/render layer**
   - A full-screen `<canvas>` renders the city, roads, river tiles, buildings, vehicles, particles, weather, lightning, smoke, projectiles, and destruction effects.
   - Rendering is handled manually with 2D canvas drawing, not a framework.

3. **Game logic/audio/input layer**
   - JavaScript maintains global state and entity arrays.
   - Audio is split between looping HTML audio tracks for BGM and Web Audio decoded buffers for sound effects.
   - Pointer input on the canvas deploys the currently selected cleanup/attack tool.
   - A resize observer initializes the simulation and keeps the canvas sized to the viewport.

## Game loop / state model
The game uses a standard real-time loop driven by `requestAnimationFrame`:

- `gameLoop(now)`
  - computes delta time
  - applies time scaling (`0.5x`, `1x`, `2x`)
  - repeatedly calls `updateGame(step)` with capped substeps
  - calls `drawGame()`

### Core state
Global state includes:

- `gameState`: primarily `PLAYING` and `GAMEOVER`
- `score`
- `energy`
- `infiniteEnergy`
- `currentWeapon`
- `isNight`
- `timeScale`
- `currentWeather`
- `currentLayout`
- arrays for `buildings`, `traffic`, `activeEffects`, `particles`, `smoke`, `texts`, `weatherParticles`, and `lightnings`

### Session flow
- On first resize, the game initializes audio and starts play.
- `regenerateCity()` randomizes city layout and weather, repopulates buildings and traffic, and clears effects.
- During play, the player taps/clicks anywhere on the field to deploy a tool if enough energy is available.
- The score rises by destroying buildings and traffic units.
- A game-over UI exists, but in the current code there is no observed loss timer or defeat condition wired into the update loop; the game appears closer to an open-ended sandbox score run with a restart overlay path available.

## Player goals
The inferred player goal is:

- **Cause maximum large-scale city destruction / cleanup output by deploying orbital tools efficiently**
- Build score by hitting clusters of buildings and vehicles
- Exploit system interactions such as weather/layout synergies and weapon combinations
- Manage energy unless sandbox mode (`Limits: OFF`) is enabled
- Rebuild the city to generate a new district/weather combination and continue scoring

Although the UI frames the fantasy as “cleanup command,” the actual mechanics are destructive spectacle: orbital strikes, void singularities, meteor storms, lasers, and summoned bots flatten the city.

## Interaction pattern
Primary interaction model:

- **Pointer/tap targeting**
  - select one of six tools in the HUD
  - tap/click the playfield to deploy that tool at a location

Secondary interactions:

- switch day/night presentation
- cycle simulation speed
- rebuild/regenerate the city
- toggle energy limits on/off
- show/hide HUD

This makes the game feel like an arcade destruction sandbox with direct-target touch controls.

## Core systems

### 1. City generation system
`regenerateCity()` picks:
- one of several layouts: `GRID`, `RIVER`, `SECTOR`, `PARK`, `SPRAWL`
- one weather type: `CLEAR`, `RAIN`, `ACID_RAIN`, `SNOW`, `STORM`

It then:
- computes roads
- optionally computes river cells
- excludes roads/river/park areas from building placement
- spawns many buildings
- seeds weather particles
- spawns moving traffic

### 2. Energy economy
Each tool has a cost:
- KINETIC: 15
- CLUSTER: 35
- LASER: 50
- VOID: 80
- METEOR: 90
- MONSTER: 100

Energy regenerates continuously according to configurable `regenSpeed`, unless infinite energy is toggled on. Weapon buttons disable when insufficient energy is available.

### 3. Destruction and scoring
`dealDamage()` checks buildings and traffic within a radius:
- buildings lose health and can be destroyed
- destroyed buildings spawn debris and increase score
- destroyed traffic adds score
- floating score text appears for hits

This is the main scoring loop.

### 4. Weapon/effect system
Tools are implemented as separate classes in `activeEffects`:

- **KineticRod**: fast vertical strike with explosion radius
- **ClusterBomb**: delayed multi-burst bombardment with possible fire ignition
- **LaserBeam**: sustained beam, can trigger chain lightning in rain/storm and steam over river layouts
- **VoidHole**: pulls in traffic and other projectiles, grows stronger when fed
- **MeteorShower / Meteor**: repeated heavy impacts over an area
- **Kaiju** (`MONSTER` / “BOT”): summoned roaming entity that stomps and damages structures, can be enraged by lasers

### 5. Emergent interaction system
The code intentionally supports combo behavior:
- laser + rain/storm = chain lightning / “GRID SURGE”
- laser + river = steam cover
- void + cluster/meteor = projectile consumption / “VACUUM BOOST”
- laser near summoned bot = enraged bot / “BOT OVERDRIVE”
- weather suppresses or enables fire spread
- rain/storm/snow reduce fire intensity

This is one of the game’s most defining systems.

### 6. Ambient simulation
The city feels alive through:
- traffic spawning and movement
- weather particles
- smoke and fire spread
- lightning flashes
- screen shake, particles, floating text
- day/night palette swap
- alternating BGM

### 7. UX feedback system
The game continuously reinforces actions using:
- banners
- combo text
- animated GIF reactions
- haptics/vibration
- sound effects
- glow/glass UI and glitch transitions

## Inferred genre / gameplay shape
Strongest inferred shape:

- **Arcade destruction sandbox**
- **Pointer-driven city attack simulator**
- **Light resource-management spectacle game**

It is not a survival or defense game in practice; the player is the destructive force. The closest overall shape is an action sandbox where the fun comes from chaining high-impact tools across a procedurally varied miniature city.

## Gameplay heuristic
A likely optimal play heuristic from the code:

1. Watch the current district layout and weather.
2. Choose a tool based on energy and synergy:
   - use **PULSE/KINETIC** for cheap precision hits
   - use **BURST/CLUSTER** for clustered districts and fire setup
   - use **BEAM/LASER** during rain or storm for chain-lightning combos
   - use **VACUUM/VOID** when many cars/projectiles are nearby
   - use **STORM/METEOR** for dense areas and large score bursts
   - use **BOT/MONSTER** for long-lived area damage, especially if laser enraged
3. Spend energy in bursts, then let regeneration refill.
4. Use rebuild to refresh layouts and continue the score chase.
5. Use sandbox mode if the intended play goal is spectacle rather than pacing.

## Presentation and tone
The code communicates:
- a neon sci-fi command-center tone
- orbital strike / future warfare imagery
- playful “cleanup command” framing over clearly destructive mechanics
- strong arcade feedback and toy-like experimentation

Overall, this appears to be a **sci-fi city destruction click/tap sandbox with energy-limited superweapons, procedural district variations, and combo-driven environmental interactions**.