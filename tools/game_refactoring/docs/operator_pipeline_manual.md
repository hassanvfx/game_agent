# Operator Pipeline Manual

## Purpose

This document describes the operator-pipeline architecture currently preserved in `game_refactoring`.

The code remains the source of truth. This manual exists to explain the intended staged pipeline model, operator responsibilities, and architectural boundaries while the repository is being cleaned up and re-framed away from legacy `game_remix_editor` / `game_remixer` branding.

The current production path remains the source of truth for real transformations:

```text
creative_refactor_cli.py
  -> run_parallel_batch.py
  -> spec_adaptor.py
  -> run_single_game.py workers
```

The intended operator-pipeline structure is:

```text
[Run-level spec adaptor once]
          |
          v
[Per-game operator pipeline]
          |
          +--> 1. Gameplay + narrative adaptation
          +--> 2. Theme / visual identity / emoji rebranding
          +--> 3. Media mapper
          +--> 4. Final code/UI/mobile repair
```

Some supporting fixtures and helper paths in the repository still reflect a lab or dry-run origin. Those areas should be treated as experimental or transitional scaffolding, not as the canonical architectural identity of the project.

---

## Baseline

The v2 scaffold starts from a known-good production run:

```text
run_id: cli_prompt_hp_known_state_20260429
run_dir: runs/cli_prompt_hp_known_state_20260429
manifest: fixtures/harry_potter_two_game_manifest.json
style: neutral_prototype
prompt: make it harry potter like with flappy bird gameplay
model: gpt-5.4
```

Final production status:

```text
status: transform_completed
current_phase: parallel_batch_finished
games_total: 2
games_transform_completed: 2
games_transform_failed: 0
completed: true
failed: false
```

Spec adaptor status:

```text
spec_adaptor.status: ready
recomposition_summary_present: true
remix_identity_present: true
failure_reason: null
```

The baseline is documented in:

```text
docs/journals/formal-creative-refactor-cli-followup.md
```

---

## Production Boundaries

This documentation cleanup pass must not modify production behavior.

Do not change these production files unless a future task explicitly requests it:

```text
scripts/run_single_game.py
scripts/run_parallel_batch.py
scripts/creative_refactor_cli.py
scripts/generate_task_packet.py
scripts/spec_adaptor.py
```

The production spec adaptor remains run-level:

```text
style preset + user remix prompt
        |
        v
run_dir/spec_adaptor/adapted/
```

Architecture rule:

```text
spec adaptor = one writer per run
game workers = many readers
```

The operator pipeline preserves this rule. The adapted spec is treated as read-only shared input for per-game operators.

---

## Fixture-First Workflow

Some pipeline development and validation paths use fixture manifests under:

```text
fixtures/operator_pipeline_lab/<fixture_id>/
```

The Harry Potter fixture lives at:

```text
fixtures/operator_pipeline_lab/harry_potter/
```

The fixture manifest declares:

- known-good production run reference
- source game manifest
- optional extended manifest
- adapted spec directory
- audio catalog path
- emoji asset root
- default style and remix prompt
- expected game IDs

The fixture-oriented runner validates these paths before planning any stage.

Execution paths that use isolated workspaces should copy source game code into workspace-local directories and mutate only those workspaces. They must not mutate:

- original source fixtures
- production `runs/` outputs
- production orchestration scripts

---

## Operator Responsibilities

### 1. Gameplay + Narrative Adaptation

Operator ID:

```text
gameplay_narrative
```

Stage slug:

```text
stage_01_gameplay_narrative
```

Responsibilities:

- adapt objective, framing, story, labels, and copy
- reinterpret the remix prompt into the existing gameplay context
- preserve mechanics, controls, boot flow, and win/loss conditions
- avoid heavy visual/audio work

### 2. Character-First Visual Identity

Operator ID:

```text
visual_emoji_identity
```

Stage slug:

```text
stage_02_visual_emoji_identity
```

Responsibilities:

- apply character-first visual identity and theme direction
- invest the most effort in making the main playable character memorable and polished
- derive enemies, hazards, collectibles, props, backgrounds, and UI from that character's visual language
- use canvas, CSS shapes, procedural drawing, and emojis where practical
- preserve mechanics and controls
- avoid audio work
- avoid media mapping and whitelist/compliance work

### 3. Media Mapper

Operator ID:

```text
media_mapper
```

Stage slug:

```text
stage_03_media_mapper
```

Responsibilities:

- use workspace-local approved catalogs under `catalogs/`
- use approved references from `catalogs/audios.json`
- use approved references from `catalogs/gifs.json`
- use approved references from `catalogs/sprites.json`
- use approved references from `catalogs/fonts.json` when mapped font/icon plumbing is needed
- replace or remove unapproved external media URLs where practical
- perform actual mapping/import plumbing so approved assets are wired into the game
- ensure mapped assets appear in the game when the code structure allows it
- add semantic one-shots or loops where practical
- keep playback non-blocking
- do not make gameplay depend on audio playback
- preserve mechanics and controls

### 4. Final Code/UI/Mobile Repair

Operator ID:

```text
final_code_ui_mobile_repair
```

Stage slug:

```text
stage_04_final_code_ui_mobile_repair
```

Responsibilities:

- repair code after creative/media passes
- improve readability
- optimize mobile safe zones and responsive layout
- own typography hierarchy, icon polish, and premium mobile UI cleanup
- minimize, dismiss, fade, or collapse instructional overlays during active play
- act as the final doctor/fix pass for runtime and layout issues
- keep controls unobstructed
- preserve mechanics, controls, boot flow, and win/loss conditions

---

## Shared Operator Contract

Every operator prompt uses this stdout contract:

```text
OPERATOR STATUS: completed|failed
CHANGED FILES: file1, file2 or NONE
SUMMARY: one short sentence
MECHANICS CHECK: preserved|issues
VISUAL CHECK: preserved|updated|issues
AUDIO CHECK: integrated|not_applicable|issues
MOBILE CHECK: safe|not_checked|issues
```

Shared rules:

```text
- edit only the provided working clone path
- preserve boot flow
- preserve controls
- preserve win/loss conditions
- do not replace project from scratch
- do not modify files outside workspace
- do not depend on audio playback for gameplay
```

The lab runner will eventually parse this stdout contract into `operator_result.json`.

---

## Registry Config

The stage registry lives at:

```text
configs/operator_pipeline_v2.json
```

Shape:

```json
{
  "pipeline_id": "operator_pipeline_v2",
  "max_retries_per_stage": 3,
  "default_agent_timeout_seconds": 3600,
  "operators": [
    {
      "id": "gameplay_narrative",
      "stage_number": 1,
      "prompt": "prompts/operators_v2/01_gameplay_narrative.md",
      "summary_required": true
    }
  ]
}
```

Registry loader responsibilities:

- load JSON config
- validate unique operator IDs
- validate sequential stage numbers
- validate prompt files exist
- resolve one operator by step ID
- resolve operators through a selected final step
- expose deterministic stage slugs such as `stage_03_media_mapper`

---

## Lab Runner Commands

Registry and dry-run commands:

```bash
python3 scripts/operator_pipeline_lab.py --help

python3 scripts/operator_pipeline_lab.py inspect-registry

python3 scripts/operator_pipeline_lab.py dry-run \
  --fixture harry_potter \
  --step media_mapper

python3 scripts/operator_pipeline_lab.py dry-run \
  --fixture harry_potter \
  --through final_code_ui_mobile_repair
```

Lab-local run initialization commands:

```bash
python3 scripts/operator_pipeline_lab.py init-run \
  --fixture harry_potter

python3 scripts/operator_pipeline_lab.py init-run \
  --fixture harry_potter \
  --lab-run-id opv2_example

python3 scripts/operator_pipeline_lab.py init-run \
  --fixture harry_potter \
  --source-manifest fixtures/harry_potter_four_game_manifest.json \
  --lab-run-id opv2_live_four_game_20260429

python3 scripts/operator_pipeline_lab.py inspect-run \
  --fixture harry_potter \
  --lab-run-id opv2_example

python3 scripts/operator_pipeline_lab.py summarize-run \
  --fixture harry_potter \
  --lab-run-id opv2_example
```

`init-run` creates copied fixture workspaces under the fixture lab path and writes `lab_run_state.json`. It still does not invoke workers or create production runs. `--source-manifest` can override the default fixture game list while retaining the same adapted spec/audio/emoji context. `summarize-run` prints a resume-oriented view with completed/pending stages and recommended resume commands.

Prompt packet generation command:

```bash
python3 scripts/operator_pipeline_lab.py build-prompt \
  --fixture harry_potter \
  --lab-run-id opv2_example \
  --game-id 25b14fff-43f9-452a-8820-54d8056bfe84 \
  --step media_mapper \
  --attempt 1
```

`build-prompt` creates a stage attempt workspace and writes `operator_prompt.txt`, `operator_invocation.json`, and `operator_stage_state.json`. It still does not invoke workers or create production runs.

Execution-facing commands are guarded:

```bash
python3 scripts/operator_pipeline_lab.py run-step \
  --fixture harry_potter \
  --lab-run-id opv2_example \
  --game-id 25b14fff-43f9-452a-8820-54d8056bfe84 \
  --step media_mapper \
  --attempt 1 \
  --execute

python3 scripts/operator_pipeline_lab.py run-progressive \
  --fixture harry_potter \
  --lab-run-id opv2_example \
  --game-id 25b14fff-43f9-452a-8820-54d8056bfe84 \
  --through final_code_ui_mobile_repair \
  --execute

python3 scripts/operator_pipeline_lab.py run-fixture \
  --fixture harry_potter \
  --lab-run-id opv2_live_four_game_20260429 \
  --through final_code_ui_mobile_repair \
  --model gpt-5.4 \
  --agent-timeout 900 \
  --execute
```

Safety rule:

```text
run-step and run-progressive must refuse real worker execution unless --execute is passed.
```

`run-step` is implemented for a previously prepared prompt packet. It reuses `execute_worker_command()` and writes stdout/stderr/result/state artifacts. Successful `run-step` executions automatically promote the attempt workspace back to `pipeline/current/`.

Manual promotion is also available for completed attempts:

```bash
python3 scripts/operator_pipeline_lab.py promote-attempt \
  --fixture harry_potter \
  --lab-run-id opv2_example \
  --game-id 25b14fff-43f9-452a-8820-54d8056bfe84 \
  --step media_mapper \
  --attempt 1
```

`run-progressive` remains a guarded placeholder until multi-stage orchestration is implemented.

---

## Lab-Local Run Initialization

`init-run` is the first live-code lab milestone. It creates a resumable lab run without running operators.

For each expected fixture game, it copies the source workspace from the source manifest into:

```text
fixtures/operator_pipeline_lab/harry_potter/runs/<lab_run_id>/games/<game_id>/input/
fixtures/operator_pipeline_lab/harry_potter/runs/<lab_run_id>/games/<game_id>/pipeline/current/
```

The `input/` copy is the immutable lab-local snapshot for comparison. The `pipeline/current/` copy is the mutable latest-good workspace that future stage attempts will copy from and promote back into.

The run state is written to:

```text
fixtures/operator_pipeline_lab/harry_potter/runs/<lab_run_id>/lab_run_state.json
```

The state tracks:

- lab run id
- fixture id
- pipeline id
- source/adapted spec/audio/emoji references
- safety flags showing no production runs or worker invocations
- per-game input/current workspace paths
- per-game initialized stage state
- completed/failed stage lists reserved for future resume

Generated lab runs are ignored by git via:

```text
fixtures/operator_pipeline_lab/*/runs/
```

---

## Operator Prompt Packet Generation

`build-prompt` bridges lab-local workspace initialization and future worker execution.

For one game, one operator stage, and one attempt, it:

1. Resolves the operator from the registry.
2. Loads `lab_run_state.json`.
3. Finds the selected game and stage state.
4. Copies the latest-good `pipeline/current/` workspace into the stage attempt workspace.
5. Builds a complete operator prompt packet from:
   - lab run metadata
   - game metadata
   - fixture paths
   - adapted spec path
   - audio catalog path
   - emoji asset root
   - operator prompt skeleton
   - required stdout contract
   - retry context placeholder
6. Writes invocation and stage-state metadata.
7. Updates `lab_run_state.json` with the prompt-built attempt.

Generated files:

```text
games/<game_id>/pipeline/<stage_slug>/attempt_01/
  workspace/
  operator_prompt.txt
  operator_invocation.json
  operator_stage_state.json
```

Safety behavior:

```text
invokes_workers: false
invokes_cline: false
creates_production_runs: false
```

Retry-safe behavior:

- existing attempt directories are never overwritten
- use `--attempt 2` or `--attempt 3` for later retry attempts
- future retry prompts can include previous attempt stdout/stderr/result context

---

## Guarded Single-Stage Worker Execution

`run-step` is the first live worker execution path in the lab, and it is intentionally narrow.

Requirements:

1. A lab run must already exist.
2. A stage attempt must already be prepared with `build-prompt`.
3. The command must include `--execute`.

Without `--execute`, `run-step` refuses execution:

```bash
python3 scripts/operator_pipeline_lab.py run-step \
  --fixture harry_potter \
  --lab-run-id opv2_example \
  --game-id 25b14fff-43f9-452a-8820-54d8056bfe84 \
  --step media_mapper \
  --attempt 1
```

Execution command shape:

```bash
python3 scripts/operator_pipeline_lab.py run-step \
  --fixture harry_potter \
  --lab-run-id opv2_example \
  --game-id 25b14fff-43f9-452a-8820-54d8056bfe84 \
  --step media_mapper \
  --attempt 1 \
  --model gpt-5.4 \
  --execute
```

Runtime behavior:

- reads `operator_prompt.txt`
- runs `cline` inside the attempt workspace
- streams stdout to `operator_stdout.txt`
- streams stderr to `operator_stderr.txt`
- heartbeats `operator_stage_state.json`
- parses the shared operator stdout contract
- writes `operator_result.json`
- updates attempt metadata in `lab_run_state.json`

Successful `run-step` executions promote the completed attempt workspace to `pipeline/current/`. If a completed result already exists, `promote-attempt` can promote it manually without invoking a worker.

`run-progressive` now sequences one game's selected operators with retries and promotion. It remains guarded and refuses execution unless `--execute` is provided.

---

## Progressive One-Game Orchestration

`run-progressive` automates the stage loop for one game.

Command shape:

```bash
python3 scripts/operator_pipeline_lab.py run-progressive \
  --fixture harry_potter \
  --lab-run-id opv2_example \
  --game-id 25b14fff-43f9-452a-8820-54d8056bfe84 \
  --through final_code_ui_mobile_repair \
  --model gpt-5.4 \
  --execute
```

Resume from a specific stage:

```bash
python3 scripts/operator_pipeline_lab.py run-progressive \
  --fixture harry_potter \
  --lab-run-id opv2_example \
  --game-id 25b14fff-43f9-452a-8820-54d8056bfe84 \
  --from-stage media_mapper \
  --through final_code_ui_mobile_repair \
  --execute
```

Behavior:

1. Loads registry and lab run state.
2. Resolves operators through `--through`.
3. Optionally filters the sequence from `--from-stage`.
4. Skips stages already listed in `completed_stages`.
5. For each incomplete stage:
   - builds an attempt prompt if missing
   - runs the attempt through guarded `run-step`
   - promotes on success
   - retries up to `max_retries_per_stage`
6. Marks the stage/game/run failed if all attempts fail.
7. Leaves all artifacts under the fixture-local ignored `runs/` directory.

---

## Run Monitoring and Resume Summary

`summarize-run` is the preferred command for long fixture runs because the host shell can time out before all games finish.

Command:

```bash
python3 scripts/operator_pipeline_lab.py summarize-run \
  --fixture harry_potter \
  --lab-run-id opv2_live_four_game_20260429
```

It prints:

- lab run id and artifact root
- per-game completed stage count
- failed stage count
- current stage
- latest attempt state/result per stage
- heartbeat timestamps for running attempts
- a recommended `run-progressive` resume command for each incomplete game

This is especially useful when a parent `run-fixture` shell is killed by an external timeout. The run artifacts remain valid, and the next game/stage can be resumed with the printed command.

---

## Multi-Game Fixture Orchestration

`run-fixture` runs one-game progressive orchestration across selected games in an initialized lab run.

Command shape:

```bash
python3 scripts/operator_pipeline_lab.py run-fixture \
  --fixture harry_potter \
  --lab-run-id opv2_live_four_game_20260429 \
  --through final_code_ui_mobile_repair \
  --model gpt-5.4 \
  --agent-timeout 900 \
  --execute
```

Single-game filtering for resume or smoke tests:

```bash
python3 scripts/operator_pipeline_lab.py run-fixture \
  --fixture harry_potter \
  --lab-run-id opv2_live_four_game_20260429 \
  --game-id 5b273ca9-6828-4560-a0a8-e56cec6780f8 \
  --through final_code_ui_mobile_repair \
  --execute
```

Behavior:

- loads all games from `lab_run_state.json`
- optionally filters to `--game-id`
- calls `run-progressive` for each selected game
- supports `--from-stage` for per-game resume
- supports `--fail-fast`
- writes `fixture_run_summary` into `lab_run_state.json`
- prints aggregate attempted/completed/failed counts

Generated artifacts remain under the git-ignored fixture-local `runs/` directory.

---

## Promotion Model

Promotion moves a completed stage attempt into the latest-good workspace.

Promotable attempt requirements:

- `operator_result.json` exists
- `operator_result.json.status` is `completed`
- attempt `workspace/` exists

Manual promotion command:

```bash
python3 scripts/operator_pipeline_lab.py promote-attempt \
  --fixture harry_potter \
  --lab-run-id opv2_example \
  --game-id 25b14fff-43f9-452a-8820-54d8056bfe84 \
  --step media_mapper \
  --attempt 1
```

Promotion behavior:

- replaces `games/<game_id>/pipeline/current/` with the attempt workspace
- marks the attempt as `promoted`
- marks the stage as `completed`
- records the promoted attempt number
- appends the stage slug to `completed_stages`
- removes the stage from `failed_stages` if present

This keeps `pipeline/current/` as the source for the next stage attempt.

`run-progressive` is still deferred; the next milestone will automate stage sequencing and retry decisions.

---

## Dry-Run Behavior

Dry-run mode must:

- load the selected fixture manifest
- load and validate the registry
- resolve selected operators
- print planned stages
- print planned artifact paths
- print retry count
- validate referenced prompt/spec/audio/emoji paths
- avoid production run creation
- avoid Cline or worker invocation

Dry-run mode is safe to run repeatedly.

---

## Artifact Layout

The planned future live-execution layout is:

```text
fixtures/operator_pipeline_lab/harry_potter/runs/<lab_run_id>/
  lab_run_state.json
  games/<game_id>/
    input/
    pipeline/
      current/
      stage_01_gameplay_narrative/
        attempt_01/
          workspace/
          operator_stage_state.json
          operator_prompt.txt
          operator_stdout.txt
          operator_stderr.txt
          operator_result.json
          operator_invocation.json
      stage_02_visual_emoji_identity/
      stage_03_media_mapper/
      stage_04_final_code_ui_mobile_repair/
```

Each stage supports:

```text
attempt_01
attempt_02
attempt_03
```

The dry-run runner prints these planned paths without creating a production run.

---

## Retry Model

Future live execution should follow this model:

```text
for stage in operators:
  for attempt in 1..max_retries_per_stage:
    copy previous good workspace
    build operator prompt
    run worker
    heartbeat stage state
    capture stdout/stderr
    if success:
      promote workspace to pipeline/current
      break
    else:
      accumulate retry context
  if all attempts fail:
    mark stage failed
    stop pipeline
```

The existing runtime helper `execute_worker_command()` from `scripts/creative_refactor_runtime.py` should be reused for future worker execution. No second subprocess system is needed.

---

## Resume Model

The artifact contract is designed so future execution can resume from arbitrary parts.

Supported future resume concepts:

### Resume whole pipeline from latest good stage

```text
pipeline/current/ = latest promoted good workspace
continue at next incomplete stage
```

### Resume a specific game

```bash
run-progressive --fixture harry_potter --game-id <game_id> --execute
```

### Resume from a specific stage

```bash
run-progressive --fixture harry_potter --from-stage media_mapper --execute
```

### Re-run one stage from current

```bash
run-step --fixture harry_potter --step media_mapper --execute
```

### Retry a failed stage with context

```text
attempt_01/operator_stdout.txt
attempt_01/operator_stderr.txt
attempt_01/operator_result.json
        |
        v
attempt_02 prompt includes retry context
```

### Fork from a previous good stage

```text
stage_02 successful workspace
        |
        v
new stage_03 attempt
```

This first scaffold reserves these concepts in docs and planned output. It does not yet implement live resume mutation.

---

## Verification

Primary verification command set:

```bash
python3 -m py_compile \
  scripts/operator_registry_v2.py \
  scripts/operator_pipeline_lab.py

python3 scripts/operator_pipeline_lab.py --help

python3 scripts/operator_pipeline_lab.py inspect-registry

python3 scripts/operator_pipeline_lab.py dry-run \
  --fixture harry_potter \
  --step media_mapper

python3 scripts/operator_pipeline_lab.py dry-run \
  --fixture harry_potter \
  --through final_code_ui_mobile_repair
```

Lab-local initialization verification:

```bash
python3 scripts/operator_pipeline_lab.py init-run \
  --fixture harry_potter \
  --lab-run-id opv2_milestone2_verify_20260429

python3 scripts/operator_pipeline_lab.py inspect-run \
  --fixture harry_potter \
  --lab-run-id opv2_milestone2_verify_20260429
```

Prompt packet verification:

```bash
python3 scripts/operator_pipeline_lab.py build-prompt \
  --fixture harry_potter \
  --lab-run-id opv2_milestone2_verify_20260429 \
  --game-id 25b14fff-43f9-452a-8820-54d8056bfe84 \
  --step media_mapper \
  --attempt 1

python3 -m json.tool \
  fixtures/operator_pipeline_lab/harry_potter/runs/opv2_milestone2_verify_20260429/games/25b14fff-43f9-452a-8820-54d8056bfe84/pipeline/stage_03_media_mapper/attempt_01/operator_invocation.json \
  >/dev/null

python3 -m json.tool \
  fixtures/operator_pipeline_lab/harry_potter/runs/opv2_milestone2_verify_20260429/games/25b14fff-43f9-452a-8820-54d8056bfe84/pipeline/stage_03_media_mapper/attempt_01/operator_stage_state.json \
  >/dev/null

test -s \
  fixtures/operator_pipeline_lab/harry_potter/runs/opv2_milestone2_verify_20260429/games/25b14fff-43f9-452a-8820-54d8056bfe84/pipeline/stage_03_media_mapper/attempt_01/operator_prompt.txt
```

Guard verification without invoking workers:

```bash
python3 scripts/operator_pipeline_lab.py run-step \
  --fixture harry_potter \
  --lab-run-id opv2_milestone2_verify_20260429 \
  --game-id 25b14fff-43f9-452a-8820-54d8056bfe84 \
  --step media_mapper \
  --attempt 1 \
  2>&1 | grep -q "refuses real worker execution unless --execute is passed"

python3 scripts/operator_pipeline_lab.py run-progressive \
  --fixture harry_potter \
  --lab-run-id opv2_milestone2_verify_20260429 \
  --game-id 25b14fff-43f9-452a-8820-54d8056bfe84 \
  --through final_code_ui_mobile_repair \
  2>&1 | grep -q "refuses real worker execution unless --execute is passed"
```

Promotion verification with synthetic completed result:

```bash
python3 scripts/operator_pipeline_lab.py promote-attempt \
  --fixture harry_potter \
  --lab-run-id opv2_milestone2_verify_20260429 \
  --game-id 25b14fff-43f9-452a-8820-54d8056bfe84 \
  --step media_mapper \
  --attempt 1

python3 scripts/operator_pipeline_lab.py inspect-run \
  --fixture harry_potter \
  --lab-run-id opv2_milestone2_verify_20260429
```

Progressive orchestration guard and skip verification:

```bash
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
  --from-stage media_mapper \
  --through media_mapper \
  --execute
```

The second command uses the synthetic already-completed media-mapper stage and verifies progressive orchestration can skip completed stages without launching a new worker.

Four-game fixture and `run-fixture` verification:

```bash
python3 -m json.tool fixtures/harry_potter_four_game_manifest.json >/dev/null

python3 scripts/operator_pipeline_lab.py init-run \
  --fixture harry_potter \
  --source-manifest fixtures/harry_potter_four_game_manifest.json \
  --lab-run-id opv2_live_four_game_20260429

python3 scripts/operator_pipeline_lab.py inspect-run \
  --fixture harry_potter \
  --lab-run-id opv2_live_four_game_20260429

python3 scripts/operator_pipeline_lab.py summarize-run \
  --fixture harry_potter \
  --lab-run-id opv2_live_four_game_20260429

python3 scripts/operator_pipeline_lab.py run-fixture \
  --fixture harry_potter \
  --lab-run-id opv2_live_four_game_20260429 \
  --through final_code_ui_mobile_repair \
  2>&1 | grep -q "refuses real worker execution unless --execute is passed"
```

Optional JSON validation:

```bash
python3 -m json.tool configs/operator_pipeline_v2.json >/dev/null
python3 -m json.tool fixtures/operator_pipeline_lab/harry_potter/lab_manifest.json >/dev/null
```

---

## Non-Goals

This milestone does not:

- replace production creative refactor flow
- modify production orchestration files
- add Playwright verification after each stage
- run real v2 operators by default
- introduce a second production orchestration engine
- parse real operator output from live workers
- integrate v2 into the production creative refactor path

The goal is a safe, inspectable scaffold for the next development unit.