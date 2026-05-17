# Blueprint

## High-level code structure
The game is a single-file HTML application with embedded CSS and JavaScript.

- **HTML layer**: defines a mobile-first vertical app shell with:
  - a header for karma, time, step count, sound, and notebook access
  - a central scene panel that presents the current event and choice buttons
  - an off-canvas notebook/menu with tabs for People, Acts, and Map
  - an interaction modal for character conversations and side activities
  - a start screen and a day-reset sleep transition
- **CSS layer**: creates a hand-drawn notebook aesthetic with rounded sketch panels, animated feedback, day/night palette swapping, and compact touch-friendly controls.
- **JavaScript layer**: contains all game data, state, scene flow, UI rendering, menu systems, relationship logic, location travel, arrest/jail flow, and audio/feedback handling.

The data model is mostly declarative:
- `CONFIG` sets day length, karma limits, relationship threshold, and crime threshold.
- `STEP_MAP` defines the 8-step daily timeline.
- `LOCATIONS`, `CHARACTERS`, `ACTIVITY_TYPES`, `INTERACTION_TEMPLATES`, `JAIL_SCENARIOS`, and `SCENARIOS` define the playable content pools.
- A mutable `state` object stores progression and temporary status.

## Game loop / state model
The core loop is a short repeated day with exactly **8 actions per loop**.

### Persistent and session state
Tracked state includes:
- `day`
- `step`
- `karma` from -10 to 10
- `currentLocation`
- `metCharacters`
- `relationships` per character, usually 0 to 100
- `inJail`
- `crimeHeat`
- `isInjured`
- `menuTab`
- current scene and interaction target

### Main flow
1. Player starts the day from a title screen.
2. `initGame()` resets the current day state and loads the opening node.
3. Each scene presents a short narrative prompt plus 2-3 actions.
4. Choosing an option:
   - adjusts karma and/or relationships
   - may increase crime heat
   - may heal injury
   - may trigger instant arrest
   - usually advances to the next step
5. `advanceStep()` moves the clock forward through the 8-slot school day.
6. Scenario selection depends on:
   - current time-slot pool from `STEP_MAP`
   - whether the player is currently visiting a location
   - whether the player is in jail
7. At the end of step 8, `triggerSleepReset()` advances the day, soft-recenters karma toward neutral, clears location and jail state, and starts another loop.

### Alternate flow states
- **Location mode**: if the player visits School, Home, Store, or Doctor from the notebook map, subsequent nodes pull from that location until the player leaves.
- **Jail mode**: if crime heat reaches the threshold or an option triggers instant arrest, the player is forced into a jail mini-loop for the rest of the day.
- **Interaction mode**: the notebook can open social actions with known characters or fire off side activities with randomized outcomes.

## Player goals
The code suggests a soft-goal rather than a formal win screen:

- survive and shape a better version of the repeated day
- build positive karma through helpful or kind choices
- discover characters and improve relationships
- reach at least 50 relationship with a character to unlock **Ask Out**
- avoid crime escalation and arrest
- manage injury by visiting the doctor when needed
- explore alternate tones of play, from wholesome to chaotic

The title and copy imply the fantasy is to **rewrite the loop** by steering the day toward a preferred moral/social outcome.

## Interaction pattern
The interaction model is a **choice-driven narrative routine**:
- tap a large button to select a scene response
- optionally open the notebook to:
  - check known people and their bond meters
  - choose extra activity categories
  - travel to a location
- use modal-based interaction for:
  - conversations
  - compliments
  - pranks
  - fights
  - asking someone out
  - side activities like crime, social posting, and self-care

Player input is simple, direct, and mobile-oriented:
- no movement controls
- no timing skill checks
- outcomes are selected from authored branches with some randomness

## Core systems
### 1. Daily schedule system
A fixed 8-step structure creates pacing:
- Wake Up
- Commute
- Homeroom
- Classes
- Lunch
- Afternoon
- Clubs
- Evening

### 2. Scenario node system
Each scenario is a lightweight node with:
- emoji
- title
- descriptive text
- optional associated character
- list of options
- stat effects and next-step routing

### 3. Karma system
A centered morality meter tracks whether the player trends good or bad.
- positive actions increase karma
- disruptive/cruel/criminal actions lower karma
- UI reflects this on a BAD-to-GOOD bar

### 4. Relationship system
Known characters have percentage bonds.
- scenes can unlock characters
- social options change relationship values
- stronger relationships unlock Ask Out
- many character interactions are randomized from templates

### 5. Crime heat and arrest system
Criminal choices increment `crimeHeat`.
- some actions cause immediate arrest
- repeated crimes cause guaranteed arrest once threshold is reached
- arrest shifts the rest of the loop into jail scenarios

### 6. Injury / healing system
Fights can injure the player.
- injury disables some physical actions
- doctor location can cure injury
- injury can persist across resets if untreated

### 7. Location travel system
The notebook map lets the player jump to specific places.
- travel changes the scenario pool
- location persists until manually leaving
- each location has its own tone and event set

### 8. Feedback and presentation system
The game reinforces outcomes with:
- toast text
- sound effects
- animated reaction GIFs for good/bad social beats
- icon warnings for injury and wanted status
- night mode in evening scenes

## Inferred genre / gameplay shape
Strongest inferred shape:

- **choice-based life simulator / school social loop**
- with **story-choice** and **light stat-management** elements
- framed as a **time-loop day sim**
- presented like a compact comedic visual novel without long-form dialogue trees

This is not an action game or simulation in the physics sense. It plays more like a humorous branching day-planner where each tap spends one action and nudges social, moral, and consequence systems.

## Gameplay heuristic
A likely effective player strategy is:
1. favor positive karma choices to avoid spiraling downward
2. meet characters early to unlock more notebook interactions
3. use compliments/chat to build one key relationship above 50
4. avoid crimes unless intentionally chasing a chaos run
5. visit the doctor if injured
6. use location travel for variety and access to healing or safer events
7. treat the loop as replayable experimentation, learning which decisions are wholesome, risky, or romantic

## Tone and presentation inference
The game is playful, mischievous, and teen-comedy oriented:
- school-life setting
- doodle/notebook UI
- emoji-led scenes
- exaggerated consequences like jail, broken bones, and mystery stew
- romance and social embarrassment mixed with low-stakes chaos

Overall, it feels like a **comedic school-day karma sandbox** built around repeated short runs and expressive binary-to-messy choices.