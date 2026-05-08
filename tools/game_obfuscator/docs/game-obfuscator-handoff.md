# Game Obfuscator - Handoff Document

**Last Updated:** 2026-04-26  
**Current Milestone:** Milestone 8 hardening complete — ready for dashboard work  
**Status:** Verification-integrated pipeline ready for next implementation task

---

## 1. Objective

Build a resumable, observable `game_obfuscator` system modeled after `game_remixer`.

The system should:

- take a **manifest** as input
- create a timestamped **run**
- process one or more game folders from `game_remixer` outputs as **seed inputs**
- aggressively transform each game so final output is:
  - one obfuscated `index.html`
  - one minimal `assets/emoji/` folder containing only used emoji images
  - observability artifacts and persisted state
- remove all audio
- keep the game functional

---

## 2. What Has Already Been Confirmed

### A. Input package shape
A `game_remixer` output game folder is a good normalized seed input.

Example inspected package:

- `../game_remixer/runs/run_game_remixer_20260426T132029Z/output/4d55e825-8749-412c-92a6-0a0bf4178ac9/`

Observed structure:
- `index.html`
- `assets/...`
- metadata JSON files

Important conclusion:
- containment is at the **folder level**
- `index.html` is not standalone by itself
- the folder is locally runnable via relative paths
- some packages may still be only `partially_offline_ready`

### B. `game_remixer` orchestration model
Reference files:
- `../game_remixer/scripts/create_run.py`
- `../game_remixer/scripts/prepare_inputs.py`

Pattern confirmed:
- manifest input
- timestamped run folder
- `input_manifest.json`
- `run_state.json`
- `games/<game_id>/game_state.json`
- mirrored inputs under run-local `input/`
- output per game
- resumable phase/state model

### C. Emoji image corpus
Local emoji source exists:

- `emoji-images-1.2.1/`
- image corpus in `emoji-images-1.2.1/imgs/`

Library characteristics:
- deterministic emoji PNG filenames based on unicode codepoints
- suitable as a local replacement image source
- only used emoji files should be copied into output packages

---

## 3. Recommended Seed Games

Use `../game_remixer/runs/run_game_remixer_20260426T132029Z/output/` as the initial seed pool.

Recommended initial sample set:

1. `4d55e825-8749-412c-92a6-0a0bf4178ac9`
   - already inspected
   - good known reference sample

2. `4e069308-48ba-4835-bd3f-51f0d86eafe1`
   - use as second sample to validate multi-game manifest flow

3. `80db988c-42c0-443c-94ed-6f7abeb035d0`
   - use as third sample to test repeatability and artifacts

These are only initial seed candidates from the same run output batch and can be refined after analysis tooling is added.

---

## 4. Proposed `game_obfuscator` Run Model

Top-level invocation:

```bash
python scripts/create_run.py --manifest path/to/manifest.json
```

Run directory:

```text
runs/run_game_obfuscator_<timestamp>/
  input_manifest.json
  run_state.json
  input/
  output/
  games/
  dashboard/
```

Per-game state path:

```text
runs/run_game_obfuscator_<timestamp>/games/<game_id>/game_state.json
```

Per-game output target:

```text
runs/run_game_obfuscator_<timestamp>/output/<game_id>/
  index.html
  assets/
    emoji/
  artifacts/
```

---

## 5. Proposed Manifest Shape

Initial draft:

```json
{
  "run_label": "seed_batch_001",
  "games": [
    {
      "game_id": "4d55e825-8749-412c-92a6-0a0bf4178ac9",
      "display_name": "Seed Game 1",
      "source_path": "../game_remixer/runs/run_game_remixer_20260426T132029Z/output/4d55e825-8749-412c-92a6-0a0bf4178ac9"
    },
    {
      "game_id": "4e069308-48ba-4835-bd3f-51f0d86eafe1",
      "display_name": "Seed Game 2",
      "source_path": "../game_remixer/runs/run_game_remixer_20260426T132029Z/output/4e069308-48ba-4835-bd3f-51f0d86eafe1"
    }
  ]
}
```

Possible later additions:
- `tags`
- `obfuscation_profile`
- `emoji_mapping_profile`
- `verification_profile`
- `notes`

---

## 6. Proposed Per-Game Phase State Machine

Initial recommended phases:

1. `created`
2. `input_prepared`
3. `inventory_scanned`
4. `emoji_mapping_planned`
5. `audio_removed`
6. `bundle_created`
7. `obfuscation_complete`
8. `verification_passed` or `verification_failed`
9. `packaged`

This should be stored in `game_state.json` along with:
- status
- current phase
- source path
- input mirror path
- working path
- output path
- attempt count
- last error
- timestamps
- artifact references

---

## 7. Observability Requirements

Every game should emit artifacts.

Minimum initial artifact set:

- `input_inventory.json`
- `analysis_summary.json`
- `emoji_mapping_plan.json`
- `audio_removal_report.json`
- `bundle_report.json`
- `obfuscation_report.json`
- `verification.json`
- `events.ndjson`

Important rule:
- never do aggressive transforms without leaving pre- and post-transform evidence

---

## 8. Immediate Next Task

Implement **Milestone 9 — dashboard + open-latest-dashboard workflow**.

### Scope
- build a run dashboard generator
- surface run-level and per-game status in a browser-friendly format
- expose artifact links for fast inspection
- add a helper to open the latest dashboard on macOS
- validate dashboard generation against:
  - `runs/run_game_obfuscator_seed_batch_001/`

### Required context updates from Milestone 8
- `scripts/obfuscate_outputs.py` was hardened to:
  - preserve inline `<script>` blocks
  - remove risky global inter-tag whitespace collapse
- `scripts/verify_outputs.py` is no longer a scaffold
  - it now runs real Playwright-based browser verification
  - local workflow depends on:
    - `.venv/`
    - Playwright Python package
    - installed Chromium runtime
- sample game `4d55e825-8749-412c-92a6-0a0bf4178ac9` now passes verification via browser automation

### Out of scope for next task
- stronger obfuscation levels
- wider rewrite heuristics
- large transformation changes unrelated to dashboarding or verification observability

---

## 9. Acceptance Criteria for Next Task

Milestone 9 is complete when:

- a dashboard is generated for a run
- the dashboard shows run status and per-game verification results
- key artifacts are linked from the dashboard
- there is a simple way to open the latest dashboard locally
- the seed run dashboard renders successfully

---

## 10. Handoff Rule

Milestones 1 through 8 are now complete.

After Milestone 9 implementation is complete:
- update `docs/journals/game-obfuscator.md`
- update this handoff doc
- update `docs/game-obfuscator-fresh-agent-recap.md`
- then hand off before any stronger obfuscation or optimization work

This keeps context size controlled and preserves milestone boundaries.

---

## 11. Primary References

- `docs/journals/game-obfuscator.md`
- `docs/game-obfuscator-handoff.md`
- `emoji-images-1.2.1/README.md`
- `../game_remixer/scripts/create_run.py`
- `../game_remixer/scripts/prepare_inputs.py`
- `../game_remixer/runs/run_game_remixer_20260426T132029Z/output/`

---

## 12. Current Recommendation

Proceed with **Milestone 9 only** using the now-verified seed run:

- `runs/run_game_obfuscator_seed_batch_001/`

Milestone 8 deliverables now exist:
- hardened `scripts/obfuscate_outputs.py`
- Playwright-backed `scripts/verify_outputs.py`
- local browser automation environment in `.venv/`
- per-game `verification.json` files with real browser artifacts
- seed sample `4d55e825-8749-412c-92a6-0a0bf4178ac9` verifying as `passed`

Important caveat:
- keep current obfuscation safety level stable
- prioritize dashboarding and observability before attempting stronger obfuscation again
