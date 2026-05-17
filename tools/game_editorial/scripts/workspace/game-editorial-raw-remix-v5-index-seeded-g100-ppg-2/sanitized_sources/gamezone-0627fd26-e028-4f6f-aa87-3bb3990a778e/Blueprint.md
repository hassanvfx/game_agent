# Blueprint

## High-level code structure
The game is implemented as a single self-contained `index.html` document with three major layers:

1. **Presentation / UI layer**
   - Inline CSS defines the full visual identity: futuristic checkpoint styling, HUD panels, overlays, control buttons, reaction cards, and mobile-responsive layout behavior.
   - HTML provides the HUD, start/game-over overlays, control buttons, and reaction GIF containers.

2. **3D rendering layer**
   - Three.js is loaded from a local workspace copy and used to render a simple conveyor-belt checkpoint scene.
   - A scene, perspective camera, renderer, lights, floor plane, conveyor belt, and a hero cargo crate are created.
   - Contents inside the crate are represented by simple geometric meshes.

3. **Game logic / systems layer**
   - JavaScript inside `DOMContentLoaded` owns all runtime state.
   - Systems include audio playback, object generation, x-ray visualization, decision resolution, score handling, spawning, and UI event wiring.

## Game loop / state model
This is not a physics-heavy continuous action game; it is a repeating **spawn → inspect → decide → resolve → respawn** loop.

### Primary runtime state
- `score`: increases by 100 for each correct decision.
- `gameActive`: gates whether play is live.
- `isXray`: tracks whether the player is actively holding scan.
- `currentBag`: declared but effectively unused in behavior.
- `bagHasContraband`: whether the current crate contains illegal items.
- `isProcessing`: prevents input during crate movement / transitions.
- `activeReactionTimer`: controls temporary feedback cards.

### State flow
1. **Start screen**
   - Player reads a short briefing and presses Start Watch.
2. **Initialization**
   - Audio is unlocked.
   - Three.js scene is initialized.
   - Background music begins.
   - Score resets and first crate spawns.
3. **Crate arrival**
   - A crate animates onto the conveyor from the left.
   - Controls become available once the crate stops at inspection position.
4. **Inspection**
   - Player can hold the Scan button to activate x-ray view.
   - Illegal items are tinted danger red; safe items glow cyan.
5. **Decision**
   - Player chooses either:
     - `FLAG` for suspicious / contraband cargo
     - `CLEAR` for safe cargo
   - There is no separate “submit after scan”; the decision buttons are the final action.
6. **Resolution**
   - Correct call:
     - score increases
     - positive status and success feedback play
     - crate exits and a new one spawns
   - Incorrect call:
     - music stops
     - fail reaction plays
     - game-over overlay appears with final score
7. **Restart**
   - Restart resets score and begins the loop again.

## Player goals
The player acts as a checkpoint inspector screening cargo crates.

Immediate goal:
- Determine whether the current crate contains contraband.

Operational goal:
- Use the x-ray scan to inspect contents before making a judgment.

Scoring goal:
- Build the highest possible streak of correct calls, worth 100 points per crate.

Failure condition:
- One incorrect judgment immediately ends the run.

## Interaction pattern
The interaction model is short-session, high-clarity, and binary:

- Press **Start Watch** to begin.
- Wait for the crate to reach the scanner.
- Hold **Scan** to reveal crate contents.
- Press **Flag** if contraband is present.
- Press **Clear** if no contraband is present.
- Repeat until a mistake causes game over.

Control style:
- Mouse and touch are both supported.
- Scan is intentionally hold-based (`mousedown` / `touchstart` active, released on `mouseup` / `touchend`).
- Decision buttons are single-tap / single-click actions.
- Minor mouse movement shifts the camera slightly for a reactive 3D feel.

## Core systems

### 1. Cargo generation system
Each spawned crate contains 3 to 5 placed items chosen from:
- illegal: gun, bomb, knife
- safe: bottle, laptop, generic box

Generation heuristic:
- About 40% of crates are forced to contain contraband.
- Contraband crates may contain more than one illegal item.
- Safe crates use harmless props only.

### 2. X-ray inspection system
The scan button temporarily changes materials:
- crate shell becomes faint cyan wireframe
- illegal contents become bright red / pink
- safe contents become cyan translucent meshes

This system is the game’s signature mechanic and main information-reveal action.

### 3. Judgment / verification system
The decision logic is simple:
- `FLAG` is correct only when contraband exists.
- `CLEAR` is correct only when contraband does not exist.

There is no partial credit, no timer pressure system, and no multi-step review process.

### 4. Progression / difficulty shape
Progression is score-based rather than level-based:
- repeated crate reviews
- static rules
- increasing self-imposed tension as score rises

Inferred difficulty comes from:
- randomized crate contents
- visual reading under brief inspection
- one-strike failure structure

There is no explicit speed ramp in the code, but the arcade pressure comes from perfect-play requirements.

### 5. Feedback and juice system
- Success/fail reaction GIF cards
- SFX for UI, scanning, warnings, success, fail, and blocked input
- Background music loop
- Status text shifts between safe/warning states
- Start and game-over overlays reinforce session framing

### 6. Mobile-safe UI system
The HUD and buttons are laid out with:
- responsive media queries
- large thumb-friendly action buttons
- safe-area bottom spacing
- touch-specific scan behavior
- no complex gesture dependency

## Inferred genre / gameplay shape
Strongest inferred shape:
- **inspection-based arcade decision game**
- **binary judgment / checkpoint screening sim-lite**
- **light 3D reflex-and-observation game**

It borrows qualities from:
- x-ray luggage inspection minigames
- spot-the-danger classification games
- survival-by-perfect-decisions arcade loops

It is not a deep simulator; it is a compact, accessible, round-based checkpoint screening game with a polished sci-fi presentation.

## Gameplay heuristic
The optimal player heuristic is:

1. Wait for the crate to fully stop.
2. Hold Scan long enough to read the silhouettes / highlighted contents.
3. Look specifically for any illegal silhouette: gun, bomb, or knife.
4. If any illegal item is present, choose **Flag**.
5. If only neutral items appear, choose **Clear**.
6. Repeat carefully because a single wrong call ends the run.

The game rewards cautious recognition over speed clicking. The central skill is correctly mapping the x-ray reveal to a binary security decision under arcade pressure.