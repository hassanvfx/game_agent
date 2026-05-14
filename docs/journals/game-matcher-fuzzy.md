# Game Matcher Fuzzy Implementation Journal

**Last Updated:** 2026-05-14  
**Feature Spec:** New Whoosh-based `game_matcher_fuzzy` tool compatible with `game_generator` matcher contract  
**Backend Reference:** N/A

---

## 📊 Implementation Status Overview

### ✅ Phase 1: Discovery and Contract Mapping - **COMPLETE**

- [x] Inspect current `game_matcher` CLI contract
- [x] Inspect `game_generator` matcher invocation
- [x] Inspect local published game metadata source
- [x] Confirm dependency strategy for Whoosh
- [x] Finalize output compatibility requirements

**Status:** ✅ Complete

### Phase 2: Tool Scaffolding - **REMOVED**

- [x] Create `tools/game_matcher_fuzzy/` structure
- [x] Add CLI entrypoints for build and query
- [x] Add README and version metadata
- [x] Add package/module layout

**Status:** Removed after evaluation

### Phase 3: Indexing and Query Implementation - **FAILED / REMOVED**

- [x] Build Whoosh index from `games/published/public/app.json`
- [x] Support optional `--app-json` override
- [x] Add lazy auto-build when index is missing
- [x] Add MD5-based rebuild detection
- [x] Emit results in `game_matcher`-compatible JSON shape
- [x] Evaluate retrieval quality on representative prompts
- [x] Remove the tool after failed quality evaluation

**Status:** Failed concept validation

---

## 📝 Journal Entries

### 2026-05-14 00:23 - Initial discovery and implementation plan

**What Changed:**
- Created this journal for the new `game_matcher_fuzzy` workstream.
- Inspected the current `game_matcher` CLI and its output contract.
- Inspected the `game_generator` matcher invocation contract.
- Confirmed the structured metadata source lives in `games/published/public/app.json`.

**Why:**
The new fuzzy matcher should be introduced as a parallel tool with the same external contract, minimizing risk to the current pipeline and allowing side-by-side validation before any swap-over.

**Files Investigated:**
- `tools/game_matcher/cli/game_matcher_cli.py` - Existing CLI inputs and JSON output behavior
- `tools/game_matcher/matcher/cli_support.py` - Existing output shape helpers and ranking expectations
- `tools/game_generator/scripts/run_pipeline.py` - Existing matcher invocation path and subprocess contract
- `games/published/public/app.json` - Structured source-of-truth game metadata for indexing
- `requirements.txt` - Current project dependency baseline

**Technical Decisions:**
- Use `games/published/public/app.json` as the primary index source instead of parsing `app.js` in v1.
- Keep a separate `game_matcher_fuzzy` tool rather than replacing `game_matcher` directly.
- Preserve the prompt-based JSON array output contract used by `game_generator`.
- Provide an explicit build-index command and lazy auto-build at query time when the index is missing.
- Add source fingerprint metadata using MD5 of the source `app.json` to detect when rebuilds are required.
- Support a default source path plus optional override via `--app-json`.

**Findings:**
- Current matcher CLI accepts:
  - positional `prompt`
  - `--limit`
  - `--out`
  - `--env-file`
  - `--index`
  - `--url`
- Current generator invocation is effectively:
  - `python3 cli/game_matcher_cli.py <prompt> --limit <n>`
- Current generator expects a JSON array of objects containing fields like:
  - `game_id`
  - `name`
  - `url`
  - `cover_url`
  - `matched_queries`
  - `coverage`
  - `distance`
  - `best_feed_position`
  - `played_count`

**Blockers / Risks:**
- `whoosh` is not currently installed in the environment.
- It is not yet present in `requirements.txt`, so dependency strategy needs to be finalized before implementation can complete cleanly.

**Next Steps:**
- [ ] Decide how to add/install `whoosh`
- [ ] Scaffold `tools/game_matcher_fuzzy`
- [ ] Implement index builder from `app.json`
- [ ] Implement query CLI with lazy build and MD5-based staleness detection
- [ ] Validate emitted JSON shape against `game_generator`

**Status:** In Progress

---

## 🐛 Known Issues

### Pure lexical Whoosh retrieval was insufficient

**Problem:**  
A standalone Whoosh-based matcher over `games/published/public/app.json` did not produce sufficiently reliable semantic retrieval quality for target prompts.

**Root Cause:**  
The corpus contains rich metadata, but purely lexical weighted-field matching was not enough for semantic expansion and concept bridging. Representative failures included:
- `kawaii` returning no useful results
- `mario bros` returning weak or irrelevant matches
- partial success on direct lexical prompts like `flappy bird`, but inconsistent behavior on broader semantic prompts

**Status:**  
- [x] Being investigated
- [x] Fixed

**Workaround:**  
Keep the existing LLM-assisted matcher path for semantic query expansion.

**Resolution:**  
The experimental `tools/game_matcher_fuzzy` implementation was removed. The retained conclusion is that semantic expansion still requires an LLM-assisted step rather than a purely local Whoosh index over current metadata.

---

## 📚 Quick Reference

### Key Files

- `tools/game_matcher/cli/game_matcher_cli.py` - Existing matcher CLI contract
- `tools/game_matcher/matcher/cli_support.py` - Existing output schema helpers
- `tools/game_generator/scripts/run_pipeline.py` - Current matcher subprocess caller
- `games/published/public/app.json` - Primary fuzzy index source
- `requirements.txt` - Project dependency manifest

### Important Commands

```bash
python3 -c "import whoosh; print(whoosh.__file__)"
```

### Notes & Decisions

**Decision:** Use `app.json` as the database for fuzzy matching  
**Rationale:** It already contains normalized title, description, prompt, and rich tag fields per game/remix entry, which is a much better source for Whoosh than raw `app.js`.

**Decision:** Add MD5-based rebuild detection against source `app.json`  
**Rationale:** This ensures the cached search index is rebuilt when the source content changes, while avoiding rebuilds on every query.

**Decision:** Default to `games/published/public/app.json` with `--app-json` override  
**Rationale:** Sensible default for local usage while preserving flexibility for alternate corpora.