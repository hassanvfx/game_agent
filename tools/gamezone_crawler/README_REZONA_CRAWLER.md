# Rezona Topic + Search Crawler

This repository includes standalone Rezona data collection scripts:

- `rezona_topic_search_crawler.py`
- `fetch_rezona_game_details.py`

The crawler fetches:
- all Rezona topics
- all topic games by paginating each topic to the end
- curated search queries for games / meme / Gen Z / franchise terms
- progressive JSON output for every task unit so runs can be resumed or inspected while they are in progress

---

## What the crawler does

The crawler hits these confirmed Rezona endpoints:

- `GET /api/v3/topic/all`
- `GET /api/v3/game/get_by_topic?topic_id=...&page=...&size=...`
- `GET /api/v3/search?type=game&q=...&page=...&size=...`

The enrichment helper hits:

- `GET /api/v3/game/detail?game_id=...`

Behavior:
- uses a global bearer token
- waits **2 seconds between API calls** by default
- prints live progress to the terminal
- writes JSON files progressively as each topic page and query page completes
- resumes from the latest run folder unless `--fresh-run` is used

The game detail enrichment helper:
- reads `summaries/all_games_deduped.json` from a crawl run
- extracts each unique `game_id`
- calls `GET /api/v3/game/detail?game_id=...`
- saves per-game `source_game.json`, `detail.json`, and `normalized.json`
- skips already cached games by default to minimize repeated API calls
- supports `--limit` for small-batch testing and `--force` for explicit re-fetches

Note:
- this enrichment path is disabled by default in the main crawler
- it was implemented and smoke-tested successfully
- in practice, `GET /api/v3/game/detail` mostly returned the same public fields already present in the deduped crawl output
- because the added API cost did not produce much new value, this step should be treated as optional/manual unless canonical per-game caching is specifically needed

---

## Script location

```bash
python3 rezona_topic_search_crawler.py --help
python3 fetch_rezona_game_details.py --help
```

---

## Token management

The script currently contains a hardcoded default token near the top of the file:

```python
DEFAULT_TOKEN = "..."
```

### To update the token

Open:

- `rezona_topic_search_crawler.py`

Find:

```python
DEFAULT_TOKEN = "..."
```

Replace the string with the latest valid Rezona access token.

### Alternative: pass token on the command line

You can also override the hardcoded token at runtime:

```bash
python3 rezona_topic_search_crawler.py --token 'YOUR_NEW_TOKEN'
```

If the hardcoded token expires, update the constant or use `--token`.

---

## Query management

The built-in query list lives near the top of the crawler:

```python
DEFAULT_QUERIES = [
    "brainrot",
    "meme",
    "skibidi",
    ...
]
```

### To update the default query set

Open:

- `rezona_topic_search_crawler.py`

Edit the `DEFAULT_QUERIES` list:
- add new terms
- remove weak terms
- reorder terms if desired

Example:

```python
DEFAULT_QUERIES = [
    "brainrot",
    "minecraft",
    "flappy bird",
    "gta",
    "roblox",
]
```

### To run with a custom query set without editing the file

```bash
python3 rezona_topic_search_crawler.py --queries brainrot minecraft 'flappy bird' gta
```

This overrides the built-in defaults for that run only.

---

## Common commands

### 1. Full run with the built-in query set

```bash
python3 rezona_topic_search_crawler.py --fresh-run
```

Use this when you want a clean full run with all built-in queries.

### 2. Resume the latest run

```bash
python3 rezona_topic_search_crawler.py
```

By default, the script resumes the latest run recorded in:

- `outputs/rezona_crawl/latest_run.txt`

### 3. Small test run

```bash
python3 rezona_topic_search_crawler.py \
  --fresh-run \
  --queries brainrot minecraft 'flappy bird' \
  --output-root outputs/rezona_crawl_test
```

### 4. Run with a different token

```bash
python3 rezona_topic_search_crawler.py \
  --token 'YOUR_NEW_TOKEN' \
  --fresh-run
```

### 5. Change delay between calls

```bash
python3 rezona_topic_search_crawler.py --delay-seconds 3
```

### 6. Change page sizes

```bash
python3 rezona_topic_search_crawler.py \
  --topic-page-size 50 \
  --search-page-size 50
```

### 7. Change max results per query

```bash
python3 rezona_topic_search_crawler.py --max-results-per-query 500
```

### 8. Fetch game details for the latest run

```bash
python3 fetch_rezona_game_details.py --limit 5
```

This uses `outputs/rezona_crawl/latest_run.txt`, skips already cached games, and fetches at most 5 uncached game details.

### 9. Fetch game details for a specific run

```bash
python3 fetch_rezona_game_details.py \
  --run-dir outputs/rezona_crawl/run_20260415T064109Z \
  --limit 5
```

### 10. Force-refresh cached game details

```bash
python3 fetch_rezona_game_details.py \
  --run-dir outputs/rezona_crawl/run_20260415T064109Z \
  --limit 5 \
  --force
```

### 11. Run the crawler and automatically enrich game details

```bash
python3 rezona_topic_search_crawler.py \
  --fresh-run \
  --post-enrich-game-details \
  --post-enrich-limit 5
```

---

## Output structure

A run creates a directory like:

```text
outputs/rezona_crawl/run_YYYYMMDDTHHMMSSZ/
```

Inside it:

```text
manifest.json
topics/
  topics.json
  topic_<id>.json
search/
  query_<slug>.json
summaries/
  topics_summary.json
  search_summary.json
  all_games_deduped.json
game_details/
  enrichment_summary.json
  game_<id>/
    source_game.json
    detail.json
    normalized.json
```

### File descriptions

#### `manifest.json`
Run-level status and progress:
- run id
- timestamps
- query list
- page sizes
- delay
- topic status
- search status
- game detail enrichment status
- total API calls

#### `topics/topics.json`
The full topic list returned by:
- `/api/v3/topic/all`

#### `topics/topic_<id>.json`
Per-topic progressive state:
- topic metadata
- pages fetched
- last page fetched
- completion flag
- stop reason
- all collected games for that topic

#### `search/query_<slug>.json`
Per-query progressive state:
- original query
- slug
- pages fetched
- last page fetched
- completion flag
- stop reason
- raw search items
- flattened game objects

#### `summaries/topics_summary.json`
Summary of topic crawl coverage.

#### `summaries/search_summary.json`
Summary of query crawl coverage.

#### `summaries/all_games_deduped.json`
Global deduped union of topic games + search games.

#### `game_details/enrichment_summary.json`
Summary of the game detail enrichment execution:
- processed count
- skipped count
- failed count
- API calls made
- last processed game id

#### `game_details/game_<id>/source_game.json`
Original deduped game object from the crawler summary.

#### `game_details/game_<id>/detail.json`
Raw response from `GET /api/v3/game/detail`.

#### `game_details/game_<id>/normalized.json`
Normalized subset of important game detail fields for downstream analysis.

---

## Progressive persistence and resume behavior

The crawler writes progress after each page.

That means:
- if the run stops mid-way, files already written remain usable
- rerunning without `--fresh-run` resumes the latest run
- completed topic files and completed query files are skipped automatically

Resume behavior is based on:
- `outputs/.../latest_run.txt`
- per-task JSON state files

---

## CLI reference

```bash
python3 rezona_topic_search_crawler.py --help
```

Available options:

- `--token TOKEN`
  - override the hardcoded token
- `--output-root OUTPUT_ROOT`
  - choose a different output directory
- `--delay-seconds DELAY_SECONDS`
  - time to wait between requests
- `--search-page-size SEARCH_PAGE_SIZE`
  - requested search page size
- `--topic-page-size TOPIC_PAGE_SIZE`
  - requested topic page size
- `--max-results-per-query MAX_RESULTS_PER_QUERY`
  - cap saved deduped results per query
- `--queries [QUERIES ...]`
  - override the default query set
- `--fresh-run`
  - start a brand-new run directory instead of resuming

---

## Recommended operating workflow

### For a normal production crawl
1. update `DEFAULT_TOKEN` with a fresh token if needed
2. review `DEFAULT_QUERIES`
3. start a fresh run:
   ```bash
   python3 rezona_topic_search_crawler.py --fresh-run
   ```
4. watch terminal progress
5. inspect:
   - `manifest.json`
   - `summaries/search_summary.json`
   - `summaries/all_games_deduped.json`

### For experimentation
Use a small query subset first:

```bash
python3 rezona_topic_search_crawler.py \
  --fresh-run \
  --queries brainrot minecraft 'flappy bird'
```

Then scale up once the token and results look good.

---

## Updating queries strategically

Good categories to maintain:
- meme / Gen Z / Alpha terms
- genre / mechanic terms
- relationship / social / drama terms
- popular franchise / clone-seed terms

Examples:
- `brainrot`
- `skibidi`
- `rizz`
- `quiz`
- `zombie`
- `racing`
- `fighting`
- `love`
- `drama`
- `minecraft`
- `flappy bird`
- `angry birds`
- `gta`
- `roblox`
- `fortnite`

If a query returns very low volume or poor-quality matches, remove it from `DEFAULT_QUERIES`.

---

## Troubleshooting

### Problem: token stops working
Symptoms:
- HTTP 401 / auth failures
- API error responses

Fix:
- get a fresh access token
- replace `DEFAULT_TOKEN`
- rerun with `--fresh-run` or resume as needed

### Problem: run was interrupted
Fix:
- rerun without `--fresh-run`
- the crawler should resume from the latest saved state

### Problem: too much output
Fix:
- run with a smaller query list:
  ```bash
  python3 rezona_topic_search_crawler.py --queries brainrot minecraft
  ```

### Problem: want isolated output
Fix:
- use a custom output root:
  ```bash
  python3 rezona_topic_search_crawler.py --output-root outputs/my_custom_run --fresh-run
  ```

---

## Current known cleanup items

The crawler currently works, but these are worth improving later:
- remove the outdated placeholder-token warning text
- replace deprecated `datetime.utcnow()` usage with timezone-aware UTC
- optionally add CSV exports in addition to JSON summaries

---

## Related files

- `rezona_topic_search_crawler.py`
- `docs/api-reconstruction.md`
- `docs/journals/rezona-topic-search-crawler.md`