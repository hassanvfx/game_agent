# game_matcher_v2

Deterministic tag-family matcher built from `games/published/public/app.json`.

## Purpose

`game_matcher_v2` separates matching into two layers:

1. **Deterministic local ranking**
   - built directly from `games/published/public/app.json`
   - uses only structured tag families
   - does not use title, description, or prompt text

2. **Future agent/Cline semantic projection**
   - prompt in
   - ranked tags per family out
   - feeds the deterministic ranker

The deterministic core is implemented first so it can be tested independently using fixture expectations.

## Source of truth

Default source:

```text
games/published/public/app.json
```

All derived artifacts should be rebuildable from this file.

## Tag families

The deterministic ranker uses these tag families:

- `mechanic_tags`
- `semantic_tags`
- `mood_tags`
- `setting_tags`
- `character_tags`
- `games_tags`
- `franchise_tags`

## Planned weighting model

Initial draft:

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

## Deterministic workflow

### 1. Build artifacts
Generate:
- aggregated tag-family vocabularies
- normalized per-game tag documents
- metadata with source fingerprint

### 2. Rank from selected tags
Input shape:

```json
{
  "mechanic_tags": [{"tag": "Endless runner", "rank": 1}],
  "semantic_tags": [{"tag": "arcade", "rank": 1}],
  "mood_tags": [],
  "setting_tags": [],
  "character_tags": [],
  "games_tags": [{"tag": "Flappy Bird", "rank": 1}],
  "franchise_tags": []
}
```

Output:
- ranked game list in the current matcher-compatible contract

## Contract goal

The final CLI should preserve the current matcher-style output array:

- `game_id`
- `name`
- `url`
- `cover_url`
- `matched_queries`
- `coverage`
- `distance`
- `best_feed_position`
- `played_count`

## Status

Deterministic scorer phase in progress.