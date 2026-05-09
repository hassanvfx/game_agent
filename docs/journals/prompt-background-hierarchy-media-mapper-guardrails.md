# Prompt Background Hierarchy and Media Mapper Guardrails Journal

**Last Updated:** 2026-05-08 20:45  
**Feature Spec:** N/A  
**Backend Reference:** See [clineflow/index.json](./index.json) for API file paths

---

## 📊 Implementation Status Overview

### ✅ Phase 1: Prompt Review and Planning - **COMPLETE**

- [x] Review narrative, gameplay, visual-first, visual redesign, and media mapper prompts
- [x] Define cross-stage guidance for animated background hierarchy
- [x] Define non-destructive media mapper boundaries

**Status:** ✅ Complete

### Phase 2: Prompt Updates - **COMPLETE**

- [x] Update gameplay prompt with secondary reactive background guidance
- [x] Update narrative prompt with animated-background idealization guidance
- [x] Update visual-first prompt with secondary visual-weight background rules
- [x] Update visual redesign prompt with protected authored-scene refinement rules
- [x] Update media mapper prompt with like-for-like replacement boundaries

**Status:** ✅ Complete

### Phase 3: Verification - **COMPLETE**

- [x] Verify edited prompt text is coherent across stages
- [x] Confirm media mapper is explicitly prevented from downgrading prior visual-stage background work

**Status:** Complete

### Phase 4: Level Adapter World Evolution - **COMPLETE**

- [x] Update level adapter with world-identity guidance across levels
- [x] Add visual evolution rules for five unique-but-related metaverse worlds
- [x] Extend level-planning artifacts to track world progression and visual continuity

**Status:** Complete

### Phase 5: Two-Game Raw-Backed Prompt Experiment - **IN PROGRESS**

- [ ] Add a setup script that selects 2 raw-backed games from the Vatsal top set
- [ ] Configure one run for `harry potter` and one run for `rick and morty`
- [ ] Launch the experiment scaffold and capture run metadata

**Status:** In Progress

### Phase 6: Full Background Lifecycle Hardening - **COMPLETE**

- [x] Update narrative/gameplay prompts to imagine and plan authored animated worlds rather than tolerate cheap stock scene ownership
- [x] Update visual/repair prompts to require authored-world creation and removal/demotion of dominant stock image backgrounds
- [x] Update media mapper and level adapter prompts to preserve and evolve the authored world across later stages

**Status:** Complete

---

## 📝 Journal Entries

### 2026-05-08 20:45 - Initial Prompt Guardrail Setup

**What Changed:**
- Created a task journal for the cross-stage prompt-guidance change
- Captured the requested background hierarchy concept and media-mapper preservation rule
- Began implementation by updating the gameplay prompt

**Why:**
The user wants the remix pipeline to consistently treat animated backgrounds as idealized but secondary visual support. Earlier stages should introduce and refine that world layer, while later media mapping must avoid flattening or replacing stronger authored scene work with simpler mapped assets.

**Files Created:**
- `docs/journals/prompt-background-hierarchy-media-mapper-guardrails.md` - Tracks this prompt-guidance task

**Next Steps:**
- [x] Update the narrative prompt with early animated-background concept framing
- [x] Update the visual-first and visual redesign prompts with visual hierarchy language
- [x] Update the media mapper prompt with explicit non-destructive guardrails
- [x] Verify coherence across all edited prompts

**Status:** Complete

---

### 2026-05-08 20:47 - Cross-Stage Guardrails Applied

**Achievement:**
Applied the requested animated-background hierarchy and non-destructive media-mapper guidance across the targeted prompt stages.

**Implementation Details:**
- Updated `tools/game_refactoring/prompts/operators_v2/01_creative_remix_v1_narrative.md` - added narrative guidance to idealize animated backgrounds as secondary worldbuilding support
- Updated `tools/game_refactoring/prompts/operators_v2/02_creative_remix_v1_gameplay.md` - added secondary reactive background framing and explicit non-mechanical limits
- Updated `tools/game_refactoring/prompts/operators_v2/03_creative_remix_v1_visuals.md` - added background hierarchy guidance and authored-background preservation rules
- Updated `tools/game_refactoring/prompts/operators_v2/06_creative_remix_v3_visual_ui_redesign.md` - added atmospheric support-layer guidance for animated backgrounds during redesign
- Updated `tools/game_refactoring/prompts/operators_v2/03_media_mapper.md` - added like-for-like and non-destructive media-mapper boundaries to protect earlier visual-stage scene work

**Technical Decisions:**
The guidance was distributed by stage responsibility rather than forcing one generic rule everywhere. Narrative introduces the idea, gameplay constrains its meaning, visual stages control hierarchy and preservation, and media mapper is explicitly prevented from flattening richer prior scene work into simpler mapped assets.

**Testing:**
Manual prompt review confirmed the requested through-line:
- narrative idealizes the animated background
- gameplay keeps it decorative and non-mechanical
- visual stages keep it secondary in visual weight
- media mapper preserves earlier authored scene/background work

**Next Steps:**
- [x] Confirm all target prompts were updated
- [x] Confirm animated background hierarchy is explicit across stages
- [x] Confirm media mapper guardrails prevent destructive downgrades of prior visual-stage work

**Status:** Complete

---

### 2026-05-08 20:52 - Level Adapter World Evolution Added

**Achievement:**
Extended the level-adapter stage so the five-level ladder now evolves as five distinct but related worlds within the same metaverse.

**Implementation Details:**
- Updated `tools/game_refactoring/prompts/operators_v2/10_creative_remix_v3_level_adapter.md` - added Mario-style world-identity guidance across levels
- Added a `World Identity Across Levels` section to require each level to read as its own world while preserving shared visual DNA
- Added a `Visual Evolution Across Levels` section to let animated backgrounds and scene framing convey evolving time, stakes, world state, and storyline
- Expanded `progressive_disclosure_plan.md` requirements to include visual world identity, cross-level continuity, and background-driven metaverse storytelling
- Expanded `level_adapter_rationale.md` requirements to explain how world progression stays readable, related, and non-mechanical

**Technical Decisions:**
The new rules make level progression evolve on two synchronized tracks:
- mechanical complexity
- world identity / visual storytelling

This preserves the prior background hierarchy rule by keeping background evolution secondary to gameplay readability, while still allowing each level to feel like a unique world in the same metaverse family.

**Testing:**
Manual review confirmed the level adapter now requires:
- five visually unique-but-related worlds
- metaverse continuity across levels
- animated-background evolution as world/story signaling
- clear restrictions against turning atmosphere into fake mechanics or clutter

**Next Steps:**
- [x] Confirm the level adapter defines world identity across levels
- [x] Confirm artifact requirements cover both gameplay and visual evolution
- [x] Confirm background evolution remains secondary to gameplay readability

**Status:** Complete

---

## 🐛 Known Issues

### None currently documented

**Problem:** 
No implementation issues recorded yet.

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

- `tools/game_refactoring/prompts/operators_v2/01_creative_remix_v1_narrative.md` - Narrative-stage guidance
- `tools/game_refactoring/prompts/operators_v2/02_creative_remix_v1_gameplay.md` - Gameplay-stage framing and truthfulness rules
- `tools/game_refactoring/prompts/operators_v2/03_creative_remix_v1_visuals.md` - Visual-first authored look and hierarchy rules
- `tools/game_refactoring/prompts/operators_v2/06_creative_remix_v3_visual_ui_redesign.md` - Second-pass visual/UI refinement rules
- `tools/game_refactoring/prompts/operators_v2/03_media_mapper.md` - Media-mapper scope and wiring rules

### Useful Links

- [Journal Template](../../clineflow/JOURNAL_TEMPLATE.md)

---

### 2026-05-08 20:54 - Two-Game Raw-Backed Experiment Requested

**Achievement:**
Started a follow-up experiment setup for two raw-backed games selected from the Vatsal top set, with one run for `harry potter` and one for `rick and morty`.

**Implementation Details:**
- Reviewed the existing raw-backed manifest builder at `tmp/game_refactoring_experiments/scripts/build_vatsal100_raw_backed_manifest.py`
- Reviewed the existing disposable experiment scaffold at `tmp/game_refactoring_experiments/scripts/setup_four_game_lane_collision_experiment.py`
- Confirmed the reusable pieces needed for:
  - selecting from Vatsal ids resolved against `games/raw`
  - writing manifests/prompts/metadata
  - launching run workflows from a setup script

**Technical Decisions:**
The new experiment should reuse the existing raw-backed Vatsal selection logic but produce a simpler two-game setup with two fixed prompts:
- `harry potter`
- `rick and morty`

**Next Steps:**
- [ ] Create the two-game raw-backed experiment setup script
- [ ] Run the setup script
- [ ] Capture selected games, manifests, and launched run metadata

**Status:** In Progress

---

### 2026-05-08 21:04 - Full Background Lifecycle Hardening Requested

**Achievement:**
Started a broader prompt hardening pass to enforce the full authored-background lifecycle from narrative through level adaptation.

**Implementation Details:**
- Confirmed a real failure case in a generated `node_04_visuals` workspace where a stock image background still owned the scene while the “animated background” was only decorative garnish
- Identified the needed lifecycle chain:
  - imagine
  - plan
  - create
  - refine
  - keep
  - adapt across levels
- Expanded scope beyond the visual pass alone so later stages cannot preserve or reintroduce the same failure mode

**Technical Decisions:**
The background rule must become a full pipeline contract:
- narrative imagines the authored world
- gameplay plans decorative/non-mechanical world response
- visuals create the true scene foundation
- repair removes/demotes stock scene ownership if it survives
- media mapper protects the authored world from flattening
- level adapter evolves the same world family across levels

**Next Steps:**
- [x] Patch the prompt files from narrative through level adapter
- [x] Explicitly forbid dominant cheap stock image backgrounds from counting as the authored world
- [x] Verify the new lifecycle wording is consistent across stages

**Status:** Complete

---

### 2026-05-08 21:09 - Full Background Lifecycle Hardening Applied

**Achievement:**
Applied the authored-background lifecycle rule across the full remix chain so cheap stock image scenes can no longer survive as the dominant world layer.

**Implementation Details:**
- Updated `tools/game_refactoring/prompts/operators_v2/01_creative_remix_v1_narrative.md` - narrative now imagines a true authored animated world rather than tolerating stock backdrops
- Updated `tools/game_refactoring/prompts/operators_v2/02_creative_remix_v1_gameplay.md` - gameplay now plans decorative world response without legitimizing unchanged stock scene ownership
- Updated `tools/game_refactoring/prompts/operators_v2/03_creative_remix_v1_visuals.md` - visuals now explicitly fail if a cheap stock/static background image still owns the playfield
- Updated `tools/game_refactoring/prompts/operators_v2/06_creative_remix_v3_visual_ui_redesign.md` - redesign now treats surviving stock scene ownership as unfinished visual work
- Updated `tools/game_refactoring/prompts/operators_v2/09_creative_remix_v3_final_mobile_repair.md` - final repair now recovers dominant stock scene ownership if earlier passes failed
- Updated `tools/game_refactoring/prompts/operators_v2/03_media_mapper.md` - media mapper now preserves the authored world rather than cheap placeholder scene ownership
- Updated `tools/game_refactoring/prompts/operators_v2/10_creative_remix_v3_level_adapter.md` - level adaptation now evolves the authored world across levels rather than preserving a placeholder stock scene

**Technical Decisions:**
The rule was made lifecycle-wide instead of local to visuals:
- imagine in narrative
- plan in gameplay
- create in visuals
- refine in redesign/final repair
- keep in media mapper
- adapt in levels

This closes the failure mode where decorative atmosphere is added while the real scene foundation remains a generic stock background image.

**Testing:**
Manual review confirmed every targeted downstream stage now rejects the anti-pattern of leaving a cheap static stock background as the dominant world layer while calling the result an authored animated background.

**Next Steps:**
- [x] Confirm the lifecycle wording is present from narrative through level adapter
- [x] Confirm cheap stock image dominance is explicitly disallowed
- [x] Confirm later stages preserve and evolve the authored world rather than the placeholder scene

**Status:** Complete

---

### 2026-05-08 21:20 - Remix theme design-system artifact added to narrative and visual stages

**Achievement:**
Extended the prompt chain so the narrative stage now defines an explicit remix design system in `remix_theme.json`, and both visual stages are instructed to consume that artifact directly.

**Implementation Details:**
- Updated `tools/game_refactoring/prompts/operators_v2/01_creative_remix_v1_narrative.md`
  - added a required `remix_theme.json` artifact
  - defined it as a compact role-based visual mapping system
  - required mappings for current/default colors, shapes, panel styles, CTA treatments, and broader authored-world styling cues
- Updated `tools/game_refactoring/prompts/operators_v2/03_creative_remix_v1_visuals.md`
  - made `remix_theme.json` a required design-system contract when present
  - explicitly told the visuals stage to map current colors, shapes, surfaces, and primitives through that artifact
  - required propagation across UI, HUD, CTA, panels, environment, and category differentiation
- Updated `tools/game_refactoring/prompts/operators_v2/06_creative_remix_v3_visual_ui_redesign.md`
  - added `remix_theme.json` to optional upstream artifacts
  - required the redesign pass to treat it as the system for remapping existing colors, shapes, surfaces, and styles into the authored remix identity
  - reinforced whole-surface propagation during second-pass polish

**Technical Decisions:**
The new artifact is defined as a compact implementation-facing mapping system, not a vague mood board. That keeps later stages grounded in:
- role-based palette mapping
- shape-language mapping
- CTA / panel / border treatment rules
- focal actor and environment styling cues
- consistent visual do / do-not rules

This should reduce drift between narrative intention and later visual execution.

**Testing:**
Manual review confirmed:
- narrative now creates `remix_theme.json`
- first visual pass explicitly consumes it
- second visual/redesign pass explicitly propagates it

**Next Steps:**
- [x] Confirm the narrative stage creates `remix_theme.json`
- [x] Confirm the first visual pass treats it as a required contract when present
- [x] Confirm the redesign pass propagates the same design system across the full UI/game surface

**Status:** Complete

---

### 2026-05-08 21:39 - Visual UI redesign prompt hardened to Playwright-only runtime validation

**Achievement:**
Strengthened the visual UI redesign stage so it can no longer casually validate through an external/system browser and must rely only on the assigned Playwright runtime.

**Implementation Details:**
- Updated `tools/game_refactoring/prompts/operators_v2/06_creative_remix_v3_visual_ui_redesign.md`
  - expanded the baseline screenshot rules
  - added a dedicated `Playwright-Only Runtime Validation Rule`
  - explicitly forbade:
    - external/system browser use
    - ad-hoc manual browser checking outside the assigned Playwright runtime
    - attaching to another localhost server
    - choosing another port
  - required all screenshots, state checks, and browser-grounded evidence to come only from the assigned Playwright runtime and be written into the current attempt workspace

**Technical Decisions:**
This mirrors the stronger runtime-discipline philosophy already present in the later mobile repair stage, but moves that guardrail earlier into the visual UI redesign pass where inappropriate external browser validation was still slipping in.

**Testing:**
Manual review confirmed the redesign stage now clearly states:
- Playwright-only runtime validation
- no external/system browser fallback
- no alternate localhost attachment
- workspace-local screenshot/evidence requirements

**Status:** Complete

---

## 💭 Notes & Decisions

### Design Decisions

**Decision:** Animated backgrounds should be introduced as authored worldbuilding but remain secondary in gameplay visual weight.  
**Rationale:** This preserves readability, focal identity, and control clarity while still allowing richer scene presentation.  
**Alternatives Considered:** Letting the background act as a co-equal visual layer was rejected because it risks overwhelming gameplay-facing elements.

**Decision:** Media mapper should not overwrite complex prior visual-stage scene work with simpler mapped assets.  
**Rationale:** The media-mapper stage should enrich and safely wire approved media, not downgrade authored graphics or background animation systems.  
**Alternatives Considered:** Broad replacement authority for media mapper was rejected because it can erase stronger prior-stage art direction.

---

## ✅ Testing Checklist

- [x] Manual review of all edited prompts
- [x] Cross-stage consistency check
- [x] Confirm media mapper boundaries are explicit and enforceable

---

## 🎯 Success Criteria

- [x] All target prompts updated
- [x] Animated background hierarchy is explicit across relevant stages
- [x] Media mapper guardrails prevent destructive downgrades of prior visual-stage work
- [x] Level adapter defines five visually unique worlds in one metaverse family
- [x] Level-planning artifacts require both mechanical and visual world progression
- [x] Cheap stock image backgrounds are explicitly disallowed from remaining the dominant authored world layer
- [x] The authored world lifecycle is defined from narrative through level adaptation
- [x] The narrative stage creates a compact `remix_theme.json` design-system artifact for later stages
- [x] Both visual stages explicitly consume and propagate `remix_theme.json` when present
- [x] The visual UI redesign stage explicitly requires Playwright-only runtime validation and forbids external/system browser fallback
