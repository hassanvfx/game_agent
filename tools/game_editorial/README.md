# game_editorial

Editorial analysis tooling for canonical, traceable batches derived from the live published game corpus.

## Current canonical source

The first toolchain reads:

```text
games/published/public/app.json
```

This matches the default source used by `game_matcher_v2`.

## First batch: top mechanic identities

The initial script computes the top **single mechanic identities** from the published corpus, ranks them by an editorial distinctiveness heuristic, and fetches the top matcher results for each one.

### Entrypoint

```bash
python3 scripts/build_top_mechanic_identity_batch.py
```

### Useful flags

- `--app-json games/published/public/app.json`
- `--top-n 100`
- `--matches-per-tag 10`
- `--min-support 2`
- `--out-dir tools/game_editorial/scripts/workspace/custom_run`
- `--force-rebuild`

## Output artifacts

By default the script writes a timestamped run folder under:

```text
tools/game_editorial/scripts/workspace/
```

Each run contains:

- `batch_summary.json`
- `top_100_mechanic_tags.json`
- `matches_by_mechanic_tag.json`

## Ranking heuristic

For the first editorial pass, mechanic identities are ranked with:

```text
distinctiveness_score = support * ln(N / support)
```

Where:

- `support` = number of published entries carrying the mechanic tag
- `N` = total number of published entries in `app.json`

This favors tags that recur enough to be meaningful but are not so universal that they stop being identity-defining.

## Prompt starter seeds

The tool area also hosts prompt-starter seeds. The first seed set comes from the user-provided `remixIdeas` examples and is intended to expand over time to cover a much broader span of mechanic families.

## Architecture boundary

`game_editorial` owns editorial batch generation and artifact writing. It reuses `game_matcher_v2` for deterministic retrieval/scoring rather than re-implementing matcher behavior.
