# Creative Remix V3 Next Steps Plan

## Goal

Finish the realistic `creative_remix_v3` second-pass architecture so it becomes:

1. `remix_inference`
2. `narrative`
3. `gameplay`
4. `visuals`
5. `media_mapper`
6. `visual_ui_redesign`
7. `optional_config_refactor`
8. `final_mobile_repair`
9. `level_adapter`
10. `multilevel_qa`

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

### 1. Add `visual_ui_redesign`
Replace separate `narrative_refine` and `visuals_refine` behavior with one merged pass.

Its role is:
- reduce text
- use direct imperative language
- keep UI language plain, didactic, and scannable
- support compact icon-forward communication when helpful
- avoid decorative or wordy phrasing
- simplify instead of adding more density
- strengthen the focal actor / main character / visual anchor
- unify the design system
- create state-aware visual/UI summaries
- detect visual overlap / clutter
- preserve what is already strong
- reduce generic leftovers
- improve mobile-safe layout clarity
- preserve start / continue / confirm / restart actionability

### 2. Replace `media_mapper_refine`
Remove the idea of a second generic media refinement pass at the end of v3.

Replace it with:
- `optional_config_refactor`
- `final_mobile_repair`

### 3. Add `optional_config_refactor`
This new stage should:
- scaffold a normalized `optional_config`
- support URL param injection
- support runtime override via a `game-configs` browser event
- merge defaults, URL params, and runtime event data safely
- apply theme and asset overrides only where they map safely
- preserve procedural/native fallback rendering when no asset is provided
- preserve current gameplay bounding boxes
- keep the game repairable by the final mobile repair stage
- avoid owning runtime level selection

Required artifacts:
- `optional_config_usage.md`
- `asset_slot_bounding_boxes.md`
- `operator_result_contract.json`

### 4. Add `final_mobile_repair`
This final stage should:
- treat the current refactored `index.html` as the main work surface
- fix overlap, breakage, mobile actionability, layout safety, modal safety, and control visibility
- stabilize the transformed canonical output
- not introduce more thematic complexity

### 5. Add `level_adapter`
This post-repair stage should:
- inspect the stabilized canonical `index.html`
- deeply determine what actually creates difficulty in the real game
- separate real complexity from fake complexity
- use Nintendo-style progressive disclosure and additive teaching
- first create rationale artifacts before generating variants
- preserve `index.html` as the canonical repaired surface
- create `level_demo.html` as a Mario Bros. 3 style attract/start screen
- make `level_demo.html` a looping safe simulation of competent play
- ensure the background is actual autoplayed game behavior, not a dead decorative backdrop
- continuously demonstrate how a competent player would avoid death mechanics and pursue the objective
- never allow the demo to actually die or actually complete the goal
- keep the demo overlay light:
  - title
  - at most a very short subtitle/tagline
  - `Start Game`
- keep the card discreet and avoid obscuring the focal gameplay subject
- emit `start-game` when the start button is pressed with no valid `?level=` parameter
- allow `?level=0..5` URL routing where:
  - `0` routes to `index.html`
  - `1..5` route to the corresponding derived level file
- derive:
  - `index_level_01.html`
  - `index_level_02.html`
  - `index_level_03.html`
  - `index_level_04.html`
  - `index_level_05.html`
- allow external JS updates only when backward compatibility across canonical and derived levels is preserved
- remove redundant intro/tutorial layers from levels 1–5 when safe because `level_demo.html` serves as the intro/attract surface
- validate flows across demo and derived levels

Required artifacts:
- `mechanics_complexity_decomposition.md`
- `progressive_disclosure_plan.md`
- `level_adapter_rationale.md`
- `level_demo.html`
- `index_level_01.html`
- `index_level_02.html`
- `index_level_03.html`
- `index_level_04.html`
- `index_level_05.html`
- `level_flow_validation.md`
- `operator_result_contract.json`

### 6. Add `multilevel_qa`
This post-level stage should:
- use `index.html` as the canonical structural and behavioral reference
- validate the entire family:
  - `index.html`
  - `level_demo.html`
  - `index_level_01.html`
  - `index_level_02.html`
  - `index_level_03.html`
  - `index_level_04.html`
  - `index_level_05.html`
- open/play each surface mentally
- record notes and screenshot-style state observations
- compare each level to the canonical game and intended difficulty delta
- identify shared bugs vs level-specific bugs
- fix shared issues at shared source when possible
- fix local issues only where needed
- repeat test -> notes -> repair -> retest until passing
- validate:
  - direct file-open compatibility
  - demo autoplay
  - start flows
  - menu open/close
  - pause/resume
  - restart/continue
  - modal confirm/dismiss
  - `?level=0..5` routing
  - mobile actionability across the family
- preserve backward compatibility if shared JS/CSS is updated

Required artifacts:
- `multilevel_qa_report.md`
- `operator_result_contract.json`

### 7. Update `scripts/game_workflow.py`
Wire `creative_remix_v3` to:
- prepend:
  - `remix_inference`
- keep round 1:
  - `narrative`
  - `gameplay`
  - `visuals`
  - `media_mapper`
- keep round 2 as a merged communication/visual cleanup:
  - `visual_ui_redesign`
- replace the final node chain:
  - remove `media_mapper_refine`
  - remove `gameplay_refine`
  - remove separate `narrative_refine`
  - remove separate `visuals_refine`
  - add `optional_config_refactor`
  - add `final_mobile_repair`
  - add `level_adapter`
  - add `multilevel_qa`

## Expected Outcome

After these changes:
- v3 becomes less about “more stuff”
- more about:
  - cleaner language
  - simpler stronger visual identity
  - safer final public build
  - final mobile stability
  - controlled post-repair level derivation
  - final family-wide QA across demo and levels

## Execution Order

1. create `remix_inference` prompt
2. create `visual_ui_redesign` prompt
3. create `optional_config_refactor` prompt
4. create `final_mobile_repair` prompt
5. create `level_adapter` prompt
6. create `multilevel_qa` prompt
7. update `scripts/game_workflow.py`
8. remove `gameplay_refine` from the v3 pipeline
9. merge separate `narrative_refine` and `visuals_refine` into `visual_ui_redesign`
10. optionally rerun canonical Harry Potter v3 experiment