# Visual UI Redesign State Map

## Runtime grounding status
- Assigned validation URL: `http://127.0.0.1:43108/`
- Dedicated local server started on assigned port.
- Browser-grounded screenshot capture was **blocked** because no connected Playwright/MCP browser runtime was available in this node.
- This state map is therefore based on source inspection and the served runtime contract, not screenshots.

## 1. Title / attract

Reference:
- Source state: `#start-screen` visible by default
- Main copy: `HOGWARTS SPELLSTORM TRIAL`
- CTA: `Start Trial`

Current layout sketch:
```text
+----------------------------------+
|      Hogwarts Night Practicum    |
|    HOGWARTS SPELLSTORM TRIAL     |
|      [ First-Year Charms ]       |
|   Intro paragraph                |
|   [ instruction ] [ goal ]       |
|          [ Start Trial ]         |
|      mobile-safe hint line       |
+----------------------------------+
```

Reduced / refined layout sketch:
```text
+----------------------------------+
|      Hogwarts Night Practicum    |
|    HOGWARTS SPELLSTORM TRIAL     |
|      [ current chamber chip ]    |
|   One compact objective line      |
|   [ Cast ]       [ Goal ]         |
|          [ Start Trial ]         |
|          small safety hint       |
+----------------------------------+
```

Assessment:
- Main focal anchor: title + chamber chip
- Main UI message: start the magical trial and understand cast goal quickly
- Busy or clear: now compact and clear
- CTA/control safety: safe; primary button remains centered and large
- Reachability: preserved
- Copy risk: reduced from longer onboarding sentence to shorter direct summary
- Overlap/clutter: low
- 400x700 suitability: improved through shorter paragraph and two concise cards

## 2. Ready / start transition

Reference:
- Trigger: `#startBtn` click
- Result: start screen hidden, HUD shown, game initialized

Current layout sketch:
```text
+---------------- gameplay ----------------+
| HUD appears top-left                    |
|                                         |
|      board + spell clusters             |
|                                         |
| control hint lower-left   mute lower-r. |
+-----------------------------------------+
```

Reduced / refined layout sketch:
```text
+---------------- gameplay ----------------+
| compact HUD with chamber + points       |
|                                         |
|      board remains dominant             |
|                                         |
| cast hint lower-left      mute lower-r. |
+-----------------------------------------+
```

Assessment:
- Main focal anchor: playfield and shooter pedestal
- Main UI message: drag to aim, release to cast
- Busy or clear: clear
- CTA/control safety: safe; hint is non-interactive and opposite mute button
- Reachability: preserved
- Copy risk: low
- Overlap/clutter: limited by keeping helper chip small
- 400x700 suitability: improved with compact corner hint

## 3. Active play

Reference:
- HUD built by `updateThemeHud()`
- Board rendered on canvas
- Touch/mouse aim semantics unchanged

Current layout sketch:
```text
+-----------------------------------------+
| [crest][chamber][points][subtitle][meta]|
|                                         |
|     spell orb grid / magical backdrop   |
|                                         |
|          launcher / aim line            |
| [drag-release hint]          [mute]     |
+-----------------------------------------+
```

Reduced / refined layout sketch:
```text
+-----------------------------------------+
| [crest][points + chamber + 2 pills]     |
|                                         |
|      board remains the visual focus     |
|                                         |
|         launcher and dashed aim line    |
| [cast hint]                    [mute]   |
+-----------------------------------------+
```

Assessment:
- Main focal anchor: board + active projectile
- Main UI message: score, chamber identity, next progression threshold
- Busy or clear: controlled; HUD is richer but still compact
- CTA/control safety: safe
- Reachability: preserved
- Copy risk: low; all labels are compact
- Overlap/clutter: low-medium, but acceptable because HUD remains a single top card
- 400x700 suitability: acceptable due compact pills and non-modal hint

## 4. Pause
- No pause state detected in current implementation.

## 5. Win / progression loop

Reference:
- Empty grid immediately calls `initGame()` again
- No dedicated win modal exists

Current layout sketch:
```text
+-----------------------------------------+
| combo feedback GIF / points increase    |
| board resets into next loop             |
+-----------------------------------------+
```

Reduced / refined layout sketch:
```text
+-----------------------------------------+
| combo feedback remains transient         |
| HUD progression pills explain chamber    |
| board resets without extra modal         |
+-----------------------------------------+
```

Assessment:
- Main focal anchor: combo feedback + refreshed chamber HUD
- Main UI message: points increased and trial continues
- Busy or clear: clear
- CTA/control safety: preserved
- Reachability: preserved
- Copy risk: none, no win modal
- Overlap/clutter: low
- 400x700 suitability: strong

## 6. Lose / fail

Reference:
- Trigger: bubble reaches fail threshold
- `#game-over-screen` shown, HUD hidden
- Restart button preserved

Current layout sketch:
```text
+----------------------------------+
|        Ward Collapse             |
|      Spell Line Breached         |
|   compact failure sentence       |
|    House Points   large value    |
|         [ Try Again ]            |
|   small reassurance copy         |
+----------------------------------+
```

Reduced / refined layout sketch:
```text
+----------------------------------+
|        Ward Collapse             |
|      Spell Line Breached         |
|      short recovery sentence     |
|      points as hero metric       |
|         [ Try Again ]            |
|      one-line semantic footer    |
+----------------------------------+
```

Assessment:
- Main focal anchor: failure title + score value
- Main UI message: failure occurred, restart is immediate
- Busy or clear: clear
- CTA/control safety: safe; restart remains centered and large
- Reachability: preserved
- Copy risk: reduced
- Overlap/clutter: low
- 400x700 suitability: improved by replacing plain score sentence with stronger score block

## 7. Restart / continue

Reference:
- Trigger: `#restartBtn`
- Result: game over screen hidden, HUD shown, `initGame()` called

Assessment:
- Main focal anchor: restart button
- Main UI message: try again with same mechanics
- Busy or clear: clear
- CTA/control safety: preserved
- Reachability: preserved
- Copy risk: low
- Overlap/clutter: low
- 400x700 suitability: safe

## Repair summary tied to this map
- Shortened title-screen instructions and split them into two scan-friendly cards.
- Added a low-footprint lower-left control hint during active play to support mobile-first comprehension.
- Strengthened HUD hierarchy with chamber progress, subtitle, and next-threshold indicator.
- Upgraded fail screen score presentation without changing fail/restart behavior.
- Kept mute button in the existing protected bottom-right corner and avoided gameplay-area obstruction.

## Remaining risks for final mobile repair
- No browser-grounded screenshots were available, so final visual clipping and exact safe-area behavior remain unverified.
- HUD width at very narrow devices should still be checked in-browser.
- Remote media load timing and GIF overlap should be smoke-tested once browser runtime access is available.