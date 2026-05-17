# Blueprint

## High-level code structure
The game is implemented as a single self-contained `index.html` application with three main layers:

1. **Presentation layer**
   - Inline CSS defines the neon cyberpunk HUD, modal panels, buttons, and responsive layout.
   - A full-screen `<canvas>` renders the animated slot reels, glowing symbols, grid background, and particles.
   - HTML overlays provide the HUD, scan button, upgrade shop, win feedback, game-over screen, GIF reactions, and audio elements.

2. **Configuration and media layer**
   - A small JSON config block (`#game-config`) exposes tweakable values such as spin speed and neon color.
   - Remote audio and GIF assets are wired directly into the DOM.
   - Fonts are loaded remotely to support the sci-fi arcade presentation.

3. **Game logic layer**
   - `AudioManager` handles BGM and sound effects.
   - A global `state` object stores progression, money, quota, spins, upgrades, reels, particles, and timing.
   - `Reel` and `Particle` classes encapsulate animated reel behavior and win effects.
   - Top-level functions manage state transitions, spinning, payout evaluation, progression, upgrades, input handling, UI updates, restart flow, and the main render loop.

## Game loop / state model
The runtime model is lightweight and event-driven:

- **Persistent game state**
  - `level`: current shift reached
  - `money`: current haul toward quota
  - `quota`: target money for the current shift
  - `spinsLeft`: remaining scans for the shift
  - `upgrades`: luck, multiplier, extra spins
  - `reels`: three slot reels
  - `particles`: temporary visual feedback
  - `gameState`: `PLAYING`, `SPINNING`, or `GAMEOVER`

- **Main loop**
  - `requestAnimationFrame(loop)` continuously:
    - paints the background
    - draws lane/grid scenery
    - updates each reel
    - draws each reel and symbol
    - updates and renders particles

- **Interaction/state transitions**
  - `PLAYING` → player can scan, open shop, or buy upgrades
  - `SPINNING` → reels animate and input is mostly locked
  - spin completion triggers `evaluateWin()`
  - if quota met: `levelUp()`
  - if scans exhausted before quota: `GAMEOVER`
  - restart returns to a fresh run

This is effectively a short-session arcade progression loop layered onto a slot-machine resolution system.

## Player goals
The player goal is to hit each shift’s money quota before scans run out.

Immediate goals:
- press **SCAN** to roll for matching symbols
- accumulate enough haul to fill the route quota bar
- spend money in the **Rig Bay** when it is worth delaying progress

Longer-term goals:
- survive to higher shifts
- increase odds and payouts through upgrades
- chase jackpots and better scoring runs

Failure condition:
- run out of scans before meeting the current quota

Success/progression condition:
- meet quota and advance to the next shift, where the quota increases

## Interaction pattern
The game is essentially a one-button slot-driven arcade loop with supporting menu interaction.

Primary interactions:
- **Pointer/tap on SCAN**: consume one scan and spin the three reels
- **Pointer/tap on Rig Bay**: open the upgrade modal
- **Pointer/tap on upgrade buttons**: spend current haul for permanent run upgrades
- **Pointer/tap on restart**: begin a new run after failure

Feedback pattern:
- instant audio cue on scan and outcomes
- animated reel stopping with slight staggering
- large text popups for jackpot/cache/shift clear
- particle burst, flash, vibration, and GIF reactions on wins/losses
- progress bar and counters constantly reflect run state

## Core systems
### 1. Three-reel slot resolution
Each reel contains weighted symbols with values and custom neon-drawn shapes. The game evaluates:
- **3 matching symbols** = big win, triple symbol value times multiplier
- **2 matching symbols** = smaller payout based on the matched symbol times multiplier
- **no match** = no meaningful payout

### 2. Weighted rarity / luck tuning
Each symbol has a weight. The luck upgrade reduces effective weights to make rarer symbols more likely, which is a simple probability manipulation system.

### 3. Shift quota progression
Every level represents a new “shift.” The quota scales upward using exponential growth:
- base quota starts at 100
- next quotas scale by `100 * 1.5^(level - 1)` and are floored

This creates increasing pressure while preserving the same core spin loop.

### 4. Limited-attempt economy
The player has a fixed scan budget each shift:
- starts at 10 scans
- extra-spins upgrade adds more scans per shift
This makes the game feel like a push-your-luck resource challenge rather than a pure endless slot.

### 5. Upgrade shop
The Rig Bay provides three run-persistent upgrades:
- **Signal Booster**: improves rare payout chance
- **Payout Relay**: increases payout multiplier
- **Charge Cell**: grants more scans each shift

These upgrades turn money into future consistency and scale.

### 6. Arcade presentation and sensory feedback
The game reinforces outcomes with:
- synthwave/cyberpunk UI styling
- canvas glow effects
- sound effects and looping BGM
- vibration on supported devices
- win/fail GIF badges
- particle bursts and flash overlays

## Inferred genre / gameplay shape
Strongest inferred shape:
- **clicker-like slot/arcade progression game**
- **single-screen luck-based resource management game**
- **light meta-progression run game**

It is not a traditional casino simulator. The framing reinterprets slot mechanics as a futuristic “scanner” or “courier route cache scan” system, but the underlying gameplay is clearly a slot-machine-inspired match-and-payout loop with upgrade-driven progression.

## Gameplay heuristic
A player likely succeeds by following this pattern:
1. Spin early to build a small haul.
2. Buy upgrades when they meaningfully improve future expected value.
3. Prioritize payout multiplier and extra scans for consistency, with luck as a rare-symbol enhancer.
4. Race the quota bar before exhausting the scan budget.
5. Repeat across increasingly difficult shifts.

The design encourages fast sessions, readable outcomes, and escalating risk/reward rather than precise dexterity.

## Confidence notes
Confidence is fairly high because the code explicitly defines:
- reel weights and symbol values
- payout logic
- level/quota scaling
- upgrade effects
- fail and progression conditions
- the UI fiction (“shift,” “route quota,” “haul,” “Rig Bay,” “scan”)

The only notable ambiguity is categorization: the presentation theme suggests a courier-scanner fantasy, but the underlying mechanics are most directly a slot-like clicker/arcade loop rather than a traditional action game.