# Remix v4 Clone Workflow

## Task History
- Task 1 (2026-05-16 14:43 America/Mexico_City): Plan a full clone of the existing `creative_remix_v4` workflow into a new `remix-v4-clone` flow that first renames `index.html` and linked CSS/JS assets with an `_old` prefix, then uses blueprint and mechanic analysis to build a substantially new game while using `_old` files as reference-only fallback material.

## Task 1 — Planning `remix-v4-clone`

### Status
Implemented and validated.

### User Requirements Captured
- Copy the existing Remix v4 workflow rather than modifying it in place.
- Name the new flow `remix-v4-clone`.
- Add an early step that renames `index.html` and linked CSS/JS files with an `_old` prefix.
- Treat the `_old` prefixed files as reference-only surfaces.
- Use the blueprint and mechanic analysis to build an entirely new game rather than only reskinning the original.
- Minimize dependence on the `_old` files except when behavior is confusing or there is risk of breaking core expectations.

### Relevant Existing Files
- `tools/game_refactoring/scripts/game_workflow.py`
- `tools/game_refactoring/docs/game_workflow_cli.md`
- `tools/game_refactoring/prompts/operators_v2/00_creative_remix_v4_remix_inference_plus.md`
- `tools/game_refactoring/prompts/operators_v2/01_creative_remix_v4_world_design_superprompt.md`
- `tools/game_refactoring/prompts/operators_v2/03_creative_remix_v4_visuals_unified.md`
- `tools/game_refactoring/prompts/operators_v2/04_creative_remix_v4_final_mobile_repair_aggressive.md`

### Technical Planning Notes
- The current v4 workflow is registered in `scripts/game_workflow.py` as `creative_remix_v4`.
- The current v4 pipeline is four stages: `remix_inference_plus`, `world_design_superprompt`, `visuals_unified`, and `final_mobile_repair_aggressive`.
- The best implementation path appears to be a new additive workflow definition plus new prompt files, not mutation of existing v4 prompts.
- The new clone workflow likely needs an extra first-stage prompt dedicated to source preservation and rename orchestration.
- Later prompts should shift from “preserve mechanics, transform visuals” toward “rebuild a new game informed by blueprint + mechanic analysis, with old files available only as reference”.

### Proposed Implementation Outline
- Add a new workflow entry in `tools/game_refactoring/scripts/game_workflow.py`.
- Create a new stage-0 prompt that renames the original entrypoint and directly linked CSS/JS assets to `_old*` names and records the mapping.
- Create clone-specific downstream prompt files derived from v4 but rewritten around a rebuild-first contract.
- Update workflow CLI documentation so the new flow is discoverable and its semantics are explicit.

### Success Criteria
- A new workflow id exists and can be launched without affecting `creative_remix_v4`.
- The first stage preserves original runtime files under `_old` names.
- Downstream stages are instructed to build a new playable game as the main surface.
- `_old` assets are clearly designated as reference-only, not the default implementation surface.
- Documentation explains when to use `remix-v4-clone` versus `creative_remix_v4`.

### Next Steps
- [ ] Implement the new workflow entry and prompt set.
- [ ] Add clone-specific file-rename/reference-only instructions.
- [ ] Update workflow CLI docs.
- [ ] Run a dry validation of workflow registration.

### 2026-05-16 14:45 - Implemented initial `remix-v4-clone` workflow scaffolding

**Achievement:**
- Added a new additive workflow id, `remix-v4-clone`, to the workflow registry.
- Added a dedicated stage-0 preservation prompt for `_old` renaming behavior.
- Added clone-specific wrapper prompts for the planning, world design, visual rebuild, and final repair stages.
- Updated CLI docs so the new workflow is discoverable and its rebuild-first semantics are explicit.

**Implementation Details:**
- Updated `tools/game_refactoring/scripts/game_workflow.py` with a new five-stage workflow:
  1. `clone_surface_preserve`
  2. `clone_remix_inference_plus`
  3. `clone_world_design_superprompt`
  4. `clone_visuals_unified`
  5. `clone_final_mobile_repair_aggressive`
- Updated `tools/game_refactoring/docs/game_workflow_cli.md` with a new workflow section and example invocation.
- Added new prompt files:
  - `tools/game_refactoring/prompts/operators_v2/00_remix_v4_clone_surface_preserve.md`
  - `tools/game_refactoring/prompts/operators_v2/01_remix_v4_clone_remix_inference_plus.md`
  - `tools/game_refactoring/prompts/operators_v2/02_remix_v4_clone_world_design_superprompt.md`
  - `tools/game_refactoring/prompts/operators_v2/03_remix_v4_clone_visuals_unified.md`
  - `tools/game_refactoring/prompts/operators_v2/04_remix_v4_clone_final_mobile_repair_aggressive.md`

**Technical Decisions:**
- Kept `creative_remix_v4` unchanged to avoid regression risk.
- Used clone-specific wrapper prompts instead of mutating the large v4 prompt bodies.
- Made the first stage responsible for `_old` preservation so later stages can consistently assume a rebuild-first workspace.

**Next Steps:**
- [ ] Run a lightweight validation that `remix-v4-clone` resolves from the registry.
- [ ] Confirm the generated manifest shape is valid for the new workflow.

### 2026-05-16 14:49 - Corrected workflow ordering after user review

**Problem Encountered:**
- The first implementation put the `_old` preservation step before inference.
- That did not match the intended sequence.

**Correction:**
- The workflow must begin with the normal `remix_inference_plus` stage.
- The new clone-specific step comes immediately after inference and is responsible for:
  - renaming old public/runtime files to `_old` forms
  - creating the new public game surface
  - rebuilding from the upstream blueprint while using old files only as reference-only fallback material

**Implementation Details:**
- Reworked `tools/game_refactoring/scripts/game_workflow.py` so `remix-v4-clone` now starts with the existing v4 inference prompt.
- Removed the mistaken first-step prompt ordering.
- Replaced the earlier preservation-first prompt pair with a single new prompt:
  - `tools/game_refactoring/prompts/operators_v2/01_remix_v4_clone_rebuild_from_blueprint_and_old_refs.md`
- Updated `tools/game_refactoring/docs/game_workflow_cli.md` to describe the corrected step order.

**Corrected Node Order:**
1. `remix_inference_plus`
2. `clone_rebuild_from_blueprint_and_old_refs`
3. `clone_world_design_superprompt`
4. `clone_visuals_unified`
5. `clone_final_mobile_repair_aggressive`

**Technical Decision:**
- Reused the existing `00_creative_remix_v4_remix_inference_plus.md` directly for the first stage so the workflow begins with the same strong v4 planning contract the user requested.

**Next Steps:**
- [ ] Validate the corrected workflow registration.
- [ ] Validate dry manifest generation for the corrected node order.

### 2026-05-16 14:51 - Validated corrected workflow and documented fixture-path issue

**Achievement:**
- Confirmed the corrected `remix-v4-clone` workflow registers and launches through the dry-run path when using a known-good raw-backed manifest.
- Isolated the earlier validation failure to a bad fixture source path rather than a workflow-definition bug.

**Validation Results:**
- The first dry-run attempt using `tmp/game_refactoring_experiments/fixtures/top100_vatsal_first_game_manifest.json` failed before execution because the manifest referenced a missing source directory:
  - `/Users/hassan/repos/game_agent/games/top100_vatsal/gamezone-0a438816-ecee-420b-afd6-4a36ddc935e3`
- Re-running validation with `tmp/game_refactoring_experiments/fixtures/top107_vatsal_raw_backed_harry_potter_manifest.json` succeeded.
- Successful dry-run result:
  - `workflow_id`: `remix-v4-clone`
  - `workflow_manifest_path`: `tools/game_refactoring/runs/_workflow_manifests/remix-v4-clone__top107_vatsal_raw_backed_harry_potter_manifest.json`
  - `workflow_games_count`: `107`

**Technical Conclusion:**
- The corrected workflow registry, node order, and prompt wiring are valid.
- The earlier error was environmental/fixture-related, not a schema or ordering failure in `remix-v4-clone`.

**Recommended Follow-up:**
- If the top100 fixture is still needed, repair or regenerate its `source_path` entries before using it for future validation runs.

### 2026-05-16 16:28 - Standardized clone prompt namespace and stage IDs

**Achievement:**
- Standardized the clone workflow so all five stages now use clone-specific stage IDs or clone-specific workflow naming.
- Added a clone-namespaced inference prompt file so the workflow no longer mixes original v4 and clone prompt filenames.

**Implementation Details:**
- Updated `tools/game_refactoring/scripts/game_workflow.py` so the first clone stage id is now `clone_remix_inference_plus`.
- Added `tools/game_refactoring/prompts/operators_v2/00_remix_v4_clone_remix_inference_plus.md`.
- Kept the downstream clone files aligned as:
  - `00_remix_v4_clone_remix_inference_plus.md`
  - `01_remix_v4_clone_rebuild_from_blueprint_and_old_refs.md`
  - `02_remix_v4_clone_world_design_superprompt.md`
  - `03_remix_v4_clone_visuals_unified.md`
  - `04_remix_v4_clone_final_mobile_repair_aggressive.md`
- Updated workflow docs so the listed stage names match the clone namespace used in run manifests.

**Technical Decision:**
- The clone inference prompt is a namespaced clone wrapper that preserves the same planning behavior while making the workflow naming uniform in manifests and run-stage reporting.

### 2026-05-16 16:30 - Revalidated uniform clone namespace in manifest output

**Achievement:**
- Revalidated the workflow after the clone namespace cleanup.
- Confirmed the generated workflow manifest now uses clone-specific stage ids and clone-specific prompt filenames consistently.

**Validation Results:**
- Dry-run command succeeded with the known-good raw-backed manifest:
  - `python3 tools/game_refactoring/scripts/game_workflow.py --json --id remix-v4-clone --games-manifest-source tmp/game_refactoring_experiments/fixtures/top107_vatsal_raw_backed_harry_potter_manifest.json --dry-run-operators --dry-run-spec-adaptor`
- Generated workflow manifest confirmed these node ids:
  1. `clone_remix_inference_plus`
  2. `clone_rebuild_from_blueprint_and_old_refs`
  3. `clone_world_design_superprompt`
  4. `clone_visuals_unified`
  5. `clone_final_mobile_repair_aggressive`
- Generated workflow manifest confirmed these prompt files:
  - `00_remix_v4_clone_remix_inference_plus.md`
  - `01_remix_v4_clone_rebuild_from_blueprint_and_old_refs.md`
  - `02_remix_v4_clone_world_design_superprompt.md`
  - `03_remix_v4_clone_visuals_unified.md`
  - `04_remix_v4_clone_final_mobile_repair_aggressive.md`

**Conclusion:**
- The clone workflow now has both:
  - uniform clone prompt-file naming
  - uniform clone stage ids in run manifests

### 2026-05-16 16:48 - Created random 5-game raw manifest for live clone testing

**Achievement:**
- Added a small tmp helper script to generate a random five-game raw manifest for `remix-v4-clone` testing.
- Generated a concrete manifest from valid `games/raw` folders.

**Implementation Details:**
- Created helper script:
  - `tmp/build_remix_v4_clone_random5_manifest.py`
- Generated manifest:
  - `tmp/game_refactoring_experiments/fixtures/remix_v4_clone_random5_raw_manifest.json`

**Selected Games:**
- `gamezone-c14a5837-e68c-47b6-bcd9-590ee01a46f4`
- `gamezone-41fcaef2-88f8-4f7f-8899-add99dabb0fd`
- `gamezone-efd80ca1-bcf6-4311-9d15-64d5464ca2d8`
- `gamezone-a4ab4099-cbe6-4bd6-97e4-bc1c2f54dab7`
- `gamezone-f01c6359-f748-4669-ba8d-712417369194`

**Technical Notes:**
- The helper script only considers raw game folders that contain `index.html`.
- It reported `candidate_count: 1001` valid raw candidates at generation time.

**Next Steps:**
- [ ] Launch or dry-run `remix-v4-clone` with `tmp/game_refactoring_experiments/fixtures/remix_v4_clone_random5_raw_manifest.json`.

### 2026-05-16 16:49 - Launched live 5-game `remix-v4-clone` run

**Achievement:**
- Launched a live `remix-v4-clone` run using the newly created random 5-game raw manifest.

**Launch Details:**
- Manifest:
  - `tmp/game_refactoring_experiments/fixtures/remix_v4_clone_random5_raw_manifest.json`
- Run id:
  - `run_game_remixer_20260516T224958Z`
- Run dir:
  - `tools/game_refactoring/runs/run_game_remixer_20260516T224958Z`
- Dashboard:
  - `tools/game_refactoring/runs/run_game_remixer_20260516T224958Z/dashboard/index.html`
- Status path:
  - `tools/game_refactoring/runs/run_game_remixer_20260516T224958Z/run_state.json`
- Output root:
  - `tools/game_refactoring/runs/run_game_remixer_20260516T224958Z/output`
- Workflow manifest:
  - `tools/game_refactoring/runs/_workflow_manifests/remix-v4-clone__remix_v4_clone_random5_raw_manifest.json`
- Workflow game count:
  - `5`

**Technical Notes:**
- Launch used `--max-concurrency 1` for a safer first live test.
- Launch response reported status `created`, which is the expected initial run scaffold state immediately after handoff to the batch launcher.

### 2026-05-16 19:02 - Mobile-first 2-game relaunch is working great

**Achievement:**
- The `remix-v4-clone` flow is now in a strong working state for focused testing.
- We successfully reduced the test scope to two games, tightened the custom rebuild-stage rails, and relaunched with the corrected prompt setup.

**Why This Outcome Is Strong:**
- clone prompt files were corrected into literal full-copy files where intended
- the custom rebuild step now drives a more stable and auditable rebuild process
- rebuild guidance is now mobile-first, portrait-oriented, and aligned with final mobile-repair QA expectations
- the reduced two-game manifest makes iteration faster and safer while preserving meaningful runtime coverage

**Current Best-Known Working Run:**
- Run id:
  - `run_game_remixer_20260517T005525Z`
- Manifest:
  - `tmp/game_refactoring_experiments/fixtures/remix_v4_clone_random2_raw_manifest.json`

**Working-State Summary:**
- The updated clone flow is working well enough to continue iterative prompt tuning from a smaller two-game lane.
- This is now a good checkpoint for committing the clone-flow foundation and the stronger rebuild/mobile rails.

### 2026-05-16 19:03 - Commit checkpoint requested after strong working outcome

**Achievement:**
- Reached a strong checkpoint where the updated `remix-v4-clone` workflow is working well in a focused two-game lane.
- The user explicitly requested a commit with the framing that this is working great.

**Checkpoint Summary:**
- clone workflow scaffold and registration are in place
- clone prompt set is corrected so only the inserted rebuild stage is custom
- rebuild stage now has stronger inline/stability/mobile-first/testing rails
- reduced two-game retry manifest is available for faster iteration
- fresh relaunch run `run_game_remixer_20260517T005525Z` is the best-known live checkpoint using the stronger prompt setup
