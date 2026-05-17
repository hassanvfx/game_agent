# Blueprint

## High-level code structure
The game is implemented as a single self-contained HTML document with embedded CSS and JavaScript. Its structure is divided into four main layers:

1. **Presentation layer**
   - Inline CSS defines a neon arcade visual identity, responsive layout rules, glassmorphism panels, animated reactions, and button states.
   - HTML contains a fixed full-screen canvas for ambient particle effects plus a UI overlay for menus, HUD, question prompts, and end screens.

2. **Audio system**
   - `AudioManager` manages background music, sound effect loading, Web Audio API playback, user-gesture unlock behavior, and synthesized fallback sounds when remote assets fail.

3. **Question/content system**
   - `QuestionBank` procedurally produces quiz prompts from three mini-pools:
     - arithmetic
     - world capitals
     - simple logic/pattern recognition
   - `generateQuestion()` randomly selects one of these categories each round.

4. **Game/state system**
   - Global runtime variables track `gameState`, `score`, `currentQuestion`, particles, and timed UI reactions.
   - Core flow functions include `startGame()`, `nextQuestion()`, `handleAnswer()`, `endGame()`, and the perpetual `loop()` for background/confetti rendering.

## Game loop / state model
The title does not use a physics-heavy gameplay loop; instead it mixes a standard animation loop with a turn-based quiz state machine.

### Runtime states
- **START**: title card is shown, player can begin a run
- **PLAY**: HUD and question card are active, answer buttons are interactive
- **WIN**: target streak reached, trophy screen shown, celebratory confetti repeats
- **LOSE**: wrong answer ends the run immediately and shows retry screen

### Loop model
- `requestAnimationFrame(loop)` runs continuously.
- Each frame:
  - clears the canvas
  - updates ambient floating particles and temporary confetti
  - renders the current visual effects
- Separate event-driven transitions control quiz progression:
  - start button begins the run
  - answering correctly advances to the next generated question after a short delay
  - answering incorrectly ends the run after feedback is shown
  - reaching the configured target score triggers a win state

## Player goals
The player’s immediate objective is to answer the current multiple-choice prompt correctly.

The larger goal is to build a **perfect streak** until reaching the configured target score. The run appears to require consecutive correct answers because any wrong answer instantly ends the session. This makes the game feel more like an arcade challenge than a relaxed trivia quiz.

## Interaction pattern
- Primary interaction is **single-tap / single-click answer selection**
- There are no movement controls, drag actions, or typing inputs during play
- Flow is:
  1. Start run
  2. Read category and prompt
  3. Tap one of four answer buttons
  4. Receive immediate audio/visual feedback
  5. Continue or fail based on correctness
  6. Restart after win or loss

The UI is optimized for quick mobile-friendly tapping with large buttons, locked viewport scaling, and simple one-screen decisions.

## Core systems
### 1. Quiz generation
The game synthesizes endless lightweight trivia from predefined templates rather than storing a linear question set. This supports replayability with low content complexity.

### 2. Streak progression
Progress is represented as a score/streak meter from `0` to `targetScore`. This is the main progression axis and victory condition.

### 3. Instant fail condition
A single wrong answer ends the run. This is one of the defining mechanics and shapes the arcade pressure.

### 4. Feedback system
Correct answers trigger:
- green button highlight
- success sound
- celebratory GIF card
- localized confetti burst

Wrong answers trigger:
- red button highlight
- wrong-answer sound
- fail GIF card
- screen shake
- reveal of the correct answer
- delayed transition to lose screen

### 5. Ambient visual effects
A canvas-based particle field runs behind the interface to maintain motion even though gameplay is menu/card driven. Additional confetti effects intensify successful moments and the win screen.

### 6. Configurability
A small embedded config block exposes:
- game title
- theme color
- target score

This suggests the game was built as a lightweight reskinnable template.

## Inferred genre / gameplay shape
The strongest reading is:

- **Primary genre:** quiz game / arcade trivia challenge
- **Secondary feel:** score-attack streak game
- **Session shape:** short-run, restart-heavy, casual browser game
- **Skill emphasis:** quick recall, pattern spotting, avoiding mistakes under light pressure

This is not a deep narrative or educational simulator. It is a compact arcade quiz loop presented with flashy cyber/retro aesthetics, short runs, and binary success/failure outcomes.

## Gameplay heuristic
A player is expected to:
- start a fresh run
- rapidly answer a rotating mix of simple knowledge and logic questions
- protect a growing streak
- avoid the single mistake that resets the attempt
- chase the trophy by hitting the exact target score

The emotional arc is:
- anticipation on start screen
- fast focus during prompt solving
- burst reward on each correct answer
- sudden collapse on a miss
- celebratory payoff on a perfect clear

## Inference confidence
Confidence is **high** for:
- overall quiz structure
- state model
- streak-based win/loss flow
- arcade presentation
- mobile/casual interaction style

Confidence is **moderate** for:
- intended audience nuances
- whether “in a row” is purely thematic or the only scoring model, though code strongly indicates instant failure on any miss and therefore effectively enforces a perfect streak.