# Game Downloader

A standalone manifest-driven game downloader and local mirroring runtime.

## Scope

This package is focused on five capabilities only:

- input manifest
- run/output structure
- worker and queue execution
- per-game artifacts and status tracking
- dashboard/report observability

It intentionally excludes any crawler or source-discovery system.

## Minimal manifest contract

```json
{
  "items": [
    {
      "game_id": "game-001",
      "url": "https://example.com/game/index.html"
    }
  ]
}
```

Required fields per item:

- `game_id`
- `url`

## Current extraction status

This package is being extracted from an existing mirroring runtime.

Initial copied source material:

- `game_downloader/core/mirror_system.py`
- `scripts/batch_execute_run.py`
- `scripts/execute_queue_slice.py`
- `scripts/summarize_batch_run.py`
- `scripts/find_partial_games.py`
- `scripts/rebuild_specific_games.py`
- `scripts/rebuild_missing_summaries.py`
- `scripts/rebuild_processed_batch.py`
- `scripts/rebuild_classified_bucket.py`
- `scripts/classify_partial_games.py`
- `scripts/generate_qa_index.py`

## Planned public workflow

```bash
python3 scripts/create_run.py --input fixtures/sample_manifest.json
python3 scripts/run_batch.py --run-id <run_id>
python3 scripts/summarize_run.py --run-id <run_id>
python3 scripts/build_dashboard.py --run-id <run_id>
```

## Directory layout

```text
game_downloader/
  docs/
  fixtures/
  game_downloader/
    core/
  runs/
  scripts/
```
