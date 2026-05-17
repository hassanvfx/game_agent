# Game Pipeline Orchestrator Implementation Journal

**Last Updated:** 2026-05-17 08:03 America/Mexico_City  
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
