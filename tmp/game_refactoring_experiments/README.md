# Game Refactoring Experiments Manual

This manual documents how to configure quick disposable experiments under `tmp/game_refactoring_experiments/`, especially for raw-backed Vatsal selections and prompt-driven remix runs.

## Purpose

These scripts are for fast experiment setup without hand-building manifests every time.

Common goals:
- sample games from the Vatsal top set
- prefer `games/raw` as the actual source when available
- pair chosen games with one or more remix prompts
- launch runs quickly with reproducible metadata
- keep experiment scaffolding disposable and easy to rerun

---

## Core Source Selection Model

There are two important source sets:

- `games/top100_vatsal`
  - used as the reference set of allowed `gamezone-*` ids
- `games/raw`
  - preferred source of actual playable input folders for experiments

### Preferred rule

For these experiments, the preferred selection flow is:

1. read game ids from `games/top100_vatsal`
2. resolve those ids against `games/raw`
3. only use ids that exist in both places
4. launch using the `games/raw/...` path as `source_path`

This gives you:
- a constrained experiment pool based on the Vatsal top set
- raw-backed source folders for the actual run input

### Why raw is preferred over top100 folder paths

Prefer `games/raw` when possible because:
- it is the desired source of truth for these experiments
- it avoids sampling directly from the curated top folder as the live source
- it matches the newer raw-backed workflow already used in recent experiments

---

## Existing Scripts

### 1. Raw-backed manifest builder

File:
- `tmp/game_refactoring_experiments/scripts/build_vatsal100_raw_backed_manifest.py`

What it does:
- lists `gamezone-*` ids from `games/top100_vatsal`
- resolves those ids against `games/raw`
- writes reusable fixture JSON files
- optionally emits a sampled raw-backed manifest

Useful variables:
- `--seed`
- `--sample-size`
- `--manifest-name`
- `--run-label`

Example:
```bash
python3 tmp/game_refactoring_experiments/scripts/build_vatsal100_raw_backed_manifest.py \
  --seed 20260508 \
  --sample-size 4 \
  --manifest-name top100_vatsal_raw_backed_random4_manifest.json \
  --run-label top100-vatsal-raw-backed-random4
```

Outputs include:
- `tmp/game_refactoring_experiments/fixtures/top100_vatsal_gamezone_ids.json`
- `tmp/game_refactoring_experiments/fixtures/top100_vatsal_raw_resolved_ids.json`
- sampled manifest JSON

---

### 2. Four-game disposable experiment scaffold

File:
- `tmp/game_refactoring_experiments/scripts/setup_four_game_lane_collision_experiment.py`

What it does:
- samples 4 games
- writes one-game manifests
- writes prompt files
- writes experiment metadata
- generates a launch script for staggered starts

This script is useful as a reusable pattern for multi-job experiment scaffolding.

Key configurable variables:
- experiment name
- runs root
- workflow id
- pipeline
- source mode
- model
- max concurrency
- agent timeout
- stagger seconds
- playwright port overrides
- overwrite/force behavior

---

### 3. Two-game raw-backed prompt experiment

File:
- `tmp/game_refactoring_experiments/scripts/setup_two_game_raw_prompt_experiment.py`

What it does:
- samples 2 Vatsal-top ids that also exist in `games/raw`
- writes one manifest per selected raw-backed game
- writes prompt files
- optionally launches two runs immediately
- stores metadata in an experiment directory

Current fixed prompts:
- `harry potter`
- `rick and morty`

Example:
```bash
python3 tmp/game_refactoring_experiments/scripts/setup_two_game_raw_prompt_experiment.py \
  --force \
  --launch
```

---

## Most Important Variables To Tweak

### Prompt values

In prompt-driven experiment setup scripts, prompts are usually defined in a constant like:

```python
PROMPTS = [
    "harry potter",
    "rick and morty",
]
```

Change these when you want a different thematic comparison.

Examples:
- `"pokemon"`
- `"cyberpunk detective"`
- `"ancient egypt speedrun"`
- `"spongebob horror parody"`

### Source preference

The important source roots are usually:

```python
TOP100_ROOT = ROOT / "games" / "top100_vatsal"
RAW_ROOT = ROOT / "games" / "raw"
```

If the experiment is meant to be raw-backed:
- keep `TOP100_ROOT` as the id pool
- keep `RAW_ROOT` as the preferred `source_path` root

If you intentionally want direct top-folder sourcing instead:
- sample and launch from `TOP100_ROOT`
- but only do that when the experiment specifically calls for it

### Random seed

Most scripts include a seed like:

```python
DEFAULT_RANDOM_SEED = 20260508
```

Or a CLI arg like:
- `--seed`

Use this to:
- reproduce a previous sample
- intentionally change which games are selected

### Sample size

When supported, `--sample-size` controls how many resolved raw-backed games are selected.

Examples:
- `2` for pair experiments
- `4` for lane/collision experiments
- larger values for batch sampling

### Experiment name

Usually exposed as:
- `--experiment-name`

This controls the folder under:
- `tmp/game_refactoring_experiments/experiments/`

Use a new name when you want to preserve previous experiment scaffolds.

Examples:
- `two_game_raw_prompt_experiment`
- `harry_vs_rick_raw_pair`
- `metaverse_world_progression_trial`

### Runs root

Usually exposed as:
- `--runs-root`

This determines where launched runs are written.

Current common value:
- `/Volumes/HDD2026/output`

Change this when:
- testing on another external disk
- isolating runs in a different output location

### Workflow id

Usually exposed as:
- `--workflow-id`

Common value:
- `creative_remix_v3`

Change this only if you want a different workflow.

### Pipeline

Usually exposed as:
- `--pipeline`

Common values:
- `v2`
- `legacy`

Current default for these experiments:
- `v2`

### Source mode

Usually exposed as:
- `--source-mode`

Common values:
- `inplace`
- `copy`

Typical current usage:
- `inplace`

### Model

Usually exposed as:
- `--model`

Common current value:
- `gpt-5.4`

### Max concurrency

Usually exposed as:
- `--max-concurrency`

Examples:
- `1` for very controlled single-job runs
- higher values for batch throughput

### Agent timeout

Usually exposed as:
- `--agent-timeout`

Used to tune how long each launched run can execute.

### Playwright leased-port controls

Optional overrides:
- `--playwright-port-base`
- `--playwright-port-pool-size`
- `--playwright-port-lease-ttl-seconds`

Use these only when you need to explicitly tune port allocation behavior for browser-grounded validation.

### Force overwrite

Usually:
- `--force`

Use when reusing an existing experiment directory and you want to replace its scaffold.

### Launch immediately

Usually:
- `--launch`

Use when the setup script should both:
- build the experiment scaffold
- and immediately launch the runs

Omit it when you only want scaffolding/metadata without starting runs.

---

## Typical Experiment Patterns

### Pattern A: Build a reusable raw-backed manifest first

Use when:
- you want to inspect or reuse a selected pool before launching

Example:
```bash
python3 tmp/game_refactoring_experiments/scripts/build_vatsal100_raw_backed_manifest.py \
  --seed 20260508 \
  --sample-size 2 \
  --manifest-name manual_pair_manifest.json \
  --run-label manual-pair
```

### Pattern B: Setup and launch a two-game themed comparison

Use when:
- you want a quick A/B thematic experiment

Example:
```bash
python3 tmp/game_refactoring_experiments/scripts/setup_two_game_raw_prompt_experiment.py \
  --experiment-name harry-vs-rick-raw \
  --runs-root /Volumes/HDD2026/output \
  --source-mode inplace \
  --model gpt-5.4 \
  --force \
  --launch
```

### Pattern C: Setup only, launch later

Use when:
- you want manifests/prompts/metadata first
- then manually inspect before starting

Example:
```bash
python3 tmp/game_refactoring_experiments/scripts/setup_two_game_raw_prompt_experiment.py \
  --experiment-name inspect-first \
  --force
```

---

## Output Structure

Typical experiment directory shape:

```text
tmp/game_refactoring_experiments/experiments/<experiment-name>/
  manifests/
  prompts/
  logs/
  metadata/
```

Important outputs:
- `manifests/*.json`
- `prompts/*.txt`
- `logs/*.log`
- `metadata/experiment_plan.json`

When runs are launched, the external output root will contain run directories like:
- `/Volumes/HDD2026/output/run_...`

---

## How To Think About Experiment Configuration

When configuring a quick experiment, decide these in order:

1. **Pool**
- where do allowed ids come from?
- usually `games/top100_vatsal`

2. **Actual source path**
- where should `source_path` point?
- usually `games/raw`

3. **Sample size**
- 1, 2, 4, or more?

4. **Prompt mapping**
- which prompt goes to which selected game?

5. **Launch mode**
- scaffold only?
- or scaffold + launch?

6. **Run environment**
- runs root
- workflow
- source mode
- model
- concurrency
- timeout

---

## Best Practices

- prefer raw-backed sources when the experiment is about modern reusable run input
- keep experiment names descriptive and disposable
- use `--seed` when you want reproducibility
- use `--force` only when you truly want to replace an experiment scaffold
- keep `max-concurrency=1` for controlled comparisons unless throughput matters more than observability
- store prompts in generated files rather than hardcoding them only in commands
- inspect `metadata/experiment_plan.json` after setup to confirm exact selections and launch commands

---

## Fast Checklist

Before launching:
- confirm the experiment should use Vatsal ids resolved against `games/raw`
- confirm prompts are the intended ones
- confirm `runs-root`
- confirm `source-mode`
- confirm whether `--launch` should be used
- confirm whether you want a new experiment name or to overwrite an old one

After launching:
- inspect `metadata/experiment_plan.json`
- note selected `game_id`s
- note `run_id`s
- note run directories under `/Volumes/HDD2026/output`

---

## Current Raw-Backed Pair Example

The current two-game setup script launched:
- one `harry potter` run
- one `rick and morty` run

using:
- Vatsal-top ids
- resolved against `games/raw`
- `creative_remix_v3`
- `pipeline=v2`
- `source-mode=inplace`
- `model=gpt-5.4`

This is the recommended pattern for quick disposable pair experiments in the current workflow.