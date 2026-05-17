# Blueprint

## High-level code structure
- **Single-file HTML game**: `index.html` contains markup, embedded CSS, configuration data, audio elements, UI overlays, and all gameplay logic.
- **Canvas-first presentation**: the Sudoku board, keypad, highlights, particles, and animated backdrop are rendered on a full-screen `<canvas>`.
- **DOM-assisted HUD/UI**: timer, mistake counter, title badge, result modal, restart button, audio tags, and GIF feedback overlays are normal DOM elements layered over the canvas.
- **Config-driven startup**: a JSON config block defines difficulty, accent/theme color, and mistake limit, then gets parsed at boot into runtime state.
- **Light state machine**: runtime is organized around a small set of states (`BOOT`, `PLAYING`, `GAMEOVER`) with dedicated initialization, input, rendering, and end-screen behavior.

## Game loop / state model
- On `DOMContentLoaded`, the game:
  - parses config,
  - sizes the canvas,
  - builds responsive layout zones,
  - wires pointer input and restart behavior,
  - initializes a new Sudoku puzzle,
  - enters `PLAYING`,
  - starts the animation loop.
- The animation loop:
  - computes delta time,
  - updates the timer while playing,
  - decays screen shake,
  - redraws backdrop, board, keypad, and particles every frame.
- State transitions:
  - `BOOT` -> `PLAYING` during startup,
  - `PLAYING` -> `GAMEOVER` after either puzzle completion or reaching the mistake cap,
  - restart returns to a fresh `PLAYING` run.

## Player goals
- Solve a generated 9x9 Sudoku grid by filling every empty cell with its correct value.
- Avoid exceeding the strike limit while completing the board.
- Finish quickly for a cleaner run, with completion time shown on the win screen.

## Interaction pattern
- Tap/click a cell to select it.
- If the cell is editable, tap/click an on-screen two-row number pad to enter digits 1-9 or clear with `X`.
- Correct entries lock in visually with glow/particles.
- Incorrect entries still place the attempted digit, mark it as an error, and consume one mistake.
- The game is designed for pointer-based play and appears intentionally mobile-safe, with touch suppression and responsive layout calculations.

## Core systems
- **Sudoku generation and solving**
  - Generates a full valid board by filling diagonal boxes and solving recursively.
  - Removes values according to the configured difficulty to create the puzzle.
  - Stores both current value and solution per cell.
- **Board state**
  - Each cell tracks `val`, `solution`, `isFixed`, `isError`, and `animScale`.
  - Selection is tracked by a single `selectedIndex`.
- **Validation / fail-win rules**
  - Correct number: updates cell, clears error state, triggers feedback, then checks for win.
  - Wrong number: marks the cell as erroneous, increments mistakes, triggers shake/error feedback, and can cause loss.
  - Win occurs only when every cell matches its solution.
- **Responsive layout model**
  - One layout calculator defines both draw regions and hit-testing zones for the grid and keypad.
  - This keeps interaction aligned with rendering across screen sizes.
- **Feedback systems**
  - HUD timer and strike counter,
  - particle bursts on correct placement,
  - camera shake on mistakes,
  - ambient loop plus UI/correct/error/win/game-over sounds,
  - GIF overlays for burst and end-state reactions,
  - vibration hooks for supported devices.
- **Presentation layer**
  - Futuristic “zen neon” theme with Audiowide/Rajdhani typography, glowing grid lines, glassmorphism HUD panels, and meditative sci-fi copy.

## Inferred genre / gameplay shape
- Primary genre: **Sudoku / number puzzle game**
- Delivery style: **mobile-friendly arcade-puzzle wrapper**
- The game presents classic Sudoku logic through a polished neon relaxation-meets-arcade skin, using audiovisual reinforcement and a mistake-limit failure condition to make it feel more game-like than a plain puzzle app.

## Gameplay heuristic
- The intended rhythm is:
  1. scan the board,
  2. select an empty square,
  3. place a number from the keypad,
  4. get immediate audiovisual confirmation or punishment,
  5. gradually stabilize the whole grid before mistakes run out.
- The design encourages short, focused sessions with low-friction restarts.
- Although branded as “Zen,” the mistake cap and shake/error responses add tension, producing a calm-on-the-surface but performance-oriented puzzle loop.
