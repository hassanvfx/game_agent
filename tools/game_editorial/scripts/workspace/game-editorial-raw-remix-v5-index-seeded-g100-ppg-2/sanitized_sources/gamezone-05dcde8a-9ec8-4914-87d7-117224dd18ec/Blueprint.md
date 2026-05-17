# Blueprint

## High-level code structure
This game is implemented as a single self-contained HTML document with inline CSS and JavaScript.

- **Presentation layer**
  - Fullscreen `<canvas>` for all world rendering.
  - HTML overlay UI for the start screen, HUD, mute button, speech bubble, GIF feedback, and game-over screen.
  - Tailwind utility classes are used alongside custom CSS for neon arcade styling and responsive layout.

- **Configuration layer**
  - A hidden JSON config block defines tunable runtime values:
    - `busSpeed`
    - `voiceVolume`
    - `showLyrics`

- **Audio / voice systems**
  - `VoiceManager` wraps browser speech synthesis and controls the singing announcer/bus voice.
  - `AudioManager` mixes:
    - looping background music
    - HTML audio SFX
    - synthesized notes and tones through Web Audio
    - lyric-triggered speech events

- **Core game system**
  - `Game` owns:
    - canvas sizing and drawing
    - input binding
    - world setup
    - entity spawning
    - update loop
    - collision checks
    - score/state transitions

## Game loop / state model
The game follows a straightforward arcade loop with three primary states:

- **START**
  - Start overlay is visible.
  - The bus is shown in an idle/demo state.
  - Input starts a run.

- **PLAYING**
  - The bus moves automatically from left to right only in presentation; gameplay is actually forward auto-scroll.
  - Obstacles and collectibles spawn from the right and move left toward the player.
  - Speed gradually increases over time.
  - The player switches between two lanes to collect notes and avoid hazards.
  - Score increases by collecting note items.

- **GAMEOVER**
  - Triggered by colliding with a roadblock/rock.
  - Music and singing stop.
  - Crash and game-over feedback plays.
  - Final score is displayed and the player can restart.

Per-frame loop:
1. compute `dt`
2. update parallax scenery
3. animate player lane interpolation and singing mouth motion
4. spawn entities if spacing allows
5. move entities left based on current speed
6. resolve collisions
7. update particles
8. draw background, road, scenery, entities, player, and effects
9. request next animation frame

## Player goals
The immediate player goal is to survive as long as possible while collecting glowing music notes.

Primary objectives:
- switch into the lane containing notes
- avoid the lane containing rocks/roadblocks
- maintain the run as speed ramps up
- achieve a higher note count/score before crashing

The game is score-chasing rather than level-based.

## Interaction pattern
The interaction model is intentionally simple and mobile-friendly.

- **Pointer / tap**
  - tap start button to begin
  - tap anywhere during play to switch lanes
- **Keyboard**
  - `Space`
  - `ArrowUp`
  - `ArrowDown`

All of these effectively trigger a single action: **toggle between the two lanes**.

This produces a one-input arcade rhythm-runner pattern:
- read the lane layout
- time one-tap swaps
- collect rewards
- avoid instant-loss hazards

## Core systems
### 1. Two-lane runner movement
The player bus occupies one of two vertical lanes. Movement is not analog; it toggles between upper and lower road lanes with smoothing for animation.

### 2. Endless spawning
Entities spawn off-screen to the right with randomized spacing and randomized lane assignment.

Entity types:
- `NOTE` collectible
- `ROCK` hazard

Spawn bias favors hazards:
- approximately 70% rocks
- approximately 30% notes

### 3. Collision and scoring
Collision is checked by horizontal proximity to the bus x-position and vertical lane alignment.

- note collision:
  - score +1
  - collect SFX
  - celebration GIF
  - sparkle particles
- rock collision:
  - danger GIF
  - crash/game-over audio
  - particle burst
  - end run

### 4. Speed escalation
Base run speed comes from config and increases gradually over time, creating rising difficulty without introducing additional mechanics.

### 5. Audio-musical identity
This game’s main signature is the music-themed wrapper around a simple lane runner.

Audio systems include:
- looping backing music
- melodic synthesized note scheduler
- voice-synth “singing” lyric callouts
- lane switch / collect / crash feedback sounds

The lyric lines and speech bubble make the bus feel like a singing character rather than a generic vehicle.

### 6. Visual feedback
The game uses layered feedback to reinforce success/failure:
- score HUD
- animated speech bubble for sung lyrics
- celebration and danger reaction GIFs
- particles on lane swap, collection, and crash
- bright neon palette and glowing UI panels

### 7. Lightweight world simulation
Background clouds, trees, ground bands, and dashed road markings scroll continuously to suggest forward motion and maintain the parade/night-drive atmosphere.

## Inferred genre / gameplay shape
Strongest inferred genre shape:

- **lane-based endless runner**
- **music-themed arcade dodging/collecting game**
- **casual one-button reflex game**

More specifically, it feels like:
- a two-lane endless runner
- with rhythm/music presentation and collectible note theming
- tuned for short replayable sessions and mobile tap controls

## Heuristic summary
This is a compact arcade runner where a singing neon bus rides through a night parade road. The player repeatedly taps to swap between two lanes, trying to catch glowing musical notes while avoiding jagged roadblocks. Difficulty rises through speed increase, while the game’s identity is carried by speech-synth vocals, looping music, bright neon UI, and animated feedback rather than by deep progression systems.