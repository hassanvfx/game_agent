# Creative Remix v4 Merged Prompt Workflow

## Task History
- Task 1 (2026-05-09T07:01:09.240448Z): Create a no-touch Remix v4 workflow by source-concatenating existing prompt files into new v4 production harnesses and registering a new `creative_remix_v4` workflow.

## Task 1 — Remix v4 merged prompts and workflow registration

### Status
Implemented.

### User Requirements Captured
- Do not modify existing Remix v3/v1 source prompt files.
- Create new Remix v4 prompt files/configuration only.
- Start by concatenating existing large prompt files into v4 draft files with provenance markers.
- Reduce/unify in chunks without losing context.
- Keep final v4 prompts long, comprehensive, and production-grade rather than compressed summaries.
- Preserve global harness invariants:
  - do not break mechanics
  - avoid risky gameplay logic rewrites
  - prefer procedural/code-native art
  - keep animated, level-reactive motion-graphic backgrounds
  - keep recognizable procedural characters/items/props
  - final mobile repair must aggressively fix console/runtime/mobile UI defects
- v4 target stages:
  1. remix inference plus mechanic decomposition / 5-level planning
  2. merged world design / narrative / gameplay / media mapping
  3. visual base transformation
  4. visual UI refinement
  5. aggressive final mobile repair

### Implementation Notes
- New v4 prompt files were generated from existing source prompts.
- Each new v4 prompt starts with a unified v4 production harness, then retains source prompt material as a provenance-marked instruction library.
- Raw source-concat archival bundles were created in `tools/game_refactoring/prompts/operators_v2/v4_source_bundles/`.
- `tools/game_refactoring/scripts/game_workflow.py` now has a new `creative_remix_v4` workflow entry.
- Existing Remix v3/v1 prompt files remain source-only and were not edited.

### New v4 Prompt Files
- `tools/game_refactoring/prompts/operators_v2/00_creative_remix_v4_remix_inference_plus.md`
- `tools/game_refactoring/prompts/operators_v2/01_creative_remix_v4_world_design_superprompt.md`
- `tools/game_refactoring/prompts/operators_v2/02_creative_remix_v4_visuals_base.md`
- `tools/game_refactoring/prompts/operators_v2/03_creative_remix_v4_visual_ui_refine.md`
- `tools/game_refactoring/prompts/operators_v2/04_creative_remix_v4_final_mobile_repair_aggressive.md`

### New Workflow
`creative_remix_v4` active stages:
1. `remix_inference_plus`
2. `world_design_superprompt`
3. `visuals_base`
4. `visual_ui_refine`
5. `final_mobile_repair_aggressive`

### Validation Plan
- Confirm v4 files exist.
- Confirm workflow resolves `creative_remix_v4`.
- Confirm source v3 prompt files were not modified by reviewing git diff scope.


### Validation Results
- `python3 tmp/validate_creative_remix_v4.py` passed:
  - `creative_remix_v4_validation_ok`
  - `v4_prompt_count 5`
  - `source_prompts_modified 0`
- `python3 tmp/check_creative_remix_v4_readiness.py` passed:
  - `creative_remix_v4_readiness_ok`
  - `workflow_nodes 5`
  - `dry_manifest_game_count 1`
- The readiness check confirmed:
  - workflow resolution for `creative_remix_v4`
  - expected five-node v4 stage order
  - required v4 production markers
  - provenance/source markers
  - raw concat bundle presence
  - dry manifest construction for one game

### Temp Tooling Decision
The temporary scripts remain in `tmp/` for reproducibility and quick follow-up validation:
- `tmp/create_creative_remix_v4.py`
- `tmp/fix_v4_mechanics_invariant.py`
- `tmp/validate_creative_remix_v4.py`
- `tmp/check_creative_remix_v4_readiness.py`

### Recommended Next Step
Run a one-game `creative_remix_v4` smoke test with low concurrency before using the 107-game manifests.

### One-Game v4 Harry Potter Smoke Launch
- Recorded at: `2026-05-09T07:06:33.151170Z`
- Requested smoke prompt: `Harry Potter`
- Workflow: `creative_remix_v4`
- Manifest: `tmp/game_refactoring_experiments/fixtures/top100_vatsal_first_game_manifest.json`
- Source mode: `copy`
- Pipeline: `v2`
- Max concurrency: `1`
- Note: three launch invocations were accidentally triggered by duplicate tool calls; no relaunch was performed after detection.
- `scripts/kill_all_tool_runtimes.py` was run afterward and reported zero matched/surviving tool runtimes.
- Existing run states still showed `parallel_batch_running`; treat the latest run as the primary monitor target.
- Primary monitor run: `run_v4_harry_potter_one_game_20260509T070549Z`

Launched run IDs:
- `run_v4_harry_potter_one_game_20260509T070547Z`
  - run dir: `/Users/hassan/repos/game_agent/tmp/game_refactoring_experiments/runs/run_v4_harry_potter_one_game_20260509T070547Z`
  - dashboard: `/Users/hassan/repos/game_agent/tmp/game_refactoring_experiments/runs/run_v4_harry_potter_one_game_20260509T070547Z/dashboard/index.html`
  - status: `/Users/hassan/repos/game_agent/tmp/game_refactoring_experiments/runs/run_v4_harry_potter_one_game_20260509T070547Z/run_state.json`
- `run_v4_harry_potter_one_game_20260509T070548Z`
  - run dir: `/Users/hassan/repos/game_agent/tmp/game_refactoring_experiments/runs/run_v4_harry_potter_one_game_20260509T070548Z`
  - dashboard: `/Users/hassan/repos/game_agent/tmp/game_refactoring_experiments/runs/run_v4_harry_potter_one_game_20260509T070548Z/dashboard/index.html`
  - status: `/Users/hassan/repos/game_agent/tmp/game_refactoring_experiments/runs/run_v4_harry_potter_one_game_20260509T070548Z/run_state.json`
- `run_v4_harry_potter_one_game_20260509T070549Z`
  - run dir: `/Users/hassan/repos/game_agent/tmp/game_refactoring_experiments/runs/run_v4_harry_potter_one_game_20260509T070549Z`
  - dashboard: `/Users/hassan/repos/game_agent/tmp/game_refactoring_experiments/runs/run_v4_harry_potter_one_game_20260509T070549Z/dashboard/index.html`
  - status: `/Users/hassan/repos/game_agent/tmp/game_refactoring_experiments/runs/run_v4_harry_potter_one_game_20260509T070549Z/run_state.json`

### One-Game Raw-Backed v4 Harry Potter End-to-End Launch
- Recorded at: `2026-05-09T07:07:56.534437Z`
- Workflow: `creative_remix_v4`
- Prompt: `Harry Potter`
- Source mode: `copy`
- Pipeline: `v2`
- Max concurrency: `1`
- Selected raw-backed game: `gamezone-0f3dc736-8159-48cf-93d0-bd78a54b8cd0`
- Source path: `/Users/hassan/repos/game_agent/games/raw/gamezone-0f3dc736-8159-48cf-93d0-bd78a54b8cd0`
- Single-game manifest: `/Users/hassan/repos/game_agent/tmp/game_refactoring_experiments/fixtures/v4_harry_potter_raw_one_game_manifest.json`
- Run id: `run_v4_harry_potter_raw_one_game_20260509T070741Z`
- Run dir: `/Users/hassan/repos/game_agent/tmp/game_refactoring_experiments/runs/run_v4_harry_potter_raw_one_game_20260509T070741Z`
- Dashboard: `/Users/hassan/repos/game_agent/tmp/game_refactoring_experiments/runs/run_v4_harry_potter_raw_one_game_20260509T070741Z/dashboard/index.html`
- Status: `/Users/hassan/repos/game_agent/tmp/game_refactoring_experiments/runs/run_v4_harry_potter_raw_one_game_20260509T070741Z/run_state.json`
- Output root: `/Users/hassan/repos/game_agent/tmp/game_refactoring_experiments/runs/run_v4_harry_potter_raw_one_game_20260509T070741Z/output`
- Launcher stdout: `/Users/hassan/repos/game_agent/tmp/game_refactoring_experiments/runs/run_v4_harry_potter_raw_one_game_20260509T070741Z/batch_launcher_stdout.txt`
- Launcher stderr: `/Users/hassan/repos/game_agent/tmp/game_refactoring_experiments/runs/run_v4_harry_potter_raw_one_game_20260509T070741Z/batch_launcher_stderr.txt`
- Workflow manifest: `tools/game_refactoring/runs/_workflow_manifests/creative_remix_v4__v4_harry_potter_raw_one_game_manifest.json`

This is the clean raw-backed single-game end-to-end v4 smoke run requested after the earlier duplicate launch attempt.

### Corrected HDD Output v4 Harry Potter Raw One-Game Launch
- Recorded at: `2026-05-09T07:10:52.518990Z`
- Correction: expected runs root is `/Volumes/HDD2026/output`.
- Pre-launch cleanup: `python3 scripts/kill_all_tool_runtimes.py` reported zero matched/surviving runtimes.
- Workflow: `creative_remix_v4`
- Prompt: `Harry Potter`
- Source mode: `copy`
- Pipeline: `v2`
- Max concurrency: `1`
- Selected raw-backed game: `gamezone-0f3dc736-8159-48cf-93d0-bd78a54b8cd0`
- Source path: `/Users/hassan/repos/game_agent/games/raw/gamezone-0f3dc736-8159-48cf-93d0-bd78a54b8cd0`
- Single-game manifest: `/Users/hassan/repos/game_agent/tmp/game_refactoring_experiments/fixtures/v4_harry_potter_raw_one_game_manifest.json`
- Run id: `run_v4_harry_potter_raw_one_game_20260509T071032Z`
- Run dir: `/Volumes/HDD2026/output/run_v4_harry_potter_raw_one_game_20260509T071032Z`
- Dashboard: `/Volumes/HDD2026/output/run_v4_harry_potter_raw_one_game_20260509T071032Z/dashboard/index.html`
- Status: `/Volumes/HDD2026/output/run_v4_harry_potter_raw_one_game_20260509T071032Z/run_state.json`
- Output root: `/Volumes/HDD2026/output/run_v4_harry_potter_raw_one_game_20260509T071032Z/output`
- Launcher stdout: `/Volumes/HDD2026/output/run_v4_harry_potter_raw_one_game_20260509T071032Z/batch_launcher_stdout.txt`
- Launcher stderr: `/Volumes/HDD2026/output/run_v4_harry_potter_raw_one_game_20260509T071032Z/batch_launcher_stderr.txt`
- Workflow manifest: `tools/game_refactoring/runs/_workflow_manifests/creative_remix_v4__v4_harry_potter_raw_one_game_manifest.json`

This is the corrected raw-backed single-game Harry Potter v4 run using the expected external HDD output root.

### Model 5.5 HDD Output v4 Harry Potter Raw One-Game Launch
- Recorded at: `2026-05-09T07:12:12.781370Z`
- Workflow: `creative_remix_v4`
- Prompt: `Harry Potter`
- Model: `gpt-5.5`
- Source mode: `copy`
- Pipeline: `v2`
- Max concurrency: `1`
- Runs root: `/Volumes/HDD2026/output`
- Selected raw-backed game: `gamezone-0f3dc736-8159-48cf-93d0-bd78a54b8cd0`
- Source path: `/Users/hassan/repos/game_agent/games/raw/gamezone-0f3dc736-8159-48cf-93d0-bd78a54b8cd0`
- Single-game manifest: `/Users/hassan/repos/game_agent/tmp/game_refactoring_experiments/fixtures/v4_harry_potter_raw_one_game_manifest.json`
- Run id: `run_v4_harry_potter_raw_one_game_model55_20260509T071151Z`
- Run dir: `/Volumes/HDD2026/output/run_v4_harry_potter_raw_one_game_model55_20260509T071151Z`
- Dashboard: `/Volumes/HDD2026/output/run_v4_harry_potter_raw_one_game_model55_20260509T071151Z/dashboard/index.html`
- Status: `/Volumes/HDD2026/output/run_v4_harry_potter_raw_one_game_model55_20260509T071151Z/run_state.json`
- Output root: `/Volumes/HDD2026/output/run_v4_harry_potter_raw_one_game_model55_20260509T071151Z/output`
- Launcher stdout: `/Volumes/HDD2026/output/run_v4_harry_potter_raw_one_game_model55_20260509T071151Z/batch_launcher_stdout.txt`
- Launcher stderr: `/Volumes/HDD2026/output/run_v4_harry_potter_raw_one_game_model55_20260509T071151Z/batch_launcher_stderr.txt`
- Workflow manifest: `tools/game_refactoring/runs/_workflow_manifests/creative_remix_v4__v4_harry_potter_raw_one_game_manifest.json`

This is the model 5.5 comparison run matching the previous v4 Harry Potter raw-backed one-game setup.

### Remix v4 Model Decision
- Recorded at: `2026-05-09T07:27:14.630721Z`
- Decision: use `gpt-5.5` as the preferred/default model for Remix v4 runs.
- Rationale: after launching the model 5.5 comparison run for the same raw-backed Harry Potter single-game setup, future `creative_remix_v4` experiments should be launched with `--model gpt-5.5` unless explicitly testing another model.
- Applies to:
  - one-game v4 smoke tests
  - raw-backed v4 prompt experiments
  - future v4 batch launches
- Existing model 5.4 runs remain useful as comparison artifacts, but v4 going forward should use model 5.5.

### Remix v4 Final Repair Media Error Policy
- Final mobile repair should focus on code-level runtime errors, gameplay blockers, mobile actionability, and screenshot-visible UI/layout defects.
- Do not chase expected/transient catalog or generated-media 404/400 responses, including Giphy/generated assets that may still be processing.
- Treat optional decorative GIF/image/audio fetch failures as `non-blocking external/generated media fetch noise` unless they crash code, hide required controls, block play, or make required gameplay entities invisible.
- Valid media fixes are deterministic corrections where the correct replacement is known: wrong CDN hostname, outdated library route, typo in a required local asset path, or missing required media that breaks code/playability.
- Remix 3 prompts remain untouched; this policy applies to the new Remix v4 final mobile repair prompt.

### Model 5.5 HDD Output v4 Rick and Morty Raw One-Game Launch
- Recorded at: `2026-05-09T07:34:06.028648Z`
- Workflow: `creative_remix_v4`
- Prompt: `Rick and Morty`
- Model: `gpt-5.5`
- Source mode: `copy`
- Pipeline: `v2`
- Max concurrency: `1`
- Runs root: `/Volumes/HDD2026/output`
- Selected raw-backed game: `gamezone-0f3dc736-8159-48cf-93d0-bd78a54b8cd0`
- Source path: `/Users/hassan/repos/game_agent/games/raw/gamezone-0f3dc736-8159-48cf-93d0-bd78a54b8cd0`
- Single-game manifest: `/Users/hassan/repos/game_agent/tmp/game_refactoring_experiments/fixtures/v4_rick_morty_raw_one_game_manifest.json`
- Run id: `run_v4_rick_morty_raw_one_game_model55_20260509T073337Z`
- Run dir: `/Volumes/HDD2026/output/run_v4_rick_morty_raw_one_game_model55_20260509T073337Z`
- Dashboard: `/Volumes/HDD2026/output/run_v4_rick_morty_raw_one_game_model55_20260509T073337Z/dashboard/index.html`
- Status: `/Volumes/HDD2026/output/run_v4_rick_morty_raw_one_game_model55_20260509T073337Z/run_state.json`
- Output root: `/Volumes/HDD2026/output/run_v4_rick_morty_raw_one_game_model55_20260509T073337Z/output`
- Launcher stdout: `/Volumes/HDD2026/output/run_v4_rick_morty_raw_one_game_model55_20260509T073337Z/batch_launcher_stdout.txt`
- Launcher stderr: `/Volumes/HDD2026/output/run_v4_rick_morty_raw_one_game_model55_20260509T073337Z/batch_launcher_stderr.txt`
- Workflow manifest: `tools/game_refactoring/runs/_workflow_manifests/creative_remix_v4__v4_rick_morty_raw_one_game_manifest.json`

This is the model 5.5 Remix v4 Rick and Morty retry run using the updated final repair media-error policy.

### Remix v4 Unified Visual Pass
- Recorded at: `2026-05-09T07:37:08.892805Z`
- Decision: merge `visuals_base` and `visual_ui_refine` into one Remix v4 visual pass.
- New node id: `visuals_unified`
- New prompt file: `tools/game_refactoring/prompts/operators_v2/03_creative_remix_v4_visuals_unified.md`
- Source prompts appended into unified prompt:
  - `02_creative_remix_v4_visuals_base.md`
  - `03_creative_remix_v4_visual_ui_refine.md`
- Updated `creative_remix_v4` stage list:
  1. `remix_inference_plus`
  2. `world_design_superprompt`
  3. `visuals_unified`
  4. `final_mobile_repair_aggressive`
- Remix 3 prompts remain untouched.
- The unified visual pass preserves both responsibilities:
  - procedural animated visual transformation
  - HUD/UI/mobile visual refinement with runtime/screenshot discipline

### Remix v4 Animated Background Replacement Mandate
- Restored and strengthened the original animated-background invariant for Remix v4.
- If an input game has a boring/generic/static/stock-like background image dominating the playfield, v4 should not preserve it as the world identity.
- `world_design_superprompt` must plan a prompt-specific procedural animated replacement, including motion-graphic layers, semantic motifs, and level/progress reactivity.
- `visuals_unified` must execute the replacement/demotion so the procedural authored world becomes the true scene foundation.
- Decorative overlays, tinting, particles, wrapper styling, or themed copy around an unchanged stock/static image are explicitly insufficient.
- Mechanics, controls, HUD readability, hitboxes, and mobile actionability remain protected.

### Remix v4 Shared Context Header
- Added one shared Remix v4 context header block to all active Remix v4 prompts.
- The shared header includes:
  - four-stage workflow summary
  - stage tag summary
  - global policy tag summary
- Purpose: every Remix v4 node sees the whole workflow shape, its role, and the shared invariants immediately at prompt start.
- Remix 3 prompts remain untouched.
