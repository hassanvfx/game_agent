# Game Pipeline Orchestrator Implementation Journal

**Last Updated:** 2026-05-18 09:48 America/Mexico_City  
**Feature Spec:** N/A  
**Backend Reference:** N/A

---

## 📊 Implementation Status Overview

### ✅ Phase 1: Discovery and Architecture - **COMPLETE**

- [x] Inspect sibling projects and identify integration points
- [x] Confirm remixer lookup CLI contract via `get_game`
- [x] Define strict fail-hard orchestration behavior

**Status:** ✅ Complete

### Phase 2: File-Backed Orchestrator and Run Model - **IN PROGRESS**

- [ ] Create run directory and persisted run-state model
- [ ] Implement matcher/remixer/remix-editor/obfuscator orchestration
- [ ] Persist raw artifacts, commands, poll history, and final outputs
- [ ] Align remix editor and obfuscator integrations to updated upstream CLI contracts
- [ ] Add multi-attempt async stage watchdogs with escalating retry windows

**Status:** 🔧 In Progress

### ✅ Phase 3: Observer CLI and HTML Dashboard - **COMPLETE**

- [x] Implement observer CLI terminal rendering and JSON mode
- [x] Implement auto-updating HTML dashboard backed by run files
- [x] Add lightweight local dashboard server and validate flow

**Status:** ✅ Complete

---

## 📝 Journal Entries

### 2026-05-18 09:48 - Reconciled completed vs failed searches into `manifest_may_18_searches_1`

**Achievement:**
- Added a dedicated reconciliation artifact that combines the two completed search batches into one success/failure report
- Captured where successful outputs were copied, and where failed items should be investigated, without needing to manually inspect each batch item file

**Implementation Details:**
- Added `tmp/reconcile_manifest_batches.py`
  - reconciles these completed batches:
    - `batch_pipeline_20260517T205036Z` → `tmp/curated_limit2_prompt_only_manifest.json`
    - `batch_pipeline_20260517T205038Z` → `tmp/vatsal_top_mechanics.json`
  - emits:
    - `tmp/manifest_may_18_searches_1.json`
- The artifact contains:
  - top-level summary counts
  - batch-level summaries
  - `successful_items`
  - `failed_items`
  - failure rollups by manifest and by failed step

**Technical Decisions:**
- Treated `result_summary.final_output_dir` and `result_summary.final_output_dirs` as the source of truth for successful reconciled outputs
- Treated `last_error`, `result_summary.error`, `pipeline_run_id`, and upstream refactor metadata as the source of truth for failed items
- Kept the artifact as a single combined JSON report so future filtering can be done from one place rather than splitting immediately into multiple files

**Testing:**
- Ran:
  - `python3 tmp/reconcile_manifest_batches.py`
- Confirmed generated artifact:
  - `tmp/manifest_may_18_searches_1.json`
- Confirmed totals:
  - `total_successes: 93`
  - `total_failures: 187`
  - `failure_count_by_step`:
    - `matcher: 176`
    - `refactoring: 11`
- Confirmed manifest-level success/failure totals:
  - `curated_top_80`: `32 completed`, `48 failed`
  - `vatsal_top_mechanics_200`: `61 completed`, `139 failed`

**Next Steps:**
- [ ] Optionally derive a success-only manifest from `manifest_may_18_searches_1.json`
- [ ] Optionally derive a failure-only investigation list grouped by matcher vs refactoring issues
- [ ] Optionally add a second tmp script that exports just the successful prompts into a relaunch-ready manifest

**Status:** Complete

### 2026-05-17 14:11 - Generated first mechanic-rooted `vatsal_top_mechanics` manifest with sidecar annotations

**Achievement:**
- Built the first mechanic-rooted catalog pass as a standard runnable batch manifest derived from the content-manager mechanic sheet
- Preserved a separate annotations sidecar so future focused passes can expand by mechanic, feel, player context, aesthetic, or meme cluster without breaking manifest compatibility

**Implementation Details:**
- Added `tmp/extract_first_100_mechanics.py`
  - reads `/Users/hassan/Downloads/game_mechanic_tags_2026-2.xlsx`
  - extracts and normalizes the first 100 mechanic rows into JSON
  - writes `tmp/first_100_mechanics_rows.json`
- Added `tmp/generate_vatsal_top_mechanics.py`
  - consumes:
    - `tmp/first_100_mechanics_rows.json`
    - `tmp/curated_limit2_prompt_only_manifest.json`
  - emits:
    - `tmp/vatsal_top_mechanics.json`
    - `tmp/vatsal_top_mechanics.annotations.json`
  - generates 2 brand/style variants per mechanic row
  - keeps the output manifest in the normal batch format with `defaults` + `runs`
- Added `tmp/validate_vatsal_top_mechanics.py`
  - validates the generated manifest with `batch_pipeline_state.resolve_manifest(...)`
  - prints a summary of total runs, unique prompts, and annotations count

**Technical Decisions:**
- Kept the new file as a **regular manifest** so it remains directly runnable by the existing batch launcher
- Used a **sidecar annotations file** instead of embedding extra metadata into the main manifest, because this keeps the launch artifact simple while still enabling future filtered/focused passes
- Used the curated manifest as an **inspiration palette** and the XLSX as the **mechanic hierarchy backbone**
- Set safer exploratory defaults for the first pass:
  - `publish: false`
  - `upload: false`
  - `limit: 6`
  - `matcher_mode: v2`

**Testing:**
- Ran:
  - `python3 tmp/extract_first_100_mechanics.py`
  - confirmed `row_count: 100`
- Ran:
  - `python3 tmp/generate_vatsal_top_mechanics.py`
  - confirmed generated outputs:
    - `tmp/vatsal_top_mechanics.json`
    - `tmp/vatsal_top_mechanics.annotations.json`
- Ran:
  - `python3 tmp/validate_vatsal_top_mechanics.py`
  - confirmed:
    - `resolved_run_count: 200`
    - `annotations_item_count: 200`
    - `unique_prompt_count: 124`

**Caveats / Follow-ups:**
- Some mechanics still produce duplicate prompt values across the two variants because the second prompt candidate can collapse to the same short key in low-entropy rows
- The first pass is structurally valid, but still needs editorial tightening before it should be considered the final production catalog

**Next Steps:**
- [ ] Tighten prompt deduplication so each mechanic produces two more distinct but still mechanic-rooted search keys where possible
- [ ] Matcher-prevalidate a sample slice of the new 200-run manifest before launching any expensive batch
- [ ] Decide whether to derive smaller follow-up manifests by cluster (cozy, horror, style, social, action) from the annotations sidecar

**Status:** Complete

### 2026-05-17 13:15 - Corrected the editorial pass to preserve brand hooks in remix prompts

**Achievement:**
- Corrected the earlier editorial pass so branded concepts were not replaced by generic concepts in the final manifest
- Restored the intended structure for the affected entries:
  - `prompt` = short mechanic/theme key
  - `remix_prompt` = explicit satirical/parody-inspired brand hook plus full mobile-first remixer guidance

**Implementation Details:**
- Updated `tmp/editorialize_curated_manifest.py`
  - changed the helper from generic concept replacement into a branded-entry normalization helper
  - helper now supports both transitional states:
    - previously swapped generic prompts
    - original brand-heavy prompts
  - helper now rewrites affected entries into short mechanic-first prompts while keeping brand references only in `remix_prompt`
- Updated `tmp/curated_limit2_prompt_only_manifest.json`
  - corrected affected entries such as:
    - `dynasty strategy drama` → satirical remix prompt inspired by Game of Thrones
    - `crime escalation strategy` → satirical remix prompt inspired by Breaking Bad
    - `forbidden romance fantasy` → satirical remix prompt inspired by Twilight
    - `workplace cringe comedy` → satirical remix prompt inspired by The Office
    - `camp slasher survival` → satirical remix prompt inspired by Friday the 13th
    - `killer doll horror` → satirical remix prompt inspired by Chucky
    - `possession horror narrative` → satirical remix prompt inspired by The Exorcist
    - `surreal psychedelic visual` → satirical remix prompt inspired by Pink Floyd
    - `retro-future comedy` → satirical remix prompt inspired by Futurama
    - `mutant team strategy` → satirical remix prompt inspired by X-Men
    - `cyberpunk rebellion chase` → satirical remix prompt inspired by Akira

**Technical Decisions:**
- Preserved brand familiarity inside the generation instruction rather than the matcher query so search remains broader and less brittle
- Used “A satirical game inspired by …” phrasing to keep the parody intent explicit in the remixer instruction
- Avoided re-replacing branded entries with generic lifestyle/mobile concepts once the desired contract was clarified

**Testing:**
- Ran:
  - `python3 tmp/editorialize_curated_manifest.py`
- Confirmed:
  - branded affected entries normalize into short mechanic-first prompts
  - brand/IP references remain in `remix_prompt`
  - a second helper run becomes stable after the rewrite

**Next Steps:**
- [ ] Decide whether to normalize the remaining brand-heavy prompts in the rest of the manifest to the same short-key + satirical-remix pattern
- [ ] Matcher-prevalidate the strongest revised entries before launching a fresh batch

**Status:** Complete

### 2026-05-17 12:42 - Applied editorial mobile-first pass to the curated batch manifest

**Achievement:**
- Kept the existing curated catalog structure intact while applying a focused editorial replacement pass for stronger Gen Z / millennial casual mobile fit
- Preserved the agreed contract:
  - `prompt` = short mechanic/search key
  - `remix_prompt` = redundant remixer instruction

**Implementation Details:**
- Added `tmp/editorialize_curated_manifest.py`
  - repeatable helper that updates the curated manifest in place
  - replaces selected weaker entries with stronger mobile-native vectors
- Updated `tmp/curated_limit2_prompt_only_manifest.json`
  - preserved defaults and overall catalog breadth
  - replaced 13 targeted entries with more casual/mobile-native concepts

**Editorial Replacements Applied:**
- `Game of Thrones dark fantasy strategy RPG` → `cozy kingdom builder`
- `Breaking Bad crime escalation strategy` → `text thread detective`
- `Twilight romance fantasy` → `closet outfit sorter`
- `The Office workplace comedy sim` → `cafe order rush`
- `Friday the 13th camp-slasher survival` → `haunted hotel hidden-object`
- `Chucky killer-doll horror` → `ghost photo mystery`
- `Exorcist possession-horror narrative` → `witch potion merge`
- `Pink Floyd surreal psychedelic visual` → `playlist mood matcher`
- `forgot-my-password first-world-problems meme` → `doomscroll reflex game`
- `avocado-toast brunch-problems meme` → `beauty shelf organizer`
- `Futurama sci-fi comedy` → `delivery route dash`
- `X-Men mutant-team strategy` → `idle hero collector`
- `Akira cyberpunk rebellion` → `neon scooter dodger`

**Technical Decisions:**
- Replaced entries that skewed too lore-heavy, too system-heavy, or too abstract relative to portrait-first casual mobile play
- Added more vectors with clearer one-thumb verbs and stronger mobile retention/readability patterns:
  - sorting
  - matching
  - merge loops
  - route/dodge loops
  - phone-native social deduction
  - aesthetic organization fantasy
- Kept the broader fandom / seasonal / aesthetic / meme coverage so the catalog still feels editorially diverse rather than over-optimized into one genre

**Testing:**
- Ran:
  - `python3 tmp/editorialize_curated_manifest.py`
- Confirmed:
  - `replacement_count: 13`
  - manifest JSON structure remained valid
  - entries continue to use short `prompt` plus redundant mobile-first `remix_prompt`

**Next Steps:**
- [ ] Optionally matcher-prevalidate the strongest replaced entries before launching a new batch
- [ ] Decide whether to launch a fresh curated batch from the revised manifest or make one more editorial tightening pass first

**Status:** Complete

### 2026-05-17 12:23 - Restored root artifact materialization to default across all published runs

**Achievement:**
- Fixed the publish-side artifact materialization flow so root `public/app.json`, `public/index.json`, and related root views no longer collapse to only the most recent publish run by default
- Preserved targeted materialization support while making the default behavior aggregate all `run_*` snapshots under the published runs directory

**Implementation Details:**
- `../game_publish_pipeline/scripts/materialize_artifact_view.py`
  - made `--runs` optional instead of required
  - added `--runs-root` with default `games/published/runs`
  - added automatic discovery of all `run_*` directories when `--runs` is omitted
  - added materialization reporting for `run_source` and `runs_root`
- `../game_publish_pipeline/scripts/refresh_app_artifacts.py`
  - stopped invoking the materializer with only the current `run_dir`
  - now invokes the materializer with `--runs-root <published runs root>` so the root artifact view is rebuilt from the full run history instead of the single latest run

**Technical Decisions:**
- Kept explicit `--runs` support for one-off remediation or investigation flows where an operator wants to materialize a specific subset of runs
- Passed `--runs-root` from `refresh_app_artifacts.py` even though the materializer now has a default, so custom publish roots still behave correctly when callers override the runs root
- Preserved `latest-wins` precedence so the newest run snapshot still overrides older collisions while keeping historical coverage intact

**Testing:**
- Verified syntax:
  - `python3 -m py_compile ../game_publish_pipeline/scripts/materialize_artifact_view.py ../game_publish_pipeline/scripts/refresh_app_artifacts.py`
- Verified default-all-runs discovery:
  - `python3 ../game_publish_pipeline/scripts/materialize_artifact_view.py --dry-run`
  - confirmed:
    - `run source: auto-discovered`
    - `run count: 12`
    - root materialization no longer scopes itself to only the current run
- Executed real write-back:
  - `python3 ../game_publish_pipeline/scripts/materialize_artifact_view.py`
  - confirmed merged root artifacts were rebuilt from all discovered runs with:
    - `merged_records: 1135`
    - `records kept after sanitization: 860`
    - `records removed as stale/missing-index: 275`
- Rebuilt matcher v2 artifacts against the rematerialized root catalog:
  - `python3 ../game_matcher_v2/cli/build_artifacts.py --force`
  - confirmed matcher v2 `game_count: 860`
- Re-ran the original debug experiment:
  - `python3 tmp/debug_first_prompt_matcher_limit6.py`
  - prompt `Mario platformer` now returns `ranked_match_count: 6` instead of the earlier single-result failure mode

**Next Steps:**
- [ ] Commit the publish materialization fix and verified corpus rebuild
- [ ] Optionally rerun a full pipeline/batch flow now that the matcher corpus has been restored

**Status:** Complete

### 2026-05-17 12:34 - Verified corpus recovery after all-runs rematerialization

**Achievement:**
- Confirmed the root published catalog and matcher v2 corpus recovered from the one-game collapsed state after real all-runs materialization
- Verified that the original `Mario platformer` `limit 6` experiment now produces the expected multi-result ranking

**Implementation Details:**
- Root published artifact view now reflects the full materialized corpus under:
  - `games/published/public/app.json`
- Matcher v2 derived artifacts now reflect the rebuilt catalog under:
  - `../game_matcher_v2/fixtures/derived/metadata.json`
  - `../game_matcher_v2/fixtures/derived/normalized_games.json`
- The debug helper outputs captured the restored ranking behavior:
  - `tmp/debug_first_prompt_selected_tags.json`
  - `tmp/debug_first_prompt_ranked_matches.json`

**Technical Decisions:**
- Validated the fix through the same exact prompt/limit experiment used during diagnosis so the before/after comparison stayed apples-to-apples
- Kept the focus on corpus correctness rather than altering matcher ranking logic, because the earlier one-result behavior was proven to be a data-view problem

**Testing:**
- Live counts after write-back:
  - root published `app.json`: `860`
  - matcher v2 derived corpus: `860`
- Repeat matcher experiment:
  - prompt: `Mario platformer`
  - limit: `6`
  - ranked results returned: `6`

**Next Steps:**
- [ ] Commit all verified changes together with the journal update

**Status:** Complete

### 2026-05-17 10:40 - Added upload auth preflight for single-run and batch launches

**Achievement:**
- Added a non-interactive gcloud auth preflight so upload-enabled runs fail fast before expensive matcher/refactor/publish work begins
- Extended the batch launcher to perform the same preflight once at batch start when any item requests upload

**Implementation Details:**
- `scripts/upload_auth_preflight.py`
  - added shared helpers for:
    - `gcloud --version`
    - `gcloud auth list --filter=status:ACTIVE --format=value(account)`
    - `gcloud config get-value project`
- `scripts/run_pipeline.py`
  - stores upload preflight payloads under `state.preflight.upload_auth`
  - records an explicit `preflight` step when `--upload` is requested
  - fails early with a clear operator-facing error if no active gcloud auth is available
- `scripts/run_batch_pipeline.py`
  - checks resolved items for `upload=true`
  - runs one shared preflight before launching item 1
  - persists the batch-level preflight result and blocks the batch if it fails
- `scripts/batch_pipeline_state.py`
  - added `preflight` to persisted batch state
  - preserves batch `blocked` status when preflight fails
- `README.md`
  - documented fail-fast upload auth preflight behavior for both single-run and batch launches

**Technical Decisions:**
- Kept the preflight non-interactive and lightweight so it catches the most common operator issue—missing/expired gcloud login—without introducing a heavy storage probe before every run
- Persisted preflight payloads directly in run and batch state so observer tooling can explain why a launch was blocked
- Chose batch-level preflight once per invocation instead of once per item because all upload-enabled items share the same local gcloud auth context

**Testing:**
- Planned validation:
  - `python3 -m py_compile scripts/upload_auth_preflight.py scripts/run_pipeline.py scripts/run_batch_pipeline.py scripts/batch_pipeline_state.py`
  - dry/local verification that batch state records preflight results before item launch

**Next Steps:**
- [ ] Validate syntax after the preflight changes
- [ ] Create the top-10 franchises manifest with `limit=1`, `publish=true`, `upload=true`
- [ ] Launch the batch and inspect whether preflight passes or blocks the run cleanly

**Status:** In Progress

### 2026-05-17 10:27 - Added durable serial batch orchestration and first-class matcher limits

**Achievement:**
- Extended the single-run pipeline CLI so matcher/refactor fan-out is configurable with a first-class `--limit`
- Added a resumable serial batch orchestration layer with persistent item state, resolved manifests, and a dedicated observer CLI

**Implementation Details:**
- `scripts/run_pipeline.py`
  - added `--limit` argument and persisted `matcher_limit` into run state, dashboard payloads, and final response payloads
  - updated matcher selection to carry forward up to `limit` matches instead of always truncating to two
  - relaxed matcher failure from “fewer than two” to “no matches” so one-item runs are valid
- `scripts/demo_pipeline_launch.py`
  - added `--limit` passthrough so the convenience launcher can drive the same single-run behavior
- `scripts/batch_pipeline_state.py`
  - added persistent batch helpers for:
    - batch directory layout
    - manifest validation/resolution
    - top-level defaults + per-item override merging
    - item files under `batch_runs/<batch_id>/items/`
    - summary/count recomputation and event logging
- `scripts/run_batch_pipeline.py`
  - added a serial batch launcher that:
    - creates a persisted batch run from `--manifest`
    - or resumes with `--resume-batch`
    - launches one child `run_pipeline.py` item at a time
    - detects the created child `pipeline_run_id`
    - reconciles persisted child run state on resume
- `scripts/observe_batch_pipeline.py`
  - added terminal/JSON/watch inspection for batch runs
- `README.md`
  - documented the new `--limit`, batch manifest shape, and batch observer commands

**Technical Decisions:**
- Kept `run_pipeline.py` as the single-run execution engine and put all queue/resume behavior into separate batch scripts for clean encapsulation
- Resolved manifest defaults once into a persisted `manifest.resolved.json` so resuming a batch never depends on future default changes
- Chose conservative resume semantics: running items reconcile against persisted child `pipeline_runs/<run_id>/run_state.json`, and items missing a child run id are blocked instead of silently relaunched

**Testing:**
- Planned validation:
  - `python3 -m py_compile scripts/run_pipeline.py scripts/demo_pipeline_launch.py scripts/batch_pipeline_state.py scripts/run_batch_pipeline.py scripts/observe_batch_pipeline.py`
  - create a minimal manifest and validate empty/synthetic observer paths plus manifest resolution behavior

**Next Steps:**
- [ ] Run syntax checks for the new batch files and updated pipeline scripts
- [ ] Create a small manifest fixture and validate batch creation/observation behavior
- [ ] Decide whether a batch HTML dashboard is worth adding later or if terminal/JSON observer coverage is enough

**Status:** In Progress

### 2026-05-17 09:57 - Added downstream visibility for soft-accepted refactor outputs

**Achievement:**
- Extended the local pipeline orchestrator and dashboard presenter so upstream refactor runs can finish with warnings without being flattened into hard failure
- Preserved downstream compatibility by continuing to consume `final_output_dirs` while surfacing the new warning-oriented status and per-game acceptance metadata

**Implementation Details:**
- `scripts/run_pipeline.py`
  - captured upstream `games_transform_soft_completed` during refactor polling
  - persisted upstream terminal status via `last_known_status`
  - preserved existing completion behavior as long as `final_output_dirs` exist
- `scripts/pipeline_dashboard_presenter.py`
  - changed refactor stage status derivation to prefer upstream `last_known_status`
  - added support for `transform_completed_with_warnings` in stage flow rendering
  - added per-card soft-acceptance fields:
    - `soft_acceptance_reason`
    - `soft_acceptance_warning_count`
  - updated refactor card copy so `soft_completed` renders as `Refactor Accepted With Warnings`
- Added tmp validation helpers for shorter, reusable verification commands:
  - `tmp/validate_soft_acceptance.py`
  - `tmp/verify_soft_acceptance_flow.py`

**Technical Decisions:**
- Kept the orchestrator contract permissive: refactoring is still operationally usable when upstream emits finalized outputs plus a warning-grade terminal status
- Treated `transform_completed_with_warnings` as distinct from hard failure, but still visually cautionary in the dashboard
- Used fixture-style tmp scripts instead of long inline Python one-liners so verification is easier to rerun and less brittle

**Testing:**
- Syntax validation:
  - `python3 -m py_compile ../game_refactoring/scripts/create_run.py ../game_refactoring/scripts/run_operator_pipeline_game.py ../game_refactoring/scripts/run_operator_pipeline_batch.py ../game_refactoring/scripts/creative_refactor_cli.py ../game_refactoring/scripts/build_dashboard.py scripts/run_pipeline.py scripts/pipeline_dashboard_presenter.py`
- Soft-acceptance eligibility proof:
  - `python3 tmp/validate_soft_acceptance.py`
  - confirmed the failed `Archive Rush 3D` workspace is eligible because it has:
    - playable `index.html`
    - `assets/`
    - passing runtime evidence checks
    - screenshots
    - only contract/finalization-style unresolved artifacts remaining
- End-to-end downstream proof:
  - `python3 tmp/verify_soft_acceptance_flow.py`
  - confirmed fixture output flows through:
    - upstream `status`: `transform_completed_with_warnings`
    - dashboard summary soft-completed counters
    - pipeline presenter refactor stage status
    - refactor card warning messaging for `Archive Rush 3D`

**Next Steps:**
- [ ] Run one real upstream refactor execution after this code pass so the new state is produced by live code, not only by fixture simulation
- [ ] Decide whether publish/finalize should optionally exclude `soft_completed` outputs unless an operator explicitly opts in

**Status:** Complete

### 2026-05-17 08:44 - Expanded dashboard to show failed refactor entries plus publish/finalize path status

**Achievement:**
- Fixed the local pipeline dashboard so refactor cards no longer hide failed games
- Added clearer publish and finalize sections so skipped publish state and finalized output copy paths are visible
- Verified the latest `3d gta game` run now exposes the failed `Archive Rush 3D` refactor item with its error and paths

**Implementation Details:**
- `scripts/pipeline_dashboard_presenter.py`
  - changed `build_refactor_cards(...)` to load upstream refactoring dashboard payloads and build cards from all upstream game entries, not just successful `final_output_dirs`
  - successful refactor cards still expose local preview URLs when finalized output exists
  - failed refactor cards now expose:
    - `status`
    - `phase`
    - `local_path`
    - `input_mirror_path`
    - `upstream_output_path`
    - `last_error`
  - added `build_finalize_cards(...)` using finalize step details and finalized output dirs
  - improved `build_publish_cards(...)` so when publish has no CDN entries it still shows a status card with the skip reason
  - added a `Finalize` stage tile to `stage_flow`
  - updated browser rendering to display:
    - failure-aware refactor cards
    - status-aware publish cards
    - finalize cards with source/destination/local paths

**Technical Decisions:**
- Kept the fix in the presentation layer because upstream run data was already correct and complete
- Used upstream refactor dashboard `games[*]` as the source of truth for per-game refactor outcomes
- Preserved successful preview behavior while extending visibility for failures and local finalize copy behavior

**Testing:**
- Recompiled presenter:
  - `python3 -m py_compile scripts/pipeline_dashboard_presenter.py`
- Refreshed dashboard assets for:
  - `pipeline_runs/run_pipeline_20260517T140907Z`
- Verified refreshed dashboard payload now includes:
  - failed refactor card for `Archive Rush 3D`
  - `last_error: node_01_remix_v5_super_operator failed after retries; last_status=failed`
  - `input_mirror_path` and upstream/local output paths for the failed item
  - publish status card with reason `publish flag not provided`
  - finalize card with source and destination paths for the finalized successful output

**Next Steps:**
- [ ] Optionally surface upstream working-clone/operator artifact paths too if you want one-click failure investigation links
- [ ] Optionally do a browser UI pass on the refreshed dashboard if another visual verification is requested

**Status:** Complete

### 2026-05-17 08:03 - Added root-view sanitization to published artifact materialization

**Achievement:**
- Fixed the published-root inconsistency that allowed matcher/refactoring to target entries whose root `public` assets did not actually exist
- Added sanitization to the publish-pipeline materializer so root catalog views now prune non-materialized entries
- Verified the problematic GTA-like composite key was removed from the root views after rematerialization

**Implementation Details:**
- `../game_publish_pipeline/scripts/materialize_artifact_view.py`
  - added safe path resolution helpers for record-backed index paths
  - added scope-aware candidate path resolution using:
    - `public_index_html`
    - `obfuscated_index_html`
    - `index_html`
    - `published_path/index.html`
  - added a sanitization pass that removes merged records when none of the target `index.html` candidates exist in the target scope root
  - applied the same pruning logic to:
    - `index.json`
    - `app_tags.json`
    - `app.json`
  - added reporting for:
    - merged record count
    - kept record count
    - removed record count
    - removed sample keys
- `../game_publish_pipeline/README.md`
  - documented that root-view materialization now sanitizes against real root assets
- Temporary validation helpers added:
  - `tmp/rematerialize_with_sanitization.py`
  - `tmp/verify_sanitization_downstream.py`

**Technical Decisions:**
- Fixed the issue at the materialized-view boundary instead of only patching the local orchestrator, because the root published catalog should be trustworthy for all downstream consumers
- Chose default-on sanitization so root metadata cannot drift ahead of the actual root asset tree
- Required real `index.html` existence as the acceptance condition because downstream refactoring source resolution ultimately depends on a playable materialized path

**Testing:**
- Re-ran full-run materialization across 8 discovered published runs
- Sanitization pruned 275 stale entries from each root artifact view
- Verified the problematic key was removed from root `public/app.json`:
  - `gamezone-29e7c3b5-974b-47c7-b7bf-585b6d5cc301__remix-2d9ceef4234dc323cd850ecec55d170a`
- Verified downstream matcher impact:
  - target key no longer present in root `public/app.json`
  - target game id no longer appears in top matcher results for `3d gta game` after rebuild

**Next Steps:**
- [ ] Optionally add a `--no-sanitize` escape hatch if operators ever need to inspect raw merged metadata for debugging
- [ ] Decide whether the orchestrator should still defensively skip non-resolvable matches as a second layer of protection

**Status:** Complete

### 2026-05-17 07:48 - Added large live stopwatch timer to the dashboard

**Achievement:**
- Added a large, visually prominent stopwatch-style timer near the top of the dashboard
- The timer now counts live from run `started_at` until the run ends, then freezes on the final elapsed value

**Implementation Details:**
- `scripts/pipeline_dashboard_presenter.py`
  - added browser-side time parsing and clock-format helpers
  - added `renderRunTimer(...)` to display a large `MM:SS` / `HH:MM:SS` counter
  - added `updateLiveRunTimer()` and `installLiveRunTimerTick()` so the timer updates every second in the browser
  - wired the timer to persisted run timing fields via `data-started-at` and `data-ended-at`
- Updated docs to explain the difference between:
  - static human-readable duration summaries
  - the large live stopwatch counter

**Technical Decisions:**
- Kept the stopwatch ticking in browser JavaScript while preserving artifact-backed timing as the source of truth for final durations
- Reused the existing 5-second dashboard refresh loop and added a separate 1-second UI-only timer tick for smoother elapsed-time feedback

**Testing:**
- Confirmed the new run timing payload already exposes the timestamps required by the live counter
- Prepared validation updates so future checks can confirm the timer HTML wiring exists alongside the timing payload

**Next Steps:**
- [ ] Extend the tmp validator to assert the generated HTML contains the live timer hooks
- [ ] Optionally do a visual browser pass on the fresh dashboard if requested

**Status:** Complete

### 2026-05-17 07:40 - Added dashboard stage durations and sample-case maintenance documentation

**Achievement:**
- Added human-readable run timing and per-stage durations to the local pipeline dashboard
- Documented a concrete maintenance workflow using one successful and one failed sample run from persisted artifacts
- Kept the change localized to the dashboard presentation layer plus a small payload-contract cleanup for `completed_at`

**Implementation Details:**
- `scripts/pipeline_dashboard_presenter.py`
  - added timestamp parsing helpers for ISO-8601 values from persisted run artifacts
  - added duration formatting for human-readable output such as `22s`, `4m 25s`, and `5m 7s`
  - extended `current_run_view` with run-level timing metadata
  - extended `stage_flow` items with stage-level timing metadata derived from `steps[*].details.started_at` / `completed_at`
  - updated dashboard HTML rendering to show:
    - Started
    - Finished
    - Total Time
    - per-stage Duration / Started / Ended values
- `scripts/run_pipeline.py`
  - added `completed_at` to the dashboard base payload so completed runs expose a cleaner timing contract
- `README.md`
  - added a short dashboard timing and maintenance reference section
- `docs/pipeline-dashboard-maintenance.md`
  - added a future-facing maintenance document covering artifact sources, sample runs, validation flow, and troubleshooting notes

**Sample Cases:**
- Successful run:
  - `pipeline_runs/run_pipeline_20260517T110057Z`
  - expected durations after refresh:
    - total: `5m 7s`
    - match: `22s`
    - refactor: `4m 25s`
    - publish: `20s`
- Failed run:
  - `pipeline_runs/run_pipeline_20260517T124528Z`
  - expected durations after refresh:
    - total: `20s`
    - match failed after `20s`
    - refactor/publish remain pending with no duration values

**Technical Decisions:**
- Computed durations in the presenter layer instead of browser-only JavaScript so the dashboard contract stays reusable for future observer tooling and documentation
- Reused persisted step timestamps rather than inventing new orchestration state
- Treated `updated_at` as the fallback end marker only when a run or stage has started but not yet exposed an explicit completed timestamp

**Testing:**
- Refreshed dashboard assets for both sample runs and verified the enriched payloads now include timing blocks
- Confirmed successful-run stage timings resolved from real step artifacts:
  - matcher `22s`
  - refactoring `4m 25s`
  - publish `20s`
- Confirmed failed-run matcher timing resolved to `20s` while untouched pending stages remained unset

**Next Steps:**
- [ ] Optionally mirror the same timing summary in `observe_pipeline_run.py` terminal output if operators want parity with the HTML dashboard
- [ ] Optionally add a browser-level visual check of the refreshed dashboard cards if another UI pass is requested

**Status:** Complete

### 2026-05-17 07:24 - Materialized all published runs and restored GTA-like matcher coverage

**Achievement:**
- Materialized the root published artifact views from all discovered published run snapshots
- Expanded `games/published/public/app.json` from the previously observed 2-record slice to a merged 1,131-record catalog
- Confirmed `game_matcher_v2` now returns real ranked matches for `3d game gta` once the root catalog was rebuilt from all runs

**Implementation Details:**
- Used the publish-pipeline materializer across all discovered run snapshots under `games/published/runs/`
- Materialization merged 8 run directories into the root published views with `latest-wins` precedence
- Rebuilt root artifacts:
  - `games/published/public/index.json`
  - `games/published/public/app_tags.json`
  - `games/published/public/app.json`
  - `games/published/obfuscated/index.json`
  - `games/published/obfuscated/app_tags.json`
  - `games/published/obfuscated/app.json`
- Resulting merged record counts:
  - public `index.json`: 1,131
  - public `app_tags.json`: 1,131
  - public `app.json`: 1,131
  - obfuscated `index.json`: 1,131
  - obfuscated `app_tags.json`: 1,131
  - obfuscated `app.json`: 1,131

**Technical Decisions:**
- Kept the v2-only matcher repair in place and did not add deprecated matcher fallback logic
- Confirmed the original path assumption was already correct (`games/published/public/app.json`); the real issue was that the root view had not been materialized from the full run history
- Treated root-view materialization as the correct recovery path because `game_matcher_v2` derives its controlled vocabulary from the root published catalog

**Testing:**
- After materialization, direct `game_matcher_v2` CLI probing showed:
  - prompt `3d game gta` now returns 2 ranked matches
  - top hits included GTA-like tags such as:
    - `Third person shooter`
    - `Grand Theft Auto`
    - `urban crime spree`
    - `police pursuit`
    - `open urban sandbox`
- `mario kart racing xmas style` continued returning ranked matches successfully after the expanded catalog rebuild

**Next Steps:**
- [ ] Re-run the demo launcher against `3d game gta` using the materialized root catalog if needed for another end-to-end confirmation
- [ ] Decide whether all-runs materialization should become part of the normal publish refresh workflow or remain an operator repair step

**Status:** Complete

---

### 2026-05-17 07:05 - Repaired match v2 no-coverage behavior and clarified corpus limits

**Achievement:**
- Repaired `game_matcher_v2` so prompts with no controlled-vocabulary coverage now return an empty ranked result instead of crashing inside selector validation
- Updated the local orchestrator to surface the no-coverage case as an explicit matcher failure message instead of the older generic selector error
- Confirmed the current published corpus is still only two holiday-kart games, so matcher source pathing was not the actual root cause

**Implementation Details:**
- `../game_matcher_v2/game_matcher_v2/selector.py`
  - removed the hard failure on an empty validated tag payload
  - empty `{}` selected-tags payloads are now treated as a valid no-coverage outcome
- `../game_matcher_v2/game_matcher_v2/scorer.py`
  - returns `[]` immediately when no validated tags remain after normalization
- `scripts/run_pipeline.py`
  - detects `matcher_mode == "v2"` with zero matches and raises a specific error:
    - `matcher v2 had no controlled-vocabulary coverage for prompt`
  - preserves strict pipeline failure semantics while making the failure reason operator-readable
- Temporary validation helpers created during repair:
  - `tmp/matcher_corpus_probe.py`
  - `tmp/validate_matcher_v2.py`
  - `tmp/validate_pipeline_no_coverage.py`

**Technical Decisions:**
- Kept strict fail-hard behavior at the orchestrator level because downstream refactoring still requires two concrete source matches
- Relaxed match-v2 internals instead of fabricating unrelated tags, so low-coverage prompts fail honestly rather than producing misleading holiday/kart matches
- Confirmed that `games/published/public/app.json` is already the correct source path, but it currently contains only 2 entries, so corpus breadth is a separate data problem rather than a path bug

**Testing:**
- Corpus probe:
  - `python3 tmp/matcher_corpus_probe.py`
  - confirmed both published app.json files contain only 2 entries
- Matcher validation:
  - `python3 tmp/validate_matcher_v2.py`
  - `3d game gta` now exits `0` with:
    - `result_payload: []`
    - `tags_payload: {}`
  - `mario kart racing xmas style` still returns 2 ranked matches with validated tags
- Orchestrator validation:
  - `python3 tmp/validate_pipeline_no_coverage.py`
  - confirmed pipeline now fails with explicit error:
    - `matcher v2 had no controlled-vocabulary coverage for prompt`

**Next Steps:**
- [ ] Decide whether to keep the temporary validation helpers or remove them after review
- [ ] Broaden the published tagged corpus if match v2 needs to support prompts outside the current holiday-kart slice

**Status:** Complete

---

### 2026-05-17 06:47 - Validated demo launcher wiring against the current dashboard

**Achievement:**
- Confirmed `scripts/demo_pipeline_launch.py` launches a brand-new run and opens/serves the dashboard for that exact run id
- Verified the current dashboard is not stale or pointed at an older successful run when a new run fails early
- Reconciled the journal status with the codebase: observer CLI, live dashboard, and local dashboard server are implemented and validated

**Implementation Details:**
- Validation flow used:
  - `python3 scripts/demo_pipeline_launch.py "3d game gta" --no-open`
- New run created during validation:
  - run id: `run_pipeline_20260517T124528Z`
  - dashboard URL: `http://127.0.0.1:8438/index.html`
- Inspected generated artifacts for the new run:
  - `pipeline_runs/run_pipeline_20260517T124528Z/run_state.json`
  - `pipeline_runs/run_pipeline_20260517T124528Z/dashboard/dashboard_data.json`
  - `pipeline_runs/run_pipeline_20260517T124528Z/matcher/matcher.command.json`
  - `pipeline_runs/run_pipeline_20260517T124528Z/matcher/matcher.stderr.txt`
- The matcher failed for this prompt with:
  - `selector output did not contain any valid controlled-vocabulary tags`
- Despite the matcher failure, the served dashboard correctly showed:
  - prompt `3d game gta`
  - run id `run_pipeline_20260517T124528Z`
  - failed matcher state for the current run
  - older successful runs only inside the separate `recent_runs` section

**Technical Decisions:**
- Treated the dashboard payload files and served page as the source of truth for validation rather than relying on the journal’s older phase labels
- Counted this as dashboard validation success even though the pipeline prompt failed, because the objective of this check was wiring/freshness of the dashboard, not matcher prompt quality

**Testing:**
- Demo launcher created a fresh run directory and reported a matching dashboard URL
- Visual inspection of the served page confirmed it reflected the new failed run rather than a stale older run
- Artifact inspection confirmed `dashboard_data.json` and `run_state.json` matched the same fresh run id and failure details

**Next Steps:**
- [ ] If desired, retry demo validation with a matcher-friendly prompt that produces valid controlled-vocabulary tags
- [ ] Keep Phase 2 journal items focused on orchestration robustness while treating dashboard validation as complete

**Status:** Complete

---

### 2026-05-17 05:09 - Completed v5 workflow migration and scoped upload verification

**Achievement:**
- Completed the local orchestrator migration from the old v4 refactoring handoff to `creative_remix_v5`
- Fixed publish-stage upload scoping so GCS sync targets only the current run's game ids instead of sweeping the entire published roots
- Verified the end-to-end publish+upload path with a clean rerun and live dashboard

**Implementation Details:**
- `scripts/run_pipeline.py`
  - launches `creative_remix_v5` through `scripts/game_workflow.py`
  - derives upload scope from the publish report via `extract_publish_game_ids(...)`
  - invokes `scripts/sync_to_gcs.py` with `--mode per-item` and repeated `--only-item <game_id>` arguments
- Successful verification run:
  - prompt: `starwars meets kawaii space invaders`
  - run id: `run_pipeline_20260517T110057Z`
  - dashboard: `http://127.0.0.1:8602/index.html`
- Verified upload payload reported only:
  - `gamezone-34c63716-4569-4f8a-8b34-355250dda951`
  - `gamezone-e5741de0-8da4-4b6d-8eab-9771c3300be2`

**Technical Decisions:**
- Scoped the fix inside `game_generator` because the regression came from this orchestrator's broad upload invocation, while the sibling publish tool already supported item-level targeting
- Preserved the existing publish pipeline contract and reused `sync_to_gcs.py --only-item` rather than introducing a new upload manifest shape

**Testing:**
- `python3 -m py_compile scripts/run_pipeline.py`
- temp helper validation confirmed scoped upload arguments are built from publish-report game ids
- live rerun confirmed:
  - publish completed
  - upload completed
  - dashboard opened successfully
  - upload summary `only_items` matched the current run ids

**Next Steps:**
- [x] Run lightweight validation checks on the scoped-upload change
- [x] Re-run the themed publish+upload flow
- [x] Confirm upload artifacts show only current-run game ids being synced

**Status:** Complete

---

### 2026-05-17 04:58 - Scoped publish upload to current run game ids

**Achievement:**
- Identified that publish+upload runs were spending time syncing the entire published roots instead of just the game ids produced by the current pipeline run
- Updated the orchestrator upload handoff to scope `sync_to_gcs.py` to the current run's game ids only

**Implementation Details:**
- Modified `scripts/run_pipeline.py` to derive ordered `game_id` values from the publish report's deployment and obfuscation sections
- Updated the upload invocation from a broad `sync_to_gcs.py --target both` call to a scoped per-item call using:
  - `--mode per-item`
  - repeated `--only-item <game_id>` arguments for the current run
- Added guardrails so upload now fails fast if the publish report does not expose game ids needed for a scoped sync

**Technical Decisions:**
- Kept the fix local to `game_generator` rather than modifying the sibling publish pipeline because the immediate regression was caused by how this orchestrator invoked `sync_to_gcs.py`
- Reused existing `sync_to_gcs.py --only-item` support instead of inventing a new manifest contract for uploads

**Testing:**
- Validate that `scripts/run_pipeline.py` compiles cleanly after the upload scoping change
- Re-run a publish+upload flow and inspect `sync_to_gcs.command.json` to confirm it contains only run-scoped `--only-item` values

**Next Steps:**
- [ ] Run lightweight validation checks on the scoped-upload change
- [ ] Re-run the themed publish+upload flow
- [ ] Confirm upload artifacts show only current-run game ids being synced

**Status:** In Progress

---

### 2026-05-17 04:25 - Switched orchestrator workflow handoff from v4 to v5

**Achievement:**
- Updated the local orchestrator to launch the upstream `creative_remix_v5` workflow instead of `creative_remix_v4`
- Reconfirmed that the v5 source of truth lives in the sibling `../game_refactoring` repository docs and workflow registry
- Prepared validation around the user-provided test query `mario bros platformer`

**Implementation Details:**
- Modified `scripts/run_pipeline.py` so `PipelineRun.run_refactoring()` now launches `scripts/game_workflow.py --json --id creative_remix_v5`
- Updated orchestrator docstrings/comments that still described the older v4 workflow handoff
- Revalidated upstream references in:
  - `../game_refactoring/docs/game_workflow_cli.md`
  - `../game_refactoring/scripts/game_workflow.py`
  - `../game_refactoring/docs/operator_pipeline_manual.md`

**Technical Decisions:**
- Kept the existing manifest-driven integration boundary unchanged because the upstream v5 workflow still uses the same `game_workflow.py` launcher contract and `--games-manifest-source` handoff pattern
- Treated the sibling repo documentation and workflow registry as authoritative rather than relying on older local comments or historical journal notes

**Testing:**
- Verify the orchestrator now references `creative_remix_v5` as the workflow id in `scripts/run_pipeline.py`
- Run the pipeline with the test query `mario bros platformer` and confirm the refactoring launch artifacts record the v5 workflow handoff

**Next Steps:**
- [ ] Run lightweight validation checks on the updated orchestrator and journal changes
- [ ] Execute a verification flow using `mario bros platformer`
- [ ] Inspect generated run artifacts for the v5 workflow id and handoff metadata

**Status:** In Progress

---

### 2026-04-26 19:12 - Initial Setup

**What Changed:**
- Created journal structure for the game pipeline orchestrator feature
- Recorded the agreed orchestration model and observability requirements
- Outlined implementation phases for orchestrator, observer, and dashboard work

**Why:**
This task spans multiple phases, integrates several sibling repositories, and requires architectural decisions around strict failure handling and observability. A dedicated journal is required to preserve implementation context and decisions.

**Files Created:**
- `docs/journals/game-pipeline-orchestrator.md` - Tracks architecture, decisions, progress, and verification for the orchestrator feature

**Next Steps:**
- [ ] Inspect current repository structure for new CLI/module placement
- [ ] Implement the file-backed run model and orchestrator skeleton
- [ ] Add observer and dashboard support around the persisted run state

**Status:** In Progress

---

## 🐛 Known Issues

### Upstream CLI contract drift

**Problem:** 
The orchestrator journal documented older remix editor and obfuscator command/result expectations, while the sibling repositories now expose richer payloads and an obfuscator `output-path` contract instead of a remix-style result shape.

**Root Cause:** 
The orchestrator integration notes and implementation were created before the latest upstream CLI contract updates landed.

**Status:** 
- [ ] Being investigated
- [ ] Blocked (waiting for...)
- [x] Fixed

**Workaround:** 
Use the sibling repo CLI implementations as the source of truth when validating integration behavior.

**Resolution:** 
Updated the orchestrator plan and implementation to align with the current remix editor `start-batch/status/result` payloads and the obfuscator `start/status/output-path` contract. Additional orchestration issues were later identified around long-running async stage retries, cancellation, and stale status polling that can miss a completed upstream remix-editor run without a reconciliation pass.

---

## 🔧 Backend API Reference

### External CLI Contracts

**Matcher:**
- `../game_matcher/cli/game_matcher_cli.py`
- Expected to accept a prompt and return ranked JSON results including usable `game_id` values

**Remixer Lookup:**
```bash
cd /Volumes/Elements/game_remixer
./get_game GAMEID
```

Returns:
- absolute `index.html` path on success
- exit `1` on not found / missing export root
- exit `2` on invalid usage

**Remix Editor:**
```bash
python3 /Volumes/Elements/game_remix_editor/scripts/creative_refactor_cli.py --json start-batch --manifest <manifest> --remix-prompt "<prompt>" --poll-seconds <seconds>
python3 /Volumes/Elements/game_remix_editor/scripts/creative_refactor_cli.py --json status --run-id <run_id>
python3 /Volumes/Elements/game_remix_editor/scripts/creative_refactor_cli.py --json result --run-id <run_id>
```

Start payload includes at least:
- `run_id`
- `run_dir`
- `status_path`
- `dashboard_path`
- `output_root`
- `status`
- `current_phase`

Status/result payloads include canonical run metadata and expose `final_output_dirs` only once the run is terminal.

**Obfuscator:**
```bash
python3 /Volumes/Elements/game_obfuscator/scripts/game_obfuscator_cli.py start --manifest <manifest>
python3 /Volumes/Elements/game_obfuscator/scripts/game_obfuscator_cli.py status --run-id <run_id>
python3 /Volumes/Elements/game_obfuscator/scripts/game_obfuscator_cli.py output-path --run-id <run_id> --include-games
```

Start payload includes at least:
- `run_id`
- `run_dir`
- `status_path`
- `dashboard_path`
- `output_root`
- `status`
- `current_phase`

Status payload includes:
- `run_id`
- `run_dir`
- `status`
- `current_phase`
- `dashboard_path`
- `output_root`
- `completed`

Output payload includes:
- `run_id`
- `run_dir`
- `status`
- `current_phase`
- `output_path`
- `completed`

Optional:
- `game_outputs` when `--include-games` is passed

---

## 📚 Quick Reference

### Key Files

- `docs/journals/game-pipeline-orchestrator.md` - Feature journal
- `clineflow/PROCEDURES.md` - Workflow and journaling rules
- `clineflow/JOURNAL_TEMPLATE.md` - Journal template reference

### Planned New Files

- `scripts/run_pipeline.py` - Main orchestrator CLI
- `scripts/observe_pipeline_run.py` - Terminal/JSON observer CLI
- `scripts/serve_pipeline_dashboard.py` - Lightweight HTTP server for dashboard viewing
- `pipeline_runs/<run_id>/...` - Persisted run artifacts, state, and dashboard data

### Important Commands

```bash
# Planned orchestrator usage
python3 scripts/run_pipeline.py "a harry potter flappy bird game" --obfuscate

# Planned observer usage
python3 scripts/observe_pipeline_run.py --run-dir pipeline_runs/<run_id>
python3 scripts/observe_pipeline_run.py --run-dir pipeline_runs/<run_id> --json
python3 scripts/observe_pipeline_run.py --run-dir pipeline_runs/<run_id> --watch

# Planned dashboard serving
python3 scripts/serve_pipeline_dashboard.py --run-dir pipeline_runs/<run_id>
```

---

## 💭 Notes & Decisions

### Design Decisions

**Decision:** Use a file-backed run directory as the single source of truth.  
**Rationale:** This enables strict observability, post-failure inspection, simple dashboard rendering, and clear artifact retention without requiring a live backend service.  
**Alternatives Considered:** Direct console-only orchestration was rejected because it does not provide durable state or a strong basis for an observer/dashboard.

**Decision:** Use strict fail-hard behavior for matcher and `get_game`.  
**Rationale:** The user explicitly expects 500-class failure semantics if these upstream contracts fail.  
**Alternatives Considered:** Fallback to lower-ranked matches was rejected.

**Decision:** Observer should support both JSON mode and an HTML dashboard.  
**Rationale:** JSON mode supports automation and debugging, while the HTML dashboard provides a detailed human-readable live view with auto-update.  
**Alternatives Considered:** Terminal-only observer was rejected as insufficiently observable.

**Decision:** Treat sibling CLI implementations as the authoritative source of contract truth.  
**Rationale:** The remix editor and obfuscator contracts evolve independently; reading the live CLI implementations avoids drift between journal notes and actual payload semantics.  
**Alternatives Considered:** Relying on journal-only contract notes was rejected because it had already drifted from the current upstream behavior.

### Future Enhancements

**Nice to Have:**
- Resume/retry support for partially completed runs
- Richer artifact linking and drill-down views in the dashboard

**Potential Improvements:**
- Aggregate metrics across pipeline runs
- Optional compression/export of final results
- Escalating retry ladder for `remix_editor` and `obfuscator` with explicit upstream cancellation between attempts
- Terminal reconciliation against upstream remix-editor status/result artifacts when live polling appears stale

---

## ✅ Testing Checklist

- [ ] Integration flow validates CLI contracts against sibling tools
- [ ] Manual testing scenarios:
  - [ ] Matcher success path
  - [ ] `get_game` failure path
  - [ ] Remix editor polling path
  - [ ] Obfuscator polling path
  - [ ] Dashboard auto-update behavior
- [ ] HTML dashboard loads over local HTTP server
- [ ] Observer JSON output is stable and machine-readable

---

## 🎯 Success Criteria

- [ ] All phases completed
- [ ] Orchestrator produces fully observable persisted runs
- [ ] Observer CLI supports terminal and JSON modes
- [ ] HTML dashboard auto-updates from run data
- [ ] Final output is copied to a stable output location
- [ ] Strict failure handling is enforced across upstream steps
- [ ] Remix editor and obfuscator integrations match current upstream CLI contracts
