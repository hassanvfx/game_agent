# Blueprint

## High-level code structure
- Single-file browser game implemented entirely in `index.html`.
- Three major layers live together:
  - **Presentation layer:** HTML overlays for start, HUD, game-over, and victory screens.
  - **Visual styling layer:** large inline CSS block defining the neon arcade look, responsive HUD, modal panels, and full-screen canvas behavior.
  - **Gameplay/runtime layer:** inline JavaScript that initializes assets, audio, feedback GIFs, canvas rendering, state variables, input handling, spawning, collision logic, and the main animation loop.
- No module system, build tooling, external framework, or multi-file architecture is present in the gameplay code. The game is effectively a self-contained canvas arcade prototype.

## Game loop / state model
- The game uses a **requestAnimationFrame-driven loop**.
- Core mutable global state includes:
  - `gameActive`
  - `day`
  - `weight`
  - `playerX`, `playerY`, `playerRadius`
  - `items`
  - `particles`
  - `explosionParticles`
  - combo/shake state such as `caughtStreak`, `shakeScreen`, `shakeIntensity`
- The loop flow is:
  1. Clear canvas.
  2. Draw arena/background.
  3. Update and draw decorative background particles.
  4. Apply temporary screen shake if active.
  5. Clamp and draw the player avatar near the bottom.
  6. Spawn falling items based on random chance and current day.
  7. Update/draw all falling items.
  8. Detect collisions with the player.
  9. Resolve food pickup, hazard loss, or victory at Day 99.
  10. Queue next animation frame if still active.
- Game states are effectively:
  - **Start / pre-run**
  - **Active play**
  - **Failure / run over**
  - **Victory / Day 99 celebration**

## Player goals
- Move horizontally to catch safe falling food.
- Increase the “Day” counter from 1 to 99 by collecting food.
- Avoid dangerous falling objects entirely because a single hazard pickup ends the run immediately.
- Survive long enough to complete the implied challenge run, framed as reaching “Day 99.”

## Interaction pattern
- Primary input is **horizontal pointer/touch tracking**:
  - Mouse movement on desktop
  - Touch dragging on mobile
- The player character does not jump, shoot, or perform multiple actions; the interaction is a **one-axis catch/dodge control scheme**.
- Sessions are fast, restartable, and arcade-like:
  - Start button
  - Instant loss on bad pickup
  - Immediate retry loop
  - One clear long-run win condition

## Core systems
- **Item spawning system**
  - Randomly spawns falling collectibles and hazards.
  - Spawn frequency scales slightly with day progression.
- **Collision system**
  - Radial overlap check between circular player body and falling item position.
- **Progression system**
  - Each food pickup increments day and weight.
  - Player radius grows slightly over time, implying visible character growth and increased collision footprint.
- **Risk/reward readability**
  - Food and hazards are distinguished using different emoji pools and glow colors.
- **Feedback system**
  - Audio controller handles BGM and one-shot SFX.
  - Feedback controller shows animated reaction GIFs for streak/combo moments and failure.
  - HUD updates live with day and weight.
  - Screen shake and explosion particles reinforce impact states.
- **Win/lose resolution**
  - Hazard collision triggers game over panel and stops the loop.
  - Reaching Day 99 triggers a celebratory explosion sequence and victory panel.

## Gameplay heuristic
- This is a **casual survival-catcher arcade game** with increasing pressure.
- The dominant heuristic is:
  - Stay near safe targets,
  - make small lateral adjustments,
  - avoid overcommitting when hazards share the lane,
  - and manage the increased difficulty caused by longer survival and a larger player hitbox.
- Because the character grows with success, the run subtly becomes harder over time even while the player is “powering up,” creating a humorous anti-power-fantasy tension.

## Inferred genre / gameplay shape
- Best described as a **single-screen arcade survival / dodge-and-collect game**.
- It also overlaps with:
  - lane-runner-like evasion,
  - wave survival pacing,
  - endless score-chase structure,
  - light reaction game design.
- Presentation suggests a playful meme-arcade tone rather than simulation or narrative depth.

## Presentation and tone
- Neon purple arcade backdrop, big comic-display title, emoji-based falling objects, and celebratory/failure overlays create a **flashy, humorous, snack-chaos aesthetic**.
- The phrase “Arcade Appetite: Day 99” frames the run like an exaggerated internet challenge.
- Tone is energetic, unserious, and immediate.

## Confidence notes
- High confidence on the one-axis catch/dodge gameplay loop, Day 99 objective, and failure condition because they are explicit in UI copy and collision logic.
- Moderate confidence on intended thematic reading of the hazard emojis; they function mechanically as instant-loss obstacles even if their fiction is slightly abstract.
- High confidence that the game is meant as a compact mobile-friendly arcade experience rather than a deep progression title.