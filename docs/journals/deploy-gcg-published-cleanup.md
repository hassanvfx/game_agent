# deploy_gcg Published Cleanup Journal

**Last Updated:** 2026-05-22 05:06  
**Feature Spec:** `tools/game_publish_pipeline/scripts/deploy_gcg.py` published-only cleanup / deploy wrapper  
**Backend Reference:** existing publish-pipeline refresh, validation, and GCS sync scripts

---

## 📊 Implementation Status Overview

### ✅ Phase 1: Contract and reuse discovery - **COMPLETE**
- [x] Inspect current published-candidate audit logic
- [x] Inspect existing identical public-vs-obfuscated detector
- [x] Inspect refresh / validation / sync integration points

**Status:** ✅ Complete

### 🔧 Phase 2: Wrapper implementation - **IN PROGRESS**
- [x] Add published-only `deploy_gcg.py` orchestration wrapper
- [x] Fold identical public-vs-obfuscated findings into the candidate model
- [x] Add safe media sanitization for published public / obfuscated trees
- [x] Implement reusable cleanup helpers in `game_publish_pipeline/cleanup.py`

**Status:** ✅ Complete

### Phase 3: Cloud mirror + verification - **PLANNED**
- [x] Extend per-item GCS sync with remote prune behavior
- [x] Smoke-test audit-only and regeneration flow
- [x] Document results and operator usage

**Status:** ✅ Complete

---

## 📝 Journal Entries

### 2026-05-22 05:06 - Added repo-level publish and maintenance workflow document

**What Changed:**
- added `docs/game-publish-maintenance-workflow.md`
- captured a clearer operator-facing explanation of responsibility boundaries across:
  - `tools/game_refactoring`
  - `tools/game_generator`
  - `tools/game_publish_pipeline`
  - `tools/game_editorial`
- documented three practical flows:
  - experimental remix path
  - end-to-end generation path
  - publish / deployment path
- documented a maintenance recipe for post-publish repairs such as audio fixes
- explicitly recorded the corrected rule that final published-state validation belongs **after** root artifact materialization

**Why:**
The user wanted a more intentional, repo-ready explanation of how these tools fit together, with special emphasis on the difference between experimentation, generation, publishing, maintenance repair, and the post-materialization validation rule.

**Notes:**
- the document was written as an operator workflow reference rather than a low-level implementation spec
- terminology was aligned against current READMEs for `game_refactoring`, `game_generator`, `game_publish_pipeline`, and `game_editorial`

**Status:** Complete

---

### 2026-05-22 02:29 - Moved final-state validation into materialize_artifact_view.py

**What Changed:**
- wired final root validation into `tools/game_publish_pipeline/scripts/materialize_artifact_view.py` instead of `refresh_app_artifacts.py`
- refactored `tools/game_publish_pipeline/scripts/check_app_json_state.py` so its report generation can be imported and reused programmatically
- `materialize_artifact_view.py` now validates the final materialized root state against the generated root `app.json` after both public and obfuscated artifacts are written
- the materializer now reports validation status in its final JSON output and can optionally write the full checker report to disk
- added materializer CLI controls:
  - `--validate-final-state`
  - `--no-validate-final-state`
  - `--strict-final-state-validation`
  - `--validation-report-path`

**Why:**
This aligns the validation with the actual final root artifacts produced by materialization, which matches the corrected direction from the user and keeps refresh orchestration separate from final-state verification.

**Verification:**
- syntax-check passed for both updated scripts:
  - `python -m py_compile tools/game_publish_pipeline/scripts/check_app_json_state.py tools/game_publish_pipeline/scripts/materialize_artifact_view.py`
- added repo-local verification helpers to avoid long shell commands:
  - `tmp/smoke_materialize_final_state_validation.py`
  - `tmp/run_materialize_final_state_validation_real.py`
- tmp-only smoke confirmed the hook runs end-to-end from the materializer, but sanitized to zero records because the isolated tmp roots intentionally did not include published game folders
- real-environment validation passed via:
  - `python tmp/run_materialize_final_state_validation_real.py`
- real-environment validation summary:
  - `entry_count = 977`
  - `valid_public_count = 977`
  - `valid_obfuscated_count = 977`
  - `missing_public_folder_count = 0`
  - `missing_public_index_count = 0`
  - `missing_obfuscated_folder_count = 0`
  - `missing_obfuscated_index_count = 0`
  - `same_html_count = 0`
  - `failure_count = 0`
  - `cache_key = d9bb47e605249ebc32c728142288fff5:9122b83fb52d80fa7b8e0e8e82b738ce`
  - report written to `tmp/materialize_final_state_validation_real_report.json`

**Status:** Complete

---

### 2026-05-22 02:26 - Removed checker integration from refresh_app_artifacts.py

**What Changed:**
- removed the recently added materialized-state validation wiring from `tools/game_publish_pipeline/scripts/refresh_app_artifacts.py`
- removed the refresh-level checker constant, helper functions, CLI flags, summary output fields, and post-materialization validation call
- kept `refresh_app_artifacts.py` focused on:
  - building root public artifacts from a manifest
  - transforming/writing obfuscated root artifacts
  - writing run snapshots
  - invoking materialization
  - generating annotator dashboards

**Why:**
The user explicitly corrected the design direction: they do **not** want the checker living in `refresh_app_artifacts.py`. The desired validation target is the final root `app.json` created by the materialization step, so refresh-level checker behavior was removed to avoid mixing orchestration concerns.

**Verification:**
- confirmed the script still parses after removal with:
  - `pyenv exec python -m py_compile tools/game_publish_pipeline/scripts/refresh_app_artifacts.py`

**Status:** Complete

---

### 2026-05-22 02:13 - Added dual-mode app.json state checker with MD5 cache keys

**What Changed:**
- added `tools/game_publish_pipeline/scripts/check_app_json_state.py`
- the checker validates published runtime state directly from an `app.json` catalog and supports:
  - `--mode public`
  - `--mode obfuscated`
  - `--mode both`
- for each entry it verifies the expected folder and `index.html` exist for the selected side(s)
- for each existing public/obfuscated `index.html` it computes per-file MD5 checksums
- when both sides are checked it flags any entries whose public and obfuscated `index.html` files are byte-identical
- added stable cache-key material to the report:
  - `app_json_md5`
  - `public_state_md5`
  - `obfuscated_state_md5`
  - `combined_state_md5`
  - `cache_key = app_json_md5:combined_state_md5`

**Smoke Results:**
- command run:
  - `pyenv exec python tools/game_publish_pipeline/scripts/check_app_json_state.py --mode both --report-path tmp/check_app_json_state_report.json > tmp/check_app_json_state_stdout.json`
- summary from the generated report:
  - `entry_count = 977`
  - `valid_public_count = 977`
  - `valid_obfuscated_count = 977`
  - `missing_public_folder_count = 0`
  - `missing_public_index_count = 0`
  - `missing_obfuscated_folder_count = 0`
  - `missing_obfuscated_index_count = 0`
  - `same_html_count = 0`
  - `failure_count = 0`
  - `cache_key = d9bb47e605249ebc32c728142288fff5:9122b83fb52d80fa7b8e0e8e82b738ce`

**Why:**
The user wanted a tiny targeted verifier for `app.json` parity against real published folder state, plus lightweight checksum-based cache keys and explicit same-content detection between public and obfuscated HTML outputs.

**Operator Notes:**
- dual-mode validation:
  - `pyenv exec python tools/game_publish_pipeline/scripts/check_app_json_state.py --mode both`
- strict validation with non-zero exit on missing files or identical HTML pairs:
  - `pyenv exec python tools/game_publish_pipeline/scripts/check_app_json_state.py --mode both --strict`
- write a reusable JSON report:
  - `pyenv exec python tools/game_publish_pipeline/scripts/check_app_json_state.py --mode both --report-path tmp/check_app_json_state_report.json`

**Status:** Complete

---

### 2026-05-22 01:50 - Added verbose deploy wrapper progress output

**What Changed:**
- extended `tools/game_publish_pipeline/scripts/deploy_gcg.py` with a new `--verbose` flag
- added wrapper-side progress output for the previously quiet stages:
  - startup / root selection
  - catalog audit summary
  - identical public-vs-obfuscated detection summary
  - candidate mapping summary
  - delete target preview / apply target listing
  - sanitize root summaries and changed-file entries
  - runtime manifest build summary
  - refresh / validate / sync child command stage banners
- updated `tmp/smoke_deploy_gcg_wrapper.py` to exercise the wrapper with `--verbose`

**Smoke Results:**
- `pyenv exec python tools/game_publish_pipeline/scripts/deploy_gcg.py --dry-run --verbose` now prints readable stage banners before the JSON footer
- current post-cleanup dry-run state showed:
  - `public_candidates = 0`
  - `obfuscated_candidates = 0`
  - `public_delete_targets = 0`
  - `obfuscated_delete_targets = 0`
  - `runtime_manifest_entries = 977`
  - sanitize root scans for both roots with `changed = 0`

**Why:**
The user wants to run the full command in an external console and see obvious stage-by-stage progress instead of waiting on a mostly silent wrapper.

**Operator Notes:**
- full local flow with verbose wrapper output:
  - `pyenv exec python tools/game_publish_pipeline/scripts/deploy_gcg.py --confirm-delete --verbose`
- full local flow + GCS sync planning with verbose output:
  - `pyenv exec python tools/game_publish_pipeline/scripts/deploy_gcg.py --confirm-delete --sync-to-gcs --sync-gcs-dry-run --verbose`
- full local flow + real GCS sync with verbose output:
  - `pyenv exec python tools/game_publish_pipeline/scripts/deploy_gcg.py --confirm-delete --sync-to-gcs --verbose`

**Status:** Complete

---

### 2026-05-22 01:17 - Wrapper and GCS prune smokes passed

**What Changed:**
- completed the first implementation pass for:
  - `tools/game_publish_pipeline/game_publish_pipeline/cleanup.py`
  - `tools/game_publish_pipeline/scripts/deploy_gcg.py`
  - `tools/game_publish_pipeline/scripts/sync_to_gcs.py`
- added repo-local smoke scripts under `tmp/` instead of relying on long inline shell commands:
  - `tmp/smoke_deploy_gcg_cleanup_helpers.py`
  - `tmp/smoke_deploy_gcg_wrapper.py`
  - `tmp/smoke_sync_to_gcs_prune.py`
  - `tmp/smoke_sync_to_gcs_main_prune.py`

**Smoke Results:**
- cleanup helper smoke:
  - public candidate count: `215`
  - obfuscated candidate count: `215`
  - identical affected gamezones: `158`
  - mapped public delete targets: `368`
  - mapped obfuscated delete targets: `368`
  - sanitize changed files in dry-run analysis: `3`
- wrapper dry-run smoke:
  - status: `dry_run`
  - runtime manifest entries after planned cleanup: `1189`
  - explicit apply confirmation still required: `true`
- GCS prune smokes:
  - helper-level prune mapping correctly isolated stale remote `gamezone-beta`
  - main dry-run planning produced `2` sync operations plus `1` prune operation in the isolated smoke root

**Why:**
This proves the new cleanup + wrapper + prune path works in audit-first mode without mutating published roots or touching real remote state.

**Operator Notes:**
- audit / preview only:
  - `pyenv exec python tools/game_publish_pipeline/scripts/deploy_gcg.py --dry-run`
- apply cleanup + regenerate artifacts:
  - `pyenv exec python tools/game_publish_pipeline/scripts/deploy_gcg.py --confirm-delete`
- apply cleanup + regenerate + plan GCS sync:
  - `pyenv exec python tools/game_publish_pipeline/scripts/deploy_gcg.py --confirm-delete --sync-to-gcs --sync-gcs-dry-run`

**Status:** Complete

---

### 2026-05-22 00:54 - Milestone plan written and helper module started

**Milestone Plan:**
- **Milestone 1 — Cleanup helpers**
  - audit existing public / obfuscated `app.json`
  - collect candidate composite keys and identical affected gamezone ids
  - map cleanup candidates to concrete published directories
  - sanitize disallowed `.mp3` refs in runtime text files while preserving approved `https://*.vercel.app/*.mp3`
  - emit structured helper reports for the wrapper
- **Milestone 2 — `deploy_gcg.py`**
  - run the audit helpers
  - require explicit delete confirmation before any removal
  - delete published-only targets
  - rebuild the runtime manifest from remaining public dirs
  - run refresh + validation
- **Milestone 3 — `sync_to_gcs.py`**
  - keep per-item sync
  - add remote prune / mirror behavior for stale gamezone prefixes
- **Milestone 4 — Verification**
  - dry-run the wrapper
  - dry-run sync prune
  - document the operator flow and results

**Implementation Notes:**
- started a reusable helper module at `tools/game_publish_pipeline/game_publish_pipeline/cleanup.py`
- helper scope is intentionally package-level so the future wrapper can reuse the same audit, mapping, identical-detection, and sanitization logic without copying script-only code
- sanitization is constrained to gamezone runtime text files and skips artifact folders plus root catalog artifacts

**Why:**
The wrapper needs a small reusable foundation first; otherwise the orchestration script would become a large pile of one-off inline logic.

**Next Steps:**
- [ ] Finish the helper module and verify it imports cleanly
- [ ] Wire the helper module into a published-only `deploy_gcg.py`
- [ ] Extend `sync_to_gcs.py` with prune support after the wrapper is in place

**Status:** In Progress

---

### 2026-05-21 23:44 - Scope and implementation plan locked

**What Changed:**
- established the implementation plan for a new published-only wrapper at `tools/game_publish_pipeline/scripts/deploy_gcg.py`
- confirmed reuse boundaries across:
  - `tmp/audit_published_catalog_regressions.py`
  - `tools/game_publish_pipeline/scripts/detect_identical_public_obfuscated.py`
  - `tools/game_publish_pipeline/scripts/refresh_app_artifacts.py`
  - `tools/game_publish_pipeline/scripts/validate_published_outputs.py`
  - `tools/game_publish_pipeline/scripts/sync_to_gcs.py`
- added a new requirement from the user: identical public-vs-obfuscated published outputs should also count as cleanup candidates

**Why:**
The wrapper needs to stay safe by default while reusing the existing publish-pipeline contract. Locking the scope first avoids building a second competing artifact flow.

**Planned Deliverables:**
- `tools/game_publish_pipeline/scripts/deploy_gcg.py`
- stricter media sanitization for `.html`, `.js`, `.css`, and `.json`
- per-item GCS mirror support with explicit remote prefix pruning

**Next Steps:**
- [ ] Implement the wrapper audit report and candidate merge logic
- [ ] Extend the sync helper with true per-item mirror behavior
- [ ] Run smoke checks and document operator usage

**Status:** In Progress

---

## 🎯 Success Criteria

- [x] Audit-first flow is safe by default
- [x] Candidate list includes missing screenshots, generic titles, no tags, and identical public-vs-obfuscated outputs
- [x] Confirmed deletions target actual published directories
- [ ] Public and obfuscated root catalogs regenerate cleanly after cleanup
- [x] Per-item GCS sync can prune stale remote gamezone prefixes
