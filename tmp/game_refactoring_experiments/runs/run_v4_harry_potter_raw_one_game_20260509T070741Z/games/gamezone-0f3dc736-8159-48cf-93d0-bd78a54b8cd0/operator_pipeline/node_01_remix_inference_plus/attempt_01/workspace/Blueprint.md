# Blueprint

## Current game reality

### High-level code structure
- A single-file HTML game in `index.html` with inline CSS and JavaScript.
- The game uses one full-screen `<canvas>` for rendering and a lightweight DOM overlay for:
  - start screen
  - game-over screen
  - HUD score pill
  - mute button
  - celebratory / danger GIF feedback
- Core systems implemented in script:
  - `AudioManager` for music, SFX, mute handling
  - `Bubble`, `Projectile`, and `Particle` classes
  - grid creation, bubble matching, floating-cluster dropping, and game state transitions
  - pointer/touch drag-release aiming input
  - requestAnimationFrame update/draw loop

### Game loop / state model
- States: `START`, `PLAY`, `GAMEOVER`
- Player flow:
  1. open start screen
  2. tap start
  3. aim by dragging
  4. release to shoot one projectile bubble
  5. if 3+ connected same-color bubbles are formed, they pop
  6. disconnected clusters fall for bonus score
  7. if the field clears, the game restarts immediately as a looped win/reset
  8. if a landed bubble reaches too low on the board, game over appears
- Loop is a protected real-time arcade loop:
  - update projectile motion
  - detect wall bounce and grid collision
  - snap projectile to nearest valid grid slot
  - resolve matches and drops
  - draw background, board, launcher, projectile, particles, and aim guide

### Player goals
- Shoot colored projectiles into the hanging field.
- Create connected groups of at least 3 same-color bubbles.
- Clear the board and keep bubbles from reaching the loss line.
- Maximize score through pops and floating-cluster drops.

### Interaction pattern
- Touch/mouse drag to set shot angle.
- Release to fire.
- No directional movement avatar, no inventory, no menu-heavy complexity.
- This is a one-screen arcade puzzle shooter.

### Core systems
- Hex-like staggered grid adjacency model
- Bounce-shot projectile physics
- Match-3 cluster resolution
- Floating cluster detection from roof connectivity
- Score update system
- Loss when stack reaches bottom threshold
- Auto-reset on board clear
- Responsive resize and mobile-safe touch routing
- Audio and feedback GIF support

### Inferred genre/gameplay shape
- Strongest match: bubble shooter / one-screen arcade puzzle-action hybrid
- It behaves like a classic drag-aim-release color matching board clearer with mild combo reward emphasis.

### Current identity summary
- Current presentation is sci-fi / aurora / signal-relay themed.
- Signal orbs, storm interference, beacon grid, aurora dispatch framing.
- Existing identity is cosmetic and can be remixed without touching protected mechanics.

## Intended remixed trajectory: Harry Potter

### Remix direction summary
The safest and strongest remix is to reinterpret the bubble shooter as a **Hogwarts spell-combination duel chamber**:
- the launcher becomes the player wand / wand focus at the bottom
- projectiles become spell or potion orbs
- the hanging grid becomes enchanted spell clusters, cursed charms, or floating potion globes
- pops become spell-chain dispels
- floating drops become unsupported cursed clusters collapsing away
- win loop becomes clearing the chamber and advancing to the next magical lesson/trial conceptually
- failure becomes magical overload reaching the student line

This direction preserves the exact mechanics while making the game immediately recognizable under the Harry Potter prompt.

## Preserve vs change guidance

### Preserve absolutely
- Drag-to-aim, release-to-fire controls
- Bounce-shot projectile behavior
- Grid shape and adjacency logic
- Match threshold of 3
- Score semantics:
  - popped matches = 10 points each
  - dropped floating bubbles = 20 points each
- Win/loss semantics
- Immediate board reset on full clear
- One-screen arcade format
- Main loop, collision model, and rendering architecture
- Mobile-safe input arrangement
- Start / play / game-over state flow

### Safely change
- Title, copy, lore framing, labels
- Color interpretation of bubble types
- Visual motif language
- HUD wording
- Background world identity
- Audio mapping to approved magical / mystical categories
- GIF mappings to celebratory / fail reactions from approved catalog
- Procedural art style of bubbles, launcher, sky overlay, particles, and scene dressing
- Conceptual five-level progression plan for downstream implementation

### Tiny safe repairs only if later stages need them
- Media remapping to approved catalog URLs
- Cosmetic clarity improvements
- Readability improvements for theme consistency
- Non-mechanical HUD wording cleanup

## Mechanic and remix heuristic
This game does **not** need new mechanics to feel more Harry Potter.
It needs:
- stronger magical school framing
- distinct Hogwarts-like lesson / trial progression across five conceptual levels
- clearer magical object language for colors
- stronger world evolution from classroom to forbidden chamber-style magical escalation
- procedural wizarding motifs layered on existing rendering

## Downstream emphasis
Later stages should prioritize:
1. thematic re-skinning of existing bubble/orb language into wizarding spell objects
2. stronger magical background and HUD identity
3. five-level progression framing without mechanical breakage
4. procedural magical art over pasted stock franchise art
5. approved catalog media only

## What must not be overinterpreted
- Do not turn this into a roaming wizard action game.
- Do not add character movement, spell inventory, enemy AI, mana systems, or dialogue trees.
- Do not force broom flight, house sorting systems, or narrative traversal mechanics.
- Do not rewrite it into a platformer, runner, or combat arena.
- Do not replace the board-clearing loop; only reinterpret it.