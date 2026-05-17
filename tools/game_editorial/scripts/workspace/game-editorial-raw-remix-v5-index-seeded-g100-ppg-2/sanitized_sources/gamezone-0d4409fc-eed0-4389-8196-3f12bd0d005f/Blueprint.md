# Blueprint

## High-level code structure
The game is implemented as a single self-contained `index.html` file with three main layers:

1. **Presentation / UI layer**
   - Inline CSS defines the neon school aesthetic, responsive HUD, start screen, win screen, dialogue bubble, joystick, and feedback overlay.
   - DOM elements handle onboarding, HUD counters, sound toggle, character switch button, dialogue, and overlays.

2. **Systems layer inside script**
   - `AudioSys` manages background music and short cues for start, collect, switch, blocked actions, and win.
   - `FeedbackSys` manages celebratory reaction GIF overlays for collecting lunches and winning.
   - `Assets` and helper drawing functions procedurally generate all game visuals on canvases instead of loading sprite sheets.

3. **Game / simulation layer**
   - Map generation creates a tall school layout with a central corridor and paired classrooms.
   - `Game` owns state for player position, score, items, NPCs, particles, dialogue, active character, camera, update logic, draw logic, and win state.
   - Input is driven by a touch/pointer joystick, plus UI buttons for sound and character swapping.

## Game loop / state model
The state flow is simple and arcade-like:

- **Start screen state**
  - Player sees the title, mission summary, and a single “START RUN” button.
  - No simulation runs until start is pressed.

- **Active play state**
  - `Game.start()` initializes assets, generates the map, resets state, and enters `requestAnimationFrame` loop.
  - Each frame:
    - read joystick vector
    - move player with collision checks
    - update facing/animation
    - move camera to follow player
    - test item pickups
    - test NPC proximity for dialogue
    - update particles
    - render visible map, pickups, NPCs, player, and effects

- **Win state**
  - Triggered when score reaches 5 collected lunches.
  - Background music pauses, win audio and celebratory overlay play, and a win screen is shown.
  - Restart resets score, respawns lunches/NPCs, and resumes the loop.

This is not a level progression structure with multiple stages; it is one contained scavenger-run loop with replay.

## Player goals
Primary goal:
- Collect **5 lunch items / sandwiches** hidden across the school map.

Secondary motivations:
- Explore classrooms and corridor branches efficiently.
- Avoid wasting time on blocked routes caused by walls, lockers, tables, and chalkboards.
- Swap between four scout characters to change the avatar identity and trigger short character flavor lines.
- Pass near NPCs to hear ambient campus chatter.

The win condition is purely collection-based.

## Interaction pattern
Core interaction is intentionally minimal and mobile-first:

- **Touch and drag joystick** to move
- **Tap sound button** to toggle audio
- **Tap switch button** to cycle between playable characters
- **Walk near NPCs** to trigger dialogue automatically
- **Walk into sandwich pickups** to collect them automatically

There is no attack, inventory, puzzle input, or direct action button beyond character switching. The play pattern is explore -> spot pickup -> navigate around obstacles -> collect -> repeat until 5/5.

## Core systems
### 1. Procedural campus layout
The map is generated in code using tile values:
- floor
- wall
- locker
- door
- table
- chair
- chalkboard

The school is a vertically extended hallway with ten repeated classroom rows, making the game feel like a compact exploration run through a stylized campus tower.

### 2. Collision and navigation
Player movement is analog, with collision tested against solid tiles:
- walls
- lockers
- tables
- chalkboards

Doors and chairs are passable, which creates readable routes into rooms and around classroom furniture.

### 3. Collectible hunt
Five sandwich items are randomly spawned on valid tiles away from the starting position. Collection happens by proximity radius, not button press.

### 4. Character identity swapping
The player can cycle among:
- Legoshi
- Haru
- Louis
- Jack

This does not alter mechanics, speed, or abilities. It is a cosmetic/flavor system that changes the displayed name and triggers a short quote.

### 5. NPC ambient dialogue
Twenty NPCs are distributed through classrooms. Approaching one shows a dialogue bubble with short campus-themed hint text. This acts as light flavor plus mild navigational suggestion.

### 6. Camera and rendering
The camera follows the player across a much larger map than the screen. Rendering uses a scaled canvas and generated pixel-art sprites with a neon palette.

### 7. Juice / feedback
The game reinforces progress through:
- pickup sound
- win sound
- floating particles
- animated GIF reaction overlay
- HUD score update
- win screen

## Inferred genre / gameplay shape
Strongest inferred shape:
- **top-down mobile exploration collectathon**
- **light arcade scavenger hunt**
- **casual campus-themed character chat game**

It borrows some adventure-RPG presentation cues (NPC proximity dialogue, tile map, character roster), but the actual mechanics are much lighter and more arcade-like than a full RPG. The game is best understood as a short replayable **touch-controlled scavenger run through a school hallway/classroom maze**.

## Gameplay heuristic
A likely effective player strategy is:

1. Start moving immediately up or down the central corridor.
2. Dip into classrooms whenever a pickup becomes visible.
3. Use door openings rather than trying to force through walls/furniture.
4. Treat NPCs as flavor and soft hints, not objectives.
5. Switch characters only for novelty or dialogue flavor.
6. Sweep methodically until the 5th lunch is collected and the run ends.

## Confidence notes
Confidence is fairly high because the full gameplay logic is visible in one file:
- clear score target (`0/5`)
- explicit mission text (“Collect 5 lunches”)
- explicit touch-only control note
- visible win trigger at score >= 5
- no hidden systems suggesting deeper mechanics

Lower-confidence areas:
- The title references “Cherryton: Classrooms & Chats,” while the start screen brands the game as “Snack Scout: Neon Hall Snack Dash.” This suggests the project identity may have shifted during iteration.
- Character references imply Beastars-inspired theming, but the actual gameplay remains abstracted into a school snack scavenger loop rather than a narrative franchise game.