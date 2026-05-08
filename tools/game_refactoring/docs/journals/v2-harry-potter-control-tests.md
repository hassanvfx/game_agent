# V2 Harry Potter Control Tests Journal

**Last Updated:** 2026-04-30  
**Feature Spec:** `docs/operator_pipeline_manual.md`  
**Backend Reference:** See `clineflow/index.json` for API file paths

---

## 📊 Implementation Status Overview

### ✅ Phase 1: Baseline Verification - **Complete**

- [x] Identify the last successful v2 Harry Potter production smoke run
- [x] Verify baseline run artifacts still exist locally
- [x] Confirm baseline run status and completion counts
- [x] Confirm available historical extended-run artifacts

**Status:** ✅ Complete

### 🔧 Phase 2: Two-Game Control Test - **In Progress**

- [x] Start a fresh v2 control run using `fixtures/harry_potter_two_game_manifest.json`
- [x] Monitor initial run status and stage progression
- [ ] Validate final result contract and generated artifacts
- [ ] Confirm completion counts match the two-game baseline

**Status:** In Progress

### 🔧 Phase 3: Four-Game Extended Control Test - **In Progress**

- [x] Start a fresh v2 control run using `fixtures/harry_potter_four_game_manifest.json`
- [x] Confirm the extended run entered the v2 parallel batch pipeline
- [ ] Monitor run status through completion
- [ ] Compare extended-run outcomes against journaled expectations

**Status:** In Progress

---

## 📝 Journal Entries

### 2026-04-30 09:45 - Baseline Identification and Control Test Setup

**What Changed:**
- Created a dedicated journal for v2 Harry Potter control test work.
- Verified the v2 CLI surface and current `start-batch` invocation options.
- Confirmed the most recent successful baseline production smoke run is `cli_v2_hp_two_game_20260429`.
- Verified local baseline artifact presence at `runs/cli_v2_hp_two_game_20260429/run_state.json`.
- Read the baseline run state and confirmed:
  - `status: transform_completed`
  - `current_phase: parallel_batch_finished`
  - `games_total: 2`
  - `games_transform_completed: 2`
  - `games_transform_failed: 0`
- Checked for a locally preserved four-game lab artifact at `runs/opv2_live_four_game_20229/lab_run_state.json` and found it missing.

**Why:**
The control tests need a trustworthy known-good reference before launching new runs. The journaled two-game v2 smoke run is present locally and provides the cleanest current baseline for direct comparison. The four-game run remains documented in the journal, but its local artifact directory is not currently available at the expected path, so the new extended control test will serve as the fresh verification source.

**Files Created:**
- `docs/journals/v2-harry-potter-control-tests.md` - Journal for baseline verification and new control-test execution.

**Next Steps:**
- [ ] Continue polling the two-game control run until final completion
- [ ] Resolve final `status` and `result` contracts for the two-game run
- [ ] Continue polling the four-game control run until stable stage progress is visible
- [ ] Resolve final `status` and `result` contracts for the four-game run
- [ ] Summarize pass/fail against baseline expectations

**Status:** In Progress

---

### 2026-04-30 09:49 - Live Control Runs Started

**Achievement:**
Started fresh two-game and four-game Harry Potter v2 control runs and confirmed that both entered the operator pipeline.

**Implementation Details:**
- Started two-game run `hp_v2_control_two_game_20260430` against `fixtures/harry_potter_two_game_manifest.json`.
- Started four-game run `hp_v2_control_four_game_20260430` against `fixtures/harry_potter_four_game_manifest.json`.
- Confirmed both runs reached:
  - `status: running`
  - `current_phase: parallel_batch_running`
- Verified the two-game run created expected per-game operator pipeline artifacts under `runs/hp_v2_control_two_game_20260430/games/`.
- Verified both games in the two-game run completed stage 1 (`gameplay_narrative`) successfully with `returncode: 0`.
- Verified both games in the two-game run advanced into stage 2 (`visual_emoji_identity`) with fresh heartbeats, indicating active worker progress.
- Observed that top-level CLI `status` currently remains coarse/stale for in-flight v2 execution (`games_transform_completed: 0` and unchanged `updated_at`) even while nested stage state files continue progressing.
- Confirmed the four-game run entered the same v2 batch path with:
  - `games_total: 4`
  - `operator_pipeline_v2.enabled: true`
  - `max_retries_per_stage: 3`

**Technical Decisions:**
Per-stage artifact inspection is currently the more reliable live-health signal than the top-level CLI `status` response for v2 runs, because nested operator state files show active heartbeats and stage advancement while the top-level summary has not yet advanced.

**Testing:**
Verified with:
- `python3 scripts/creative_refactor_cli.py --json start-batch ...`
- `python3 scripts/creative_refactor_cli.py --json status --run-id ...`
- direct inspection of:
  - `run_state.json`
  - `run_parallel_batch_debug_trace.log`
  - `game_state.json`
  - `operator_stage_state.json`
  - `operator_stdout.txt`

**Next Steps:**
- [ ] Wait for stage 2+ completion in the two-game run
- [ ] Resolve final `result` contract for the two-game run
- [ ] Inspect early stage artifacts for the four-game run
- [ ] Resolve final `result` contract for the four-game run
- [ ] Produce a control-test summary with baseline comparison

**Status:** In Progress

---

### 2026-04-30 10:50 - Best Point-in-Time Checkpoint Before Commit

**Achievement:**
Captured the prompt-leak fix and the cleanest current neutral no-prompt validation state as a checkpoint commit.

**Implementation Details:**
- Identified the main contamination path as manifest `display_name` flowing from `scripts/create_run.py` into `scripts/run_operator_pipeline_game.py` prompt packets.
- Verified the same shared source game received conflicting prompt context before the fix:
  - two-game run used `display_name: Control Game 1`
  - four-game run used `display_name: Harry Potter Lab Game 1`
- Patched `scripts/run_operator_pipeline_game.py` so generic manifest labels are sanitized before entering operator prompt packets.
- Verified sanitized prompt packets for both no-prompt reruns now match on the shared game:
  - `display_name: 25b14fff-43f9-452a-8820-54d8056bfe84`
  - `selected_style_id: neutral_prototype`
  - `remix_prompt: None`
- Re-ran both no-prompt neutral controls:
  - `hp_v2_control_two_game_20260430_rerun`
  - `hp_v2_control_four_game_20260430_rerun`
- Verified the reruns did **not** produce spec adaptation:
  - `spec_adaptor: null`
  - no `spec_adaptor/` directory
- Verified the shared game now lands in a neutral/original family instead of Harry Potter:
  - two-game rerun title: `Heartline Vanguard: Escort Run`
  - four-game rerun title: `Starlight Sentinel: Corridor Defense`
- Latest live status at checkpoint:
  - two-game rerun completed successfully: `2 / 2`
  - four-game rerun still active with `2 / 4` games completed and one failed stage in `08a032f7-6c39-461b-9cf1-03c117c12b6b` stage 1

**Technical Decisions:**
This is the best checkpoint to preserve because it contains the key contamination fix, a validated no-prompt rerun showing aligned prompt packets, and enough live evidence to separate “prompt/spec leakage” from the remaining issue of neutral-theme creative drift.

**Testing:**
Verified with:
- direct prompt-packet comparison for the shared game across reruns
- run-state inspection for both reruns
- stage-state aggregation for completion/running/failure counts
- output-title inspection showing removal of Harry Potter drift from the shared game

**Next Steps:**
- [ ] Inspect the failed stage in the four-game rerun if we want full pipeline reliability
- [ ] Decide whether neutral/no-prompt mode should preserve source thematic identity more strictly
- [ ] If needed, tighten operator instructions so neutral mode favors original thematic retention over generic sci-fi reinterpretation

**Status:** In Progress

---

### 2026-04-30 10:52 - Prompt-Control Follow-up Setup

**Achievement:**
Prepared a dedicated two-game manifest for the next pair of prompt-driven control tests using the requested game ids.

**Implementation Details:**
- Created `fixtures/control_prompt_spiderman_brainrot_two_game_manifest.json`.
- Included the two requested source games:
  - `5b273ca9-6828-4560-a0a8-e56cec6780f8`
  - `25b14fff-43f9-452a-8820-54d8056bfe84`
- Assigned neutral display labels:
  - `Prompt Control Game 1`
  - `Prompt Control Game 2`
- This manifest is intended to be reused for two separate prompt-control runs:
  - prompt: `spider man`
  - prompt: `brainrot`

**Technical Decisions:**
The manifest uses neutral display names so the next prompt-driven comparison isolates the user prompt as the main thematic steering factor, instead of allowing franchise or fixture naming to bias the operator prompt packets.

**Next Steps:**
- [ ] Launch `spider man` control test
- [ ] Launch `brainrot` control test
- [ ] Capture run ids and early prompt/spec state
- [ ] Compare thematic behavior between the two prompt-driven runs

**Status:** In Progress

---

### 2026-04-30 11:05 - Master Plan for Spec-Layer Hardening and Retry Safety

**Achievement:**
Recorded the regression-safe implementation plan for hardening spec-adaptor IO contracts and adding bounded augmented retries at the spec layer.

**Implementation Details:**
- Established a five-part plan:
  1. Contract hardening for required spec-adaptor outputs
  2. Three-attempt retry architecture at the spec layer
  3. Augmented retry prompts that explicitly list missing/invalid artifacts
  4. Non-regression guardrails for healthy prompt and no-prompt paths
  5. Verification matrix using `brainrot`, `spider man`, and neutral reruns
- The immediate motivating failure is `prompt_control_brainrot_20260430`, where:
  - recomposition agent returned `returncode=0`
  - stdout claimed `recomposition_summary.json` was changed
  - required `recomposition_summary.json` was missing on disk
  - batch aborted before operator stages launched
- Agreed design direction:
  - retries must include previous failure evidence
  - retries must explicitly name missing files / invalid JSON / missing required keys
  - successful spec adaptation must require validated artifact presence, not just successful stdout

**Master Plan:**
- **Phase 1 — Contract Hardening**
  - Require `recomposition_summary.json`
  - Validate file existence, valid JSON, and required keys
  - Validate stdout/file consistency
  - Emit structured validation failures
- **Phase 2 — Spec-Layer Retry System**
  - Add max 3 attempts
  - Store artifacts in `spec_adaptor/attempt_01..03/`
  - Record per-attempt state and failure reasons
  - Publish top-level `ready` only on validated success
- **Phase 3 — Augmented Retry Prompting**
  - Inject previous failure reason
  - List exact missing/invalid artifacts
  - Include concise prior stdout/stderr evidence
  - Require explicit pre-finish verification
- **Phase 4 — Non-Regression Guardrails**
  - Preserve healthy prompt flows
  - Preserve no-prompt behavior skipping spec adaptor
  - Keep retry additive and artifact-preserving
- **Phase 5 — Verification**
  - Re-run `prompt_control_brainrot_20260430`
  - Re-check `prompt_control_spiderman_20260430`
  - Re-check neutral no-prompt reruns
  - Ensure no false `ready` states remain

**Implementation Order:**
1. Add validation helpers in `scripts/spec_adaptor.py`
2. Stop false-ready publication on invalid artifact bundles
3. Add attempt-local spec artifact layout
4. Add 3-attempt retry loop
5. Add augmented retry harness content
6. Re-run `brainrot`
7. Regression-check `spider man` and no-prompt paths
8. Update journal and commit

**Primary Files Expected to Change:**
- `scripts/spec_adaptor.py`
- `scripts/run_operator_pipeline_batch.py`
- `docs/journals/v2-harry-potter-control-tests.md`

**Success Criteria:**
- Missing required spec artifacts cannot be mislabeled as success
- Retry attempts explicitly name missing/invalid outputs
- Spec adaptation retries up to 3 times
- Failed runs leave precise per-attempt evidence
- Healthy prompt runs still work
- No-prompt runs remain unaffected

**Dry Plan Extension: Scaffold + Mutation Validation**
- Seed `recomposition_summary.json` with scaffold placeholders before each attempt.
- Validate mutation instead of existence only:
  - file still exists
  - valid JSON
  - required keys present
  - placeholder sentinel values removed
  - semantically populated fields
- Longer-term preferred shape:
  - clean attempt-local spec workspaces
  - canonical promoted result pointers
  - reusable mutation-validation pattern for other structured agent-authored outputs

**Status:** In Progress

---

## 🐛 Known Issues

### Missing Historical Four-Game Local Artifact

**Problem:** 
The journal references a successful four-game v2 fixture run `opv2_live_four_game_20229`, but the expected local file `runs/opv2_live_four_game_20229/lab_run_state.json` is not present.

**Root Cause:** 
Unknown from current inspection. The run may have been cleaned up, moved, or recorded only in journal output.

**Status:** 
- [x] Being investigated
- [ ] Blocked (waiting for...)
- [x] Fixed

**Workaround:** 
Use the documented journal record as historical evidence and run a fresh four-game control test for current validation.

**Resolution:** 
The exact historical local artifact path is still unavailable, but the extended-run history is sufficiently documented in `docs/journals/operator-pipeline-v2.md`, and a fresh four-game control run has now been started to replace the missing preserved local evidence.

---

## 📚 Quick Reference

### Key Files

- `docs/journals/operator-pipeline-v2.md` - Historical v2 rollout journal and baseline evidence
- `docs/journals/v2-harry-potter-control-tests.md` - Current control test journal
- `fixtures/harry_potter_two_game_manifest.json` - Fast control-test fixture
- `fixtures/harry_potter_four_game_manifest.json` - Extended control-test fixture
- `scripts/creative_refactor_cli.py` - Main CLI entrypoint
- `scripts/run_operator_pipeline_batch.py` - v2 batch orchestration path

### Important Commands

```bash
# Inspect CLI
python3 scripts/creative_refactor_cli.py start-batch --help

# Start a two-game v2 control run
python3 scripts/creative_refactor_cli.py --json start-batch \
  --manifest fixtures/harry_potter_two_game_manifest.json \
  --pipeline v2 \
  --style neutral_prototype \
  --run-id hp_v2_control_two_game_20260430

# Poll status
python3 scripts/creative_refactor_cli.py --json status \
  --run-id hp_v2_control_two_game_20260430

# Resolve final result
python3 scripts/creative_refactor_cli.py --json result \
  --run-id hp_v2_control_two_game_20260430
```

---

## 💭 Notes & Decisions

### Design Decisions

**Decision:** Use `cli_v2_hp_two_game_20260429` as the primary known-good baseline.  
**Rationale:** It is both documented and still present locally with a complete `run_state.json`, making it the strongest available control reference.  
**Alternatives Considered:** Using the four-game fixture run as the primary baseline was rejected because the expected local run artifact was not found.

### Future Enhancements

**Potential Improvements:**
- Add a small helper command for baseline comparison across run ids.
- Preserve summarized fixture verification artifacts in a stable path for future regression checks.
- Extend the scaffold + mutation-validation pattern to other structured agent-authored artifacts across the pipeline.
- Priority future candidates:
  - judge/evidence JSON artifacts
  - attempt-level markdown/json reports
  - structured adaptation summaries
- Preferred long-term shape:
  - scaffold required files
  - validate semantic mutation, not just presence
  - use clean attempt-local retries
  - keep canonical promoted pointers for downstream readers

---

### 2026-04-30 13:55 - Prompt-Title / Neutral-Title Prompt Packet Hardening

**Achievement:**
Hardened the operator prompt packet title logic so prompt runs intentionally use the prompt as creative title context, while no-prompt runs use a neutral generic title and no longer leak manifest test labels.

**Implementation Details:**
- Confirmed the no-prompt contamination source by reading:
  - `runs/prompt_control_no_prompt_e2e_20260430/games/5b273ca9-6828-4560-a0a8-e56cec6780f8/operator_pipeline/stage_01_gameplay_narrative/attempt_01/operator_prompt.txt`
- Verified the operator prompt packet still contained:
  - `display_name: Prompt Control Game 1`
  - `remix_prompt: None`
- Patched `scripts/run_operator_pipeline_game.py`:
  - expanded `sanitize_display_name_for_prompt(...)` to accept `remix_prompt`
  - if `remix_prompt` is present and non-empty, return the prompt text as the prompt-facing display title
  - if no prompt is present and the manifest label is generic/unsafe, return `Game Remix`
  - added `prompt control game ` to the unsafe prefix list
- Re-ran a fresh no-prompt validation batch:
  - `prompt_control_no_prompt_e2e_fix_20260430`
- Verified the fresh operator prompt packet now contains:
  - `display_name: Game Remix`
  - `remix_prompt: None`

**Why:**
The no-prompt control path must remain neutral. Passing fixture labels like `Prompt Control Game 1` into the agent-facing prompt packet adds unintended context that can bias theme adaptation. Using the user prompt as title for prompted runs is intentional creative conditioning, while `Game Remix` keeps no-prompt runs generic and clean.

**Testing:**
Verified with:
- prompt-packet inspection before the fix
- source-code patch in `scripts/run_operator_pipeline_game.py`
- fresh rerun `prompt_control_no_prompt_e2e_fix_20260430`
- prompt-packet inspection after the fix confirming `display_name: Game Remix`

**Next Steps:**
- [ ] Finish monitoring `prompt_control_no_prompt_e2e_fix_20260430` to full completion if a final regression pass is desired
- [ ] Commit checkpoint with spec-adaptor hardening + prompt-packet contamination fixes

**Status:** In Progress
