# Blueprint

## High-level code structure
- A single self-contained `index.html` file implements presentation, UI, and story orchestration.
- CSS defines a cinematic, gothic visual novel interface with a fullscreen video stage, overlay HUD, bottom-anchored choice buttons, progress dots, animated transitions, and an ending screen.
- HTML provides a small set of fixed UI layers:
  - fullscreen video container and `<video>` element
  - tap-to-start play gate / cover screen
  - pause button
  - progress tracker
  - feedback HUD with scene label and decision badge
  - dynamic choice container
  - transition flash
  - GIF reaction overlay
  - replayable ending screen
- JavaScript acts as a lightweight narrative engine that sequences six pre-rendered video scenes, waits for scene endpoints, presents binary choices, updates UI state, and plays approved remote audio/GIF feedback.

## Game loop / state model
The game behaves like a compact episode-based interactive novel:
1. Player sees a branded start gate with poster art and taps to begin.
2. Audio is unlocked, the first video scene starts, and ambience begins looping.
3. The engine waits until a scene reaches its stopping point.
4. A two-choice prompt appears.
5. The player taps one option, which records only that a decision was made, not a branching path.
6. The next predetermined scene video loads and plays.
7. This repeats across a fixed sequence of six scenes.
8. The final scene plays to completion, then the episode-complete overlay appears with a replay button.

Primary tracked state inferred from code:
- `currentSceneIndex`: current story segment / progress position
- `choiceCount`: number of choices confirmed so far
- `isPaused`: pause UI state
- `audioUnlocked` / `audioEnabled`: browser-safe audio gating
- HUD and overlay visibility classes controlling moment-to-moment interaction mode

This is effectively a **linear state machine with choice pauses**, not a true branching narrative graph.

## Player goals
- Progress through a melodramatic mystery episode titled **House of Secrets**.
- Make repeated dramatic choices at cliffhanger moments.
- Witness the full reveal/resolution by completing all scenes.
- Optionally replay the episode after completion.

## Interaction pattern
- Primary interaction is tap/click.
- The experience is mostly passive viewing interrupted by short decision points.
- Choices are binary, large, mobile-friendly buttons presented at the bottom of the screen.
- A pause/resume button provides minimal playback control during active scenes.
- No free movement, simulation, or systemic world manipulation is present.

## Core systems
### 1. Scene sequencing system
- `story()` chains scene playback and choice prompts in a fixed order.
- `playClip()` swaps the current video source, flashes the screen, updates progress state, and resumes playback.
- `waitEnd()` supports either freezing near a scene endpoint or waiting for a full video end event.

### 2. Choice presentation system
- `ask()` dynamically creates two buttons for the current decision.
- Selections advance the story but do not alter which next scene plays.
- The game uses choices for emotional participation and pacing rather than branching outcomes.

### 3. Feedback / drama signaling system
- Scene labels and progress dots communicate advancement through the episode.
- A decision badge shifts between warning/success tones.
- GIF overlays emphasize “decision made” and “secret revealed” beats.
- A transition flash punctuates scene changes.

### 4. Audio system
- Approved remote audio is used for start, choose, tension, reveal, pause, resume, completion, and looping ambience.
- Audio is unlocked only after user interaction, indicating mobile/browser compatibility awareness.
- `safePlay()` and cooldown logic reduce autoplay failures and sound spam.

### 5. Episode framing / replay system
- The start gate frames the game like an episodic chapter.
- The end screen confirms completion and offers a hard reload replay flow.

## Inferred genre / gameplay shape
- Strongest reading: **interactive novel / story choice game**
- Secondary reading: **light chat-simulator-style drama episode** because the player mostly reacts to social conflict rather than manipulating a world
- Presentation style: mobile-first, short-form, episodic, streamer/social-drama flavored visual story
- Structural shape: a **linear cinematic story with binary decision checkpoints**

## Gameplay heuristic
This game is best understood as a **tap-through drama episode**:
- watch a short pre-rendered cutscene
- absorb a heightened emotional cliffhanger
- choose between two dramatic responses
- receive audiovisual feedback
- continue to the next scene until the episode resolves

The fun comes from:
- soap-opera escalation
- curiosity about family conflict and hidden motives
- feeling involved through repeated decision confirmations
- polished audiovisual pacing rather than deep branching or mechanical mastery

## Confidence notes
- Confidence is high that the project is intentionally a linear interactive-video story.
- Confidence is moderate that the “choices” are mostly cosmetic because every selection resolves to the same next clip and there is no branch state storage.
- Confidence is lower on the exact fictional lore because the source scenes are referenced video files not visible in the current workspace listing, so narrative specifics are inferred from cut-map comments, labels, and UI copy.
