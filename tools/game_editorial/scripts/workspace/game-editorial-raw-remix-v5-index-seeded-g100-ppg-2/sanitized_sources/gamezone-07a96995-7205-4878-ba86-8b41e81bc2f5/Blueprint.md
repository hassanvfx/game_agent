# Blueprint

## High-level code structure
- **Single-file web game** implemented entirely in `index.html`.
- **Three UI layers**:
  - a login screen that validates a player nickname before entering the app,
  - a faux chat/community interface with multiple channels,
  - a full-screen modal game overlay containing the actual arcade gameplay canvas.
- **Inline styling and Tailwind configuration** establish a futuristic neon dashboard/chat aesthetic.
- **Inline JavaScript** manages:
  - login and username filtering,
  - channel switching and chat rendering,
  - audio setup and playback,
  - arcade game initialization, input, entity spawning, collision handling, HUD updates, and win/fail flows.

## Game loop / state model
- **Meta-state flow**:
  1. Login screen
  2. Chat hub / event feed
  3. Launch run overlay
  4. Active run
  5. Fail retry or win reward state
  6. Return to chat with unlocked reward status
- **Persistent session state**:
  - `currentUser`
  - `currentChannel`
  - `hasWon`
- **Run state**:
  - player position, speed, health, invulnerability timer
  - scrolling road offset and gradually increasing road speed
  - active entities array for collectibles and obstacles
  - collected core count toward the target of 10
  - left/right input flags
- **Frame loop**:
  - `requestAnimationFrame(updateGame)`
  - scroll background road
  - process left/right movement
  - update invulnerability flicker
  - randomly spawn lane-based entities
  - move entities downward
  - render player, collectibles, and obstacles
  - resolve collisions
  - check win/loss conditions

## Player goals
- Enter the event feed, then launch the featured run.
- Steer the vehicle left and right across four lanes.
- Collect **10 energy cores** while avoiding construction barriers/obstacles.
- Preserve all 3 health points until the target is reached.
- On success, claim the reward and update the chat feed state.

## Interaction pattern
- **Pre-game UI**: click/tap login, channel items, launch/run buttons.
- **Gameplay controls**:
  - keyboard left/right arrows on desktop,
  - touch left/right halves of the canvas on mobile.
- **Feedback style**:
  - HUD counters for collected cores and health,
  - audio cues for start, collect, crash, fail, and win,
  - animated reaction GIFs for crash and victory,
  - chat feed changes after success to reinforce progression.

## Core systems
- **Identity/login gate** with restricted word filtering.
- **Chat-themed wrapper** that frames the game as a live event inside a social feed.
- **Lane runner driving system** with four lanes and increasing speed.
- **Spawn system** for collectible cores and damaging obstacles.
- **Collision and health system** with temporary invulnerability after hits.
- **Win/fail loop** with retry handling and a post-win reward claim.
- **Audio controller** that unlocks media after player interaction and throttles repeated SFX.
- **Responsive/mobile support** via touch input, mobile sidebar handling, and contained canvas interaction.

## Inferred genre / gameplay shape
- Primarily an **arcade lane-based avoidance-and-collection runner** presented inside a **mock social/chat interface**.
- It mixes:
  - **lane runner / endless runner** moment-to-moment mechanics,
  - **light arcade driving presentation**,
  - **meta UI dressing** that makes the run feel like a featured event in an online community.
- The experience is short-session, score/goal-driven, and casual rather than simulation-heavy.

## Gameplay heuristic
- Stay near the center unless a collectible or barrier forces a lane change.
- Favor safe collection over risky swerves because health is limited to three hits.
- As speed rises, early positioning matters more than reactive dodging.
- Winning depends on sustained lane discipline rather than precision physics or deep resource strategy.

## Confidence notes
- High confidence on the lane-runner and obstacle-dodging interpretation because the canvas logic explicitly uses four lanes, left/right steering, collectible count, health, and escalating speed.
- Moderate confidence on genre labeling between “lane runner,” “endless runner,” and “driving arcade game” because the game uses car visuals but the structure is simpler than a full racing game.
