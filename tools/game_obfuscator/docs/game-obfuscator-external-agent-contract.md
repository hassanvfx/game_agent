# Game Obfuscator External Agent Contract

## Purpose

This document describes the **current supported external integration surface** for `game_obfuscator`.

This contract is for:
- external agents
- automation callers
- machine-facing wrappers

The product now has:
- one supported pipeline
- one supported launch command
- deterministic single-path processing
- synchronous execution from the caller perspective

---

## Current Execution Model

The current tool should be treated as:

- **deterministic**
- **single-path**
- **synchronous**
- **fast for normal use**
- **not a launch/poll background orchestration system**

The old multi-stage and study paths have been removed.

### What this means
A caller should now think of the tool as:

1. call `start`
2. wait for the command to finish
3. read the returned JSON
4. use the reported output paths

There is no longer a recommended external polling loop.

---

## Supported CLI Surface

The main supported machine-facing command is:

- `start`

The following commands still exist as read surfaces:
- `status`
- `output-path`

But for the current product shape, external agents should normally use only:

- `start`

Example:

```bash
python3 scripts/game_obfuscator_cli.py start --manifest manifests/random_batch_036.json
```

Optional explicit run id:

```bash
python3 scripts/game_obfuscator_cli.py start \
  --manifest manifests/random_batch_036.json \
  --run-id my_custom_run_id
```

---

## Input Model

### Supported input configuration
Input is configurable through:

- `--manifest`

The manifest controls:
- which games are processed
- each game id
- each source path

Example manifest:

```json
{
  "games": [
    {
      "game_id": "example-game",
      "display_name": "Example Game",
      "source_path": "/absolute/path/to/source/game"
    }
  ]
}
```

### Source expectations
Each game source directory should contain at minimum:
- `index.html`

The current simple pipeline then:
- mirrors the source locally
- prunes to retained surface
- keeps:
  - `index.html`
  - `assets/**/*.js`
  - `assets/**/*.css`
- removes everything else from the published copy
- obfuscates inline classic HTML scripts in place
- minifies module scripts conservatively
- obfuscates retained external JS files
- minifies retained CSS

---

## Output Model

### Current output behavior
Output directory is **not caller-configurable via CLI flag**.

The tool writes into a run-scaffolded directory:

```text
runs/<run_id>/output/
```

Per-game output path:

```text
runs/<run_id>/output/<game_id>/
```

### Practical implication
A caller can control:
- the manifest input
- the optional run id

A caller cannot currently pass:
- `--output-dir`
- `--output-root`

### How to influence output location today
Use:
- `--run-id` to control the run folder name

Example:

```bash
python3 scripts/game_obfuscator_cli.py start \
  --manifest manifests/random_batch_036.json \
  --run-id my_custom_run_id
```

This produces outputs under:

```text
runs/my_custom_run_id/output/
```

---

## Command Contract

## 1. Primary Command: `start`

### Request
```bash
python3 scripts/game_obfuscator_cli.py start --manifest <manifest-path>
```

Optional:
```bash
python3 scripts/game_obfuscator_cli.py start --manifest <manifest-path> --run-id <run-id>
```

### Behavior
- creates the run scaffold
- executes the deterministic simple pipeline
- finishes before returning control to the caller
- returns machine-readable JSON at the end

### Success expectation
For normal external use, a caller should treat:
- process exit code `0`
- returned JSON payload

as the primary completion contract.

### Response shape
```json
{
  "run_id": "run_game_obfuscator_20260427T025801Z",
  "run_dir": "/absolute/path/to/runs/run_game_obfuscator_20260427T025801Z",
  "status": "completed",
  "current_phase": "simple_obfuscation_complete",
  "output_path": "/absolute/path/to/runs/run_game_obfuscator_20260427T025801Z/output",
  "completed": true,
  "game_outputs": [
    {
      "game_id": "example-game",
      "output_path": "/absolute/path/to/runs/run_game_obfuscator_20260427T025801Z/output/example-game"
    }
  ],
  "status_path": "/absolute/path/to/runs/run_game_obfuscator_20260427T025801Z/run_state.json",
  "dashboard_path": "/absolute/path/to/runs/run_game_obfuscator_20260427T025801Z/dashboard/index.html",
  "accepted_at": "2026-04-27T02:58:01Z",
  "pipeline_mode": "simple",
  "launcher_stdout_path": "/absolute/path/to/runs/run_game_obfuscator_20260427T025801Z/logs/launcher.stdout.log",
  "launcher_stderr_path": "/absolute/path/to/runs/run_game_obfuscator_20260427T025801Z/logs/launcher.stderr.log",
  "output_root": "/absolute/path/to/runs/run_game_obfuscator_20260427T025801Z/output"
}
```

### Important note
Some fields in the response still reflect the historical run-scaffold structure:
- `status_path`
- `dashboard_path`
- `launcher_*`
- `pipeline_mode`

External callers may ignore those if they only need:
- `run_id`
- `run_dir`
- `output_root`
- `output_path`
- `game_outputs`

---

## 2. Optional Read Command: `status`

### Request
```bash
python3 scripts/game_obfuscator_cli.py status --run-id <run_id>
```

or

```bash
python3 scripts/game_obfuscator_cli.py status --run-dir <run_dir>
```

### When to use it
This is now primarily:
- a diagnostic command
- a debugging command
- a compatibility read surface

It is **not the recommended primary agent loop** anymore.

---

## 3. Optional Read Command: `output-path`

### Request
```bash
python3 scripts/game_obfuscator_cli.py output-path --run-id <run_id>
```

Optional per-game outputs:
```bash
python3 scripts/game_obfuscator_cli.py output-path --run-id <run_id> --include-games
```

### When to use it
This is useful when:
- a caller wants a stable output lookup command
- a caller already knows the run id
- a caller wants per-game output directories after completion

It is optional if the caller already trusts the final `start` result and run directory.

---

## Recommended External Workflow

```bash
python3 scripts/game_obfuscator_cli.py start \
  --manifest /absolute/path/to/manifest.json \
  --run-id my_custom_run_id
```

Then:
- wait for the command to exit
- treat exit code `0` as transport success
- use the returned run/output paths
- optionally inspect `output-path --include-games` if you want per-game paths

### Rule of thumb
- trust `start` as the primary contract
- use `status` only for debugging/inspection
- use `output-path` only as a convenience lookup surface

---

## Current Limitations

### Supported today
- configurable input manifest
- configurable run id
- deterministic single-path processing
- synchronous caller experience
- machine-readable output metadata

### Not supported today
- caller-specified output directory flag
- caller-specified output root flag
- multiple pipeline modes
- legacy workflow selection
- `game_obfuscator_cline` workflow path

---

## Recommendation For Future Extension

If external agents need direct output placement, the next CLI feature to add would be:

- `--output-root <path>`

Until then, the supported model remains:

- input configurable by manifest
- output location derived from run id under `runs/<run_id>/output/`