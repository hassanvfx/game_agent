# Cosmic Foundry Blueprint

## High-level code structure
- A single-file browser game implemented in `index.html`.
- The document contains:
  - inline CSS for the full visual theme, HUD, start screen, shop sheet, and feedback overlays
  - inline HTML for the canvas, HUD, start overlay, shop UI, and audio elements
  - inline JavaScript for audio handling, entity rendering, shop generation, game state, and the animation loop
- Core JavaScript pieces:
  - `AudioManager`: loads approved remote audio, unlocks audio on first interaction, plays looping background music and short UI/shop sound effects
  - `Particle`: lightweight visual burst effect used when clicking or purchasing
  - `Entity`: moving celestial body instances with wraparound movement and custom drawing rules
  - `Game`: central singleton managing state, input, shop behavior, economy, rendering, and UI updates
- Static progression data is held in `GAME_DATA`, which defines purchasable celestial objects from asteroid through universe with escalating costs and income values.
- Presentation metadata for shop badges/icons is held in `ENTITY_THEMES`.

## Game loop / state model
- The game uses a continuous `requestAnimationFrame` render loop.
- Render/update flow each frame:
  1. clear and redraw the space background
  2. animate drifting stars
  3. update and render purchased entities
  4. update and render temporary particles
  5. render an attract-mode beacon animation before the game starts
- Economy progression is driven by a separate `setInterval` ticking once per second:
  - if the game has started, money increases by `incomePerSec * incomeMultiplier`
  - HUD and shop affordability are refreshed each tick
- Main state variables:
  - `money`
  - `incomePerSec`
  - `entities`
  - `particles`
  - `stars`
  - `isRunning`
  - `shopOpen`
- Start state:
  - player sees a title card and atmospheric background
  - gameplay begins on any pointer or keyboard interaction
- Active state:
  - HUD appears
  - shop button is enabled
  - player purchases entities to increase passive income
- There is no fail state, reset loop, or explicit win screen. The game is an open-ended accumulation toy.

## Player goals
- Begin the simulation by activating the foundry.
- Spend starting credits on the cheapest celestial objects.
- Increase passive credit income over time.
- Unlock and buy increasingly large and exotic cosmic entities.
- Fill the space scene with drifting bodies while scaling toward massive late-game objects like galaxies and universes.

## Interaction pattern
- Initial interaction: tap/click/press a key to start.
- Main interaction loop:
  - open the shop via the floating planet button
  - inspect available space objects and their income rates
  - buy any item the player can afford
  - wait for passive income to accumulate
  - repeat purchases to accelerate growth
- Optional tactile interaction:
  - tapping the canvas emits particles, adding a lightweight cosmetic feedback layer
- Feedback:
  - positive purchase/start GIF appears on success
  - fail GIF and blocked sound play when funds are insufficient
  - button disabled state communicates affordability

## Core systems
- **Idle economy system**: passive income accumulates every second based on purchased objects.
- **Shop/progression ladder**: a long ordered unlock curve from minor rocks to universe-scale entities.
- **Visual collection system**: each purchase adds a visible drifting object to the starfield, turning progression into scene-building.
- **Audio feedback system**: ambient loop plus start, buy, blocked, and menu SFX.
- **Responsive mobile-first UI system**: full-screen canvas with overlaid HUD and bottom-sheet shop adapted for small screens.
- **Cosmetic feedback system**: particles, glow, GIF overlays, neon typography, and animated title emblem.

## Inferred genre / gameplay shape
- Strongest reading: a space-themed idle/clicker hybrid with shop-based passive-income progression.
- Secondary shape: a light collection/display sandbox because bought objects persist visually and populate the scene.
- The game is not action-heavy; the main mechanic is economic accumulation and incremental upgrading rather than skill challenge.
- Tone and structure suggest a casual, satisfying progression game intended for short sessions and touch devices.

## Heuristic summary
Cosmic Foundry is an incremental space economy game where the player starts with a small amount of money, opens a star catalog, and buys celestial bodies that generate passive income. Each purchase both increases production and visually expands the drifting cosmic tableau on the canvas. The result is a calm, neon, mobile-friendly idle experience centered on accumulation, escalation, and the pleasure of building a living starfield.