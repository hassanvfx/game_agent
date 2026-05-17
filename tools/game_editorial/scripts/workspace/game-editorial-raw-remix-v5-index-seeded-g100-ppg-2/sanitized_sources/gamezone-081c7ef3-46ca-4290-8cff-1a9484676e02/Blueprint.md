# Blueprint

## High-level code structure
The game is implemented as a single self-contained `index.html` file with three main layers:

1. **Presentation layer**
   - Inline CSS defines the entire visual language: neon sci-fi gradients, glassmorphism HUD cards, animated avatar halo, floating combat-text style feedback, reaction GIF overlays, and mobile-safe button layout.
   - The HTML structure contains three main screens/states:
     - start overlay
     - active gameplay HUD/stage
     - game-over overlay

2. **UI layer**
   - DOM references are collected into a `ui` object.
   - Visual updates are driven by `updateUI()`, `logEvent()`, `showReactionGif()`, and `spawnFloatingText()`.

3. **Game logic layer**
   - A compact mutable `state` object tracks the entire run.
   - Data tables (`CAREERS`, `EVENTS`) define progression and random yearly incidents.
   - Core flow functions include `resetGame()`, `advanceTurn()`, `checkCareer()`, `checkDeath()`, and `die()`.

4. **Audio layer**
   - Remote audio assets are loaded into a lightweight audio manager with BGM, SFX playback, unlock handling for browser autoplay restrictions, and a sound toggle.

## Game loop / state model
This is a **turn-based life-run loop** disguised with arcade pacing and presentation.

### Persistent state values
- `age`: increases by 1 every turn
- `money`: earned or spent through actions and random events
- `health`: passively declines and can recover slightly
- `happiness` / morale: fluctuates based on work/rest/social pressure
- `smarts`: the skill/education stat used for career advancement
- `careerIndex`: current job tier
- `alive`: whether the run is ongoing

### Turn loop
Each player action triggers a full yearly turn:

1. Player selects one of four actions.
2. Baseline annual wear occurs:
   - happiness -2
   - health -1
3. The chosen action applies its own stat changes.
4. Career promotion may trigger if skill thresholds are met.
5. A random life event may occur with ~30% chance.
6. Age increments by one year.
7. Stats are clamped and warning feedback may fire.
8. UI refreshes.
9. Death/end-of-run conditions are checked.

### End conditions
The run ends when:
- **health reaches 0**: burnout/exhaustion death state
- **age reaches 100**: successful full-life completion

Notably, low happiness is dangerous but not directly fatal; it functions as a pressure stat that increases warning state and contributes to poor outcomes.

## Player goals
The player appears to be trying to:
- survive as long as possible
- avoid burnout
- build money
- improve smarts/skills
- climb through career tiers
- finish a satisfying century-long life run, or at least reach a high-status role before collapse

There is no map or level progression; the score fantasy is an optimized life trajectory.

## Interaction pattern
The interaction model is very simple and mobile-friendly:

- Tap **Shift** to earn money, but lose morale/health
- Tap **Train** to raise skills, but spend money
- Tap **Recover** to restore morale and some health
- Tap **Network** to raise morale, but spend money

This creates a repeated balancing act:
- work funds study and social activity
- study unlocks promotions and stronger work income
- recovery prevents health collapse
- networking helps morale stay viable

The game is therefore a **single-screen choice loop** with immediate audiovisual feedback and no direct movement or spatial navigation.

## Core systems

### 1. Resource balancing
The fundamental system is a triad of competing meters:
- health
- happiness/morale
- money

Smarts functions as a progression stat rather than a survival meter.

### 2. Career progression
Career advancement is gated by smarts thresholds:
- Between Gigs
- Stock Clerk
- Front Desk Rep
- Team Lead
- Systems Specialist
- Clinic Director
- Executive Chief

Promotion is not guaranteed on threshold hit; it is probabilistic, which adds uncertainty and a “keep pushing” cadence.

### 3. Random event injection
Random events add volatility:
- bonuses
- fees
- health setbacks
- morale boosts
- audit/commute setbacks
- minor educational boosts

This stops the game from being a pure deterministic optimizer.

### 4. Attrition and burnout pressure
Every turn naturally drains the player a little. Work drains more. This gives the game a survival flavor even though it is fundamentally a life/career management loop.

### 5. Feedback spectacle
Although mechanically simple, the game frames every action with:
- floating text popups
- warning sounds
- positive/negative reaction GIFs
- animated avatar changes by age/condition
- start and game-over overlays

This gives it an arcade “run” identity instead of a spreadsheet simulation tone.

## Inferred genre / gameplay shape
Best abstracted as:

- **arcade life simulator**
- **turn-based resource management game**
- **light career progression sim**
- **single-screen survival-management loop**

It borrows the emotional cadence of clicker/idle stat-balancing games, but interaction is active and discrete rather than passive. The strongest gameplay identity is a **life choices / roleplay-adjacent stat survival game** with very compressed yearly turns.

## Heuristic summary
“Life Sprint” is a compact mobile-first life-management game where each tap advances a full year. The player continuously trades off work, learning, rest, and socializing to keep health and morale afloat long enough to earn money, get promoted, and survive a full simulated lifespan. The codebase is small, single-file, and driven by straightforward state mutation plus polished HUD/audio feedback.