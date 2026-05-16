# giphy_api

Thin Python CLI wrapper around Giphy.

## Installed CLI command

From `pyproject.toml`:

- `giphy = giphy_cli.cli:main`

After install, use:

```bash
giphy --help
```

## Commands

From `giphy_cli/cli.py`:

- `giphy search <query>`
- `giphy trending`
- `giphy translate <phrase>`
- `giphy random`

### Common options

- `--json` (machine-readable output)

Command-specific options:

- `search`: `--limit`, `--offset`, `--rating`, `--lang`
- `trending`: `--limit`, `--rating`
- `random`: `--tag`, `--rating`

## Examples

```bash
giphy search "cats" --limit 5
giphy search "cats" --limit 5 --json
giphy trending --limit 10
giphy translate "mind blown"
giphy random --tag "excited"
```

## Architecture boundary

`giphy_api` is a wrapper CLI layer: argument parsing + output shaping around service/config modules. It does not implement a custom GIF backend.
