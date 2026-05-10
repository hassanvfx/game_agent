# Sample Game Folder Shape Reference

Source sample:
- First 10 entries from `tmp/retry_manifests/latest_selected_remix_deploy_manifest.json`
- Analyzed with `tmp/analyze_sample_game_folder_shapes.py`

## Common top-level directories
- `assets/`
- `catalogs/`

## Common top-level primary files
These appeared in all 10 sampled folders:
- `Blueprint.md`
- `Identity.json`
- `RecreationPrompt.md`
- `RemixDelta.md`
- `index.html`
- `operator_result_contract.json`
- `remix_plan_v4.json`
- `remix_theme.json`
- `screens_01_title_or_entry.png`
- `screens_02_live_play.png`
- `screens_03_menu_or_modal.png`
- `screens_04_fail_or_win.png`

## Common AppleDouble noise files to ignore
These also appeared in all 10 sampled folders and should be ignored:
- `._Blueprint.md`
- `._Identity.json`
- `._RecreationPrompt.md`
- `._RemixDelta.md`
- `._assets`
- `._catalogs`
- `._index.html`
- `._operator_result_contract.json`
- `._remix_plan_v4.json`
- `._remix_theme.json`
- `._screens_01_title_or_entry.png`
- `._screens_02_live_play.png`
- `._screens_03_menu_or_modal.png`
- `._screens_04_fail_or_win.png`

## Variant metadata filenames observed across samples
Not every sample used the same mechanics/semantic filenames. Observed variants include:
- `SemanticTags.json`
- `semantic_tags.json`
- `MechanicsClassification.json`
- `mechanics_classification.json`
- `MechanicsRanking.json`
- `mechanics_ranking.json`
- `MechanicsRationale.json`

## Structural conclusions
1. `index.html` is stable and should be treated as required.
2. `assets/` is stable and should be copied when present.
3. Prompt/identity/plan markdown/json files are usually top-level.
4. Screenshot-like evidence files are present as top-level PNGs named like:
   - `screens_01_title_or_entry.png`
   - `screens_02_live_play.png`
   - `screens_03_menu_or_modal.png`
   - `screens_04_fail_or_win.png`
   - plus occasional additional `screens_05_*` / `screens_06_*`
5. AppleDouble `._*` files are pervasive and must always be ignored.
6. Semantics/mechanics naming is not fully normalized, so extractor code should support filename variants, not only one canonical spelling.

## Immediate implementation implication
The adapted-json output script should:
- ignore `._*`
- use the shared extractor utility
- optionally augment screenshot discovery to include top-level `screens_*.png`
- support semantics/mechanics filename variants when building normalized metadata