# Blueprint

## Current game reality

### High-level code structure
- `index.html` provides a single-canvas arcade game shell with:
  - a full-screen `<canvas>` playfield
  - a HUD bar and score display
  - start and game-over overlay screens
  - reaction cards for success and danger feedback
- `assets/obfuscated/inline-script-001.js` contains the actual game logic:
  - global `State`
  - `Bug` and `Particle` classes
  - spawn, resize, UI update, drag handlers, start/end state transitions, and the frame loop
- `assets/obfuscated/inline-script-002.js` is a compatibility shim for audio objects and audio contexts
- `assets/obfuscated/inline-style-001.css` controls the menu cards, HUD, overlay styling, and mobile-safe layout

### Game loop / state model
The game is a one-screen survival loop:
1. Start screen opens with a single CTA.
2. Starting the run activates the canvas game state and clears prior entities.
3. Bugs spawn inside an ellipse positioned over a giant foot graphic.
4. The player presses on a nearby bug, drags it away, and releases.
5. If the drag distance is large enough, the bug is cleared.
6. If bugs remain too long, health drains.
7. When health reaches zero, the game ends and the game-over screen appears.

### Player goals
- Keep the health bar alive.
- Remove as many bugs as possible.
- Survive increasing spawn pressure.

### Interaction pattern
- Press near a bug to grab it.
- Drag to reposition it.
- Release after a large enough displacement to clear it.
- If the displacement is too small, the bug snaps back.

### Core systems
- Pointer/touch drag selection
- Continuous spawn timer with gradual difficulty increase
- Health drain from uncleared bugs after linger time
- Score increase and partial health restore on successful clears
- HUD updates and reaction callouts
- Start/game-over screen flow

### Inferred genre / gameplay shape
- Simple one-screen arcade cleanup game
- Touch-first survival pressure loop
- Reaction/timing game with direct manipulation rather than tap attacks

### Current identity summary
The source game presents as a neon dance-floor bug clearing game called **Beat Bug Blitz**. The fiction is “clear glitch bugs off the stage,” but the real mechanics are a drag-and-clear survival system centered on a giant foot-shaped target zone.

## Remix-direction summary

### Intended remixed trajectory
The Harry Potter prompt fits best as a **magical pest containment drill at Hogwarts**, not as a spell-combat rewrite.

Recommended remixed identity:
- The bugs become magical pests such as Cornish pixies, cursed beetles, or dark enchanted critters.
- The giant foot/ground plane becomes a bewitched footprint or containment sigil.
- The tweezers become enchanted containment tongs or levitation tongs.
- The HUD becomes a ward or shield stability meter.
- Clears become captures/containments.
- Failure becomes ward collapse or castle contamination.

### Why this direction is safe
It preserves:
- the drag gesture
- the one-screen canvas loop
- the survival pacing
- the score and health semantics
- the mobile input model

It changes only:
- fiction
- visual identity
- copy
- background worldbuilding
- readable thematic progression

## Preserve-vs-change guidance

### Preserve
These are protected mechanics and should remain effectively untouched downstream:
- drag-to-clear interaction
- press/move/release control semantics
- bug selection radius logic
- clear threshold distance logic
- health drain logic
- health restore logic
- score semantics
- spawn escalation architecture
- one-screen state flow
- mobile-first usability

### Change safely
These are safe theming surfaces:
- title and instructional copy
- creature design
- playfield/background styling
- HUD label wording
- reaction card images and text
- color palette and magical VFX framing
- level/world progression framing
- menu and game-over narrative language

### Do not overinterpret
Downstream stages should **not**:
- add spell buttons, mana bars, or projectile combat
- turn this into a runner, shooter, or lane game
- replace dragging with tapping
- rewrite the main loop or physics
- use franchise styling that reduces readability on mobile

## Five-level progression heuristic
The source game has no explicit levels, so the remix should define a safe conceptual five-level journey while reusing the same core survival system.

1. **Boot Room Induction**  
   Warm Hogwarts prep room. Basic magical pest containment framing.

2. **Moving Stair Mischief**  
   Corridor/staircase backdrop with stronger urgency and magical motion.

3. **Greenhouse Overflow**  
   Herbology setting with lush magical props and fuller thematic density.

4. **Forbidden Forest Edge**  
   Darker atmosphere and stronger warning-state tension.

5. **Battle of the Clock Tower**  
   Castle emergency finale with the highest readable visual stakes.

## 1.5-level core
- **Level 1** proves the base reskin works with no logic changes.
- **Level 1.5** proves progression can emerge from background evolution, creature styling, and stronger urgency cues without touching mechanics.

## Downstream execution heuristic
- Stage 1 should preserve mechanics and rewrite fiction/UI copy.
- Stage 2 should build a procedural Harry Potter-inspired art language and world-specific backgrounds.
- Stage 3 should refine readability, contrast, and polish.
- Stage 4 should verify that mechanics, mobile controls, and clarity remain intact.

## Confidence notes
Confidence is high on the mechanical interpretation because the code clearly shows:
- one drag verb
- one spawn loop
- one survival fail condition
- no hidden multilevel logic

Confidence is medium on the exact current fiction because the code is partially obfuscated, but the implemented behavior is still clear from the state loop, handlers, and UI text.