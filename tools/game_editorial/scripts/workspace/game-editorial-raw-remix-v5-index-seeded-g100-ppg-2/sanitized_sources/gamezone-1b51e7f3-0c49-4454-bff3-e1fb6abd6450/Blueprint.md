# Blueprint

## High-level code structure
The game is implemented as a single self-contained `index.html` file with three main layers:

1. **Presentation / layout**
   - HTML defines a full-screen mobile-first shell with a canvas playfield, floating HUD, action buttons, a supply-shop modal, toast messaging, animated GIF feedback badges, and a game-over overlay.
   - CSS establishes a cozy neon-purple pet-care aesthetic with glassmorphism panels, compact HUD bars, and strong touch-target sizing.

2. **Simulation / gameplay logic**
   - A global `STATE` object tracks the current phase, canvas size, the pet instance, particles, money drops, economy values, message timers, and work cooldown timing.
   - `CONFIG` stores stat decay values, pet color palettes, prices, and reward ranges/configuration.
   - The `Cat`, `MoneyDrop`, and `Particle` classes model the main on-screen entities.

3. **Systems / orchestration**
   - `AudioSys` manages background music, UI/gameplay SFX, unlock behavior, and play/pause sync with game state.
   - Event handlers connect pointer input and UI buttons to actions like work, play, sleep, shop, buy food, feed, and restart.
   - The `loop()` function drives updates, rendering, cooldown visuals, and HUD syncing through `requestAnimationFrame`.

## Game loop / state model
The runtime model is a lightweight real-time pet-care loop.

- **Phases**
  - `BOOT`: implied startup before initialization completes.
  - `PLAYING`: normal simulation, stat decay active, player can interact.
  - `GAMEOVER`: triggered when happiness/trust reaches zero.

- **Core loop**
  1. Initialize canvas, audio, and a fresh cat with randomized palette.
  2. Enter `PLAYING`.
  3. Every frame:
     - update pet animation and stat decay/recovery
     - update falling/bouncing money pickups
     - update floating particles
     - redraw the room-like background and pet
     - update cooldown overlay and HUD bars
  4. Player offsets decay through actions.
  5. If happiness/trust drops to zero, transition to `GAMEOVER`.
  6. Restart resets money, food stock, cooldowns, particles, and the pet.

## Player goals
The player’s short-term and long-term goals are:

- keep the cat’s **food**, **fun**, **energy**, and especially **trust/happiness** from collapsing
- earn **tips/money** by doing work shifts
- convert money into **food stock**
- spend stocked food to restore hunger
- alternate between work, play, sleep, and affection taps to stabilize all needs
- survive as long as possible without the cat losing trust and leaving

This creates a survival-through-maintenance objective rather than a level-completion structure.

## Interaction pattern
The interaction model is direct, touch-friendly, and real-time:

- **Tap the pet** to give affection and slightly restore happiness/trust.
- **Tap Shift** to spawn collectible coins/tips, gated by a cooldown.
- **Tap coins** on the canvas to collect money.
- **Tap Shop** to open a modal where the player can buy food or serve a meal from stock.
- **Tap Play** to boost fun at the cost of energy.
- **Tap Sleep / Wake** to toggle the pet’s sleep state, restoring energy over time while slowing some other needs.
- **Tap Restart Shift** after failure.

The game mixes UI-button actions with direct on-canvas collection and pet interaction.

## Core systems
### 1. Need decay system
The pet has four stats:

- hunger
- fun
- energy
- happiness/trust

These decay continuously while awake. Happiness decays faster if hunger, fun, or energy are low, making it the fail-state stat.

### 2. Sleep recovery system
Sleep changes the pet state and alters simulation behavior:

- energy regenerates
- hunger/fun still decay, but more slowly
- happiness can recover slightly if hunger is safe
- some interactions are blocked while sleeping

### 3. Work-and-collect economy
Pressing the work button spawns several physical coin pickups on the canvas:

- work is on cooldown
- player must manually tap the spawned coins to bank money
- money is then spent on food purchases

This adds an active collection layer rather than granting currency instantly.

### 4. Inventory/shop system
Food is not used directly from money. The game has a simple two-step resource loop:

- spend money to buy food stock
- spend one food stock to feed the cat

This creates light inventory management.

### 5. Affection and mood feedback
Tapping the cat grants small happiness gains and triggers hearts/positive feedback. Failed actions trigger negative toast/GIF feedback, reinforcing the pet-bond fantasy.

### 6. Audio/haptics feedback
The code includes:

- looping background music
- click, reward, collect, blocked, and game-over SFX
- vibration/haptic hooks for supported devices

### 7. Visual-state rendering
The cat is drawn entirely on canvas and visually reflects status:

- sleeping face and floating “Zzz”
- playful arc effect
- hunger/fun warning emojis
- random coat palettes
- squash/stretch and blinking animation

## Inferred genre / gameplay shape
Strongest inferred genre shape:

- **pet simulator / virtual pet care game**
- with **light resource management**
- and a **real-time survival-maintenance loop**

It resembles a compact “care shift” variant of a Tamagotchi-like pet sim, framed as balancing caregiving duties and short work bursts. It is not level-based, narrative-heavy, or puzzle-driven; it is a continuous upkeep game with soft pressure and cozy presentation.

## Progression shape
Progression appears to be session-based rather than stage-based:

- the player starts with modest money and food
- pressure increases naturally through continuous stat decay
- success depends on maintaining equilibrium
- the only hard progression marker is how long the player keeps the shift alive
- restart begins a new run with a fresh randomized cat palette

## Gameplay heuristic
A practical strategy inferred from the systems:

1. Keep happiness/trust from snowballing downward.
2. Use **play** before fun becomes critical, but avoid draining energy too far.
3. Use **sleep** proactively when energy is low, not only in emergencies.
4. Use **work** whenever off cooldown to sustain the economy.
5. Actually collect the spawned money drops quickly.
6. Buy food before stock hits zero.
7. Feed before hunger becomes low enough to accelerate happiness loss.
8. Use pet taps as small trust stabilizers between larger actions.

The intended feel is a cozy but slightly hectic balancing act: a cute caretaker game where neglect compounds quickly, so the player must rotate maintenance actions intelligently.