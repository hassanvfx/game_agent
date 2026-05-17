# Blueprint

## High-level code structure
This game is implemented as a single self-contained HTML document with three main layers:

1. **Presentation layer**
   - Inline CSS defines a sci-fi neon visual theme, glassmorphism menu cards, HUD pills, feedback toasts, and responsive layout rules.
   - The DOM provides menu screens, level select, HUD, pause/game-over modal, hidden audio elements, and lightweight configuration data.

2. **Simulation / puzzle logic**
   - `Random` provides deterministic seeded randomness.
   - `SudokuGenerator` generates a full 9x9 Sudoku solution and removes numbers according to difficulty to create a playable puzzle.
   - Seed generation is based on difficulty plus level number, so each level is reproducible.

3. **Runtime controller / renderer**
   - `AudioManager` manages BGM/SFX, browser audio unlocking, cooldowns, and synthesized fallback sounds.
   - A single global `app` object holds game state, input handling, layout calculations, UI transitions, timer logic, win/loss evaluation, particle effects, and all canvas drawing.

The game mixes DOM UI for meta screens with a canvas-rendered board and numpad for play.

## Game loop / state model
The state model is explicit and simple:

- `MENU`
- `LEVEL_SELECT`
- `GAME`
- `PAUSED`

### Flow
- The player lands on the main menu and chooses a difficulty.
- The game shows a level-select screen for that difficulty.
- Choosing a level generates a deterministic Sudoku puzzle and enters gameplay.
- During gameplay:
  - a timer increments once per second,
  - the canvas loop continuously redraws the board, selection state, numpad, and particles,
  - pointer input selects cells and enters numbers.
- The player can pause at any time.
- The run ends in one of two terminal states:
  - **win:** all empty cells are correctly filled,
  - **loss:** the player reaches 3 mistakes ("glitches").

Although the render loop runs with `requestAnimationFrame`, the underlying puzzle is turn-based rather than action-heavy.

## Player goals
Primary player goal:
- Complete the 9x9 Sudoku board correctly.

Secondary goals:
- Finish with fewer than 3 mistakes.
- Clear selected sectors/levels across easy, medium, and hard sets.
- Likely improve completion speed, since a visible timer tracks elapsed time.

## Interaction pattern
The interaction model is pointer/touch-first and highly mobile-aware:

- Tap a grid cell to select it.
- Tap a number on the bottom canvas numpad to place a value.
- Correct placements fill the board permanently.
- Incorrect placements increase the error counter and add screen shake / failure feedback.
- Menu, pause, resume, retry, and level selection are button-driven via DOM UI.

There is no drag, movement, or freeform control. The experience is discrete, readable, and puzzle-oriented.

## Core systems
### 1. Deterministic puzzle generation
- A seeded generator ensures each difficulty/level combination always produces the same board.
- Difficulty affects puzzle density via the number of removed cells:
  - easy: 30 holes
  - medium: 42 holes
  - hard: 54 holes

### 2. Sudoku validation through answer matching
- The game does not validate arbitrary legal candidate placement in a sandbox sense.
- Instead, each placement is checked directly against the precomputed solution grid.
- A correct match fills the cell.
- A wrong match counts as a mistake immediately.

### 3. Failure-pressure system
- The player has a 3-error limit.
- Wrong answers trigger:
  - error counter increase,
  - shake effect,
  - fail sound,
  - fail feedback card,
  - eventual run loss if the cap is reached.

This makes the game feel more like a level-based challenge run than a relaxed endless Sudoku board.

### 4. Progression and persistence
- The game is structured into difficulty bands and level lists:
  - Easy: 10 levels
  - Medium: 10 levels
  - Hard: 25 levels
- Completed levels are stored in `localStorage` under `sudoku_progress`.
- The level-select screen visually marks completed sectors.

### 5. Presentation feedback
- Correct placements spawn particles.
- Wins trigger confetti and a success toast.
- Losses trigger a failure toast.
- The UI language reframes Sudoku as a futuristic “orbit/sector stabilization” mission.

### 6. Audio system
- Menu, pause, resume, place, fail, and win all have dedicated audio cues.
- Background music plays during puzzle runs.
- Audio is unlocked on first interaction to satisfy browser autoplay restrictions.

## Inferred genre / gameplay shape
Strongest genre inference:
- **Sudoku / number puzzle game**

Broader gameplay shape:
- **Level-based mobile puzzle game** with arcade-style failure states and sci-fi skinning.

It is not a traditional open-ended Sudoku app because:
- it has explicit level progression,
- it uses win/loss states,
- it has a strict 3-mistake cap,
- it emphasizes presentation and run structure over free puzzle note-taking.

## Gameplay heuristic
The intended player loop appears to be:

1. Choose a difficulty.
2. Pick a sector/level.
3. Scan the Sudoku board visually.
4. Tap a cell and commit a number from the bottom numpad.
5. Avoid mistakes because errors are capped at three.
6. Finish the board to stabilize the sector.
7. Unlock a sense of mastery through faster clears and higher-difficulty sectors.

The experience is designed to make Sudoku feel brisk, gamified, and accessible on touch devices rather than meditative or feature-dense.

## Confidence notes
High confidence:
- The game is fundamentally a Sudoku puzzle game with deterministic level generation.
- The interaction model is cell selection plus numpad entry.
- The structure is menu → difficulty → level → run → win/loss.

Moderate confidence:
- Speed/challenge orientation is part of the intended feel because of the timer, mistake cap, and celebratory feedback, though there is no explicit star-rating or leaderboard system.
- The "orbit" framing is cosmetic/thematic rather than mechanically transformative.