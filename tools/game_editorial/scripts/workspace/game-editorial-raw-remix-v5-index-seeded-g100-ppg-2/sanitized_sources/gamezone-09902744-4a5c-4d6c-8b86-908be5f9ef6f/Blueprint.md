# Blueprint: Signal Shift

## High-level code structure
The game is implemented as a single self-contained `index.html` file with three layers:

1. **HTML shell**
   - A full-screen `<canvas>` used for all core gameplay rendering.
   - A decorative overlay layer for floating danmaku text and ambient screen effects.
   - UI helper elements for toast notifications, a first-interaction audio hint, and two reaction GIFs.
   - Audio elements for looping background ambience/music and short UI/gameplay sound effects.

2. **Embedded CSS**
   - Defines a neon sci-fi visual style with dark gradients, glowing panels, holographic grid lines, and floating overlay effects.
   - Styles small HTML-based feedback elements that sit over the canvas.

3. **Embedded JavaScript game logic**
   - Initializes and resizes the board.
   - Creates and maintains a 6x8 match-3 grid.
   - Handles pointer input, swapping, matching, scoring, cascades, countdown timing, restart flow, and all rendering.
   - Uses a small state object plus async animation helpers to sequence board resolution.

## Game loop / state model
The runtime uses a lightweight animation-frame loop.

### Core state
The central `state` object tracks:
- `grid`: 2D array of tile objects
- `selected`: currently selected cell
- `pointerDownCell`: drag-start cell for swipe swapping
- `score`: accumulated points
- `timeLeft`: countdown from 60 seconds
- `comboChain`: declared but not meaningfully used as persistent state
- `lastTs`: previous frame timestamp
- `resolving`: whether swaps/cascades are currently animating
- `gameOver`: whether the timed run has ended

### Frame loop
`tick()` runs on `requestAnimationFrame` and:
- computes delta time
- decreases the timer while the match is active
- flips to game-over state when time reaches zero
- renders HUD, board, tiles, selection highlight, and game-over overlay

### Board lifecycle
1. Board is seeded with random tiles while avoiding immediate starting matches.
2. Player selects or drags between adjacent cells.
3. A swap is animated.
4. If no match is formed, the move is rejected and swapped back.
5. If a match is formed:
   - matched cells are found
   - score is awarded
   - matched tiles fade/shrink away
   - columns collapse downward
   - new tiles spawn from above
   - chain reactions continue until no matches remain

## Player goals
The player is trying to:
- create adjacent-tile swaps that form lines of 3 or more matching symbols
- maximize score within a 60-second timed run
- trigger cascades and chain combos for better scoring and stronger feedback
- keep making valid links quickly before the signal timer expires

The game does **not** appear to have level progression, win states, unlocks, or puzzle objectives beyond score-chasing within the timer.

## Interaction pattern
The interaction model is direct and touch-friendly:
- **Tap a tile, then tap an adjacent tile** to swap
- **Press and drag from one tile into an adjacent tile** to swap by gesture
- **Tap after game over** to immediately restart the timed session
- **First pointer interaction** also unlocks audio playback

This is designed for mobile-first play:
- full-screen canvas
- disabled text selection/tap highlight
- safe-area aware UI positioning
- no keyboard dependency

## Core systems
### 1. Match-3 board system
- 6 columns by 8 rows
- six tile types
- horizontal and vertical 3+ matching detection
- starting board avoids accidental auto-matches at creation

### 2. Swap validation
- only orthogonally adjacent swaps are allowed
- swaps that do not create any match are reverted

### 3. Cascade resolution
- clears all matched cells
- collapses tiles downward per column
- spawns new random tiles
- repeats until stable
- supports combo chains through repeated resolution passes

### 4. Scoring system
- base score depends on match length
- 4-in-a-row gives a higher multiplier
- 5+ gives an even larger multiplier
- later cascade chains multiply total gain further

### 5. Time-pressure session loop
- one round lasts 60 seconds
- HUD shows score and remaining time
- the round ends automatically when the timer empties
- restart is immediate and frictionless

### 6. Feedback / juice system
The game leans heavily on stylish reactive feedback:
- toast popups for score/combo/failure messages
- reaction GIFs for combos and failed actions
- floating danmaku-style praise text on bigger chains
- layered audio with ambience plus swap/collect/combo/fail/game-over cues
- glowing animated tiles and pulsing cores
- sci-fi language framing score as “signal” and time as “uplink”

## Inferred genre / gameplay shape
**Primary genre shape:** timed match-3 puzzle game  
**Secondary feel:** arcade score-attack puzzle game with a cyber-neon streaming/terminal presentation

It is not level-based, narrative-based, or progression-heavy. The experience is closest to a fast arcade mode where the player chases score and spectacle in a one-minute session.

## Presentation and theme heuristic
The game wraps standard match-3 rules in a futuristic “signal routing” fiction:
- title: **Signal Shift**
- score is framed as signal/data
- failure is framed as signal loss or a closed uplink window
- tiles use emoji-like techno mascots and devices (robot, alien, satellite, battery, crystal, spark)
- visual language suggests an arcade console / cyber control deck / holographic network terminal

## Confidence notes
High confidence:
- timed match-3 identity
- swipe/tap swap interaction
- score-attack structure
- combo/cascade emphasis
- mobile-friendly single-screen design

Moderate confidence:
- thematic fiction is mostly cosmetic rather than mechanical
- “signal routing” is the intended fantasy wrapper rather than a literal systems puzzle premise

Low confidence:
- no evidence of deeper progression, unlocks, or meta systems beyond a replay loop