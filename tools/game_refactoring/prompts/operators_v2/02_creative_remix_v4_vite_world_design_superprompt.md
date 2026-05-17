Work only inside the provided workspace.

# Creative Remix v4 Vite Variant — Stage 2 — World Design Superprompt (Bundle-Aware)

This stage reuses the normal v4 world-design role, but for compiled Vite-style targets you must author a world plan that maps directly onto known bundle patch surfaces.

## Read order

Read first if present:

1. `vite_surface_manifest.json`
2. `bundle_patch_targets.json`
3. `runtime_surface_map.md`
4. `visual_component_map.json`
5. upstream Stage 1 artifacts such as `remix_plan_v4.json`

## Variant-specific guidance

- Keep world-design artifacts compact and directly useful for compiled-surface patching.
- Prefer decisions that later stages can apply to:
  - HUD labels
  - help/pause/game-over overlays
  - generated textures
  - palette remapping
  - background motion systems
  - mobile control copy
- Avoid drifting into large low-leverage planning outputs that do not help patch the shipped bundle.
- World design must map the remix onto visible components, not just onto generic theme prose.
- If a component is marked `critical` or `major` in `visual_component_map.json`, define how it should be visually replaced or redrawn.

## Mandatory component-level output

Create or update a compact `component_art_direction.json` if feasible.

For each major component, specify:
- `theme_role`
- `new_visual_identity`
- `motif_vocabulary`
- `palette_direction`
- `copy_tone`
- `animation_direction`
- `replacement_priority`

Focus especially on:
- player avatar
- enemy obstacles
- collectibles
- background layers
- HUD panel
- help/pause/game-over modal family

## Not enough for this stage

These alone are insufficient:
- vague franchise vibe statements
- generic color suggestions
- broad world prose with no component mapping
- plans that do not tell Stage 3 how to redraw the major visible surfaces

## Required contract payload

Use:

```json
{
  "status": "ok",
  "detail": "Created a compiled-target-aware authored world and design-system plan aligned to the known Vite bundle patch surfaces."
}
```

## Additional instruction

After following the variant-specific rules above, follow the same core expectations as `01_creative_remix_v4_world_design_superprompt.md`.