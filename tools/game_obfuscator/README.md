# game_obfuscator

## Overview and pipeline position

This tool transforms packaged HTML/JavaScript/CSS into obfuscated and minified game
outputs. The publish pipeline calls its synchronous `start` contract and consumes
the resulting run/output metadata.

```text
public bundles from game_deploy
              |
manifest: source_path + output_path
              |
     synchronous start command
              |
     obfuscation / minification
              |
obfuscated game folders + run state + terminal JSON
              |
     game_publish_pipeline -> artifact refresh / optional sync
```

Inputs are game manifests; output locations come from the manifest and CLI options.
Node dependencies are declared in `package.json`; install them with `npm install`
inside this tool directory before running the transformation locally. Status and
output-path commands inspect recorded runs after execution.

All commands below run from `tools/game_obfuscator/`. From the repository root,
prefix script paths with `tools/game_obfuscator/`.

See the [publish pipeline](../game_publish_pipeline/README.md) and
[workspace overview](../../README.md).

CLI tool for deterministic obfuscation/minification runs over a manifest of games.

## Primary contract (sync)

Main entrypoint:

```bash
python3 scripts/game_obfuscator_cli.py start --manifest manifests/example.json
```

`start` is synchronous in current implementation: it runs the simple pipeline and returns terminal JSON.

Optional args:

- `--manifest` (required)
- `--run-id` (optional explicit run id)
- `--output-root` (optional explicit output root)

## Secondary diagnostic commands

These commands still exist, but are secondary introspection surfaces:

```bash
python3 scripts/game_obfuscator_cli.py status --run-id <run_id>
python3 scripts/game_obfuscator_cli.py output-path --run-id <run_id> --include-games
```

## Pipeline scripts referenced by the CLI

- `scripts/create_run.py`
- `scripts/run_game_obfuscator_simple_pipeline.py`

The CLI records launcher/stdout/stderr paths in run state and emits run/output metadata in JSON.

## Architecture boundary

`game_obfuscator` owns run scaffolding + deterministic obfuscation execution and output resolution. It does not publish/deploy to final public catalogs; upstream orchestration tools consume its terminal output contract.
