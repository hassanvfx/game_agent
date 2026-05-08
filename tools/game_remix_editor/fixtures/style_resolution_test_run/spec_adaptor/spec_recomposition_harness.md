# Spec Recomposition Harness

You are performing the first-stage spec recomposition pass for Game Remixer.

## Goal
Rewrite the editable creative spec bundle so it reflects the runtime user remix prompt as strongly and coherently as possible while preserving all invariant safety, system, and compliance constraints.

## Selected style preset
`neutral_prototype`

## Runtime user remix prompt
`make it harry potter like`

## Editable target scope
`all editable creative files`

If explicit targets are provided, focus your strongest modifications on those target files, but keep the whole editable creative bundle coherent.

## Editable creative files
- creative_remix_contract.md: /Volumes/Elements/game_remix_editor/fixtures/style_resolution_test_run/spec_adaptor/adapted/creative_remix_contract.md
- creative_refactor_agent_template.md: /Volumes/Elements/game_remix_editor/fixtures/style_resolution_test_run/spec_adaptor/adapted/creative_refactor_agent_template.md
- visual_identity_contract.md: /Volumes/Elements/game_remix_editor/fixtures/style_resolution_test_run/spec_adaptor/adapted/visual_identity_contract.md
- theme_policy.md: /Volumes/Elements/game_remix_editor/fixtures/style_resolution_test_run/spec_adaptor/adapted/theme_policy.md

These files are editable in place:
- `creative_remix_contract.md` carries broad remix framing and gameplay-aware remix guidance
- `visual_identity_contract.md` carries branding / palette / visual identity guidance
- `theme_policy.md` carries theme / mood / atmosphere guidance
- `creative_refactor_agent_template.md` carries the worker-facing interpretation framing

## Fixed invariant reference files
- audio_policy.md: /Volumes/Elements/game_remix_editor/fixtures/style_resolution_test_run/spec_adaptor/invariants/audio_policy.md
- network_policy.md: /Volumes/Elements/game_remix_editor/fixtures/style_resolution_test_run/spec_adaptor/invariants/network_policy.md
- system_contract.md: /Volumes/Elements/game_remix_editor/fixtures/style_resolution_test_run/spec_adaptor/invariants/system_contract.md
- refactor_compliance_spec.md: /Volumes/Elements/game_remix_editor/fixtures/style_resolution_test_run/spec_adaptor/invariants/refactor_compliance_spec.md

These files are NOT editable. They must be treated as hard constraints only:
- no network
- no audio
- system/compliance boundaries
- required artifact/evidence expectations

## Editing instructions
1. Read the runtime user remix prompt carefully.
2. Read every editable creative file completely before rewriting.
3. Read the invariant reference files completely before rewriting.
4. Rewrite the editable creative files in place so they become a coherent adapted bundle.
5. Keep gameplay-related creative guidance editable through `creative_remix_contract.md` when the prompt implies gameplay shifts.
6. Do not rewrite or contradict the invariant reference files.
7. Do not create new editable spec files in this first pass.
8. Prefer strong, culturally aware interpretation of symbolic references over literal keyword dependence.
9. Keep the resulting bundle internally aligned across theme, visual identity, remix framing, gameplay framing, and worker framing.
10. Preserve playability, controls, win/loss semantics, boot flow, readability, and control-safe behavior as non-negotiable.

## Canalization / activation rules
- Theme-heavy prompts should strongly influence `theme_policy.md`
- Visual / art-direction prompts should strongly influence `visual_identity_contract.md`
- Gameplay-leaning prompts should strongly influence gameplay-related guidance inside `creative_remix_contract.md`
- Broad cultural or franchise prompts may influence several creative files together
- `creative_refactor_agent_template.md` should be updated so the downstream worker interprets the recomposed bundle correctly

## Output requirements
When finished, create:
- `recomposition_summary.json`

This summary file must contain JSON with at least:
- `status`
- `summary`
- `editable_files_reviewed`
- `files_modified`
- `notes`

After updating the editable files and writing `recomposition_summary.json`, return exactly these four lines and nothing else:
CHANGED FILES: file1, file2 or NONE
SUMMARY: one short sentence describing the recomposed bundle
PRIMARY SHIFT: one short sentence naming the dominant reinterpretation
INVARIANTS: preserved|issues
