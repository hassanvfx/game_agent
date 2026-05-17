# Blueprint

## High-level code structure
The game is implemented as a single self-contained HTML document with:
- inline CSS for layout, HUD styling, touch controls, and retro sci-fi presentation
- a single full-screen canvas for world rendering
- DOM overlays for HUD, dialogue, start screen, game-over/victory screen, and touch buttons
- a module script containing all runtime systems: input handling, world generation, entity simulation, combat, quest flow, audio, rendering, and UI updates

The codebase is functionally organized into these major areas:
1. **Core engine and state**: canvas setup, timing, resize handling, main loop flags
2. **Input system**: touch joystick on the left half of the screen, action buttons on the right, mouse fallback
3. **Game logic**: world grid, player model, enemy spawning, combat, skills, level progression, quest progression
4. **Rendering**: tile map drawing, entity sorting, sprite-like primitive rendering, particles, floating text, joystick visualization
5. **UI and dialogue**: HUD bar updates, NPC dialogue, quest text, modal screen control
6. **Audio and feedback media**: remote audio playback, GIF-based event feedback, BGM lifecycle
7. **System flow**: start, reset, victory, game over, animation loop

## Game loop / state model
The runtime uses a classic `requestAnimationFrame` loop:
- compute delta time
- update simulation if `isRunning`
- draw the world and overlays every frame
- request the next frame

### Core runtime states
The game implicitly moves through these layers of state:
- **Boot / title state**: start screen visible, gameplay inactive
- **Running gameplay state**: HUD active, world initialized, player can move and fight
- **Dialogue substate**: dialogue box appears when standing near the quest NPC while stationary
- **Quest progression state**:
  - `START`: meet the Dispatcher
  - `HUNT`: defeat 5 normal enemies ("globs")
  - `BOSS`: boss target appears
  - `WIN`: boss defeated and route secured
- **Fail state**: player HP reaches zero, game over modal shown
- **Victory state**: boss defeated, success modal shown

### Simulation model
The simulation updates:
- player movement and collision against terrain
- attack cooldown and skill cooldowns
- enemy pursuit and contact damage
- projectile travel and hit detection
- particle and floater lifetimes
- auto-spawning of enemies until the world population target is met
- interaction checks with the Dispatcher NPC
- HUD text and bars

## Player goals
The inferred player goal is:
1. report to the Dispatcher
2. clear the supply route by defeating 5 roaming hostile globs
3. survive enemy pressure while using attacks and rotating skills
4. defeat the raider chief / boss when it appears
5. secure the route and finish the shift

Secondary goals:
- avoid taking too much damage
- level up for stronger attacks and more health
- gather credits from kills
- manage cooldowns and choose the right active skill

## Interaction pattern
The game is built around direct real-time touch-friendly action:
- **left half of screen**: analog-style movement joystick
- **right side buttons**:
  - **TAG**: basic melee attack
  - **TOOL**: use currently selected special skill
  - **SWAP**: cycle between skills

The interaction loop is:
- move through a compact overworld arena
- close distance or reposition around enemies
- use short-range attacks repeatedly
- rotate between ranged shot, burst/dash utility, and heal
- return near the quest/NPC anchor for narrative framing at the start
- push through a simple kill-count objective into a boss finish

## Core systems
### 1. Procedural overworld
- 64x64 tile grid
- center spawn plaza made of stone
- water borders, random trees, decorative flowers
- collision tiles block pathing
- top-down camera follows the player

### 2. Player combat kit
- basic directional melee attack based on facing
- three swappable skills:
  - **SCAN**: forward projectile attack
  - **BURST**: temporary speed burst / dash-oriented mobility
  - **PATCH**: heal
- cooldown management displayed on HUD

### 3. Enemy pressure
- simple hostile mobs constantly spawn outside the player
- enemies chase when within a detection radius
- touching enemies deals continuous damage over time
- a stronger boss spawns after the hunt objective is completed

### 4. Progression
- enemies award XP and credits
- leveling increases survivability and attack output
- quest progression changes HUD objective text and culminates in a boss encounter

### 5. Feedback and juice
- floating combat text
- particles
- enemy flash on hit
- health bars over enemies
- HUD bars for health and cooldown
- victory/failure GIF overlays
- remote audio for attack, hits, UI, win/loss, and ambient loop

### 6. Narrative wrapper
- the Dispatcher NPC introduces the mission
- fiction reframes combat as frontier route-clearing and dispatch work
- win/loss text reinforces the convoy/supply-lane premise

## Inferred genre / gameplay shape
This game most strongly reads as a:
- **top-down action survival micro-RPG**
- **arena survival / wave defense lite**
- **mobile-friendly action game with light quest structure**

It blends:
- real-time dodging and melee/ranged combat
- constant enemy respawn pressure
- short-form progression through XP and rank
- a simple quest chain leading to a boss fight

## Gameplay heuristic
The intended way to play appears to be:
- begin by speaking to the Dispatcher
- keep moving to avoid contact damage from converging enemies
- use melee attacks for nearby targets
- rotate to **SCAN** when safer ranged damage is needed
- use **BURST** for evasive repositioning and kiting
- use **PATCH** reactively to recover during pressure
- farm the required five glob defeats efficiently without getting surrounded
- prepare for the marked chief encounter by entering it with health and cooldowns ready

## Confidence notes
Confidence is fairly high because the game logic, quest states, UI labels, and win/lose conditions are explicit in the code. Some thematic naming is more stylized than mechanically literal:
- skill name **SCAN** actually behaves like a projectile attack
- **BURST** is represented as a speed/dash effect rather than a discrete dash displacement
- the title and sci-fi UI imply a frontier courier setting, while the map structure is mechanically a simple top-down combat field