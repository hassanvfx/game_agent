# Operator Pipeline v2 Lab Scaffold Implementation Journal
# Operator Pipeline v2 Lab Scaffold Implementation Journal

**Last Updated:** 2026-04-29  
**Feature Spec:** `docs/operator_pipeline_manual.md`  
**Baseline Reference:** `docs/journals/formal-creative-refactor-cli-followup.md`

---

## 📊 Implementation Status Overview

### ✅ Milestone 0: Baseline Confirmation - **Complete**

- [x] Real prompt-aware production CLI path revalidated before this task
- [x] Known-good run documented as `cli_prompt_hp_known_state_20260429`
- [x] Spec adaptor reported `ready`
- [x] 2 / 2 fixture games completed successfully

**Status:** ✅ Complete

### ✅ Milestone 1: Documentation and Task Journal - **Complete**

- [x] Create this ClineFlow journal
- [x] Create `docs/operator_pipeline_manual.md`
- [x] Document production boundaries, fixture-first workflow, dry-run mode, retry contract, and future execution model

**Status:** ✅ Complete

### ✅ Milestone 2: Registry Config and Loader - **Complete**

- [x] Create `configs/operator_pipeline_v2.json`
- [x] Create `scripts/operator_registry_v2.py`
- [x] Validate unique operator IDs
- [x] Validate sequential stage numbers
- [x] Validate prompt paths
- [x] Support resolving `--step` and `--through`

**Status:** ✅ Complete

### ✅ Milestone 3: Operator Prompt Skeletons - **Complete**

- [x] Create gameplay/narrative operator prompt
- [x] Create visual/emoji identity operator prompt
- [x] Create audio integration operator prompt
- [x] Create final code/UI/mobile repair operator prompt
- [x] Include shared stdout contract and preservation rules

**Status:** ✅ Complete

### ✅ Milestone 4: Harry Potter Fixture Lab Manifest - **Complete**

- [x] Create `fixtures/operator_pipeline_lab/harry_potter/README.md`
- [x] Create `fixtures/operator_pipeline_lab/harry_potter/lab_manifest.json`
- [x] Reference known-good run, source manifests, adapted spec dir, audio catalog, emoji assets, and expected games

**Status:** ✅ Complete

### ✅ Milestone 5: Safe Lab Runner Scaffold - **Complete**

- [x] Create `scripts/operator_pipeline_lab.py`
- [x] Support `inspect-registry`
- [x] Support dry-run with `--step`
- [x] Support dry-run with `--through`
- [x] Add guarded execution-facing placeholders that refuse real execution unless `--execute` is passed

**Status:** ✅ Complete

### ✅ Milestone 6: Stage/Retry Artifact Contract - **Complete**

- [x] Document planned artifact layout
- [x] Include retry model
- [x] Reserve state files for arbitrary resume
- [x] Print planned artifact paths during dry-run

**Status:** ✅ Complete

### ✅ Milestone 7: Lab-Local Run Initialization - **Complete**

- [x] Add `init-run` command
- [x] Add `inspect-run` command
- [x] Copy fixture source games into lab-local `input/` and `pipeline/current/`
- [x] Write `lab_run_state.json`
- [x] Verify init/inspect workflow without worker execution

**Status:** ✅ Complete

### ✅ Milestone 8: Operator Prompt Packet Generation - **Complete**

- [x] Add `build-prompt` command
- [x] Copy `pipeline/current/` into a stage attempt workspace
- [x] Write `operator_prompt.txt`
- [x] Write `operator_invocation.json`
- [x] Write `operator_stage_state.json`
- [x] Update `lab_run_state.json` with prompt-built attempt metadata
- [x] Verify generated JSON and non-empty prompt packet

**Status:** ✅ Complete

### ✅ Milestone 9: Guarded Single-Stage Worker Execution - **Complete**

- [x] Implement `run-step` for prepared prompt packets
- [x] Keep `run-step` guarded by required `--execute`
- [x] Reuse `execute_worker_command()`
- [x] Stream stdout/stderr to attempt artifacts
- [x] Parse shared operator stdout contract into `operator_result.json`
- [x] Heartbeat and update `operator_stage_state.json`
- [x] Keep `run-progressive` guarded as a placeholder until retry/promotion
- [x] Verify guard behavior without invoking workers

**Status:** ✅ Complete

### ✅ Milestone 10: Attempt Promotion - **Complete**

- [x] Add workspace replacement helper for promotion
- [x] Promote successful `run-step` attempts to `pipeline/current/`
- [x] Add manual `promote-attempt` command
- [x] Require completed `operator_result.json` for manual promotion
- [x] Update `completed_stages`, stage status, promoted attempt metadata, and current workspace
- [x] Verify promotion workflow without invoking real workers

**Status:** ✅ Complete

### ✅ Milestone 11: Progressive One-Game Orchestration - **Complete**

- [x] Implement `run-progressive` for one game
- [x] Resolve stages through `--through`
- [x] Support `--from-stage`
- [x] Skip completed stages
- [x] Build missing prompts per attempt
- [x] Run stage attempts through guarded `run-step`
- [x] Promote successful attempts
- [x] Retry up to `max_retries_per_stage`
- [x] Mark stage/game/run failed when all attempts fail
- [x] Verify guard and completed-stage skip behavior without launching a new worker

**Status:** ✅ Complete

### ✅ Milestone 12: First Live One-Game Progressive Fixture Run - **Complete**

- [x] Initialize fresh live lab run `opv2_live_one_game_20260429`
- [x] Run one game through all four v2 operator stages
- [x] Confirm 4 / 4 stages completed
- [x] Confirm 0 failed stages
- [x] Confirm final workspace exists under `pipeline/current/`
- [x] Inspect stage result summaries
- [x] Confirm final `index.html` exists and contains broom/audio/start flow markers

**Status:** ✅ Complete

### ✅ Milestone 13: Four-Game Fixture Orchestration Scaffold - **Complete**

- [x] Create `fixtures/harry_potter_four_game_manifest.json`
- [x] Add four-game manifest reference to Harry Potter lab manifest
- [x] Add `--source-manifest` override to `init-run`
- [x] Add `run-fixture` command
- [x] Support optional `--game-id`, `--from-stage`, and `--fail-fast`
- [x] Write aggregate `fixture_run_summary` to `lab_run_state.json`
- [x] Verify four-game initialization and guarded `run-fixture`

**Status:** ✅ Complete

### ✅ Milestone 14: Four-Game Live Run Monitoring and Resume - **Complete**

- [x] Start four-game live fixture run `opv2_live_four_game_20229`
- [x] Detect external shell timeout during long fixture run
- [x] Add `summarize-run` command for resume-oriented monitoring
- [x] Confirm game 1 completed 4 / 4 stages
- [x] Confirm game 2 completed 4 / 4 stages after resume
- [x] Run game 3 through all stages
- [x] Run game 4 through all stages
- [x] Summarize final four-game aggregate results

**Status:** ✅ Complete

### ✅ Milestone 15: Production CLI v2 Integration - **Complete**

- [x] Clone `run_parallel_batch.py` to `scripts/run_operator_pipeline_batch.py`
- [x] Create `scripts/run_operator_pipeline_game.py`
- [x] Preserve parallel game scheduling and sequential per-game stages
- [x] Wire `creative_refactor_cli.py start-batch` to use v2 by default
- [x] Keep `--pipeline legacy` fallback
- [x] Launch real CLI v2 smoke run `cli_v2_hp_two_game_20260429`
- [x] Verify final `status` contract
- [x] Verify final `result` contract
- [x] Fix stale heartbeat compatibility in production v2 batch runner
- [ ] Update docs/journal and commit production integration checkpoint

**Status:** ✅ Complete

---

## 📝 Journal Entries

### 2026-04-29 16:45 - Initial Setup

**What Changed:**
- Created the ClineFlow journal for the operator pipeline v2 lab scaffold.
- Recorded the known-good production baseline as the starting point.
- Defined milestone tracking for docs, config, prompts, fixture manifest, registry loader, dry-run runner, and verification.

**Why:**
The project requires every task to maintain persistent context through `docs/journals/`. This scaffold is intentionally isolated from production so staged operators can be developed against fixtures without replacing the healthy production creative refactor pipeline.

**Baseline Evidence:**
- Run ID: `cli_prompt_hp_known_state_20260429`
- Run directory: `runs/cli_prompt_hp_known_state_20260429`
- Source manifest: `fixtures/harry_potter_two_game_manifest.json`
- Style: `neutral_prototype`
- Prompt: `make it harry potter like with flappy bird gameplay`
- Model: `gpt-5.4`
- Status: `transform_completed`
- Games completed: `2 / 2`
- Spec adaptor status: `ready`

**Production Boundaries:**
The first v2 lab milestone must not modify production behavior. These files are explicitly out of scope unless requested later:
- `scripts/run_single_game.py`
- `scripts/run_parallel_batch.py`
- `scripts/creative_refactor_cli.py`
- `scripts/generate_task_packet.py`
- `scripts/spec_adaptor.py`

**Planned Files:**
- `docs/operator_pipeline_manual.md`
- `configs/operator_pipeline_v2.json`
- `scripts/operator_registry_v2.py`
- `scripts/operator_pipeline_lab.py`
- `prompts/operators_v2/01_gameplay_narrative.md`
- `prompts/operators_v2/02_visual_emoji_identity.md`
- `prompts/operators_v2/03_audio_integration.md`
- `prompts/operators_v2/04_final_code_ui_mobile_repair.md`
- `fixtures/operator_pipeline_lab/harry_potter/README.md`
- `fixtures/operator_pipeline_lab/harry_potter/lab_manifest.json`

**Resume-Oriented Design Decision:**
The scaffold will reserve a stateful artifact layout that supports future live code testing and arbitrary resume:
- `lab_run_state.json` as run-level state
- `operator_stage_state.json` as attempt-level state
- `operator_invocation.json` for command/prompt metadata
- `operator_result.json` for parsed worker result
- `pipeline/current/` as the promoted latest-good workspace

**Next Steps:**
- [x] Create `docs/operator_pipeline_manual.md`
- [x] Create registry config and prompt skeletons
- [x] Create fixture manifest and README
- [x] Implement registry loader and dry-run lab CLI
- [x] Run verification commands
- [x] Update this journal with final verification results

**Status:** Complete

---

### 2026-04-29 16:52 - Scaffold Implementation and Verification

**Achievement:**
Completed the fixture-first Operator Pipeline v2 lab scaffold and verified the requested dry-run command set.

**Implementation Details:**
- Created `docs/operator_pipeline_manual.md` with pipeline overview, operator scopes, registry model, dry-run behavior, retry semantics, artifact layout, and future resume model.
- Created `configs/operator_pipeline_v2.json` with four sequential operators and three retries per stage.
- Created `prompts/operators_v2/01_gameplay_narrative.md` for gameplay/copy adaptation while preserving mechanics.
- Created `prompts/operators_v2/02_visual_emoji_identity.md` for visual/emoji identity work.
- Created `prompts/operators_v2/03_audio_integration.md` for non-blocking catalog-only audio integration.
- Created `prompts/operators_v2/04_final_code_ui_mobile_repair.md` for final repair, UI, and mobile-safe cleanup.
- Created `fixtures/operator_pipeline_lab/harry_potter/README.md` and `lab_manifest.json` referencing the known-good Harry Potter/flappy control run.
- Created `scripts/operator_registry_v2.py` with registry loading, validation, `--step`/`--through` resolution, and deterministic stage slug helpers.
- Created `scripts/operator_pipeline_lab.py` with `inspect-registry`, dry-run planning, fixture validation, artifact path planning, and guarded future execution placeholders.

**Technical Decisions:**
- Dry-run mode prints planned paths but does not create production runs, invoke Cline, or execute workers.
- The artifact layout reserves `pipeline/current/`, stage attempt folders, `operator_stage_state.json`, `operator_invocation.json`, and `operator_result.json` for future arbitrary resume.
- `run-step` and `run-progressive` are intentionally guarded placeholders; without `--execute` they refuse execution, and with `--execute` they still report that live v2 execution is not implemented in this scaffold milestone.
- The lab runner reuses existing JSON helper `load_json()` from `scripts/creative_refactor_runtime.py`.

**Verification:**
Passed:

```bash
python3 -m py_compile scripts/operator_registry_v2.py scripts/operator_pipeline_lab.py
python3 -m json.tool configs/operator_pipeline_v2.json >/dev/null
python3 -m json.tool fixtures/operator_pipeline_lab/harry_potter/lab_manifest.json >/dev/null
python3 scripts/operator_pipeline_lab.py --help
python3 scripts/operator_pipeline_lab.py inspect-registry
python3 scripts/operator_pipeline_lab.py dry-run --fixture harry_potter --step audio_integration
python3 scripts/operator_pipeline_lab.py dry-run --fixture harry_potter --through final_code_ui_mobile_repair
```

Production boundary check passed:

```bash
git diff --name-only -- scripts/run_single_game.py scripts/run_parallel_batch.py scripts/creative_refactor_cli.py scripts/generate_task_packet.py scripts/spec_adaptor.py
```

The command returned no modified production files.

**Status:** Complete

---

### 2026-04-29 17:10 - Milestone 2 Start: Lab-Local Run Initialization

**What Changed:**
- Started the next master-plan milestone after the dry-run scaffold.
- Inspected `fixtures/harry_potter_two_game_manifest.json`.
- Confirmed both source game paths exist:
  - `/Volumes/Elements/full_7k_qa_release/mirror_runs/full_7k_run_20260415_snapshot/games/25b14fff-43f9-452a-8820-54d8056bfe84/replay/attempt_0001`
  - `/Volumes/Elements/full_7k_qa_release/mirror_runs/full_7k_run_20260415_snapshot/games/08a032f7-6c39-461b-9cf1-03c117c12b6b/replay/attempt_0001`

**Planned Implementation:**
- Extend `scripts/operator_pipeline_lab.py` with:
  - `init-run --fixture harry_potter`
  - `inspect-run --fixture harry_potter --lab-run-id <id>`
- Create lab-local run directories under:
  - `fixtures/operator_pipeline_lab/harry_potter/runs/<lab_run_id>/`
- Copy source game code into:
  - `games/<game_id>/input/`
  - `games/<game_id>/pipeline/current/`
- Write `lab_run_state.json` as the future resume source of truth.
- Keep worker execution disabled.

**Verification:**
Passed:

```bash
python3 -m py_compile scripts/operator_pipeline_lab.py scripts/operator_registry_v2.py
python3 scripts/operator_pipeline_lab.py --help
python3 scripts/operator_pipeline_lab.py init-run --fixture harry_potter --lab-run-id opv2_milestone2_verify_20260429
python3 scripts/operator_pipeline_lab.py inspect-run --fixture harry_potter --lab-run-id opv2_milestone2_verify_20260429
python3 scripts/operator_pipeline_lab.py dry-run --fixture harry_potter --through final_code_ui_mobile_repair
```

Generated run:

```text
fixtures/operator_pipeline_lab/harry_potter/runs/opv2_milestone2_verify_20260429/
```

Git hygiene check:

```bash
git status --short --ignored fixtures/operator_pipeline_lab/harry_potter/runs .gitignore docs/operator_pipeline_manual.md docs/journals/operator-pipeline-v2.md scripts/operator_pipeline_lab.py
```

Confirmed generated lab run output is ignored:

```text
!! fixtures/operator_pipeline_lab/harry_potter/runs/
```

**Additional Files Updated:**
- `.gitignore` now ignores `fixtures/operator_pipeline_lab/*/runs/`.
- `docs/operator_pipeline_manual.md` now documents `init-run`, `inspect-run`, lab-local workspace semantics, and lab run verification commands.

**Status:** Complete

---

### 2026-04-29 17:31 - Milestone 8: Operator Prompt Packet Generation

**Achievement:**
Implemented and verified prompt packet generation for one lab-local game/stage/attempt without invoking workers.

**Implementation Details:**
- Extended `scripts/operator_pipeline_lab.py` with `build-prompt`.
- Added lab run state loading helpers.
- Added game and stage lookup helpers.
- Added prompt packet rendering that combines:
  - lab invocation metadata
  - working clone path
  - latest-good workspace path
  - known-good run metadata
  - adapted spec path
  - audio catalog path
  - emoji asset root
  - default style/remix prompt
  - retry context placeholder
  - required stdout contract
  - operator-specific prompt skeleton
- Added `operator_invocation.json` generation.
- Added `operator_stage_state.json` generation.
- Updated `lab_run_state.json` stage attempts with prompt-built metadata.
- Updated `docs/operator_pipeline_manual.md` with `build-prompt` usage and verification.

**Verification:**
Passed:

```bash
python3 -m py_compile scripts/operator_pipeline_lab.py scripts/operator_registry_v2.py

python3 scripts/operator_pipeline_lab.py build-prompt \
  --fixture harry_potter \
  --lab-run-id opv2_milestone2_verify_20260429 \
  --game-id 25b14fff-43f9-452a-8820-54d8056bfe84 \
  --step audio_integration \
  --attempt 1

python3 -m json.tool \
  fixtures/operator_pipeline_lab/harry_potter/runs/opv2_milestone2_verify_20260429/games/25b14fff-43f9-452a-8820-54d8056bfe84/pipeline/stage_03_audio_integration/attempt_01/operator_invocation.json \
  >/dev/null

python3 -m json.tool \
  fixtures/operator_pipeline_lab/harry_potter/runs/opv2_milestone2_verify_20260429/games/25b14fff-43f9-452a-8820-54d8056bfe84/pipeline/stage_03_audio_integration/attempt_01/operator_stage_state.json \
  >/dev/null

test -s \
  fixtures/operator_pipeline_lab/harry_potter/runs/opv2_milestone2_verify_20260429/games/25b14fff-43f9-452a-8820-54d8056bfe84/pipeline/stage_03_audio_integration/attempt_01/operator_prompt.txt

python3 scripts/operator_pipeline_lab.py inspect-run \
  --fixture harry_potter \
  --lab-run-id opv2_milestone2_verify_20260429
```

**Safety:**
- `build-prompt` does not invoke workers.
- `build-prompt` does not invoke Cline.
- Existing attempt directories are refused to avoid accidental overwrite.
- Generated prompt packet artifacts remain under git-ignored fixture lab runs.

**Status:** Complete

---

### 2026-04-29 17:36 - Milestone 9: Guarded Single-Stage Worker Execution

**Achievement:**
Implemented the first live worker execution path as a guarded, single-stage `run-step` command for previously prepared prompt packets.

**Implementation Details:**
- Extended `scripts/operator_pipeline_lab.py` with guarded `run-step` execution.
- `run-step` now requires:
  - `--fixture`
  - `--lab-run-id`
  - `--game-id`
  - `--step`
  - `--attempt`
  - `--execute`
- Reused `execute_worker_command()` from `scripts/creative_refactor_runtime.py`.
- Added `build_worker_command()` for the lab-local Cline command shape.
- Added heartbeat updates to `operator_stage_state.json`.
- Added `parse_operator_stdout()` for the shared operator stdout contract.
- Added `operator_result.json` writing with:
  - status
  - execution status
  - return code
  - timeout flag
  - summary
  - changed files
  - mechanics/visual/audio/mobile checks
  - stdout/stderr paths
  - timing metadata
- Updated `operator_invocation.json` with redacted command metadata when execution starts.
- Updated `lab_run_state.json` attempt status during running and completion.
- Kept `run-progressive` as a guarded placeholder until retry/promotion is implemented.

**Verification:**
Passed without invoking real workers:

```bash
python3 -m py_compile scripts/operator_pipeline_lab.py scripts/operator_registry_v2.py

python3 scripts/operator_pipeline_lab.py --help

python3 scripts/operator_pipeline_lab.py run-step \
  --fixture harry_potter \
  --lab-run-id opv2_milestone2_verify_20260429 \
  --game-id 25b14fff-43f9-452a-8820-54d8056bfe84 \
  --step audio_integration \
  --attempt 1 \
  2>&1 | grep -q "refuses real worker execution unless --execute is passed"

python3 scripts/operator_pipeline_lab.py run-progressive \
  --fixture harry_potter \
  --lab-run-id opv2_milestone2_verify_20260429 \
  --through final_code_ui_mobile_repair \
  2>&1 | grep -q "refuses real worker execution unless --execute is passed"
```

**Safety:**
- No worker is invoked unless `--execute` is explicitly present.
- `run-step` requires a prebuilt attempt from `build-prompt`.
- `run-progressive` remains unimplemented for execution until retry/promotion.
- No production orchestration files were modified.

**Status:** Complete

---

### 2026-04-29 17:40 - Milestone 10: Attempt Promotion

**Achievement:**
Implemented promotion of completed stage attempts into `pipeline/current/`, both automatically after successful `run-step` and manually through `promote-attempt`.

**Implementation Details:**
- Extended `scripts/operator_pipeline_lab.py` with `replace_workspace()`.
- Added `promote_attempt_workspace()` to replace the latest-good workspace with an attempt workspace.
- Added `validate_promotable_result()` requiring `operator_result.json.status == completed`.
- Added `promote-attempt` CLI command for manual promotion of completed attempts.
- Updated successful `run-step` behavior to automatically promote completed attempts.
- Updated lab run state promotion metadata:
  - attempt status becomes `promoted`
  - stage status becomes `completed`
  - stage records `promoted_attempt`
  - game appends stage slug to `completed_stages`
  - game removes stage slug from `failed_stages` if present
  - game `current_stage` returns to `null`
- Updated `docs/operator_pipeline_manual.md` with the promotion model and verification commands.

**Verification:**
Passed with a synthetic completed `operator_result.json` and no real worker invocation:

```bash
python3 -m py_compile scripts/operator_pipeline_lab.py scripts/operator_registry_v2.py

python3 scripts/operator_pipeline_lab.py promote-attempt \
  --fixture harry_potter \
  --lab-run-id opv2_milestone2_verify_20260429 \
  --game-id 25b14fff-43f9-452a-8820-54d8056bfe84 \
  --step audio_integration \
  --attempt 1

python3 scripts/operator_pipeline_lab.py inspect-run \
  --fixture harry_potter \
  --lab-run-id opv2_milestone2_verify_20260429
```

Observed `inspect-run` result:

```text
game: 25b14fff-43f9-452a-8820-54d8056bfe84
completed_stages: 1
failed_stages: 0
```

**Safety:**
- Promotion remains fixture-local under ignored lab run directories.
- Production orchestration files remain untouched.
- Manual promotion requires a completed result artifact.
- Progressive multi-stage orchestration remains deferred.

**Status:** Complete

---

### 2026-04-29 17:52 - Milestone 11: Progressive One-Game Orchestration

**Achievement:**
Implemented `run-progressive` for one-game stage sequencing with retries, promotion, completed-stage skipping, and resume-from-stage support.

**Implementation Details:**
- Replaced the previous `run-progressive` placeholder with `run_progressive_execute()`.
- Added helpers:
  - `mark_stage_failed()`
  - `stage_is_completed()`
  - `result_status()`
  - `build_prompt_for_progressive()`
  - `run_step_for_progressive()`
- `run-progressive` now:
  - requires `--execute`
  - requires `--game-id`
  - resolves operators through `--through`
  - filters by `--from-stage` when provided
  - skips already completed stages
  - builds missing prompt attempts
  - runs attempts via `run-step`
  - promotes completed attempts
  - retries up to registry `max_retries_per_stage`
  - marks stage/game/run failed if all attempts fail
- Updated `docs/operator_pipeline_manual.md` with progressive orchestration behavior and verification commands.

**Verification:**
Passed without launching a new worker:

```bash
python3 -m py_compile scripts/operator_pipeline_lab.py scripts/operator_registry_v2.py

python3 scripts/operator_pipeline_lab.py --help

python3 scripts/operator_pipeline_lab.py run-progressive \
  --fixture harry_potter \
  --lab-run-id opv2_milestone2_verify_20260429 \
  --game-id 25b14fff-43f9-452a-8820-54d8056bfe84 \
  --through final_code_ui_mobile_repair \
  2>&1 | grep -q "refuses real worker execution unless --execute is passed"

python3 scripts/operator_pipeline_lab.py run-progressive \
  --fixture harry_potter \
  --lab-run-id opv2_milestone2_verify_20260429 \
  --game-id 25b14fff-43f9-452a-8820-54d8056bfe84 \
  --from-stage audio_integration \
  --through audio_integration \
  --execute
```

Observed skip output:

```text
skip completed: stage_03_audio_integration
Operator Pipeline v2 progressive run completed
```

**Safety:**
- `run-progressive` refuses execution without `--execute`.
- Verification used an already completed synthetic stage to avoid launching a new worker.
- Generated lab run artifacts remain git-ignored.
- Production orchestration remains untouched.

**Status:** Complete

---

### 2026-04-29 18:35 - Milestone 12: First Live One-Game Progressive Fixture Run

**Achievement:**
Ran the first full live v2 progressive operator pipeline on one Harry Potter fixture game using real worker execution inside a fixture-local lab workspace.

**Run Details:**
- Fixture: `harry_potter`
- Lab run ID: `opv2_live_one_game_20260429`
- Game ID: `25b14fff-43f9-452a-8820-54d8056bfe84`
- Command:
  ```bash
  python3 scripts/operator_pipeline_lab.py run-progressive \
    --fixture harry_potter \
    --lab-run-id opv2_live_one_game_20260429 \
    --game-id 25b14fff-43f9-452a-8820-54d8056bfe84 \
    --through final_code_ui_mobile_repair \
    --model gpt-5.4 \
    --agent-timeout 900 \
    --execute
  ```

**Final Status:**
- Completed stages: `4`
- Failed stages: `0`
- Final workspace:
  ```text
  fixtures/operator_pipeline_lab/harry_potter/runs/opv2_live_one_game_20260429/games/25b14fff-43f9-452a-8820-54d8056bfe84/pipeline/current
  ```

**Stage Results:**
- `stage_01_gameplay_narrative`: completed
  - Adapted player-facing narrative to a magical broom-duel theme while preserving controls, progression, HUD behavior, shop flow, combat loop, restart flow, and mobile pointer input.
- `stage_02_visual_emoji_identity`: completed
  - Applied a fantasy visual reskin in `index.html`, updating HUD, menus, buttons, canvas-rendered scene/characters while preserving loop, controls, shop flow, and start entry point.
- `stage_03_audio_integration`: completed
  - Integrated gesture-safe semantic audio using approved catalog-backed audio pools and a gameplay loop.
- `stage_04_final_code_ui_mobile_repair`: completed
  - Repaired mobile safe areas and canvas resize stability without changing gameplay.

**Final Workspace Inspection:**
- `index.html` exists.
- `index.html` size: `47927` bytes.
- Marker checks:
  - `broom`: present
  - `audio`: present
  - `startGame`: present
  - `Harry`: not present
  - `Hogwarts`: not present

**Technical Note:**
The absence of direct `Harry`/`Hogwarts` text appears consistent with the lab's safer theme adaptation approach: the output preserved a magical broom-flight identity without relying on explicit protected names.

**Verification Commands:**
```bash
python3 scripts/operator_pipeline_lab.py inspect-run \
  --fixture harry_potter \
  --lab-run-id opv2_live_one_game_20260429

find fixtures/operator_pipeline_lab/harry_potter/runs/opv2_live_one_game_20260429/games/25b14fff-43f9-452a-8820-54d8056bfe84/pipeline \
  -maxdepth 4 \( -name 'operator_result.json' -o -name 'operator_stage_state.json' \) \
  -print | sort
```

**Safety:**
- All artifacts are under ignored fixture-local lab run directories.
- Production orchestration files were not modified.
- Only one game was executed; the second fixture game remains initialized but untouched.

**Status:** Complete

---

### 2026-04-29 18:51 - Milestone 13: Four-Game Fixture Orchestration Scaffold

**Achievement:**
Implemented the four-game fixture setup and fixture-level orchestration command needed to scale v2 from one game to a selected four-game batch.

**Implementation Details:**
- Created `fixtures/harry_potter_four_game_manifest.json` using the first four games from the five-game source manifest.
- Updated `fixtures/operator_pipeline_lab/harry_potter/lab_manifest.json` with `optional_four_game_manifest_path`.
- Added `--source-manifest` support to `init-run`.
  - This allows selecting a different source game set while keeping the same fixture context, adapted specs, audio catalog, and emoji assets.
- Added `run-fixture` to `scripts/operator_pipeline_lab.py`.
  - Iterates games from `lab_run_state.json`.
  - Optionally filters with `--game-id`.
  - Calls `run-progressive` for each selected game.
  - Supports `--from-stage`.
  - Supports `--fail-fast`.
  - Writes `fixture_run_summary` into `lab_run_state.json`.
- Updated `docs/operator_pipeline_manual.md` with the four-game manifest, `--source-manifest`, and `run-fixture` usage.

**Verification:**
Passed:

```bash
python3 -m py_compile scripts/operator_pipeline_lab.py scripts/operator_registry_v2.py

python3 -m json.tool fixtures/harry_potter_four_game_manifest.json >/dev/null

python3 -m json.tool fixtures/operator_pipeline_lab/harry_potter/lab_manifest.json >/dev/null

python3 scripts/operator_pipeline_lab.py --help

python3 scripts/operator_pipeline_lab.py init-run \
  --fixture harry_potter \
  --source-manifest fixtures/harry_potter_four_game_manifest.json \
  --lab-run-id opv2_live_four_game_20260429

python3 scripts/operator_pipeline_lab.py inspect-run \
  --fixture harry_potter \
  --lab-run-id opv2_live_four_game_20260429

python3 scripts/operator_pipeline_lab.py run-fixture \
  --fixture harry_potter \
  --lab-run-id opv2_live_four_game_20260429 \
  --through final_code_ui_mobile_repair \
  2>&1 | grep -q "refuses real worker execution unless --execute is passed"
```

**Four-Game Lab Run Initialized:**
- Lab run ID: `opv2_live_four_game_20260429`
- Games initialized: `4`
- Game IDs:
  - `25b14fff-43f9-452a-8820-54d8056bfe84`
  - `08a032f7-6c39-461b-9cf1-03c117c12b6b`
  - `5b273ca9-6828-4560-a0a8-e56cec6780f8`
  - `50fcc248-ffa7-41a2-aa08-dda405159b58`

**Safety:**
- `run-fixture` refuses execution unless `--execute` is passed.
- Four-game lab run artifacts remain under ignored fixture-local `runs/`.
- Production orchestration files remain untouched.

**Status:** Complete

---

### 2026-04-29 19:21 - Milestone 14 Start: Four-Game Live Run Monitoring

**What Changed:**
- Started the live four-game fixture run:
  ```bash
  python3 scripts/operator_pipeline_lab.py run-fixture \
    --fixture harry_potter \
    --lab-run-id opv2_live_four_game_20260429 \
    --through final_code_ui_mobile_repair \
    --model gpt-5.4 \
    --agent-timeout 900 \
    --fail-fast \
    --execute
  ```
- The host shell/background wrapper killed the parent `run-fixture` process after roughly 10 minutes, while game 2 was in progress.
- Added `summarize-run` to `scripts/operator_pipeline_lab.py` for long-run monitoring and resume planning.
- Updated `docs/operator_pipeline_manual.md` to document `summarize-run`.

**Current Live Run State:**
- Lab run ID: `opv2_live_four_game_20260429`
- Game 1 `25b14fff-43f9-452a-8820-54d8056bfe84`: `4 / 4` stages complete
- Game 2 `08a032f7-6c39-461b-9cf1-03c117c12b6b`: `4 / 4` stages complete after resume/continuation
- Game 3 `5b273ca9-6828-4560-a0a8-e56cec6780f8`: `0 / 4` stages complete
- Game 4 `50fcc248-ffa7-41a2-aa08-dda405159b58`: `0 / 4` stages complete

**Monitoring Command:**
```bash
python3 scripts/operator_pipeline_lab.py summarize-run \
  --fixture harry_potter \
  --lab-run-id opv2_live_four_game_20260429
```

**Technical Note:**
Long live fixture runs can exceed the environment's command wrapper timeout. The pipeline state remains resumable because each stage writes attempt artifacts and `lab_run_state.json`. Continue remaining games with individual `run-progressive` commands rather than one long parent `run-fixture` command.

**Next Steps:**
- [x] Commit `summarize-run` support
- [x] Run game 3 with `run-progressive`
- [x] Run game 4 with `run-progressive`
- [x] Summarize final four-game results

**Status:** Complete

---

### 2026-04-29 19:37 - Four-Game Live Run Complete

**Achievement:**
Completed the selected four-game Harry Potter v2 fixture run with all games finishing all four operator stages.

**Final Aggregate Result:**
- Lab run ID: `opv2_live_four_game_20260429`
- Games total: `4`
- Games completed: `4`
- Games failed: `0`
- Total stage completions: `16 / 16`

**Per-Game Final State:**
- `25b14fff-43f9-452a-8820-54d8056bfe84`: `4 / 4` stages complete, `0` failed
- `08a032f7-6c39-461b-9cf1-03c117c12b6b`: `4 / 4` stages complete, `0` failed
- `5b273ca9-6828-4560-a0a8-e56cec6780f8`: `4 / 4` stages complete, `0` failed
- `50fcc248-ffa7-41a2-aa08-dda405159b58`: `4 / 4` stages complete, `0` failed

**Verification Command:**
```bash
python3 scripts/operator_pipeline_lab.py summarize-run \
  --fixture harry_potter \
  --lab-run-id opv2_live_four_game_20260429
```

Aggregate verification output:

```text
aggregate_games_completed= 4
aggregate_games_failed= 0
```

**Operational Notes:**
- Long parent `run-fixture` commands can be killed by the host shell/background timeout.
- The fixture run remained resumable because each stage writes `operator_stage_state.json`, `operator_result.json`, and updates `lab_run_state.json`.
- `summarize-run` was used to identify exact resume points.
- Games 3 and 4 were completed with individual `run-progressive` resumes.

**Safety:**
- All generated artifacts remained under ignored fixture-local `runs/`.
- Production orchestration files were not modified.
- The four-game run used the v2 lab path only.

**Status:** Complete

---

### 2026-04-29 21:09 - Production CLI v2 Smoke Run

**Achievement:**
Validated that the real `creative_refactor_cli.py` path launches and completes a two-game production batch using the new operator pipeline v2 runner.

**Run Details:**
- CLI command:
  ```bash
  python3 scripts/creative_refactor_cli.py --json start-batch \
    --manifest fixtures/harry_potter_two_game_manifest.json \
    --run-id cli_v2_hp_two_game_20260429 \
    --style neutral_prototype \
    --remix-prompt "make it harry potter like with flappy bird gameplay" \
    --model gpt-5.4 \
    --agent-timeout 900 \
    --max-concurrency 1
  ```
- Launcher invocation confirmed:
  - `"pipeline": "v2"`
  - `"batch_runner": "run_operator_pipeline_batch.py"`

**Final Run State:**
From `runs/cli_v2_hp_two_game_20260429/run_state.json`:

```json
{
  "status": "transform_completed",
  "current_phase": "parallel_batch_finished",
  "games_total": 2,
  "games_transform_completed": 2,
  "games_transform_failed": 0
}
```

**Result Contract Verified:**
```bash
python3 scripts/creative_refactor_cli.py --json result \
  --run-id cli_v2_hp_two_game_20260429
```

Returned:

```json
{
  "run_id": "cli_v2_hp_two_game_20260429",
  "status": "transform_completed",
  "completed": true,
  "final_output_dirs": [
    ".../output/08a032f7-6c39-461b-9cf1-03c117c12b6b",
    ".../output/25b14fff-43f9-452a-8820-54d8056bfe84"
  ]
}
```

**Game-Level Confirmation:**
Both games ended with:
- `status: completed`
- `current_phase: creative_refactor_completed`
- `creative_status: completed`
- all four `operator_pipeline_completed_stages`

**Stale Heartbeat Compatibility Fix:**
Updated `run_operator_pipeline_batch.py` to detect v2 heartbeat/state files under:

```text
games/<game_id>/operator_pipeline/stage_*/attempt_*/operator_stage_state.json
```

and to mark those attempt state files failed on stale termination before falling back to the legacy `job_state.json` path.

This means the new production path now has v2-aware stale worker monitoring while preserving legacy compatibility.

**Status:** Complete

---

### 2026-04-29 21:12 - Production CLI v2 Integration Finalized

**Achievement:**
Completed the production integration checkpoint for operator pipeline v2 and verified the real main CLI path completes successfully with the new runner.

**Implementation Details:**
- Created `scripts/run_operator_pipeline_game.py` as the production per-game staged operator worker.
- Cloned and adapted `scripts/run_parallel_batch.py` into `scripts/run_operator_pipeline_batch.py`.
- Preserved bounded parallel scheduling across games.
- Preserved sequential stage execution within each game.
- Updated `scripts/creative_refactor_cli.py`:
  - added `--pipeline v2|legacy`
  - defaulted `start-batch` to `v2`
  - preserved `--pipeline legacy` fallback
  - recorded launcher metadata:
    - `pipeline`
    - `batch_runner`
- Verified production-compatible output layout:
  - `runs/<run_id>/run_state.json`
  - `runs/<run_id>/games/<game_id>/game_state.json`
  - `runs/<run_id>/output/<game_id>/`
- Added stale heartbeat compatibility for v2 by reading latest:
  - `operator_pipeline/stage_*/attempt_*/operator_stage_state.json`

**Main CLI v2 Smoke Run:**
- Run ID: `cli_v2_hp_two_game_20260429`
- Manifest: `fixtures/harry_potter_two_game_manifest.json`
- Style: `neutral_prototype`
- Prompt: `make it harry potter like with flappy bird gameplay`
- Model: `gpt-5.4`
- Agent timeout: `900`
- Max concurrency: `1`

**Verified Contracts:**
Status contract:
```bash
python3 scripts/creative_refactor_cli.py --json status \
  --run-id cli_v2_hp_two_game_20260429
```

Result contract:
```bash
python3 scripts/creative_refactor_cli.py --json result \
  --run-id cli_v2_hp_two_game_20260429
```

Final production run state:
```json
{
  "status": "transform_completed",
  "current_phase": "parallel_batch_finished",
  "games_total": 2,
  "games_transform_completed": 2,
  "games_transform_failed": 0
}
```

Final result payload:
```json
{
  "run_id": "cli_v2_hp_two_game_20260429",
  "status": "transform_completed",
  "completed": true,
  "final_output_dirs": [
    ".../output/08a032f7-6c39-461b-9cf1-03c117c12b6b",
    ".../output/25b14fff-43f9-452a-8820-54d8056bfe84"
  ]
}
```

**Status:** Complete

---

## 🐛 Known Issues

No known issues at scaffold start.

---

## 📚 Quick Reference

### Key Files

**Documentation:**
- `docs/journals/operator-pipeline-v2.md` - This implementation journal
- `docs/operator_pipeline_manual.md` - Operator pipeline v2 architecture and workflow manual
- `docs/journals/formal-creative-refactor-cli-followup.md` - Known-good production baseline reference

**Production Files Preserved:**
- `scripts/spec_adaptor.py` - Existing run-level spec adaptor
- `scripts/generate_task_packet.py` - Existing production task packet builder
- `scripts/run_single_game.py` - Existing per-game production worker runner
- `scripts/run_parallel_batch.py` - Existing production batch runner
- `scripts/creative_refactor_cli.py` - Existing production CLI

**New v2 Lab Files:**
- `configs/operator_pipeline_v2.json` - Stage registry config
- `scripts/operator_registry_v2.py` - Registry loader and validation helpers
- `scripts/operator_pipeline_lab.py` - Fixture-first dry-run lab CLI
- `prompts/operators_v2/` - Operator prompt skeletons
- `fixtures/operator_pipeline_lab/harry_potter/` - Fixture lab metadata

### Important Commands

```bash
python3 -m py_compile \
  scripts/operator_registry_v2.py \
  scripts/operator_pipeline_lab.py

python3 -m json.tool configs/operator_pipeline_v2.json >/dev/null
python3 -m json.tool fixtures/operator_pipeline_lab/harry_potter/lab_manifest.json >/dev/null

python3 scripts/operator_pipeline_lab.py --help
python3 scripts/operator_pipeline_lab.py inspect-registry
python3 scripts/operator_pipeline_lab.py dry-run --fixture harry_potter --step audio_integration
python3 scripts/operator_pipeline_lab.py dry-run --fixture harry_potter --through final_code_ui_mobile_repair
```

---

## 💭 Notes & Decisions

### Fixture-First Lab Boundary

**Decision:** Develop operator pipeline v2 under `fixtures/operator_pipeline_lab/` rather than replacing production orchestration.

**Rationale:** The production prompt-aware CLI path was just revalidated and is healthy. The v2 operator sequence needs staged experimentation, retry semantics, and resumable artifacts without destabilizing the existing batch flow.

**Alternatives Considered:** Extending `run_parallel_batch.py` or `run_single_game.py` directly was rejected for this milestone because it would risk changing known-good production behavior.

### Dry-Run First

**Decision:** Initial runner validates and prints plans only. It does not invoke Cline, create production runs, or mutate production outputs.

**Rationale:** Registry shape, prompt paths, fixture paths, stage ordering, and artifact contracts should be stabilized before live execution.

### Future Resume Model

**Decision:** Reserve resume-capable state files and deterministic stage directories now.

**Rationale:** Live fixture execution should be able to resume from the latest successful workspace, rerun a stage, retry a failed stage with accumulated context, or continue through a selected stage range.

---

## ✅ Testing Checklist

- [x] Registry loader compiles
- [x] Lab runner compiles
- [x] Registry JSON validates
- [x] Fixture manifest JSON validates
- [x] Help command works
- [x] Registry inspection works
- [x] Dry-run by single step works
- [x] Dry-run through final stage works
- [x] Production files remain unmodified
- [x] Lab runner compiles after `init-run` / `inspect-run`
- [x] Lab-local run initialization works
- [x] Lab-local run inspection works
- [x] Generated lab runs are ignored by git
- [x] Lab runner compiles after `build-prompt`
- [x] Prompt packet generation works
- [x] Generated invocation/stage JSON validates
- [x] Generated operator prompt is non-empty
- [x] Lab runner compiles after guarded `run-step`
- [x] `run-step` refuses execution without `--execute`
- [x] `run-progressive` refuses execution without `--execute`
- [x] Lab runner compiles after promotion support
- [x] Manual `promote-attempt` works with completed result
- [x] Promoted stage is reflected in `inspect-run`
- [x] Lab runner compiles after progressive orchestration
- [x] `run-progressive` refuses execution without `--execute`
- [x] `run-progressive` skips completed stages
- [x] First live one-game progressive run completed
- [x] Live run completed 4 / 4 operator stages
- [x] Live run produced final `pipeline/current/` workspace
- [x] Four-game manifest JSON validates
- [x] Four-game lab run initializes
- [x] `run-fixture` refuses execution without `--execute`
- [x] `summarize-run` prints resume-oriented status
- [x] Four-game live run completed game 1
- [x] Four-game live run completed game 2
- [x] Four-game live run completed game 3
- [x] Four-game live run completed game 4
- [x] Four-game live run completed 4 / 4 games
- [x] Four-game live run completed 16 / 16 stages
- [x] Production CLI v2 smoke run completed 2 / 2 games
- [x] Production CLI `status` contract verified
- [x] Production CLI `result` contract verified
- [x] Production v2 stale heartbeat handling is v2-aware

---

## 🎯 Success Criteria

- [x] All requested scaffold files created
- [x] Documentation gives a fresh agent enough context
- [x] Registry validation catches malformed config
- [x] Dry-run resolves operator selections and prints planned artifacts
- [x] Fixture references validate against existing repository paths
- [x] Verification command set passes
- [x] Production behavior remains untouched
- [x] Lab-local game workspaces initialize under fixture-local `runs/`
- [x] Lab-local state is inspectable via `inspect-run`
- [x] Generated lab run artifacts are protected from accidental commit
- [x] Operator prompt packets can be generated without worker execution
- [x] Stage attempt workspaces are created from `pipeline/current/`
- [x] Prompt packet metadata is persisted for future worker execution
- [x] Guarded single-stage worker execution path is implemented
- [x] Worker execution remains opt-in via `--execute`
- [x] Progressive execution remains deferred until multi-stage orchestration
- [x] Completed attempts can be promoted to `pipeline/current/`
- [x] Promotion metadata is persisted in `lab_run_state.json`
- [x] Progressive one-game orchestration is implemented
- [x] Progressive resume from stage is supported
- [x] Progressive retry loop is bounded by registry retry count
- [x] One-game live v2 staged pipeline completed inside fixture lab
- [x] Live run artifacts stayed under git-ignored fixture-local run directory
- [x] Final workspace retained start/audio/theme markers
- [x] Four-game source manifest override works
- [x] Fixture-level orchestration command is implemented
- [x] Fixture run summary support is available
- [x] Long fixture runs can be monitored and resumed by game/stage
- [x] Four-game v2 lab run completed without failed games
- [x] Main CLI now launches v2 by default
- [x] Production stale heartbeat logic is compatible with v2 paths
