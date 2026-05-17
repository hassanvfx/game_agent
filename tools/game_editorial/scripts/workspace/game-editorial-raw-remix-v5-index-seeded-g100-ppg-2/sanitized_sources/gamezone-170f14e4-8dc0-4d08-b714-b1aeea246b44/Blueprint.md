# Blueprint

## High-level code structure
The game is a single-file HTML arcade experience implemented entirely in `index.html` with embedded CSS and JavaScript. The structure is:

- **HTML shell and HUD**
  - A full-screen `canvas` used for all gameplay rendering.
  - HUD panels for score, tool selection, tutorial hinting, and status messaging.
  - Two GIF overlays for success/failure feedback.
  - A hidden config blob in JSON form for tunable gameplay values.
- **Presentation layer**
  - Large inline CSS block defines a neon arcade look with glassmorphism HUD panels, pixel-style headings, and mobile-safe layout behavior.
- **Audio system**
  - `AudioManager` loads approved remote music and UI/SFX clips through Web Audio.
  - Handles unlock-on-first-input, cooldowns, separate BGM/SFX gain buses, and event-triggered sound playback.
- **Game state and loop**
  - Global state stores money, grid cells, particles, floating score text, current tool, camera, and overlay timers.
  - `requestAnimationFrame` drives a simple update/draw loop.
- **Rendering system**
  - Isometric grid rendering through helper projection functions.
  - Cell drawing uses prism-like shapes and emoji prompts to visualize machine states and available actions.
  - Particle and floating-text systems reinforce moment-to-moment actions.
- **Input/UI logic**
  - Pointer input maps screen positions into isometric grid coordinates.
  - Tool buttons switch the currently active action mode.
  - Interaction rules are enforced per tile state.

## Game loop / state model
The runtime model is a **continuous real-time management loop** over a small fixed grid.

### Core state per cell
Each grid cell contains:
- `state`: `empty`, `prepped`, `cooking`, or `done`
- `timer`: elapsed charge/cook time while active
- `maxTime`: target duration from config
- `bounce`: transient animation offset
- `dishId`: random visual variation token

### Global progression state
- **Money / prize total** is the main score.
- **Current tool** determines the only action the player can attempt:
  - `prep`
  - `cook`
  - `serve`
- **No fail state, timer pressure, or win screen** is present in code.
- Play appears effectively endless and score-chasing.

### Update loop behavior
Every frame:
1. Audio cooldowns tick down.
2. Each cell updates:
   - bounce decays
   - cooking timers advance
   - steam particles spawn randomly while charging
   - finished cells flip from `cooking` to `done`
3. Overlay timers for celebration/failure fade out.
4. Particles and floating texts animate and expire.
5. Scene redraws fully on canvas.

This makes the gameplay feel like a light real-time station-management toy with immediate feedback.

## Player goals
The player’s practical goal is to:
- fill arcade stations with snack orders,
- activate the charge/processing phase,
- wait until a station completes,
- cash out finished stations for money,
- repeat this loop across as many stations as possible.

The score incentive is straightforward: each completed station awards a fixed payout from config (`dishPrice`), so efficient chaining and keeping many stations cycling at once is the implied mastery layer.

## Interaction pattern
The interaction model is **single-tap direct manipulation plus mode switching**.

### Tool flow
The intended order is explicitly taught in UI text and enforced in logic:

1. **Beam In / Prep**
   - Tap an empty station to place an order.
2. **Charge / Cook**
   - Switch tools, then tap a prepped station to begin timed processing.
3. **Jackpot / Serve**
   - Switch tools again, then tap a finished glowing station to collect money.

Wrong actions do not hard-punish the player, but they do:
- play an error sound,
- bounce the cell,
- show a fail GIF,
- display corrective tutorial language.

This creates a forgiving but structured arcade-management rhythm.

## Core systems
### 1. Isometric station grid
The whole game revolves around a configurable square isometric board (`gridSize`, default 4x4). Each tile is a self-contained station with simple state transitions.

### 2. Three-step production pipeline
Despite the food theming, the presentation reframes cooking as a sci-fi arcade process:
- order deployment,
- machine charging,
- ticket/prize cash-out.

This pipeline is the central mechanic.

### 3. Real-time waiting layer
Once a station enters `cooking`, it completes automatically after `cookTime`. This adds asynchronous multitasking: the player is encouraged to prepare other stations while waiting.

### 4. Score economy
Completed stations increase a visible dollar total. The economy is flat and easy to read; there are no expenses, upgrades, or resource sinks implemented.

### 5. Feedback stack
The game leans heavily on responsive feedback:
- audio cues for each action type,
- haptics bridge calls,
- status text updates,
- tutorial text updates,
- particles,
- floating score text,
- GIF celebration/failure flashes,
- animated HUD score pulse.

### 6. Configurability
The embedded config allows external tuning of:
- charge/cook duration,
- payout per completion,
- grid size.

This suggests the game was built as a configurable casual prototype.

## Inferred genre / gameplay shape
Strongest inference: **casual click/tap management arcade game** with toy-like time-management elements.

It is not a deep tycoon or simulation game because:
- there are no upgrades, staffing systems, or persistent economy layers,
- there is no scheduling complexity or customer queue system,
- interactions are limited to one repeated three-step loop.

It also is not a puzzle in the strict sense, because:
- there is no combinational board logic,
- no limited moves,
- no deterministic objective state to solve.

The closest gameplay shape is:
- **clicker/tapper-adjacent loop**
- **light cooking/restaurant process fantasy**
- **small-grid asynchronous task management**
- **score-attack arcade presentation**

## Gameplay heuristic
A player who understands the game will likely optimize around:
- filling many empty stations quickly with **Prep**,
- converting all prepped stations into **Charge** state,
- rotating to **Jackpot** collection as stations finish,
- minimizing idle empty stations,
- avoiding wasted taps with the wrong tool selected.

In short: **maintain station uptime and cycle the whole grid through prep → charge → jackpot as efficiently as possible.**

## Confidence notes
Confidence is fairly high on the interaction loop because the code is explicit about:
- state transitions,
- tool order,
- payout,
- tutorial messaging,
- real-time completion behavior.

Confidence is lower on any deeper progression interpretation because no levels, upgrades, loss conditions, or long-form content are implemented in the inspected code.