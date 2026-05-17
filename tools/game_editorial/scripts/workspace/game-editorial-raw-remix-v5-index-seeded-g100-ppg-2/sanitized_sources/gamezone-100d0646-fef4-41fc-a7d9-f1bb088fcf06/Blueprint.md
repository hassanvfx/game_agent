# Blueprint

## High-level code structure
The project is a single-file HTML game with embedded CSS and JavaScript. The structure is divided into four main layers:

1. **Presentation layer**
   - A full-screen HTML shell with a start screen, story card, HUD, feedback overlays, and ending screen.
   - Heavy use of inline CSS for a neon-glass arcade UI.
   - A background canvas provides animated ambience separate from the gameplay UI.

2. **Configuration layer**
   - A JSON config block embedded in the HTML defines editable values such as text speed, theme color, and hero name.
   - JavaScript reads this config at startup and exposes a small `updateGameConfig` hook.

3. **Audio/feedback layer**
   - Preloaded remote audio elements for background music and UI/event sound effects.
   - A fallback Web Audio synthesizer generates sounds if media playback fails.
   - Success/failure GIF overlays reinforce player choice feedback.

4. **Game logic layer**
   - A lightweight state object tracks `health`, `mood`, and the current story node.
   - A `storyNodes` object defines the narrative graph, choice branches, stat changes, and ending nodes.
   - Rendering functions update text, choices, bars, and ending results.

## Game loop / state model
This is not a physics-driven arcade loop; it is a **choice-rendering progression loop**:

1. Show current narrative node.
2. Type out the node text with a configurable typewriter effect.
3. Reveal 2 player choices.
4. On click:
   - play sound,
   - show particles,
   - show success/fail visual feedback,
   - modify health and mood,
   - update HUD bars,
   - move to the next node.
5. If the next node is an ending, or if health/mood reach zero, show a game-over / ending screen.
6. Player can restart and replay alternate branches.

The state model is very compact:
- `health`: physical stamina / energy
- `mood`: emotional resilience
- `node`: current position in the branching story graph

## Player goals
The player is trying to survive a chaotic Monday and reach a satisfying ending. More specifically, the player is balancing:
- **Energy/health preservation**
- **Mood preservation**
- **Short-term tactical choices**
- **Branch navigation toward favorable endings**

The player can succeed in several tones:
- survive the workday,
- become an office hero,
- escape into leisure,
- step away from work entirely.

Failure states happen through bad endings or by depleting health or mood.

## Interaction pattern
The interaction pattern is:
- tap/click to start,
- read a short scenario prompt,
- choose one of two options,
- observe immediate audiovisual/stat feedback,
- continue to the next branch.

There is no free movement, aiming, dragging, or timing challenge. The primary verb is **selecting narrative choices**. Replay value comes from trying different branches and endings.

## Core systems
### 1. Branching narrative graph
A hand-authored node map drives the full experience. Each node includes:
- text,
- emoji,
- two choices,
- destination node,
- stat deltas,
- flavor feedback message.

### 2. Dual-stat survival system
The game uses two visible meters:
- **Energy / health**
- **Mood**

These act as soft survival resources and create tension during otherwise simple narrative choices.

### 3. Ending resolution system
The game has authored endings such as:
- Fired
- Couch Potato
- Survived
- Office Hero
- Escapist
- Meltdown

It also includes stat-collapse endings:
- Exhausted
- Drained

### 4. Feedback juice system
Each choice is reinforced by:
- click/success/warning/fail sounds,
- celebratory or fail GIFs,
- screen shake on negative outcomes,
- particles from the clicked button,
- animated HUD bar changes.

### 5. Ambient presentation system
A looping parallax particle canvas and stylized glassmorphism UI create a playful “chaos arcade” wrapper around the story.

## Inferred genre / gameplay shape
The strongest inferred gameplay shape is a **short-form branching choice game / interactive story with light survival-stat management**. It also has some qualities of:
- story choice game,
- interactive novel,
- life choices simulator,
- light roleplay simulator,
- incremental story vignette.

It is not a simulation in a systems-heavy sense and not an arcade action game despite the arcade presentation. The real core is comedic branching narrative decision-making.

## Gameplay heuristic
A player who performs well will usually:
- avoid heavy mood crashes early,
- avoid choices with obvious overreaction or social self-sabotage,
- preserve enough energy to reach later scenes,
- choose stabilizing or socially positive options when available.

The design encourages reading the tone of each scene:
- impulsive, greedy, avoidant, or self-destructive choices usually hurt,
- calm, practical, or empathetic choices usually improve the odds,
- some “lazy” outcomes are framed as alternate wins rather than pure failure.

## Inference confidence
Confidence is **high** that the game is a branching narrative comedy about surviving Monday/workplace chaos, because the story graph, state variables, endings, and UI are all explicit in code.

Confidence is **moderate-to-high** that replayability is intended through multiple endings rather than deep strategy, because the total system scope is compact and centered on branching authored scenes rather than emergent mechanics.