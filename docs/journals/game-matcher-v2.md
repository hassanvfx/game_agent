# Game Matcher V2 Implementation Journal

**Last Updated:** 2026-05-14  
**Feature Spec:** Tag-family-driven `game_matcher_v2` with deterministic local ranking over `games/published/public/app.json`  
**Backend Reference:** N/A

---

## 📊 Implementation Status Overview

### ✅ Phase 1: Architecture and Contract Mapping - **COMPLETED**

- [x] Confirm `games/published/public/app.json` as the source-of-truth corpus
- [x] Confirm current `game_matcher` CLI/output contract
- [x] Confirm sibling `game_refactoring` uses direct `cline` subprocess orchestration
- [x] Define aggregated tag-family artifact format
- [x] Define deterministic scorer contract and fixture format

**Status:** Complete

### ✅ Phase 2: Deterministic Core - **COMPLETED**

- [x] Scaffold `tools/game_matcher_v2/`
- [x] Build aggregated tag-family artifacts from `app.json`
- [x] Build normalized per-game tag documents
- [x] Implement weighted local scoring from ranked selected tags to games
- [x] Add fixture-driven expectation tests/examples

**Status:** Complete

### ✅ Phase 3: Agent Integration - **COMPLETED**

- [x] Define per-family ranked tag output schema
- [x] Add Cline-powered selector step using aggregated family vocabularies
- [x] Wire selector output into deterministic scorer
- [x] Preserve current matcher-compatible output contract

**Status:** Complete

---

## 📝 Journal Entries

### 2026-05-14 01:48 - Initial `game_matcher_v2` direction

**What Changed:**
- Created this journal for the new `game_matcher_v2` direction.
- Established that `app.json` is the correct source corpus.
- Decided to avoid title/description/prompt matching in v2 and rely on structured tag families only.
- Confirmed the sibling `game_refactoring` project invokes `cline` directly from Python subprocess commands.

**Why:**
The failed fuzzy-matcher attempt showed that purely lexical retrieval was insufficient. The new direction uses:
1. structured tag-family vocabularies extracted from `app.json`
2. LLM/Cline semantic projection into ranked tags per family
3. deterministic local ranking against the full `app.json` corpus

This separates semantic expansion from final ranking and makes the local core easier to test.

**Core Tag Families:**
- `mechanic_tags`
- `semantic_tags`
- `mood_tags`
- `setting_tags`
- `character_tags`
- `games_tags`
- `franchise_tags`

**Key Decisions:**
- `games/published/public/app.json` remains the only source of truth
- all aggregated vocabularies and normalized game-tag documents must be rebuildable from `app.json`
- no title/description/prompt fields in the deterministic ranker for v2
- local scoring should be weighted by family importance plus selected-tag rank
- fixture expectations should be created first to validate the deterministic scorer before grounding the final Cline implementation

**Planned Weighting Model (initial draft):**
- mechanic tags × 5
- games tags × 4
- franchise tags × 4
- semantic tags × 3
- mood tags × 2
- character tags × 2
- setting tags × 1.5

Rank weighting draft:
- rank 1 = 1.0
- rank 2 = 0.8
- rank 3 = 0.6
- rank 4 = 0.4
- rank 5 = 0.2

**Output Contract Goal:**
Preserve compatibility with the current matcher-style JSON array:
- `game_id`
- `name`
- `url`
- `cover_url`
- `matched_queries`
- `coverage`
- `distance`
- `best_feed_position`
- `played_count`

**Sibling Cline Orchestration References:**
- `tools/game_refactoring/scripts/spec_adaptor.py`
- `tools/game_refactoring/scripts/run_operator_pipeline_game.py`
- `tools/game_refactoring/scripts/creative_refactor_runtime.py`

**Next Steps:**
- [ ] Scaffold `tools/game_matcher_v2/`
- [ ] Define aggregated family artifact files
- [ ] Define normalized per-game tag document format
- [ ] Implement deterministic scorer
- [ ] Create fixtures for selected-tag expectations and expected ranked outputs
- [ ] Only then add the Cline selector step

**Status:** In Progress

---

### 2026-05-14 02:40 - Cline selector integration landed

**What Changed:**
- Added `tools/game_matcher_v2/game_matcher_v2/selector.py` to implement the Cline-facing selector layer.
- Added `tools/game_matcher_v2/cli/match_prompt.py` to run the full flow: ensure artifacts, invoke selector, validate selected tags, and score games.
- Added `tmp/smoke_game_matcher_v2_selector.py` to smoke-test the selector workspace builder and deterministic scoring path with a controlled selected-tags payload.
- Preserved the deterministic scorer as the final ranking authority; the selector only chooses ranked tags from controlled vocabularies.

**Why:**
This is the core v2 architecture: semantic prompt interpretation should happen only in the selector stage, while the final game ranking remains deterministic and rebuildable from `app.json`.

**Selector Layer Responsibilities:**
- create a per-run workspace under `tools/game_matcher_v2/tmp/selector_runs/` (or an override path)
- copy slim tag-family catalogs into `workspace/catalog/*.json`
- write `selector_prompt.txt` and `selector_result_contract.json`
- invoke `cline -a <workspace> --model <model> <prompt>`
- require `workspace/selected_tags.json`
- validate that every chosen tag is copied exactly from the controlled vocabulary and that each family has unique ranks 1..5

**New Files:**
- `tools/game_matcher_v2/game_matcher_v2/selector.py`
- `tools/game_matcher_v2/cli/match_prompt.py`
- `tmp/smoke_game_matcher_v2_selector.py`

**Smoke Test Result:**
The temp smoke script successfully:
1. rebuilt/loaded deterministic artifacts
2. built a selector workspace for `flappy bird`
3. validated a controlled selected-tags payload
4. scored games and returned Flappy-Bird-family remixes at the top

Observed top results included:
- `Flappy Bird: Sky Cab Migration`
- `Flappy Bird: Skyway Migration`
- `Flappy Candy Rescue`

**Next Steps:**
- [ ] Run a true end-to-end invocation through `cline` using `tools/game_matcher_v2/cli/match_prompt.py`
- [ ] Add README usage for the new selector-backed CLI
- [ ] Consider exporting selector helpers from `game_matcher_v2/__init__.py` if import ergonomics matter later

**Status:** In Progress

---

### 2026-05-14 02:44 - Added projected compute cost accounting

**What Changed:**
- Extended `tools/game_matcher_v2/game_matcher_v2/selector.py` to include `game_refactoring`-style projected token pricing metadata.
- `selector_usage.json` now includes a `projectedCost` section with:
  - currency
  - pricing basis
  - per-million token rates
  - per-bucket cost breakdown
  - projected total
- `selector_result.json` now embeds the full `usage_summary` payload instead of only linking to the usage file path.

**Why:**
The selector step is the only compute-bearing task in `game_matcher_v2`, so each selector run should leave behind the same kind of auditable per-task cost record used by `game_refactoring`.

**Cost Model Added:**
- `inputTokens`: $5.00 / 1M
- `cacheReadTokens`: $0.50 / 1M
- `outputTokens`: $30.00 / 1M
- `cacheWriteTokens`: $0.00 / 1M

**Effect:**
Every selector task now persists:
- raw stdout/stderr
- invocation metadata
- normalized token usage
- projected USD cost per task
- embedded cost summary in the run result artifact

**Status:** In Progress

---

### 2026-05-14 03:09 - Replaced rank contract with normalized score

**What Changed:**
- Removed the selector-facing `rank` contract and replaced it with normalized `score` values in `[0.0, 1.0]`.
- Updated `tools/game_matcher_v2/game_matcher_v2/scorer.py` so deterministic weighting now uses the selector-provided score directly.
- Updated `tools/game_matcher_v2/game_matcher_v2/selector.py` prompt text, result contract, and validation rules to require score-based outputs.
- Updated fixture payloads and smoke scripts to the new score schema.
- Re-ran smoke testing and a live `cline` end-to-end prompt test after the migration.

**Why:**
The old rank contract only conveyed order. The normalized score contract preserves deterministic local scoring while giving the selector a more expressive confidence signal.

**Deterministic Effect:**
The deterministic architecture did not change. Only the per-tag weight source changed:
- old: `family_weight * rank_bucket_weight`
- new: `family_weight * selector_score`

**Verification:**
- score-based smoke script ran successfully
- live prompt run `python3 tools/game_matcher_v2/cli/match_prompt.py "flappy bird"` completed successfully under the new contract

**Status:** In Progress

---

## 📚 Quick Reference

### Key Files

- `games/published/public/app.json` - source-of-truth corpus
- `tools/game_matcher/cli/game_matcher_cli.py` - existing matcher CLI contract
- `tools/game_matcher/matcher/cli_support.py` - current matcher output shape and local ranking helpers
- `tools/game_refactoring/scripts/spec_adaptor.py` - sibling Cline orchestration reference
- `tools/game_refactoring/scripts/run_operator_pipeline_game.py` - sibling worker invocation reference
- `tools/game_refactoring/scripts/creative_refactor_runtime.py` - sibling execution/runtime capture reference

### Notes & Decisions

**Decision:** Exclude title/description/prompt from v2 deterministic ranking  
**Rationale:** Keep v2 ontology-first and reduce lexical noise. Use only structured tag families.

**Decision:** Build deterministic local ranking before the Cline selector integration  
**Rationale:** This allows fixture-based validation and isolates scoring quality from LLM behavior.

**Decision:** Make all artifacts rebuildable from `app.json`  
**Rationale:** `app.json` is dynamic, so derived vocabularies and normalized documents must refresh easily and deterministically.