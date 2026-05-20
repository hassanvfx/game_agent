# Audio Library

Reusable MP3 audio catalog for the operator-pipeline audio mapping pass.

This folder supports two things:

1. A local/staging workflow for messy generated audio filenames.
2. A CDN-backed runtime index at `assets/audios/audios.json`.

The trusted CDN base URL is:

```text
https://gamezone-virid.vercel.app/assets/audios/
```

## Folder Layout

```text
assets/audios/
  README.md
  manifest.json
  audios.json
  catalog.json
  incoming/
  unmatched/
  sfx/
  ui/
  music/
  ambience/
```

## Canonical Merge Workflow

This library now has a **canonical merged catalog** plus a **cache-aware generator flow**:

1. `audios.json` remains the concrete inventory of materialized audio files.
2. `catalog.json` is the merged canonical source combining:
   - concrete library asset families
   - semantic query/regeneration records sourced from `tools/game_refactoring/catalogs/audios.json`
3. `jobs_list.json` is the flat operational ledger whose status is reconciled from disk.
4. `catalog_final.json` is a disk-reconciled final/materialized snapshot in `catalog.json`-compatible shape.
5. generator scripts use the canonical catalog to:
   - choose the Suno route (`suno-sounds` for SFX, `suno-music` for music-like assets)
   - submit async jobs
   - poll until completion
   - download outputs
   - rename them into the expected filename family
   - place them into the library tree

### Build the merged canonical catalog

```bash
python3 tools/library/scripts/build_audio_catalog.py
```

This writes:

```text
tools/library/assets/audios/catalog.json
```

### Build the disk-reconciled final catalog snapshot

```bash
python3 tools/library/scripts/build_audio_catalog_final.py --desired-total-variants 4 --variants-per-request 2
```

This writes:

```text
tools/library/assets/audios/catalog_final.json
```

`catalog_final.json` preserves the planner record shape from `catalog.json`, but rewrites
concrete `variants` and semantic `reference_items` to the materialized disk state and
adds per-record `materialized` status fields such as:

- `existing_count`
- `missing_variants`
- `next_variant_numbers`
- `next_destinations`
- `status`

### Preview cache-aware generation behavior

```bash
python3 tools/library/scripts/generate_audio_variants.py --dry-run --record-id jump --desired-count 3
```

### Important generator behavior

- existing files are skipped by default
- generation continues record-by-record even when a prior item fails
- use `--overwrite-all` to force regeneration/replacement of already existing target filenames
- async KIE/Suno job state is written under the library jobs tree for resumability/debugging

## Normalized Jobs List

For unattended generation, use the normalized flat jobs file:

```bash
python3 tools/library/scripts/build_audio_jobs_list.py --desired-total-variants 4 --variants-per-request 2
```

This writes:

```text
tools/library/assets/audios/jobs_list.json
```

If you want one stable command that reconciles first, runs missing jobs, and then
refreshes local artifacts again, use:

```bash
python3 tools/library/scripts/reconcile_audio_artifacts.py
```

That launcher does three phases:

1. reconcile planner state into `jobs_list.json` + `catalog_final.json`
2. run missing jobs via the batch runner
3. refresh local JSON artifacts again after the run

By default, this launcher now behaves like:

```bash
python3 tools/library/scripts/reconcile_audio_artifacts.py --include-semantic-query --verbose-stages
```

So the bare command means:

- run **all jobs** by default, including semantic jobs
- show **per-item funnel/stage output** by default

It rebuilds both final local artifacts:

- `tools/library/assets/audios/jobs_list.json`
- `tools/library/assets/audios/catalog_final.json`

Helpful variants:

```bash
# reconcile only, do not run generation
python3 tools/library/scripts/reconcile_audio_artifacts.py --reconcile-only

# dry-run the full reconcile + run + refresh workflow
python3 tools/library/scripts/reconcile_audio_artifacts.py --dry-run --max-records 3

# force concrete-only mode
python3 tools/library/scripts/reconcile_audio_artifacts.py --concrete-only

# disable per-item funnel output
python3 tools/library/scripts/reconcile_audio_artifacts.py --quiet
```

The older tmp helper still works as a compatibility wrapper:

```bash
python3 tmp/reconcile_flat_jobs_ledger_from_disk.py
```

## Runtime Compatibility Mapping Layer

The published runtime audit showed that most remaining mismatches are not unknown
audio concepts; they are mostly **taxonomy drift** between published runtime paths
and the canonical library paths.

This repo now keeps a permanent compatibility-mapping manifest at:

```text
tools/library/assets/audios/deploy_audio_mappings.json
```

It is split into two mapping tiers:

1. `reduced_aliases`
   - low-risk compatibility reroots
   - example: `ui/game_over_01.mp3` → `sfx/game_over_01.mp3`
2. `enriched_aliases`
   - curated semantic polyfills
   - example: `ui/ui_click_01.mp3` → `ui/click_01.mp3`

The same manifest also records legacy/outlier prefixes that should later be
sanitized to empty string in the obfuscator/publication compatibility pass:

- `assets/bgm/0001/`
- `assets/sfx/0001/`
- `assets/audio/0000/`

To validate current mapping coverage against the latest audit artifact, run:

```bash
python3 tools/library/scripts/validate_deploy_audio_mappings.py
```

That script checks:

- whether every mapped `source_location` exists in `audios.json`
- how many high-priority runtime mismatch paths are already covered by the
  reduced + enriched mapping layers

This mapping manifest is intended to be the source of truth for the future
`deploy_audios.py` workflow, where deployment can happen in two stages:

1. canonical library files + reduced aliases
2. enriched semantic polyfills layered on top

The deploy script now exists at:

```bash
python3 tools/library/scripts/deploy_audios.py --stage all --dry-run
```

By default it targets the sibling library tree:

```text
../game_agent_library/assets/audios
```

Stage behavior:

```bash
# stage 1: canonical + reduced aliases
python3 tools/library/scripts/deploy_audios.py --stage reduced

# stage 2: enriched aliases only, layered on top
python3 tools/library/scripts/deploy_audios.py --stage enriched

# one-shot full deploy
python3 tools/library/scripts/deploy_audios.py --stage all
```

Each run writes a JSON report to:

```text
../game_agent_library/assets/audios/deploy_audio_report.json
```

unless you override it with `--report-path`.

Each job record contains the concrete prompt + destination mapping for one real
library asset family, plus generation planning fields such as:

- `destination_pattern`
- `existing_count`
- `missing_variants`
- `variants_per_request`
- `requests_needed`

`variants_per_request` defaults to `2` because Suno commonly returns two audio
items per request in this workflow.

The jobs list can also include semantic/world records in the same normalized
shape, distinguished by:

- `record_type: "asset_family"`
- `record_type: "semantic_query"`

For semantic jobs, the reconciled destination fields now preserve the original
Vercel taxonomy when it already exists in the source references. That means
semantic jobs use destination patterns like:

- `assets/audios/bgm/forest_bgm_{nn:02d}.mp3`
- `assets/audios/sfx/forest_enemy_{nn:02d}.mp3`

instead of rewriting those records into a synthetic `semantic/...` path.

The unattended overnight batch runner still processes only `asset_family`
records by default.

To include semantic/world jobs too, use:

```bash
python3 tools/library/scripts/run_audio_jobs_batch.py --include-semantic-query --desired-total-variants 4 --variants-per-request 2
```

That expands execution from the default concrete-only set to the full reconciled
job list, including semantic records whose destinations preserve the original
`assets/audios/...` taxonomy.

For verbose per-item stage logging during execution, add:

```bash
python3 tools/library/scripts/run_audio_jobs_batch.py --include-semantic-query --verbose-stages
```

This prints stage lines for each job, for example:

- record start
- request planned
- submit started / succeeded / failed
- poll started / succeeded / failed
- outputs resolved
- download started
- materialize generated

## Unattended Resumable Batch Runner

To run an overnight/resumable batch over the concrete library families:

```bash
python3 tools/library/scripts/run_audio_jobs_batch.py --desired-total-variants 4 --variants-per-request 2
```

Helpful options:

```bash
# dry-run planning only
python3 tools/library/scripts/run_audio_jobs_batch.py --dry-run --max-records 3

# limit the run while testing
python3 tools/library/scripts/run_audio_jobs_batch.py --max-records 5

# run only selected families
python3 tools/library/scripts/run_audio_jobs_batch.py --record-id jump --record-id action_loop

# run the full reconciled batch, including semantic_query jobs
python3 tools/library/scripts/run_audio_jobs_batch.py --include-semantic-query

# run the full reconciled batch with verbose per-stage logs
python3 tools/library/scripts/run_audio_jobs_batch.py --include-semantic-query --verbose-stages
```

Batch state is written to:

```text
tools/library/assets/audios/jobs/batch/latest_batch_state.json
```

The runner is resumable because it:

- rebuilds the normalized jobs list from the current catalog
- skips already-complete families by default
- writes per-job results and batch state
- can be re-run safely after interruption

## Downstream View Policy

For now, downstream views should be regenerated **explicitly**, not implicitly.

That means:

- `catalog.json` and `audios.json` are updated during generation
- the semantic/refactoring-side view is **not** auto-rewritten by the overnight batch

This keeps unattended runs focused on the concrete library taxonomy and avoids
surprising side effects outside the library workflow.

## Sanitizer Workflow

Place generated MP3 files with prompt-like filenames in:

```text
assets/audios/incoming/
```

Preview what will happen:

```bash
python3 scripts/sanitize_audio_library.py --dry-run
```

Apply the sanitizer:

```bash
python3 scripts/sanitize_audio_library.py --apply
```

The sanitizer copies files into clean locations and updates:

```text
assets/audios/audios.json
```

Original files in `incoming/` are not deleted.

## Output Naming

All audio files are MP3.

Examples:

```text
sfx/jump_01.mp3
sfx/jump_02.mp3
sfx/damage_01.mp3
ui/click_01.mp3
music/action_loop_01.mp3
ambience/spooky_loop_01.mp3
```

The matching CDN URLs are derived from the local location:

```text
sfx/jump_01.mp3
```

becomes:

```text
https://gamezone-virid.vercel.app/assets/audios/sfx/jump_01.mp3
```

## `audios.json` Shape

`audios.json` is grouped by semantic audio category.

Each audio item has exactly:

```text
name
url
location
usage
audio_type
```

`audio_type` is one of:

```text
one_shot
loop
```

Example:

```json
{
  "jumps": [
    {
      "name": "jump_01",
      "url": "https://gamezone-virid.vercel.app/assets/audios/sfx/jump_01.mp3",
      "location": "sfx/jump_01.mp3",
      "usage": "Player jump, bounce, upward movement",
      "audio_type": "one_shot"
    }
  ],
  "ambient_loops": [
    {
      "name": "ambient_loop_01",
      "url": "https://gamezone-virid.vercel.app/assets/audios/music/ambient_loop_01.mp3",
      "location": "music/ambient_loop_01.mp3",
      "usage": "Default background music",
      "audio_type": "loop"
    }
  ]
}
```

## Groups

```text
jumps
lands
shoots
projectiles
hits
damages
enemy_hits
enemy_defeats
pickups
bonuses
powerups
explosions
blocked_actions
warnings
successes
failures
game_overs
level_completes
clicks
hovers
starts
pauses
resumes
menu_opens
menu_closes
ambient_loops
action_loops
victory_loops
defeat_loops
soft_magic_loops
spooky_loops
arcade_loops
```

## Audio Type Rules

```text
sfx/*      -> one_shot
ui/*       -> one_shot
music/*    -> loop
ambience/* -> loop
```

## Runtime Rules

- Audio URLs must come from `assets/audios/audios.json`.
- The audio operator must not invent remote audio URLs.
- The approved CDN prefix is `https://gamezone-virid.vercel.app/assets/audios/`.
- Missing optional audio should degrade safely without crashing.
- Do not add autoplay behavior that blocks game boot.
- User gesture requirements should be respected by initializing audio after click/tap/start.
- The audio operator should preserve existing gameplay mechanics.

## Mirrored Local Root

The local cache/materialization root now mirrors the Vercel taxonomy more
directly:

```text
tools/library/assets/audios/
```

instead of the older:

```text
tools/library/audio_library/
```

That means local files now live under the same conceptual tree shape as their
published Vercel counterparts, while generation jobs still target relative
subpaths like:

- `sfx/jump_03.mp3`
- `music/action_loop_03.mp3`
- `assets/audios/bgm/calm_bgm_01.mp3` for semantic jobs

The library scripts also reconcile catalog/index state against the filesystem
before planning jobs, so deleted files are treated as missing and become pending
again automatically.

## Canonical Events

The older `manifest.json` still records the canonical event names and preferred clean locations. `audios.json` is the runtime-friendly grouped index for multiple variants.

Canonical events:

```text
ui_click
ui_hover
start_game
pause
resume
menu_open
menu_close
jump
land
shoot
projectile
hit
damage
enemy_hit
enemy_defeat
pickup
bonus
powerup
explosion
blocked
warning
success
fail
game_over
level_complete
ambient_loop
action_loop
victory_loop
defeat_loop
soft_magic_loop
spooky_loop
arcade_loop
```

## Short Generative Prompts

Use these short prompts when generating source MP3s. After generation, drop the files into `incoming/`; the sanitizer will infer the clean category from the prompt-like filename.

### One-Shots

#### `jump`

```text
Playful upward jump sound with a quick pitch rise, light bounce, and tiny magical sparkle. Clean arcade-fantasy feel.
```

#### `land`

```text
Soft landing thump with a padded impact and subtle dust puff. Gentle, non-violent, game-ready.
```

#### `shoot`

```text
Magical casting shot with a quick wand-like whoosh and bright sparkle attack. Not gun-like.
```

#### `projectile`

```text
Fast magical projectile zip with airy shimmer and tiny particle sparkle. Lightweight and energetic.
```

#### `hit`

```text
Compact arcade hit sound with a soft bonk impact and slight sparkle. Clear but non-violent.
```

#### `damage`

```text
Player damage cue with a short descending blip and soft impact. Mild, readable, family-friendly.
```

#### `enemy_hit`

```text
Enemy hit cue with a quick magical pop, small crunchy impact, and sparkle dust.
```

#### `enemy_defeat`

```text
Whimsical enemy defeat poof with sparkles and a tiny descending vanish tail.
```

#### `pickup`

```text
Bright collectible pickup chime with a small upward sparkle. Rewarding and lightweight.
```

#### `bonus`

```text
Joyful bonus reward burst with ascending sparkles. Celebratory, original, and arcade-like.
```

#### `powerup`

```text
Power-up activation with rising magical energy, glittering highlights, and a confident resolve.
```

#### `explosion`

```text
Soft arcade explosion pop with rounded burst, dust, and sparkle debris. Non-realistic and non-violent.
```

#### `blocked`

```text
Blocked action cue with a short dull tick or wooden clack and slight downward pitch.
```

#### `warning`

```text
Brief warning pulse with soft magical tension. Noticeable but not harsh or alarmist.
```

#### `success`

```text
Positive success chime with a clean sparkle tail. Short, satisfying, and original.
```

#### `fail`

```text
Gentle fail cue with a soft descending wobble or muted thunk. Mild and non-annoying.
```

#### `failure`

```text
Gentle fail cue with a soft descending wobble or muted thunk. Mild and non-annoying.
```

#### `game_over`

```text
Gentle game-over sting with descending notes and a soft magical fade. Bittersweet, not dramatic.
```

#### `level_complete`

```text
Short level-complete flourish with bright sparkles and upbeat arcade-fantasy resolution.
```

#### `click`

```text
Tiny UI click with a crisp soft tap and subtle sparkle. Clean and responsive.
```

#### `hover`

```text
Subtle UI hover cue with a very short airy tick or shimmer. Quiet and non-intrusive.
```

#### `start`

```text
Start-game confirmation with a short magical whoosh-chime. Inviting and energetic.
```

#### `pause`

```text
Pause cue with a short soft downward blip and gentle stop feeling.
```

#### `resume`

```text
Resume cue with a short upward blip or light shimmer restart feeling.
```

#### `menu_open`

```text
Menu-open cue with a quick card unfold or magical reveal shimmer. Friendly and clean.
```

#### `menu_close`

```text
Menu-close cue with a quick soft fold-away or reverse shimmer. Pairs naturally with menu open.
```

### Loops

#### `ambient_loop`

```text
Seamless casual game ambient loop with light fantasy arcade mood, soft plucks, warm pads, and gentle rhythm. Original, no vocals.
```

#### `action_loop`

```text
Seamless action gameplay loop with upbeat arcade-fantasy energy, light percussion, plucky synths, and magical sparkle accents. Original, no vocals.
```

#### `victory_loop`

```text
Seamless victory/results loop with cheerful fantasy arcade mood, bright harmony, and celebratory light percussion. Original, no vocals.
```

#### `defeat_loop`

```text
Seamless defeat/results loop with gentle bittersweet arcade-fantasy mood, soft descending harmony, and calm emotional tone. Original, no vocals.
```

#### `soft_magic_loop`

```text
Seamless soft magic ambience loop with airy shimmer, distant twinkles, warm pad, and calm enchanted atmosphere. No vocals.
```

#### `spooky_loop`

```text
Seamless family-friendly spooky ambience loop with soft wind, playful ghostly tones, subtle creaks, and magical mystery. No screams, no vocals.
```

#### `arcade_loop`

```text
Seamless arcade ambience loop with gentle retro room tone, soft synth bed, and tiny electronic sparkle textures. Energetic but unobtrusive.
```
