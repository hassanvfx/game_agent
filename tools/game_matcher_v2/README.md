# game_matcher_v2

`game_matcher_v2` is a tag-family-driven matcher built from `games/published/public/app.json`.

It separates matching into two layers:

1. **Selector layer via Cline**
   - takes a freeform user prompt
   - projects it into a controlled tag vocabulary by family
   - returns validated per-family selected tags with normalized `score` values in `[0.0, 1.0]`

2. **Deterministic local scorer**
   - loads only structured tag families from `app.json`
   - ignores title, description, and prompt text
   - ranks games locally from the selector output

This keeps semantic interpretation separate from final ranking, while ensuring the corpus-side ranking remains rebuildable and testable.

## Source of truth

Default source:

```text
games/published/public/app.json
```

All derived artifacts must be rebuildable from this file.

## Tag families

The scorer uses these structured families:

- `mechanic_tags`
- `semantic_tags`
- `mood_tags`
- `setting_tags`
- `character_tags`
- `games_tags`
- `franchise_tags`

## Weighting model

Family weights:

- mechanic tags × 5
- games tags × 4
- franchise tags × 4
- semantic tags × 3
- mood tags × 2
- character tags × 2
- setting tags × 1.5

Per-tag contribution:

```text
family_weight * selector_score
```

Where `selector_score` is a normalized float in `[0.0, 1.0]` chosen by the selector.

## Artifact build workflow

### 1. Build derived artifacts

Generate:

- aggregated tag-family vocabularies
- normalized per-game tag documents
- metadata with source fingerprint

Example:

```bash
python3 tools/game_matcher_v2/cli/build_artifacts.py
```

## Selector contract

The selector must choose tags only from the controlled family vocabularies and emit this shape:

```json
{
  "mechanic_tags": [
    {"tag": "tap to flap", "score": 0.98},
    {"tag": "endless run structure", "score": 0.84}
  ],
  "semantic_tags": [
    {"tag": "arcade", "score": 0.78}
  ],
  "mood_tags": [],
  "setting_tags": [],
  "character_tags": [],
  "games_tags": [
    {"tag": "Flappy Bird", "score": 0.92}
  ],
  "franchise_tags": []
}
```

Validation rules:

- every tag must exist in the controlled vocabulary for that family
- every `score` must be a float in `[0.0, 1.0]`
- invalid or out-of-vocabulary entries are dropped
- the run fails only if no valid selected tags remain after validation

## End-to-end CLI

Run the full flow:

1. ensure artifacts exist
2. invoke the Cline selector
3. validate selected tags
4. score games locally
5. return matcher-style ranked results

Example:

```bash
python3 tools/game_matcher_v2/cli/match_prompt.py "flappy bird"
```

Useful flags:

```bash
python3 tools/game_matcher_v2/cli/match_prompt.py \
  "angry birds" \
  --limit 10 \
  --selected-tags-out tmp/angry_selected_tags.json \
  --out tmp/angry_ranked_games.json
```

The CLI also prints the selector run-artifact directory to stderr so each run can be inspected later.

## Output contract

The final scored output preserves the matcher-style result array used elsewhere in the project:

- `game_id`
- `name`
- `url`
- `cover_url`
- `matched_queries`
- `coverage`
- `distance`
- `best_feed_position`
- `played_count`

`matched_queries` is retained for downstream compatibility even though v2 internally matches from selected tags rather than legacy query strings.

## Selector artifacts and cost tracking

Each selector run writes auditable artifacts under the configured runs directory, including:

- selector prompt
- invocation metadata
- stdout / stderr
- validated selected tags
- usage summary
- projected token cost

Projected pricing currently uses:

- `inputTokens`: $5.00 / 1M
- `cacheReadTokens`: $0.50 / 1M
- `outputTokens`: $30.00 / 1M
- `cacheWriteTokens`: $0.00 / 1M

## Intended `game_generator` handoff

The current `game_generator` pipeline expects the matcher stage to return a ranked matcher-style list, then selects top results and resolves each selected game's source path before launching the remixer/editor flow.

`game_matcher_v2` is designed to slot into that same boundary:

1. `match_prompt.py` returns ranked matcher-style game results
2. the pipeline selects the top N games it wants to remix
3. the pipeline resolves each selected result into a source directory
4. the remixer/editor consumes those resolved source directories

In other words, the generator/remixer handoff should continue to operate on **resolved game selections**, while `game_matcher_v2` improves only the upstream prompt-to-match selection step.

If the pipeline wants richer context later, the most useful extra artifact to pass along is the validated selected-tags payload from the selector run, alongside the ranked match list.

## Current status

- deterministic scorer: implemented
- selector-backed end-to-end CLI: implemented
- score-based selector contract: implemented
- projected selector cost accounting: implemented
- pipeline integration into `game_generator`: pending