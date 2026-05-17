# Blueprint

## High-level code structure
- **Single-page HTML shell**: `index.html` contains the entire visible shell, styling, UI overlay, media hooks, and runtime bootstrapping.
- **Canvas game core**: the actual gameplay is rendered inside a Construct 2 canvas (`#c2canvas`) driven by `c2runtime.js`, with jQuery handling resize and startup glue.
- **Decorative shell layer**: fixed-position DOM elements provide a candy-themed backdrop, mascot badge, HUD chips, and reaction card around the canvas without covering the playfield.
- **Media director layer**: inline JavaScript adds non-core audiovisual feedback through approved remote audio and GIF URLs. It reacts to generic pointer/click timing rather than deep game-state integration.
- **Mobile/input protection layer**: CSS and JS suppress touch gestures on the canvas, preserve fullscreen-style play, and pause/resume when the page visibility changes.

## Game loop / state model
Inferred loop:
1. The page loads a Construct 2 runtime and stretches the canvas to the full viewport.
2. The player begins interacting by tap, click, or swipe-like gestures on the board.
3. The runtime likely handles a **match-3 candy board** where pieces are swapped or selected to form rows/columns of matching candies.
4. Successful actions produce board clears, cascades, score gain, and likely combo chains.
5. The shell-level media system reacts loosely to interaction cadence:
   - first interaction unlocks music,
   - quick board interactions suggest collection,
   - periodic successful activity triggers combo celebration feedback,
   - idle/stalled interaction timing suggests a blocked or no-move state.
6. The session continues through repeated matching, collecting, and chain-making until a level target, score threshold, move limit, or similar milestone is reached.

## Player goals
- Match candy pieces into sets, most likely in groups of 3 or more.
- Trigger chain reactions and larger combos for better outcomes.
- Clear board states efficiently and avoid stalled patterns.
- Progress through increasingly demanding puzzle situations, likely with score or objective-based advancement.

## Interaction pattern
- Primary interaction is **direct board manipulation** on a portrait mobile-friendly canvas.
- Likely control scheme:
  - tap/select then swap,
  - or swipe adjacent candies to exchange positions.
- Feedback style is rapid and arcade-like: immediate audiovisual acknowledgement for matches, combos, and stalled states.
- The game appears intended to be readable in short sessions with lightweight onboarding and immediate action.

## Core systems
- **Construct 2 runtime system**: hidden internal logic for piece spawning, board validation, matching, clearing, scoring, and progression.
- **Board interaction system**: pointer-driven candy selection/swapping on the canvas.
- **Cascade/combo system**: inferred from “sweet chain landed” messaging and celebration feedback.
- **Collection/score feedback system**: inferred from “candies collected” event text and pickup sound design.
- **Blocked-state hinting**: inferred from “shuffle stalled — try a new candy lane,” suggesting no-move or failed-action moments.
- **Ambient presentation system**: looping arcade ambience plus polished shell visuals frame the game as a lively candy puzzle.
- **Visibility suspension system**: pauses runtime/audio when the tab is hidden, suitable for mobile/browser play.

## Inferred genre / gameplay shape
- **Primary genre**: Match-3 puzzle game.
- **Gameplay shape**: level-based or score-chasing candy board puzzler with bright arcade feedback, short interaction cycles, and combo emphasis.
- **Platform assumption**: browser/mobile web casual game in portrait orientation.
- **Session feel**: quick, accessible, replayable, and feedback-heavy rather than narrative-driven.

## Confidence notes
- **High confidence**: candy theme, match-3 identity, portrait casual puzzle framing, direct board interaction, combo-oriented feedback.
- **Medium confidence**: progression is level-based rather than endless; there may be score/move/time targets.
- **Low confidence**: exact underlying Construct 2 rules, booster systems, level map structure, and win/fail conditions are not visible because `c2runtime.js` is not present in the working clone.