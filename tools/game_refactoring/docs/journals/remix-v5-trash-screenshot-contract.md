# Remix v5 Trash Screenshot Contract Journal

**Last Updated:** 2026-05-17 05:21 America/Mexico_City  
**Feature Spec:** Align Remix v5 disposable before-screenshot naming with the `_trash` lifecycle contract.

---

## 📊 Implementation Status Overview

### ✅ Phase 1: Investigation - **COMPLETE**

- [x] Inspect the v5 super operator prompt and related code paths for screenshot naming rules
- [x] Trace how screenshot filename instructions are generated and passed into the pipeline
- [x] Identify why `_trash.ext` naming was being ignored

**Status:** ✅ Complete

### ✅ Phase 2: Source-of-Truth Fix - **COMPLETE**

- [x] Update the seeded Remix v5 template manifest to require a `_trash` before screenshot artifact
- [x] Confirm the conflict came from the source template contract rather than the seeded file bodies

**Status:** ✅ Complete

### ✅ Phase 3: Verification - **COMPLETE**

- [x] Re-scan source files for remaining hardcoded legacy before-screenshot references
- [x] Document verification steps for a future v5 run

**Status:** ✅ Complete

---

## 📝 Journal Entries

### 2026-05-17 05:21 - Root cause and contract fix

**Achievement:**
Located and fixed the source-of-truth contract conflict that caused disposable original-game screenshots to keep an `_old` filename.

**Implementation Details:**
- Updated `fixtures/remix_v5_contract_templates/manifest.json` so the required runtime-generated before screenshot is now `v5_before_index_trash.png`.
- Confirmed the active v5 super-operator prompt already instructs operators to use `_trash.png` for temporary original-game reference captures.
- Confirmed the seeded template files themselves did not hardcode the legacy before-screenshot filename; the conflict originated from the manifest's required runtime artifact list.

**Technical Decisions:**
I changed the template manifest rather than generated run artifacts because the manifest is the upstream contract copied into new attempt workspaces. Fixing the contract source prevents future runs from reintroducing the `_old` screenshot requirement.

**Testing:**
- Re-scan source directories for remaining hardcoded legacy before-screenshot references.
- Verify a future Remix v5 workspace seeds `v5_before_index_trash.png` in the runtime artifact expectations.
- Verify downstream `runtime_evidence.json` / `operator_result_contract.json` use the `_trash` name for disposable before screenshots.

**Verification Steps:**
- Run a fresh Remix v5 attempt so the workspace is copied from the updated template manifest.
- Confirm the seeded workspace manifest lists `v5_before_index_trash.png` under `runtime_generated_artifacts`.
- Confirm the generated operator output uses `v5_before_index_trash.png` in `runtime_evidence.json`, `operator_result_contract.json`, and any copied manifest output.
- Confirm preserved runtime files still use `_old` naming where appropriate, such as `index_old.html`.
- Confirm post-step cleanup still treats the before screenshot as disposable through the existing `*_trash.*` cleanup rule.

**Status:** Complete

---

## 💭 Notes & Decisions

### Design Decisions

**Decision:** Reserve `_old` for preserved legacy runtime files and `_trash` for disposable original/baseline screenshot captures.  
**Rationale:** This matches the v5 prompt contract and the runtime cleanup contract (`*_trash.*` removal) without overloading `_old` for two different lifecycle meanings.
