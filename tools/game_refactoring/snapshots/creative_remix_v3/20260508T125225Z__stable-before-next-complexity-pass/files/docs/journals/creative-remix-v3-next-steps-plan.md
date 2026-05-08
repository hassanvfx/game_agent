# Creative Remix V3 Next Steps Plan

## Goal

Finish the realistic `creative_remix_v3` second-pass architecture so it becomes:

1. `remix_inference`
2. `narrative`
3. `gameplay`
4. `visuals`
5. `media_mapper`
6. `narrative_refine`
7. `visuals_refine`
8. `optional_config_refactor`
9. `final_mobile_repair`

## Work Breakdown

### 0. Add `remix_inference`
Add a new opening stage derived from the tag/inference prompt.

This stage should:
- analyze the current game and codebase
- interpret the current game through the active remix prompt
- formulate the intended remixed identity rather than only the source identity
- emit remix-conditioned tags, mechanics ranking, blueprint guidance, and recreation prompt outputs
- produce a concise delta brief describing what later stages should preserve versus transform

Required outputs should include:
- `Blueprint.md`
- `Identity.json`
- mechanics ranking artifact
- companion classification artifact
- semantic tags artifact
- `RecreationPrompt.md`
- `RemixDelta.md`

### 1. Finalize `narrative_refine`
Already mostly updated.
Its role is:
- reduce text
- use direct imperative language
- keep UI language plain, didactic, and scannable
- support compact icon-forward communication when helpful
- avoid decorative or wordy phrasing

### 2. Rewrite `visuals_refine`
Update it so its role is:
- simplify instead of adding more density
- strengthen the focal actor / main character / visual anchor
- unify the design system
- create state-machine-oriented ASCII render summaries
- detect visual overlap / clutter
- preserve what is already strong
- reduce generic leftovers
- improve mobile-safe layout clarity

### 3. Replace `media_mapper_refine`
Remove the idea of a second generic media refinement pass at the end of v3.

Replace it with:
- `optional_config_refactor`
- `final_mobile_repair`

### 4. Add `optional_config_refactor`
This new stage should:
- scaffold a normalized `optional_config`
- support URL param injection
- support runtime override via a `game-configs` browser event
- merge defaults, URL params, and runtime event data safely
- apply theme and asset overrides only where they map safely
- preserve procedural/native fallback rendering when no asset is provided
- preserve current gameplay bounding boxes
- normalize the current game as `level 0`
- spread escalation conservatively but distinctly across levels `1-9`
- document level complexity using ASCII diagrams
- document replaceable asset regions and bounding boxes using ASCII diagrams
- keep the game repairable by the final mobile repair stage

Required artifacts:
- `optional_config_usage.md`
- `level_complexity_plan.md`
- `asset_slot_bounding_boxes.md`
- `operator_result_contract.json`

### 5. Add `final_mobile_repair`
This final stage should:
- treat the current refactored `index.html` as the main work surface
- fix overlap, breakage, mobile actionability, layout safety, modal safety, and control visibility
- stabilize the transformed final output
- not introduce more thematic complexity

### 6. Update `scripts/game_workflow.py`
Wire `creative_remix_v3` to:
- prepend:
  - `remix_inference`
- keep round 1:
  - `narrative`
  - `gameplay`
  - `visuals`
  - `media_mapper`
- keep round 2:
  - `narrative_refine`
  - `visuals_refine`
- replace the final node:
  - remove `media_mapper_refine`
  - remove `gameplay_refine`
  - add `optional_config_refactor`
  - add `final_mobile_repair`

## Expected Outcome

After these changes:
- v3 becomes less about “more stuff”
- more about:
  - cleaner language
  - fairer difficulty
  - simpler stronger visual identity
  - safer final public build
  - final mobile stability

## Execution Order

1. create `remix_inference` prompt
2. finalize `visuals_refine`
3. create `optional_config_refactor` prompt
4. create `final_mobile_repair` prompt
5. update `scripts/game_workflow.py`
6. remove `gameplay_refine` from the v3 pipeline
7. update `visuals_refine` for discreet fade-in level display
8. optionally rerun canonical Harry Potter v3 experiment
