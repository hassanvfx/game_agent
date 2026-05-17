# Blueprint

## High-level code structure
The game is implemented as a single self-contained `index.html` document with four main layers:

1. **Presentation and layout**
   - Inline CSS defines the neon night-market visual language, HUD glass panels, start screen, responsive sizing, and touch-friendly controls.
   - DOM elements provide the start overlay, HUD, cook button, audio tags, and two feedback GIF elements.

2. **Configuration layer**
   - A JSON blob in `#game-config` declares editable tunables:
     - `cookSpeed`
     - `dayDuration`
     - `foodPrice`
   - The script mirrors this into `window.gameConfigDefs` and `window.gameConfig`, allowing runtime config overrides.

3. **Audio system**
   - `AudioManager` wraps Web Audio / HTML audio behavior.
   - It initializes an `AudioContext`, unlocks audio on first interaction, preloads remote sound effects, plays looping background music, and falls back to generated oscillator sounds when remote audio fails.

4. **Game logic and rendering**
   - A single canvas render loop driven by `requestAnimationFrame`.
   - Global state variables track money, stock, cooking progress, customers, particles, floating text, stars, and time-of-day.
   - The game uses a simple update/draw architecture:
     - `initGame()`
     - `update(dt)`
     - `draw()`
     - helpers such as `spawnCustomer()`, `spawnParticle()`, `spawnFloatText()`, `updateHUD()`, `showFeedbackGif()`

## Game loop / state model
The state model is minimal and arcade-like.

### States
- `START`
  - Start overlay visible.
  - Player cannot meaningfully interact with the cooking loop yet.
- `PLAY`
  - Main loop updates time, customers, particles, UI, and rendering.

### Core runtime loop
Each animation frame:
1. Compute `dt` from the last timestamp.
2. If in `PLAY`:
   - advance in-game time
   - compute `dayCycle`
   - determine `isNight`
   - randomly spawn customers up to a cap
   - update each customer state
   - update particles and floating text
   - periodically refresh HUD
3. Render the entire scene on canvas:
   - sky / sun or moon / stars
   - skyline and street
   - stall and chef
   - customers
   - stock visuals
   - cooking progress bar
   - particles and floating reward text
   - night vignette overlay

### Core state variables
- `money`: total earnings
- `foodStock`: completed servings available to sell
- `cookingProgress`: tap-driven meter toward producing one serving
- `gameTime`: elapsed time
- `dayCycle`: normalized cycle position
- `isNight`: toggles night visuals and price multiplier
- `customers`: queue of active buyers
- `particles`, `floatTexts`, `stars`: presentation feedback systems

## Player goals
The inferred player goal is to run a small street-food stall and earn as much cash as possible by:
- repeatedly tapping to cook skewers
- maintaining enough stock for incoming customers
- serving customers before they lose patience
- taking advantage of the night-time price bonus for larger payouts

There is no formal win state or level completion. The goal is score maximization within an endless arcade loop.

## Interaction pattern
The interaction model is extremely simple and mobile-first:

- **Primary action:** tap / press the large central **TAP TO COOK** button
- Repeated taps fill a cooking meter
- Completing the meter adds one food item to stock
- Customers arrive automatically
- If stock is available, waiting customers automatically purchase after a short delay
- If they wait too long without stock, they leave angrily

This creates a one-button management rhythm:
**tap to produce -> build stock -> auto-serve customers -> earn money -> keep up with demand**

## Core systems
### 1. Cooking / production system
- Each tap adds `cookSpeed` to `cookingProgress`
- At `COOK_MAX`, progress resets and `foodStock` increments
- Producing stock triggers steam particles, SFX, and a cooking reaction GIF

### 2. Customer queue system
- Customers spawn randomly while under the cap of 5
- They walk in from the left, line up near the counter, then wait
- If stock exists and the wait time exceeds a brief threshold, they buy automatically
- If the wait exceeds 8 seconds with no service, they leave with a fail cue

### 3. Economy / scoring system
- Every sale increases `money` by `foodPrice`
- At night, sale value is doubled
- Sales trigger floating money text, coin particles, and a positive reaction effect

### 4. Time-of-day cycle
- `dayDuration` controls the speed of the full cycle
- The game visually shifts between sunset/day and night
- Night enables a visible **NIGHT BONUS x2** indicator and doubles selling price

### 5. Visual feedback system
- Animated cooking bar
- Floating money text / anger emoji
- Steam and coin particles
- Reaction GIFs
- Animated stars, glowing celestial bodies, and colorful gradients

### 6. Audio feedback system
- Looping background ambience/music
- Start, cook, sell, and fail sounds
- Oscillator fallback behavior if remote sound loading fails

## Inferred genre / gameplay shape
Strongest inferred genre shape:
- **light arcade management**
- **tap-driven cooking / service loop**
- **score attack / endless survival of demand pressure**
- **casual mobile one-button economy game**

It is not a deep tycoon or simulation. The game is closer to a compact, reactive **cooking clicker / arcade service game** with a day-night bonus mechanic and a highly stylized presentation.

## Gameplay heuristic summary
The intended moment-to-moment heuristic appears to be:

1. Start the shop
2. Tap quickly to fill the cook meter
3. Convert taps into food stock
4. Anticipate a steady stream of customers
5. Avoid empty stock while customers wait
6. Earn cash automatically from served customers
7. Exploit night-time for doubled revenue
8. Continue indefinitely, chasing a higher cash total

## Confidence notes
High confidence:
- one-button cooking loop
- auto-selling customers
- endless score-chasing structure
- night bonus economy mechanic
- casual mobile-friendly design intent

Moderate uncertainty:
- there is no explicit failure state, stage progression, or upgrade system
- customer spawn pacing is random rather than wave-authored
- the time-of-day comment suggests slightly rough logic, but the intended design is clearly a sunset-to-night service cycle