# Blueprint

## High-level code structure
This game is implemented as a single self-contained `index.html` document with:
- inline CSS for the neon sci-fi visual identity and responsive HUD layout
- HTML for the start screen, HUD, upgrade panel, offline earnings modal, feedback GIF overlays, audio tags, and the main canvas
- an inline ES module script containing configuration, persistent state, upgrade definitions, audio handling, rendering, input wiring, save/load logic, and the main loop

There is no external gameplay framework. The game uses:
- a full-screen `<canvas>` for the moving conveyor-belt scene and animated entities
- DOM-based UI for progression controls and status display
- `localStorage` for persistence and offline earnings recovery
- HTML audio elements plus Web Audio decoding for music and sound effects

## Game loop / state model
The game follows a lightweight idle/clicker loop with a real-time render pass.

### Core state
Persistent state includes:
- `money`
- `rebirths`
- `upgrades.auto`
- `upgrades.speed`
- `upgrades.value`
- `upgrades.luck`
- `lastSaveTime`

Runtime-only state includes:
- active moving bot/signal units (`tvs`)
- floating text particles
- auto-production timer
- play/session flags
- transient UI feedback timers

### Loop behavior
Once the player presses **GO LIVE**, the game:
1. initializes audio
2. hides the start screen
3. shows the HUD
4. starts the animation loop
5. checks for offline earnings

During each animation frame:
1. auto-production may spawn new courier units based on Auto-Relay level
2. every active unit moves across the belt
3. units that leave the right side of the screen convert into money
4. payout value is modified by value upgrades, rebirth multiplier, and random viral payout checks
5. particles are updated
6. the full conveyor scene is redrawn on the canvas

### Progression model
The economy is exponential and layered:
- manual production creates the initial earnings source
- automation reduces reliance on tapping
- speed increases throughput
- value increases payout per completed unit
- luck adds occasional critical 5x payouts
- rebirth resets progress in exchange for permanent doubled earnings multipliers

## Player goals
The immediate player goal is to tap **TRANSMIT** to send robot courier signals across the belt and earn credits when they exit the screen.

The medium-term goal is to buy upgrades that:
- automate signal launching
- move signals faster
- make each sale worth more
- increase the chance of viral 5x rewards

The long-term goal is to reach the rebirth threshold, reset the network, and build a stronger permanent multiplier for future runs.

## Interaction pattern
The interaction pattern is very simple and mobile-friendly:
- tap/click **GO LIVE** to begin
- tap/click **TRANSMIT** to spawn a manual courier unit
- tap/click upgrade buttons in the broadcast list to invest earnings
- optionally trigger **RESET NETWORK** once the rebirth threshold is reached
- claim offline earnings from the modal after returning to the game

The canvas is mostly observational rather than direct-manipulation gameplay. The player does not steer units; instead they control production and economy timing.

## Core systems
### 1. Manual production
Pressing the main transmit button creates a glowing courier unit and plays a tap sound.

### 2. Automated production
The Auto-Relay upgrade periodically spawns units at decreasing intervals, capped to prevent infinite acceleration.

### 3. Conveyor movement and payout resolution
Units travel from left to right along a belt. When they move past the screen edge, they are sold automatically for currency.

### 4. Upgrade economy
Each upgrade has:
- a base cost
- an exponential cost multiplier
- a level cap
- a focused gameplay effect

### 5. Critical reward system
Luck creates a percentage chance for a 5x payout, reinforced by bonus SFX, floating text, and reward GIF feedback.

### 6. Prestige / rebirth
At one million credits, the player can reset their economy and upgrades for a permanent payout multiplier.

### 7. Persistence and offline income
The game autosaves and stores a timestamp. On return, if the player had automation unlocked, it estimates missed production and awards catch-up earnings in a modal.

### 8. Audio-visual feedback
The experience is reinforced by:
- looping background music
- action and bonus sounds
- fail feedback for unaffordable purchases
- animated reward/failure GIF callouts
- floating payout text
- glowing neon HUD styling

## Inferred genre / gameplay shape
Strongest inferred shape:
- **clicker / idle economy game** with a prestige layer

Secondary shape:
- **light conveyor-themed management fantasy**
- **casual incremental game with cosmetic action feedback**
- **single-screen mobile-first tap game**

This is not a skill runner despite the title language. The player does not dodge, steer, or traverse levels. The mechanical heart is earning, upgrading, automating, and prestiging.

## Gameplay heuristic
A player experience heuristic inferred from the code:
1. Start with active tapping to create visible momentum.
2. Convert early earnings into automation as soon as possible.
3. Improve speed to increase turnover frequency.
4. Stack value and luck for larger spikes and more satisfying reward moments.
5. Use offline earnings as a retention loop.
6. Rebirth at the threshold to accelerate future cycles.

## Presentation and tone
The game presents as a cyber-neon “broadcast factory”:
- dark futuristic background
- perspective grid floor
- glowing conveyor belt
- robot courier crates moving laterally
- synthetic terminology such as signal, relay, boost, network reset
- playful, flashy reward moments rather than serious simulation

## Confidence notes
Confidence is high that the implemented game is an idle/clicker prestige game.
Confidence is moderate on the narrative framing because the code mixes names like:
- Neon Signal Factory
- Signal Sprinter
- robot courier broadcast line
- signal bot sales

These suggest the exact fiction shifted during development, but the gameplay loop is consistent: send neon robotic broadcast units down a conveyor for money, upgrade the pipeline, and prestige.