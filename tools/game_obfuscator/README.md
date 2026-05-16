# game_obfuscator

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
