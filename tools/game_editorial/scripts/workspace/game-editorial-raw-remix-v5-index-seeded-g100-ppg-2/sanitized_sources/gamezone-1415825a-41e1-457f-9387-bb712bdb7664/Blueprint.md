# Blueprint

## High-level code structure
The game is implemented as a single self-contained HTML document with:
- inline CSS for all presentation, responsive layout, overlays, HUD, and visual effects
- inline JavaScript for asset setup, audio control, physics, rendering, UI state changes, and input handling
- a single `<canvas>` used for all real-time game rendering
- DOM-based overlay panels for the title screen, HUD, combo feedback, and game-over screen

The code is organized into clear sections:
1. Asset declarations
2. Audio controller class
3. Core game state and canvas references
4. Visual/background/particle rendering helpers
5. Gameplay logic and physics
6. Input and UI event wiring

## Game loop / state model
The state model is lightweight and arcade-oriented.

### Main states
- **Start screen**: intro panel is visible, gameplay inactive
- **Active run**: HUD visible, animation frame loop running, player can tap/click the ball
- **Game over**: loop stops, final score is shown, restart becomes available

### Main loop behavior
During the active state, the requestAnimationFrame loop repeatedly:
1. clears the canvas
2. draws the stadium background and moving clouds
3. updates ball physics
4. draws the ball
5. draws active particles

If the ball touches the ground, the run ends immediately and the game transitions to game over.

## Player goals
The player goal is to keep a soccer ball airborne for as many consecutive juggles as possible.

Success is measured by:
- the current juggle count during play
- the final juggle total shown after failure

There is no level progression or stage map; progression is score-based and performance-based within repeated short runs.

## Interaction pattern
The interaction model is direct and minimal:
- the player taps or clicks near the ball
- successful input applies an upward kick and a sideways/spin response based on contact position
- each valid hit increments the score
- missing the ball or letting it fall to the ground ends the round

The interaction feel is tuned for quick retry loops:
- forgiving hitbox
- strong upward kick impulse
- immediate score feedback
- short combo messaging bursts
- instant restart option

## Core systems
### 1. Ball physics
The ball has:
- position
- velocity
- angular velocity
- radius
- bounce behavior against left/right walls

Physics include:
- constant gravity
- friction damping
- wall bounce damping
- game-over trigger on ground impact

### 2. Skill-based touch/click control
The kick direction uses pointer position relative to the ball:
- a hit gives fixed upward force
- side contact introduces horizontal motion
- side contact also adds spin

This creates a simple mastery curve around positioning and timing.

### 3. Score and streak feedback
The score increments per successful juggle.
A secondary streak layer triggers every 5 hits:
- combo text updates
- combo sound effect plays
- celebration reaction GIF flashes

This system frames the game as a streak-chasing arcade challenge.

### 4. Audio feedback
The audio system includes:
- looping background music during active play
- kick sound on each successful juggle
- combo sound for streak milestones
- UI sounds for start/restart
- fail sound on game over

### 5. Juice and presentation effects
Feedback systems include:
- particle bursts on successful hits
- combo/fail reaction GIF overlays
- glowing HUD
- dramatic night stadium background
- animated clouds and spotlighting
- ball shadow and shine

## Inferred genre / gameplay shape
This is best understood as a **single-screen arcade skill game** centered on **tap-based soccer juggling**.

Its gameplay shape is:
- immediate start
- one-object mastery challenge
- rising self-imposed difficulty as the ball drifts and gains momentum
- failure on drop
- rapid restart loop
- score-chasing replayability

## Gameplay heuristic
The intended play heuristic appears to be:
- keep the ball near the screen center
- tap slightly off-center when correction is needed
- avoid overcorrecting lateral drift
- maintain rhythm under increasing positional instability
- chase higher streaks and milestone feedback rather than unlock-based progression

## Inference confidence notes
Confidence is high on the core loop because the code explicitly implements:
- a soccer ball
- juggle scoring
- fail on ground hit
- start/restart loops
- combo and crowd-style messaging

Confidence is lower only on broader framing language such as “neon derby mode,” which appears stylistic rather than a separate mechanic.