# Top107 Legacy Raw Layout Reference

Source basis:
- Manifest: `tmp/retry_manifests/top107_legacy_raw_manifest.json`
- 10-folder random sample analysis:
  - `tmp/analyze_top107_legacy_raw_sample.py`
  - output: `tmp/top107_legacy_raw_sample_analysis.json`

## Legacy layout identity
This layout is the raw Vatsal top107 shape under:
- `games/raw/gamezone-.../`

Unlike the run-output layout, these folders are already raw-backed game folders and commonly contain:
- direct playable source files
- normalized metadata sidecars
- playwright evidence files
- a nested `remix-<hash>/` subfolder

## Common top-level directories
Present in all 10 sampled legacy raw folders:
- `assets/`
- `catalogs/`
- `remix-<hash>/`

## Common top-level metadata files
Present in all 10 sampled legacy raw folders:
- `Blueprint.md`
- `Identity.json`
- `RecreationPrompt.md`
- `index.html`
- `operator_result_contract.json`
- `semantic_tags.json`
- `mechanics_classification.json`
- `mechanics_ranking.json`
- `delta_issue_ledger.md`

## Common evidence files
Very common in the 10-sample legacy raw layout:
- `playwright_initial.png`
- `playwright_after_start.png`
- `playwright_console_errors.json`
- `playwright_observation_log.md`
- `playwright_screenshots.json`

Additional variants observed:
- `playwright_runtime_evidence.json`
- `playwright_server.log`
- `playwright_server.pid`
- `playwright_after_*.png`
- `playwright_post_fix*.png`
- `playwright_run_*.json`

## Legacy field-source map
For this legacy layout, the most likely mappings are:

### Core metadata
- `game_id`
  - folder name `gamezone-...`
  - fallback `Identity.json` if it includes it

- `recreation_prompt_markdown`
  - `RecreationPrompt.md`

- `blueprint_markdown`
  - `Blueprint.md`

- `identity`
  - `Identity.json`

- `semantic_tags`
  - `semantic_tags.json`

- `mechanics_classification`
  - primary: `mechanics_classification.json`
  - supporting/fallback context: `mechanics_ranking.json`

### Playable/runtime files
- `index.html`
  - top-level `index.html`

- `assets_dir`
  - top-level `assets/`

### Screenshot/evidence sources
Legacy layout appears to use playwright evidence as the screenshot source:
- `playwright_initial.png`
- `playwright_after_start.png`
- `playwright_after_*.png`
- `playwright_post_fix*.png`

These should likely map into normalized screenshots arrays when explicit `screenshots/` folders are absent.

## Key difference from run layout
Run layout:
- richer operator/output artifacts
- often `SemanticTags.json` / `MechanicsClassification.json`
- top-level `screens_*.png`

Legacy raw layout:
- lower-case metadata filenames are canonical
- playwright evidence PNGs are the most stable screenshot source
- includes a nested `remix-<hash>/` directory that should not be mistaken for the primary source root

## Implementation implication
To support both layouts, the shared extractor should branch roughly as:

1. **Run layout**
- prefer `SemanticTags.json`
- prefer `MechanicsClassification.json`
- collect `screens_*.png`

2. **Legacy raw layout**
- prefer `semantic_tags.json`
- prefer `mechanics_classification.json`
- use `playwright_*.png` evidence images as screenshots
- ignore nested `remix-<hash>/` as primary metadata source unless needed as fallback