# Blueprint

## High-level code structure
The game is implemented as a single self-contained HTML file with:
- inline CSS for the full visual theme, HUD, start screen, and game-over screen
- inline JavaScript for asset definitions, audio control, physics, rendering, input handling, and UI state changes
- one full-screen `<canvas>` used for all gameplay rendering
- DOM overlays for menu screens, score HUD, next-piece preview, and reaction GIF/caption feedback

The code is organized into practical sections:
1. asset and theme configuration
2. audio controller
3. core game constants and mutable state
4. resize/init helpers
5. physics model and ball entity
6. game loop and win/loss checks
7. mouse/touch input handling
8. UI start/restart controls

## Game loop / state model
The game uses a real-time `requestAnimationFrame` loop gated by `gameActive`.

### Core state variables
- `gameActive`: whether the main loop should run
- `score`: current score
- `balls`: all active dropped/merged objects
- `particles`: floating background text particles
- `nextBallType`: which small-tier object will drop next
- `currentDropperX`: horizontal aim position
- `isDropping`: temporary lockout between drops
- `gameOverTimer`: counts frames while the stack stays inside the danger zone

### State flow
1. **Start screen**
   - player sees title, description, and start button
2. **Game start**
   - HUD appears
   - score/state reset
   - audio unlocked and BGM started
   - loop begins
3. **Active play**
   - player moves the drop position horizontally
   - player taps/clicks to release the current orb
   - physics updates and collisions resolve
   - equal-tier collisions merge into a higher tier
   - score updates
4. **Danger evaluation**
   - a warning line near the top acts as the fail threshold
   - if settled pieces remain above that line for long enough, the round ends
5. **Game over**
   - loop stops
   - BGM stops, fail SFX/GIF trigger
   - score is shown
   - restart returns to a fresh active run

## Player goals
The player is trying to:
- drop pieces into a shared pit
- line up matching pieces so they collide and merge
- grow pieces through successive evolution tiers
- keep the pile below the warning line
- survive longer and earn a higher score through cleaner combo chains

This is a score-chasing survival puzzle rather than a level-based campaign.

## Interaction pattern
Primary interaction is extremely simple:
- **move pointer/finger horizontally** to aim the drop lane
- **tap/click** to release the current piece
- wait briefly for the next queued piece
- repeat while managing stack shape and merge opportunities

The design is optimized for both mouse and touch. There is no keyboard dependency.

## Core systems
### 1. Drop-and-stack system
A preview orb hovers at the top until placed. The player chooses its x-position and drops it into the pit.

### 2. Physics simulation
Each orb has:
- position
- velocity
- radius/mass
- gravity
- friction
- bounce against the floor/walls
- collision impulse response

The simulation runs multiple substeps per frame for stability.

### 3. Merge progression
If two objects of the same tier overlap, they are deleted and replaced by a higher-tier object at their midpoint. This is the defining system of the game.

### 4. Tier ladder
There are 7 tiers total, visually represented as meme-like emoji/icon spheres:
- skull
- clown
- coin/image
- moai
- alien
- brain
- cosmos/final-tier orb

Only the first three tiers can appear as fresh drops; higher tiers are earned through merges.

### 5. Score system
Score increases when merges occur. Higher-tier merges award more points.

### 6. Loss condition
The game watches for settled balls crossing into the top warning zone. If the stack remains there long enough, the run ends.

### 7. Juice / feedback system
The presentation adds strong arcade feedback through:
- BGM and drop/bump/merge/fail SFX
- animated GIF reactions for merges and failure
- floating slang/brainrot words in the background
- colorful HUD and exaggerated title styling

## Inferred genre / gameplay shape
Strongest genre reading:
- **physics merge puzzle**
- **arcade score attack**
- **casual one-button drop game**

It closely resembles the “Suika-style” family of games: a vertical container where same-tier objects merge into larger ones, with failure caused by stack overflow near the top.

## Gameplay heuristic
The intended strategy appears to be:
- keep the center of mass stable
- avoid creating isolated mismatched large pieces near the top
- intentionally set up same-tier contact rather than dropping randomly
- leave room for chain reactions
- treat early drops as board shaping and later drops as rescue/combo decisions

The tone suggests a humorous, meme-chaos reskin of a familiar merge-stack puzzle formula rather than a deep simulation game.

## Confidence notes
Confidence is high on the core loop because the entire game logic is visible in one file.
Lower-confidence inference areas:
- whether the “brainrot” theme is meant as satire, parody, or purely cosmetic
- whether the final cosmos tier has any hidden special behavior beyond being the cap tier

No level progression, shop, unlock tree, or narrative progression is present in the code.