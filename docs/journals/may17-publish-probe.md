# May 17 Publish Probe Journal

**Last Updated:** 2026-05-21  
**Feature Spec:** N/A  
**Scope:** Smoke-test `game_publish_pipeline` against May 17 HDD run outputs to prove whether identity metadata and top-level PNG screenshots are packaged correctly, and whether `__pXX` pollutes `game_id`.

---

## 📊 Implementation Status Overview

### ✅ Phase 1: Investigation Setup - **COMPLETE**

- [x] Trace `game_publish_pipeline` → `game_deploy` coordination
- [x] Inspect May 17 HDD folder shape
- [x] Confirm a broken published sample was deployed from `games/raw/...`, not directly from the HDD run folders

**Status:** ✅ Complete

### ✅ Phase 2: Smoke Publish Proof - **COMPLETE**

- [x] Create isolated probe plan targeting `/Volumes/HDD2026/output-May17th/output`
- [x] Run a 1–2 item smoke publish into isolated test roots
- [x] Inspect deployed metadata and screenshot outputs
- [x] Verify whether published `game_id` includes `__pXX`

**Status:** ✅ Complete

### 🔧 Phase 3: Recovery Recommendation - **IN PROGRESS**

- [x] Summarize proof and recommend a safe fix/recovery path

**Status:** 🔧 In Progress

---

## 📝 Journal Entries

### 2026-05-21 19:04 - Initial smoke-publish probe setup

**What Changed:**
- Created a dedicated journal for the May 17 HDD smoke-publish proof run.
- Confirmed the current investigation hypothesis:
  - May 17 `__pXX` folders appear to contain valid `Identity.json` and top-level PNG screenshots.
  - The currently broken published sample was deployed from a normalized `games/raw/...` folder that no longer had screenshots.

**Why:**
We need a controlled proof that the publisher/deployer can ingest the May 17 source folders directly enough to preserve identity + screenshots, while also observing whether the suffix `__pXX` incorrectly becomes part of the canonical published `game_id`.

**Next Steps:**
- [ ] Run an isolated smoke publish into HDD test roots
- [ ] Inspect output metadata and packaged screenshots
- [ ] Capture proof of `game_id` behavior with `__pXX`

**Status:** In Progress

---

### 2026-05-21 19:06 - Smoke publish proof succeeded against May 17 HDD folders

**Achievement:**
- Ran an isolated `game_publish_pipeline` smoke publish using two real May 17 source folders:
  - `gamezone-0022d901-ea58-4a11-b909-fff27f0ee38f__p01`
  - `gamezone-0022d901-ea58-4a11-b909-fff27f0ee38f__p02`
- Published into an isolated HDD probe root:
  - `/Volumes/HDD2026/output-May17th/output/publish_probe_20260522T010620Z`

**What the probe proved:**
- `Identity.json` was successfully ingested.
  - Example extracted titles:
    - `Miso Comet Supper Rush`
    - `Dead Orbit Velocity Duel`
- Top-level PNG screenshots were successfully packaged.
  - Each deploy produced:
    - `screenshots/01.jpg`
    - `screenshots/02.jpg`
    - `screenshots/03.jpg`
- `deploy.normalized_screenshot_sources` was populated from the May 17 top-level PNGs.
  - Example source files:
    - `v5_after_entry.png`
    - `v5_after_merge.png`
    - `v5_after_spawn.png`
- Final `public/app.json` entries had `screenshots_count = 3` for both test items.

**Critical finding:**
- The pipeline also proved the risk we expected: `game_id` was polluted by the prompt-slot suffix.
- The deploy step published under:
  - `gamezone-0022d901-ea58-4a11-b909-fff27f0ee38f__p01`
  - `gamezone-0022d901-ea58-4a11-b909-fff27f0ee38f__p02`
- So the May 17 folders are **good enough for screenshots + identity**, but **unsafe for direct production publishing** without normalizing the canonical `game_id`.

**Implementation Details:**
- Added `tmp/run_may17_publish_probe.py` to run the proof publish into isolated HDD roots.
- Used a real pipeline invocation rather than a mocked deploy step.
- Captured deploy dir summaries including metadata, screenshot outputs, and proof flags.

**Recommended fix path:**
1. Normalize May 17 source folders before production publishing so:
   - canonical `game_id = gamezone-...`
   - variant marker `__pXX` is preserved only as provenance/metadata, not the published id.
2. Preserve/copy the top-level PNG screenshots from May 17 sources into the normalized publish source.
3. Optionally add a guardrail that fails publish when the inferred `game_id` contains `__p`.

**Status:** In Progress

---

### 2026-05-21 19:18 - Direct local-root overwrite run confirmed overwrite is not cleanup

**Achievement:**
- Ran the same two May 17 `__pXX` source folders directly into the default local publish roots using `--overwrite`.
- Captured the result in `tmp/may17_local_publish_overwrite_report.json`.

**What Changed:**
- New local published outputs were created under:
  - `games/published/public/gamezone-0022d901-ea58-4a11-b909-fff27f0ee38f__p01/remix-7b24222a0ad8a4ca6bc3b88a1c58270c`
  - `games/published/public/gamezone-0022d901-ea58-4a11-b909-fff27f0ee38f__p02/remix-48aac9609a5c0d031f6a7f9a9a734e69`
- The new local outputs correctly packaged screenshots and extracted titles.

**Key Result:**
- `--overwrite` **did not delete or replace older outlier remixes** for the same `__pXX` ids when the remix hash changed.
- Before the run there were already older outlier records like:
  - `...__p01__remix-35fdd97c5241e93c06cdd937d243ff7d`
  - `...__p02__remix-7e28c6de22878eae340adaa5c395a886`
- After the run, the root catalogs contained **both** the older broken outliers and the newly published outliers.

**Why This Happened:**
- `game_deploy --overwrite` only removes an existing destination when the destination path is the same.
- Because the new May 17 publish produced new remix hashes, the output paths were different, so the old outlier remix dirs remained on disk.
- `refresh_app_artifacts.py` then called `materialize_artifact_view.py`, which merged run snapshots from the historical `games/published/runs` store and kept all still-resolvable outlier records alive in the root catalogs.

**Conclusion:**
- A direct local-root rerun with `--overwrite` is **not enough** to clean old broken outliers.
- If we want cleanup, we must explicitly delete the outlier dirs (and then rematerialize catalogs), or publish from normalized canonical ids instead.

**Status:** In Progress

---

### 2026-05-21 20:38 - Full 195-item May 17 overwrite regression run completed

**Achievement:**
- Built a dedicated repo-wide regression audit workflow for published catalogs.
- Ran the full May 17 batch from the HDD source root using `--overwrite` into the default local publish roots.
- Completed before/after audits and diffed the exact new bad records.

**Artifacts Created:**
- `tmp/audit_published_catalog_regressions.py`
- `tmp/build_may17_full_publish_manifest.py`
- `tmp/run_may17_full_regression.py`
- `tmp/compare_may17_regression_candidates.py`
- `tmp/may17_regression_baseline_audit.json`
- `tmp/may17_regression_after_audit.json`
- `tmp/may17_full_regression_delta.json`
- `tmp/may17_full_publish_report.json`

**Baseline Counts:**
- `public_total_entries = 1364`
- `obfuscated_total_entries = 1364`
- `public_zero_screenshots_count = 208`
- `public_generic_titles_count = 208`
- `public_no_tags_count = 496`
- `public_candidate_for_removal_count = 500`
- Obfuscated counts matched public exactly.

**After Full Overwrite Counts:**
- `public_total_entries = 1557`
- `obfuscated_total_entries = 1557`
- `public_zero_screenshots_count = 209`
- `public_generic_titles_count = 208`
- `public_no_tags_count = 498`
- `public_candidate_for_removal_count = 503`
- Obfuscated counts again matched public exactly.

**Net Delta:**
- `+193` total published entries in each catalog
- `+1` zero-screenshot record
- `+0` generic-title records
- `+2` no-tag records
- `+3` candidate-for-removal records

**Exact New Candidate Records Introduced:**
1. `gamezone-129300d1-1426-447f-a724-110b81a97251__p02__remix-ab9127a45bf6e2cd8b3a61c8f81256d4`
   - new zero-screenshot candidate
2. `gamezone-00949d28-6fa6-4cc3-8b31-ff3d5791265b__p01__remix-03c18ba73e35f64fcb4051ccf61ef915`
   - new no-tags candidate
3. `gamezone-13a9a732-aa95-4ab1-afb6-1bfac2c50239__p01__remix-4202ac63c7e554ffcc42d6f7608442f7`
   - new no-tags candidate

**Interpretation:**
- The rerun was **not neutral** under the strict regression metric.
- It did **not** increase generic `gamezone-...` title failures.
- But it **did** add three new removal candidates:
  - one missing screenshots
  - two missing all tracked tag families
- So the expectation that the rerun would “not add more broken records” was **not fully met**.

**Additional Note:**
- The full overwrite publish initially failed due to disk exhaustion, but after freeing space it succeeded end-to-end with the same regression scripts.

**Status:** In Progress

---

### 2026-05-21 20:49 - Sampled the 3 new bad records against source artifacts

**Goal:**
Determine whether the 3 newly introduced bad records were caused by deploy-time corruption or by missing/mismatched source artifacts.

**Findings:**

#### 1) `gamezone-129300d1-1426-447f-a724-110b81a97251__p02__remix-ab9127a45bf6e2cd8b3a61c8f81256d4`
- This is the **new zero-screenshot** record.
- The published metadata already shows:
  - `screenshots_jpg = []`
  - `deploy.normalized_screenshot_sources = []`
- The May 17 source folder itself is missing the expected top-level screenshot PNGs.
  - No `v5_after_entry.png`
  - No `v5_after_merge.png`
  - No `v5_after_spawn.png`
- Its `runtime_evidence.json` explains why:
  - `status = blocked`
  - `blocked_reason = Assigned validation port ... already occupied`
  - `browser_screenshots = not captured due port conflict`
  - `screenshots = []`
- The sibling source folder `...__p01` **does** contain the expected `v5_after_*` PNGs.

**Root Cause:**
- This is a **source-side screenshot absence**, not a deploy packaging bug.
- The source run never captured screenshots for this `__p02` item because runtime validation was blocked by a port conflict.

#### 2) `gamezone-00949d28-6fa6-4cc3-8b31-ff3d5791265b__p01__remix-03c18ba73e35f64fcb4051ccf61ef915`
#### 3) `gamezone-13a9a732-aa95-4ab1-afb6-1bfac2c50239__p01__remix-4202ac63c7e554ffcc42d6f7608442f7`
- These are the **2 new no-tags** records.
- Their published metadata json files are not empty; they contain meaningful metadata.
- Both source folders contain the expected screenshot PNGs, and deploy packaged them successfully.
- The problem is the **schema shape** of the tag metadata:
  - `semantic_tags.json` uses top-level fields like:
    - `tags`
    - `preserve` / `transform`
    - or `preserve_tags` / `transform_tags`
  - `mechanics_classification` uses `ranked_mechanics`
- But `scripts/generate_published_app_metadata.py` derives app catalog tag families from different expected shapes:
  - `semantic_tags.theme`
  - `semantic_tags.mood`
  - `semantic_tags.setting`
  - `semantic_tags.characters`
  - `semantic_tags.similar_games`
  - `semantic_tags.similar_franchises`
  - and mechanic tags from:
    - `mechanics_classification.selected_top_5`
    - `selected_top_5_categories`
    - `mechanic_tags`
    - or `semantic_tags.mechanics`

**Root Cause:**
- These 2 regressions are caused by an **app catalog extraction schema mismatch**, not by missing source metadata.
- Useful tag information exists in the source/published metadata, but the app metadata generator does not currently map these legacy/split-json shapes into the tracked app tag families.

**Recovery Implications:**
- The zero-screenshot record likely needs regenerated or recovered screenshots from source/runtime evidence; deploy alone cannot invent them.
- The 2 no-tags records are likely recoverable by expanding `scripts/generate_published_app_metadata.py` to support legacy tag layouts such as:
  - `semantic_tags.tags`
  - `mechanics_classification.ranked_mechanics[].name`

**Status:** In Progress

---

### 2026-05-21 21:10 - Computed the general failure distribution across the full candidate pool

**Goal:**
Break down the full published-catalog failure pool into overlap buckets so we can tell whether the dominant issue is screenshots, generic titles, missing tags, or combinations of those signals.

**High-Level Counts (public catalog):**
- `total_entries = 1557`
- `candidate_for_removal_count = 503`
- `zero_screenshots_count = 209`
- `generic_titles_count = 208`
- `no_tags_count = 498`

**Set Consistency:**
- Public and obfuscated tracked-failure sets match exactly.
- The candidate pool is exactly the union of the three tracked failure sets.

**Exact Failure Distribution (public/obfuscated are identical):**
- `zero_only = 4` (0.8% of candidates, 0.26% of total catalog)
- `generic_only = 1` (0.2% of candidates, 0.06% of total catalog)
- `no_tags_only = 287` (57.06% of candidates, 18.43% of total catalog)
- `zero_generic_only = 0`
- `zero_no_tags_only = 4` (0.8% of candidates, 0.26% of total catalog)
- `generic_no_tags_only = 6` (1.19% of candidates, 0.39% of total catalog)
- `all_three = 201` (39.96% of candidates, 12.91% of total catalog)

**Pairwise Overlap Totals:**
- `zero_and_generic = 201`
- `zero_and_no_tags = 205`
- `generic_and_no_tags = 207`
- `all_three = 201`

**Interpretation:**
- The pool is overwhelmingly tag-driven: `498 / 503` candidates have no tracked tags at all.
- The largest single bucket is `no_tags_only = 287`, so more than half of the current bad pool is metadata/tag-only failure rather than screenshot failure.
- The second-largest bucket is `all_three = 201`, which means the screenshot and generic-title signals are usually coupled with missing tags, not isolated on their own.
- Truly isolated screenshot/title failures are rare: only `4` screenshot-only records and `1` generic-title-only record remain.
- Because public and obfuscated sets match exactly, one remediation strategy should fix both catalogs.

**Artifacts Created:**
- `tmp/summarize_may17_failure_distribution.py`
- `tmp/may17_failure_distribution.json`
- `tmp/may17_failure_distribution.md`

**Status:** In Progress

---

### 2026-05-21 22:59 - Restricted public tag recovery to structured file data only

**Goal:**
Re-run the public metadata recovery using only structured data that actually exists on disk, with no prompt-derived tag inference and no hidden `._*` sidecar garbage.

**What Changed:**
- Removed prompt-based mechanic/tag recovery from `scripts/generate_published_app_metadata.py`.
- Kept tag extraction grounded in structured metadata fields only, specifically:
  - `semantic_tags.*` legacy buckets already present in published metadata json files
  - `semantic_tags.tags` / `preserve_tags` / `transform_tags`
  - `mechanics_classification.selected_*`
  - `mechanics_classification.ranked_mechanics[*].tag|name|title|category`
- Updated file enumeration to ignore hidden macOS sidecar junk:
  - any file whose basename starts with `._`

**Structured-source inspection result:**
- For sampled residual no-tag records, `deploy.source_output_dir` mostly resolved back to the same published game folders rather than to richer raw/source artifact directories.
- The sampled source folders generally only contained sibling `game-obfuscated-*.json` files with the same high-level schema keys:
  - `semantic_tags`
  - `identity`
  - `mechanics_classification`
- For many residual records those structured sections were simply empty (`{}`), so there was no additional accurate tag data to recover from disk.

**Validation Result (public catalog only):**
- Baseline before structured-only tag recovery:
  - `generic_titles_count = 9`
  - `no_tags_count = 263`
  - `candidate_for_removal_count = 271`
- After structured-only recovery:
  - `generic_titles_count = 9`
  - `no_tags_count = 207`
  - `candidate_for_removal_count = 215`
- Net improvement from structured-only tag recovery:
  - `no_tags_recovered = 56`
  - `no_tags_recovered_pct = 21.29%`

**Interpretation:**
- The earlier lower `no_tags_count = 163` depended on prompt-derived guessing and is no longer considered trustworthy for this task.
- The accurate recovery ceiling from real structured file data appears to be the structured-only result above.
- Remaining residual no-tag records mostly do not have enough non-empty structured metadata on disk to support a truthful recovery.

**Artifacts Used:**
- `tmp/inspect_structured_public_source_recovery.py`
- `tmp/validate_public_tag_recovery.py`
- `tmp/generated_metadata_public_tag_recovery_latest/app.json`
- `tmp/generated_metadata_public_tag_recovery_latest/audit.json`

**Status:** In Progress

---

### 2026-05-21 23:08 - Promoted structured-only catalogs into real public and obfuscated roots

**Goal:**
Replace the real root published catalogs with the strict structured-only regenerated result, and keep obfuscated in parity with the same transformed catalog view.

**What Changed:**
- Promoted the structured-only regenerated catalogs into the real roots:
  - `games/published/public/index.json`
  - `games/published/public/app_tags.json`
  - `games/published/public/app.json`
- Regenerated matching obfuscated root catalogs from the promoted public payload using the same public→obfuscated transform used by the publish pipeline:
  - `games/published/obfuscated/index.json`
  - `games/published/obfuscated/app_tags.json`
  - `games/published/obfuscated/app.json`
- Backed up the previous real root catalogs before writing:
  - `tmp/catalog_promotions/promotion_20260522T050850Z/public/`
  - `tmp/catalog_promotions/promotion_20260522T050850Z/obfuscated/`

**Verification:**
- Post-promotion real-catalog audit:
  - `tmp/catalog_promotions/promotion_20260522T050850Z/real_catalog_audit.json`
- Verified final root counts are identical between public and obfuscated:
  - `public_no_tags_count = 207`
  - `public_generic_titles_count = 9`
  - `public_candidate_for_removal_count = 215`
  - `obfuscated_no_tags_count = 207`
  - `obfuscated_generic_titles_count = 9`
  - `obfuscated_candidate_for_removal_count = 215`

**Interpretation:**
- The real root catalogs now reflect the strict structured-only recovery pass.
- Public and obfuscated remain in parity after promotion.
- This is the trustworthy ceiling from actual structured file data currently present on disk.

**Artifacts Created:**
- `tmp/promote_structured_only_catalogs.py`
- `tmp/catalog_promotions/promotion_20260522T050850Z/real_catalog_audit.json`

**Status:** Complete

---

## 💭 Notes & Decisions

### Working Hypothesis

- `game_deploy.deployer.normalize_screenshot_candidates()` should package top-level PNGs from the May 17 folders.
- `game_deploy.metadata_extractor` should read `Identity.json` successfully.
- `infer_game_id()` is likely to treat `gamezone-...__p01` as the canonical `game_id`, which is probably undesirable for production publishing.
