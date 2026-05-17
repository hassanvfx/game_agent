# Blueprint

## High-level code structure
The game is implemented as a single self-contained `index.html` file with three main layers:

1. **HTML UI shell**
   - Fullscreen `canvas` for rendering the world and combat
   - DOM-based HUD for player HP, boss HP, touch controls, start screen, fail screen, and victory screen
   - Two feedback GIF overlays for impact and victory reactions

2. **CSS presentation layer**
   - Neon sci-fi visual language with dark glassmorphism panels
   - Mobile-first fullscreen layout
   - Virtual joystick and large touch-friendly combat buttons
   - Responsive sizing for controls and screen cards

3. **JavaScript game runtime**
   - Asset constants for remote audio
   - `AudioController` for BGM and SFX playback
   - Global state objects for player, boss, NPCs, projectiles, particles, and environment props
   - Update functions for player logic, boss AI, projectiles, particles, summoning fountain, and rendering
   - A `requestAnimationFrame` loop that advances gameplay outside menu/end states

## Game loop / state model
The code explicitly uses a small state machine:

- `MENU` — intro overlay and instructions
- `ROAM` — free movement in a sparse arena/city district with ambient civilians
- `SUMMONING` — breach ritual phase after pressing the summon button
- `BOSS` — one-on-one combat against the Black Knight
- `WIN` — victory overlay after boss HP reaches zero
- `OVER` — defeat overlay after player HP reaches zero

Core loop flow:

1. Start on menu
2. Enter roaming arena
3. Move with the virtual joystick
4. Press **Breach** to summon the boss
5. Survive and damage the boss through melee timing
6. Use parry to counter the boss’s slash or projectile
7. Win by reducing boss HP to zero or lose when player HP is depleted
8. Restart resets back to roaming state

The game loop updates:
- player movement and timers
- projectiles
- particles and temporary effects
- roaming NPC drift or boss behavior depending on state
- then renders the whole scene every frame

## Player goals
Primary player goal:
- Defeat and contain the **Black Knight**

Sub-goals:
- Survive long enough to learn the boss pattern
- Stay in range for melee damage
- Time parries correctly to negate hits and stun the boss
- Capitalize on stun windows for safe attacks

## Interaction pattern
The interaction model is touch-first, arcade-style, and real-time:

- **Left side:** virtual joystick for movement
- **Right side:** attack button
- **Right side, after summoning:** parry button replaces/augments the summon flow
- **Start / retry / run again:** standard UI buttons

Moment-to-moment interaction rhythm:
- reposition
- bait boss behavior
- react to telegraphed attack
- parry or avoid damage
- punish with short-range strikes
- repeat until victory or defeat

## Core systems
### 1. Movement and camera
- The player moves on a large scrolling map
- Camera follows the player by centering on them
- Building rectangles act as simple collision blockers

### 2. Arena/world generation
- Procedurally scattered building blocks create a sparse district
- Ambient NPC dots wander during the roam phase
- World exists mostly as a staging ground before the boss encounter

### 3. Summoning / phase transition
- The “Breach” action transitions the game from wandering to boss combat
- A dark fountain/portal visual appears
- Civilians are cleared
- Audio shifts from roaming ambience to boss combat music
- Parry is enabled for the fight

### 4. Combat
- **Attack:** short-range melee burst with a timed swing
- **Parry:** temporary defensive window with cooldown
- **Damage model:** fixed-ish player and boss damage values with floating numbers
- **Hit feedback:** particles, shake, GIF flashes, HUD updates

### 5. Boss AI
The boss uses a simple finite behavior model:
- `CHASE` — pursue player
- `SLASH` — close-range melee attack with windup and hit frame
- `STAR` — ranged projectile throw when far away
- `STUNNED` — vulnerable state caused by successful parry

This makes the encounter feel like a pattern-learning boss duel rather than freeform enemy swarms.

### 6. Audio feedback
- Separate roaming and boss music loops
- Distinct SFX for attack, enemy hit, parry, hurt, summon, projectile, fail, victory, and UI actions
- Audio is unlocked on first user interaction

### 7. Juice / presentation feedback
- Screen shake
- Particles
- Floating damage text
- Animated impact/victory GIF callouts
- Boss HP bar and stylized action buttons

## Inferred genre / gameplay shape
Best abstracted gameplay shape:
- **mobile action boss duel**
- **top-down arena combat**
- **single-boss pattern-reading encounter**
- **light action game with parry timing**

It borrows from:
- top-down action games
- boss rush encounter design
- simple arena survival pressure
- telegraph-and-counter combat loops

## Gameplay heuristic
What the player is expected to learn:
- Roaming is only a setup phase; the true game is the boss fight
- Aggression without timing is punished
- Parry is the key mastery mechanic
- Optimal play means staying close enough to punish, but alert enough to counter slash or projectile timing
- The fight rewards recognition of spacing:
  - close range invites slash
  - far range invites projectile
  - correct parry creates the safest damage window

## Difficulty and progression shape
Progression is encounter-based rather than level-based:
- brief onboarding via instruction screen
- immediate free movement tutorial space
- one deliberate summoning trigger
- one escalating boss encounter
- hard fail or full victory reset

There is no long-form meta progression, inventory, or stage sequence. The progression is a single contained run with skill improvement coming from player mastery.

## Confidence notes
High confidence:
- Single-file HTML/canvas game
- Touch-first controls
- Boss-centered combat loop
- Parry-stun-punish as signature mechanic
- Top-down arena presentation

Moderate confidence:
- Thematically framed as “containment” rather than literal fantasy knight duel
- Intended audience includes mobile arcade action players

Low confidence:
- Any broader narrative beyond the containment framing
- Whether roaming was intended to be expanded into a larger game mode