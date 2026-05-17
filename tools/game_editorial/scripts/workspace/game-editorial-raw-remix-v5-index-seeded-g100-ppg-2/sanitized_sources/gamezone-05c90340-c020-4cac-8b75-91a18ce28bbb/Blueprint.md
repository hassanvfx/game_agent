# Blueprint

## High-level code structure
The game is implemented as a single self-contained `index.html` document with three main layers:

1. **Presentation layer**
   - Inline CSS defines a sci-fi neon visual theme, glass HUD panels, start/game-over overlays, animated feedback badges, and responsive mobile-safe layout.
   - A full-screen `<canvas>` is used for all board and token rendering.
   - DOM UI elements handle the HUD, dice display, start/restart buttons, turn label, and reaction GIF feedback.

2. **Asset and feedback layer**
   - A small `ASSETS` object defines remote audio and GIF resources.
   - `AudioController` manages BGM, victory music, one-shot sound effects, loop switching, and a simple cooldown system for repeated sounds.
   - Feedback helpers update a status badge and temporary reaction GIFs for captures and blocked turns.

3. **Game logic and render loop**
   - Global state variables track turn ownership, dice value, token data, animation lockouts, board sizing, and whether the loop has started.
   - Logical path arrays (`MAIN_PATH`, `RED_HOME_PATH`, `BLUE_HOME_PATH`) define the board traversal model.
   - Gameplay functions handle move validation, rolling, token movement, collisions, win checks, turn switching, simple bot behavior, and board/token drawing.
   - A continuous `requestAnimationFrame` loop redraws the board and token state.

## Game loop / state model
The game uses a straightforward stateful turn loop rather than a physics simulation.

### Core state
- `gameActive`: whether a match is currently running
- `currentTurn`: `0` for the human red side, `1` for the blue AI
- `diceValue`: the resolved roll for the active turn
- `isDiceRolled`: whether the current player has already rolled
- `tokens`: eight token objects total, four per side
- `animating`: temporary interaction lock while moves resolve
- `gameLoopStarted`: ensures the canvas render loop starts only once

### Token state model
Each token has:
- `player`: red human or blue AI
- `state`: `HOME`, `TRACK`, `HOME_STRETCH`, or `FINISHED`
- `pos`: logical progress index within the current state path
- `x`, `y`: board coordinates derived from state and path position

### Turn flow
1. Player starts match from overlay.
2. Human turn begins with the dice enabled.
3. Human clicks the dice to roll.
4. If at least one legal move exists, the player clicks a highlighted red token to move it.
5. If no legal move exists, the turn auto-passes after blocked feedback.
6. Rolling a 6 grants an extra turn.
7. After the human turn ends, the blue AI rolls automatically.
8. The bot chooses randomly among valid moves.
9. The cycle continues until one side gets all four tokens to the finish.

## Player goals
The player controls the **red squad** and aims to:
- launch all four tokens from home by rolling 6s
- move tokens around the shared loop path
- send opposing blue tokens back home by landing on them
- enter the red home stretch at the end of the route
- finish all four tokens at the center before the blue AI does

## Interaction pattern
The game is a light turn-based board interaction model:
- click/tap **Start Mission** to begin
- click/tap the large center HUD die on the player's turn
- click/tap one of the player's valid red tokens on the board to apply the move
- restart from the game-over screen when the race is finished

The board itself is the main interaction surface. The game clearly highlights selectable human tokens, and the AI acts automatically without direct player input.

## Core systems
### 1. Dice and turn control
The die drives legal movement and governs turn transitions. A 6 is required to leave home, and also grants another turn after movement.

### 2. Token routing system
Tokens move through:
- a shared 52-step outer loop
- a player-specific home stretch
- a final center finish state

Blue tokens use the same loop but enter with an offset start position, mirroring standard two-sided Ludo routing logic.

### 3. Collision / capture system
If a moved token lands on an opponent occupying the same active track cell, the opposing token is reset to `HOME`. This is a major tactical pressure point.

### 4. Win condition system
A side wins when all four of its tokens reach `FINISHED`. The result overlay, victory audio loop, and winner text are then shown.

### 5. AI opponent system
The blue side is controlled by a minimal bot:
- auto-rolls when its turn begins
- checks legal moves
- randomly selects one valid token to move
This suggests casual accessibility rather than deep strategy AI.

### 6. Audio and feedback system
The game emphasizes arcade feel through:
- looping background music
- separate victory loop
- roll, move, start, blocked, capture, and win SFX
- text badge feedback for move outcomes
- animated GIF reactions for successful captures and blocked/no-move moments

### 7. Canvas presentation system
The board is redrawn every frame with:
- a starfield background
- a stylized 15x15 Ludo-like board
- colored home quadrants
- central triangular goal area
- glossy cartoon pilot tokens
- responsive scaling based on viewport size

## Inferred genre / gameplay shape
This is best described as a **casual two-side Ludo board game reskinned as a neon sci-fi race duel**.

It preserves classic Ludo structure:
- dice-gated token deployment
- looping shared path
- captures that return opponents home
- home stretch and exact finishing progression

But the presentation reframes it as:
- a space race
- red pilot squad versus blue AI core
- “launch,” “orbit,” and “mission” themed feedback
- arcade UI polish instead of a traditional tabletop look

## Gameplay heuristic
The moment-to-moment play heuristic appears to be:

- **roll for deployment first** when pieces are still in base
- **advance active tokens steadily** to create finish pressure
- **capitalize on captures** when available, since resets are powerful
- **use extra turns from 6s** to accelerate launches or progress
- **balance spreading tokens vs. finishing them**, though the game’s simple ruleset and random AI keep it lightweight

Because the AI is random, the intended feel is likely not hard strategy but a fast, readable, family-friendly arcade board match with satisfying audiovisual feedback.

## Confidence notes
Confidence is high that the game is a Ludo-derived race game rather than an original board system because:
- the board is 15x15
- the path lengths and home-stretch logic map closely to Ludo
- leaving home requires a roll of 6
- captures send enemies back home
- four tokens per side race to finish

Confidence is moderate on intended thematic interpretation beyond “space/orbit race,” since the theme is mostly conveyed through UI copy, token styling, audio/FX choices, and palette rather than deeper narrative systems.