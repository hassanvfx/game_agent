Work only inside the provided workspace.

# Creative Remix v4 Vite Variant — Stage 4 — Final Mobile Repair Aggressive (Bundle-Aware)

This stage reuses the normal v4 final repair role, but compiled Vite-style targets must validate both runtime correctness and that the visible remix delta actually landed.

## Read order

Read first if present:

1. `bundle_patch_targets.json`
2. `runtime_surface_map.md`
3. `remix_theme.json`
4. Stage 3 artifacts and screenshots

## Variant-specific guidance

- Validate the assigned runtime as usual.
- Fix real runtime/mobile bugs as usual.
- Also confirm the game is no longer visually too close to the original generic shipped surface.
- If gameplay works but visible remix delta is still weak, apply safe final player-facing copy/palette/UI repairs before finishing.
- Prefer small, deterministic compiled-bundle edits over broad risky rewrites.

## Final originality gate

Before finishing, explicitly check whether any of these still look too generic:
- player art
- obstacle art
- collectible art
- background layer stack
- HUD shell
- pause/help/game-over overlays

If they still read as near-original and safe compiled-surface fixes remain available, make one more visual push before completion.

## Variant acceptance bar

Do not finish while the app still looks essentially like an unchanged generic bundle if safe player-facing compiled-surface fixes remain available.

Runtime correctness alone is not sufficient for success in this Vite variant.

## Required contract payload

Use:

```json
{
  "status": "ok",
  "detail": "Completed final mobile/runtime repair for the compiled Vite remix target and verified both actionability and visible remix-specific surface changes."
}
```

## Additional instruction

After following the variant-specific rules above, follow the same core expectations as `04_creative_remix_v4_final_mobile_repair_aggressive.md`.