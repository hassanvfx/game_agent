# Blueprint

## High-level code structure
The game is implemented as a single self-contained HTML document with inline CSS and JavaScript. It combines:
- a full-screen canvas used for the scenic background and character rendering
- layered HTML UI for menus, dialogue, choices, ending screens, mute control, and reaction stickers
- embedded story data objects that define dialogue text, branching choices, endings, and scene composition
- a lightweight audio controller for music loops and sound effects
- a simple asset preload step for remote background and character images

The overall structure is data-driven. Story content lives in `STORY`, visual scene composition lives in `SCENE_GRAPH`, and the runtime engine reads both to decide what to render and which interaction comes next.

## Game loop / state model
This is not a physics or action game loop. It is a narrative scene runner with a continuous render loop.

### Continuous loop
- `requestAnimationFrame(draw)` continuously repaints the canvas
- the draw loop renders the current background and character sprites
- character positions and opacity are interpolated each frame for soft transitions

### State model
Runtime state is stored in a single `state` object:
- `lang`: current language, effectively English in this build
- `node`: current story node id
- `typing`: whether the typewriter effect is actively revealing text
- `textIndex` and `timer`: typewriter progress
- `chars`: active on-canvas character instances with target position, scale, and alpha
- `muted`: audio enabled/disabled
- `loaded`: whether visual assets finished preloading
- `feedbackTimer`: controls temporary GIF reaction overlays
- `currentEndingMood`: chooses the active music loop

### Node flow
The story advances through named nodes such as:
- `start`
- `meet_leo`
- `choice_1`
- `sit_down`
- `choice_2`
- `good_ending_path`
- `end_good`

Each node can contain:
- dialogue text
- a speaker name
- optional choices
- a next node
- a scene definition with background and visible characters
- an ending marker

### Input flow
- Start button begins the scene
- Pointer/tap anywhere advances dialogue when no choice overlay is open
- If text is still typing, a tap completes the current line instantly
- Choice buttons branch the story
- Restart returns to the start state after an ending

## Player goals
The player’s immediate goal is to move through a short romantic encounter in a park scene.

The inferred emotional goal is to decide how open, reserved, or private Mia will be during the meeting with Leo. The outcome is not score-based; instead it is expressed as tone and relationship warmth:
- positive outcome: collaborative connection
- neutral outcome: polite distance
- negative outcome: solitary ending

## Interaction pattern
The interaction model is a tap-through interactive dialogue scene with occasional binary choices.

Primary pattern:
1. Start the scene
2. Read text as it types in
3. Tap to advance
4. Make a dialogue choice when prompted
5. Continue through the resulting branch
6. Reach one of several ending cards
7. Restart if desired

This is closest to a compact visual novel or interactive story vignette rather than a systems-heavy simulator.

## Core systems
### 1. Story scripting
Dialogue, speakers, choices, and endings are encoded in static objects. This is the main content system.

### 2. Scene staging
`SCENE_GRAPH` determines:
- which background is shown
- which characters are present
- where they stand
- their scale and fade state
- what node follows next

### 3. Typewriter dialogue presentation
Each node’s text reveals character-by-character at a fixed speed. Input can fast-forward the current line.

### 4. Branching choice system
Certain nodes present two choice buttons. These route the player into different branches and eventually distinct endings.

### 5. Character portrait and speaker framing
A speaker name tag and circular avatar portrait mirror who is currently talking, reinforcing the visual-novel structure.

### 6. Reactive feedback layer
Choice selection triggers short sticker-like GIF feedback and matching success/fail style sound effects, giving lightweight emotional reinforcement.

### 7. Audio mood management
The game swaps between:
- main loop for the core scene
- victory-like loop for the best ending
- defeat-like loop for the most distant ending

### 8. Ending presentation
The final state shows a title and description summarizing the emotional result of the encounter.

## Inferred genre / gameplay shape
Primary inferred genre:
- interactive novel game

Secondary shape:
- story choice game
- chat simulator style conversational flow
- short romantic visual novel vignette

## Gameplay heuristic
The game is built around emotional branching, not mastery. A player is rewarded for openness and reciprocal engagement.

Heuristic summary:
- accepting contact moves the scene toward shared presence
- leaning into mutual exchange produces the strongest ending
- maintaining distance leads to quieter or lonelier resolutions
- the design encourages replay to sample all three emotional outcomes

## Presentation and tone
Presentation cues suggest a romantic, dreamy, moonlit panel aesthetic:
- soft neon-blue and pink glassmorphism UI
- cinematic layered background and character silhouettes
- sketchbook and story-panel language in text
- gentle music and reactive sticker overlays
- slow, intimate pacing centered on dialogue

## Confidence notes
Confidence is high that this is a short branching romance interaction scene with visual-novel framing. Confidence is lower on whether it is intended to be classified strictly as a visual novel versus a story-choice microgame, because the category universe does not include “visual novel” explicitly and the implementation is extremely lightweight.