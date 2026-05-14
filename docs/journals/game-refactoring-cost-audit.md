# Game Refactoring Cost Audit Journal

**Last Updated:** 2026-05-13  
**Feature Spec:** Track per-run Cline token/cost usage inside `tools/game_refactoring`

---

## 📊 Implementation Status Overview

### ✅ Phase 1: Discovery and rollback safety - **COMPLETE**

- [x] Locate the `game_refactoring` runtime boundaries
- [x] Identify the shared worker execution layer
- [x] Create a pre-change rollback tag

**Status:** ✅ Complete

### Phase 2: Usage capture proof - **IN PROGRESS**

- [ ] Add shared NDJSON usage extraction from Cline `run_result`
- [ ] Persist a per-invocation usage artifact for the smallest proof path
- [ ] Verify the proof path keeps existing behavior stable when usage is missing

**Status:** 🔧 In Progress

### Phase 3: Aggregation rollout - **PLANNED**

- [ ] Expand usage artifact writing to broader game_refactoring worker paths
- [ ] Produce a run-level `cost_report.json` summary
- [ ] Validate the aggregated report shape on a small real run

**Status:** Planned

---

## 📝 Journal Entries

### 2026-05-13 19:41 - Initial planning and rollback checkpoint

**What Changed:**
- Identified `tools/game_refactoring/scripts/creative_refactor_runtime.py` as the shared subprocess execution boundary.
- Confirmed worker entrypoints in `spec_adaptor.py`, `run_operator_pipeline_game.py`, `creative_refactor_cli.py`, and related scripts.
- Created a rollback tag before implementation work.

**Why:**
The safest implementation is to instrument the centralized worker execution/result path instead of changing every stage independently.

**Files Created:**
- `docs/journals/game-refactoring-cost-audit.md` - Task journal for usage/cost instrumentation work

**Technical Decisions:**
- Start with a minimal proof path rather than full pipeline rollout.
- Prefer parsing the final `run_result` NDJSON event and normalizing `aggregateUsage` first, with fallback to `usage`.
- Keep missing usage non-fatal so existing runs remain stable.

**Rollback Reference:**
- Git tag: `pre-cost-audit-20260513-194147`

**Next Steps:**
- [ ] Inspect the active Cline command builders for JSON/verbose support
- [ ] Add shared usage parsing helpers in the runtime layer
- [ ] Write a first per-invocation usage artifact for the proof path

**Status:** In Progress

---

### 2026-05-13 20:07 - Runtime parsing and aggregation rollout

**Achievement:**
Added shared Cline `run_result` usage parsing, persisted proof-path usage artifacts, and extended operator-pipeline reporting toward per-game and run-level cost summaries.

**Implementation Details:**
- Modified `tools/game_refactoring/scripts/creative_refactor_runtime.py` to parse NDJSON stdout, capture the final `run_result`, and normalize usage metadata onto `WorkerExecutionResult`.
- Modified `tools/game_refactoring/scripts/spec_adaptor.py` to invoke Cline with `--json -v`, write `recomposition_usage.json`, and include usage metadata in `adaptation_report.json`.
- Modified `tools/game_refactoring/scripts/run_operator_pipeline_game.py` to invoke operator workers with `--json -v`, write `operator_usage.json` per attempt, and emit per-game `operator_pipeline/cost_report.json`.
- Modified `tools/game_refactoring/scripts/run_operator_pipeline_batch.py` to emit a run-scope `runs/<run_id>/cost_report.json` from per-game reports.

**Technical Decisions:**
- Missing usage remains non-fatal and is encoded as `usage_unavailable` instead of failing the run.
- The normalized usage shape prefers `aggregateUsage` and falls back to `usage`.
- Cost aggregation is layered: invocation -> game -> run.

**Next Steps:**
- [ ] Re-run syntax validation after the latest batch-runner patch
- [ ] Perform a small dry-run/live validation to confirm report paths and JSON shape
- [ ] Update the journal with final verification notes

**Status:** In Progress

---

### 2026-05-13 20:14 - Live probe confirmed usage capture

**Achievement:**
Confirmed the new usage capture with a real Cline-backed `spec_adaptor` debug run.

**Live Validation Path:**
- Command used:

```bash
python3 tools/game_refactoring/scripts/debug_spec_adaptor.py \
  --case-name cost_audit_live_probe \
  --style neutral_prototype \
  --remix-prompt "Reply with a minimal coherent prototype-friendly remix direction for a calm neon puzzle game." \
  --prompt-targets creative_refactor_agent_template \
  --model gpt-5.4 \
  --agent-timeout 180 \
  --clean
```

**Observed Artifacts:**
- `tools/game_refactoring/fixtures/spec_adaptor_debug/cost_audit_live_probe/spec_adaptor/recomposition_usage.json`
- `tools/game_refactoring/fixtures/spec_adaptor_debug/cost_audit_live_probe/spec_adaptor/adaptation_report.json`
- `tools/game_refactoring/fixtures/spec_adaptor_debug/cost_audit_live_probe/spec_adaptor/recomposition_stdout_attempt_01.txt`

**Captured Usage Example:**
```json
{
  "source_event_type": "run_result",
  "finishReason": "completed",
  "iterations": 5,
  "durationMs": 96617,
  "provider": "litellm",
  "model": "gpt-5.4",
  "usage": {
    "inputTokens": 98655,
    "outputTokens": 8829,
    "cacheReadTokens": 68096,
    "cacheWriteTokens": 0,
    "totalCost": 0
  }
}
```

**Notes:**
- The proof path successfully recorded `run_result` usage into both the standalone usage artifact and the higher-level adaptation report.
- The stdout log clearly contains structured JSON events, including intermediate `usage` events and the final `run_result` used by the parser.
- `totalCost` remained `0`, which matches the earlier expectation for this provider/model path when pricing metadata is unavailable.

**Next Steps:**
- [ ] Run a small operator-pipeline game example to confirm `operator_usage.json` and per-game `cost_report.json`
- [ ] Run a tiny batch example to confirm run-scope `runs/<run_id>/cost_report.json`
- [ ] Finalize docs if the broader validations are desired

**Status:** In Progress

---

### 2026-05-13 21:40 - Projected cost layer requested

**Achievement:**
Started extending the reporting layer so token usage can also produce projected USD estimates when provider-reported `totalCost` remains zero.

**Pricing Basis Added:**
```text
Input:        $5.00 / 1M tokens
Cached input: $0.50 / 1M tokens
Output:      $30.00 / 1M tokens
```

**Implementation Direction:**
- Keep provider-reported `totalCost` unchanged.
- Add derived token totals.
- Add projected cost breakdown and projected total in usage summaries.
- Roll projected totals upward into per-game and run-scope reports.

**Status:** In Progress

---

### 2026-05-13 21:46 - Projected cost validated on live probe

**Achievement:**
Validated projected USD cost fields against a regenerated live `spec_adaptor` probe.

**Observed Usage Totals:**
- `inputTokens`: `111809`
- `outputTokens`: `13853`
- `cacheReadTokens`: `49920`
- `cacheWriteTokens`: `0`
- `totalTokens`: `125662`
- `totalTokensIncludingCache`: `175582`

**Projected Cost Breakdown:**
- input: `$0.559045`
- cached input: `$0.024960`
- output: `$0.415590`
- cache write: `$0.000000`
- projected total: `$0.999595`

**Artifact Confirmation:**
- `recomposition_usage.json` now includes:
  - `tokenTotals`
  - `projectedCost.currency`
  - `projectedCost.pricingBasis`
  - `projectedCost.breakdown`
  - `projectedCost.total`
- `adaptation_report.json` also embeds the enriched `usage_summary`

**Notes:**
- Provider-reported `totalCost` remains `0`, but projected pricing is now available alongside raw token accounting.
- The live probe path remains suitable for future spot-checks when pricing assumptions change.

**Status:** In Progress

---

## 🎯 Success Criteria

- [ ] Per-invocation usage artifacts capture token/cost metadata when Cline emits `run_result`
- [ ] Missing usage metadata does not fail the run
- [ ] A run-level cost report can summarize all captured worker invocations
- [ ] Documentation/journal is updated alongside code changes
