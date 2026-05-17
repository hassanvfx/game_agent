# Blueprint

## High-level code structure
The game is implemented as a single self-contained `index.html` file with:
- inline CSS for the full visual theme, HUD, overlays, and responsive layout
- inline HTML for audio tags, canvas container, HUD, start screen, and game-over screen
- inline JavaScript for configuration, entities, input handling, audio, state updates, and rendering

The architecture is lightweight and arcade-oriented:
1. **Configuration layer**: a JSON script tag defines tunable values such as cook speed, burn speed, spawn rate, and theme color.
2. **State layer**: global variables track play status, score, misses, particles, customers, pans, timers, and screen shake.
3. **Entity layer**: `Particle`, `Pan`, and `Customer` classes encapsulate update and draw behavior.
4. **System layer**: helper functions manage audio, GIF feedback, color interpolation, particle spawning, game-over checks, initialization, game start, and the animation loop.
5. **Presentation layer**: a canvas renders the kitchen scene while DOM overlays provide readable menus and score UI.

## Game loop / state model
The game uses a standard `requestAnimationFrame` loop:
- compute delta time
- update customer spawn timer
- spawn customers into a queue up to a cap
- update customer movement toward queue positions
- update pan cooking/burning progress
- update particles and shake decay
- redraw the full scene each frame

Primary global states:
- **pre-game**: start overlay visible, game not running
- **playing**: HUD visible, customers spawn, pans can be interacted with
- **game-over**: gameplay stops after 3 misses, game-over overlay appears

Per-pan state machine:
- `empty` → first tap starts cooking
- `cooking` → progress fills until food becomes ready
- `cooked` → second timer begins; food is ready but can burn
- `burned` → counts as a miss; player can tap to clear/reset the pan

## Player goals
The player is trying to:
- keep food moving efficiently across three pans
- wait until food reaches the ready window
- serve waiting customers before food burns
- avoid accumulating 3 misses
- maximize score by serving as many customers as possible

The score reward is simple and immediate:
- serving a cooked item to a waiting customer grants points
- burning food increases the miss count
- serving with no customers wastes the food and resets the pan

## Interaction pattern
The game is a direct tap/click arcade loop:
- tap a pan once to begin cooking
- visually monitor the ring and food color
- react to the green “READY” cue
- tap the ready pan again to serve
- if burned, tap again to clear the pan

The interaction is single-screen and fast, with no inventory, navigation, or complex menus. Timing judgment and queue management drive play.

## Core systems
### 1. Cooking timing system
Each pan independently advances through cooking and burning using configurable rates. This is the main skill system.

### 2. Customer queue system
Customers periodically spawn and form a line. Ready food can only score if at least one customer is waiting.

### 3. Risk/reward serving system
The player must balance:
- waiting long enough for the dish to become ready
- not waiting so long that it burns
- not overcooking pans when no customers are present

### 4. Failure / lives system
Burned food increments a miss counter. At 3 misses, the session ends.

### 5. Feedback system
The game reinforces outcomes with:
- score and miss HUD updates
- sound effects for ready, serve, fail, blocked, and game over
- animated GIF feedback for serve/fail beats
- particles and screen shake

### 6. Responsive single-canvas presentation
The canvas resizes to fit the viewport, and the game is tuned for pointer/touch use on mobile as well as desktop.

## Inferred genre / gameplay shape
This is best understood as a **casual arcade cooking/timing game** with light queue management. It combines:
- reaction-based timing
- short-session score chasing
- kitchen-service fantasy
- single-screen multitasking pressure

The overall gameplay shape resembles a stripped-down mobile cooking reflex game rather than a deep management simulator. It is closer to an arcade “cook at the right moment and serve the line” loop than to a restaurant-building or resource-heavy simulation.

## Gameplay heuristic
A strong player strategy is likely:
1. light up multiple pans early to prepare throughput
2. avoid filling every pan if no customers are queued
3. prioritize serving ready food immediately once customers exist
4. scan the pans constantly for imminent burn states
5. treat misses as the main loss condition and score as secondary to survival

## Confidence notes
Confidence is **high** on the core loop because the pan state machine, customer queue, score system, and miss-based fail state are explicit in code.
Confidence is **moderate** on thematic nuance because customers all request the same burger-like item and there is no broader restaurant progression beyond difficulty-by-pressure.