# Blueprint

## High-level code structure
The game is implemented as a single self-contained `index.html` file with three main layers:

1. **Presentation layer**
   - Inline CSS defines a neon sci-fi UI, responsive overlays, HUD, feedback GIFs, and start/game-over panels.
   - A full-screen `<canvas>` renders the active playfield and all game entities.

2. **Configuration layer**
   - A JSON blob in `#game-config` exposes tweakable gameplay values:
     - `alienSpeed`
     - `gravity`
     - `bounceForce`
     - `headColor`

3. **Runtime/game logic layer**
   - `AudioManager` handles background music, sound effect loading, playback, cooldowns, and synthesized fallback sounds.
   - A DOMContentLoaded block initializes state, input, resize handling, update/draw logic, UI transitions, and the animation loop.

## Game loop / state model
The game uses a classic requestAnimationFrame loop with three explicit states:

- **START**
  - Start screen visible.
  - Background/canvas still renders for ambience.
  - Player can begin via the launch button.

- **PLAYING**
  - Main interactive state.
  - Player steers a horizontal rescue skiff at the bottom of the screen.
  - A drifting rescue pod falls under gravity, bounces off walls/ceiling, and gains new horizontal motion when struck by the skiff.
  - Score increases by 10 on each successful rescue bounce.

- **GAMEOVER**
  - Triggered when the pod falls below the bottom of the screen.
  - Final score is shown.
  - Mission-failure feedback appears.
  - Player can restart into a fresh run.

Per-frame behavior during play:
1. Smoothly move the player skiff toward pointer/touch x-position.
2. Apply gravity and velocity to the falling pod.
3. Resolve wall and ceiling bounces.
4. Check for skiff/pod collision and convert it into a strong upward bounce.
5. Spawn particles, score popups, shake, audio, and feedback UI.
6. End the run if the pod drops off-screen.
7. Draw the starfield, skiff, pod, particles, and popups.

## Player goals
The player’s goal is to keep the drifting rescue pod in play as long as possible by catching and bouncing it with the rescue skiff. The immediate objective is survival/maintenance of the pod signal; the scoring objective is to chain as many successful rescues as possible.

## Interaction pattern
- **Primary input:** pointer/touch horizontal movement on the canvas
- **Interaction style:** direct-positioning paddle control
- **Action cadence:** continuous real-time reactive play
- **Failure condition:** missing the pod and letting it fall off the bottom edge
- **Restart loop:** instant retry from the game-over screen

This makes the interaction read like a one-buttonless arcade catching game or paddle survival loop.

## Core systems
### 1. Paddle / skiff control
- The player entity (“alien” variable, visually a rescue skiff) follows the pointer target with smoothing.
- Horizontal motion is clamped to the screen.

### 2. Falling pod physics
- The pod (“head” variable, but presented as a rescue pod/crew unit) has:
  - position
  - velocity
  - gravity
  - rotation
  - collision state

### 3. Bounce/collision response
- Wall and ceiling hits invert velocity with damping.
- Skiff collision gives a configurable upward impulse.
- Hit offset affects lateral velocity and spin, giving the player some control over trajectory.

### 4. Scoring and juice
- Each successful catch gives `+10`.
- A popup appears at the collision point.
- Particles spawn for impact/reward feedback.
- Screen shake emphasizes collisions and success.

### 5. Audio feedback
- Looping background music during gameplay.
- Distinct sounds for:
  - starting
  - successful rescue
  - wall impact
  - mission failure
- Fallback synthesized tones exist if asset loading fails.

### 6. UI state transitions
- Start screen and game-over screen are handled through DOM class toggles.
- HUD only appears during active play.
- Status banners and reaction GIFs reinforce success/failure moments.

### 7. Responsive/mobile presentation
- Canvas fills viewport.
- Touch input is supported.
- UI scales for narrow screens.
- Layout avoids scroll and uses touch-safe sizing.

## Inferred genre / gameplay shape
This is best understood as a **single-screen arcade paddle survival game** with strong resemblance to:
- an endless keep-up / juggling loop,
- a simplified physics paddle game,
- an arcade “don’t let it drop” score chase.

It is not level-based and does not appear to have enemies, narrative branching, or resource economy. Its structure is:
- launch run,
- juggle falling target,
- score from repeated saves,
- fail on drop,
- instantly retry.

## Gameplay heuristic
The intended play heuristic appears to be:
- stay centered under the pod,
- make controlled catches rather than extreme saves,
- use off-center hits to shape the pod’s lateral path,
- react quickly to ricochets from walls,
- maintain a stable rhythm for long scoring runs.

The emotional loop is arcade tension plus recovery satisfaction: brief danger spikes, clean rescue rebounds, and immediate retry motivation after failure.

## Confidence notes
Confidence is high on the real-time arcade survival interpretation because the code clearly implements:
- one active falling object,
- one horizontal catcher,
- score-on-bounce,
- fail-on-drop,
- restartable endless runs.

Confidence is lower only around thematic naming because variables still use legacy labels like `alien` and `head`, while the UI text reframes them as a rescue skiff and drifting pod.
