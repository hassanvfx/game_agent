# Vatsaltop100 App Alpha Batch Implementation Journal

**Last Updated:** 2026-05-10  
**Feature Spec:** App alpha published catalog + annotator collection support  
**Backend Reference:** See repository tools under `tools/game_publish_pipeline/`, `tools/game_deploy/`, and published artifacts under `games/published/`

---

## 📊 Implementation Status Overview

### ✅ Phase 1: Discovery and schema verification - **COMPLETE**

- [x] Inspect existing published metadata schemas
- [x] Verify canonical published remix directory shape in code
- [x] Lock generated identity key strategy
- [x] Lock lineage field naming

**Status:** ✅ Complete

### Phase 2: Source-set resolution and manifest design - **COMPLETE**

- [x] Inspect annotator consumer and app descriptor
- [x] Identify canonical 50-game shipped remix batch
- [x] Identify canonical published Vatsal top107 remix set
- [x] Define the normalized 157-entry batch manifest

**Status:** ✅ Complete

### Phase 3: Generator implementation - **COMPLETE**

- [x] Build generalized published metadata generator
- [x] Support full-scan mode over published remix folders
- [x] Support manifest-constrained subset mode
- [x] Emit `index.json`, `app_tags.json`, and `app.json`

**Status:** ✅ Complete

### Phase 4: Collection integration and validation - **IN PROGRESS**

- [ ] Add App Alpha Batch collection support to annotator/app flow
- [x] Generate 157-entry outputs
- [x] Validate counts, paths, identity keys, and lineage fields
- [ ] Document final outputs and verification

**Status:** 🔧 In Progress

---

## 📝 Journal Entries

### 2026-05-10 13:35 - Master plan established

**What Changed:**
- Created the master implementation journal for the app alpha batch work.
- Consolidated the current planning decisions into one source of truth.
- Recorded the current verified architecture and the remaining implementation phases.

**Why:**
- This task spans schema design, generator implementation, collection wiring, and validation.
- A persistent journal is required by project rules and also reduces drift while switching between planning and execution.

**Current Verified Decisions:**
- The published catalog unit is a **published remix entry**, not a bare `gamezone-id`.
- Verified publish/deploy shape:
  - `games/published/public/<game_id>/remix-<remix_uuid>/`
- Generated top-level record keys will use:
  - `gamezone-<id>__remix-<hash>`
- Future remix ancestry will be tracked with lineage metadata, not with primary-key overloading.
- Locked lineage field name:
  - `remix_parent_id`

**Planned Generated Record Model:**
```json
{
  "gamezone-abc__remix-123": {
    "game_id": "gamezone-abc",
    "remix_id": "remix-123",
    "published_path": "gamezone-abc/remix-123",
    "remix_parent_id": null,
    "root_game_id": "gamezone-abc",
    "lineage_depth": 0
  }
}
```

**Planned Outputs:**
- `games/published/index.json`
- `games/published/app_tags.json`
- `games/published/app.json`

**Planned Generator Modes:**
1. **Full scan mode**
   - scans all remix folders under `games/published/public/`
2. **Manifest mode**
   - constrains output to explicitly selected remix entries

**Planned Batch Name:**
- `Vatsaltop100_app_alpha_batch`

**Target Collection Contents:**
- 107 published remix entries for the Vatsal top107 set
- 50 published remix entries for the shipped app-alpha set
- Expected total: **157**

**Files Created:**
- `docs/journals/vatsaltop100-app-alpha-batch.md` - Master planning journal for this workstream

**Next Steps:**
- [ ] Add App Alpha Batch collection support to the annotator/app flow
- [ ] Update this journal with the completed implementation details and final validation summary

**Status:** In Progress

---

## 🧭 Canonical Architecture Decisions

### 1. Published identity model

**Canonical unit:** one published remix folder

**Filesystem shape:**
```text
games/published/public/<game_id>/remix-<remix_uuid>/
```

**Primary generated key:**
```text
gamezone-<id>__remix-<hash>
```

### 2. Lineage model

The key is only for uniqueness.

Lineage is stored separately in metadata:
- `remix_parent_id`
- `root_game_id`
- `lineage_depth`

This keeps:
- identity stable
- future remix-of-remix chains representable
- downstream key collisions avoidable

### 3. Output responsibilities

**`index.json`**
- inventory/file view
- assets, screenshots, file manifests

**`app_tags.json`**
- lightweight catalog for discovery/filtering
- tags, screenshots, title, description

**`app.json`**
- heavyweight catalog
- all lightweight fields plus `prompt` and `blueprint`

### 4. Generator strategy

A single generalized generator should support:
- repository-wide regeneration
- subset/batch generation from a manifest

This avoids creating separate one-off scripts for each batch.

---

## 🧱 Proposed Batch Manifest Shape

```json
{
  "batch_name": "Vatsaltop100_app_alpha_batch",
  "collection_slug": "vatsaltop100_app_alpha_batch",
  "generated_at": "2026-05-10T00:00:00Z",
  "entries": [
    {
      "game_id": "gamezone-abc",
      "remix_id": "remix-123",
      "composite_key": "gamezone-abc__remix-123",
      "published_path": "gamezone-abc/remix-123",
      "variant_group": "vatsal_top107",
      "remix_parent_id": null,
      "root_game_id": "gamezone-abc",
      "lineage_depth": 0
    }
  ]
}
```

---

## 🔍 Pending Verification Work

### Annotator/app integration surfaces
Need to inspect:
- `games/published/public/565a0bf4-5160-47b8-a905-2f4362475cdf-annotator.html`
- `games/published/public/7a075949-5edb-4e9e-89b1-84c32cf8db36-app.json`

Purpose:
- determine current collection loading assumptions
- determine whether collection descriptors must be added or transformed
- confirm whether current consumers assume plain `gamezone-id` keys

### Source-set discovery
Resolved canonical sources:
- 50-entry shipped app-alpha remix set:
  - `tmp/retry_manifests/latest_selected_remix_obfuscator_manifest.json`
- 107-entry Vatsal top107 raw-backed source set:
  - `tmp/game_refactoring_experiments/fixtures/top107_vatsal_raw_backed_full_manifest.json`

Normalization/output manifest created at:
- `tmp/retry_manifests/vatsaltop100_app_alpha_batch_manifest.json`

Verified summary:
- `top107_count = 107`
- `app_alpha_50_count = 50`
- `total_entries = 157`
- `unique_composite_keys = 157`
- `duplicate_keys = {}`

---

## ✅ Validation Requirements

### Identity validation
- Every generated composite key is unique
- Every key matches `game_id + remix_id`
- Every `published_path` resolves to an actual remix directory

### Count validation
- 107 entries in `vatsal_top107`
- 50 entries in `app_alpha_50`
- 157 total entries

### Output validation
- `index.json` contains 157 entries
- `app_tags.json` contains 157 entries
- `app.json` contains 157 entries

### Lineage validation
- `remix_parent_id` is null or points to a valid composite key
- `lineage_depth` is coherent with ancestry

### Frontend validation
- existing collection still loads by default
- `App alpha batch` appears as a selectable collection
- selecting it loads the correct 157-entry dataset

---

### 2026-05-10 15:16 - Shared metadata extractor split out for deploy/publish QA

**What Changed:**
- Extracted the game-folder scanning and metadata assembly logic from `tools/game_deploy/game_deploy/deployer.py` into a shared utility:
  - `tools/game_deploy/game_deploy/metadata_extractor.py`
- Updated the deployer to use the shared extractor instead of owning all of the scan/assembly steps inline.
- Added a quick sample harness:
  - `tmp/test_metadata_extractor_samples.py`
- Added a direct run-folder uniqueness checker:
  - `tmp/check_known_run_output_uniqueness.py`

**Why:**
- We need a fast deterministic loop before treating the 124 `run_id/game_id` folders as publish inputs.
- Pulling the folder-to-metadata conversion into one shared utility reduces drift between deploy behavior and QA behavior.
- A small harness lets us test representative source folders without running the full publisher pipeline.

**Validated Samples:**
- `run_v4_harry_potter_vatsal107_model55_c1_20260509T083751Z/output/gamezone-021fa461-bb56-4b35-ab57-25d8b29813e1`
- `run_v4_rick_morty_retry2_20260510T054341Z/output/gamezone-2afa409a-2d47-421c-8344-d85b635b2c3a`
- `run_v4_brainrot_momsday_retry2_20260509T174740Z/output/gamezone-0a438816-ecee-420b-afd6-4a36ddc935e3`

**Validation Outcome:**
- The shared extractor successfully produced:
  - inferred `game_id`
  - stable `remix_uuid` from folder hash
  - `index.html`
  - `assets_dir`
  - normalized `semantic_tags`
  - normalized `identity`
  - normalized `mechanics_classification`
  - `recreation_prompt_markdown`
  - `blueprint_markdown`
- The sample harness also surfaced real data gaps clearly:
  - all three tested samples had zero screenshots
  - one tested sample had empty semantic/mechanics payloads despite having identity/prompt/blueprint

**Run-Folder Uniqueness Finding:**
- The 17 listed run folders do **not** represent 50 unique folders when collapsed by `game_id`.
- Direct inspection found:
  - `124` unique `run_id/game_id` folders
  - `50` unique `game_id` values
  - `33` game IDs repeated across multiple runs
- This confirms we should think in terms of `run_id/game_id` as the raw publish candidate identity before any later selection/deduping.

**Files Added/Changed:**
- `tools/game_deploy/game_deploy/metadata_extractor.py`
- `tools/game_deploy/game_deploy/deployer.py`
- `tmp/test_metadata_extractor_samples.py`
- `tmp/check_known_run_output_uniqueness.py`

**Next Steps:**
- [ ] Expand the sample harness into a stricter QA judge for required fields
- [ ] Decide whether screenshots are required at publish time or only catalog time
- [ ] Run the shared extractor across a broader subset of the 124 raw run/game folders
- [ ] Define the manifest shape for passing the selected 124 `run_id/game_id` candidates into the publisher

### 2026-05-10 15:43 - 124 raw run/game extraction workflow established

**What Changed:**
- Added a manifest builder for the direct raw run/game input set:
  - `tmp/build_124_run_game_manifest.py`
- Generated:
  - `tmp/retry_manifests/run_game_124_manifest.json`
- Updated the shared extractor to emit richer lineage/remix fields:
  - `run_id`
  - `remix_id`
  - `remix_parent_id`
  - `root_game_id`
  - `lineage_depth`
- Wired those richer fields through the actual deploy flow and validated on a real published output.
- Ran the adapted JSON builder across the full 124 raw `run_id/game_id` entries:
  - `tmp/adapted_game_json_124.json`

**124-Set Summary:**
- Total extracted entries: `124`
- Entries with `run_id`: `124`
- Entries with `remix_id`: `124`
- Entries with screenshots: `123`
- Entries without screenshots: `1`
  - sample missing game: `gamezone-9597144a-ac05-4534-b2bd-9151b8a16c07`
- Entries with semantic tags: `124`
- Entries missing semantic tags: `0`
- Entries with mechanics classification: `115`
- Entries missing mechanics classification: `9`

**Why This Matters:**
- We now have a scriptable path from raw run folders to normalized full-info JSON at the 124-entry scale.
- The remaining data-quality gap is concentrated mostly in mechanics classification, not in semantics or run/remix identity.
- The actual publish flow is now aligned with the same shared extractor used by the test/adapted-json scripts.

**Files Added/Changed:**
- `tmp/build_124_run_game_manifest.py`
- `tmp/retry_manifests/run_game_124_manifest.json`
- `tmp/adapted_game_json_124.json`
- `tools/game_deploy/game_deploy/metadata_extractor.py`
- `tmp/build_adapted_game_json.py`

### 2026-05-10 15:45 - Commit note for next stage

**What Changed:**
- Prepared the repository for commit after establishing the 124-entry raw `run_id/game_id` extraction workflow.
- Recorded the explicit next-stage handoff note for follow-up implementation.

**Next Stage Comment:**
- Build a normalizer for the shape of the Vatsal top100 raw folders so their structure can be mapped deterministically into the same full games-info JSON schema.

### 2026-05-10 15:47 - Commit note for next stage

**What Changed:**
- Prepared the repository for commit after establishing the 124-entry raw `run_id/game_id` extraction workflow.
- Recorded the explicit next-stage handoff note for follow-up implementation.

**Next Stage Comment:**
- Build a normalizer for the shape of the Vatsal top100 raw folders so their structure can be mapped deterministically into the same full games-info JSON schema.

### 2026-05-10 16:01 - Legacy-layout extractor branch added and validated

**What Changed:**
- Extended `tools/game_deploy/game_deploy/metadata_extractor.py` with contract-safe layout detection so the extractor now supports:
  - the existing run-output layout
  - the raw Vatsal legacy layout
- Kept the extractor output contract stable:
  - same `ExtractedGameMetadata` dataclass
  - same normalized metadata payload keys
  - no run-layout branch contract changes
- Added internal legacy-layout behavior:
  - lowercase metadata files treated as primary
  - playwright evidence PNGs treated as screenshot sources
  - nested `remix-*` folders not treated as the primary root by default
- Added a reusable validation script:
  - `tmp/validate_top107_legacy_extraction.py`
- Generated full legacy-layout normalized output:
  - `tmp/adapted_game_json_top107_legacy.json`
- Generated full legacy-layout validation summary:
  - `tmp/adapted_game_json_top107_legacy_summary.json`

**Why:**
- The raw top107 Vatsal folders use a structurally different shape than the 124 run-output folders.
- We needed a second internal extraction strategy without breaking the existing publish/deploy contract.
- Using one shared extractor preserves consistency across deploy, publish, and QA scripts.

**Validation Outcome:**
- Backward compatibility spot-checks on representative run-layout folders still succeeded.
- Legacy-layout 10-sample validation succeeded with stable normalized output.
- Full top107 legacy extraction completed successfully:
  - `entry_count = 107`
  - `with_assets_dir = 102`
  - `with_screenshot_files = 106`
  - `with_semantic_tags = 107`
  - `with_identity = 107`
  - `with_mechanics_classification = 107`
  - `with_recreation_prompt = 107`
  - `with_blueprint = 107`
- Data gaps observed in the full legacy set:
  - 5 entries without `assets_dir`
  - 1 entry without screenshots
    - `gamezone-9dfd3280-7905-484c-a7cd-714850d499ee`

**Files Added/Changed:**
- `tools/game_deploy/game_deploy/metadata_extractor.py`
- `tmp/validate_top107_legacy_extraction.py`
- `tmp/adapted_game_json_top107_legacy.json`
- `tmp/adapted_game_json_top107_legacy_summary.json`

### 2026-05-10 16:03 - Legacy deployer smoke test succeeded against raw folder input

**What Changed:**
- Added a script-based deploy smoke test:
  - `tmp/smoke_test_legacy_deployer.py`
- Ran the actual deployer path against a representative raw legacy folder:
  - `games/raw/gamezone-0f3dc736-8159-48cf-93d0-bd78a54b8cd0`
- Deployed into a temporary published root:
  - `tmp/deploy_smoke_legacy_public/`
- Wrote a deploy verification summary:
  - `tmp/deploy_smoke_legacy_summary.json`

**Why:**
- The extractor-only validation was necessary but not sufficient.
- We also needed to confirm the real deployer path can consume raw legacy folders end-to-end and emit a proper published remix bundle.

**Smoke-Test Outcome:**
- The deployer accepted the raw legacy folder directly.
- It produced:
  - `index.html`
  - copied assets
  - `screenshots/` with `4` PNG files
  - `game-obfuscated-995250285d1bbbd61938f53ee080a8ee.json`
- The emitted metadata preserved the expected deploy contract keys:
  - `game_id`
  - `run_id`
  - `remix_id`
  - `remix_parent_id`
  - `root_game_id`
  - `lineage_depth`
  - `semantic_tags`
  - `identity`
  - `mechanics_classification`
  - screenshot fields
  - `deploy`
- Verified deploy metadata source path:
  - `games/raw/gamezone-0f3dc736-8159-48cf-93d0-bd78a54b8cd0`

**Files Added/Changed:**
- `tmp/smoke_test_legacy_deployer.py`
- `tmp/deploy_smoke_legacy_public/`
- `tmp/deploy_smoke_legacy_summary.json`

### 2026-05-10 16:08 - Full 107 legacy deploy batch completed

**What Changed:**
- Added a manifest builder for real deploy inputs:
  - `tmp/build_top107_legacy_deploy_manifest.py`
- Generated:
  - `tmp/retry_manifests/top107_legacy_deploy_manifest.json`
- Added a full deploy smoke-batch runner:
  - `tmp/run_top107_legacy_deploy_smoke.py`
- Ran the 107-entry deployer batch into a temporary published root:
  - `tmp/deploy_smoke_top107_legacy_public/`
- Generated smoke-batch verification:
  - `tmp/deploy_smoke_top107_legacy_summary.json`
- Added the real deploy runner:
  - `tmp/run_top107_legacy_deploy_real.py`
- Ran the real 107 deploy pass into:
  - `games/published/public`
- Generated real deploy summary:
  - `tmp/deploy_real_top107_legacy_summary.json`

**Why:**
- After validating extractor-only behavior and a single-folder deploy smoke test, the next required proof was full-batch deployer execution.
- Running a temporary-root smoke batch first reduced risk before touching the real published tree.

**107-Batch Smoke Summary:**
- `entry_count = 107`
- `with_index = 107`
- `with_assets_dir = 102`
- `with_screenshots = 106`
- `with_semantic_tags = 107`
- `with_identity = 107`
- `with_mechanics = 107`
- `with_recreation_prompt = 107`
- `with_blueprint = 107`

**Observed Gaps:**
- 5 entries without copied assets
- 1 entry without screenshots:
  - `gamezone-9dfd3280-7905-484c-a7cd-714850d499ee`

**Outcome:**
- The full 107-entry deploy smoke batch succeeded.
- The real 107-entry deploy pass into `games/published/public` also completed successfully.

**Files Added/Changed:**
- `tmp/build_top107_legacy_deploy_manifest.py`
- `tmp/retry_manifests/top107_legacy_deploy_manifest.json`
- `tmp/run_top107_legacy_deploy_smoke.py`
- `tmp/deploy_smoke_top107_legacy_public/`
- `tmp/deploy_smoke_top107_legacy_summary.json`
- `tmp/run_top107_legacy_deploy_real.py`
- `tmp/deploy_real_top107_legacy_summary.json`
- `games/published/public/` (107 new legacy deploy outputs)

### 2026-05-10 16:26 - Merged 231-entry Vatsal App Alpha collection generated and wired into annotator

**What Changed:**
- Audited the merged `107 + 124` set with a dedicated uniqueness script:
  - `tmp/audit_merged_107_124_uniqueness.py`
- Verified the merged set is additive at the remix/composite-key layer:
  - `231` total entries
  - `231` unique remix UUIDs
  - `231` unique composite keys
  - repeated `game_id` values only, no remix/composite collisions
- Added a merged manifest builder:
  - `tmp/build_vatsal_app_alpha_231_manifest.py`
- Generated:
  - `tmp/retry_manifests/vatsal_app_alpha_231_manifest.json`
- Added a real deploy catch-up runner for the 124 run-output set:
  - `tmp/run_124_real_deploy.py`
- Ran the 124 deploy pass against `games/published/public`:
  - `57` newly deployed
  - `67` already present and skipped
- Added a merged collection generator:
  - `tmp/generate_vatsal_app_alpha_collection.py`
- Generated merged catalog artifacts:
  - `tmp/generated_collections/vatsal_app_alpha/index.json`
  - `tmp/generated_collections/vatsal_app_alpha/app_tags.json`
  - `tmp/generated_collections/vatsal_app_alpha/app.json`
- Published collection-facing files into the public folder:
  - `games/published/public/vatsal_app_alpha-index.json`
  - `games/published/public/vatsal_app_alpha-app_tags.json`
  - `games/published/public/vatsal_app_alpha-app.json`
- Updated the public annotator HTML:
  - `games/published/public/565a0bf4-5160-47b8-a905-2f4362475cdf-annotator.html`
- Added a dataset switcher so the annotator can toggle between:
  - `current_release`
  - `vatsal_app_alpha`

**Validation Outcome:**
- Merged manifest summary:
  - `legacy_107_count = 107`
  - `run_124_count = 124`
  - `total_entries = 231`
  - `unique_composite_keys = 231`
- Generated public collection files all contain `231` entries:
  - `vatsal_app_alpha-index.json`
  - `vatsal_app_alpha-app_tags.json`
  - `vatsal_app_alpha-app.json`
- Annotator wiring now includes:
  - dataset selector UI
  - persisted dataset choice in local storage
  - dynamic fetch path switching between the original app JSON and the new Vatsal App Alpha dataset

**Files Added/Changed:**
- `tmp/audit_merged_107_124_uniqueness.py`
- `tmp/merged_107_124_uniqueness_audit.json`
- `tmp/build_vatsal_app_alpha_231_manifest.py`
- `tmp/retry_manifests/vatsal_app_alpha_231_manifest.json`
- `tmp/run_124_real_deploy.py`
- `tmp/deploy_real_run124_summary.json`
- `tmp/generate_vatsal_app_alpha_collection.py`
- `tmp/generated_collections/vatsal_app_alpha/index.json`
- `tmp/generated_collections/vatsal_app_alpha/app_tags.json`
- `tmp/generated_collections/vatsal_app_alpha/app.json`
- `games/published/public/vatsal_app_alpha-index.json`
- `games/published/public/vatsal_app_alpha-app_tags.json`
- `games/published/public/vatsal_app_alpha-app.json`
- `games/published/public/565a0bf4-5160-47b8-a905-2f4362475cdf-annotator.html`

## 📚 Quick Reference

### Key files
- `tools/game_publish_pipeline/game_publish_pipeline/pipeline.py`
- `tools/game_deploy/game_deploy/deployer.py`
- `games/published/index.json`
- `games/published/app_tags.json`
- `games/published/app.json`
- `games/published/public/7a075949-5edb-4e9e-89b1-84c32cf8db36-app.json`
- `games/published/public/565a0bf4-5160-47b8-a905-2f4362475cdf-annotator.html`

### Implemented new files
- `docs/journals/vatsaltop100-app-alpha-batch.md`
- `tmp/inspect_batch_sources.py`
- `tmp/build_vatsaltop100_app_alpha_batch_manifest.py`
- `tmp/retry_manifests/vatsaltop100_app_alpha_batch_manifest.json`
- `scripts/generate_published_app_metadata.py`
- `tmp/verify_generated_published_metadata.py`

---

## 🎯 Success Criteria

- [ ] Master journal maintained
- [x] Exact source sets for 107 + 50 resolved
- [x] Batch manifest created
- [x] Generalized generator implemented
- [x] Full-scan mode works
- [x] Manifest-constrained mode works
- [x] 157-entry app-alpha outputs generated
- [ ] Annotator/app collection switching updated
- [x] Counts, paths, and lineage validated

---

*This journal is the master planning source for the Vatsaltop100 app alpha published catalog and annotator collection work.*

### 2026-05-10 18:35 - Obfuscation contract mapped into dataset generation

**What Changed:**
- Updated `scripts/generate_published_app_metadata.py` so obfuscation detection follows the publisher contract instead of relying only on a naive remix-relative mirror path.
- Added per-item `obfuscation_status` metadata to generated records in:
  - `index.json`
  - `app_tags.json`
  - `app.json`
- Added contract loading from:
  - `tmp/retry_manifests/latest_selected_remix_obfuscator_manifest.json`
- Added fallback resolution for the actual published obfuscated layout now observed in the repository:
  - `games/published/obfuscated/<game_id>/index.html`
- Regenerated the `vatsal_app_alpha` dataset with the new contract-aware fields.
- Updated `tmp/verify_obfuscated_path_shape.py` to validate the saved per-item obfuscation status instead of only checking a guessed path shape.

**Why:**
- The annotator needs verified per-item play targets, not guessed path rewrites.
- The obfuscator manifest still reflects the publisher contract inputs, but the current obfuscated output layout is game-level in practice for most published outputs.
- Saving explicit status in generated metadata makes the dataset the source of truth for downstream UI behavior.

**Validation Summary:**
- Regenerated entries: `231`
- Verification output:
  - `checked_count = 231`
  - `with_variant_count = 229`
  - `missing_contract_index_count = 0`
  - `missing_contract_match_count = 182`
- Interpretation:
  - `229/231` items now resolve to a verified obfuscated playable target.
  - The manifest-based contract only directly matched the historical 49-item selected-remix subset.
  - The broader `229` coverage comes from validating the actual published obfuscated game-level layout.

**Files Changed:**
- `scripts/generate_published_app_metadata.py`
- `tmp/regenerate_vatsal_app_alpha_with_obfuscation_fields.py`
- `tmp/verify_obfuscated_path_shape.py`
- `games/published/public/vatsal_app_alpha-index.json`
- `games/published/public/vatsal_app_alpha-app_tags.json`
- `games/published/public/vatsal_app_alpha-app.json`

**Notes for Follow-up:**
- The generator contract is now good enough for annotator consumption.
- Remaining UI work is to move the obfuscation toggle into the iframe toolbar and validate reload behavior against `vatsal_app_alpha`.
