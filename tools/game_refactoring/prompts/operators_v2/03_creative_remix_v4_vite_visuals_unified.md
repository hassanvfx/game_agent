Work only inside the provided workspace.

# Creative Remix v4 Vite Variant — Stage 3 — Visuals Unified (Bundle-Aware)

This stage reuses the normal v4 visual transformation role, but compiled Vite-style targets must prioritize high-leverage visible patch surfaces first.

## Read order

Read first if present:

1. `bundle_patch_targets.json`
2. `runtime_surface_map.md`
3. `visual_component_map.json`
4. `component_art_direction.json`
5. `remix_theme.json`
6. `remix_plan_v4.json`
7. then the actual compiled files

## Variant-specific guidance

- Focus first on surfaces that guarantee strong visible delta:
  - title / branding
  - HUD copy
  - pause / help / game-over copy
  - player / obstacle / collectible visuals
  - road / background palette and motion
- Use localized, compiled-bundle-safe edits.
- Avoid broad speculative searching once known patch surfaces exist.
- Ensure the output looks obviously remixed even if the target is minified and structurally awkward.

## Aggressive-but-safe art replacement policy

For compiled Vite targets, Stage 3 is explicitly allowed to create new procedural art helpers and redraw major visual components as long as mechanics remain unchanged.

Allowed examples:
- new procedural Phaser graphics helper functions
- replacement vehicle silhouettes
- new collectible silhouettes
- new background layer systems
- modal/HUD restyling with new typography, spacing, iconography, and themed copy
- new lane marker / roadside decorative motif systems

### High aggression allowed
- player texture redraw
- obstacle texture redraw
- collectible redraw
- lane marker redesign
- road-side/world prop systems
- animated background layers
- HUD redesign
- help / pause / game-over overlay redesign

### Low aggression only
- input dispatch
- event names
- hitbox dimensions
- score math
- spawn timing
- pause/restart semantics

## Minimum visible-delta expectation

Aim to change as many of these as safely possible:
- title text
- help screen text
- pause text
- game-over text
- HUD wording
- player identity surface
- obstacle identity surface
- collectible identity surface
- background palette / motif

At minimum, the stage should materially transform:
- player art
- obstacle art
- collectible art
- background art
- HUD visual identity
- at least one modal/overlay family

## Generic result is not acceptable

Do not stop at wrapper polish, tiny hue shifts, or text-only renaming if major components still read as the original generic racer. If safe visible component redraws remain available, continue pushing the art system.

## Required contract payload

Use:

```json
{
  "status": "ok",
  "detail": "Applied a bundle-aware unified visual remix pass focused on high-leverage player-facing surfaces for the compiled Vite target."
}
```

## Additional instruction

After following the variant-specific rules above, follow the same core expectations as `03_creative_remix_v4_visuals_unified.md`.