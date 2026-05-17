# Blueprint

## Overview
This codebase is a single-file browser arcade game implemented entirely in `index.html` with inline CSS and JavaScript. It presents a neon-styled space shooter where the player controls a ship at the bottom of the screen, automatically fires upward, and survives by sliding left and right to destroy falling meteors/hostile objects.

## High-level code structure
- **HTML shell**
  - Fullscreen `<canvas>` for gameplay rendering.
  - Overlay UI layer for:
    - start screen
    - HUD
    - game-over screen
    - reactive feedback GIFs
- **CSS presentation layer**
  - Neon sci-fi visual theme
  - glassmorphism panels
  - responsive/mobile-safe layout
  - animated hero ship and UI glow effects
- **Inline JavaScript game code**
  - asset declarations
  - audio controller
  - game state and entity storage
  - rendering helpers
  - main loop
  - input handling
  - UI screen transitions

## Game loop / state model
The game uses a simple real-time loop driven by `requestAnimationFrame`.

### Main state variables
- `gameActive`: whether the run is currently in progress
- `score`: current run score
- `frameCount`: timing source for spawn/fire cadence
- entity arrays:
  - `bullets`
  - `enemies`
  - `particles`
  - `stars`
- `player`: horizontal ship position plus size data

### State flow
1. **Start screen**
   - player sees title card and launch button
2. **Active run**
   - HUD visible
   - player ship moves horizontally
   - bullets auto-fire at fixed intervals
   - enemies spawn from the top and move downward
   - score increases on enemy destruction
3. **Game over**
   - triggered by collision between enemy and player
   - BGM stops, fail feedback appears
   - final score shown
4. **Restart**
   - run state resets and play resumes immediately

## Player goals
- Survive as long as possible
- Destroy as many falling enemies/meteors as possible
- Maximize score
- Avoid direct collisions with incoming threats

## Interaction pattern
- **Primary input:** horizontal movement only
- **Desktop:** mouse movement across the canvas
- **Mobile:** touch drag / touch move across the canvas
- **Combat model:** shooting is automatic; the player focuses on positioning and dodging rather than firing manually

This creates a one-axis dodge-and-aim-by-position interaction model.

## Core systems
### 1. Player movement system
- Ship is locked near the bottom of the screen
- Only `x` position changes
- Position clamps to screen boundaries

### 2. Auto-fire projectile system
- Bullets spawn every fixed number of frames
- Bullets travel upward
- Bullet firing includes repeated SFX with throttling

### 3. Enemy spawn and descent system
- Enemies spawn at random horizontal positions above the screen
- They fall downward with randomized size, speed, and color
- Effective difficulty ramps because spawn cadence and speed increase with score

### 4. Collision system
- Bullet vs enemy: enemy is destroyed, particles spawn, score increases
- Enemy vs player: immediate game over
- Enemies leaving the bottom are simply removed

### 5. Particle / feedback system
- Small explosion particles on successful hits
- Animated GIF flashes for hit and fail reactions
- Reinforces arcade reward and failure moments

### 6. Audio system
- One looping BGM track
- SFX for start, shooting, scoring/exploding, and failure
- Audio is unlocked on user interaction to satisfy browser autoplay rules

### 7. Background / spectacle system
- Animated starfield
- gradient nebula background
- motion streaks
- glowing ship, enemy, and projectile rendering

## Inferred genre / gameplay shape
The game most strongly resembles a **casual arcade space shooter** with **lane-free horizontal dodging** and **automatic fire**. It is not a deep simulation or progression-heavy title; it is a score-chasing survival action game with quick restart loops.

## Progression shape
- Immediate start
- No menus, upgrades, or level map
- Difficulty scales during a single run through:
  - faster/more frequent enemy pressure
  - increased need for precise dodging
- Progression is **run-based score progression**, not meta-progression

## Presentation and tone
- neon sci-fi / arcade cabinet aesthetic
- playful but intense space-combat framing
- readable, lightweight, mobile-friendly interface
- “one more try” replay structure

## Gameplay heuristic summary
A faithful recreation should preserve:
- fullscreen canvas arcade presentation
- bottom-positioned ship controlled only on the horizontal axis
- constant automatic shooting
- falling enemy hazards with collision-based defeat
- score-based survival loop
- quick restart flow
- neon, high-contrast sci-fi visuals with audio feedback and lightweight spectacle