# Formal Creative Refactor CLI Follow-Up Journal

**Last Updated:** 2026-04-26 17:05 America/Mexico_City  
**Feature Spec:** N/A  
**Backend Reference:** N/A

---

## 📊 Implementation Status Overview

### Phase 1: Context Consolidation - **COMPLETE**

- [x] Capture the global architecture context behind spec recomposition, packet generation, and downstream worker execution
- [x] Capture the local script-level context for `scripts/debug_creative_refactor.py` and `scripts/run_single_game.py`
- [x] Define what should remain a low-level execution engine versus what should become a user-facing CLI layer

**Status:** Complete

### Phase 2: CLI Surface Design - **IN PROGRESS**

- [x] Define the formal command shape for a future creative-refactor CLI
- [x] Define stable inputs, defaults, and override semantics
- [x] Define output artifacts, status files, and observability expectations
- [x] Define how direct replay, pipeline replay, and future batch-facing commands relate to each other
- [ ] Redefine the scope from replay-oriented CLI toward manifest-driven batch orchestration CLI
- [ ] Define stable `start-batch`, `status`, and `result` contracts
- [ ] Define the canonical final-destination contract around `runs/<run_id>/output/`

**Status:** In Progress

### Phase 3: Shared Runtime Extraction - **COMPLETED**

- [x] Identify duplicated worker-execution logic between `scripts/debug_creative_refactor.py` and `scripts/run_single_game.py`
- [x] Extract a shared helper/module for worker launch, streaming capture, timeout handling, and final result materialization
- [x] Define what future heartbeat/state reporting should look like for both debug and formal CLI paths

**Status:** Completed

---

### 2026-04-26 23:30 - Async Batch Lifecycle Alignment

**What Changed:**
- Refactored `scripts/creative_refactor_cli.py` so `start-batch` now behaves as a true async acceptance command instead of blocking until `run_parallel_batch.py` exits
- Added detached launcher behavior for batch orchestration using `subprocess.Popen(..., start_new_session=True)` with run-local stdout/stderr capture
- Added run-local launcher observability artifacts:
  - `batch_launcher_invocation.json`
  - `batch_launcher_stdout.txt`
  - `batch_launcher_stderr.txt`
- Added `finish` as an alias for `result`
- Extended `status` payloads with lifecycle booleans:
  - `running`
  - `completed`
  - `failed`
- Updated `scripts/run_parallel_batch.py` so it can reuse a pre-created run when invoked with an existing `--run-id`
- Updated `README.md` to document the user-facing lifecycle as:
  - `start-batch`
  - `status`
  - `result` / `finish`

**Why:**
The previous CLI surface exposed lifecycle-oriented command names, but `start-batch` was still implemented with `subprocess.run(...)`, which blocked until the full manifest-driven batch completed. That meant the effective contract was synchronous even though the naming implied async orchestration.

This created two problems:
- the docs could not honestly describe a `start → status → finish` lifecycle
- agents and operators were encouraged to treat `status` and `result` as secondary helpers instead of the primary control loop

The refactor fixes the contract mismatch by making `start-batch` return immediately after run acceptance and detached launch.

**Implementation Details:**
- `start-batch` now:
  1. creates the run scaffold up front via `create_run.py`
  2. resolves the run identity before long-running work begins
  3. launches `run_parallel_batch.py` detached against that known `run_id`
  4. returns immediately with:
     - `run_id`
     - `run_dir`
     - `status_path`
     - `dashboard_path`
     - `output_root`
     - launcher `pid`
     - launcher artifact paths
- `run_parallel_batch.py` now detects when `--run-id` already points to an existing run directory and reuses it instead of trying to recreate the run
- `finish` was added as a semantic alias to `result` so the CLI can be described more naturally as:
  - start
  - status
  - finish
- `README.md` now presents the manifest-driven orchestration contract in lifecycle terms and keeps the lower-level direct batch runner documented separately as an implementation engine

**Success Criteria:**
- `start-batch` is non-blocking
- `status` is the authoritative source of truth for active vs terminal state
- `result` / `finish` resolve output locations without introducing new semantics
- launcher failures become inspectable through dedicated run-local artifacts

**Status:** Completed

### Phase 4: Implementation and Validation - **COMPLETED**

- [x] Build the formal CLI wrapper on top of the shared execution engine
- [x] Validate direct-attempt replay through the new CLI
- [x] Validate pipeline parity with the new CLI surface
- [x] Update top-level docs and usage examples

**Status:** Completed

---

## 📝 Journal Entries

### 2026-04-26 17:00 - Follow-Up Task Initialization

**What Changed:**
- Created a dedicated follow-up journal for turning the current parameterized replay tooling into a formal creative-refactor CLI
- Captured the necessary global context from the current architecture
- Captured the necessary local context from the current worker/debug scripts
- Defined the high-level implementation phases for the next task

**Why:**
The current debugging and recovery work produced a useful low-level replay tool:
- `scripts/debug_creative_refactor.py`

That tool is already parameterized enough to serve as the execution core for a future formal CLI. Rather than treating it as a temporary debugging script, the next task should formalize:
- its command surface,
- its stable input contract,
- its output artifact contract,
- its observability behavior,
- and its relationship to the main pipeline runner.

This journal creates a clean handoff target so the next session can build the CLI deliberately instead of rediscovering architecture context.

**Global Context:**
- The pipeline architecture has moved from deterministic Python-side prompt injection to an agent-authored spec recomposition workspace.
- Main flow now is:
  1. choose baseline style preset
  2. copy editable creative files into `spec_adaptor/adapted/`
  3. copy invariant files into `spec_adaptor/invariants/`
  4. write:
     - `user_remix_prompt.txt`
     - `spec_recomposition_harness.md`
     - `recomposition_context.json`
  5. run first-stage CLI recomposition agent
  6. feed adapted creative files into packet generation
  7. downstream creative worker edits the game
- Editable creative files are:
  - `creative_remix_contract.md`
  - `visual_identity_contract.md`
  - `theme_policy.md`
  - `creative_refactor_agent_template.md`
- Invariant files are:
  - `audio_policy.md`
  - `network_policy.md`
  - `system_contract.md`
  - `refactor_compliance_spec.md`

**Local Context:**
- `scripts/run_single_game.py`
  - owns the real downstream creative worker invocation in the pipeline
  - now streams stdout/stderr incrementally
  - kills the full worker process group on timeout
  - writes durable completion/timeout artifacts
  - now uses `--reasoning-effort high`
  - still owns heartbeat emission through `job_state.json`
- `scripts/debug_creative_refactor.py`
  - replays a prepared attempt directly from:
    - `creative_refactor_prompt.txt`
    - `creative_refactor_task_packet.json`
    - `creative_refactor_invocation.json`
  - currently exposes:
    - `--attempt-dir`
    - `--timeout`
    - `--model`
    - `--verbose`
    - `--json-output`
    - `--thinking`
    - `--reasoning-effort`
  - currently writes:
    - `direct_worker_invocation.json`
    - `direct_worker_stdout.txt`
    - `direct_worker_stderr.txt`
    - `direct_worker_result.json`
  - does not yet write a heartbeat/state file
- The direct replay and the real pipeline path have both now been validated successfully for the mixed prompt case when using:
  - realistic timeout (`900`)
  - high reasoning
  - improved observability flags

**Key Technical Decisions to Carry Forward:**
- The debug replay script should become the low-level engine for the future formal CLI, not be replaced by a separate implementation.
- Shared worker launch/stream/timeout logic should be extracted so:
  - `scripts/run_single_game.py`
  - future formal CLI
  - current debug replay script
  can all rely on one execution core.
- Timeout should remain a first-class terminal state.
- Streaming stdout/stderr capture and structured result artifacts are mandatory features, not optional debugging extras.
- A future formal CLI should preserve parity with the real pipeline configuration, especially around:
  - model
  - timeout
  - reasoning effort
  - observability flags

**Recommended Future CLI Shape:**
- Low-level replay mode:
  - replay an existing prepared attempt by `--attempt-dir`
- Higher-level pipeline-oriented mode:
  - accept run/game identifiers and resolve the attempt automatically
- Stable options should likely include:
  - `--attempt-dir`
  - `--run-dir`
  - `--game-id`
  - `--timeout`
  - `--model`
  - `--reasoning-effort`
  - `--thinking`
  - `--verbose`
  - `--json-output`
  - future `--heartbeat` / `--state-file`
- Stable output contract should include:
  - invocation record
  - stdout/stderr streams
  - result json
  - optional heartbeat/state json

**Next Steps:**
- [x] Inspect shared logic boundaries between `scripts/run_single_game.py` and `scripts/debug_creative_refactor.py`
- [x] Design the formal CLI surface and command modes
- [x] Define the shared worker-execution helper/module API
- [x] Decide whether heartbeat/state reporting belongs in the helper or only in wrapper layers
- [x] Implement the formal CLI tool in a future task

**Status:** Completed

---

### 2026-04-26 17:05 - Formal CLI Implementation

**What Changed:**
- Added `scripts/creative_refactor_runtime.py` as a shared execution/runtime helper for worker launch, stream capture, timeout handling, duration calculation, and JSON persistence
- Added `scripts/creative_refactor_cli.py` as the new formal CLI with:
  - `replay` mode for explicit attempt-dir execution
  - `pipeline` mode for resolving the latest or explicit attempt from `--run-dir` and `--game-id`
- Refactored `scripts/run_single_game.py` to use the shared runtime helper while preserving heartbeat updates through a wrapper-level callback
- Converted `scripts/debug_creative_refactor.py` into a thin compatibility wrapper that now delegates to the formal CLI
- Updated `README.md` with the new CLI entrypoint, modes, outputs, and compatibility wrapper usage

**Why:**
This formalized the low-level replay tooling into a stable entrypoint without duplicating the worker execution path in multiple scripts. The pipeline runner and the replay CLI now share one process-launch implementation, which reduces divergence risk and preserves the operational lessons from the debugging work.

**Implementation Details:**
- Shared runtime helper responsibilities now include:
  - streaming stdout/stderr to disk while the worker runs
  - killing the full worker process group on timeout
  - returning a normalized execution result object with status, timing, and byte counts
  - reusable JSON read/write helpers
- Heartbeat behavior remains wrapper-specific by design:
  - `run_single_game.py` passes a heartbeat callback so `job_state.json` continues to update during pipeline execution
  - replay CLI paths currently remain artifact-focused and do not emit a dedicated heartbeat/state file yet
- The new CLI emits the same durable replay artifacts used by the earlier debug tool:
  - `direct_worker_invocation.json`
  - `direct_worker_stdout.txt`
  - `direct_worker_stderr.txt`
  - `direct_worker_result.json`

**Validation:**
- Verified `python3 scripts/creative_refactor_cli.py --help`
- Verified `python3 scripts/creative_refactor_cli.py replay --help`
- Verified `python3 scripts/creative_refactor_cli.py pipeline --help`
- Verified `python3 scripts/debug_creative_refactor.py replay --help`
- Verified the newly added live batch test harness correctly fails fast when the manifest-driven batch commands do not yet exist:
  - `python3 scripts/test_creative_refactor_batch_cli_live.py --manifest fixtures/harry_potter_two_game_manifest.json --run-id cli_live_no_prompt_20260426 ...`
  - current failure reason:
    - missing `start-batch`
    - missing `status`
    - missing `result`

**Scope Correction:**
- This implementation successfully covered the low-level replay and pipeline-attempt CLI layer.
- It does **not** yet satisfy the broader manifest-driven orchestration CLI requested later.
- The next task should build on top of existing orchestration code in `scripts/run_parallel_batch.py` rather than replacing it.

**Open Follow-Up:**
- Decide whether the replay CLI should regain pre-subcommand compatibility for legacy invocations that omit `replay`
- Add an optional replay heartbeat/state artifact if parity with pipeline observability becomes necessary
- Extend the formal CLI upward into a batch orchestration surface with:
  - `start-batch`
  - `status`
  - `result`

**Status:** Completed

---

### 2026-04-26 17:12 - Batch Orchestration CLI Scope Clarification

**What Changed:**
- Reassessed the intended CLI scope after clarifying that the target tool should accept a manifest of games and run the full show, not just replay a single prepared attempt
- Inspected:
  - `scripts/creative_refactor_cli.py`
  - `scripts/creative_refactor_runtime.py`
  - `scripts/run_parallel_batch.py`
- Defined the correct contract for a higher-level manifest-driven batch CLI

**Why:**
The originally documented follow-up drifted toward the lower-level replay/debug surface. Your actual requirement is a higher-level orchestration CLI that:
- accepts a manifest file
- launches the full end-to-end run
- exposes a pollable status surface
- returns the final destination to inspect after completion

That is closer to a formal wrapper around `run_parallel_batch.py` and the run-state/dashboard/output model than to the lower-level replay commands.

**Findings:**
- `scripts/creative_refactor_cli.py`
  - currently covers replay-oriented use cases only
- `scripts/creative_refactor_runtime.py`
  - already provides the right shared worker-execution primitive for low-level launches
- `scripts/run_parallel_batch.py`
  - already contains most of the orchestration behavior needed for the formal batch CLI:
    - manifest input
    - create run
    - prepare inputs
    - optional spec adaptor
    - bounded parallel per-game execution
    - heartbeat monitoring
    - dashboard refresh
    - final run-state updates

**Correct Batch CLI Contract:**
- `start-batch`
  - inputs:
    - `--manifest`
    - optional `--run-id`
    - `--style`
    - `--remix-prompt` / `--remix-prompt-file`
    - `--model`
    - `--agent-timeout`
    - `--max-concurrency`
    - `--poll-seconds`
    - `--stale-heartbeat-seconds`
  - returns:
    - `run_id`
    - `run_dir`
    - `status_path`
    - `dashboard_path`
    - `output_root`
    - optionally launcher PID if detached
- `status`
  - inputs:
    - `--run-id` or `--run-dir`
  - returns:
    - `run_id`
    - `run_dir`
    - `status`
    - `current_phase`
    - `updated_at`
    - `games_total`
    - `games_transform_completed`
    - `games_transform_failed`
    - `dashboard_path`
    - `output_root`
    - `completed`
- `result`
  - inputs:
    - `--run-id` or `--run-dir`
  - returns:
    - `run_dir`
    - `dashboard_path`
    - `output_root`
    - `final_output_dirs`

**Final Destination Clarification:**
- There is not yet a separate publish/package artifact path in the current codebase.
- The truthful current final destination contract is:
  - run directory:
    - `runs/<run_id>/`
  - status file:
    - `runs/<run_id>/run_state.json`
  - dashboard:
    - `runs/<run_id>/dashboard/index.html`
  - output root:
    - `runs/<run_id>/output/`
  - final per-game destinations:
    - `runs/<run_id>/output/<game_id>/`

**Recommended Implementation Strategy:**
- Do not create a second orchestration engine.
- Extend `scripts/creative_refactor_cli.py` upward into a batch-facing CLI.
- Reuse or extract orchestration behavior from `scripts/run_parallel_batch.py`.
- Treat `run_state.json` as the canonical pollable state surface.

**Next Steps:**
- [x] Add `start-batch` to `scripts/creative_refactor_cli.py`
- [x] Add `status` to `scripts/creative_refactor_cli.py`
- [x] Add `result` to `scripts/creative_refactor_cli.py`
- [x] Reuse `run_parallel_batch.py` orchestration behind the new CLI rather than duplicating it
- [x] Document `runs/<run_id>/output/` as the current formal final destination contract
- [ ] Update `README.md` with manifest-driven batch CLI examples
- [x] Add a live batch CLI test harness that asserts the contract for `start-batch`, `status`, and `result`
- [x] Re-run the live test harness once the batch commands exist
- [ ] Add a prompt-aware live test invocation once the no-prompt batch case passes

**Live Validation Notes:**
- The no-prompt control live harness now progresses correctly against the new contract:
  - `start-batch` returns structured run metadata
  - `status` returns pollable JSON and reaches `transform_completed`
  - `result` returns the formal destination contract
- The `result` command was corrected so it only emits `final_output_dirs` after completion, preserving a cleaner terminal-state contract
- The prompt-aware live harness has been started and verified to:
  - create the run
  - wire `spec_adaptor`
  - expose live pollable status
  - keep downstream job heartbeats active while running
- Final prompt-aware terminal completion is still pending at the time of this journal entry

**Status:** In Progress

### 2026-04-29 16:40 - Prompt-Aware Known-State CLI Recheck

**What Changed:**
- Re-ran the known-good prompt-aware Harry Potter/flappy batch from the real `scripts/creative_refactor_cli.py` entrypoint before starting the operator pipeline v2 scaffold.
- Used the same successful input shape as historical run `cli_live_prompt_restart2_20260426`:
  - manifest: `fixtures/harry_potter_two_game_manifest.json`
  - style: `neutral_prototype`
  - remix prompt: `make it harry potter like with flappy bird gameplay`
  - two-game parallel execution
- Created new verification run:
  - `runs/cli_prompt_hp_known_state_20260429`

**Commands:**
```bash
python3 scripts/creative_refactor_cli.py --help
python3 scripts/creative_refactor_cli.py start-batch --help
python3 scripts/creative_refactor_cli.py status --help
python3 scripts/creative_refactor_cli.py result --help

python3 scripts/creative_refactor_cli.py --json start-batch \
  --manifest fixtures/harry_potter_two_game_manifest.json \
  --run-id cli_prompt_hp_known_state_20260429 \
  --style neutral_prototype \
  --remix-prompt "make it harry potter like with flappy bird gameplay" \
  --model gpt-5.4 \
  --agent-timeout 900 \
  --max-concurrency 2 \
  --poll-seconds 5 \
  --stale-heartbeat-seconds 900

python3 scripts/creative_refactor_cli.py --json status \
  --run-id cli_prompt_hp_known_state_20260429

python3 scripts/creative_refactor_cli.py --json result \
  --run-id cli_prompt_hp_known_state_20260429
```

**Verification:**
- CLI surface checks passed for:
  - `start-batch`
  - `status`
  - `result`
- `start-batch` returned the expected async launch payload with run paths and launcher artifact paths.
- Spec adaptor completed successfully:
  - `spec_adaptor.status: ready`
  - `recomposition_summary_present: true`
  - `remix_identity_present: true`
  - `failure_reason: null`
- Final CLI status reached:
  - `status: transform_completed`
  - `current_phase: parallel_batch_finished`
  - `games_total: 2`
  - `games_transform_completed: 2`
  - `games_transform_failed: 0`
- `creative_refactor_cli.py --json result` returned final output dirs:
  - `runs/cli_prompt_hp_known_state_20260429/output/08a032f7-6c39-461b-9cf1-03c117c12b6b`
  - `runs/cli_prompt_hp_known_state_20260429/output/25b14fff-43f9-452a-8820-54d8056bfe84`
- Both per-game `creative_refactor_result.json` files completed and changed `index.html`.

**Representative Worker Summaries:**
- `08a032f7-6c39-461b-9cf1-03c117c12b6b`: Refactored the trivia game into a moonlit academy courier trial with parchment HUD, lantern accents, and tower-sky opening identity.
- `25b14fff-43f9-452a-8820-54d8056bfe84`: Reframed the game into a moonlit academy courier trial with a parchment-and-brass HUD and broom-flight presentation.

**Technical Decision:**
This confirms the baseline production CLI path is healthy immediately before introducing the isolated v2 operator lab scaffold. The scaffold work can proceed from a known-good real `creative_refactor_cli.py` state rather than relying on a wrapper harness.

**Status:** Complete

---

## 📚 Quick Reference

### Relevant Existing Files

- `scripts/run_single_game.py`
  - real pipeline worker launch path
- `scripts/debug_creative_refactor.py`
  - direct replay/debug engine
- `scripts/generate_task_packet.py`
  - packet construction and adapted-ref activation
- `scripts/spec_adaptor.py`
  - creative bundle recomposition orchestration
- `scripts/run_sample_batch.py`
  - sequential batch orchestration and batch-level observability
- `docs/journals/style-preset-and-dynamic-spec-overhaul.md`
  - master architecture and validation journal

### Current Replay Tool Inputs

- `--attempt-dir`
- `--timeout`
- `--model`
- `--verbose`
- `--json-output`
- `--thinking`
- `--reasoning-effort`

### Current Replay Tool Outputs

- `direct_worker_invocation.json`
- `direct_worker_stdout.txt`
- `direct_worker_stderr.txt`
- `direct_worker_result.json`

### Proven Successful Runtime Pattern

- provider/model context aligned to:
  - `openai`
  - `gpt-5.4`
  - `reasoning_effort: high`
  - `stream: true`
- successful long-run replay settings:
  - timeout `900`
  - reasoning `high`
  - `--verbose`
  - `--json`
  - no explicit `--thinking` override required

---

## 💭 Notes & Decisions

### Design Principles for the Follow-Up

**Decision:** Treat `scripts/debug_creative_refactor.py` as the seed of a formal CLI, not as disposable debug-only code.  
**Rationale:** It already defines a useful parameterized execution boundary and artifact contract.

**Decision:** Extract shared execution logic before building a richer CLI wrapper.  
**Rationale:** This avoids divergence between debug behavior and pipeline behavior.

**Decision:** Preserve observability as a first-class capability.  
**Rationale:** The debugging effort showed that streaming output, structured result files, and timeout-aware finalization are essential operational features.

### Open Questions for the Next Task

- Should the formal CLI live as:
  - a new script like `scripts/creative_refactor_cli.py`
  - or a refactor/expansion of `scripts/debug_creative_refactor.py`?
- Should heartbeat/state reporting be:
  - always on
  - optional
  - or wrapper-specific?
- Should the formal CLI accept only prepared attempts first, or also synthesize/reconstruct attempts from run/game IDs?
- How much of the current direct replay artifact naming should become a stable public contract?

---

## ✅ Success Criteria

- [x] Follow-up journal captures enough global and local context for a fresh session
- [x] Future task can identify the low-level engine versus user-facing CLI boundary immediately
- [x] Future task can implement a formal creative-refactor CLI without rediscovering previous debugging decisions

---

*This journal records the follow-up task for formalizing the parameterized creative-refactor replay tooling into a future CLI interface.*