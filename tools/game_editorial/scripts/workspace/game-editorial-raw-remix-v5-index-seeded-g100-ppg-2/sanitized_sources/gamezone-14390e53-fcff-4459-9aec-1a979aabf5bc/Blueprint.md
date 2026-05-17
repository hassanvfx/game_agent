# Blueprint

## High-level code structure
This game is implemented as a single self-contained `index.html` file with three major layers:

1. **Presentation layer**
   - Inline CSS defines the full visual identity: neon sci-fi gradients, glass HUD panels, mobile touch controls, overlay menus, relic index grid, rarity text styles, and feedback GIF positioning.
   - HTML contains the canvas, HUD, start/index/game-over overlays, audio elements, and touch controls.

2. **Game data and systems**
   - `SaveSystem` persists discovered weapon/relic IDs to `localStorage`.
   - Weapon content is generated from:
     - a `RARITIES` table
     - an `ARCHETYPES` table
     - rarity-specific name prefixes
   - `initWeaponDB()` combines those sources into a 60-item collectible database.

3. **Runtime/gameplay layer**
   - Global state tracks `gameState`, `score`, `camera`, entities, particles, visual effects, and current touch input.
   - Core classes:
     - `Entity` base class for movement, friction, bounds, shadowing
     - `Player` for movement, holding/throwing/grabbing, melee combat, damage
     - `Enemy` for pursuit and contact damage
     - `Weapon` for idle, held, and thrown behavior
     - `VisualEffect` for transient attack arcs
   - A `loop()` function updates simulation state and renders the world every animation frame.

## Game loop / state model
The game uses a simple top-level state machine:

- `MENU`
  - Start screen with title and buttons
  - Access to the relic archive/index
- `PLAYING`
  - Real-time movement and combat
  - Weapons spawn in the arena
  - Enemies continuously spawn faster as score increases
  - Score rises by defeating enemies
  - HP decreases from enemy contact
- `GAMEOVER`
  - Triggered when player HP reaches zero
  - Final score shown
  - Restart or return to menu

The per-frame loop does the following during `PLAYING`:
1. Update contextual button label (`CLAIM` vs `CAST`)
2. Spawn enemies over time, with spawn interval scaling by score
3. Maintain a minimum ambient number of dropped weapons
4. Update player, enemies, weapons, particles, and attack effects
5. Remove dead enemies and expired effects
6. Smoothly follow the player with a camera and small shake effects
7. Render the arena, collectibles, enemies, player, particles, and attack arcs

## Player goals
The player has two overlapping goals:

1. **Immediate survival/combat goal**
   - Stay alive in an enclosed arena while enemies swarm inward.
   - Fight using default melee or stronger found weapons.
   - Manage spacing because enemies damage the player on touch.

2. **Collection/meta goal**
   - Pick up and discover as many unique relic/weapons as possible.
   - Unlock entries in the persistent archive/index.
   - Chase rarer items with stronger stats and more dramatic throw properties.

The score system rewards defeating enemies, while the archive system rewards exploration and pickup variety.

## Interaction pattern
The interaction model is twin-stick-adjacent but simplified for touch:

- **Left thumb / joystick zone:** movement direction
- **Right action buttons:**
  - `STRIKE` = melee attack in facing direction
  - `CLAIM` = pick up nearby weapon if empty-handed
  - `CAST` = throw held weapon if already carrying one

Interaction rhythm:
1. Move through the arena
2. Spot a dropped relic
3. Claim it to gain new melee stats and possibly unlock archive progress
4. Use `STRIKE` for close-range arc attacks
5. Use `CAST` to throw the weapon, with different trajectories depending on archetype
6. Recover another relic and continue surviving against the swarm

## Core systems
### 1. Arena survival
- Large bounded square world (`WORLD_SIZE = 2500`)
- Enemy spawn points try to avoid appearing too close to the player
- Spawn pressure increases with score

### 2. Weapon collection and rarity system
- 10 weapon archetypes × 6 rarities = 60 collectible relics
- Each rarity modifies damage/knockback via a multiplier
- Heavy weapons reduce movement speed
- Throw behavior varies by weapon type:
  - normal throw
  - straight piercing throw
  - boomerang return

### 3. Close-range combat
- Melee attacks use an arc/cone hit check
- Range, cooldown, damage, and knockback depend on held weapon
- Unarmed attacks still function, but weaker

### 4. Throwable weapon combat
- Held weapons can be thrown
- Straight throws can pass through multiple enemies
- Boomerang battleaxe returns to the player
- Normal throws hit and often drop back to idle

### 5. Persistent collection index
- First-time pickups are saved to `localStorage`
- Archive screen reveals unlocked relic names and keeps unknown ones hidden
- This creates light long-term progression across runs

### 6. Feedback/audio juice
- Web Audio buffers for BGM, hit, pickup, fail, menu, damage, and game-over sounds
- Toast popups announce new relics and rarities
- GIF overlays reinforce pickups and combat impacts
- Camera shake, glow, particles, and rarity text styling enhance responsiveness

## Inferred genre / gameplay shape
The strongest inferred gameplay shape is:

- **Arcade arena survival action game**
- with **melee-and-throw combat**
- plus **light collection/meta-progression**
- and **mobile-first touch controls**

It is not a level-based progression game or a narrative game. It plays like a compact score-chasing survival brawler where weapon discovery and archive completion provide the longer-term hook.

## Gameplay heuristic
A likely intended player heuristic is:

- Keep moving to avoid contact damage.
- Grab stronger relics whenever safe, especially rare/heavy ones.
- Use melee when enemies cluster near your facing arc.
- Throw straight or boomerang weapons to control crowds or hit safely at range.
- Accept short risk windows to claim new relics because archive unlocks persist.
- Optimize for both survival score and collection completion over repeated runs.

## Confidence notes
Confidence is fairly high because the full gameplay logic, UI states, controls, scoring, spawning, archive persistence, and weapon behavior are directly visible in source. Lower-confidence areas are only thematic interpretation details, since the presentation says “mythical archive” while the mechanics are abstract neon arena combat rather than lore-heavy worldbuilding.