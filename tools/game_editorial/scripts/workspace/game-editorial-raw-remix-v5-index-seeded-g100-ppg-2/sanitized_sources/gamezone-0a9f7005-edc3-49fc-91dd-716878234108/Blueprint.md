# Blueprint

## High-level code structure
The project is a single-file mobile-first HTML application with inline CSS and JavaScript in `index.html`. It is organized into three broad layers:

1. **Shell / lobby UI**
   - Top header with branding, currency, and avatar.
   - Bottom tab navigation for Home, Profile, Messages, and Settings.
   - Screen containers that swap visibility by tab.

2. **Arcade overlay**
   - A full-screen `#game-layer` that appears above the lobby UI.
   - Canvas-based gameplay with a small HUD, start hint, and game-over modal.

3. **Client-side logic systems**
   - `app`: manages tabs, messages, chat overlay, settings, and game launching.
   - `audio`: handles background music and one-shot sound effects.
   - `mediaFx`: shows success/fail GIF reactions.
   - `gameEngine`: runs the canvas loop and hosts three microgames.

The code is not split into modules; all systems live in one document and communicate through shared globals.

## Game loop / state model
There are two nested state models:

### 1. App-level navigation state
The outer application acts like an arcade/social hub:
- `currentTab` tracks which screen is active.
- Settings track `sfx` and `music`.
- Messages and chat are lightweight mock social features.
- Launching a game reveals the game overlay without leaving the app shell.

### 2. In-game runtime state
`gameEngine` owns the currently active microgame:
- `active`: whether the canvas loop is running.
- `currentGame`: selected ruleset (`runner`, `pizza`, or `sword`).
- `score`: shared score value displayed as XP.
- `width` / `height`: canvas dimensions.
- Per-game state is stored directly on the engine object during initialization.

The loop is a standard `requestAnimationFrame` cycle:
1. Clear/fill background.
2. Update current game state.
3. Draw current game state.
4. Queue the next frame if still active.

Input is unified through touch and mouse events and forwarded to the current game via `input()` handlers.

## Player goals
The main player-facing goal is to enter short arcade challenges and score as highly as possible. The most emphasized experience is the featured game **Sky Sprint**, but the app also offers two additional mini-games.

Per game, the inferred goals are:
- **Sky Sprint**: stay alive by timing jumps across moving platforms and collect coins for score.
- **Snack Catch**: move a chef left/right to catch pizzas while avoiding bombs.
- **Signal Duel**: wait for the signal, then tap quickly at the correct moment to score reaction wins.

The meta-goal is not deep progression; it is quick-session score chasing inside a playful social arcade wrapper.

## Interaction pattern
The entire experience is designed around **one-thumb mobile interaction**:
- Tap cards and tabs in the lobby.
- Tap to jump in the runner.
- Touch left/right halves of the screen to move in the catcher.
- Tap only when prompted in the reaction duel.
- Use simple overlays for start, fail, retry, and exit.

The UX emphasizes fast entry, immediate feedback, bright arcade styling, and short repeatable play sessions.

## Core systems
### 1. Tabbed hub interface
A fake social/mobile platform structure frames the arcade:
- Home highlights featured content and quick challenges.
- Profile shows identity and stats.
- Messages opens a stylized chat thread.
- Settings controls audio behavior.

### 2. Microgame launcher
Game cards call `app.launchGame(gameId)`, which:
- shows the canvas overlay,
- starts audio transitions,
- passes control to `gameEngine.load(gameId)`.

### 3. Shared canvas engine
The engine provides:
- resize handling,
- input wiring,
- score tracking,
- restart/exit/game over handling,
- a generic animation loop.

### 4. Three microgame rulesets
Each ruleset supplies:
- `init(g)`
- `update(g)`
- `draw(g, ctx)`
- `input(g, type, x, y)`

This makes the structure closer to a tiny arcade cartridge collection than a single large game.

### 5. Audio feedback system
The audio layer supports:
- menu/game music swapping,
- unlock-on-first-interaction behavior,
- UI clicks,
- jump/collect/fail/win cues.

### 6. Visual feedback system
Success/fail GIF overlays reinforce arcade reward and failure moments without affecting gameplay controls.

## Inferred genre / gameplay shape
This is best understood as a **mobile arcade hub containing three hypercasual mini-games**, wrapped in a mock social-lobby presentation.

The dominant gameplay shape is:
- **Arcade portal / social shell**
- **Featured endless runner**
- **Secondary reflex-based mini-games**
- **Short-session, replay-heavy score attack**

The strongest core identity is the featured runner, but the shipped codebase behaves more like a **mini arcade collection** than a single standalone genre piece.

## Heuristic summary
- **Primary fantasy**: hanging out in a neon mobile arcade app and launching quick challenges.
- **Primary behavior**: tap-driven reflex play with instant retries.
- **Primary reward**: score gain, audiovisual feedback, and lightweight social flavor.
- **Progression shape**: session-based rather than persistent; difficulty ramps inside individual runs.
- **Design priority**: mobile-friendly responsiveness, clarity, and snackable arcade pacing.

## Confidence notes
Confidence is high on the structural reading because all systems are visible in one file. Confidence is moderate on the intended product identity because the app presents itself as a unified arcade/social experience while internally containing three distinct mini-games. The featured runner appears to be the intended flagship mechanic.