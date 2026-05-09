# Game Refactoring External In-Place Runs Journal

**Last Updated:** 2026-05-08  
**Feature Spec:** N/A  
**Backend Reference:** N/A

---

## 📊 Implementation Status Overview

### ✅ Phase 1: Repository Hygiene and Storage Policy - **COMPLETE**

- [x] Mirror the external `.gitignore` baseline into the repo root
- [x] Ignore common tool-generated run/output artifacts
- [x] Keep `games/` as a tracked documentation shell while ignoring local contents

**Status:** ✅ Complete

### ✅ Phase 2: `game_refactoring` External Run-Root Support - **COMPLETE**

- [x] Audit hardcoded `runs/` assumptions in the production path
- [x] Add optional custom `--runs-root` support while preserving default behavior
- [x] Preserve legacy `--run-id` behavior for default-root runs
- [x] Keep `--source-mode inplace` behavior intact

**Status:** ✅ Complete

### ✅ Phase 3: External In-Place Experiment and Runtime Fixes - **COMPLETE**

- [x] Create a temporary single-game manifest for the first `top100_vatsal` game
- [x] Launch `creative_remix_v3` using `inplace` mode with external run storage
- [x] Diagnose the initial launcher failure
- [x] Fix dashboard handling for external in-place input paths
- [x] Resume the run and confirm operator pipeline creation

**Status:** ✅ Complete

### ✅ Phase 4: Process-Control Validation - **COMPLETE**

- [x] Exercise `kill-all --include-cline --dry-run`
- [x] Exercise the real `kill-all --include-cline`
- [x] Confirm current matcher did not detect the active experiment run
- [x] Record follow-up guidance for improving process matching

**Status:** ✅ Complete

---

## 📝 Journal Entries

### 2026-05-08 16:10 - Repo hygiene baseline and local-storage policy

**What Changed:**
- Added a root `.gitignore` using the mirror repo’s ignore baseline.
- Expanded the root ignore rules to cover generated `tools/**/runs/`, `tools/**/outputs/`, `.clineflow.local`, and generated workspace files.
- Updated repository policy so `games/` stays local-only in git while `games/README.md` remains tracked.
- Verified there are no nested `.git` directories under `tools/`.

**Why:**
This repo mixes source code with large local game assets, generated run artifacts, and per-machine tooling files. The immediate goal was to prevent accidental commits of machine-local or high-volume runtime data while preserving a clear documented structure for future work.

**Files Created:**
- `.gitignore` - Root ignore policy for repo-local and tool-generated artifacts.
- `games/README.md` - Documents that `games/` is a local storage area for raw, published, template, and generated game assets.

**Technical Decisions:**
- Chose additive ignore rules rather than deleting local content.
- Kept only documentation tracked under `games/` and ignored the rest.
- Used broad tool-level ignore patterns because multiple tools already create their own run/output folders.

**Status:** Complete

---

### 2026-05-08 16:24 - Audit and implementation of custom external run-root support

**Achievement:**
Added optional external run-root support to the production `game_refactoring` path without changing default behavior.

**Implementation Details:**
- Modified `tools/game_refactoring/scripts/create_run.py`
  - added optional `--runs-root`
  - persisted `run_dir` and `runs_root` into `run_state.json`
- Modified `tools/game_refactoring/scripts/creative_refactor_cli.py`
  - added `--runs-root` to batch-start flows
  - forwarded `--runs-root` to `create_run.py`
  - changed downstream batch launch to prefer `--run-dir <resolved path>`
- Modified `tools/game_refactoring/scripts/run_operator_pipeline_batch.py`
  - added `--run-dir` and `--runs-root`
  - preserved `--run-id` fallback to repo-local `runs/`
- Modified `tools/game_refactoring/scripts/run_parallel_batch.py`
  - added `--run-dir` and `--runs-root`
  - preserved default-root compatibility
- Modified `tools/game_refactoring/scripts/game_workflow.py`
  - added `--runs-root`
  - passed it through to `creative_refactor_cli.py`

**Code Snippet:**
```python
# tools/game_refactoring/scripts/create_run.py
parser.add_argument(
    "--runs-root",
    help="Optional custom root directory under which the run directory should be created. Defaults to the repo-local runs/ directory.",
)

runs_root = Path(args.runs_root).resolve() if args.runs_root else RUNS_ROOT
run_dir = runs_root / run_id
```

**Technical Decisions:**
- Followed a strict compatibility rule:
  - no new flag provided → old behavior unchanged
- Treated resolved absolute `run_dir` as the runtime source of truth
- Preserved `--run-id` as a backward-compatible convenience for default-root runs

**Testing:**
- Verified syntax by compiling:
  - `create_run.py`
  - `creative_refactor_cli.py`
  - `run_operator_pipeline_batch.py`
  - `run_parallel_batch.py`
  - `game_workflow.py`

**Status:** Complete

---

### 2026-05-08 16:29 - External in-place experiment setup pattern

**Achievement:**
Established a reusable pattern for running `game_refactoring` against games stored outside the tool repo, without copying inputs, while storing run artifacts externally.

**Implementation Details:**
- Created temporary fixture space:
  - `tmp/game_refactoring_experiments/fixtures/`
- Wrote a single-game manifest:
  - `tmp/game_refactoring_experiments/fixtures/top100_vatsal_first_game_manifest.json`
- Selected first game from `games/top100_vatsal/`:
  - `/Users/hassan/repos/game_agent/games/top100_vatsal/gamezone-0a438816-ecee-420b-afd6-4a36ddc935e3`
- Launched workflow:
  - `creative_remix_v3`
  - `--source-mode inplace`
  - `--runs-root /Volumes/backup/output/remixed`

**Experiment command pattern:**
```bash
python3 tools/game_refactoring/scripts/game_workflow.py \
  --json \
  --id creative_remix_v3 \
  --games-manifest-source tmp/game_refactoring_experiments/fixtures/top100_vatsal_first_game_manifest.json \
  --source-mode inplace \
  --runs-root /Volumes/backup/output/remixed
```

**Resolved run metadata:**
- `run_id`: `run_game_remixer_20260508T222946Z`
- `run_dir`: `/Volumes/backup/output/remixed/run_game_remixer_20260508T222946Z`
- `output_root`: `/Volumes/backup/output/remixed/run_game_remixer_20260508T222946Z/output`

**Technical Decisions:**
- Kept the workflow-generated manifest under repo-local `tools/game_refactoring/runs/_workflow_manifests/`
- Sent the real run scaffold, dashboard, logs, and transformed outputs to `/Volumes/backup/output/remixed`
- Used `inplace` mode so the source game remains the original directory and is not mirrored into the run input folder

**Reusable Pattern for Future Runs:**
1. Create a temp fixture manifest under `tmp/game_refactoring_experiments/fixtures/`
2. Point `source_path` to the real external or shared source game directory
3. Use `--source-mode inplace`
4. Use `--runs-root /Volumes/.../desired-output-root`
5. Treat `<runs-root>/<run_id>/output/<game_id>/` as the actual transformed output destination

**Status:** Complete

---

### 2026-05-08 16:31 - Dashboard bug discovered and fixed for external in-place sources

**Problem Encountered:**
The experiment appeared stuck and no operator pipeline directory showed up at first.

**Investigation:**
- Checked launcher stderr and run state.
- Found the batch runner was crashing during the first dashboard build.
- Reproduced the failure directly with:
  - `python3 tools/game_refactoring/scripts/build_dashboard.py --run-dir /Volumes/backup/output/remixed/run_game_remixer_20260508T222946Z`

**Root Cause:**
`tools/game_refactoring/scripts/build_dashboard.py` assumed all input paths lived under the `game_refactoring` repo root:

```python
def relative_url(path: Path, root: Path) -> str:
    return "/" + path.relative_to(root).as_posix()
```

That assumption breaks in `inplace` mode when `input_mirror_path` points to an external game such as:

```text
/Users/hassan/repos/game_agent/games/top100_vatsal/gamezone-.../index.html
```

**Solution:**
Updated `relative_url()` to fall back to an absolute `file://` URI when the path is outside the tool root.

**Code Snippet:**
```python
def relative_url(path: Path, root: Path) -> str:
    try:
        return "/" + path.relative_to(root).as_posix()
    except ValueError:
        return path.resolve().as_uri()
```

**Result:**
- Dashboard generation succeeded for external in-place inputs.
- Resumed the existing run manually.
- Confirmed operator pipeline directories were created, including:
  - `operator_pipeline/current`
  - `operator_pipeline/node_01_remix_inference/attempt_01`

**Lessons Learned:**
Any tool that reads source files directly from `input_mirror_path` must not assume the path is under `tools/game_refactoring/`. External in-place runs make that assumption invalid.

**Status:** Complete

---

### 2026-05-08 16:33 - `kill-all --include-cline` exercised and process-matching gap documented

**Problem Encountered:**
The `kill-all --include-cline` command did not match the active experiment even while the run still reported as running.

**Investigation:**
Exercised both:
- dry-run
- real execution

Both returned:
- `matched_count: 0`
- `success: true`

**Solution / Current State:**
No code change was made yet. The command path works and returns structured results, but the matcher is too narrow for the active experiment process tree.

**Lessons Learned:**
The process matcher in `tools/game_refactoring/scripts/process_kill_utils.py` likely needs expansion to catch:
- `game_workflow.py`
- `creative_refactor_cli.py`
- `run_operator_pipeline_batch.py`
- per-game worker processes
- optional cline descendants

**Status:** Complete

---

### 2026-05-08 16:39 - Added cross-tool kill helper for future external runs

**Achievement:**
Created a top-level helper to fan out kill-all requests across tool-local CLIs and then fall back to direct process matching.

**Implementation Details:**
- Created `scripts/kill_all_tool_runtimes.py`
- The helper:
  - calls `kill-all --include-cline` in `game_refactoring`
  - calls `kill-all --include-cline` in `game_remix_editor`
  - optionally matches direct process signatures and run-specific identifiers using `pgrep -af`
- Supports:
  - `--dry-run`
  - `--force`
  - `--run-id`
  - `--run-dir`
  - `--include-default-run-patterns`

**Why:**
The tool-local kill commands were too narrow for the active experiment, so a repo-level aggregation point was needed as a safer reusable operator command for future runs.

**Validation:**
Exercised the new helper with:
- `python3 scripts/kill_all_tool_runtimes.py --dry-run --run-id run_game_remixer_20260508T222946Z --run-dir /Volumes/backup/output/remixed/run_game_remixer_20260508T222946Z --include-default-run-patterns`

This confirmed:
- both tool-local kill commands execute successfully
- the fallback matcher can be parameterized by run id and run dir
- no current matches were detected in the present process state

**Status:** Complete

---

## 🐛 Known Issues

### `kill-all --include-cline` misses active experiment processes

**Problem:**  
The command executes successfully but may not match the currently running `game_refactoring` experiment processes.

**Root Cause:**  
Likely incomplete process signature matching in `tools/game_refactoring/scripts/process_kill_utils.py`.

**Status:** 
- [ ] Being investigated
- [ ] Blocked (waiting for...)
- [x] Fixed

**Workaround:**  
Use explicit PID/process inspection or direct run-dir based recovery/restart commands until matcher coverage is improved.

**Resolution:**  
Not resolved yet; current result is documented for follow-up hardening.

---

## 📚 Quick Reference

### Key Files

- `.gitignore` - Root ignore policy
- `games/README.md` - Documents local-only game storage policy
- `tools/game_refactoring/scripts/create_run.py` - Custom external run-root support
- `tools/game_refactoring/scripts/creative_refactor_cli.py` - Batch launcher and status/result CLI
- `tools/game_refactoring/scripts/run_operator_pipeline_batch.py` - Operator-pipeline batch path
- `tools/game_refactoring/scripts/run_parallel_batch.py` - Legacy bounded parallel path
- `tools/game_refactoring/scripts/game_workflow.py` - Workflow entrypoint
- `tools/game_refactoring/scripts/build_dashboard.py` - Dashboard builder fixed for external in-place paths
- `tmp/game_refactoring_experiments/fixtures/top100_vatsal_first_game_manifest.json` - Single-game experiment manifest

### Important Commands

```bash
# Launch an external in-place workflow run
python3 tools/game_refactoring/scripts/game_workflow.py \
  --json \
  --id creative_remix_v3 \
  --games-manifest-source tmp/game_refactoring_experiments/fixtures/top100_vatsal_first_game_manifest.json \
  --source-mode inplace \
  --runs-root /Volumes/backup/output/remixed

# Check status
python3 tools/game_refactoring/scripts/creative_refactor_cli.py \
  --json status \
  --run-dir /Volumes/backup/output/remixed/run_game_remixer_<timestamp>

# Build dashboard manually for an external run
python3 tools/game_refactoring/scripts/build_dashboard.py \
  --run-dir /Volumes/backup/output/remixed/run_game_remixer_<timestamp>

# Exercise kill-all matcher
python3 tools/game_refactoring/scripts/creative_refactor_cli.py \
  --json kill-all --include-cline --dry-run

# Fan out kill-all across supported tools plus fallback process matching
python3 scripts/kill_all_tool_runtimes.py \
  --dry-run \
  --run-id run_game_remixer_<timestamp> \
  --run-dir /Volumes/backup/output/remixed/run_game_remixer_<timestamp> \
  --include-default-run-patterns
```

### Future Enhancements

**Nice to Have:**
- Expand `kill-all` process matching so it reliably catches active experiment trees
- Move workflow-generated manifests out of repo-local `runs/_workflow_manifests` if full externalization is desired
- Consider promoting `scripts/kill_all_tool_runtimes.py` into a documented operator command with stronger process signatures

**Potential Improvements:**
- Audit other tooling for repo-local path assumptions similar to the dashboard bug
- Add an explicit smoke test for `--source-mode inplace` with external game directories

---

## ✅ Testing Checklist

- [x] Manual validation of root `.gitignore` and `games/README.md`
- [x] Python syntax compilation for modified `game_refactoring` scripts
- [x] Manual launch of one external in-place experiment run
- [x] Manual verification that run artifacts were created under `/Volumes/backup/output/remixed`
- [x] Manual verification that operator pipeline directories were eventually created
- [x] Manual reproduction and fix verification for the dashboard path bug
- [x] Manual exercise of `kill-all --include-cline`

---

## 🎯 Success Criteria

- [x] Default run behavior remains unchanged when no new path flags are provided
- [x] External run-root support works for the production `game_refactoring` path
- [x] External in-place source games can be launched without copying
- [x] Dashboard generation works for external input paths
- [x] Repository documentation records the reusable pattern for future runs

---

*This journal documents the emerging pattern for running `game_refactoring` in-place against external/shared game sources while storing run outputs under an external volume root for future repeatable workflows.*

---

### 2026-05-08 18:15 - Deterministic leased-port scaffolding and prompt contract hardening

**Achievement:**
Implemented the first concrete deterministic/exclusive browser-port refactor slice for `game_refactoring`: shared lease-state scaffolding, scheduler/worker propagation of assigned ports, and prompt hardening for the highest-risk browser-grounded operators.

**Implementation Details:**
- Created `tools/game_refactoring/scripts/port_lease_service.py`
  - shared JSON-backed lease map
  - one-time pool initialization
  - passive stale eviction
  - lease acquire / refresh / release helpers
  - default unusual port pool rooted at `43100`
  - default pool size increased to `1000`
  - default lease TTL set to `3 hours`
- Modified `tools/game_refactoring/scripts/run_operator_pipeline_batch.py`
  - added batch-level playwright port pool flags
  - acquires a leased port before each worker launch
  - passes `--playwright-port` into per-game workers
  - releases the lease when the worker finishes
- Modified `tools/game_refactoring/scripts/run_operator_pipeline_game.py`
  - added `--playwright-port`
  - persists assigned port + validation root URL into run/game/stage/result metadata
  - injects a `Validation Runtime Contract` block into the operator prompt header
- Updated the most urgent conflicting prompts:
  - `tools/game_refactoring/prompts/operators_v2/01_specimen_runtime_qa.md`
  - `tools/game_refactoring/prompts/operators_v2/02_specimen_runtime_qa.md`
  - `tools/game_refactoring/prompts/operators_v2/03_specimen_playwright_fix.md`
  - `tools/game_refactoring/prompts/operators_v2/05_creative_remix_v1_visual_judge.md`

**Why:**
The earlier concurrency bug analysis strongly suggested that browser-grounded workers were still free to improvise localhost ports and therefore could attach to the wrong local server or generate screenshot evidence from the wrong runtime. The first goal here was to create an explicit runtime contract and begin enforcing exclusive assigned-port behavior end-to-end.

**Key Technical Decisions:**
- Did **not** overload `#PROMPT#`; instead added a dedicated `Validation Runtime Contract` header block.
- Kept the lease state inside the run tree via a shared `_shared/port_leases.json` path.
- Used passive cleanup on acquisition rather than full destructive pool reclaims.
- Preserved backward compatibility for non-browser nodes by allowing `--playwright-port` to remain optional.
- Kept the pool size / TTL easily configurable because the schedulers expose them as CLI flags.

**Validation:**
- Ran Python syntax compilation for:
  - `tools/game_refactoring/scripts/port_lease_service.py`
  - `tools/game_refactoring/scripts/run_operator_pipeline_batch.py`
  - `tools/game_refactoring/scripts/run_operator_pipeline_game.py`

**Remaining Follow-Up:**
- Run an end-to-end batch smoke test to verify lease acquire/release behavior in live worker launches.
- Continue evaluating whether lease refresh should be added for very long-running workers.

**Follow-Up Intent:**
- Fix Playwright behavior in the next pass after this checkpoint commit, using the restored workflow launch path as the new baseline for observation and debugging.

**Status:** In Progress

---

### 2026-05-08 18:21 - Legacy extracted batch path aligned with deterministic port contract

**Achievement:**
Extended the deterministic/exclusive port refactor into the legacy extracted remixer batch path for consistency and future safety.

**Implementation Details:**
- Modified `tools/game_refactoring/scripts/run_parallel_batch.py`
  - added the same leased-port CLI flags used by the operator-pipeline scheduler
  - acquires a leased port before each `run_single_game.py` worker launch
  - passes `--playwright-port` to the worker
  - releases the lease on worker completion
- Modified `tools/game_refactoring/scripts/run_single_game.py`
  - added `--playwright-port`
  - injects a `Validation Runtime Contract` block into the legacy in-place remix prompt
  - persists assigned port / validation URL into job, result, game, invocation, and run metadata

**Why:**
Even though `run_parallel_batch.py` targets the older extracted remixer flow rather than the newer operator-pipeline browser stages, aligning both paths reduces future divergence and makes browser/runtime isolation rules consistent across the tool.

**Validation:**
- Verified Python syntax compilation for:
  - `tools/game_refactoring/scripts/run_parallel_batch.py`
  - `tools/game_refactoring/scripts/run_single_game.py`

**Current State:**
- operator-pipeline batch path: leased-port aware
- legacy extracted batch path: leased-port aware
- prompt/runtime contract rollout: applied to both browser-heavy operator prompts and the legacy extracted single-game prompt

**Remaining Follow-Up:**
- Run a real concurrent smoke test to validate unique lease assignment and release behavior under load.

**Status:** In Progress

---

### 2026-05-08 18:28 - Disposable four-game lane-collision experiment scaffold

**Achievement:**
Created a disposable/retryable experiment scaffold for observing whether browser/runtime lanes collide over time when four different `creative_remix_v3` jobs are launched one minute apart against random games from `games/top100_vatsal`.

**Implementation Details:**
- Created:
  - `tmp/game_refactoring_experiments/scripts/setup_four_game_lane_collision_experiment.py`
- The setup script:
  - randomly samples 4 games from `games/top100_vatsal`
  - binds them to these primary prompts:
    - `rick and morty`
    - `harry potter`
    - `my mom is a meme`
    - `demon hunters anime`
  - keeps these as alternates for future reruns:
    - `flappy bird`
    - `harry  potter vibe with flappy birds gamepelay`
  - writes one-game manifests, prompt text files, a machine-readable experiment plan, a staggered launch shell script, and a single-job retry helper under:
    - `tmp/game_refactoring_experiments/experiments/four_game_lane_collision/`
- Generated scaffold artifacts:
  - `tmp/game_refactoring_experiments/experiments/four_game_lane_collision/metadata/experiment_plan.json`
  - `tmp/game_refactoring_experiments/experiments/four_game_lane_collision/launch_staggered.sh`
  - `tmp/game_refactoring_experiments/experiments/four_game_lane_collision/retry_single_job.py`
  - per-job manifests under `manifests/`
  - per-job prompt files under `prompts/`
  - per-job launch logs under `logs/`
- The generated launch commands target:
  - `tools/game_refactoring/scripts/creative_refactor_cli.py`
  - `start-batch`
  - `--pipeline v2`
  - `--source-mode inplace`
  - `--max-concurrency 1`
  - `--runs-root /Volumes/backup/output/remixed`

**Generated Sample Selection:**
- `job_01`
  - prompt: `rick and morty`
  - game: `gamezone-0f3dc736-8159-48cf-93d0-bd78a54b8cd0`
  - run_id: `run_lane_collision_20260509T002856Z_job_01_rick-and-morty`
- `job_02`
  - prompt: `harry potter`
  - game: `gamezone-27ce7533-9ca8-46f9-96b6-2463b3441495`
  - run_id: `run_lane_collision_20260509T002856Z_job_02_harry-potter`
- `job_03`
  - prompt: `my mom is a meme`
  - game: `gamezone-021fa461-bb56-4b35-ab57-25d8b29813e1`
  - run_id: `run_lane_collision_20260509T002856Z_job_03_my-mom-is-a-meme`
- `job_04`
  - prompt: `demon hunters anime`
  - game: `gamezone-2b68136d-91f0-43a1-992b-4cef879ef733`
  - run_id: `run_lane_collision_20260509T002856Z_job_04_demon-hunters-anime`

**Why:**
The immediate goal is not just to run another batch, but to make the concurrency observation loop easy to retry after partial failure. Disposable scaffolding keeps the selection, prompts, launch order, and retry commands explicit so we can reproduce the same experiment shape while inspecting whether assigned validation lanes drift or collide over time.

**Validation:**
- Verified syntax compilation for:
  - `tmp/game_refactoring_experiments/scripts/setup_four_game_lane_collision_experiment.py`
- Executed the setup script with `--force` to generate the full experiment scaffold and capture the selected games / run ids.

**Next Operational Step:**
Launch the generated staggered runner and then inspect each run’s assigned validation port metadata versus any browser-grounded evidence during execution.

**Regression Follow-Up:**
- The first disposable experiment scaffold accidentally launched `creative_refactor_cli.py start-batch` directly in order to pass the newly added leased-port flags.
- That bypassed the prior `game_workflow.py` launch shape that had been used to select the intended workflow identity.
- Fixed the regression by:
  - adding leased-port override flags to `tools/game_refactoring/scripts/creative_refactor_cli.py`
  - adding the same leased-port override flags to `tools/game_refactoring/scripts/game_workflow.py`
  - restoring `tmp/game_refactoring_experiments/scripts/setup_four_game_lane_collision_experiment.py` to launch through `game_workflow.py` again
- This preserves the pre-refactor entrypoint shape while still allowing the deterministic port settings to be forwarded end to end.

**Validation:**
- Ran Python syntax compilation for:
  - `tools/game_refactoring/scripts/creative_refactor_cli.py`
  - `tools/game_refactoring/scripts/game_workflow.py`
  - `tmp/game_refactoring_experiments/scripts/setup_four_game_lane_collision_experiment.py`

**Single-Batch Retry Setup:**
- Created:
  - `tmp/game_refactoring_experiments/fixtures/top100_vatsal_rick_and_morty_random4_manifest.json`
- Selected the same 4 random games used by the earlier seed-driven experiment:
  - `gamezone-0f3dc736-8159-48cf-93d0-bd78a54b8cd0`
  - `gamezone-27ce7533-9ca8-46f9-96b6-2463b3441495`
  - `gamezone-021fa461-bb56-4b35-ab57-25d8b29813e1`
  - `gamezone-2b68136d-91f0-43a1-992b-4cef879ef733`
- Relaunched as a single `creative_remix_v3` workflow run with:
  - remix prompt: `rick and morty`
  - source mode: `inplace`
  - runs root: `/Volumes/backup/output/remixed`
  - max concurrency: `1`
- New run metadata:
  - `run_id`: `run_game_remixer_20260509T004747Z`
  - `run_dir`: `/Volumes/backup/output/remixed/run_game_remixer_20260509T004747Z`
  - `workflow_manifest_path`: `/Users/hassan/repos/game_agent/tools/game_refactoring/runs/_workflow_manifests/creative_remix_v3__top100_vatsal_rick_and_morty_random4_manifest.json`

**Status:** In Progress
