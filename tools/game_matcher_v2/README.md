# game_matcher_v2

Deterministic matcher pipeline driven by tag-family artifacts derived from `games/published/public/app.json`.

## CLI entrypoints

- `cli/build_artifacts.py`
- `cli/score_selected_tags.py`
- `cli/match_prompt.py`

## 1) Build artifacts

```bash
python3 cli/build_artifacts.py
python3 cli/build_artifacts.py --force
python3 cli/build_artifacts.py --app-json /path/to/app.json
```

Outputs JSON including:

- `source_path`
- `artifacts_dir`
- `metadata_path`
- `game_count`
- `source_md5`
- `rebuilt`

## 2) Score selected tags

```bash
python3 cli/score_selected_tags.py --selected-tags selected_tags.json
```

Key args:

- `--selected-tags` (required)
- `--app-json`
- `--limit`
- `--force-rebuild`
- `--out`

## 3) End-to-end prompt matching

```bash
python3 cli/match_prompt.py "flappy bird"
```

Key args:

- positional `prompt`
- `--app-json`
- `--model`
- `--limit`
- `--timeout-seconds`
- `--runs-dir`
- `--force-rebuild`
- `--selected-tags-out`
- `--out`

Behavior:

1. builds/refreshes artifacts
2. runs selector
3. validates selected tags
4. scores/ranks games

## Architecture boundary

`game_matcher_v2` owns artifact construction + deterministic scoring logic and provides a prompt-to-ranked-results CLI contract. It does not perform downstream refactor/publish execution.
