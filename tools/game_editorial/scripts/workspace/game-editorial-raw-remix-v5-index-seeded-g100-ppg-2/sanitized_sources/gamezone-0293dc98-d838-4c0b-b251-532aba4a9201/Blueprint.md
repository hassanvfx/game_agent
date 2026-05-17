# Blueprint

## High-level code structure
- Single-file browser game implemented in `index.html`.
- Structure is split into:
  - HTML UI overlays for start menu, HUD, shop, chat, cheat menu, creator/paint screen, sandbox editor, and result screen.
  - CSS for arcade/glassmorphism styling, responsive safe-area support, and micro-animations.
  - Inline JavaScript containing all gameplay systems and render logic.
- Core JavaScript modules are lightweight object literals:
  - `PlayerData` for local persistence of coins, unlocks, and custom art
  - `PaintSystem` for player-made pet/guard graphics
  - `Sandbox` for custom guard placement
  - `ChatSystem` for simple keyword-based flavor chat
  - `AudioSys` for music/SFX loading and fallback synth sounds
  - `CheatSystem` for ghost/turbo modifiers
- Main gameplay rendering uses a single `<canvas>` plus DOM-based HUD and modal overlays.

## Game loop / state model
### Primary states
- `START`: title/menu hub with difficulty, shop, creator, sandbox, cheats, and chat access
- `PLAY`: active round where the player pets the dog and avoids detection
- `EDITOR`: sandbox mode for placing/removing guards
- `CREATOR`: paint/upload mode for custom dog or guard skins
- `LEVEL_TRANSITION`: brief win/reward interstitial before next level
- `LOSE`: failure state after being spotted

### Loop behavior
- Continuous `requestAnimationFrame` loop calls:
  - `update(dt)` for simulation
  - `draw()` for canvas rendering
- During play:
  - Holding pointer/space enables petting
  - Petting fills the calm meter (`score`)
  - Guard states cycle between `SAFE -> WARN -> LOOK -> SAFE`
  - If the player pets while a guard is fully in `LOOK`, the run fails unless ghost cheat is active
  - Reaching 100% calm triggers level completion
- Difficulty modifies patrol speed and reward values.
- Standard mode auto-progresses to higher levels with more/faster guards.
- Sandbox mode reuses the same play loop but with custom-placed guards and returns to editor after verification/failure.

## Player goals
- Calm the dog completely by petting during safe windows.
- Stop petting before guards fully turn and shine their surveillance beam forward.
- Survive successive rounds to earn coins/tokens.
- Spend coins on dog skins or create custom dog/guard visuals.
- Optionally design and test custom patrol layouts in sandbox mode.

## Interaction pattern
- Core interaction is hold-to-act / release-to-hide.
- Inputs:
  - Pointer/touch on canvas to pet
  - Spacebar as alternate pet input
  - Menu buttons for meta systems
  - Tap placement in sandbox editor
  - Drawing/upload actions in creator tools
  - Text input in chat overlay
- The loop is readable and casual:
  - watch patrol tell
  - hold to fill meter
  - release on danger
  - repeat until full

## Core systems
### Stealth-petting mechanic
- Main mechanic is risk-managed affection.
- Petting grows score and dog happiness, generating hearts and positive feedback.
- Guard sight cycles punish overextending.

### Patrol AI rhythm
- Each guard has a simple timed finite-state cycle.
- `WARN` telegraphs danger before `LOOK`, giving the player a reaction window.
- Level count and chosen difficulty scale the tension.

### Progression and economy
- Winning gives coins based on difficulty unless cheats are active.
- Levels increase guard count up to a cap and make timing harsher through speed scaling.
- Shop unlocks cosmetic dog skins only; progression is mostly score/endurance plus cosmetic collection.

### Creative/social side systems
- Paint/upload editor for pet and guard portraits
- Sandbox custom-level style guard placement
- Flavor chat with “Night Watch”
- Optional cheat toggles

### Audio/feedback layer
- Remote audio assets for music, UI, reward, fail, and warning cues
- GIF overlays for love/success and alert/failure
- Heart/confetti particles and HUD bar feedback

## Inferred genre / gameplay shape
- Primary genre: casual timing-based stealth game.
- Secondary shape: arcade survival / reaction game with light cosmetic progression.
- The closest play fantasy is “pet the dog only when authority is not looking.”
- Despite extra menus, the heart of the game is a compact stealth-timing minigame rather than a deep simulator or story game.

## Gameplay heuristic
- The player should read the guards’ warning state as the main telegraph.
- Optimal play is short, repeated bursts of petting rather than constant holding.
- Difficulty increases pressure through faster cycles and more simultaneous guards.
- Cosmetic systems, chat, and sandbox editor broaden engagement but do not redefine the core loop.

## Confidence notes
- High confidence on the main loop, state machine, reward structure, and cosmetic systems because they are explicit in code.
- Medium confidence on exact intended fantasy wording because the game theme mixes “police/guard patrol” framing with a playful comfort-drill tone.
- Low uncertainty overall: the game is mechanically clear even if its narrative framing is eccentric.
