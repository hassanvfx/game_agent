# Visual UI Redesign State Map

Runtime basis:
- Validation URL: `http://127.0.0.1:43100/index.html`
- Mobile viewport: `400x700`
- Baseline screenshots:
  - `previsual_screen_01_title_or_entry.png`
  - `previsual_screen_02_live_play.png`
  - `previsual_screen_03_menu_or_modal.png`
- Runtime observation: `previsual_runtime_observation.json`

## 1. Title / attract

Observed focal anchor:
- Wand-and-pixie crest centered in the start card.
- Hogwarts copy reads clearly and matches the remix theme.

Main UI message:
- Start a magical pest-control drill.

Assessment:
- Clear, but text block and button treatment can be tighter and more premium.
- CTA appears reachable at 400x700.
- Overlay is readable, though panel weight is a little heavy.
- Theme language is consistent.

Current layout sketch:
```text
┌──────────────────────┐
│ ambient castle sky   │
│      [hero crest]    │
│  Hogwarts Pest...    │
│  CORNISH PIXIE PANIC │
│  multicolor divider  │
│  2-line instructions │
│ [ BEGIN THE DRILL ]  │
└──────────────────────┘
```

Reduced layout sketch:
```text
┌──────────────────────┐
│ ambient castle sky   │
│     [hero crest]     │
│  Hogwarts Pest Ctrl  │
│  CORNISH PIXIE PANIC │
│     slim divider     │
│ Drag to banish       │
│ [ Start Drill ]      │
└──────────────────────┘
```

## 2. Ready / start transition

Observed focal anchor:
- Start button and center card.

Main UI message:
- Tap to begin.

Assessment:
- Reachability is safe.
- Minimal room to improve by reducing copy and tightening top/bottom padding.
- No obvious overlap in the baseline state.

Current layout sketch:
```text
┌──────────────────────┐
│ overlay card         │
│ title + body + CTA   │
└──────────────────────┘
```

Reduced layout sketch:
```text
┌──────────────────────┐
│ slimmer card         │
│ title + short hint   │
│ clear CTA            │
└──────────────────────┘
```

## 3. Active play

Observed focal anchor:
- Hand/ward playfield and moving pixies.
- HUD at top, tier badge at upper right.

Main UI message:
- Protect ward integrity while dragging pixies away.

Assessment:
- Gameplay remains dominant.
- HUD and progress badge likely crowd the upper band on smaller screens.
- Label language is mostly on-theme, but hierarchy can be cleaner.
- Reaction cards at bottom-right are readable but can be more compact.
- Control zones appear reachable and unobstructed.

Current layout sketch:
```text
┌────────────────────────────┐
│ [wide HUD bar...........]  │
│                [tier box]  │
│                            │
│     gameplay / hand        │
│     + pixies + effects     │
│                            │
│                 [react fx] │
└────────────────────────────┘
```

Reduced layout sketch:
```text
┌────────────────────────────┐
│ [compact HUD]  [tier box]  │
│                            │
│      larger play area      │
│      clearer top margin    │
│                            │
│              [small react] │
└────────────────────────────┘
```

## 4. Pause

Observed focal anchor:
- No dedicated pause state present.

Main UI message:
- Not applicable.

Assessment:
- Preserve current behavior; do not add a new pause mechanic in this stage.

Current layout sketch:
```text
N/A
```

Reduced layout sketch:
```text
N/A
```

## 5. Win

Observed focal anchor:
- No win screen observed in this endless-flow build.

Main UI message:
- Not applicable.

Assessment:
- Preserve endless progression semantics; no win-state invention.

Current layout sketch:
```text
N/A
```

Reduced layout sketch:
```text
N/A
```

## 6. Lose / fail

Observed focal anchor:
- Centered fail card with restart CTA.

Main UI message:
- Ward breach; try again.

Assessment:
- Theme fits the remix.
- Card can be slimmed and copy can be shortened for better scan speed.
- Restart CTA remains reachable at 400x700.

Current layout sketch:
```text
┌──────────────────────┐
│      WARD BREACH     │
│  2-line fail text    │
│ Pixies Banished: ##  │
│   [ CAST AGAIN ]     │
└──────────────────────┘
```

Reduced layout sketch:
```text
┌──────────────────────┐
│      WARD BREACH     │
│ Ward lost to pixies  │
│ Banished: ##         │
│   [ Cast Again ]     │
└──────────────────────┘
```

## 7. Restart / continue

Observed focal anchor:
- Restart button in fail card.

Main UI message:
- Retry immediately.

Assessment:
- Action stays reachable and clear.
- Touch target is already safe; visual polish should preserve current size.

Current layout sketch:
```text
┌──────────────────────┐
│ score line           │
│ [ restart button ]   │
└──────────────────────┘
```

Reduced layout sketch:
```text
┌──────────────────────┐
│ compact score line   │
│ [ restart button ]   │
└──────────────────────┘
```

## Key refinement targets

- Refine top HUD and tier badge so they read as one magical system without taking too much height.
- Shorten onboarding/fail copy to a faster, more premium command tone.
- Improve menu/button/card shape language toward arched spellbook panels instead of generic rounded capsules.
- Slightly reduce decorative weight where it competes with readability, while keeping the animated castle identity.
- Preserve gameplay area, drag semantics, score/health behavior, and start/restart reachability.