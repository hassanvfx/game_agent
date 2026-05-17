# Blueprint

## High-level code structure
The game is implemented as a single self-contained HTML document with inline CSS, HTML UI layers, and JavaScript logic. The structure is divided into:

- **Presentation layer**
  - Fullscreen canvas used for the drawing phase.
  - Overlay UI for HUD, tool controls, quiz screen, reaction feedback, and game-over screen.
  - Inline styles define a neon/memphis fashion-show visual identity.

- **Audio/feedback layer**
  - Two looping background music tracks: one for the design phase and one for the quiz phase.
  - Pooled sound effects for click, success, fail, and win.
  - GIF-based reaction overlay for positive/negative feedback.
  - Optional vibration bridge for mobile/webview environments.

- **Game logic layer**
  - Canvas drawing handlers for pointer input.
  - Level progression logic for two tracing rounds.
  - Quiz system with three multiple-choice fashion questions.
  - State transitions between drawing, quiz, and game-over phases.

## Game loop / state model
This is a lightweight state-driven casual game rather than a physics or entity-heavy loop.

### Primary states
- **PLAYING**
  - The player traces outfit templates on the canvas.
  - Palette selection, clear, and done actions are available.
  - Two rounds are presented sequentially.

- **QUIZ**
  - The drawing tools are hidden.
  - A modal card presents one multiple-choice question at a time.
  - Correct and incorrect answers trigger different feedback.

- **GAMEOVER**
  - Final score is shown after all quiz questions are answered.
  - The player can restart the full experience.

### Flow
1. Start in **Round 1** drawing mode.
2. Tap **Done**, then **Next**.
3. Enter **Round 2** drawing mode.
4. Tap **Done**, then **Next**.
5. Enter a **3-question quiz**.
6. Reach **game over** with score summary.
7. Restart to replay from round 1.

## Player goals
The player appears to be trying to:
- complete two fashion-themed tracing/drawing rounds,
- then answer style/fashion trivia questions,
- and finish with the best possible quiz score.

The drawing phase is expressive and guided, but the scoring emphasis is actually on quiz performance, since the final result displayed is the trivia score.

## Interaction pattern
Core interaction is simple, mobile-friendly, and touch-first:

- **Pointer/touch drawing** on canvas
- **Tap color swatches** to switch brush color
- **Tap Clear** to reset the current drawing
- **Tap Done** to lock in a design round
- **Tap Next** to proceed to the next stage
- **Tap quiz answers** to advance through trivia
- **Tap Remix Again** to restart

There is no evidence of drag-and-drop inventory, timing pressure, character movement, or simulation management.

## Core systems
### 1. Guided drawing system
- Uses a canvas for freehand drawing.
- Displays dashed outfit templates for each round.
- Supports color selection and brush size via config.
- Lets the player clear and redraw.

### 2. Round progression system
- Two predefined drawing rounds:
  - **Round 1: Meme Fit**
  - **Round 2: Viral Dress**
- Each round changes the template and instructional note.
- Completion is manual via the Done/Next buttons.

### 3. Quiz system
- Three static multiple-choice questions.
- Tracks current question and score.
- Immediately advances after an answer is selected.

### 4. Feedback system
- Success/fail reaction GIFs.
- Sound effects and background music that change by phase.
- Vibration calls for supported environments.

### 5. Restart loop
- After game over, the game resets back to round 1 with the same overall structure.

## Inferred genre / gameplay shape
The strongest gameplay shape is a **hybrid casual dress-up / drawing / quiz game** with very light progression.

It is not a deep dress-up system in the traditional item-selection sense. Instead, it behaves like:
- a **guided fashion sketch activity**, followed by
- a **short fashion trivia quiz**.

So the practical genre feel is:
- casual,
- kid-friendly,
- session-based,
- mobile-oriented,
- fashion-themed,
- creativity plus trivia.

## Heuristic summary
The game presents itself as a runway-fashion mini experience where the player first “creates” meme-inspired outfits by tracing silhouettes and selecting colors, then proves style knowledge through a short quiz. The code suggests a lightweight, arcade-like loop focused on fast completion, visual flair, and simple positive/negative feedback rather than meaningful drawing evaluation or deep customization.