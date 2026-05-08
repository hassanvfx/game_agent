# Game Obfuscator - Orchestration Debug Handoff

**Last Updated:** 2026-04-26  
**Purpose:** Local execution/debug handoff for the next engineer or agent working on batch orchestration reliability.

---

## 1. Task Framing

Treat the next implementation task as:

**Convert the current working single-game obfuscation pipeline into a resumable, watchdog-friendly, per-game orchestrated launcher that can safely scale to multi-game batches and future parallel execution.**

This is no longer primarily an obfuscation-strength problem. It is an orchestration and operational-state problem.

---

## 2. Known-Good Validated Path

The known-good path is the simplified moderate separate-file flow on a single game.

Validated run:

- `runs/run_game_obfuscator_20260426T172834Z/`

Validated game:

- `4d55e825-8749-412c-92a6-0a0bf4178ac9`

Representative published output:

- `runs/run_game_obfuscator_20260426T172834Z/output/4d55e825-8749-412c-92a6-0a0bf4178ac9/index.html`

Representative artifacts:

- `runs/run_game_obfuscator_20260426T172834Z/games/4d55e825-8749-412c-92a6-0a0bf4178ac9/artifacts/pre_bundle_site/index.html`
- `runs/run_game_obfuscator_20260426T172834Z/games/4d55e825-8749-412c-92a6-0a0bf4178ac9/artifacts/separate_obfuscation_report.json`
- `runs/run_game_obfuscator_20260426T172834Z/games/4d55e825-8749-412c-92a6-0a0bf4178ac9/artifacts/verification.json`
- `runs/run_game_obfuscator_20260426T172834Z/games/4d55e825-8749-412c-92a6-0a0bf4178ac9/artifacts/separate_obfuscation/verification.json`

What is already proven here:

- inline executable JS extraction works
- inline CSS extraction works
- relative CSS path normalization works after extraction
- final HTML minify/publish works
- Playwright verification passes
- report generation is sufficient for one successful game

This validated path should be preserved as the worker baseline.

---

## 3. Known-Bad / Stalled Batch Run

Known stalled run:

- `runs/run_game_obfuscator_20260426T192504Z`

Batch type:

- 5-game random batch

Observed behavior:

- only the first game completed
- the batch stalled after the first report/output success
- broad multi-game launch is therefore not trusted yet

Root interpretation:

- single-game transformation is functional
- multi-game orchestration is not robust
- current run/game state handling is not strong enough to make the stall obvious or recoverable

This is the primary active bottleneck.

---

## 4. Files To Focus On

Primary scripts involved in the current pipeline and likely orchestration refactor:

- `scripts/obfuscate_separate_outputs.py`
- `scripts/create_run.py`
- `scripts/prepare_inputs.py`
- `scripts/analyze_inputs.py`
- `scripts/plan_rewrites.py`
- `scripts/apply_rewrites.py`
- `scripts/bundle_outputs.py`
- `scripts/verify_outputs.py`

Likely supporting files to revisit soon after state hardening:

- `scripts/build_dashboard.py`
- `scripts/open_latest_dashboard.sh`
- sibling `game_remixer` orchestration/dashboard files for reference patterns

---

## 5. Current Bottleneck Statement

The pipeline should no longer be treated as blocked by per-game transformation correctness.

The active bottleneck is:

- no clearly isolated per-game work unit
- no robust launcher/worker separation
- insufficient immediate state/report flushing
- insufficient heartbeat/progress tracking
- insufficient stalled detection
- insufficient resumable control flow for incomplete runs

The system currently appears too monolithic at batch level.

That makes it vulnerable to a run that:
- processes one game successfully
- stops making progress afterward
- leaves weak evidence about where scheduling or execution actually failed

---

## 6. Likely Root-Cause Areas

These are the most likely places to investigate first.

### A. Monolithic batch control flow
If one script is both:
- iterating games
- running transformations
- writing state
- writing reports
- handling verification
- handling exceptions

then one bad branch can stall the whole batch.

### B. Missing per-stage state persistence
If `game_state.json` is only updated at coarse boundaries, the last useful progress point may be lost.

### C. Missing immediate flush/atomic writes
A report or state update may exist in memory but not yet be safely persisted when a hang occurs.

### D. No explicit heartbeat / progress freshness
A game may remain marked `running` forever without any signal that progress has stopped.

### E. Run-level aggregation too implicit
If run-level status is driven by in-memory assumptions rather than recomputation from per-game states, it can become misleading.

### F. Verification or subprocess boundary hangs
One of the later stages may be hanging without changing game state often enough to expose the problem.

---

## 7. Required Next Design

The next design should introduce a real launcher/worker orchestration model.

### A. Per-game work unit
Create an explicit unit of work concept:

- one game
- one lifecycle owner
- one state file
- one artifact directory
- one output directory
- one attempt record

Conceptually:

```text
run_game_job(run_dir, game_id)
```

### B. Per-game state transitions
Each game should move through explicit state transitions such as:

- `pending`
- `running`
- `succeeded`
- `failed`
- `stalled`

and phases such as:

- `created`
- `input_prepared`
- `analyzed`
- `rewrites_planned`
- `rewrites_applied`
- `bundled`
- `obfuscated`
- `verified`

### C. Immediate report flush
After every meaningful stage:

- write state immediately
- write/flush report immediately
- update timestamps immediately

Never wait until the end of a batch to make progress visible.

### D. Run/game timestamps
At minimum add and maintain:

- `started_at`
- `updated_at`
- `completed_at`
- `heartbeat_at`
- `last_progress_at`

### E. Last-error capture
On any failure path, persist:

- current phase
- error summary
- traceback or error detail path
- attempt count

### F. Resumable scheduling
On launcher start:

- skip succeeded games
- pick up pending games
- inspect running games for stale heartbeat
- classify stale running games as stalled
- support retrying or resuming incomplete work safely

### G. Eventual parallel-safe boundaries
Before enabling any concurrency, enforce:

- each worker writes only to its own game-local output/artifact/state paths
- no unsafe shared mutable writes
- run-level summary is recomputed from per-game state rather than appended opportunistically

---

## 8. Recommended Implementation Strategy

### Step 1 - Preserve the validated single-game worker path
Do not replace the working path with a new experimental flow. Wrap it.

### Step 2 - Separate launcher from worker
Even if still sequential, create:
- launcher logic
- one-game worker logic

### Step 3 - Make stages callable per game
Short-term acceptable approach:
- launcher invokes existing stage scripts per game and updates state around them

Longer-term preferred approach:
- expose importable per-game functions from the stage scripts

### Step 4 - Recompute run status from game states
`run_state.json` should become an aggregate view, not the only operational truth.

### Step 5 - Add watchdog-style stalled detection
Minimal useful rule:
- if a game is `running`
- and `heartbeat_at` or `last_progress_at` is stale beyond threshold
- mark it `stalled`

### Step 6 - Build dashboard from authoritative state
After state is trustworthy:
- render run summary
- render per-game status/phase
- show stalled freshness clearly
- add artifact/output links
- borrow sibling latest-dashboard access pattern

---

## 9. Suggested State Model

### `run_state.json`
Recommended fields:

- `status`
- `current_phase`
- `total_games`
- `games_pending`
- `games_running`
- `games_succeeded`
- `games_failed`
- `games_stalled`
- `started_at`
- `updated_at`
- `completed_at`
- `resume_supported`
- `launcher_version`

Example status values:

- `created`
- `running`
- `completed`
- `completed_with_failures`
- `stalled`
- `failed`

### `games/<game_id>/game_state.json`
Recommended fields:

- `game_id`
- `status`
- `phase`
- `attempt_count`
- `started_at`
- `updated_at`
- `completed_at`
- `heartbeat_at`
- `last_progress_at`
- `source_path`
- `output_path`
- `artifact_dir`
- `worker_id` or `launcher_pid`
- `last_error`
- `report_paths`

---

## 10. Dashboard and Quick Access

Borrow from sibling `game_remixer`:

- dashboard generation pattern
- latest-run discovery
- open-latest-dashboard helper behavior

But do not make dashboard the source of truth.

The dashboard should summarize:

- run health
- per-game status
- phase
- heartbeat freshness
- verification result
- output paths
- report links
- stalled visibility

If the state layer is weak, the dashboard will only make failure prettier, not easier to fix.

---

## 11. Practical Success Definition

The next milestone is successful when:

- a many-game run can be launched safely
- each game writes progress continuously
- state on disk makes stalls obvious
- launcher can resume incomplete work
- one game stalling or failing does not hide progress on others
- dashboard/open-latest can expose this state cleanly
- only after that should future parallel workers be considered

---

## 12. Immediate Instruction To Next Agent

Do not spend the next session primarily tuning obfuscation strength.

Do not resurrect strongest-first experimentation yet.

Do not optimize dashboard polish before the state model is trustworthy.

Use the validated single-game path as the worker baseline and focus the next code changes on orchestration, heartbeat, flushing, resumability, and state-driven batch control.