# Blueprint

## High-level code structure
The game is implemented as a single self-contained HTML document with three main layers:

1. **Presentation layer**
   - Inline CSS defines a neon sci-fi visual identity, responsive HUD, overlay cards, and animated feedback elements.
   - The DOM includes:
     - a full-screen canvas for board rendering
     - a start overlay
     - a game-over overlay
     - a compact HUD with turn indicator and dice button
     - two floating GIF feedback elements for capture and victory moments

2. **Asset/config layer**
   - A top-level `ASSETS` object stores remote audio and GIF URLs.
   - Color constants, player order, board geometry, and player definitions are all hard-coded in JavaScript.

3. **Game logic/runtime layer**
   - `AudioController` manages background music, victory loop, and per-event sound effects.
   - Board state is represented with track arrays and per-player token arrays.
   - Input is handled through:
     - a dice roll button
     - pointer selection on the canvas for choosing which token to move
   - Rendering is done in a persistent `requestAnimationFrame` loop.

## Game loop / state model
The runtime follows a lightweight turn-state model rather than a physics simulation loop.

### Core state flags
- `gameActive`: whether a race is currently in progress
- `turnIndex`: whose turn it is among red, green, yellow, blue
- `diceValue`: current rolled number
- `waitingForRoll`: whether the active player must roll
- `waitingForMove`: whether the active player must choose a token to move

### Token state encoding
Each token uses a numeric position model:
- `-1`: token is still in its home/base
- `0..50`: token is on the shared outer ring track
- `51..56`: token is in its final home lane
- `56`: token has fully reached home

### Turn flow
1. Active player is shown in the HUD.
2. Player presses the dice button.
3. Dice animates through random values, then resolves to `1..6`.
4. If at least one token can legally move:
   - the player taps a highlighted token on the board
   - that token advances
5. If no token can move:
   - a fail sound plays
   - turn passes automatically
6. If the roll was not a 6, turn advances to the next color.
7. If all four tokens of one color reach home, the game ends and winner UI is shown.

### Rendering model
The `gameLoop()` continuously:
- clears the canvas
- draws drifting ambient particles
- draws the board
- draws all tokens
- adds pulsing highlight rings around valid movable tokens during move selection

## Player goals
The player does not control a single avatar; instead, the players take turns controlling one color team in a four-color race. The inferred objective is:

- roll the die
- bring tokens out of base with a 6
- move all four tokens around the ring
- enter the home lane exactly within limits
- send opponents back to base by landing on them outside safe entry squares
- be the first color to bring all four tokens home

## Interaction pattern
The interaction pattern is simple, mobile-friendly, and turn-based:

- **Start interaction:** tap “Start Race”
- **Main action 1:** tap the dice button to roll
- **Main action 2:** tap one of the currently valid tokens on the canvas
- **Restart interaction:** tap “Race Again”

The game supports pointer/touch input and is clearly intended for quick casual play on phones or tablets as well as desktop.

## Core systems
### 1. Board/path system
- A fixed 15×15 board is rendered on canvas.
- The main ring path is encoded as a 52-cell coordinate array.
- Each player has:
  - a colored base quadrant
  - a unique start index on the ring
  - a six-cell home path

### 2. Turn management system
- Four-player color rotation in fixed order
- Extra-turn behavior on rolling a 6
- Skip-turn behavior when no legal move exists

### 3. Token movement system
- Tokens leave base only on a 6
- Tokens progress numerically rather than via object-heavy pathfinding
- Legal move checks prevent overshooting the final destination

### 4. Capture/combat-lite system
- Landing on an opposing token on the shared track captures it
- Captured tokens return to base (`-1`)
- Four start/safe squares are protected from capture

### 5. Win condition system
- A player wins only when all four tokens reach final home state `56`

### 6. Feedback system
- Sound effects for start, roll, move, fail, capture, and win
- Background loop during active play
- Victory loop after a winner is declared
- Reaction GIFs for capture and victory
- Glowing token highlights and polished HUD indicators

## Inferred genre / gameplay shape
This is best understood as a **digital Ludo-style board race game** presented with a neon arcade wrapper.

### Genre reading
- Primary shape: turn-based board race
- Secondary shape: casual multiplayer-style family board game adaptation
- Presentation flavor: futuristic neon arcade / cosmic relay theme

### Gameplay heuristic
The game is less about dexterity and more about:
- turn timing
- choosing the best token to advance
- deciding between racing forward, unlocking new tokens, or setting up captures
- managing risk around safe and unsafe spaces
- leveraging bonus turns from rolling 6s

### Distinguishing identity
What makes this implementation feel specific:
- it reframes a Ludo-like game as “Color Relay”
- it uses a polished sci-fi neon aesthetic instead of a traditional tabletop look
- it emphasizes quick taps, readable mobile UI, and celebratory audiovisual feedback
- it appears designed as a lightweight solo/local pass-and-play casual experience rather than a networked competitive game