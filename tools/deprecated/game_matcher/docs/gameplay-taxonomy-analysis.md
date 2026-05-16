# Gameplay Taxonomy Analysis for the CLI Matcher

## Purpose

This document ties together the CLI matcher behavior, the local reverse-index schema, and the upstream Rezona gameplay taxonomy that ultimately feeds the matcher data.

It summarizes the investigation performed for the `top800` matcher subset and records the grounded meaning of the numeric `category` / `mechanic_family` labels found in the reverse-index artifacts.

---

## 1. CLI matching flow

The CLI entrypoint is:

- `cli/game_matcher_cli.py`

It supports two input modes:

- free-text prompt matching
- direct source URL lookup via `--url`

### Prompt mode flow

1. Load `.env` and read `OPENAI_API_KEY`
2. Load the shared allowed query vocabulary from:
   - `fixtures/consolidated/all_queries.json`
3. Load the selected reverse index:
   - default: `fixtures/consolidated/top800_master_game_reverse_index.json`
   - optional full corpus: `fixtures/consolidated/master_game_reverse_index.json` via `--index all`
4. Use OpenAI to translate the free-text prompt into up to 10 allowed query strings
5. Rank games locally and deterministically against the chosen reverse index
6. Return trimmed JSON output

### URL mode flow

When `--url` is provided, the CLI:

1. Normalizes the source URL
2. Searches the selected reverse index for an exact normalized URL match
3. Returns a single game record if found

No prompt-to-query translation or ranking happens in URL mode.

---

## 2. What the `top800` subset really is

Despite the `top800` name, the current allowlist-derived subset contains:

- **796 games**

This was verified during subset generation and is documented in:

- `docs/journals/cli-matcher.md`
- `fixtures/consolidated/top800_master_game_reverse_index_summary.json`

The CLI defaults to this 796-game subset unless `--index all` is passed.

---

## 3. Reverse-index data model used by the matcher

The relevant downstream artifact is:

- `fixtures/consolidated/top800_master_game_reverse_index.json`

The matcher expects each game entry to contain fields such as:

- `game_id`
- `name`
- `url`
- `queries`
- `query_categories`
- `query_matches`
- `query_count`
- `played_count`
- `stats`

The most important ranking field is:

- `query_matches`

Each query match may contain metadata like:

- `query`
- `feed_position`
- `exact_match`
- `category`
- `subcategory`
- `mechanic_family`
- `query_type`
- `priority`
- `run_id`

---

## 4. What the matcher is actually doing

The CLI does **not** directly perform semantic embedding search over games.

Instead it performs a two-stage flow:

1. **prompt -> query selection**
   - the model chooses up to 10 exact query strings from the allowed vocabulary

2. **query selection -> local game ranking**
   - the reverse index is scored locally using:
     - missing-query penalties
     - feed-position penalties
     - exact-match bonuses
     - prompt overlap bonuses
     - popularity boosts

So the reverse index and its query taxonomy are central to retrieval quality.

---

## 5. Category vs mechanic_family vs synthetic expansion

During analysis of the top800 reverse index we found that:

- `query_categories` is a coarse game-level summary
- `category` is a coarse query bucket
- `mechanic_family` is a more useful gameplay-oriented grouping
- `intent_generated` represents synthetic expansion output rather than grounded gameplay taxonomy

### Important observation

There is **no literal `mechanic` category** in the top800 reverse index.

So if the question is “does every game have category = mechanic?”, the answer is no.

The better gameplay signal is `mechanic_family`, but even that contains a mixture of:

- genuine gameplay families
- hybrid/theme families
- synthetic/noise families

---

## 6. Synthetic / noise coverage findings

Using a first-pass synthetic/noise definition of:

- `intent_generated`
- `structure`

the top800 reverse index produced the following results:

- total games: **796**
- games with at least one synthetic/noise label: **166**
- games with only synthetic/noise labels: **23**
- total query matches: **13,415**
- synthetic/noise query matches: **7,101**
- synthetic/noise share of query matches: **52.93%**

### Interpretation

At the game level, synthetic contamination is moderate:

- about **20.9%** of games have at least some synthetic/noise labeling

At the query-match level, synthetic expansion is dominant:

- about **52.9%** of all query matches are synthetic/noise by this first-pass definition

This means raw query counts can significantly overstate grounded gameplay coverage.

---

## 7. Mechanic-family distribution findings

Using a first-pass allowlist of mechanic-oriented `mechanic_family` values, we counted how many games had at least one match in each family.

Top counts included:

- `3` -> 117
- `2` -> 106
- `4` -> 96
- `15` -> 70
- `1` -> 65
- `14` -> 64
- `5` -> 62
- `23` -> 60
- `21` -> 52
- `12` -> 50
- `11` -> 28
- `idle` -> 25
- `31` -> 24
- `match3` -> 21
- `runner` -> 21

These counts are **non-exclusive**. A single game may contribute to multiple mechanic families.

---

## 8. Upstream provenance: where the numeric labels come from

The most important breakthrough came from inspecting sibling project files in:

- `../resonalyzer2/queries/gameplay_query_library.json`
- `../resonalyzer2/queries/gameplay_query_library_expanded_clean.json`
- `../resonalyzer2/docs/gameplay-query-expansion-master-list.md`

### Seed library behavior

In the readable upstream gameplay query library, entries use semantic labels such as:

- `category = movement`
- `subcategory = runner`
- `mechanic_family = runner`

Example seed queries:

- `subway surfers`
- `temple run`
- `endless runner`

### Expanded library behavior

In the expanded clean library, the same queries become:

- `category = "1"`
- `subcategory = "expanded"`
- `mechanic_family = "1"`

This shows that the numeric labels are **not arbitrary latent classes**.

They are **section IDs from the upstream gameplay query expansion master list**.

---

## 9. Grounded numeric taxonomy legend

The grounded numeric taxonomy legend is stored in:

- `fixtures/consolidated/gameplay_taxonomy_numeric_legend.json`

That file was derived from:

- `../resonalyzer2/docs/gameplay-query-expansion-master-list.md`

The upstream master list contains **33 numbered sections**:

1. Core Movement / Runner / Platformer
2. Puzzle / Logic / Match / Draw / Sorting
3. Merge / Idle / Clicker / Tycoon
4. Survivor / Shooter / Defense / Combat
5. Driving / Vehicle / Traffic / Parking
6. Simulation / Management / Cooking / Farming / Life
7. Lifestyle / Fashion / Makeover / Home Design
8. Trivia / Quiz / Social Prompt / Party
9. Dating / Romance / Flirting / Rizz
10. Interactive Story / Chat Fiction / Choice Based
11. Arcade / Skill / Hypercasual / Physics Toy
12. IO / Crowd / Swarm / Territory
13. Sports / Ball / Competition
14. Board / Card / Casino / Word / Classic
15. Sandbox / Building / Crafting / Open World / Destruction
16. Horror / Scary / Thriller / Monster
17. Major Franchises / Pop Culture / Clone Bait
18. Kids / Family / Cartoon / Audience Terms
19. Viral / Meme / TikTok / Trend / Prank
20. Broad Genre / Intent / Discovery Catch-All
21. Battle Royale / Extraction / Multiplayer PvP
22. Open World Crime / Urban Fantasy / Heist
23. Sandbox Creator / UGC / Build-and-Share
24. Anime / Manga / Otaku / Fan Intent
25. Superhero / Comic / Action Fantasy
26. Monster / Creature / Animal Fantasy
27. School / Teen / Life Drama / Social Identity
28. Family / Parenting / Baby / Home Life
29. Food / Dessert / Kitchen / Cozy Casual
30. Beauty / Salon / Self-Care / ASMR
31. Music / Dance / Rhythm / Performance
32. Meme / Internet / Social Platform Fantasies
33. Hypercasual Ad-Bait / Ultra-Broad Retrieval

---

## 10. Best interpretation of the taxonomy stack

### Seed taxonomy
Human-readable upstream taxonomy with labels like:

- movement
- runner
- puzzle
- match3
- runner

### Expanded taxonomy
Collapsed numeric section IDs like:

- `1`
- `2`
- `3`

These propagate into downstream query artifacts.

### Matcher reverse index
The matcher inherits those numeric IDs in fields like:

- `category`
- `mechanic_family`

and also mixes in:

- named mechanic-family labels
- synthetic intent-generated expansions
- hybrid/theme families

---

## 11. Practical guidance for future analysis

If the goal is gameplay-mechanic auditing, the safest order of trust is:

1. **named grounded mechanic families**
   - e.g. `runner`, `match3`, `merge`, `sort`, `tower_defense`

2. **grounded numeric labels with official upstream legend**
   - e.g. `1`, `2`, `3`, `4`, `21`, `23`, `31`

3. **hybrid/theme categories**
   - useful in some cases, but less clean as mechanics

4. **synthetic/noise labels**
   - especially `intent_generated`

### Recommended split for analysis

#### Mechanic-centric numeric families
- 1, 2, 3, 4, 5, 11, 12, 13, 14, 21, 23, 31

#### Hybrid families
- 6, 7, 8, 9, 10, 15, 22, 29, 30

#### Theme/fantasy families
- 16, 24, 25, 26, 27, 28

#### Broad/noisy families
- 17, 18, 19, 20, 32, 33

This split is interpretive and intended for local auditing rather than as a strict upstream guarantee.

---

## 12. Related files in this repository

### Primary matcher/runtime files
- `cli/game_matcher_cli.py`
- `matcher/cli_support.py`

### Primary matcher data files
- `fixtures/consolidated/all_queries.json`
- `fixtures/consolidated/master_game_reverse_index.json`
- `fixtures/consolidated/top800_master_game_reverse_index.json`
- `fixtures/consolidated/top800_master_game_reverse_index_summary.json`
- `fixtures/consolidated/gameplay_taxonomy_numeric_legend.json`

### Journal
- `docs/journals/cli-matcher.md`

---

## 13. Related upstream sibling-project files used for grounding

These files are outside this repository but were used to recover the numeric-label legend:

- `../resonalyzer2/queries/gameplay_query_library.json`
- `../resonalyzer2/queries/gameplay_query_library_expanded_clean.json`
- `../resonalyzer2/docs/gameplay-query-expansion-master-list.md`

---

## 14. Summary

The CLI matcher is downstream of a query-taxonomy pipeline built in sibling Rezona projects.

The key findings are:

- the CLI defaults to a 796-game `top800` subset
- ranking is driven by query translation plus deterministic local reverse-index scoring
- the reverse index mixes grounded and synthetic query signals
- `intent_generated` is a major source of noise at the query-match level
- the numeric `category` / `mechanic_family` labels are grounded upstream section IDs
- the official 1–33 legend has now been recovered and stored locally in:
  - `fixtures/consolidated/gameplay_taxonomy_numeric_legend.json`

This gives the repository a local, durable reference for interpreting the taxonomy that the matcher currently consumes.