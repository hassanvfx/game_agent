# Blueprint

## High-level code structure
The game is implemented as a single self-contained `index.html` application with three major layers:

1. **Presentation layer**
   - Inline CSS defines a neon sci-fi HUD, modal overlays, and responsive/mobile-safe layout behavior.
   - The DOM contains a full-screen `<canvas>` for gameplay plus HTML overlays for the HUD, between-wave shop, game-over screen, feedback GIFs, and audio tags.

2. **Runtime/gameplay layer**
   - Inline JavaScript owns all gameplay logic.
   - Core runtime sections include:
     - boot/config parsing
     - state machine management
     - audio and haptics helpers
     - input handling
     - UI rendering/update helpers
     - shop/equipment logic
     - gameplay simulation
     - canvas rendering
     - animation frame loop

3. **Data-driven layer**
   - Weapon definitions are stored in a `WEAPONS` array.
   - Tweakable config is read from an embedded JSON script block (`basePlayerSpeed`, `themeColor`).
   - Runtime entities are grouped into arrays for bullets, enemies, particles, and floating text.

## Game loop / state model
The code uses a simple animation-frame loop and a small explicit state machine.

### States
- `INIT`
- `PLAYING`
- `SHOP`
- `GAMEOVER`

### Loop behavior
`gameLoop()` runs every frame:
1. compute delta time
2. call `update(dt)`
3. call `draw()`

### During `PLAYING`
`update(dt)` handles:
- drag-based player movement
- auto-firing toward the nearest enemy
- enemy spawning over time
- enemy pursuit and collision damage
- bullet movement and hit resolution
- kill rewards and wave completion
- particles, floating text, and camera shake

### State transitions
- **INIT → PLAYING** on first initialization
- **PLAYING → SHOP** when all enemies in the current wave are cleared
- **SHOP → PLAYING** when the player presses the next-wave button
- **PLAYING → GAMEOVER** when HP reaches zero
- **GAMEOVER → PLAYING** via full restart/reset

## Player goals
The player is trying to defend a central cybernetic “core” avatar against incoming hostile nodes/programs by:
- surviving each enemy wave
- earning credits from kills
- purchasing stronger weapons between waves
- equipping loadout upgrades
- clearing as many layers/waves as possible before dying

The immediate goal is survival and wave clear. The longer-term goal is score-like endurance progression measured by cleared layers and upgraded firepower.

## Interaction pattern
The interaction model is extremely streamlined and touch-first:

- **Movement:** pointer/touch drag moves the player relative to the drag origin
- **Combat:** fully automatic; the player continuously fires at the nearest enemy when available
- **Meta decision:** between waves, the player chooses whether to buy/equip weapons before deploying the next layer
- **Restart:** one-button reset after failure

This creates a one-thumb/mobile-friendly “move to survive while the game auto-attacks” loop.

## Core systems
### 1. Drag locomotion
The player does not steer with buttons or a joystick. Instead, pointer drag sets a target position, and the player glides toward it at configurable speed.

### 2. Auto-targeting and firing
The game continuously finds the nearest enemy and fires the equipped weapon when cooldown allows. Weapons vary by:
- damage
- fire rate
- projectile speed
- spread
- pellet count
- pierce
- color/audio identity

### 3. Wave escalation
Each wave increases:
- total enemies spawned
- enemy HP
- enemy speed pressure
- sustained survival demand

### 4. Enemy pressure
Enemies spawn from off-screen edges and move directly toward the player. Two broad enemy types are inferred:
- normal enemies
- fast enemies with higher movement speed and slightly higher reward value

### 5. Health and failure
Touching enemies reduces player HP in chunks. Low-health feedback includes red flash, fail reaction overlays, screen shake, and stronger haptic/audio feedback.

### 6. Reward economy
Enemy kills grant credits. Credits are spent in the shop to unlock stronger weapons. Purchased weapons remain owned through the current run and can be re-equipped for free.

### 7. Between-wave shop
After each cleared wave, the game pauses into a shop state. The player can:
- inspect weapon cards
- buy affordable weapons
- equip owned weapons
- proceed to the next wave

### 8. Juice/feedback layer
The game heavily reinforces actions with:
- procedural gunshot audio
- impact and defeat SFX
- looping BGM that changes by state
- floating reward text
- particles
- camera shake
- fail/success GIF callouts
- haptic vibration bridge calls

## Inferred genre / gameplay shape
Strongest interpretation: **survival-focused top-down arena shooter with auto-fire and between-wave weapon purchasing**.

Genre shape:
- arcade survival
- auto-shooter / survivor-lite
- wave defense
- score-chasing endurance game
- touch/mobile action game

It is not a traditional tower defense, because the player actively moves in real time. It is also not a pure twin-stick shooter, because aiming is automated. The closest gameplay heuristic is an **arena survival shooter with auto-aim and shop-based weapon progression**.

## Gameplay heuristic summary
A run consists of:
1. spawn into a neon cyber arena
2. drag to dodge incoming enemies
3. let the equipped weapon auto-fire at the nearest threat
4. collect credits through kills
5. survive until the wave is emptied
6. enter the patch bay shop
7. purchase or equip stronger weapons
8. deploy into the next harder layer
9. repeat until the core is breached

## Progression model
Progression is run-based and linear:
- wave count rises
- enemy durability and pressure increase
- player buying power grows through kill rewards
- weapon upgrades widen the player’s damage profile from starter pistol to SMG, rifle, shotgun, and sniper-like piercing weapon

There is no evidence of persistent meta-progression outside the current session.

## Presentation and theme
The theme is a cyberspace defense fantasy:
- title: **Firewall Breach**
- player avatar reads like a glowing core/process
- enemies resemble hostile intrusion nodes
- waves are framed as security layers
- weapons are named like hacking/patching tools
- UI language uses terms like **credits**, **layer**, **patch bay**, **deploy**, and **core breached**

The mood is:
- neon
- synthetic
- arcade-intense
- slightly defensive/paranoid
- polished but minimalist

## Confidence notes
Confidence is high on:
- wave-based survival structure
- auto-fire combat loop
- shop-driven weapon progression
- touch/drag primary interaction
- cyber-defense theme

Moderate uncertainty remains around whether the intended fantasy is “hacker avatar inside cyberspace” versus “abstract firewall defense drone,” but that does not materially change the gameplay reading.