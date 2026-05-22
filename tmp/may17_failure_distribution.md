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
- Public and obfuscated tracked-failure sets match exactly: `True`
- Candidate pool exactly equals the union of the three tracked failure sets: `True`

**Exact Failure Distribution (public/obfuscated are identical):**
- `zero_only = 4` (0.8% of candidates, 0.26% of total catalog)
- `generic_only = 1` (0.2% of candidates, 0.06% of total catalog)
- `no_tags_only = 287` (57.06% of candidates, 18.43% of total catalog)
- `zero_generic_only = 0` (0.0% of candidates, 0.0% of total catalog)
- `zero_no_tags_only = 4` (0.8% of candidates, 0.26% of total catalog)
- `generic_no_tags_only = 6` (1.19% of candidates, 0.39% of total catalog)
- `all_three = 201` (39.96% of candidates, 12.91% of total catalog)

**Pairwise Overlap Totals:**
- `zero_and_generic = 201`
- `zero_and_no_tags = 205`
- `generic_and_no_tags = 207`
- `all_three = 201`

**Interpretation:**
- This distribution shows whether the broken pool is dominated by screenshot/title coupling, tag-only gaps, or mixed failures.
- Because public and obfuscated sets match exactly, we only need one remediation plan per failure bucket rather than separate catalog fixes.

**Artifacts Created:**
- `tmp/summarize_may17_failure_distribution.py`
- `tmp/may17_failure_distribution.json`
- `tmp/may17_failure_distribution.md`

**Status:** In Progress
