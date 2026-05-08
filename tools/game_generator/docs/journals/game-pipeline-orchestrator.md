# Game Pipeline Orchestrator Implementation Journal

**Last Updated:** 2026-04-26 19:12  
**Feature Spec:** N/A  
**Backend Reference:** N/A

---

## 📊 Implementation Status Overview

### ✅ Phase 1: Discovery and Architecture - **COMPLETE**

- [x] Inspect sibling projects and identify integration points
- [x] Confirm remixer lookup CLI contract via `get_game`
- [x] Define strict fail-hard orchestration behavior

**Status:** ✅ Complete

### Phase 2: File-Backed Orchestrator and Run Model - **IN PROGRESS**

- [ ] Create run directory and persisted run-state model
- [ ] Implement matcher/remixer/remix-editor/obfuscator orchestration
- [ ] Persist raw artifacts, commands, poll history, and final outputs
- [ ] Align remix editor and obfuscator integrations to updated upstream CLI contracts
- [ ] Add multi-attempt async stage watchdogs with escalating retry windows

**Status:** 🔧 In Progress

### Phase 3: Observer CLI and HTML Dashboard - **PLANNED**

- [ ] Implement observer CLI terminal rendering and JSON mode
- [ ] Implement auto-updating HTML dashboard backed by run files
- [ ] Add lightweight local dashboard server and validate flow

**Status:** Planned

---

## 📝 Journal Entries

### 2026-04-26 19:12 - Initial Setup

**What Changed:**
- Created journal structure for the game pipeline orchestrator feature
- Recorded the agreed orchestration model and observability requirements
- Outlined implementation phases for orchestrator, observer, and dashboard work

**Why:**
This task spans multiple phases, integrates several sibling repositories, and requires architectural decisions around strict failure handling and observability. A dedicated journal is required to preserve implementation context and decisions.

**Files Created:**
- `docs/journals/game-pipeline-orchestrator.md` - Tracks architecture, decisions, progress, and verification for the orchestrator feature

**Next Steps:**
- [ ] Inspect current repository structure for new CLI/module placement
- [ ] Implement the file-backed run model and orchestrator skeleton
- [ ] Add observer and dashboard support around the persisted run state

**Status:** In Progress

---

## 🐛 Known Issues

### Upstream CLI contract drift

**Problem:** 
The orchestrator journal documented older remix editor and obfuscator command/result expectations, while the sibling repositories now expose richer payloads and an obfuscator `output-path` contract instead of a remix-style result shape.

**Root Cause:** 
The orchestrator integration notes and implementation were created before the latest upstream CLI contract updates landed.

**Status:** 
- [ ] Being investigated
- [ ] Blocked (waiting for...)
- [x] Fixed

**Workaround:** 
Use the sibling repo CLI implementations as the source of truth when validating integration behavior.

**Resolution:** 
Updated the orchestrator plan and implementation to align with the current remix editor `start-batch/status/result` payloads and the obfuscator `start/status/output-path` contract. Additional orchestration issues were later identified around long-running async stage retries, cancellation, and stale status polling that can miss a completed upstream remix-editor run without a reconciliation pass.

---

## 🔧 Backend API Reference

### External CLI Contracts

**Matcher:**
- `../game_matcher/cli/game_matcher_cli.py`
- Expected to accept a prompt and return ranked JSON results including usable `game_id` values

**Remixer Lookup:**
```bash
cd /Volumes/Elements/game_remixer
./get_game GAMEID
```

Returns:
- absolute `index.html` path on success
- exit `1` on not found / missing export root
- exit `2` on invalid usage

**Remix Editor:**
```bash
python3 /Volumes/Elements/game_remix_editor/scripts/creative_refactor_cli.py --json start-batch --manifest <manifest> --remix-prompt "<prompt>" --poll-seconds <seconds>
python3 /Volumes/Elements/game_remix_editor/scripts/creative_refactor_cli.py --json status --run-id <run_id>
python3 /Volumes/Elements/game_remix_editor/scripts/creative_refactor_cli.py --json result --run-id <run_id>
```

Start payload includes at least:
- `run_id`
- `run_dir`
- `status_path`
- `dashboard_path`
- `output_root`
- `status`
- `current_phase`

Status/result payloads include canonical run metadata and expose `final_output_dirs` only once the run is terminal.

**Obfuscator:**
```bash
python3 /Volumes/Elements/game_obfuscator/scripts/game_obfuscator_cli.py start --manifest <manifest>
python3 /Volumes/Elements/game_obfuscator/scripts/game_obfuscator_cli.py status --run-id <run_id>
python3 /Volumes/Elements/game_obfuscator/scripts/game_obfuscator_cli.py output-path --run-id <run_id> --include-games
```

Start payload includes at least:
- `run_id`
- `run_dir`
- `status_path`
- `dashboard_path`
- `output_root`
- `status`
- `current_phase`

Status payload includes:
- `run_id`
- `run_dir`
- `status`
- `current_phase`
- `dashboard_path`
- `output_root`
- `completed`

Output payload includes:
- `run_id`
- `run_dir`
- `status`
- `current_phase`
- `output_path`
- `completed`

Optional:
- `game_outputs` when `--include-games` is passed

---

## 📚 Quick Reference

### Key Files

- `docs/journals/game-pipeline-orchestrator.md` - Feature journal
- `clineflow/PROCEDURES.md` - Workflow and journaling rules
- `clineflow/JOURNAL_TEMPLATE.md` - Journal template reference

### Planned New Files

- `scripts/run_pipeline.py` - Main orchestrator CLI
- `scripts/observe_pipeline_run.py` - Terminal/JSON observer CLI
- `scripts/serve_pipeline_dashboard.py` - Lightweight HTTP server for dashboard viewing
- `pipeline_runs/<run_id>/...` - Persisted run artifacts, state, and dashboard data

### Important Commands

```bash
# Planned orchestrator usage
python3 scripts/run_pipeline.py "a harry potter flappy bird game" --obfuscate

# Planned observer usage
python3 scripts/observe_pipeline_run.py --run-dir pipeline_runs/<run_id>
python3 scripts/observe_pipeline_run.py --run-dir pipeline_runs/<run_id> --json
python3 scripts/observe_pipeline_run.py --run-dir pipeline_runs/<run_id> --watch

# Planned dashboard serving
python3 scripts/serve_pipeline_dashboard.py --run-dir pipeline_runs/<run_id>
```

---

## 💭 Notes & Decisions

### Design Decisions

**Decision:** Use a file-backed run directory as the single source of truth.  
**Rationale:** This enables strict observability, post-failure inspection, simple dashboard rendering, and clear artifact retention without requiring a live backend service.  
**Alternatives Considered:** Direct console-only orchestration was rejected because it does not provide durable state or a strong basis for an observer/dashboard.

**Decision:** Use strict fail-hard behavior for matcher and `get_game`.  
**Rationale:** The user explicitly expects 500-class failure semantics if these upstream contracts fail.  
**Alternatives Considered:** Fallback to lower-ranked matches was rejected.

**Decision:** Observer should support both JSON mode and an HTML dashboard.  
**Rationale:** JSON mode supports automation and debugging, while the HTML dashboard provides a detailed human-readable live view with auto-update.  
**Alternatives Considered:** Terminal-only observer was rejected as insufficiently observable.

**Decision:** Treat sibling CLI implementations as the authoritative source of contract truth.  
**Rationale:** The remix editor and obfuscator contracts evolve independently; reading the live CLI implementations avoids drift between journal notes and actual payload semantics.  
**Alternatives Considered:** Relying on journal-only contract notes was rejected because it had already drifted from the current upstream behavior.

### Future Enhancements

**Nice to Have:**
- Resume/retry support for partially completed runs
- Richer artifact linking and drill-down views in the dashboard

**Potential Improvements:**
- Aggregate metrics across pipeline runs
- Optional compression/export of final results
- Escalating retry ladder for `remix_editor` and `obfuscator` with explicit upstream cancellation between attempts
- Terminal reconciliation against upstream remix-editor status/result artifacts when live polling appears stale

---

## ✅ Testing Checklist

- [ ] Integration flow validates CLI contracts against sibling tools
- [ ] Manual testing scenarios:
  - [ ] Matcher success path
  - [ ] `get_game` failure path
  - [ ] Remix editor polling path
  - [ ] Obfuscator polling path
  - [ ] Dashboard auto-update behavior
- [ ] HTML dashboard loads over local HTTP server
- [ ] Observer JSON output is stable and machine-readable

---

## 🎯 Success Criteria

- [ ] All phases completed
- [ ] Orchestrator produces fully observable persisted runs
- [ ] Observer CLI supports terminal and JSON modes
- [ ] HTML dashboard auto-updates from run data
- [ ] Final output is copied to a stable output location
- [ ] Strict failure handling is enforced across upstream steps
- [ ] Remix editor and obfuscator integrations match current upstream CLI contracts
