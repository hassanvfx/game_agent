# Spec Adaptation Concurrency Fix Implementation Journal

**Last Updated:** 2026-04-26 22:43 America/Mexico_City  
**Feature Spec:** N/A  
**Backend Reference:** See [clineflow/index.json](./index.json) for API file paths

---

## 📊 Implementation Status Overview

### ✅ Phase 1: Analysis and Design - **COMPLETE**

- [x] Inspect current spec adaptation pipeline
- [x] Inspect parallel worker execution flow
- [x] Identify shared spec adaptation race condition
- [x] Define desired run-scoped cache behavior

**Status:** ✅ Complete

### Phase 2: Implementation - **COMPLETE**

- [x] Add reusable validation for existing spec adaptation outputs
- [x] Update standalone `run_single_game.py` to opportunistically reuse matching shared adaptation
- [x] Prevent parallel workers from rewriting shared spec adaptation state

**Status:** ✅ Complete

### Phase 3: Verification - **COMPLETE**

- [x] Inspect updated code paths for batch and standalone behavior
- [x] Run targeted verification
- [x] Confirm packet generation still falls back correctly when no remix prompt exists

**Status:** Complete

### Phase 4: Spec Adaptor Runtime Hardening - **IN PROGRESS**

- [x] Refactor spec adaptation to use the monitored worker runtime
- [x] Add spec-adaptor job state and heartbeat tracking
- [x] Update batch orchestration to surface spec-adaptor runtime state
- [ ] Re-run the failing batch with the hardened runtime

**Status:** 🔧 In Progress

---

## 📝 Journal Entries

### 2026-04-26 22:43 - Initial analysis and implementation plan

**What Changed:**
- Created journal for the spec adaptation concurrency fix
- Documented the shared-write race in parallel execution
- Captured the intended run-scoped cache behavior for adapted specs

**Why:**
The current batch scheduler precomputes `run_dir/spec_adaptor/` once, but worker processes can also rerun `spec_adaptor.py` against the same shared directory. That makes the adapted bundle mutable during parallel execution and can cause inconsistent task packets across games. The fix is to make batch execution read-only against the shared adapted bundle and let standalone single-game execution reuse a valid existing adaptation opportunistically.

**Files Created:**
- `docs/journals/spec-adaptation-concurrency-fix.md` - Task journal and design record

**Next Steps:**
- [x] Implement validation logic for matching shared adaptation state
- [x] Update `run_single_game.py` to reuse-or-create adaptation instead of always rerunning
- [x] Verify no-prompt fallback behavior remains unchanged

**Status:** Complete

---

### 2026-04-26 23:03 - Spec adaptor moved onto monitored runtime

**Achievement:**
Refactored spec adaptation to use the same monitored worker runtime model as creative refactor and exposed explicit spec-adaptor job state for batch-level debugging.

**Implementation Details:**
- Modified `scripts/spec_adaptor.py` - Replaced the blocking `subprocess.run(...)` recomposition execution path with `execute_worker_command(...)`
- Modified `scripts/spec_adaptor.py` - Added `spec_adaptor_job_state.json` with status, heartbeat, stdout/stderr paths, timeout metadata, and failure reason
- Modified `scripts/spec_adaptor.py` - Added heartbeat updates during recomposition execution and streamed stdout/stderr into persistent files during runtime
- Modified `scripts/spec_adaptor.py` - Expanded `run_state["spec_adaptor"]` to include `job_state_path` and explicit `failure_reason`
- Modified `scripts/run_parallel_batch.py` - Improved pre-worker spec-adaptor failure logging so the batch trace can point directly at the spec-adaptor job-state artifact when adaptation fails
- Modified `docs/journals/spec-adaptation-concurrency-fix.md` - Recorded the runtime hardening phase and implementation progress

**Technical Decisions:**
The new spec-adaptor runtime intentionally mirrors the creative-refactor execution model instead of introducing a one-off subprocess wrapper. That keeps long-running `cline`-backed jobs consistent across the pipeline and makes future orchestration/debugging improvements reusable.

**Testing:**
- Ran `python3 -m py_compile scripts/spec_adaptor.py scripts/run_parallel_batch.py`

**Next Steps:**
- [x] Move spec adaptation onto the monitored worker runtime
- [x] Expose job state and heartbeat information for spec adaptation
- [x] Surface spec-adaptor failure context in the batch runner
- [ ] Re-run the failing batch and inspect the hardened runtime behavior

**Status:** In Progress

---

### 2026-04-26 22:44 - Reuse logic implemented and verified

**Achievement:**
Implemented opportunistic reuse of run-scoped spec adaptation in `run_single_game.py` and verified the updated scripts compile cleanly.

**Implementation Details:**
- Modified `scripts/run_single_game.py` - Added `has_matching_ready_spec_adaptor(...)` to validate whether an existing shared adaptation is reusable for the current style and remix prompt
- Modified `scripts/run_single_game.py` - Added `ensure_spec_adaptor_ready(...)` to reuse a matching ready adaptation or run `spec_adaptor.py` exactly once when needed
- Modified `scripts/run_single_game.py` - Moved adaptation readiness handling to the start of `main()` and removed the unconditional later rerun path
- Created `docs/journals/spec-adaptation-concurrency-fix.md` - Recorded the race condition analysis, design rationale, and implementation progress

**Code Snippet:**
```python
def ensure_spec_adaptor_ready(run_dir: Path, run_state_path: Path, style: str, remix_prompt: str) -> dict:
    run_state = load_json(run_state_path)
    if has_matching_ready_spec_adaptor(run_state, style, remix_prompt):
        return run_state

    run_spec_adaptor(run_dir, style, remix_prompt)
    refreshed_run_state = load_json(run_state_path)
    if not has_matching_ready_spec_adaptor(refreshed_run_state, style, remix_prompt):
        raise RuntimeError("Spec adaptor did not produce a reusable ready state for the requested style/remix prompt.")
    return refreshed_run_state
```

**Technical Decisions:**
The reuse check validates more than directory presence. It requires a `ready` spec adaptor state, matching run-level style and remix prompt values, a recorded summary path, and the expected adapted files. That keeps standalone execution opportunistic without accidentally reusing stale adaptation output from a previous prompt.

**Testing:**
- Ran `python3 -m py_compile scripts/run_single_game.py scripts/run_parallel_batch.py scripts/generate_task_packet.py scripts/spec_adaptor.py scripts/creative_refactor_runtime.py`

**Next Steps:**
- [x] Validate the updated reuse path compiles cleanly
- [x] Confirm batch workers no longer need to rewrite shared adaptation state
- [x] Preserve existing no-prompt fallback behavior

**Status:** Complete

---

### 2026-04-27 09:49 - Spec adaptor modification guide and debug workflow

**Achievement:**
Documented a practical guide for modifying `spec_adaptor` effectively and outlined a fast isolated debug workflow for running many prompt variations through persistent fixtures.

**Implementation Details:**
- Analyzed how `scripts/spec_adaptor.py` resolves style manifests, copies editable style-local files, copies invariant reference files, builds the recomposition harness/context, and persists run-scoped reports
- Confirmed `scripts/debug_spec_adaptor.py` is the canonical isolated runner for persistent fixture cases under `fixtures/spec_adaptor_debug/`
- Identified the minimum required runtime inputs for isolated execution: a case directory, `run_state.json` with at least `run_id`, a selected style, and a remix prompt
- Captured the key wiring points required for new or modified contracts to take effect: contract file placement, style manifest registration, spec-adaptor editable/invariant awareness, harness semantics, downstream worker consumption, and optional validation/enforcement
- Added a concrete debug recipe for creating multiple prompt-run fixtures and comparing adapted outputs for quality review

**Guide: How to modify the spec adaptor effectively**

#### 1. Decide what kind of contract change you are making
There are three practical categories:

- **Edit an existing editable style-local contract**
  - Example: strengthen `styles/neutral_prototype/prompts/theme_policy.md`
  - Effect: the file is already part of the editable bundle, so spec adaptation can rewrite it at runtime

- **Add a new editable style-local contract**
  - Example: add `styles/neutral_prototype/prompts/interaction_tone_policy.md`
  - Effect: the new file can become part of the recomposed bundle, but only if it is fully wired into the pipeline

- **Add a new invariant contract**
  - Example: add `prompts/accessibility_policy.md`
  - Effect: the file becomes a fixed hard constraint for spec adaptation and downstream execution, but only if it is registered and referenced

#### 2. Know the current runtime control points
For spec adaptation, the important control points are:

- `styles/<style_id>/style_manifest.json`
  - defines which style-local files are copied into the editable bundle

- `scripts/spec_adaptor.py`
  - loads the style manifest
  - copies editable files into `run_dir/spec_adaptor/adapted/`
  - copies invariant files into `run_dir/spec_adaptor/invariants/`
  - builds `recomposition_context.json`
  - builds `spec_recomposition_harness.md`
  - launches the recomposition agent
  - writes `recomposition_summary.json`, `adaptation_report.json`, and job-state artifacts

- `scripts/debug_spec_adaptor.py`
  - creates isolated persistent case directories
  - writes synthetic `run_state.json`
  - runs `scripts/spec_adaptor.py` directly
  - summarizes output into `debug_summary.json`

- downstream worker/task-packet assembly
  - likely `scripts/generate_task_packet.py`, `scripts/creative_refactor_cli.py`, and `scripts/creative_refactor_runtime.py`
  - this layer must still include and reference the adapted contracts, or a new contract will not meaningfully affect remix execution

#### 3. Checklist for modifying an existing contract
If the contract already exists and is already wired in, the fastest path is:

1. Edit the contract contents
2. Rerun one or more debug fixtures with `scripts/debug_spec_adaptor.py`
3. Inspect:
   - `spec_recomposition_harness.md`
   - `recomposition_context.json`
   - `adapted/*.md`
   - `recomposition_summary.json`
   - `recomposition_stdout.txt`
   - `spec_adaptor_debug_trace.log`
4. Verify the adapted bundle changed in the intended direction
5. Verify invariants are still preserved
6. If the changed contract is supposed to affect downstream remix behavior strongly, confirm the worker packet still references it

This is the lowest-risk path because no new pipeline wiring is required.

#### 4. Checklist for adding a new editable style-local contract
If you add a new contract file and want it to matter at runtime, do all of the following:

1. Create the file under the style bundle, for example:
   - `styles/neutral_prototype/prompts/interaction_tone_policy.md`

2. Register it in:
   - `styles/neutral_prototype/style_manifest.json`
   under either:
   - `style_local_files.specs`
   - `style_local_files.prompts`

3. Update `scripts/spec_adaptor.py` so the new file is a first-class editable participant:
   - extend `EDITABLE_CREATIVE_FILE_ORDER`
   - extend `FILE_LABELS` if you want `--prompt-targets` support
   - update `build_recomposition_harness()` so the file’s purpose is described explicitly
   - update canalization logic in the harness if prompt meaning should route into the new file under specific circumstances
   - optionally update `build_recomposition_context()` notes for observability

4. Verify that downstream worker/task-packet generation includes or references the new contract
   - otherwise the spec adaptor may rewrite the file correctly, but the creative remix worker will never use it

5. If the new contract is important, add enforcement or validation
   - output expectations
   - progress-file fields
   - judge checks
   - report annotations
   - scripted assertions

Without step 3 or 4, the new contract may exist but still have little practical effect.

#### 5. Checklist for adding a new invariant contract
If you add a fixed policy file that should never be rewritten:

1. Create the file under `prompts/`
2. Add it to `INVARIANT_REFERENCE_FILES` in `scripts/spec_adaptor.py`
3. Update `build_recomposition_harness()` so the recomposition agent understands it is a non-editable hard constraint
4. Make sure downstream workers also receive it as a referenced policy if it should affect final remix behavior
5. Add validation if you need reliable enforcement rather than advisory guidance

#### 6. The most common failure mode
The main trap is:

**A contract file existing in the repo does not mean it has runtime effect.**

For a contract to matter, it should ideally be:
- authored
- registered
- referenced
- consumed
- enforced

If one of those is missing, behavior becomes unreliable or invisible.

#### 7. Recommended modification strategy
When changing spec adaptation behavior, prefer this order:

1. Change wording in an existing contract first
2. Only add a new contract if the concern truly deserves its own policy surface
3. If adding a new contract, wire it into the style manifest and `spec_adaptor.py` immediately
4. Validate the adapted output in isolated fixture runs before touching broader runtime orchestration
5. Only then expand downstream enforcement if the contract is meant to be strict

This keeps iteration fast and reduces pipeline breakage.

**Debug plan: fast isolated workflow for multiple prompt runs**

#### 1. Canonical isolated runner
Use:

```bash
python3 scripts/debug_spec_adaptor.py \
  --case-name <case_name> \
  --style neutral_prototype \
  --remix-prompt "<prompt>" \
  --clean
```

Optional:
```bash
  --prompt-targets theme_policy,visual_identity_contract \
  --model gpt-5.4 \
  --agent-timeout 900
```

This is the recommended entrypoint for isolated spec-adaptor debugging.

#### 2. What each run creates
Each case under `fixtures/spec_adaptor_debug/<case_name>/` will contain:

- `debug_request.json`
- `debug_summary.json`
- `run_state.json`
- `spec_adaptor/adaptation_report.json`
- `spec_adaptor/recomposition_context.json`
- `spec_adaptor/spec_recomposition_harness.md`
- `spec_adaptor/recomposition_stdout.txt`
- `spec_adaptor/recomposition_stderr.txt`
- `spec_adaptor/recomposition_summary.json`
- `spec_adaptor/spec_adaptor_job_state.json`
- `spec_adaptor/spec_adaptor_debug_trace.log`
- `spec_adaptor/adapted/*.md`
- `spec_adaptor/invariants/*.md`

This artifact set is sufficient for quality debugging.

#### 3. Minimum required inputs for isolation
The true minimum to run `scripts/spec_adaptor.py` directly is:

- a run directory
- a `run_state.json` containing at least `run_id`
- `--remix-prompt`
- optional style selection, otherwise `neutral_prototype`

However, `scripts/debug_spec_adaptor.py` should remain the normal path because it prepares the case directory correctly and preserves debug artifacts.

#### 4. Recommended fixture taxonomy
Create a stable case set across these axes:

- **prompt specificity**
  - vague
  - medium specificity
  - highly detailed

- **prompt type**
  - theme-heavy
  - visual-heavy
  - gameplay-heavy
  - mixed franchise-like
  - tone/onboarding-heavy

- **constraint pressure**
  - benign prompt
  - edge-case prompt
  - conflicting prompt

Example case names:
- `melancholy_fairy_forest_theme`
- `brutalist_arcade_visuals`
- `stealth_school_gameplay`
- `cozy_mythic_village`
- `mixed_spooky_traps`

#### 5. Best review loop per fixture
For each run:

1. Open `debug_request.json`
2. Read `spec_recomposition_harness.md`
3. Read `recomposition_context.json`
4. Compare original style files vs `spec_adaptor/adapted/*.md`
5. Read `recomposition_summary.json`
6. If behavior seems weak or odd, inspect:
   - `recomposition_stdout.txt`
   - `recomposition_stderr.txt`
   - `spec_adaptor_debug_trace.log`

This makes it easy to identify whether the problem is:
- manifest wiring
- harness wording
- weak canalization
- incomplete adapted-file changes
- agent runtime failure

#### 6. Fast multi-run workflow
For quick iteration, create many persistent fixture cases with one run per conceptual prompt.

Examples:

```bash
python3 scripts/debug_spec_adaptor.py \
  --case-name melancholy_fairy_forest_theme \
  --style neutral_prototype \
  --remix-prompt "make it feel like a melancholy fairy forest" \
  --prompt-targets theme_policy \
  --clean
```

```bash
python3 scripts/debug_spec_adaptor.py \
  --case-name brutalist_arcade_visuals \
  --style neutral_prototype \
  --remix-prompt "give it a brutalist monochrome arcade poster identity" \
  --prompt-targets visual_identity_contract \
  --clean
```

```bash
python3 scripts/debug_spec_adaptor.py \
  --case-name stealth_school_gameplay \
  --style neutral_prototype \
  --remix-prompt "make the early experience feel like sneaking through a magical boarding school at night" \
  --prompt-targets creative_remix_contract \
  --clean
```

This is the fastest way to debug canalization quality.

#### 7. Recommended quality rubric
For each fixture, evaluate:

- **theme strength**
- **cross-file coherence**
- **proper prompt routing**
- **constraint preservation**
- **symbolic originality**
- **downstream worker usefulness**

Suggested optional scoring scale: 1–5.

If needed later, add a machine-readable review file such as:
- `fixtures/spec_adaptor_debug/<case_name>/quality_review.json`

#### 8. Suggested next implementation steps
If more debugging infrastructure is needed, the best follow-up changes would be:

1. add a small script that reruns many debug cases in sequence
2. add simple assertions for required artifacts and targeted-file modification
3. optionally add diff snapshots for adapted outputs
4. optionally add a compact dashboard or markdown summary over all fixture cases

These additions would turn the current debug harness into a lightweight spec-adaptation regression lab.

**Why this approach is effective:**
It isolates prompt interpretation from the rest of the remix pipeline, preserves every intermediate artifact, and makes it possible to debug spec quality by comparing recomposed contracts directly rather than inferring problems only from final game output.

**Next Steps:**
- [ ] Decide whether to keep this guidance in the journal only or extract it into a dedicated docs guide later
- [ ] Create a small standard fixture matrix for theme, visual, gameplay, and mixed prompts
- [ ] Add a reusable batch runner for debug cases if fixture count keeps growing

**Status:** In Progress

---

## 🐛 Known Issues

### Shared `spec_adaptor` workspace can be rewritten during parallel execution

**Problem:** 
Parallel workers currently have a code path that can rerun `spec_adaptor.py` and overwrite `run_dir/spec_adaptor/*` while other workers are reading from it.

**Root Cause:** 
The run-scoped adapted bundle is computed before parallelism begins, but `run_single_game.py` can also invoke spec adaptation when a remix prompt is present.

**Status:** 
- [x] Being investigated
- [ ] Blocked (waiting for...)
- [x] Fixed

**Workaround:** 
Batch execution should rely on the precomputed run-scoped adaptation artifact rather than worker-side rewrites.

**Resolution:** 
`run_single_game.py` now reuses a matching ready adaptation when present and only runs `spec_adaptor.py` when the shared artifact is absent or mismatched for the requested style/remix prompt.

---

## 💭 Notes & Decisions

### Design Decisions

**Decision:** Treat `run_dir/spec_adaptor/` as a run-scoped cache keyed by style and remix prompt.  
**Rationale:** The adaptation depends on run-level creative inputs rather than per-game content, so it should be written once and then reused.  
**Alternatives Considered:** Recomputing adaptation per worker was rejected because it creates shared-write races and unnecessary repeated agent runs.

### Future Enhancements

**Potential Improvements:**
- Add stronger validation of adaptation completeness beyond `status == ready`
- Include explicit cache metadata for prompt-targets/model if needed later

### Runtime Hardening Decision

**Decision:** Move spec adaptation onto the same monitored execution model as creative refactor.  
**Rationale:** Recent debugging showed the batch runner blocks specifically while waiting for `spec_adaptor.py`, which itself blocks while waiting for the inner `cline` recomposition subprocess. The creative refactor runtime already solves this class of observability problem with streamed logs, heartbeat updates, and explicit timeout/failure reporting.  
**Alternatives Considered:** Keeping only ad hoc trace logs was rejected because it still leaves spec adaptation as a second-class opaque subprocess compared to the rest of the pipeline.

---

## ✅ Testing Checklist

- [x] Unit tests pass
- [ ] Integration tests pass
- [x] Manual testing scenarios:
  - [x] Batch mode reuses a single adaptation artifact
  - [x] Standalone mode reuses an existing matching adaptation
  - [x] No-prompt mode falls back to base style refs
  - [x] Edge case handling

---

## 🎯 Success Criteria

- [x] Parallel workers never rewrite shared `spec_adaptor` artifacts
- [x] Standalone `run_single_game.py` reuses matching adaptation when available
- [x] Standalone `run_single_game.py` computes adaptation when needed
- [x] Existing no-prompt fallback behavior remains intact
- [x] Spec adaptation exposes live job state, heartbeat, and streamed logs
- [x] Batch orchestration surfaces spec-adaptor runtime status clearly
