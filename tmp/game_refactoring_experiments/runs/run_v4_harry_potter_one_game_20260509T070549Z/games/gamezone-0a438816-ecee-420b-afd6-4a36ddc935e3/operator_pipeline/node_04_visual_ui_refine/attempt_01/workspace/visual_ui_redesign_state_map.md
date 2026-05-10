# Visual UI Redesign State Map

Runtime basis:
- Validation URL: `http://127.0.0.1:43107/`
- Mobile context: Playwright Chromium, `400x700`, touch enabled
- Baseline screenshots: `previsual_screen_01_title_or_entry.png`, `previsual_screen_02_live_play.png`
- Post-change screenshots: `postvisual_screen_01_title_or_entry.png`, `postvisual_screen_02_live_play.png`
- Layout metrics: `visual_validation_metrics.json`

## Title / Attract
Observed state:
- Main focal anchor: wand-and-pixie hero crest inside the centered menu card
- Main UI message: start the Hogwarts containment drill
- Busy or clear: moderately busy before; clearer after copy reduction and tighter panel height
- CTA/control zones safe: yes; start button remains above the fold at `bottom ~576.8`
- Reachability: start remains fully visible and tappable
- Copy issues: reduced from two longer lines to two short imperative lines plus one compact supporting note
- Overlap/clutter: reaction stack visually demoted during overlays
- Gameplay area space: overlay remains compact enough to preserve scene context
- 400x700 strength: safe after HUD width correction from full-bleed to inset width

Current layout (baseline):
```text
┌────────────────────────────────────┐
│ full-width HUD                     │
│                                    │
│         big themed card            │
│         title + ribbon             │
│         longer instructions        │
│         large CTA                  │
│                            alerts  │
└────────────────────────────────────┘
```

Reduced minimalist layout (implemented):
```text
┌────────────────────────────────────┐
│ inset HUD + year chip + hint       │
│                                    │
│        compact magical card        │
│        title + level ribbon        │
│        short action copy           │
│        one-line support note       │
│        primary CTA                 │
│                          dim alerts│
└────────────────────────────────────┘
```

## Ready / Start
Observed state:
- Main focal anchor: menu card and Begin Patrol button
- Main UI message: drag pests clear of the ward
- Busy or clear: clear
- CTA/control zones safe: yes
- Reachability: safe for thumb interaction
- Copy issues: addressed with shorter directive copy
- Overlap/clutter: no blocking overlap found
- Gameplay area space: preserved
- 400x700 strength: strong

Current layout:
```text
┌────────────────────────────────────┐
│ HUD                                │
│ menu card                          │
│ explanatory copy                   │
│ Begin Patrol                       │
└────────────────────────────────────┘
```

Reduced minimalist layout:
```text
┌────────────────────────────────────┐
│ HUD + compact hint                 │
│ menu card                          │
│ 2 short instruction lines          │
│ one small support line             │
│ Begin Patrol                       │
└────────────────────────────────────┘
```

## Active Play
Observed state:
- Main focal anchor: gameplay canvas with top ward HUD
- Main UI message: maintain ward stability and keep clearing pests
- Busy or clear: improved; HUD now has clearer hierarchy with year chip, hint, ward label, and score
- CTA/control zones safe: yes; no action buttons moved into unsafe areas
- Reachability: preserved drag space, reaction cards remain pointer-events none
- Copy issues: none critical
- Overlap/clutter: reaction stack still occupies lower-right space but remains within viewport and non-interactive
- Gameplay area space: protected; HUD occupies `~97px` height at 400x700
- 400x700 strength: safe

Current layout:
```text
┌────────────────────────────────────┐
│ HUD label + score + ward bar       │
│                                    │
│            gameplay                │
│                                    │
│                progress badge      │
│                            alerts  │
└────────────────────────────────────┘
```

Reduced minimalist layout:
```text
┌────────────────────────────────────┐
│ year chip | hint                   │
│ ward label | score                 │
│ ward bar                           │
│                                    │
│            gameplay                │
│                                    │
│                progress badge      │
│                          alerts    │
└────────────────────────────────────┘
```

## Pause
Observed state:
- Pause UI not present in this build
- Main focal anchor: N/A
- Main UI message: N/A
- Safe controls: no pause-specific controls detected
- Actionability: unaffected

## Win
Observed state:
- Win screen not reachable in bounded pass
- Closest equivalent: progression badge and phase-driven HUD feedback during active play
- Risk: final success messaging not validated in runtime for this stage

## Lose / Fail
Observed state:
- Main focal anchor: game-over menu card
- Main UI message: ward failed, restart the drill
- Busy or clear: expected clear; copy shortened conservatively
- CTA/control zones safe: intended yes; same card and button structure retained
- Reachability: restart CTA preserved
- Copy issues: shortened from longer failure sentence to tighter wording
- Overlap/clutter: reaction stack dim rule also applies on end overlay

Current layout:
```text
┌────────────────────────────────────┐
│ HUD behind fail overlay            │
│        fail card                   │
│        score + restart             │
└────────────────────────────────────┘
```

Reduced minimalist layout:
```text
┌────────────────────────────────────┐
│ HUD behind fail overlay            │
│      compact fail card             │
│      short failure copy            │
│      score + Try Again             │
└────────────────────────────────────┘
```

## Restart / Continue
Observed state:
- Main focal anchor: restart button in fail card
- Main UI message: reset the ward and continue drill flow
- Busy or clear: clear
- CTA/control zones safe: preserved
- Reachability: preserved by keeping original structure and button sizing

## Summary of Safe Repairs
- Inset the HUD on mobile instead of allowing full-bleed width.
- Added a compact year chip and one-line action hint for stronger hierarchy.
- Shortened title and fail overlay copy for faster scanning.
- Dimmed reaction cards during overlays so the menu card reads as the dominant focus.
- Reduced mobile reaction card footprint and tightened panel spacing while preserving mechanics and controls.