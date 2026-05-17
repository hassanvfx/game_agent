# Game Workflow CLI

`scripts/game_workflow.py` is a standalone workflow launcher that sits above the existing manifest-driven batch pipeline.

It exists to let you invoke named workflows as stable source-controlled node collections while keeping the input game list external and required.

## Purpose

Use `game_workflow.py` when you want to:

- launch a named workflow like `tag_and_fix`
- keep workflow structure in code instead of copying fixture manifests
- pass a required external games manifest at invocation time
- preserve the existing `creative_refactor_cli.py start-batch` orchestration path
- avoid regressing the main refactor CLI surface with workflow-specific logic

## Current workflow IDs

### `tag_and_fix`

The current `tag_and_fix` workflow is defined in `scripts/game_workflow.py` and runs these nodes:

1. `inference_outputs`
2. `playwright_fix`

### `creative_remix_v1`

The `creative_remix_v1` workflow is defined in `scripts/game_workflow.py` and runs these nodes:

1. `narrative`
2. `gameplay`
3. `visuals`
4. `media_mapper`

This workflow is intentionally more user-prompt-driven than the existing specimen-oriented flows.

When provided, the remix prompt should be treated as the primary steering signal for all four stages via:

- `--remix-prompt`
- `--remix-prompt-file`

Like `tag_and_fix`, this workflow does **not** own the input game list.

The input game list must be supplied by the caller via:

- `--games-manifest-source`

### `creative_remix_v4`

The `creative_remix_v4` workflow is defined in `scripts/game_workflow.py` and runs these nodes:

1. `remix_inference_plus`
2. `world_design_superprompt`
3. `visuals_unified`
4. `final_mobile_repair_aggressive`

This is the base four-stage v4 remix pipeline.

### `remix-v4-clone`

The `remix-v4-clone` workflow is a rebuild-first clone of Remix v4. It runs these nodes:

1. `clone_remix_inference_plus`
2. `clone_rebuild_from_blueprint_and_old_refs`
3. `clone_world_design_superprompt`
4. `clone_visuals_unified`
5. `clone_final_mobile_repair_aggressive`

The key difference from `creative_remix_v4` is that this workflow is **not** primarily a reskin/remix-on-top-of-source flow.

It first runs a clone-namespaced copy of the v4 inference/planning stage, then performs a dedicated rebuild step that preserves the source runtime by renaming `index.html` and directly linked local CSS/JS files with `_old`-style names while building a substantially new main game surface from the blueprint and mechanic analysis.

Use `remix-v4-clone` when you want to:

- preserve the original implementation as a fallback reference
- rebuild the main public surface as a new game
- minimize dependence on old source files except when resolving ambiguity or protecting core behavior expectations

### `remix-v4-vite`

The `remix-v4-vite` workflow is the Vite / compiled-bundle-specialized variant of v4. It runs these nodes:

1. `vite_surface_unpack`
2. `vite_remix_inference_plus`
3. `vite_world_design_superprompt`
4. `vite_visuals_unified`
5. `vite_final_mobile_repair_aggressive`

The key difference from `creative_remix_v4` is the extra prep stage:

- `vite_surface_unpack`

That stage is intended for shipped Vite-style or similarly compiled/minified app targets where later operators benefit from a reusable map of:

- runtime entrypoints
- bundle patch targets
- UI string surfaces
- control/input surfaces
- high-leverage compiled edit regions

Use `remix-v4-vite` when the workspace is dominated by compiled bundle artifacts and later remix stages need help avoiding token waste on irrelevant files.

## Why this script exists

Earlier workflow orchestration was briefly adapted into `scripts/creative_refactor_cli.py`, but that increased regression risk in the main CLI.

The current design keeps responsibilities separated:

- `scripts/creative_refactor_cli.py`
  - existing generic replay / batch / status / result / kill-all entrypoint
- `scripts/game_workflow.py`
  - workflow lookup
  - required games-manifest validation
  - generated manifest creation
  - delegation into the existing batch launcher

This keeps the workflow abstraction additive rather than invasive.

## How it works

At runtime, `scripts/game_workflow.py`:

1. resolves a named workflow definition
2. loads the caller-provided games manifest
3. validates that the source manifest contains a non-empty `games` list
4. builds a generated manifest that combines:
   - the workflow's source-controlled nodes
   - the caller-provided games list
5. writes that generated manifest under:
   - `runs/_workflow_manifests/`
6. launches the existing batch path through:
   - `python3 scripts/creative_refactor_cli.py --json start-batch ...`

## Basic usage

```bash
python3 scripts/game_workflow.py \
  --id tag_and_fix \
  --games-manifest-source path/to/games_manifest.json
```

## Current 10-game specimen example

```bash
python3 scripts/game_workflow.py \
  --id tag_and_fix \
  --games-manifest-source fixtures/specimen_random10_inference_playwright_manifest.json
```

## Creative remix example

```bash
python3 scripts/game_workflow.py \
  --id creative_remix_v1 \
  --games-manifest-source fixtures/specimen_random10_inference_playwright_manifest.json \
  --remix-prompt "Remix this game around a strong user-defined creative direction."
```

## Creative remix v4 Vite example

```bash
python3 scripts/game_workflow.py \
  --id remix-v4-vite \
  --games-manifest-source fixtures/specimen_random10_inference_playwright_manifest.json \
  --remix-prompt "your remix prompt here"
```

## Remix v4 clone example

```bash
python3 scripts/game_workflow.py \
  --id remix-v4-clone \
  --games-manifest-source fixtures/specimen_random10_inference_playwright_manifest.json \
  --remix-prompt "your remix prompt here"
```

## Common options

### Concurrency override

```bash
python3 scripts/game_workflow.py \
  --id tag_and_fix \
  --games-manifest-source fixtures/specimen_random10_inference_playwright_manifest.json \
  --max-concurrency 10
```

### JSON output

```bash
python3 scripts/game_workflow.py --json \
  --id tag_and_fix \
  --games-manifest-source fixtures/specimen_random10_inference_playwright_manifest.json
```

### Prompt override text

```bash
python3 scripts/game_workflow.py \
  --id tag_and_fix \
  --games-manifest-source fixtures/specimen_random10_inference_playwright_manifest.json \
  --remix-prompt "your override prompt here"
```

### Prompt override file

```bash
python3 scripts/game_workflow.py \
  --id tag_and_fix \
  --games-manifest-source fixtures/specimen_random10_inference_playwright_manifest.json \
  --remix-prompt-file path/to/prompt.txt
```

### Dry-run validation

```bash
python3 scripts/game_workflow.py --json \
  --id tag_and_fix \
  --games-manifest-source fixtures/specimen_random10_inference_playwright_manifest.json \
  --dry-run-operators \
  --dry-run-spec-adaptor
```

## Arguments

### Required

- `--id`
  - workflow identifier
- `--games-manifest-source`
  - path to a manifest containing the required `games` list

### Optional

- `--json`
- `--run-id`
- `--pipeline`
- `--model`
- `--agent-timeout`
- `--max-concurrency`
- `--poll-seconds`
- `--stale-heartbeat-seconds`
- `--remix-prompt`
- `--remix-prompt-file`
- `--dry-run-operators`
- `--dry-run-spec-adaptor`

## Input contract

The games source manifest must contain:

- a top-level `games` array
- per-game objects compatible with the existing batch pipeline

### Generic contract guidance

For workflow manifests, the safest rule is:

- mirror the per-game object shape already used by the manifests that successfully feed the current pipeline
- do not invent a new per-game schema for workflow input manifests
- if you are preparing a larger manifest, such as a 100-game manifest, copy the same per-game object structure used by an existing working manifest and expand only the list of entries

In other words:

- the workflow launcher owns workflow selection and node composition
- the caller owns the input game list
- the per-game object contract should stay aligned with the existing manifest ecosystem rather than diverging into a workflow-specific format

### Practical expectation

At minimum, current manifests commonly include fields like:

- `game_id`
- `source_path`
- `display_name`

Example shape:

```json
{
  "run_label": "some-input-set",
  "games": [
    {
      "game_id": "example-game-id",
      "source_path": "/absolute/path/to/game",
      "display_name": "example-game-id"
    }
  ]
}
```

### Important clarification

This documentation is intentionally generic:

- it describes the compatibility rule the workflow CLI expects
- it does not claim that the example above is the only possible full manifest shape across all historical or sibling-repo inputs
- when building larger manifests, prefer cloning the object shape from an already working input manifest rather than reducing fields based only on a documentation example

That is the core answer to the implementation concern:

- the workflow launcher contract is stable
- the input game list schema should be mirrored from an existing working manifest shape
- larger manifests should preserve that same per-game object structure

## Generated artifacts

### Generated workflow manifests

Workflow manifests generated by `scripts/game_workflow.py` are written under:

- `runs/_workflow_manifests/`

Example:

- `runs/_workflow_manifests/tag_and_fix__specimen_random10_inference_playwright_manifest.json`

### Batch runs

Actual launched runs continue to use the existing run layout under:

- `runs/run_game_remixer_*`

## Relationship to the main CLI

`game_workflow.py` does not replace `creative_refactor_cli.py`.

Instead:

- use `scripts/game_workflow.py` to launch named workflows
- use `scripts/creative_refactor_cli.py` for:
  - `start-batch`
  - `status`
  - `result`
  - `finish`
  - `kill-all`
  - replay/pipeline debugging paths

## Operational note

If a dry run reports simulated execution, that means the orchestration path worked but the operator workers were intentionally not run.

For example:

- `DRY RUN: no stderr; operator execution was simulated.`

That indicates the workflow launch path is valid, but not that live operators were executed.

## Extension pattern

To add a new workflow, update `WORKFLOWS` in:

- `scripts/game_workflow.py`

Add a new `WorkflowDefinition` with:

- a stable workflow ID
- a run label
- a source-controlled node list

This keeps workflow structure explicit and avoids turning fixture manifests into the source of truth for orchestration behavior.