# Remix v5 Skill Catalog Mental Simulation

**Date:** 2026-05-16  
**Status:** Draft for expectation alignment before code changes  
**Scope:** Mental model, ASCII architecture, observed callsites, cleanup risks, and validation loop for a catalog-aware `creative_remix_v5` super operator.

---

## 1. Goal

Create a new Remix v5 super operator that uses GPT-5.5-style long-horizon capability without collapsing into a lazy mega-prompt.

The v5 operator should:

1. preserve the operational integrity of the working `remix-v4-clone` flow;
2. decompose the v4-clone principles into normalized skill catalogs;
3. copy those skill catalogs into each operator attempt workspace like media catalogs;
4. expose those catalogs in the prompt header builder;
5. assemble a single runnable v5 super prompt from the cataloged skills;
6. force a full game regeneration lifecycle:
   - source mapping;
   - before QA;
   - old runtime preservation;
   - mechanic blueprint;
   - new canonical `index.html` rebuild;
   - catalog media integration;
   - mobile-first portrait visual/UI pass;
   - after QA;
   - before/after comparison;
   - repair loop.

The immediate requested step is **not coding yet**. It is to write down the mental simulation so the intended model can be compared against the actual code observations.

---

## 2. Current Observed Code Path

### 2.1 Batch/Workflow Layer

Named workflows are defined in:

```text
tools/game_refactoring/scripts/game_workflow.py
```

The current working clone workflow is:

```text
remix-v4-clone
  1. clone_remix_inference_plus
  2. clone_rebuild_from_blueprint_and_old_refs
  3. clone_world_design_superprompt
  4. clone_visuals_unified
  5. clone_final_mobile_repair_aggressive
```

Each node points to a single prompt file through a generated manifest v2 node:

```json
{
  "id": "clone_visuals_unified",
  "prompt_file": "prompts/operators_v2/03_remix_v4_clone_visuals_unified.md",
  "accepted_upstream_statuses": ["ok", "warning"],
  "requires_contract": true
}
```

### 2.2 Per-Game Operator Attempt Layer

The main runtime callsite is:

```text
tools/game_refactoring/scripts/run_operator_pipeline_game.py
```

Important observed functions:

```text
copy_workspace(source, destination, replace=False)
copy_catalogs_into_workspace(workspace)
build_operator_prompt_text(...)
run_stage_attempt(...)
```

Observed flow:

```text
prepared input/current workspace
        |
        v
+-------------------------------+
| copy_workspace(current,       |
|   attempt/workspace)          |
+-------------------------------+
        |
        v
+-------------------------------+
| copy_catalogs_into_workspace  |
|   attempt/workspace/catalogs  |
+-------------------------------+
        |
        v
+-------------------------------+
| write media_policy_report     |
+-------------------------------+
        |
        v
+-------------------------------+
| build_operator_prompt_text    |
|   prompt header + node prompt |
+-------------------------------+
        |
        v
+-------------------------------+
| invoke cline worker           |
+-------------------------------+
        |
        v
+-------------------------------+
| if success: copy attempt      |
| workspace back to current     |
+-------------------------------+
```

### 2.3 Current Catalog Copy Behavior

Current `copy_catalogs_into_workspace()` requires four catalog files:

```python
required_catalog_names = ("audios.json", "gifs.json", "sprites.json", "fonts.json")
```

It writes them into:

```text
attempt/workspace/catalogs/
  audios.json
  gifs.json
  sprites.json
  fonts.json
```

### 2.4 Current Prompt Header Behavior

`build_operator_prompt_text(...)` currently includes a catalog media policy section:

```text
## Catalog Media Policy

Use only approved remote media URLs from these catalog files:
- catalogs/audios.json -> approved remote audio sources
- catalogs/gifs.json -> approved remote GIF / animated media sources
- catalogs/sprites.json -> approved remote image / sprite / background sources
- catalogs/fonts.json -> approved remote font sources

Mandatory rules:
- Do not use media files from assets/
- From assets/, only CSS and JS files may be used
- For media replacement or new media selection, prefer remote URLs represented in the catalog files
```

### 2.5 Cleanup / Deletion Observations

#### `prepare_inputs.py`

Before operator stages run, copied source inputs are purged to keep only:

```text
index.html
assets/
```

ASCII:

```text
source game folder
   |
   | mirror_directory()
   v
prepared input mirror
   |
   | purge_prepared_directory()
   v
+-------------------------+
| index.html              |
| assets/                 |
+-------------------------+
```

This happens **before** `workspace/catalogs/` is injected into attempt workspaces, so it should not delete skill catalogs copied later.

Important separation:

```text
prepare_inputs.py owns source-game input hygiene
run_operator_pipeline_game.py owns attempt-time operator reference injection
```

So the v5 skill catalog should not be placed in prepared source mirrors. It should be injected only into operator attempt workspaces through the same catalog path as media catalogs.

```text
SOURCE / INPUT MIRROR                         OPERATOR ATTEMPT WORKSPACE

source game                                  attempt/workspace
  index.html                                   index.html
  assets/                                      assets/
                                               catalogs/
                                                 audios.json
                                                 gifs.json
                                                 fonts.json
                                                 sprites.json
                                                 skills/

prepare_inputs purge sees only left side.      catalog injection happens on right side.
```

#### `run_operator_pipeline_game.py`

This function can remove destination workspaces when `replace=True`:

```python
if destination.exists():
    if not replace:
        raise OperatorPipelineGameError(...)
    shutil.rmtree(destination)
```

Risk point:

```text
attempt/workspace, including catalogs/
        |
        | copy_workspace(..., current_workspace, replace=True)
        v
current_workspace now includes catalogs/ unless excluded
```

This matches existing media catalog behavior. It is not necessarily wrong, but v5 should document catalogs as read-only and decide whether final output should retain or strip them.

#### `media_policy.py`

Media policy intentionally ignores catalog descendants:

```python
def _is_catalog_file(relative_path: str) -> bool:
    return _normalize_relative_path(relative_path).startswith("catalogs/")
```

Therefore:

```text
catalogs/audios.json       ignored by media scans
catalogs/gifs.json         ignored by media scans
catalogs/skills/*.json     also ignored by media scans
```

---

## 3. Desired Mental Model

### 3.1 Catalogs as Capability Sources

Media catalogs tell the operator:

```text
what approved assets may be used
```

Skill catalogs should tell the operator:

```text
what operational capabilities must be applied
```

Mental model:

```text
                    +---------------------------+
                    | tools/game_refactoring/   |
                    | catalogs/                 |
                    +-------------+-------------+
                                  |
          +-----------------------+------------------------+
          |                       |                        |
          v                       v                        v
+------------------+    +------------------+     +----------------------+
| media catalogs   |    | font/sprite      |     | skill catalogs       |
| audios/gifs      |    | catalogs         |     | skills/*.json        |
+--------+---------+    +--------+---------+     +----------+-----------+
         |                       |                          |
         +-----------------------+--------------------------+
                                 |
                                 v
                    +---------------------------+
                    | attempt/workspace/catalogs|
                    +---------------------------+
```

### 3.2 v5 Build-Time and Runtime Model

Skill catalogs should serve two roles:

1. **Build-time prompt assembly input**
   - deterministic script reads `tools/game_refactoring/catalogs/skills/*.json`;
   - generates `00_creative_remix_v5_super_operator.md`.

2. **Runtime operator reference catalog**
   - runner copies `catalogs/skills/` into attempt workspace;
   - prompt header tells the operator where to find it;
   - v5 prompt treats those skill entries as authoritative rails.

ASCII:

```text
                   BUILD TIME

tools/.../catalogs/skills/*.json
              |
              | build_remix_v5_super_prompt.py
              v
tools/.../prompts/operators_v2/
  00_creative_remix_v5_super_operator.md


                   RUNTIME

source current workspace
              |
              | copy_workspace()
              v
attempt/workspace
              |
              | copy_catalogs_into_workspace()
              v
attempt/workspace/catalogs/
  audios.json
  gifs.json
  fonts.json
  sprites.json
  skills/
    skill_types.json
    remix_v5_*.json
              |
              | build_operator_prompt_text()
              v
operator prompt header says:
  "Read catalogs/skills/ as read-only capability catalogs"
```

---

## 4. Proposed Skill Catalog Shape

### 4.1 Folder

```text
tools/game_refactoring/catalogs/skills/
  README.md
  skill_types.json
  remix_v5_core_skills.json
  remix_v5_analysis_skills.json
  remix_v5_rebuild_skills.json
  remix_v5_world_skills.json
  remix_v5_visual_skills.json
  remix_v5_media_skills.json
  remix_v5_qa_skills.json
```

### 4.2 Skill Type Catalog

```json
{
  "schema_version": "1.0.0",
  "catalog_kind": "game_refactoring_skill_types",
  "skill_types": [
    { "id": "core", "description": "Global contracts and IO rules." },
    { "id": "analysis", "description": "Mechanic blueprint and source mapping." },
    { "id": "rebuild", "description": "Old runtime preservation and new surface creation." },
    { "id": "world", "description": "Authored world and narrative semantics." },
    { "id": "visual", "description": "Procedural visuals, HUD, layout, animation." },
    { "id": "media", "description": "Media catalog selection and safe wiring." },
    { "id": "qa", "description": "Before/after runtime QA and repair." }
  ]
}
```

### 4.3 Skill Entry Schema

```json
{
  "id": "qa.before_after_mobile_comparison",
  "type": "qa",
  "title": "Before/After Mobile Runtime Comparison",
  "priority": 80,
  "use_when": ["Always in creative_remix_v5"],
  "inputs": ["validation runtime contract", "rebuilt index.html"],
  "required_actions": ["Capture before evidence", "Capture after evidence"],
  "required_artifacts": ["v5_before_after_comparison.md"],
  "acceptance_bar": ["Evidence is real or blocked conditions are documented"],
  "failure_modes_prevented": ["Fake screenshots", "Desktop-only validation"]
}
```

---

## 5. Expected Code Changes Later

No implementation should happen until this model is reviewed. Once aligned, likely code changes are:

### 5.1 Folder-Aware Catalog Copy

In `run_operator_pipeline_game.py`, preserve the current required media files and add optional subfolder copying:

```text
copy_catalogs_into_workspace(workspace)
  required files:
    audios.json
    gifs.json
    sprites.json
    fonts.json

  optional directories:
    skills/
```

Expected behavior:

```text
if tools/game_refactoring/catalogs/skills/ exists:
    copytree(.../catalogs/skills, workspace/catalogs/skills)
else:
    continue without error
```

### 5.2 Prompt Header Builder Exposure

`build_operator_prompt_text(...)` should include:

```text
## Skill Catalog Policy

If present, `catalogs/skills/` contains read-only operator skill catalogs.
Use these skill catalogs as capability references, especially for `creative_remix_v5`.
Do not edit files under `catalogs/`.
When a skill requires artifacts, write those artifacts outside `catalogs/` in the attempt workspace.
```

Better version: pass the copied catalog map into `build_operator_prompt_text(...)` so the prompt can list what is actually available.

### 5.3 Invocation Metadata

Record copied catalog paths in invocation/usage artifacts:

```json
{
  "workspace_catalogs": {
    "audios.json": ".../workspace/catalogs/audios.json",
    "gifs.json": ".../workspace/catalogs/gifs.json",
    "fonts.json": ".../workspace/catalogs/fonts.json",
    "sprites.json": ".../workspace/catalogs/sprites.json",
    "skills/": ".../workspace/catalogs/skills"
  }
}
```

---

## 6. v5 Super Operator Internal Mental Model

The final `creative_remix_v5` workflow should be one node:

```text
creative_remix_v5
  └── remix_v5_super_operator
        prompt_file: prompts/operators_v2/00_creative_remix_v5_super_operator.md
```

Inside the prompt, the operator performs a phased lifecycle:

```text
+----------------------------------------------------------+
| Phase 0: IO + runtime contract                           |
+---------------------------+------------------------------+
                            |
                            v
+----------------------------------------------------------+
| Phase 1: source surface map + before QA                  |
+---------------------------+------------------------------+
                            |
                            v
+----------------------------------------------------------+
| Phase 2: mechanic blueprint + protected truth            |
+---------------------------+------------------------------+
                            |
                            v
+----------------------------------------------------------+
| Phase 3: preserve old runtime as _old references         |
+---------------------------+------------------------------+
                            |
                            v
+----------------------------------------------------------+
| Phase 4: rebuild new canonical public index.html         |
+---------------------------+------------------------------+
                            |
                            v
+----------------------------------------------------------+
| Phase 5: authored world + catalog media selection        |
+---------------------------+------------------------------+
                            |
                            v
+----------------------------------------------------------+
| Phase 6: mobile-first portrait visual/UI implementation  |
+---------------------------+------------------------------+
                            |
                            v
+----------------------------------------------------------+
| Phase 7: after QA + before/after compare + repair loop   |
+----------------------------------------------------------+
```

---

## 7. Expectation vs Observation Table

| Area | Expectation | Current Observation | Gap / Action |
|---|---|---|---|
| Media catalogs | Copied into every attempt workspace | Yes, four files are required | Keep unchanged |
| Skill catalogs | Copied as `catalogs/skills/` | Not currently supported | Add optional folder copy |
| Prompt header | Mentions media catalogs and rules | Yes | Add skill catalog policy section |
| Catalog cleanup | Catalogs should not be treated as app media | `media_policy.py` ignores all `catalogs/` descendants | Already OK |
| Input purge | Should not delete skill catalogs | Purge happens before catalog injection | Already OK |
| Attempt success copyback | May carry `catalogs/` forward | Current whole-workspace copyback does this | Decide whether acceptable or cleanup needed |
| v5 prompt execution | Single node prompt from skill catalogs | Not yet implemented | Add v5 workflow + builder |

---

## 8. Risks and Decisions to Align

### Risk 1: Catalogs Persist in Final Outputs

Because successful attempt workspaces are copied forward wholesale, `catalogs/skills/` may end up in `current_workspace` and output mirrors.

Decision options:

```text
A. Allow persistence.
   Pros: matches current media catalog behavior; simple; inspectable.
   Cons: output contains reference catalogs.

B. Strip catalogs from final output only.
   Pros: cleaner outputs.
   Cons: extra cleanup path; risk removing useful debug evidence.

C. Strip catalogs between stages.
   Pros: stages always receive fresh catalog injection.
   Cons: more invasive; probably unnecessary.
```

Initial recommendation: **A for first implementation**, then revisit if final deploy/publish treats catalogs as undesirable.

Decision framing:

```text
catalogs/ in an attempt workspace are runtime/reference inputs.
They are not authored game deliverables.
```

For the first v5 implementation, persistence is acceptable as debug evidence **only if** prompts clearly say catalogs are read-only references and generated game artifacts should not depend on mutating them. A later publish/deploy cleanup can strip `catalogs/` if product output size or cleanliness requires it.

### Risk 2: Prompt Header Lies About Skills Availability

If the header says `catalogs/skills/` exists but copying failed or folder is absent, the operator may waste effort looking for it.

Recommendation:

```text
Pass copied catalog map into build_operator_prompt_text()
and list exact copied catalog paths.
```

### Risk 3: Skill Catalogs Become Too Abstract

If skill entries are vague, v5 will become another lazy mega-prompt.

Recommendation:

```text
Each skill must include required_actions, required_artifacts,
acceptance_bar, and failure_modes_prevented.
```

### Risk 4: Assembly Drift

If JSON catalogs and assembled prompt diverge, behavior becomes unclear.

Recommendation:

```text
Generated prompt includes a source manifest header and every skill ID.
Validation checks assembled prompt coverage.
```

---

## 9. Iteration Loop

The development loop should be:

```text
+-----------------------------+
| 1. Write mental model        |
+--------------+--------------+
               |
               v
+-----------------------------+
| 2. Compare actual code path  |
+--------------+--------------+
               |
               v
+-----------------------------+
| 3. Identify gaps/risks       |
+--------------+--------------+
               |
               v
+-----------------------------+
| 4. Implement smallest change |
+--------------+--------------+
               |
               v
+-----------------------------+
| 5. Dry-run validate          |
+--------------+--------------+
               |
               v
+-----------------------------+
| 6. Inspect artifacts         |
+--------------+--------------+
               |
               v
+-----------------------------+
| 7. Update model or code      |
+-----------------------------+
```

Alignment checkpoint before coding:

```text
Do we agree that:
  [ ] skills are first-class catalogs under tools/game_refactoring/catalogs/skills/
  [ ] skills are copied into attempt workspaces as catalogs/skills/
  [ ] prompt header builder exposes skill catalog availability
  [ ] v5 still uses one assembled super prompt as the workflow prompt_file
  [ ] catalogs are read-only references inside attempts
  [ ] catalog persistence in outputs is acceptable for the first implementation
```

---

## 10. Proposed Validation Artifacts

After implementation, add a validation script such as:

```text
tmp/validate_remix_v5_skill_catalogs.py
```

It should verify:

1. `tools/game_refactoring/catalogs/skills/skill_types.json` parses.
2. Every `remix_v5_*_skills.json` parses.
3. Skill IDs are unique.
4. Skill `type` values exist in `skill_types.json`.
5. Required fields are present.
6. Assembled prompt includes every skill ID.
7. Dry-run attempt workspace includes `catalogs/skills/`.
8. Prompt text includes `## Skill Catalog Policy`.

---

## 11. Current Conclusion

The observed code supports a clean, backward-safe implementation:

```text
Existing media catalog system
        |
        v
Extend catalog copying to optional subfolders
        |
        v
Add catalogs/skills/ as a normalized operator capability catalog
        |
        v
Expose skills in prompt header
        |
        v
Assemble creative_remix_v5 super prompt from skill catalogs
```

No major orchestration rewrite appears necessary. The main expected code touchpoints are small and localized.
