# Remix v5 Skill Coverage Audit

**Date:** 2026-05-16  
**Purpose:** Second-pass anti-loss audit to verify that the latest `remix-v4-clone` pipeline value was transferred into the new Remix v5 skill catalogs without dropping important guidance, implementation detail, or guardrails.

---

## 1. Boundary That Stays Outside Skills

The following logic is **intentionally not encoded as a reusable skill catalog** and must remain a direct execution phase inside the assembled `creative_remix_v5` super prompt:

- preserve old public runtime surfaces as `_old`
- rename directly linked local CSS/JS assets into `_old` forms where safe
- create a fresh canonical public `index.html`
- treat `_old` files as reference-only evidence during rebuild
- rebuild the main public game surface from blueprint/mechanic truth rather than patching the old surface in place

This boundary comes from:

- `tools/game_refactoring/prompts/operators_v2/01_remix_v4_clone_rebuild_from_blueprint_and_old_refs.md`

That prompt is a **direct super-operator phase**, not a skill file.

---

## 2. Source Prompt Coverage Matrix

## A. `00_remix_v4_clone_remix_inference_plus.md`

### Covered in `remix_v5_core_skills.json`
- global mechanics invariance
- mobile-first runtime discipline
- real artifact/evidence discipline
- anti-lazy phase execution
- cross-phase consistency

### Covered in `remix_v5_analysis_skills.json`
- current game identity and behavior mapping
- mechanic decomposition and protected/themable classification
- complexity profiling and safe escalation
- remix premise synthesis
- recreation brief generation
- 1.5-level core definition
- five-level difficulty plan
- five-level visual evolution plan
- procedural art system planning
- downstream stage contract

### Enriched in second pass
- mechanics taxonomy / ranking / semantic tag outputs
- optional progressive-disclosure rationale artifacts derived from embedded level-adapter value

## B. `02_remix_v4_clone_world_design_superprompt.md`

### Covered in `remix_v5_world_skills.json`
- mechanic-aware semantic mapping
- authored world framing
- HUD vocabulary and copy tone
- five-level world identity
- boring static background replacement mandate
- `remix_theme.json` design-system writing
- procedural character/item/prop language

### Covered in `remix_v5_media_skills.json`
- catalog authority for media choices
- non-destructive media boundaries
- selection and wiring expectations

### Enriched in second pass
- explicit asset inventory / keep-replace-remap decision skill
- structurally feasible media target selection skill

## C. `03_remix_v4_clone_visuals_unified.md`

### Covered in `remix_v5_visual_skills.json`
- focal identity first
- procedural art library
- authored animated background
- dominant stock-scene replacement
- progression-aware scene evolution
- HUD composition preservation
- mobile-safe actionability during visual polish
- browser-native implementation playbook
- visual self-judge

### Covered in `remix_v5_core_skills.json`
- mechanics preservation and anti-lazy execution rails

### Enriched in second pass
- genre/style to technique mapping
- CDN-safe / browser-native implementation cookbook value
- explicit anti-pattern and guardrail transfer from the extended procedural graphics playbook

## D. `04_remix_v4_clone_final_mobile_repair_aggressive.md`

### Covered in `remix_v5_qa_skills.json`
- aggressive console/runtime triage
- mobile actionability and state exploration
- deterministic repair scope
- screenshot evidence and before/after comparison
- honest output contracts and risk reporting
- optional family-validation rules when multiple surfaces exist
- optional standalone screenshot artifact handling when explicitly requested

### Covered in `remix_v5_media_skills.json`
- media noise triage boundaries
- keep catalog-backed media stable unless truly blocking

### Enriched in second pass
- specific mobile tap-lifecycle anti-pattern repair rule
- explicit visual DNA / progression-family planning when level families exist

---

## 3. Second-Pass Enrichment Applied

The second pass was used to avoid losing value that often disappears during prompt-to-catalog decomposition:

- **analysis** gained explicit mechanics-ranking / semantic-tag output coverage and optional progression-rationale artifacts
- **media** gained asset inventory classification and structurally-feasible target selection
- **visual** gained implementation cookbook / genre-to-technique mapping / anti-pattern transfer
- **qa** gained the mobile `touchstart + preventDefault + click suppression` repair pattern and stronger family-progression audit language

---

## 4. Confidence Assessment

### Strongly preserved
- mechanic preservation rules
- authored world framing
- stock-scene replacement mandate
- procedural visual identity expectations
- mobile-first QA and runtime evidence discipline
- media catalog authority and safe wiring

### Explicitly guarded against loss
- prompt-specific implementation cookbook detail
- optional family QA and multilevel progression reasoning
- screenshot artifact and before/after proof expectations
- anti-pattern guidance for mobile tap breakage and shallow decorative fixes

### Remaining work before full confidence
- assemble the v5 super prompt from these skill catalogs
- ensure the direct rebuild phase is inserted between analysis and downstream skill execution
- validate that assembled prompt coverage includes all intended skill IDs and direct rebuild phases

---

## 5. Next Build Phase

With this audit in place, the next implementation steps are:

1. build `tools/game_refactoring/scripts/build_remix_v5_super_prompt.py`
2. generate `tools/game_refactoring/prompts/operators_v2/00_creative_remix_v5_super_operator.md`
3. register `creative_remix_v5` in `tools/game_refactoring/scripts/game_workflow.py`
4. validate catalog parsing + assembled prompt coverage + workflow wiring