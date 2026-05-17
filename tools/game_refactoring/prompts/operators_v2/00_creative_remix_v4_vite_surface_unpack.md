Work only inside the provided workspace.

# Creative Remix v4 Vite Variant — Stage 0 — Vite Surface Unpack

You are the deterministic prep stage for compiled Vite-style game targets.

Your goal is **not** to rebuild original source files and **not** to redesign gameplay.
Your job is to inspect the shipped app surface and create a compact, reusable map of the patchable runtime areas so later stages do not waste tokens rediscovering minified structure.

## Primary mission

1. Detect whether the workspace is a Vite-style shipped app or similar compiled bundle target.
2. Identify the real runtime entrypoints:
   - `index.html`
   - JS bundle entrypoints
   - CSS bundle entrypoints
3. Determine likely runtime stack where feasible:
   - React / Preact / Vue / plain DOM
   - Phaser / Pixi / canvas / WebGL / DOM-only
4. Produce readable artifacts describing:
   - where gameplay surfaces live
   - where UI strings and overlays live
   - where palette / texture / art logic lives
   - where mobile controls / action mapping live
   - where likely low-risk patch targets are
   - which visible components are allowed to be aggressively redrawn or replaced procedurally
5. Keep this stage analysis-first and mechanics-preserving.

## Do not do these things

- do not attempt full decompilation into fake `src/` files
- do not perform broad creative rewrites here
- do not change gameplay logic here unless a tiny deterministic read-enabling fix is absolutely required
- do not produce giant speculative narrative artifacts
- do not spend tokens on unrelated files when compiled entry surfaces are already known

## Required artifacts

Create these workspace artifacts when feasible:

### 1. `vite_surface_manifest.json`
Include fields like:
- `app_shell_detected`
- `vite_like_detected`
- `index_html_present`
- `entry_js_paths`
- `entry_css_paths`
- `framework_signals`
- `engine_signals`
- `source_map_signals`
- `compiled_bundle_risk`
- `notes`

### 2. `bundle_patch_targets.json`
Create a compact structured map of likely edit surfaces such as:
- `title_branding`
- `hud_score_surface`
- `pause_surface`
- `help_surface`
- `game_over_surface`
- `player_visual_surface`
- `enemy_visual_surface`
- `collectible_visual_surface`
- `background_surface`
- `mobile_controls_surface`
- `input_mapping_surface`
- `palette_surface`

Each target should include:
- `source_file`
- `anchor_terms`
- `risk`
- `purpose`
- `recommended_later_stage`

### 3. `runtime_surface_map.md`
Write a human-readable short guide explaining:
- what files matter most
- what later stages should read first
- what bundle regions appear to contain gameplay, UI, art, and controls
- what not to touch casually

### 4. `ui_string_inventory.json`
Capture visible / patchable user-facing strings you can confidently identify, such as:
- title text
- HUD labels
- pause text
- help text
- game-over text
- button labels

### 5. `visual_component_map.json`
Create a component-level art attack plan for later stages.

At minimum include major visible components such as:
- `player_avatar`
- `enemy_obstacles`
- `collectibles`
- `lane_markers`
- `road_bed`
- `background_layers`
- `hud_panel`
- `pause_modal`
- `help_modal`
- `game_over_modal`
- `mobile_controls`

For each component include:
- `source_file`
- `implementation_type` (procedural canvas / React overlay / CSS shell / text-only / mixed)
- `visible_importance` (critical / major / minor)
- `art_aggressiveness_allowance` (low / medium / high)
- `replacement_strategy`
- `must_preserve`

This file should make it obvious where Stage 3 is allowed to be bold.

### 6. `operator_result_contract.json`
Return a compact completion contract.

## Completion standard

This stage is complete when later stages could jump directly to the most relevant compiled surfaces instead of scanning the entire bundle from scratch, and when they have an explicit component-level map of where aggressive art replacement is safe.

## Required contract payload

Use:

```json
{
  "status": "ok",
  "detail": "Mapped the compiled Vite/runtime surfaces into reusable bundle artifacts for later remix stages."
}
```