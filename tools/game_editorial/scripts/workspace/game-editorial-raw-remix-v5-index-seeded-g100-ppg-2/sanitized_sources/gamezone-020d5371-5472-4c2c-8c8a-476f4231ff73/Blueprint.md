# Blueprint

## High-level code structure
The game is implemented as a single self-contained `index.html` document with three major layers:

1. **Presentation layer**
   - Extensive inline CSS defines a neon sci-fi visual identity, responsive HUD, overlay menus, and animated interface effects.
   - HTML contains the canvas playfield, HUD, start screen, pause menu, level-up menu, cheat/admin menu, game-over screen, and audio elements.

2. **Asset/audio layer**
   - Remote audio files are declared as `<audio>` elements for background music and sound effects.
   - Animated reaction GIF overlays are used for hit/damage feedback.
   - Fonts are loaded remotely for a futuristic interface look.

3. **Game logic layer**
   - Inline JavaScript defines configuration, upgrades, audio management, game entities, UI wiring, state transitions, the main loop, and rendering.
   - The game uses a custom lightweight canvas engine rather than a framework.

## Game loop / state model
The runtime state is centered around a mutable `state` object plus entity arrays:

- `state.active`: whether a run is in progress
- `state.paused`: whether gameplay simulation is paused
- `state.score`: score/data total
- `state.width`, `state.height`: viewport/canvas size
- `state.shake`: camera shake intensity
- `state.godMode`: cheat toggle

Other mutable collections:
- `player`
- `enemies`
- `bullets`
- `items` (XP pickups)
- `particles`
- `texts`

### Main loop flow
`requestAnimationFrame(gameLoop)` drives the game. Each frame:

1. compute delta time
2. if not paused:
   - probabilistically spawn enemies based on player level
   - update player movement and pickup collection
   - update enemies and enemy bullets
   - update magnetized XP items
   - update particles and floating combat text
3. clear and redraw the full canvas scene
4. render pickups, bullets, player, enemies, particles, and floating text
5. schedule the next frame

### State transitions
- **Start screen -> active run** via Deploy button
- **Active run -> paused** via pause button or level-up screen
- **Paused -> active run** via resume or upgrade selection
- **Active run -> game over** when HP reaches zero
- **Paused/active -> start screen** via quit/exit run
- **Active run -> cheat overlay** via DEV button

## Player goals
The immediate and repeated player goal is to survive while dragging the ship/avatar around the arena so its orbiting blade automatically destroys incoming enemies.

Longer-term goals:
- collect dropped XP/data shards
- trigger level-ups
- choose stronger upgrades
- increase survivability, blade range, damage, and movement/spin performance
- push for a higher score and higher tier before being overwhelmed

## Interaction pattern
The interaction model is touch-first and drag-based:

- press/drag on the canvas to move the player
- no attack button is required
- offense is automatic through the rotating orbital blade
- menu interaction is button-driven
- pause, restart, quit, and cheat actions are direct UI taps/clicks

This creates a **survivor-lite auto-attack dodge loop** where the player focuses on positioning rather than manual firing.

## Core systems
### 1. Drag locomotion
The player continuously moves toward the current pointer position with clamped arena bounds and speed influenced by upgrades.

### 2. Orbiting melee weapon
The player has a rotating blade/beam:
- fixed radial distance from the player
- continuous angular motion
- damages enemies on proximity with the blade tip/orbit zone
- can be upgraded for damage, range, and orbit speed

### 3. Enemy pressure
Enemies spawn from screen edges and move toward the player.
- Type 0: direct chaser
- Type 1: slower ranged unit that periodically shoots bullets

### 4. Damage and failure
Player damage comes from:
- enemies colliding with the player
- enemy bullets hitting the player

When health reaches zero, the run ends and final score/tier are shown.

### 5. XP and progression
Defeated enemies drop collectible items worth XP/data.
- pickups are magnetized when near the player
- collecting XP increases score
- filling the XP bar pauses the game for a level-up choice
- each level increases XP threshold and player level counter

### 6. Upgrade drafting
At each level-up, the player receives 3 random upgrade options drawn from a fixed upgrade table:
- damage increase
- blade reach increase
- movement speed increase
- orbit speed increase
- max HP increase with full heal

### 7. Juice/feedback systems
The game emphasizes arcade feedback via:
- camera shake
- particle bursts
- floating damage/heal/status text
- hit/fail GIF callouts
- layered sound effects and battle music
- glowing HUD and animated typography

### 8. Meta/admin tools
A visible DEV/admin menu exposes cheats:
- force level up
- full heal
- nuke enemies
- god mode

This suggests the build may be intended for quick tuning, showcase, or casual sandbox use.

## Inferred genre / gameplay shape
Strongest inference: **arena survival action game with survivor-lite and auto-attack melee mechanics**.

More specifically, it plays like:
- a compact top-down survival arena game
- a dodge-and-position experience
- an auto-offense action loop where the rotating blade is the main weapon
- a score-chasing endless run with intermittent upgrade drafts

## Gameplay heuristic
A likely optimal play pattern is:

1. keep moving in arcs rather than straight lines
2. let the orbital blade sweep enemy approach lanes
3. prioritize safe pickup collection to keep leveling
4. choose upgrades that improve blade reach/damage early
5. use movement speed to maintain spacing from bullet enemies
6. survive long enough for scaling pressure to convert the match into a score run

## Presentation and tone
The game presents itself as a stylish neon cyber/void combat scenario:
- title: **Void Slayer: Protocol Omega**
- tone: arcade, futuristic, energetic, slightly dramatic
- mood: high-contrast, glowing, intense but accessible
- visual shorthand: holographic HUD, synthwave/cyber UI, compact sci-fi pilot avatar, enemy drones

## Confidence notes
High confidence:
- drag movement
- automatic orbiting blade combat
- survival/arena structure
- level-up drafting
- endless score-chasing progression

Moderate confidence:
- intended genre label as survivor-lite rather than pure action arcade
- exact target audience beyond general mobile/casual action players

Low uncertainty areas:
- there is no evidence of discrete stages, bosses, or win condition; the code suggests an endless run until death.