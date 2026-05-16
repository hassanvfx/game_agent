# Harry Potter Operator Pipeline v2 Lab Fixture

This fixture is the first fixture-first lab target for Operator Pipeline v2.

It uses the known-good prompt-aware production CLI run as a baseline while keeping all v2 operator development isolated from production orchestration.

## Known-Good Baseline

```text
run_id: cli_prompt_hp_known_state_20260429
run_dir: runs/cli_prompt_hp_known_state_20260429
source_manifest: fixtures/harry_potter_two_game_manifest.json
style: neutral_prototype
prompt: make it harry potter like with flappy bird gameplay
```

The baseline completed successfully:

```text
status: transform_completed
games_transform_completed: 2
games_transform_failed: 0
spec_adaptor.status: ready
```

## Fixture Purpose

This fixture lets the v2 lab runner validate and later exercise staged operators safely:

```text
1. gameplay_narrative
2. visual_emoji_identity
3. audio_integration
4. final_code_ui_mobile_repair
```

The fixture references existing assets and adapted specs. It does not replace production output and does not mutate production runs.

## Dry-Run Examples

Inspect the registry:

```bash
python3 scripts/operator_pipeline_lab.py inspect-registry
```

Plan only the audio stage:

```bash
python3 scripts/operator_pipeline_lab.py dry-run \
  --fixture harry_potter \
  --step audio_integration
```

Plan all stages through final repair:

```bash
python3 scripts/operator_pipeline_lab.py dry-run \
  --fixture harry_potter \
  --through final_code_ui_mobile_repair
```

## Future Execution Model

Future live execution should create lab-local run directories under:

```text
fixtures/operator_pipeline_lab/harry_potter/runs/<lab_run_id>/
```

Operators should edit only copied workspaces inside that lab run. Arbitrary resume should be driven by:

```text
lab_run_state.json
games/<game_id>/pipeline/current/
games/<game_id>/pipeline/<stage_slug>/<attempt_slug>/
```

Production files and production runs remain read-only inputs for this lab fixture.