# Blueprint

## High-level code structure
The game is a single-file HTML application with embedded CSS and JavaScript. It is organized into four major layers:

1. **Presentation layer**
   - A start screen, gameplay screen, archive/almanac screen, and game-over overlay.
   - Heavy neon sci-fi visual styling using Tailwind utility classes plus custom CSS.
   - A canvas-based animated background and procedural SVG card art.

2. **Game data/config**
   - `CONFIG` defines starting funds and per-scan cost.
   - `RARITIES` defines the five possible relic outcomes, including weight, payout multiplier, visual style, and display metadata.

3. **Game controller**
   - A single `app` object manages state, navigation, roll/reveal flow, save/load behavior, archive rendering, and game-over handling.

4. **Support systems**
   - `audio` handles BGM and sound effects with Web Audio fallback behavior.
   - `particles` handles celebratory particle bursts and background updates.
   - Local storage persists unlocked relic archive progress.

## Game loop / state model
This is not a physics or time-pressure loop game. It is a **discrete tap-to-roll loop** with lightweight ambient animation.

### Persistent / session state
- **balance**: current money available to spend on scans
- **unlocked**: set of relic rarities discovered for the archive
- **rolling**: lock to prevent overlapping rolls
- **history**: simple screen navigation stack

### Core gameplay cycle
1. Player enters the vault screen.
2. Player spends **$100** to perform a scan.
3. A card appears and shakes briefly.
4. A weighted random rarity is selected.
5. The card flips to reveal a relic.
6. Payout is applied immediately based on multiplier.
7. New rarity is added to the archive collection.
8. Audio/particles/GIF feedback reinforce the result.
9. Player decides whether to scan again, inspect archive progress, or leave.

### Failure state
- If funds drop below the scan cost and effectively reach exhaustion, the player enters a **lockout / game over** state.
- Restart resets funds to the starting amount, but the discovered archive set remains saved unless cleared externally.

## Player goals
The inferred player goals are:

- **Primary goal:** keep scanning relics while managing a limited bankroll.
- **Secondary goal:** discover and unlock all five rarity tiers in the archive.
- **Emotional goal:** chase rare, epic, and legendary reveals for high-reward moments.

The game mixes survival of your funds with collection completion.

## Interaction pattern
- **Primary input:** tap/click buttons
- **Main action:** press the large SCAN button to pay for a randomized reveal
- **Secondary actions:** open archive, return home, restart after lockout
- **No direct movement controls:** this is menu-driven and event-driven rather than spatially navigated gameplay

## Core systems
### 1. Weighted random reward system
Each relic tier has a weight:
- common / scrap outcome is most likely
- legendary is extremely rare

This creates a slot-machine / gacha-style probability structure.

### 2. Risk-reward economy
- Every scan costs money.
- Most interesting outcomes return money via multipliers.
- Bad outcomes can drain the bankroll and force lockout.

### 3. Collection / codex progression
- Revealed rarity IDs are stored in `unlocked`.
- The archive screen shows discovered relics and hidden locked entries.
- Completion is measured as unlocked count out of total entries.

### 4. Reward presentation system
- Card shake, flip animation, rarity glow, particle explosion, and contextual sounds.
- High-tier wins trigger extra rare-feedback GIFs and stronger audiovisual celebration.

### 5. Lightweight persistence
- Archive unlock progress is saved in local storage.
- Currency is session-based and resets on restart.

## Inferred genre / gameplay shape
This game is best understood as a:

- **gacha / loot-box style reveal game**
- with **light clicker / one-button risk economy**
- and **collection tracker / archive completion**
- wrapped in a **neon sci-fi vault-opening fantasy**

It is not a deep simulator or action game; the core pleasure comes from repeated randomized reveals, rarity anticipation, and collection completion under bankroll pressure.

## Gameplay heuristic
The intended player heuristic appears to be:

- Spend repeatedly while funds allow.
- Hope to stabilize or grow balance through uncommon-to-legendary hits.
- Celebrate large reveals and gradually complete the archive.
- Accept that the run can end through unlucky scans, then restart and try again.

This produces a short-session, highly readable reward loop built around anticipation, reveal spectacle, and collection progress.
