# Blueprint

## High-level code structure
This game is implemented as a single self-contained `index.html` document with three tightly coupled layers:

1. **Presentation layer (HTML/CSS)**
   - A full-screen chat UI styled like a futuristic messenger.
   - A header framing the experience as a live relay channel.
   - A scrolling message feed with user and guide messages.
   - A bottom text input and send button.
   - Floating feedback widgets showing route/chat confirmation and channel status.

2. **Visual simulation layer (Canvas)**
   - A fullscreen canvas rendered behind the chat interface.
   - A neon-grid backdrop with a single avatar/courier marker.
   - The avatar smoothly moves toward tapped destinations.
   - Small particle effects reinforce chat prompts and route changes.

3. **Interaction/audio layer (JavaScript)**
   - Simple state setup (`INIT` -> `PLAYING`).
   - Resize handling, animation loop, and audio unlock logic.
   - Tap-to-reroute movement on the canvas.
   - Text-chat handling with canned responses and streamed AI-style output.
   - Status chip updates, GIF/feedback flashes, vibration, and sound cues.

## Game loop / state model
The game uses a lightweight realtime loop driven by `requestAnimationFrame`.

### Core state
- `gameState`: mostly `INIT` then `PLAYING`
- `world.avatar`: current position, target position, state, mood
- `world.particles`: transient feedback particles
- chat state:
  - `isGenerating`: blocks user spam while the guide is “typing”
  - message DOM acts as the visible conversation log
- audio state:
  - Web Audio buffers
  - BGM playback / suspension behavior
  - per-SFX cooldown map

### Loop behavior
Each frame:
1. Compute delta time.
2. If in `PLAYING`:
   - update avatar movement toward target
   - occasionally choose a random idle wander target
   - update and expire particles
   - redraw the background grid, avatar, halo, and particles

This is not a win/lose loop. It is a **continuous ambient interaction loop**:
- tap field -> courier reroutes
- send text -> guide replies
- observe motion/audio/status feedback
- repeat

## Player goals
The player goal is soft and expressive rather than score-based:

- keep the “relay” active
- direct the courier by tapping the field
- converse with the guide to maintain the fiction of an active night shift channel
- enjoy the audiovisual feedback of movement, typing, status shifts, and ambient neon motion

There is no explicit victory condition, fail state, timer, score, or level progression in code. The game is more about maintaining flow and roleplay presence than completing objectives.

## Interaction pattern
Primary interaction is split between two modes:

1. **Chat interaction**
   - Type short prompts into the text box
   - Press Enter or tap send
   - Receive a delayed, streamed response from the guide
   - Certain keywords trigger more specific replies and particles

2. **Direct field interaction**
   - Tap/click the canvas
   - The runner’s target position changes to the tapped point
   - Route SFX, status update, and route feedback visual are triggered

This creates a hybrid pattern:
- **chat simulator feel** for narrative flavor
- **light toy-like movement control** for tactile agency

## Core systems
### 1. Canvas courier movement system
- A single avatar interpolates toward a target coordinate.
- Speed is configurable through embedded game config.
- Idle behavior causes occasional autonomous wandering.
- Visual facing/halo effects imply momentum and direction.

### 2. Chat roleplay system
- User messages are appended instantly.
- Guide replies are generated from keyword checks plus fallback lines.
- AI reply text is streamed character by character to simulate live typing.
- Emphasis formatting converts `*action text*` into italic roleplay narration.

### 3. Feedback system
- Status chip changes state labels such as `standby`, `live`, `route locked`, `relay typing`, `relay clear`.
- Route and chat feedback images briefly animate in/out.
- Particles spawn for certain recognized prompts or routing events.

### 4. Audio/haptics system
- Background music loop for ambience.
- Short UI SFX for click/type/route/error.
- Audio context is unlocked on first interaction.
- Optional vibration/haptic bridge is triggered on completed reply.

### 5. Responsive/mobile-safe input system
- Pointer handling carefully avoids blocking text input.
- Resize observer keeps canvas matched to viewport.
- Input field auto-expands with content.
- Layout and safe-area padding suggest mobile-first intent.

## Inferred genre / gameplay shape
Strongest inference: this is a **chat simulator / interactive ambient toy** with light rerouting mechanics.

A more descriptive genre phrase would be:
**“neon chat toy with guided courier routing”**

It borrows from:
- chat simulators / interactive fiction presentation
- casual tap-to-move toys
- ambience-forward UI sandbox experiences

It does **not** behave like a traditional runner, survival game, shooter, or puzzle game because:
- there are no hazards, obstacles, goals, or failure
- no scoring or level advancement
- no precision timing challenge
- movement is freeform and low-pressure

## Gameplay heuristic
The intended player experience appears to be:

- enter a stylish cyber-night-shift communication channel
- issue messages to a fictional guide
- redirect a courier around a neon signal field
- enjoy immediate sensory feedback and the illusion of a live relay operation
- remain in a calm, continuous, low-stakes loop

The design is strongest as an **immersive mood piece** with small interaction verbs rather than a deep mechanical challenge.

## Confidence notes
Confidence is high on:
- architecture
- core interaction model
- lack of explicit win/loss progression
- chat-simulator framing

Confidence is moderate on:
- whether the intended fantasy is “runner”, “courier”, or “relay operator” first, because the code blends all three labels

Confidence is low on:
- any hidden long-term progression, because none is present in code
- classification as a formal “game” versus polished interactive toy, since it sits between both