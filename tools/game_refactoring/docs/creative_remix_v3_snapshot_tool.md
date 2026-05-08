# Creative Remix V3 Snapshot Tool

Use this tool to capture the current `creative_remix_v3` pipeline/prompt state so it can be restored or compared later.

## Script

```bash
python3 scripts/snapshot_creative_remix_v3.py --comment "your comment here"
```

Optional tag:

```bash
python3 scripts/snapshot_creative_remix_v3.py --comment "all is working ok" --tag stable-before-next-complexity-pass
```

## What it captures

The snapshot tool copies the current versions of:

- `scripts/game_workflow.py`
- `scripts/retry_harry_potter_run.py`
- `prompts/operators_v2/00_creative_remix_v3_remix_inference.md`
- `prompts/operators_v2/03_creative_remix_v1_visuals.md`
- `prompts/operators_v2/05_creative_remix_v3_narrative_refine.md`
- `prompts/operators_v2/06_creative_remix_v3_gameplay_refine.md`
- `prompts/operators_v2/07_creative_remix_v3_visuals_refine.md`
- `prompts/operators_v2/08_creative_remix_v3_optional_config_refactor.md`
- `prompts/operators_v2/09_creative_remix_v3_final_mobile_repair.md`
- `docs/journals/creative-remix-v3-next-steps-plan.md`
- `fixtures/harry_potter_single_game_25b14fff_manifest.json`

## Output location

Snapshots are written under:

```text
snapshots/creative_remix_v3/
```

Each snapshot gets its own timestamped folder containing:

- `manifest.json`
- `README.md`
- `files/` with the captured copies

## Recommended usage

Create a snapshot:
- when the current setup is stable
- before introducing more complexity
- before removing or rewriting major prompt behavior
- before running a risky experiment series

Recommended comment for the current state:

```text
all is working ok we will try next to tame the level of complexity