# game_refactoring

## Overview and pipeline position

This is the AI transformation engine. It accepts source-game manifests, launches
named workflows or operator pipelines, tracks per-game execution, and exposes
status and final output directories for downstream publishing.

```text
game_generator ----+
                   |
game_editorial ----+--> source manifest + workflow / remix prompt
                   |                     |
API / manual CLI --+                     v
                              per-game operator execution
                              AI agent + assets + browser tools
                                         |
                              run state / events / dashboard
                                         |
                              result: final_output_dirs
                                         |
                              game_publish_pipeline
```

The generator currently selects `creative_remix_v5`; other named workflows are
defined in `scripts/game_workflow.py`. Copy mode prepares run-local sources, while
inplace mode works against source directories. Configure the AI runtime and browser
requirements before real runs; concurrency, timeouts, and heartbeat options are
available on the CLI.

All commands below run from `tools/game_refactoring/`. To launch the named workflow
used by the generator:

```bash
python3 scripts/game_workflow.py --json --id creative_remix_v5 \
  --games-manifest-source /absolute/path/to/games_manifest.json \
  --remix-prompt "a neon arcade remix"
```

The source manifest contains a `games` array with `game_id`, `display_name`, and
`source_path` entries. Use the returned run ID to poll status and resolve results.
Publishing is handled by the [publish pipeline](../game_publish_pipeline/README.md).
See also the [launch manual](../../GAME_REFACTORING_LAUNCH_MANUAL.md).

Operator-pipeline CLI repository for creative refactor/transformation runs.

## Primary CLI

Main command surface:

```bash
python3 scripts/creative_refactor_cli.py <mode> [...args]
```

Modes implemented in parser:

- `replay`
- `pipeline`
- `start-batch`
- `status`
- `result`
- `finish` (alias of `result`)
- `kill-all`

Global output option:

- `--json`

## Most used orchestration modes

### Start batch

```bash
python3 scripts/creative_refactor_cli.py --json start-batch --manifest /path/to/manifest.json
```

Important args:

- `--manifest` (required)
- `--run-id`
- `--runs-root`
- `--source-mode` (`copy` or `inplace`)
- `--pipeline` (`v2` or `legacy`)
- `--model`
- `--agent-timeout`
- `--max-concurrency`
- `--poll-seconds`
- `--stale-heartbeat-seconds`
- `--remix-prompt` / `--remix-prompt-file`
- `--dry-run-operators`
- `--dry-run-spec-adaptor`

### Poll status

```bash
python3 scripts/creative_refactor_cli.py --json status --run-id <run_id>
```

### Resolve result/final output contract

```bash
python3 scripts/creative_refactor_cli.py --json result --run-id <run_id>
python3 scripts/creative_refactor_cli.py --json finish --run-id <run_id>
```

### Kill active related processes

```bash
python3 scripts/creative_refactor_cli.py --json kill-all --dry-run
```

## Supporting scripts (repo-owned)

- `scripts/game_workflow.py`
- `scripts/run_operator_pipeline_batch.py`
- `scripts/run_operator_pipeline_game.py`
- `scripts/build_dashboard.py`
- `scripts/serve_dashboard.py`

## Architecture boundary

`game_refactoring` owns run creation, per-game/operator orchestration, status/result contracts, and run-local outputs (`runs/<run_id>`). It is upstream of publish/obfuscation stages.
