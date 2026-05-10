# Blueprint

## Current game reality

### High-level code structure
- `index.html` hosts a single full-screen canvas, HUD overlays, start screen, and game-over screen.
- `assets/obfuscated/inline-script-001.js` contains the core game logic:
  - `State` stores active round state, health, score, drag state, entities, particles, and continuous difficulty.
  - `Bug` models the draggable threats.
  - `Particle` handles clear effects.
  - `resize`, `spawnEntity`, `loop`, `handleStart`, `handleMove`, `handleEnd`, `startGame`, and `endGame` drive the interaction loop.
  - `FunkAudio`, `ReactionFX`, and `GFX` provide feedback systems, though audio URLs are empty.
- `assets/obfuscated/inline-style-001.css` controls the neon UI, overlay screens, HUD, and mobile-safe layout.

### Game loop / state model
1. Start screen waits for player input.
2. Starting the game resets health, score, difficulty, and active entities.
3. Bugs spawn inside a central ellipse positioned over a large foot illustration.
4. The player drags bugs away from their origin.
5. Releasing a bug far enough clears it, adds score, and restores health.
6. Bugs left on the stage long enough begin draining health continuously.
7. Difficulty rises gradually over time, increasing spawn and damage pressure.
8. When health reaches zero, the game over overlay appears.

### Player goals
- Remove threats quickly enough to keep the health bar alive.
- Maintain control as more bugs accumulate.
- Maximize clears before the set crashes.

### Interaction pattern
- Mouse and touch drag are the full interaction model.
- Tap/press to latch onto a bug.
- Move to carry it away.
- Release after exceeding the clear distance.

### Core systems
- Spawn timing
- Drag targeting
- Distance-based clearing
- Continuous health drain from neglected threats
- Score accumulation
- Simple overlay state switching
- Canvas-based visual feedback

### Inferred genre / gameplay shape
- One-screen arcade
- Mobile-friendly drag reflex game
- Endless survival / high-score loop

### Current identity summary
The source game is a neon, music-stage-themed bug-clearing arcade toy. Its identity is built from:
- dance-floor / concert language
- "stage pulse" health framing
- glitch bugs as pests
- tweezers-like grab feedback
- stylish HUD and reaction cards

## Mechanic decomposition

### Protected mechanics
These should remain stable downstream:
- single-screen canvas playfield
- bug spawning inside the central stage area
- drag-to-remove input model
- clear threshold based on drag distance from origin
- health drain from aged, uncleared bugs
- health recovery and score gain on successful clear
- continuous difficulty increase during an endless round
- start / game over state flow
- mobile-first pointer and touch support

### Themable surfaces
These can safely shift:
- title, subtitle, instructions, and outcome copy
- HUD labels and world framing
- bug appearance and fictional identity
- stage/foot interpretation as a magical ward map or cursed imprint
- color palette and ambient overlays
- particles, reactions, and feedback language
- background storytelling and progression framing
- tweezers presentation as enchanted tongs or wizarding tool

### Repairable surfaces
- Audio can be integrated later if catalog-approved sources are added safely.
- Minor copy/UI clarity changes are safe.
- Small feedback polish is safe if it does not alter timing or controls.

## Intended remixed trajectory

### Remix-direction summary
Remix prompt: **Harry Potter**

The safest and strongest transformation is not a combat-spell game. The source interaction is already about plucking pests off a surface. That maps naturally to a Hogwarts magical pest-control scenario:
- The player is a Hogwarts student on ward-duty.
- The bugs become Cornish pixies / cursed magical pests.
- The foot stage becomes a warded magical imprint or castle protection map.
- The health bar becomes ward integrity.
- Clears become pests banished.

### Remix premise
**Hogwarts Pest Control: Cornish Pixie Panic**

A magical outbreak is spreading through Hogwarts. The player uses enchanted golden tongs to remove cursed pixies and wizarding pests from an active ward map before the castle’s protective magic collapses.

### Why this direction fits the source game
- Dragging pests off a surface already feels tactile and magical.
- No new verbs are required.
- The escalating pressure fits a spreading infestation story.
- The one-screen play area can represent different wizarding locations through visual world changes.
- A five-level progression can be conceptual and presentation-driven without changing the mechanics.

## Preserve-vs-change guidance for downstream stages

### Preserve
- All drag semantics
- Core spawn behavior
- Score and health logic
- Fail state
- Game loop timing
- Mobile actionability
- Readability of targets against the playfield

### Change
- Copy, naming, and HUD wording
- Visual identity of threats
- Background environment and progression framing
- Reaction messaging
- UI materials, typography, and magical motifs
- Procedural art system for a five-world Hogwarts journey

## Five-level progression blueprint

### Level 1 — Common Room Practice
- Beginner magical training
- Warm banners, candles, simple pixies
- Clear introduction to the ward-integrity fiction

### Level 1.5 — Moving Staircase Mischief
- First escalation proof
- More motion in the background
- Same mechanics, greater urgency

### Level 2 — Moving Staircase Rush
- Corridor ward emergency
- Stronger castle motion language
- Slightly sharper threat presentation

### Level 3 — Greenhouse Infestation
- Full intended visual stack
- Herbology glasshouse atmosphere
- Lush magical clutter kept secondary to target clarity

### Level 4 — Forbidden Forest Edge
- Darker defensive tone
- Moon haze and patronus-blue flashes
- Pressure increases through atmosphere and framing, not new controls

### Level 5 — Great Hall Night of 1,000 Charms
- Finale world-state
- Floating candles, converging house-color beams, stressed grand seal
- Highest readable pressure with the same protected interaction model

## Downstream execution heuristic
Later stages should treat this as a **thematic transformation with progression planning**, not a gameplay rewrite. The best result will:
- keep the source loop intact
- make the Harry Potter premise unmistakable
- build a procedural magical art language
- stage visual escalation across five worlds
- preserve clarity on mobile
- avoid any risky structural refactor that endangers dragging, clearing, or health behavior