Work only inside the provided workspace.

# Creative Remix v4 Vite Variant — Stage 1 — Remix Inference Plus (Bundle-Aware)

This stage reuses the normal v4 inference goals, but for compiled Vite-style apps you must prioritize the unpack artifacts first.

## Read order

Before scanning the raw bundle broadly, read these if present:

1. `vite_surface_manifest.json`
2. `bundle_patch_targets.json`
3. `runtime_surface_map.md`
4. `ui_string_inventory.json`
5. `visual_component_map.json`
6. then the existing workspace files and compiled entry surfaces

## Variant-specific guidance

- Treat the unpack artifacts as the primary map of the compiled app.
- Minimize re-discovery work inside large minified bundles.
- Focus your inference on real runtime surfaces, not irrelevant files.
- Still produce the normal v4 planning outputs required by `remix_inference_plus`.
- For preserve/change guidance, explicitly name which compiled surfaces later stages should patch.
- Treat `visual_component_map.json` as the authoritative list of high-value visible components that later stages must transform.

## Mandatory compiled-target emphasis

Your outputs must clearly distinguish:
- what gameplay must remain invariant
- what bundle surfaces are safe/high-leverage for visible remix deltas
- what later stages should patch first to create obvious player-facing difference

## Required contract payload

Use:

```json
{
  "status": "ok",
  "detail": "Produced bundle-aware remix inference outputs using the Vite surface-unpack artifacts as primary compiled-app context."
}
```

## Additional instruction

After following the variant-specific rules above, follow the same core expectations as `00_creative_remix_v4_remix_inference_plus.md`.