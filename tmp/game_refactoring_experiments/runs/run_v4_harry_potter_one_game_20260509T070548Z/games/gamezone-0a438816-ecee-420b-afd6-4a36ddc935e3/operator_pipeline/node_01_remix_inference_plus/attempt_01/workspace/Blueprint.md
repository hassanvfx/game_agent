# Blueprint

## Current game reality

### High-level code structure
- `index.html` provides a single-screen canvas arcade game with HUD, start screen, and game-over screen.
- `assets/obfuscated/inline-script-001.js` contains the full game loop, entity model, drag interaction handling, HUD updates, particle effects, and lightweight audio wrapper.
- `assets/obfuscated/inline-script-002.js` provides safe browser audio fallbacks/stubs.
- `assets/obfuscated/inline-style-001.css` styles the menu, HUD, overlays, and canvas presentation.

### Genre / gameplay shape
- One-screen arcade reflex game
- Drag-and-remove hazard clearing game
- Touch-first / mouse-compatible casual action loop

### Core player goal
Remove incoming bugs quickly enough to keep the health/pulse meter from draining to zero.

### Interaction pattern
- Start from a menu card
- During play, bugs spawn on top of a large foot illustration
- Player presses/touches a bug and drags it away from its origin
- If dragged far enough, the bug is cleared
- If bugs remain alive long enough, health drains continuously
- Game ends when health reaches zero

### Core systems
- Spawn timer that accelerates with rising difficulty
- Entity list of bugs with per-frame update/draw methods
- Drag state with pointer/touch tracking
- Health bar and score display
- Particle burst feedback on successful clears
- Reaction cards for success/danger/failure
- Start screen and game-over screen
- Optional audio hooks, currently empty in the source implementation

### Game loop / state model
- `State.active` gates gameplay
- `requestAnimationFrame(loop)` drives updates and rendering
- Difficulty slowly rises over time
- Spawn cadence shortens as difficulty rises
- Bugs become damaging after surviving for about 2 seconds
- Health drains while overdue bugs remain on screen
- Clearing a bug increases score and restores health
- Reaching zero health transitions to game over

### Camera / viewport assumptions
- Full-viewport canvas
- Static single camera
- No scrolling world
- Playfield centered around a large foot silhouette

### Input model
- Mouse and touch supported
- Start/restart via buttons
- Main play verb is press/drag/release
- No keyboard dependence

### Screen states likely present
- Start screen
- Active play screen
- Game over screen

### Progression currently implemented
- Endless survival escalation via spawn-rate pressure and accumulating bug count
- No explicit level selection, rounds, or stage transitions

## Remix-direction summary: Harry Potter trajectory

The safest Harry Potter remix is **not** to rewrite mechanics into spell dueling or broom flight. The existing mechanic is already a strong fit for:
- magical pest removal
- wand-guided flick gestures
- Hogwarts environment pressure
- escalating infestation fantasy

### Recommended remixed identity
Reframe the game as a magical cleanup defense challenge:
- Bugs become cursed magical pests / enchanted beetles / Cornish-pixie-adjacent scuttlers
- The foot/stage area becomes a wizarding surface such as a Hogwarts corridor, classroom floor, or forbidden-library aisle focal zone
- Dragging becomes a wand-guided banishing flick
- Health becomes magical ward integrity / castle calm / corridor protection
- Score becomes pests banished

### Why this direction is safe
It preserves:
- drag-to-remove semantics
- endless hazard spawning
- health drain when hazards remain too long
- score on successful removal
- start/game-over flow
- mobile actionability
- single-screen arcade structure

It only changes:
- theme framing
- copy
- visual identity
- procedural art motifs
- HUD language
- audiovisual styling
- optional safe level framing for later stages

## Preserve vs change guidance

### Preserve strictly
- Drag interaction semantics
- Clear threshold distance
- Spawn timing logic
- Difficulty ramp logic
- Health drain logic
- Score accumulation semantics
- Fail condition at zero health
- One-screen mobile-first play
- RequestAnimationFrame loop structure
- Entity collision/contact behavior as currently implied by selection radius

### Safe to transform
- Title, labels, and narrative framing
- Bug appearance and naming
- Background and environment art
- HUD styling and bar framing
- Pointer/tweezer representation into wand spell beam framing
- Particle colors and magical burst language
- Start and game-over copy
- Reaction text
- Level/world framing for a five-level downstream plan
- Audio mapping if approved remote media is later selected from catalogs

### Tiny safe repairs only if needed downstream
- Clarify text labels
- Improve readability of HUD/menu
- Improve pointer feedback
- Improve background/world layering
- Improve low-health warning legibility
- Wire approved audio URLs into existing empty media slots without changing triggers

### Must not be overinterpreted
- Do not convert to a combat game
- Do not add aiming/projectile combat that changes input semantics
- Do not replace drag-removal with tapping, keyboard casting, or lane-based movement
- Do not introduce heavy multi-scene adventure logic
- Do not change score/health rules to fit lore
- Do not rewrite the rendering architecture

## Mechanic complexity snapshot
- Complexity level: simple one-screen arcade with timing pressure
- Real difficulty sources: spawn density, delay before clearing, screen management, target acquisition under pressure
- Fake difficulty to avoid: cluttered VFX, tiny touch targets, lore-heavy modal interruptions, low-contrast wizarding decoration

## Downstream implementation heuristic
Later stages should present the game as a recognizable wizarding pest-banishing challenge with a five-level Hogwarts journey, while leaving the protected arcade loop intact.

## Intended remixed trajectory
**Source reality:** neon bug-dragging survival game over a foot illustration.  
**Target remix:** a Harry Potter-inspired magical pest banishing game where the player uses wand-like drag gestures to clear cursed critters from iconic wizarding school spaces, with five escalating world beats built through safe presentation and progression framing.