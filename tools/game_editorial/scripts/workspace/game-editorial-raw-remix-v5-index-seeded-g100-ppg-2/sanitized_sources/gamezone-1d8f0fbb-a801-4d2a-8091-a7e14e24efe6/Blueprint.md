# Blueprint

## High-level code structure
- Single-file HTML game with embedded CSS and JavaScript in `index.html`.
- Presentation is split between:
  - a full-screen `canvas` for the animated playfield,
  - an HTML HUD layer for score, timers, and navigation,
  - modal panels for shop, inventory, map selection, archive, and pause/settings.
- Data is primarily defined through in-code constants:
  - `BALL_TYPES` describes collectible/deployable orb units, prices, incomes, rarities, and flag visuals.
  - `MAP_DEFINITIONS` describes route/region unlocks and income boosts.
  - `CHAT_PHRASES` gives personality flavor text for each orb type.
- Core game behavior is driven by global state variables plus a `Ball` class for active entities.
- Persistence is handled with `localStorage`.

## Game loop / state model
- Main state machine is lightweight:
  - `PLAYING`: active simulation and income generation.
  - `PAUSED`: simulation effectively halted while menu/modal pause is open.
- The loop uses `requestAnimationFrame(gameLoop)` and performs:
  - background rendering,
  - active orb update and draw,
  - floating reward text animation,
  - shop restock countdown updates,
  - continuous rescheduling of the next frame.
- Each active orb:
  - bounces inside the screen bounds,
  - generates passive money every second,
  - can emit flavor chat bubbles,
  - reacts to clicks/taps for a tiny bonus and bounce impulse.
- Shop progression is timer-based:
  - stock refreshes on a configurable timer,
  - four recruit options are rolled using weighted rarity chances.
- Save model stores:
  - credits,
  - unlocked orb types,
  - active and stored orb inventory,
  - current map and unlocked maps,
  - shop stock and next restock timestamp.

## Player goals
- Accumulate credits over time.
- Buy stronger embassy/envoy orbs with better passive income.
- Expand the active roster up to the max active-capacity limit.
- Manage overflow by storing and redeploying owned orbs.
- Unlock higher-value route/region maps that add income multipliers.
- Fill out the archive by unlocking more orb/nation variants across rarities.

## Interaction pattern
- Primary interaction is tap/click management:
  - tap moving orbs on the canvas to get a small instant credit bump,
  - open the market to purchase new orbs,
  - open roster/inventory to equip or unequip owned orbs,
  - open regions to buy/equip maps,
  - open archive to inspect unlock progress.
- The experience is mostly passive/idle, but player input slightly accelerates growth and drives purchasing decisions.
- Audio, vibration, floating text, and GIF overlays reinforce successful or blocked actions.

## Core systems
- Passive income simulation from active deployed orbs.
- Weighted shop restocking / rarity-driven acquisition system.
- Inventory management with active-vs-stored unit counts.
- Unlock/collection tracking via archive/index view.
- Region/map upgrade system with multiplicative income boosts.
- Save/load and autosave loop.
- Cosmetic personality system through flag visuals, faces, bouncing motion, and chat callouts.
- Mobile-friendly HUD and full-screen canvas presentation.

## Inferred genre / gameplay shape
- Primary shape: idle collection/management game.
- Secondary shape: light clicker/incremental game with roster building.
- Presentation style resembles a playful “countryball embassy manager” sandbox with gacha-like rarity excitement, but without true chance-box opening as a separate mechanic.
- The strongest gameplay loop is:
  1. collect passive credits,
  2. tap orbs for bonus income,
  3. buy stronger orbs from rotating shop stock,
  4. manage active capacity,
  5. unlock boosted regions,
  6. expand collection and income scale.

## Gameplay heuristic
- Early game begins with one cheap, low-income orb and very small manual boosts from tapping.
- Growth is driven mostly by passive income stacking rather than precision play.
- Better rarities and more expensive nation orbs sharply increase progression speed.
- Because active slots are capped, inventory and deployment decisions matter once the roster grows.
- Unlocking the snow/polar route appears to be a meaningful midgame milestone because it adds a visible +15% earnings boost.
- The game is designed for short check-ins and long-term accumulation rather than intense moment-to-moment challenge.

## Confidence notes
- High confidence that this is an idle/clicker collection-management game.
- Medium confidence on whether the archive/collection fantasy should be interpreted as “collector” or “gacha-adjacent,” because acquisition is done through a rotating weighted shop rather than explicit pulls.
- High confidence that the setting/theme is intentionally a humorous countryball-style embassy simulation rather than a realistic geopolitical management game.