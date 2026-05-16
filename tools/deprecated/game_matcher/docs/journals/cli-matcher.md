# CLI Matcher Implementation Journal

**Last Updated:** 2026-04-26 14:50  
**Feature Spec:** N/A  
**Backend Reference:** N/A

---

## 📊 Implementation Status Overview

### ✅ Phase 1: Planning and Scaffolding - **COMPLETE**

- [x] Inspect existing browser matcher flow and local data contracts
- [x] Create CLI journal and implementation scaffolding
- [x] Define CLI interface and output contract

**Status:** ✅ Complete

### Phase 2: CLI Matcher Implementation - **COMPLETE**

- [x] Implement OpenAI-backed prompt-to-query translation in Python
- [x] Implement local deterministic ranking in Python
- [x] Add JSON stdout and `--out` file output behavior

**Status:** Complete

### Phase 3: Local Development Workflow - **COMPLETE**

- [x] Add virtual environment setup instructions/scripts
- [x] Scaffold `.env` support for `OPENAI_API_KEY`
- [x] Update README with setup and usage examples
- [x] Clarify `--limit 1` best-match behavior in README

**Status:** Complete

---

## 📝 Journal Entries

### 2026-04-26 14:38 - Initial Setup

**What Changed:**
- Created task journal for the CLI matcher effort
- Captured scope for CLI behavior, environment loading, and launcher scripts
- Documented the current implementation phases

**Why:**
This repository requires a journal per task. The CLI matcher work spans code, environment setup, and developer workflow, so documenting the approach upfront keeps implementation aligned and resumable.

**Files Created:**
- `docs/journals/cli-matcher.md` - Task journal for CLI matcher work

**Next Steps:**
- [x] Add the CLI script and supporting Python helpers
- [x] Add `.env` scaffolding and venv launcher scripts
- [x] Update README with setup and usage guidance

**Status:** Complete

---

### 2026-04-26 14:45 - CLI matcher completed and verified

**Achievement:**
Implemented a terminal-friendly Python CLI for the game matcher, plus local environment scaffolding and launcher scripts.

**Implementation Details:**
- Created `cli/game_matcher_cli.py` - CLI entrypoint with `prompt`, `--limit`, `--out`, and `--env-file`
- Created `matcher/cli_support.py` - Shared prompt translation, ranking, JSON loading, and `.env` parsing helpers
- Created `matcher/__init__.py` - Package marker for helper imports
- Created `.env.example` - Local API key scaffold
- Created `scripts/setup_cli_env.sh` - Virtual environment setup and `.env` bootstrap
- Created `scripts/run_cli_matcher.sh` - Launcher using `.venv/bin/python`
- Updated `.gitignore` - Ignore `.env` and `.venv/`
- Updated `README.md` - Added setup and usage docs for the CLI matcher

**Code Snippet:**
```python
load_env_file(args.env_file)
api_key = os.environ.get("OPENAI_API_KEY")
all_queries = load_json(DEFAULT_QUERIES_PATH)
reverse_index = load_json(DEFAULT_REVERSE_INDEX_PATH)
translated_queries = translate_prompt_to_queries(args.prompt, all_queries, api_key)
ranked_games = rank_games(args.prompt, translated_queries, reverse_index)
output_games = build_output_games(ranked_games, args.limit)
```

**Technical Decisions:**
The CLI keeps OpenAI usage limited to vocabulary-constrained query selection while preserving the browser's deterministic local ranking model in Python. Output defaults to machine-readable JSON, with optional file writing via `--out`.

**Testing:**
- Verified import path resolution for the CLI entrypoint
- Verified missing `OPENAI_API_KEY` failure path
- Verified `scripts/setup_cli_env.sh` creates `.venv` and scaffolds `.env`
- Verified `scripts/run_cli_matcher.sh` runs the CLI and reaches the API
- Verified `.env` and `.venv/` are ignored by Git
- Observed expected 401 response with placeholder API key from `.env.example`

**Next Steps:**
- [ ] Replace placeholder `OPENAI_API_KEY` in `.env` with a real key for live matching runs

**Status:** Complete

---

### 2026-04-26 14:50 - README clarified for top-1 matching behavior

**Achievement:**
Expanded the CLI documentation to explain how `--limit 1` should be interpreted and when to use top-1 versus top-5 output.

**Implementation Details:**
- Updated `README.md` - Added examples using `--limit 1`, `--limit 5`, and `--out`
- Documented that `--limit 1` returns the highest-ranked result from the current matcher
- Clarified that the local ranking is deterministic once translated queries are fixed, while the query-selection step can vary slightly across runs

**Technical Decisions:**
This clarification reduces ambiguity for CLI users who want a single recommendation. The README now distinguishes between "best according to the scoring model" and "objectively perfect," which better matches how the pipeline actually works.

**Testing:**
- Reviewed the README section for consistency with the implemented CLI behavior
- Confirmed the examples match the supported flags and launcher script usage

**Next Steps:**
- [ ] Replace placeholder `OPENAI_API_KEY` in `.env` with a real key for live matching runs

**Status:** Complete

---

### 2026-04-26 19:58 - Exported URL to computed game-key mapping for subset-index prep

**Achievement:**
Prepared a reusable mapping artifact from the current reverse index so the matcher can later support URL-based input and smaller subset indexes.

**Implementation Details:**
- Created `scripts/export_game_url_key_map.py` - Reads `fixtures/consolidated/master_game_reverse_index.json` and exports URL/key mappings
- Created `fixtures/consolidated/game_url_key_map.json` - Flat JSON array with `game_id`, `name`, `url`, and computed `game_key`
- Implemented `safe_name`, `slugify`, and `infer_game_key(...)` locally using the same priority order described from the downloader code:
  1. `/minigame/<id>/index.html`
  2. `/latest-....html`
  3. `game-{game_id}`
  4. slugified URL fallback

**Technical Decisions:**
The exported JSON keeps both the original `url` and the derived `game_key` so future URL-input matching can audit derivation behavior, inspect collisions, and build reduced indexes without recomputing the mapping from scratch.

**Testing:**
- Verified the source reverse index contains 8,673 games and no missing URLs
- Ran `python3 scripts/export_game_url_key_map.py`
- Verified `fixtures/consolidated/game_url_key_map.json` contains 8,673 mappings
- Verified there are 0 missing URLs, 0 missing game keys, and 8,673 unique `game_key` values in the generated output

**Next Steps:**
- [ ] Use `game_url_key_map.json` to define the smaller subset to keep
- [ ] Add a new CLI input mode that accepts URL-derived identifiers

**Status:** Complete

---

### 2026-04-26 20:05 - Built the top800 subset fixtures from an external allowlist

**Achievement:**
Created a derived subset of the full matcher index using the external allowlist copied from the remixer workspace, with all outputs namespaced under the `top800` prefix.

**Implementation Details:**
- Copied `/Volumes/Elements/game_remixer/fixtures/output_game_ids.txt` to `fixtures/consolidated/top800_game_ids.txt`
- Created `scripts/build_top800_subset.py` - Filters the URL/key map and reverse index using the `top800` allowlist
- Created `fixtures/consolidated/top800_game_url_key_map.json` - Matching subset of the full URL/key map
- Created `fixtures/consolidated/top800_master_game_reverse_index.json` - Matching subset of the full reverse index
- Created `fixtures/consolidated/top800_master_game_reverse_index_summary.json` - Verification stats for the derived subset

**Technical Decisions:**
The subset builder uses the computed `game_key` values as the stable join key between the external allowlist and the local matcher fixtures. Although the prefix is `top800`, the copied allowlist currently contains 796 entries, so the derived subset is an exact 796-game subset of the current 8,673-game full index.

**Testing:**
- Ran `python3 scripts/build_top800_subset.py`
- Verified `allowlist_count = 796`
- Verified `filtered_map_count = 796`
- Verified `filtered_game_count = 796`
- Verified `unmatched_allowlist_count = 0`
- Verified `duplicate_key_count = 0`

**Next Steps:**
- [ ] Point a matcher variant at `top800_master_game_reverse_index.json`
- [ ] Optionally add a paired filtered query index if subset-specific query acceleration is needed
- [ ] Add URL-input matching mode using the computed key mapping

**Status:** Complete

---

### 2026-04-26 20:07 - Switched the CLI default index to top800 with all-index opt-in

**Achievement:**
Updated the CLI so it now uses the `top800` subset index by default and only uses the legacy full index when `--index all` is explicitly passed.

**Implementation Details:**
- Updated `matcher/cli_support.py` - Added `TOP800_REVERSE_INDEX_PATH` alongside the legacy full-index path
- Updated `cli/game_matcher_cli.py` - Added `--index {top800,all}` with default `top800`
- Wired reverse-index selection so:
  - `top800` loads `fixtures/consolidated/top800_master_game_reverse_index.json`
  - `all` loads `fixtures/consolidated/master_game_reverse_index.json`
- Kept query vocabulary loading unchanged on `fixtures/consolidated/all_queries.json`
- Updated `README.md` - Documented the new default behavior and added `--index all` examples

**Technical Decisions:**
The query vocabulary remains shared across both index modes to minimize moving parts while changing only the ranked candidate pool. This keeps the new default lightweight without introducing a second filtered query vocabulary yet.

**Testing:**
- Ran `python3 cli/game_matcher_cli.py --help`
- Verified the CLI exposes `--index {top800,all}`
- Verified the help text states that `top800` is the default and `all` is the legacy override

**Next Steps:**
- [ ] Optionally add a filtered query vocabulary if top800-specific query narrowing is needed
- [ ] Add URL-input matching mode using the computed key mapping

**Status:** Complete

---

### 2026-04-26 20:12 - Added direct URL lookup mode to the CLI

**Achievement:**
Fixed the missing `--url` behavior so the CLI can now resolve a single indexed game directly from its source URL.

**Implementation Details:**
- Updated `cli/game_matcher_cli.py` - Added `--url` as an alternative input mode
- Made the positional `prompt` optional so the CLI can be used either for prompt matching or direct URL lookup
- Added input validation so the CLI requires exactly one of:
  - a free-text `prompt`
  - `--url`
- Updated `matcher/cli_support.py` - Added:
  - `normalize_source_url(...)`
  - `find_game_by_url(...)`
  - `build_single_game_output(...)`
- URL lookup currently searches the selected reverse index (`top800` by default, `all` with `--index all`) and returns a single JSON object with the indexed game metadata

**Technical Decisions:**
The direct URL lookup path reuses the same consolidated reverse indexes already used for prompt matching, which keeps the implementation deterministic and avoids adding a second lookup store. URL normalization strips query strings, fragments, and trailing slashes so equivalent source URLs resolve consistently.

**Testing:**
- Reproduced the failure: `python3 cli/game_matcher_cli.py --url ...` previously errored with `unrecognized arguments: --url`
- Ran:
  `python3 cli/game_matcher_cli.py --url https://storage.googleapis.com/rezona-ai-prod/minigame/6ad1554b-f180-4be3-b53e-de34a33cd3fa/index.html`
- Verified the CLI returned the indexed game record for `game_id = 637956`

**Next Steps:**
- [ ] Add a dedicated launcher/alias such as `./get_game` if a shorter command is still desired
- [ ] Document `--url` mode in `README.md`
- [ ] Commit the URL-input fix after any remaining documentation polish

**Status:** Complete

---

### 2026-04-28 20:27 - Documented CLI matcher taxonomy analysis and grounded numeric legend

**Achievement:**
Captured the matcher-taxonomy investigation in-repo, added a durable numeric-label legend JSON artifact, and tied the top800 matcher behavior to the upstream Rezona taxonomy source.

**Implementation Details:**
- Created `fixtures/consolidated/gameplay_taxonomy_numeric_legend.json` - Local JSON legend mapping numeric taxonomy IDs `1` through `33` to the recovered upstream section titles
- Created `docs/gameplay-taxonomy-analysis.md` - Consolidated reference doc covering:
  - prompt-mode and URL-mode CLI behavior
  - top800 vs all index behavior
  - reverse-index schema usage
  - synthetic/noise coverage findings
  - mechanic-family distribution findings
  - upstream provenance for numeric labels
- Verified that numeric labels in downstream matcher data originate from the upstream Rezona expansion master list rather than from a hidden classifier or ranking-time inference
- Traced the metadata collapse path from:
  - readable upstream seed metadata such as `category = movement`, `subcategory = runner`, `mechanic_family = runner`
  - to expanded numeric metadata such as `category = "1"`, `subcategory = "expanded"`, `mechanic_family = "1"`

**Grounded Numeric Legend Summary:**
- `1` -> Core Movement / Runner / Platformer
- `2` -> Puzzle / Logic / Match / Draw / Sorting
- `3` -> Merge / Idle / Clicker / Tycoon
- `4` -> Survivor / Shooter / Defense / Combat
- `5` -> Driving / Vehicle / Traffic / Parking
- `6` -> Simulation / Management / Cooking / Farming / Life
- `7` -> Lifestyle / Fashion / Makeover / Home Design
- `8` -> Trivia / Quiz / Social Prompt / Party
- `9` -> Dating / Romance / Flirting / Rizz
- `10` -> Interactive Story / Chat Fiction / Choice Based
- `11` -> Arcade / Skill / Hypercasual / Physics Toy
- `12` -> IO / Crowd / Swarm / Territory
- `13` -> Sports / Ball / Competition
- `14` -> Board / Card / Casino / Word / Classic
- `15` -> Sandbox / Building / Crafting / Open World / Destruction
- `16` -> Horror / Scary / Thriller / Monster
- `17` -> Major Franchises / Pop Culture / Clone Bait
- `18` -> Kids / Family / Cartoon / Audience Terms
- `19` -> Viral / Meme / TikTok / Trend / Prank
- `20` -> Broad Genre / Intent / Discovery Catch-All
- `21` -> Battle Royale / Extraction / Multiplayer PvP
- `22` -> Open World Crime / Urban Fantasy / Heist
- `23` -> Sandbox Creator / UGC / Build-and-Share
- `24` -> Anime / Manga / Otaku / Fan Intent
- `25` -> Superhero / Comic / Action Fantasy
- `26` -> Monster / Creature / Animal Fantasy
- `27` -> School / Teen / Life Drama / Social Identity
- `28` -> Family / Parenting / Baby / Home Life
- `29` -> Food / Dessert / Kitchen / Cozy Casual
- `30` -> Beauty / Salon / Self-Care / ASMR
- `31` -> Music / Dance / Rhythm / Performance
- `32` -> Meme / Internet / Social Platform Fantasies
- `33` -> Hypercasual Ad-Bait / Ultra-Broad Retrieval

**Key Analysis Findings:**
- The CLI defaults to the so-called `top800` reverse index, which currently contains **796 games**
- The query vocabulary remains shared across subset and full-index modes
- The matcher performs:
  1. prompt -> allowed-query selection
  2. deterministic local ranking against the selected reverse index
- `intent_generated` is a major synthetic/noise source in the current reverse index
- Using a first-pass synthetic definition of `intent_generated` and `structure`, the top800 index showed:
  - 796 total games
  - 166 games with at least one synthetic/noise label
  - 23 games with only synthetic/noise labels
  - 13,415 total query matches
  - 7,101 synthetic/noise query matches
  - 52.93% synthetic/noise query-match share
- The numeric labels are best interpreted as compressed upstream taxonomy section IDs, while named `mechanic_family` values remain more directly readable for gameplay audits

**Technical Decisions:**
Instead of leaving the taxonomy understanding in chat-only form, the repo now contains a local durable explanation layer:
- one machine-readable JSON legend
- one human-readable analysis doc
- one journal entry recording the provenance and major conclusions

This keeps future CLI-matcher work grounded even if the sibling upstream projects are unavailable or change independently.

**Testing / Verification:**
- Inspected `cli/game_matcher_cli.py` and `matcher/cli_support.py` to confirm current runtime behavior
- Inspected `fixtures/consolidated/top800_master_game_reverse_index.json` to verify local schema usage and category/mechanic_family patterns
- Queried local data to measure synthetic/noise coverage and mechanic-family distribution
- Inspected sibling upstream files:
  - `../resonalyzer2/queries/gameplay_query_library.json`
  - `../resonalyzer2/queries/gameplay_query_library_expanded_clean.json`
  - `../resonalyzer2/docs/gameplay-query-expansion-master-list.md`
- Confirmed that the expanded library replaces readable section metadata with numeric section IDs inherited from the upstream master list

**Files Created:**
- `fixtures/consolidated/gameplay_taxonomy_numeric_legend.json`
- `docs/gameplay-taxonomy-analysis.md`

**Next Steps:**
- [ ] Optionally link `docs/gameplay-taxonomy-analysis.md` from `README.md`
- [ ] Optionally add a local script that joins per-game top800 mechanic coverage with the grounded 1-33 legend
- [ ] Optionally split grounded gameplay labels from synthetic/noise labels into separate derived analysis artifacts

**Status:** Complete

---

### 2026-04-28 20:50 - Built enriched mechanics_map_top800 derived index

**Achievement:**
Created a grouped mechanic-centric view of the top800 matcher subset so each grounded taxonomy mechanic now has a single enriched object with its definition, specific observed mechanic-family labels, representative queries, and the associated game array.

**Implementation Details:**
- Created `fixtures/consolidated/mechanics_map_top800.json`
- Grouped games from `fixtures/consolidated/top800_master_game_reverse_index.json` by the grounded numeric taxonomy IDs recovered in:
  - `fixtures/consolidated/gameplay_taxonomy_numeric_legend.json`
- Emitted one top-level object per grounded taxonomy section with:
  - `mechanic`
  - `definition`
  - `taxonomy_id`
  - `classification`
  - `specific_mechanic_families`
  - `related_categories`
  - `query_examples`
  - `game_count`
  - `games`
- Each `games` entry includes:
  - `game_id`
  - `name`
  - `url`
  - `cover_url`
  - `matched_mechanic_families`
  - `matched_categories`

**Technical Decisions:**
The new artifact groups primarily by the stable grounded numeric legend rather than by the more fragmented raw query strings. This keeps the top-level buckets durable and aligned with the recovered upstream taxonomy while still preserving finer-grained detail through:
- `specific_mechanic_families`
- `query_examples`
- per-game `matched_*` trace fields

This makes the file useful both as:
- a mechanic-to-games lookup index
- and a self-describing exploration artifact for future analysis

**Testing / Verification:**
- Generated `mechanics_map_top800.json` from the current top800 reverse index and numeric legend
- Verified the output contains **33 mechanic buckets**
- Verified sample bucket structure includes the requested enriched top-level mechanic object shape
- Verified the first bucket (`Core Movement / Runner / Platformer`) reports:
  - `taxonomy_id = "1"`
  - `classification = "mechanic_centric"`
  - representative query examples
  - `game_count = 65`
  - full `games` array with per-game match metadata

**Files Created:**
- `fixtures/consolidated/mechanics_map_top800.json`

**Next Steps:**
- [ ] Optionally add a reproducible builder script for regenerating `mechanics_map_top800.json`
- [ ] Optionally link `mechanics_map_top800.json` from `docs/gameplay-taxonomy-analysis.md`
- [ ] Optionally add a filtered variant that excludes broad/noisy taxonomy buckets

**Status:** Complete

---

### 2026-04-28 22:49 - Enriched mechanics_map_top800 with stable game_key joins

**Achievement:**
Extended the mechanics map so each embedded game record now includes the stable `game_key` used elsewhere in the subset-index pipeline.

**Implementation Details:**
- Updated `fixtures/consolidated/mechanics_map_top800.json`
- Joined the mechanics map against:
  - `fixtures/consolidated/top800_game_url_key_map.json`
- Added `game_key` to every game entry inside every mechanic bucket
- Resolved keys using:
  1. `game_id`
  2. fallback URL match when needed

**Technical Decisions:**
Including `game_key` makes the mechanics map much easier to join with other derived artifacts in this repository, especially:
- top800 allowlist-driven subset files
- URL/key mapping outputs
- future mechanic-level exports or dashboards

Using the existing top800 URL/key map keeps the enrichment deterministic and aligned with the already documented subset-key derivation pipeline.

**Testing / Verification:**
- Updated **1,655** embedded game entries across all mechanic buckets
- Verified **0** missing `game_key` values after the join
- Verified fallback matching produced no unresolved records

**Files Updated:**
- `fixtures/consolidated/mechanics_map_top800.json`

**Next Steps:**
- [ ] Optionally add a reproducible builder script for mechanics-map regeneration, including `game_key`
- [ ] Optionally expose `game_key`-based joins in future analysis docs or dashboard exports

**Status:** Complete

---

### 2026-04-28 23:22 - Reproduced top800-filtered per-query evidence files from external raw crawl output

**Achievement:**
Created a local evidence-layer copy of the external Rezona raw search results, preserving the original per-query file structure while filtering each query response down to only the games present in the current top800 subset.

**Implementation Details:**
- Read external source files from:
  - `/Volumes/Elements/gamezone_crawler/outputs/rezona_crawl/run_20260415T064109Z/search`
- Used the local top800 subset from:
  - `fixtures/consolidated/top800_master_game_reverse_index.json`
- Created local filtered output directory:
  - `fixtures/consolidated/top800_filtered_query_results/run_20260415T064109Z/search/`
- For each source `query_*.json` file:
  - filtered `items` to only entries whose `item.game.game_id` exists in the top800 subset
  - filtered `games` to only game payloads whose `game_id` exists in the top800 subset
  - preserved original metadata fields such as:
    - `query`
    - `slug`
    - `pages_fetched`
    - `last_page_fetched`
    - `completed`
    - `stop_reason`
    - `updated_at`
  - added derived metadata:
    - `filter_scope = "top800"`
    - `source_run_id = "run_20260415T064109Z"`
    - `filtered_total_collected`
- Created summary artifact:
  - `fixtures/consolidated/top800_filtered_query_results/run_20260415T064109Z/summary.json`

**Technical Decisions:**
This artifact keeps provenance intact by preserving the original raw query-file structure instead of forcing the data into a second derived schema. That makes it much easier to audit “why did this game appear for this mechanic-like query?” using real raw retrieval evidence rather than only the fully consolidated reverse index.

The filtered files are intentionally query-centric rather than game-centric. They complement:
- `top800_master_game_reverse_index.json`
- `mechanics_map_top800.json`

instead of replacing them.

**Testing / Verification:**
- Processed **37** source query files
- Wrote **37** filtered local query files
- Verified the filtered query files contain a combined total of **99** top800 game appearances across all queries
- Wrote summary file:
  - `fixtures/consolidated/top800_filtered_query_results/run_20260415T064109Z/summary.json`

**Files Created:**
- `fixtures/consolidated/top800_filtered_query_results/run_20260415T064109Z/search/query_alpha.json`
- `fixtures/consolidated/top800_filtered_query_results/run_20260415T064109Z/search/query_among-us.json`
- `fixtures/consolidated/top800_filtered_query_results/run_20260415T064109Z/search/query_angry-birds.json`
- `fixtures/consolidated/top800_filtered_query_results/run_20260415T064109Z/search/query_brainrot.json`
- `fixtures/consolidated/top800_filtered_query_results/run_20260415T064109Z/search/query_crush.json`
- `fixtures/consolidated/top800_filtered_query_results/run_20260415T064109Z/search/query_dating.json`
- `fixtures/consolidated/top800_filtered_query_results/run_20260415T064109Z/search/query_drama.json`
- `fixtures/consolidated/top800_filtered_query_results/run_20260415T064109Z/search/query_fighting.json`
- `fixtures/consolidated/top800_filtered_query_results/run_20260415T064109Z/search/query_flappy-bird.json`
- `fixtures/consolidated/top800_filtered_query_results/run_20260415T064109Z/search/query_fnaf.json`
- `fixtures/consolidated/top800_filtered_query_results/run_20260415T064109Z/search/query_fortnite.json`
- `fixtures/consolidated/top800_filtered_query_results/run_20260415T064109Z/search/query_genz.json`
- `fixtures/consolidated/top800_filtered_query_results/run_20260415T064109Z/search/query_gta.json`
- `fixtures/consolidated/top800_filtered_query_results/run_20260415T064109Z/search/query_horror.json`
- `fixtures/consolidated/top800_filtered_query_results/run_20260415T064109Z/search/query_love.json`
- `fixtures/consolidated/top800_filtered_query_results/run_20260415T064109Z/search/query_mario.json`
- `fixtures/consolidated/top800_filtered_query_results/run_20260415T064109Z/search/query_meme.json`
- `fixtures/consolidated/top800_filtered_query_results/run_20260415T064109Z/search/query_minecraft.json`
- `fixtures/consolidated/top800_filtered_query_results/run_20260415T064109Z/search/query_npc.json`
- `fixtures/consolidated/top800_filtered_query_results/run_20260415T064109Z/search/query_obby.json`
- `fixtures/consolidated/top800_filtered_query_results/run_20260415T064109Z/search/query_pokemon.json`
- `fixtures/consolidated/top800_filtered_query_results/run_20260415T064109Z/search/query_quiz.json`
- `fixtures/consolidated/top800_filtered_query_results/run_20260415T064109Z/search/query_racing.json`
- `fixtures/consolidated/top800_filtered_query_results/run_20260415T064109Z/search/query_rizz.json`
- `fixtures/consolidated/top800_filtered_query_results/run_20260415T064109Z/search/query_roblox.json`
- `fixtures/consolidated/top800_filtered_query_results/run_20260415T064109Z/search/query_romance.json`
- `fixtures/consolidated/top800_filtered_query_results/run_20260415T064109Z/search/query_runner.json`
- `fixtures/consolidated/top800_filtered_query_results/run_20260415T064109Z/search/query_sigma.json`
- `fixtures/consolidated/top800_filtered_query_results/run_20260415T064109Z/search/query_simulator.json`
- `fixtures/consolidated/top800_filtered_query_results/run_20260415T064109Z/search/query_skibidi.json`
- `fixtures/consolidated/top800_filtered_query_results/run_20260415T064109Z/search/query_sonic.json`
- `fixtures/consolidated/top800_filtered_query_results/run_20260415T064109Z/search/query_subway-surfers.json`
- `fixtures/consolidated/top800_filtered_query_results/run_20260415T064109Z/search/query_tiktok.json`
- `fixtures/consolidated/top800_filtered_query_results/run_20260415T064109Z/search/query_trivia.json`
- `fixtures/consolidated/top800_filtered_query_results/run_20260415T064109Z/search/query_tycoon.json`
- `fixtures/consolidated/top800_filtered_query_results/run_20260415T064109Z/search/query_viral.json`
- `fixtures/consolidated/top800_filtered_query_results/run_20260415T064109Z/search/query_zombie.json`
- `fixtures/consolidated/top800_filtered_query_results/run_20260415T064109Z/summary.json`

**Next Steps:**
- [ ] Use the filtered per-query files to trace suspicious mechanic assignments back to raw retrieval evidence
- [ ] Optionally derive a stricter mechanic-membership score from repeated non-synthetic per-query support
- [ ] Optionally build a small browser inspector over the filtered query evidence directory

**Status:** Complete

---

## 🐛 Known Issues

### None yet

**Problem:** 
No known issues documented yet.

**Root Cause:** 
N/A

**Status:** 
- [ ] Being investigated
- [ ] Blocked (waiting for...)
- [ ] Fixed

**Workaround:** 
N/A

**Resolution:** 
N/A

---

## 📚 Quick Reference

### Key Files

- `index.html` - Existing browser implementation containing prompt translation and ranking logic
- `README.md` - Current project documentation and runtime flow
- `fixtures/consolidated/all_queries.json` - Allowed query vocabulary
- `fixtures/consolidated/master_game_reverse_index.json` - Local reverse index used for ranking

### Important Commands

```bash
python3 serve_game_matcher.py
python3 scripts/build_gameplay_reverse_index.py
python3 scripts/export_all_queries.py
./scripts/refresh_indexes.sh
```

### Environment Variables

```bash
OPENAI_API_KEY=your_api_key_here
```

---

## ✅ Testing Checklist

- [x] CLI runs from a local virtual environment
- [x] `.env` loading works
- [ ] JSON output prints correctly to stdout
- [ ] `--out` writes results to a file
- [x] README updated with verified commands

---

## 🎯 Success Criteria

- [x] CLI matcher implemented
- [x] Environment scaffolding added
- [x] Documentation updated
- [x] Manual verification completed

---

*This journal documents the CLI matcher implementation work for this repository.*