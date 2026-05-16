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

## Grounded usage example

For a live game URL such as:

```text
https://games.jabali.ai/d44f1373-e03a-4e2d-8a40-90ff9671ffeb/c33db5bd-53ee-4637-bdba-4153f2805353/
```

the intended input manifest is:

```json
{
  "items": [
    {
      "game_id": "c33db5bd-53ee-4637-bdba-4153f2805353",
      "url": "https://games.jabali.ai/d44f1373-e03a-4e2d-8a40-90ff9671ffeb/c33db5bd-53ee-4637-bdba-4153f2805353/"
    }
  ]
}
```

Save that to a file such as `fixtures/jabali_single_game.json`, then run:

```bash
python3 scripts/create_run.py --input fixtures/jabali_single_game.json
python3 scripts/run_batch.py --run-id <run_id> --count 1
python3 scripts/summarize_run.py --run-id <run_id>
python3 scripts/build_dashboard.py --run-id <run_id>
```

When `game_id` is supplied, the runtime derives a queue/game key from it. For the example above, the key will be:

```text
game-c33db5bd-53ee-4637-bdba-4153f2805353
```

## What the runtime actually does

For each manifest item, the runtime performs a local mirroring workflow:

1. create a run scaffold and queue record
2. fetch the entry URL HTML
3. extract asset URLs from the entry HTML
4. download discovered assets
5. recursively inspect downloaded text assets such as CSS and JSON-like files for more URLs
6. assemble a local replay package with rewritten references
7. classify whether the result is fully or partially offline-ready

Typical per-game artifacts include:

- fetched entry HTML
- asset URL reports
- downloaded asset files
- replay package with rewritten local references
- unresolved URL and remaining remote reference audits
- mirror build summary and offline-readiness classification

## Static mirroring vs runtime capture

The default mirror build is primarily a **static discovery** workflow: it fetches the entry HTML, parses referenced asset URLs, downloads them, and rewrites the package for local replay.

That is often sufficient for simple games, but a modern game page may load critical assets dynamically in JavaScript. For those cases, this repo also contains a **Playwright-based runtime capture** path that:

- launches Chromium
- opens the page
- records runtime network responses
- stores captured response bodies
- writes a runtime request manifest and a discovered URL list

So the practical usage model is:

1. try the normal mirror workflow first
2. inspect the replay package and offline-readiness summary
3. if important assets are still missing, use runtime capture to supplement static discovery

In short: a Jabali game URL should be treated as one manifest item, and the downloader should be understood as a staged mirroring pipeline rather than a single opaque “download this page” command.

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
