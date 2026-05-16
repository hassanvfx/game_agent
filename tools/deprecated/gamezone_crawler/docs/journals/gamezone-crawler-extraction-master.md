# Gamezone Crawler Extraction Master Journal

Last Updated: 2026-04-26 America/Mexico_City

## Objective
Create `/Volumes/Elements/gamezone_crawler` as the canonical home for the extracted Rezona/Gamezone crawler system without modifying the source repository.

## Golden Rules
- Do not modify the source repository.
- Use command-line copy tools when copying is the right operation.
- Preserve historical output structure exactly during first migration.
- Keep `outputs/rezona_crawl/` intact for continuity.

## Source Inventory Included
### Core runtime
- `rezona_topic_search_crawler.py`
- `fetch_rezona_game_details.py`

### Docs
- `README_REZONA_CRAWLER.md`
- `docs/api-reconstruction.md`
- `docs/journals/rezona-topic-search-crawler.md`

### Analysis and aggregation
- `analyze_rezona_search_overlap.py`
- `analyze_rezona_prefix_distribution.py`
- `group_rezona_games_by_id.py`
- `build_rezona_grouped_dashboard.py`
- `docs/journals/rezona-search-overlap-lake-estimate.md`
- `docs/journals/group-rezona-games-by-id.md`

### Historical outputs
- `outputs/rezona_crawl/latest_run.txt`
- `outputs/rezona_crawl/run_20260415T064109Z/`

## Migration Milestones
1. Inspect target path and source inventory.
2. Create destination skeleton.
3. Copy runtime, docs, journals, and outputs with CLI tools.
4. Add destination-only migration documentation.
5. Verify copied layout and continuity pointers.
6. Refactor only inside this destination in later passes.

## Current Status
- Target folder created.
- Core files copied.
- Historical `outputs/rezona_crawl/` copied.
- Verification pending.

## Notes
This first pass is a continuity-preserving extraction, not a rename/restructure pass.

---

## 2026-04-26 - Rezona crawler extraction smoke verification

### What Changed
- Executed a coordinated command-line smoke run from the extracted project root:
  - `cd /Volumes/Elements/gamezone_crawler && python3 rezona_topic_search_crawler.py --fresh-run --output-root outputs/rezona_crawl_smoke --queries brainrot minecraft --max-results-per-query 20`
- Verified the extracted crawler could create a new isolated run tree under:
  - `outputs/rezona_crawl_smoke/`
- Verified the generated run manifest and summaries from the new standalone location.

### Smoke Run Outcome
- Smoke run id:
  - `run_20260426T152851Z`
- API calls:
  - `13`
- Topics fetched:
  - `10`
- Topic-collected games:
  - `204`
- Queries executed:
  - `2`
- Search-collected games:
  - `40`
- Deduped games written:
  - `240`

### Verified Files
- `outputs/rezona_crawl_smoke/latest_run.txt`
- `outputs/rezona_crawl_smoke/run_20260426T152851Z/manifest.json`
- `outputs/rezona_crawl_smoke/run_20260426T152851Z/topics/`
- `outputs/rezona_crawl_smoke/run_20260426T152851Z/search/`
- `outputs/rezona_crawl_smoke/run_20260426T152851Z/summaries/all_games_deduped.json`

### Notes
- The extracted project is operational for small command-line runs from the Elements destination.
- Historical corpus continuity remains intact because the smoke test used a separate output root:
  - `outputs/rezona_crawl_smoke/`
- The crawler emitted a token warning despite the run succeeding, so the copied token-warning behavior should be cleaned up in a later destination-only pass if desired.
- The crawler also emitted `datetime.utcnow()` deprecation warnings; these are non-blocking and can be cleaned up later inside the Elements project only.

### Status
- Extraction documented
- Smoke run documented
- Standalone destination verified for small coordinated runs
