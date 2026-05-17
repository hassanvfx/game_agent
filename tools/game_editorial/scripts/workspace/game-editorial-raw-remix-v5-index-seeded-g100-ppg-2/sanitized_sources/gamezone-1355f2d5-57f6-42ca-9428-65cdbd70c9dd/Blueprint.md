# Blueprint

## High-level code structure
The game is implemented as a single self-contained HTML document with four main layers:

1. **Presentation / layout**
   - Inline CSS defines the neon-stream visual identity, HUD glass panels, reaction cards, game-over modal, and responsive mobile-friendly layout.
   - The main playfield is a full-screen `<canvas>`.

2. **DOM-driven UI**
   - HUD elements display score as **Verified Fans** and health as a percentage meter.
   - A controls hint shows the left/right input mapping with heart and block symbols.
   - A game-over overlay shows the final score and a restart button.
   - Reaction cards briefly appear for success and failure feedback.

3. **Game runtime logic**
   - Global state variables track `gameState`, `score`, `life`, `spawnTimer`, `difficultyMultiplier`, active `bubbles`, active `particles`, and screen shake.
   - A `Bubble` class represents the falling chat/message targets.
   - A `Particle` class represents simple emoji burst feedback.

4. **Systems support**
   - Pointer input maps screen halves to actions.
   - Audio playback combines HTML audio elements with oscillator fallbacks.
   - Resize handling keeps the canvas fitted to the viewport.
   - A `requestAnimationFrame` loop drives update/draw behavior.

## Game loop / state model
The state model is very small and arcade-like:

- `BOOT`
- `PLAYING`
- `GAMEOVER`

### Loop flow
Every animation frame:

1. Compute delta time.
2. If state is `PLAYING`:
   - advance spawn timer
   - spawn new bubbles at an increasing rate
   - move all active bubbles downward
   - penalize missed bubbles when they leave the screen
   - update particles
   - decay screen shake
3. Draw the background, lane tinting, center divider, bubbles, and particles.
4. Request the next frame.

### Difficulty model
Difficulty increases continuously through `difficultyMultiplier`:
- correct answers increase the multiplier slightly
- spawn rate becomes faster over time
- bubble travel speed is scaled by difficulty

This makes the play session behave like an escalating survival/accuracy challenge rather than a level-based game.

## Player goals
The player is effectively moderating or reacting to incoming streamer/chat messages:

- **LOVE** supportive fan messages
- **BLOCK** hostile/hater messages
- preserve the stream’s health/life meter
- maximize the **Verified Fans** score before the stream shuts down

The loss condition occurs when life reaches zero, framed as **Feed Shut Down** because too many bad messages slipped through.

## Interaction pattern
The game uses an extremely simple binary input model:

- tap/click **left half** of the screen = `LOVE`
- tap/click **right half** of the screen = `BLOCK`

The interaction is not direct target tapping. Instead, the player always acts on the **lowest active bubble** on screen, which creates a timing-and-priority rhythm:
- wait for the most urgent message to descend
- classify it quickly
- press the correct side before it escapes

This gives the game the feel of a fast mobile moderation reflex game.

## Core systems
### 1. Message spawning
Messages appear as rounded speech bubbles with:
- type: fan or hater
- random short text line
- color coding
- matching iconography

Fan bubbles are more common than hater bubbles.

### 2. Classification / judgment system
Each bubble has a required response:
- fan → LOVE
- hater → BLOCK

Correct input:
- removes the bubble
- adds score
- slightly increases difficulty
- triggers positive audiovisual feedback

Incorrect input:
- removes the bubble
- reduces life
- triggers failure feedback and shake

### 3. Miss penalty system
If a bubble falls off-screen:
- life decreases
- failure feedback triggers
- the bubble is removed

This means both inaction and misclassification are punished.

### 4. Survival meter
Life starts at 100%.
As life drops:
- HUD updates live
- low health can trigger a warning cue
- zero life triggers game over

### 5. Feedback system
The game strongly emphasizes instant response:
- sound effects for success, fail, warning, restart
- reaction GIF cards
- vibration hooks for mobile/webview support
- emoji particle bursts
- screen shake on mistakes

### 6. Restart loop
From game over, the player restarts instantly into a fresh endless run with reset values.

## Inferred genre / gameplay shape
Strongest inferred shape:

- **Arcade reaction classifier**
- **lane/binary sorting survival game**
- **mobile-friendly endless score chase**

It resembles a hybrid of:
- a **lane runner game** in input structure (left/right split decision)
- a **clicker/reaction game** in cadence
- a **streamer/influencer theme simulator** in framing and fiction

Despite the theme, it is not a deep management sim. The actual play is a fast, single-screen reflex game centered on identifying and responding to incoming social messages.

## Presentation and tone
The presentation suggests:
- neon social-media cyberpop styling
- playful influencer satire
- quick, punchy, short-session mobile play
- a humorous “manage your online audience” fantasy

The title and UI language frame the experience as a streamer/influencer survival challenge where reputation and fan energy are under attack from bad chat.

## Gameplay heuristic summary
A faithful gameplay heuristic is:

- endless session
- incoming chat bubbles descend from top to bottom
- player watches the lowest bubble
- left means embrace/support, right means reject/block
- score is earned from fast correct classification
- mistakes and missed messages drain life
- speed gradually ramps up
- run ends when life reaches zero
- immediate restart supports repeat high-score attempts

## Confidence notes
Confidence is fairly high on the interaction model and core loop because they are explicit in code:
- the left/right input mapping is directly implemented
- the target selection logic explicitly picks the lowest bubble
- fan vs hater classification is explicit
- the score/life/endless progression model is explicit

Lower-confidence areas are mostly interpretive:
- whether the game should be described more as moderation, fan management, or streamer survival fiction
- whether “runner” is the best taxonomy label, since it uses lane-style decisions without literal character running