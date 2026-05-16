# Gamezone Crawler

This project is the extracted standalone home for the Rezona/Gamezone crawler workflow copied out of the source repository without modifying the original source.

## Current scope
- Topic + search crawler
- Game detail enrichment helper
- Historical crawl outputs
- Rezona output analysis and grouping helpers

## Preserved output root
Historical and future continuity currently use:

- `outputs/rezona_crawl/`

This was intentionally preserved to avoid breaking resume behavior and existing analysis assumptions.

## Key entrypoints
- `rezona_topic_search_crawler.py`
- `fetch_rezona_game_details.py`
- `analyze_rezona_search_overlap.py`
- `analyze_rezona_prefix_distribution.py`
- `group_rezona_games_by_id.py`
- `build_rezona_grouped_dashboard.py`

## Documentation
- `README_REZONA_CRAWLER.md`
- `docs/api-reconstruction.md`
- `docs/journals/rezona-topic-search-crawler.md`
- `docs/journals/gamezone-crawler-extraction-master.md`

## Migration status
Initial copy-based extraction completed. Verification and destination-only refactoring can proceed from this folder.
