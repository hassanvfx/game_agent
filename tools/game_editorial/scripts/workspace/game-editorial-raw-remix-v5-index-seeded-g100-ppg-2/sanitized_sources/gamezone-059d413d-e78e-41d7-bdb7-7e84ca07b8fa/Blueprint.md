# Blueprint

## High-level code structure
The game is implemented as a single-page HTML document with:
- a full-screen canvas for all scene and character rendering
- layered DOM UI panels for the start screen, HUD, controls, instructional overlays, and win screen
- inline CSS for the bright toy-like visual theme and mobile-safe responsive layout
- inline JavaScript for state management, rendering, audio control, GIF feedback, input handling, and minigame logic

The code is organized into a few practical sections:
1. asset declarations for remote audio and reaction GIFs
2. `AudioController` for background music and sound effects
3. `GifController` for short positive/negative visual feedback overlays
4. core game state variables
5. resize/setup helpers and cloud/background initialization
6. canvas drawing helpers for the pet, stars, and camp scene
7. game logic and state transitions
8. animation loop
9. mouse/touch/button input listeners

## Game loop / state model
The game runs on a requestAnimationFrame loop after the player chooses a pet.

### Main states
- `SELECT`: title screen and pet selection
- `HUB`: central camp where the pet idles and the player chooses an activity
- `EAT`: feeding minigame where apples fall and the pet is moved horizontally to catch them
- `SHOWER`: cleaning minigame where the player rubs/touches dirt spots away
- `RACE`: obstacle-jump minigame where the pet jumps rocks
- `WIN`: end screen shown after collecting 5 stars

### Persistent progression state
- selected pet type: dog, cat, or hamster
- stars counter out of 5
- three care stats:
  - hunger
  - hygiene
  - fun

### Reward model
Each activity raises one associated stat:
- feeding raises hunger
- shower raises hygiene
- race raises fun

When any stat reaches 100:
- the player gains 1 star
- that stat resets to 50
- a win sound and celebration GIF play

The game ends once total stars reach 5.

## Player goals
The player’s immediate goal is to keep interacting with the pet through care-themed activities.

The medium-term goal is to fill the three stat meters by succeeding in the matching activities.

The top-level victory goal is to earn 5 stars by repeatedly maxing out the pet-care meters.

## Interaction pattern
The interaction flow is simple and arcade-like:
1. choose one of three pets
2. enter the camp hub
3. pick a care action from large bottom buttons
4. perform a lightweight minigame using touch or mouse gestures
5. return to the hub or continue rotating between activities
6. collect stars until the win screen appears

### Input model
- button/tap selection in menus and hub
- mouse or touch movement for feeding and cleaning
- tap/click to jump during the race
- explicit exit button for leaving minigames

This makes the game readable as a mobile-first casual experience.

## Core systems
### 1. Pet selection and identity system
The chosen pet changes the illustrated character palette and silhouette details, but the overall game structure stays the same.

### 2. Care stat system
Three meters represent the pet’s wellbeing:
- hunger
- hygiene
- fun

These act as soft progression tracks rather than survival failure conditions.

### 3. Minigame rotation system
Each core need maps to a tiny action game:
- catching falling apples
- scrubbing away mud spots
- jumping over obstacles on a track

### 4. Star progression system
Stars are the main meta-currency/progression marker. Reaching thresholds on stats converts successful care into stars.

### 5. Audio/feedback system
The game uses:
- looping background music
- distinct SFX for UI, jumping, cleaning, failures, collection, and completion
- short celebratory/failure GIF flashes for feedback

### 6. Presentation/HUD system
The HUD continuously displays:
- star count
- current mode label
- the three stat bars

Instruction banners teach each minigame in a short sentence.

### 7. Sleep interlude system
A sleep button triggers a temporary overlay and pauses music, functioning more like a flavor interaction than a full progression mechanic. It slightly reduces hunger and fun after the nap, implying rest trades off against other needs.

## Inferred genre / gameplay shape
Primary genre reading:
- pet simulator
- casual minigame collection
- light arcade care game

Secondary gameplay shape:
- mobile-friendly virtual pet loop
- stat-building through microgames instead of passive timers
- short-session family/kids-oriented play

## Gameplay heuristic
The intended player behavior appears to be:
- select a cute pet companion
- rotate between feeding, washing, and racing
- perform very short skill interactions
- watch meters rise
- convert full meters into stars
- repeat until the pet camp is fully completed

The game is not balanced like a punishing sim. It is better understood as a cheerful, forgiving companion-care loop with tiny arcade tests and visible reward bursts.

## Confidence notes
High confidence:
- virtual pet care framing
- three minigames tied to three wellbeing stats
- star-based win condition at 5 stars
- mobile/touch-first design

Moderate confidence:
- “camp” framing is mostly thematic presentation rather than a systemic camp-management layer
- sleep is a flavor mechanic with only minor stat impact, not a full energy-management system