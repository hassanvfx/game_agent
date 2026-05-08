# Game Obfuscator - Orchestration Handoff

**Last Updated:** 2026-04-26  
**Current Milestone:** Resumable watchdog-friendly orchestration  
**Status:** Single-game transformation is validated; multi-game orchestration is not yet robust  
**Summary:** The moderate separate-file obfuscation pipeline is now the trusted baseline for one game, but batch execution must be reworked into a per-game, state-driven launcher before broad runs or parallelism are attempted.

---

## 1. Project Objective

Build a **resumable, observable, manifest-driven game obfuscation system** that can safely process many remixed games and produce per-game output packages that remain playable after transformation.

Target end state per game:

- one published `output/<game_id>/index.html`
- one minimal asset set, including only needed emoji assets
- preserved runtime correctness after transformation
- persistent artifacts and state at every meaningful stage
- safe resume behavior after interruption or failure
- future readiness for parallel worker execution

This project should continue to borrow from the sibling `game_remixer` architecture where it helps, but `game_obfuscator` now needs a stricter orchestration model because its per-game work is heavier, slower, and more failure-prone.

---

## 2. Current Validated Path

The currently validated path is the **one-pass moderate separate-file obfuscation flow** running on a **single game**.

Validated run and sample:

- **Run:** `runs/run_game_obfuscator_20260426T172834Z/`
- **Sample game:** `4d55e825-8749-412c-92a6-0a0bf4178ac9`

Representative output:

- `runs/run_game_obfuscator_20260426T172834Z/output/4d55e825-8749-412c-92a6-0a0bf4178ac9/index.html`

Representative artifacts:

- `artifacts/pre_bundle_site/index.html`
- `artifacts/separate_obfuscation_report.json`
- `artifacts/verification.json`
- `artifacts/separate_obfuscation/verification.json`

What this validated path proves:

- one-pass moderate separate-file obfuscation works on a single game
- external JS can be obfuscated safely enough for the validated sample
- inline executable JS extraction into generated files works
- inline CSS extraction into generated files works
- relative CSS `url(...)` path normalization works after extraction
- final published HTML minify works
- Playwright/browser verification passes on the validated sample
- non-executable inline script blocks can be skipped intentionally and recorded in reports

This is the most important current truth: **the single-game transformation path is no longer the main blocker**.

---

## 3. Architecture That Is Working

The following architecture is already useful and should be retained:

### A. Manifest-driven run structure
The project already uses a manifest-driven run model with timestamped runs and per-game folders.

### B. Stage-oriented pipeline
The pipeline is broken into meaningful stages and scripts:

- `scripts/create_run.py`
- `scripts/prepare_inputs.py`
- `scripts/analyze_inputs.py`
- `scripts/plan_rewrites.py`
- `scripts/apply_rewrites.py`
- `scripts/bundle_outputs.py`
- `scripts/verify_outputs.py`
- `scripts/obfuscate_separate_outputs.py`

These stage boundaries are useful and should remain conceptually intact.

### C. Folderized outputs and artifacts
Per-game output and artifact separation is the correct direction. It supports observability, postmortem inspection, and future worker isolation.

### D. Moderate separate-file path as baseline
The earlier strongest-first framing is no longer the trusted baseline. The validated baseline is now:

- moderate separate-file transformation
- externalization of inline executable JS/CSS
- conservative handling of suspicious inline script blocks
- verification-backed publishing

### E. Verification-backed confidence
The system now has a known-good single-game path with verification evidence. That means future work should build on it rather than reopening already solved transformation questions first.

---

## 4. Architecture That Is Failing

The failing area is **multi-game orchestration**, not the validated single-game transformation path.

Known bad/stalled run:

- `runs/run_game_obfuscator_20260426T192504Z`

Known bad behavior:

- a 5-game random batch was launched
- only the first game completed
- the batch stalled after the first report/output success
- this means broad batch launch is not safe yet

Current interpretation:

- per-game obfuscation appears functionally viable
- batch orchestration is not robust enough to trust
- a run can appear active while making no real progress
- current state persistence does not yet provide enough clarity to diagnose or recover cleanly

This is the active blocker for the project.

---

## 5. Why the Direction Changed

The project direction has shifted for deliberate reasons.

### Previous framing that is now outdated
Older handoff language emphasized:

- strongest-first obfuscation selection logic
- dashboard as the next primary milestone
- general hardening around earlier verification failures

That framing is now stale.

### Current strategic reality
The stronger insight is now:

- the simplified moderate separate-file path is the working baseline
- the remaining risk is not “can one game be transformed?”
- the remaining risk is “can many games be orchestrated safely and observably?”

### Implication
The next milestone is **not** “make obfuscation stronger first.”

The next milestone is:

**Convert the working single-game pipeline into a resumable, watchdog-friendly, per-game orchestration launcher that can safely scale to multi-game batches and future parallel execution.**

---

## 6. Next Milestone

## Milestone: Resumable Watchdog-Friendly Orchestration Launcher

This milestone should introduce a proper launcher/worker mental model.

### Required outcomes

- explicit per-game work units
- explicit per-game lifecycle state transitions
- immediate state/report flush after every meaningful step
- heartbeat/progress timestamps
- stalled detection
- resumable incomplete-run handling
- safe sequencing across many games
- structure ready for later parallel workers
- dashboard derived from authoritative state, not used as a substitute for it

### Per-game lifecycle expectation
Each game should behave like an independent job with:

- `pending`
- `running`
- `succeeded`
- `failed`
- `stalled`

and stage-level progress such as:

- `created`
- `input_prepared`
- `analyzed`
- `rewrites_planned`
- `rewrites_applied`
- `bundled`
- `obfuscated`
- `verified`

### Launcher expectation
The launcher should:

- select pending work
- launch a game job
- observe progress while it runs
- persist run-level status updates
- continue other games when one game fails or stalls
- support restart/resume without rerunning completed games unnecessarily

---

## 7. Borrowed Patterns From `game_remixer`

The sibling `game_remixer` project should absolutely be used as reference material.

### Borrow directly
Use `game_remixer` for ideas around:

- manifest-driven run creation
- timestamped run layout
- `run_state.json`
- `games/<game_id>/game_state.json`
- mirrored inputs
- resumable phase/state conventions
- dashboard generation patterns
- quick-access “open latest dashboard” workflow

### Extend for `game_obfuscator`
Do **not** copy the sibling architecture blindly.

`game_obfuscator` needs stronger operational state because each game may:

- spend longer in heavy transformation stages
- invoke obfuscation/minification tools
- require browser verification
- hang in a way that is not obvious from coarse state alone

So `game_obfuscator` should extend the sibling pattern with:

- `heartbeat_at`
- `last_progress_at`
- `attempt_count`
- stalled classification
- clearer launcher ownership
- stricter per-game isolation
- parallel-safe write discipline

---

## 8. Dashboard Positioning

Dashboard work is still valuable, but it is no longer the primary architectural milestone by itself.

The right relationship is:

### Source of truth
- `run_state.json`
- `games/<game_id>/game_state.json`
- per-game reports and artifacts

### Dashboard role
A dashboard should be a **read-only summary layer** over authoritative state.

It should show:

- run status
- total game counts by status
- current phase per game
- heartbeat/progress freshness
- verification result
- links to outputs and reports
- obvious stalled vs running distinction

The sibling `game_remixer` dashboard logic and latest-dashboard access pattern are worth borrowing, but only after the underlying state model is trustworthy.

---

## 9. Done Definition for This Milestone

This milestone should be considered complete when:

- a run can process many games safely
- each game writes progress/state continuously
- each game flushes artifacts and state after meaningful stage changes
- a stalled game is detectable from disk state
- launcher state shows whether the run is healthy, failed, or stalled
- rerunning the launcher can resume incomplete work
- one bad game does not permanently block progress for all other games
- sequential orchestration is stable enough that future parallel execution is realistic
- dashboard rendering and “open latest dashboard” can summarize this authoritative state cleanly

This milestone is **not** complete merely because:

- the dashboard looks polished
- one game passes
- stronger obfuscation exists
- parallelism has been attempted experimentally

---

## 10. Suggested Implementation Order

Recommended order for the next implementation agent:

1. Create a clear single-game worker abstraction around the validated path.
2. Make every stage write `game_state.json` before and after execution.
3. Add `heartbeat_at`, `last_progress_at`, `updated_at`, and `attempt_count`.
4. Recompute `run_state.json` from per-game states instead of relying on fragile in-memory assumptions.
5. Implement a sequential launcher that safely processes all pending games.
6. Add stalled detection and classify stale running jobs.
7. Add resume logic for interrupted/stalled/incomplete runs.
8. Generate dashboard output from those authoritative state files.
9. Add or adapt an `open_latest_dashboard` helper.
10. Only then evaluate safe parallel worker expansion.

---

## 11. What the Next Agent Should Not Do First

Do **not** begin the next session by:

- increasing obfuscation strength
- reviving strongest-first experimentation
- polishing dashboard UX before state is trustworthy
- adding parallel workers before sequential orchestration is reliable

The correct next focus is orchestration reliability.

---

## 12. Handoff Instruction

Treat the project as having crossed an architectural boundary:

- **Transformation core:** validated enough to proceed
- **Orchestration shell:** active blocker

The next engineering task is to harden orchestration, not to re-prove single-game transformation.