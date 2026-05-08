# Creative Remix V1 Workflow Implementation Journal

**Last Updated:** 2026-05-07  
**Feature Spec:** `docs/game_workflow_cli.md`  
**Backend Reference:** N/A

---

## 📊 Implementation Status Overview

### ✅ Phase 1: Discovery and Constraints - **COMPLETE**

- [x] Confirm the new workflow name and intended stages
- [x] Verify generic manifest v2 supports new free-form node IDs
- [x] Verify remix prompt text is propagated into operator prompt context

**Status:** ✅ Complete

### Phase 2: Surgical Workflow Additions - **IN PROGRESS**

- [ ] Add `creative_remix_v1` to `scripts/game_workflow.py`
- [ ] Create four new prompt files for narrative, gameplay, visuals, and media_mapper
- [ ] Keep the change isolated to workflow wiring and prompt scaffolding only

**Status:** 🔧 In Progress

### Phase 3: Minimal Documentation and Verification - **PLANNED**

- [ ] Update `docs/game_workflow_cli.md` with the new workflow
- [ ] Verify all referenced prompt files and workflow paths are internally consistent

**Status:** Planned

---

## 📝 Journal Entries

### 2026-05-07 21:11 - Initial setup and compatibility verification

**What Changed:**
- Created a dedicated journal for the `creative_remix_v1` workflow task
- Confirmed the intended stage model is four stages: narrative, gameplay, visuals, and media_mapper
- Confirmed the workflow should be explicitly driven by the user remix prompt

**Why:**
This task requires a surgical addition to the high-level workflow CLI. Before modifying workflow definitions, the batch pipeline needed to be checked for two risk points: whether new node IDs are safe and whether the remix prompt is actually exposed to operator prompts.

**Files Investigated:**
- `scripts/game_workflow.py` - Existing high-level workflow CLI
- `scripts/run_operator_pipeline_batch.py` - Batch launcher prompt propagation
- `scripts/run_operator_pipeline_game.py` - Generic manifest v2 node loading and operator prompt construction
- `docs/game_workflow_cli.md` - Existing workflow CLI documentation

**Technical Findings:**
- Generic manifest v2 accepts free-form node IDs as long as they are unique
- Prompt files are resolved directly from the manifest and validated for existence
- `--remix-prompt` is propagated into run state and then injected into the operator prompt text
- If no remix prompt is present, fallback behavior uses display name sanitization, which confirms that explicitly prompt-driven stage instructions are the right place to strengthen remix steering without changing CLI plumbing

**Key Code References:**
```python
# scripts/run_operator_pipeline_game.py
node_id = _require_manifest_nonempty_string(node_payload, "id", f"nodes[{index}]")
prompt_file = _require_manifest_nonempty_string(node_payload, "prompt_file", f"nodes[{index}]")
```

```python
# scripts/run_operator_pipeline_game.py
prompt_text = run_state.get("remix_prompt")
if not isinstance(prompt_text, str) or not prompt_text.strip():
    prompt_text = sanitize_display_name_for_prompt(...)
```

**Next Steps:**
- [ ] Add the new workflow definition in `scripts/game_workflow.py`
- [ ] Create the four new stage prompt files
- [ ] Add the minimal documentation update
- [ ] Verify the new workflow wiring is internally consistent

**Status:** In Progress

---

## 🐛 Known Issues

### No known implementation issues yet

**Problem:** 
No code changes have been applied yet.

**Root Cause:** 
N/A

**Status:** 
- [ ] Being investigated
- [ ] Blocked (waiting for...)
- [ ] Fixed

**Workaround:** 
N/A

**Resolution:** 
N/A

---

## 📚 Quick Reference

### Key Files

- `scripts/game_workflow.py` - Workflow definition registry for named high-level flows
- `scripts/run_operator_pipeline_batch.py` - Forwards remix prompt into per-game workers
- `scripts/run_operator_pipeline_game.py` - Loads generic manifest v2 nodes and injects remix prompt into operator prompts
- `docs/game_workflow_cli.md` - User-facing workflow CLI documentation
- `prompts/operators_v2/` - Location for new prompt scaffolds

### Important Commands

```bash
python3 scripts/game_workflow.py \
  --id creative_remix_v1 \
  --games-manifest-source fixtures/specimen_random10_inference_playwright_manifest.json \
  --remix-prompt "your remix direction here"
```

---

## 💭 Notes & Decisions

### Design Decisions

**Decision:** Implement `creative_remix_v1` as a generic manifest v2 workflow addition only.  
**Rationale:** This preserves the existing orchestration path and keeps the change isolated to workflow wiring and new prompt scaffolds.  
**Alternatives Considered:** Modifying core batch or operator pipeline plumbing was rejected because the user requested a surgical change and the existing CLI already forwards remix prompt text.

### Future Enhancements

**Nice to Have:**
- Stage-specific contract conventions if the new remix workflow evolves beyond scaffold prompts
- More explicit workflow docs showing prompt-driven usage examples

---

## ✅ Testing Checklist

- [ ] Workflow definition added without affecting existing workflows
- [ ] All four prompt files exist at the referenced paths
- [ ] Documentation reflects the new workflow
- [ ] Manual dry-run validation path identified

---

## 🎯 Success Criteria

- [ ] `creative_remix_v1` exists in the workflow CLI
- [ ] The workflow contains four stages only
- [ ] Each stage has its own scaffolded prompt file
- [ ] The prompts emphasize the user remix prompt as the steering source
- [ ] No unrelated CLI or pipeline behavior is changed
- [ ] Documentation updated minimally

---

*This journal documents the surgical addition of the `creative_remix_v1` workflow to the high-level workflow CLI.*