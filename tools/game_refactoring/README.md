# game_refactoring

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
