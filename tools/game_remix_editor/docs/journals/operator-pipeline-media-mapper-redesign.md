# Operator Pipeline Media Mapper Redesign Journal

**Last Updated:** 2026-05-01 19:45 America/Mexico_City  
**Feature Spec:** Master plan for operator pipeline visual-pass redesign, media-mapper redesign, and workspace-local catalogs  
**Backend Reference:** N/A

---

## 📊 Implementation Status Overview

### ✅ Phase 1: Planning and Architecture - **COMPLETE**

- [x] Audited current emoji/audio integration points
- [x] Identified current prompt/runner catalog injection behavior
- [x] Defined milestone-based redesign plan with handoffs
- [x] Chose workspace-local `catalogs/` as the new media contract

**Status:** ✅ Complete

### Phase 2: Catalog Bootstrap - **COMPLETE**

- [x] Create root `catalogs/` directory
- [x] Copy current audio catalog into `catalogs/audios.json`
- [x] Scaffold `catalogs/gifs.json`
- [x] Scaffold `catalogs/sprites.json`
- [x] Add lightweight catalog documentation

**Status:** ✅ Complete

### Phase 3: Runner and Prompt Refactor - **COMPLETE**

- [x] Copy catalogs into each operator workspace before execution
- [x] Remove repo-root catalog references from prompt packets
- [x] Rewrite Stage 02 as character-first creative visual design
- [x] Rewrite Stage 03 as media-mapper and audio enhancement
- [x] Align docs and validation language with the new contract

**Status:** ✅ Complete

---

## 📝 Journal Entries

### 2026-05-01 19:45 - Merge feat/media-mapper into main preparation

**Achievement:**
Prepared the `feat/media-mapper` branch for integration into `main` after confirming the working tree is clean and that this journal remains the active source-of-truth for the media-mapper redesign track.

**Implementation Details:**
- Confirmed current branch: `feat/media-mapper`
- Confirmed `git status --short --branch` reports no uncommitted file changes
- Reviewed existing journal coverage and reused `docs/journals/operator-pipeline-media-mapper-redesign.md` as the active task journal for this merge step

**Technical Decisions:**
This merge is being documented in the existing redesign journal rather than creating a separate one because the branch being merged is the implementation branch for the same media-mapper redesign workstream.

**Next Steps:**
- [ ] Checkout `main`
- [ ] Merge `feat/media-mapper` into `main`
- [ ] Verify repository status and current branch after merge

**Status:** In Progress

---

### 2026-05-01 01:25 - Stage 03 rename and refined Stage 03 / Stage 04 split

**Achievement:**
Renamed Stage 03 conceptually to `media_mapper`, strengthened its mapping/plumbing ownership, and clarified that Stage 04 now owns typography/icon/layout polish plus the final doctor pass.

**Implementation Details:**
- Created `prompts/operators_v2/03_media_mapper.md` as the new Stage 03 prompt path
- Updated `configs/operator_pipeline_v2.json` so Stage 03 now uses operator ID `media_mapper`
- Updated `scripts/run_operator_pipeline_game.py` so Stage 03 retry/warning logic keys off `media_mapper`
- Strengthened runner prompt-packet wording so `catalogs/fonts.json` is surfaced alongside the other required workspace catalogs
- Updated `prompts/operators_v2/04_final_code_ui_mobile_repair.md` so Stage 04 explicitly owns typography hierarchy, icon polish, instructional-card minimization, and final doctoring
- Updated `docs/operator_pipeline_manual.md` so the operator responsibility split and example commands now reflect `media_mapper`

**Technical Decisions:**
The old `audio_integration` name was no longer accurate once Stage 03 became responsible for broader media cleanup, mapping, and import plumbing. Keeping Stage 03 as a mapping/plumbing pass and Stage 04 as a polish/doctor pass gives clearer failure ownership and cleaner validation criteria.

**Next Steps:**
- [x] Broadly replace remaining legacy `03_audio_integration` / `audio_integration` references in supporting docs and fixture references where they still serve as source-of-truth documentation
- [ ] Decide whether to delete the legacy `prompts/operators_v2/03_audio_integration.md` file after all references are migrated
- [x] Define the refreshed validation checklist separating Stage 03 mapping/plumbing checks from Stage 04 polish/doctor checks
- [ ] Run a fresh validation batch under the renamed split

**Validation Checklist Split:**

Stage 03 / Media Mapper should now be judged on:
- bad URL cleanup
- catalog adoption
- import plumbing
- mapped assets actually appearing in code/output when safely possible

Stage 04 / Final Repair should now be judged on:
- typography hierarchy
- Material Symbols/icon imports being present when needed
- icon classes/usages actually appearing when appropriate
- instruction-card minimization, dismissal, fade, or collapse during play
- mobile-safe final polish
- final runtime repair / doctoring

**Status:** In Progress

---

### 2026-05-01 17:17 - Stage 04 media-policy gate removal so Stage 03 is the trusted enforcement stage

**Achievement:**
Removed Stage 04 media/font/icon media-policy gating from the runner so Stage 03 remains the trusted enforcement stage for media-policy cleanup, while Stage 04 continues as a final repair/polish pass without retrying on inherited policy leftovers.

**Implementation Details:**
- Updated `scripts/run_operator_pipeline_game.py` to remove the `final_code_ui_mobile_repair` retry/failure gate that previously depended on:
  - `remaining_media_candidates`
  - `remaining_media_cleanup_plan`
  - `remaining_font_candidates`
  - `remaining_icon_candidates`
- Kept Stage 03 (`media_mapper`) retry/warning logic intact, still driven by:
  - `remaining_urls`
  - `remaining_media_candidates`
- Simplified final `media_policy_warning` behavior so warnings are now only emitted for unresolved Stage 03 media-mapper leftovers, not for Stage 04 inherited cleanup findings
- Confirmed by code inspection that Stage 03 and Stage 04 both call the same media-policy report writer:
  - `write_media_policy_report(...)`
- Confirmed the actual stage difference was not a different extractor, but different pass/fail gating in the runner

**Technical Decisions:**
The pipeline should have a single trusted enforcement owner for media cleanup. Since Stage 03 already owns media mapping, replacement, and cleanup semantics, Stage 04 should not independently retry/fail on inherited media/font/icon leftovers. This keeps stage ownership stable and prevents the final repair pass from re-litigating Stage 03 enforcement outcomes.

**Next Steps:**
- [ ] Run a fresh validation case and confirm Stage 04 no longer retries/fails because of inherited media-policy leftovers
- [ ] Decide whether Stage 04 should still write `media_policy_report.json` purely for diagnostics, or whether that artifact should be dropped from the final-repair stage in a later cleanup
- [ ] Reflect this Stage 03-trusted / Stage 04-diagnostic split in `docs/media_mapper_prompt_packet_spec.md` if the spec is meant to remain the authoritative policy reference

**Status:** In Progress

---

### 2026-05-01 17:08 - Deterministic Stage 03 detector hardening and follow-up validation setup

**Achievement:**
Hardened the Stage 03 detector against two grounded false-positive sources, shifted Stage 03 prompt language further toward creative catalog inference, added future-enhancement guidance to Stage 01, and launched fresh validation runs to confirm the new behavior.

**Implementation Details:**
- Updated `scripts/media_policy.py` to:
  - exclude `catalogs/` files from candidate extraction
  - narrow extension-scan matching so it only captures true local/relative `assets...` tokens
  - prevent `/assets...` tail extraction from allowlisted full URLs like `https://gamezone-virid.vercel.app/assets/...`
- Verified directly on:
  - `runs/repeat11_no_prompt_harry_flappy_canonical_20260501/games/92b1e776-6c8e-4707-9421-31d55195f9fd/operator_pipeline/stage_03_media_mapper/attempt_01/workspace`
- Confirmed rebuilt detector output after the fix reports:
  - `media_candidates: []`
  - `actionable_media_refs: []`
- Updated `scripts/run_operator_pipeline_game.py` prompt-packet wording so Python-listed font candidates are framed as required creative font-remap work sourced from `catalogs/fonts.json`
- Updated `prompts/operators_v2/03_media_mapper.md` so Stage 03 is described as creative media inference and catalog-guided mapping rather than only cleanup/compliance
- Updated `prompts/operators_v2/01_gameplay_narrative.md` with a new section:
  - `Creative Direction for Future Enhancements`
  - allowing lightweight developer comments for future media hook points
- Launched fresh Harry/flappy validation runs:
  - `validate_hp_flappy_no_prompt_20260501`
  - `validate_hp_flappy_dragon_ball_20260501`
  - `validate_hp_flappy_cut_the_rope_20260501`

**Grounded Findings:**
1. `media_policy_report.json` is the detector truth source used to build the Stage 03 packet and determine unresolved post-stage candidates.
2. The earlier repeat run exposed two real detector bugs:
   - catalog JSON files were being scanned as if they were actionable source files
   - allowlisted Vercel URLs were yielding bogus local `/assets...` tail candidates
3. After the detector hardening, those exact false positives no longer reproduce on the inspected failing workspace.
4. Stage 03 media behavior is now substantially more trustworthy, and the remaining follow-up is mainly broader validation and doc/spec cleanup.

**Technical Decisions:**
The deterministic fix is to tighten extraction order and boundaries rather than layering more heuristics afterward:
- structured full-ref extraction first
- allowlist pruning on full external refs
- limited local-token extraction only for true local/relative asset refs
- no catalog scanning during candidate extraction

**Next Steps:**
- [ ] Let the three Harry/flappy validation runs progress and inspect Stage 03 outputs
- [ ] Update `docs/media_mapper_prompt_packet_spec.md` to fully mirror the new inference-first framing and detector hardening
- [ ] Decide whether any remaining prompt files (`02_visual_emoji_identity`, `04_final_code_ui_mobile_repair`) need wording alignment in the same vector

**Status:** In Progress

---

### 2026-05-01 03:35 - Top-level CLI correction for validation experiments

**Achievement:**
Corrected the validation launch procedure to use the documented top-level user-facing CLI rather than the lower-level batch runner directly.

**Implementation Details:**
- Re-read `README.md` and confirmed the supported orchestration entrypoint is `scripts/creative_refactor_cli.py`
- Confirmed the documented manifest-driven lifecycle is:
  - `start-batch`
  - `status`
  - `result` / `finish`
- Corrected the experiment launch pattern for the three target variants:
  - no prompt
  - Harry Potter
  - Flappy Bird
- Noted that earlier direct `run_parallel_batch.py` launches were lower-level engine usage, not the preferred top-level contract the user requested

**Top-level CLI Commands To Use:**
- No prompt:
  - `python3 /Volumes/Elements/game_remix_editor/scripts/creative_refactor_cli.py --json start-batch --manifest /Volumes/Elements/game_remix_editor/fixtures/repeat2_three_game_manifest_20260430.json --style neutral_prototype --model gpt-5.4 --agent-timeout 3600 --max-concurrency 2 --poll-seconds 5 --stale-heartbeat-seconds 900`
- Harry Potter:
  - `python3 /Volumes/Elements/game_remix_editor/scripts/creative_refactor_cli.py --json start-batch --manifest /Volumes/Elements/game_remix_editor/fixtures/repeat2_three_game_manifest_20260430.json --style neutral_prototype --remix-prompt "Harry Potter" --model gpt-5.4 --agent-timeout 3600 --max-concurrency 2 --poll-seconds 5 --stale-heartbeat-seconds 900`
- Flappy Bird:
  - `python3 /Volumes/Elements/game_remix_editor/scripts/creative_refactor_cli.py --json start-batch --manifest /Volumes/Elements/game_remix_editor/fixtures/repeat2_three_game_manifest_20260430.json --style neutral_prototype --remix-prompt "Flappy Bird" --model gpt-5.4 --agent-timeout 3600 --max-concurrency 2 --poll-seconds 5 --stale-heartbeat-seconds 900`
- Status:
  - `python3 /Volumes/Elements/game_remix_editor/scripts/creative_refactor_cli.py --json status --run-id <run_id>`
- Result:
  - `python3 /Volumes/Elements/game_remix_editor/scripts/creative_refactor_cli.py --json result --run-id <run_id>`

**Technical Decisions:**
The top-level CLI is the correct interface for user-driven experiment orchestration because it preserves the intended async lifecycle and result contract. The lower-level batch runner remains useful as an engine, but it should not be treated as the primary documented user-facing launch path for these validation experiments.

**Next Steps:**
- [ ] Launch the no-prompt experiment via the top-level CLI
- [ ] Launch the Harry Potter experiment via the top-level CLI
- [ ] Launch the Flappy Bird experiment via the top-level CLI
- [ ] Poll each run through the top-level `status` command
- [ ] Inspect final outputs for surviving relative `assets/...` refs and normalized placeholder-safe replacements

**Status:** In Progress

---

### 2026-05-01 01:35 - Commit checkpoint after Stage 03 rename rollout

**Achievement:**
Finished the source-level Stage 03 rename to `media_mapper`, created a rollback tag, defined the new validation split, and launched a fresh three-game no-prompt validation batch.

**Implementation Details:**
- Created rollback tag `opv2-media-mapper-rollback-20260501-0123`
- Completed source-level replacement of `audio_integration` / `stage_03_audio_integration` references across prompts, config, runner, docs, and journal files
- Confirmed source-tree searches under `configs`, `docs`, `fixtures`, `prompts`, and `scripts` no longer report legacy Stage 03 source references
- Ran `python3 -m py_compile` successfully for `scripts/run_operator_pipeline_game.py`, `scripts/operator_registry_v2.py`, and `scripts/operator_pipeline_lab.py`
- Validated `configs/operator_pipeline_v2.json` with `python3 -m json.tool`
- Defined the refreshed validation split:
  - Stage 03 = URL cleanup, catalog adoption, import plumbing, mapped assets appearing
  - Stage 04 = typography hierarchy, icon imports/usages, instructional-card minimization, mobile-safe polish, runtime repair
- Started fresh validation batch `repeat2_media_mapper_split_20260501` using `fixtures/repeat2_three_game_manifest_20260430.json`
- Confirmed the new batch is a three-game **no-prompt** run with `remix_prompt: null`

**Technical Decisions:**
The rename is now treated as a full source-of-truth shift rather than a cosmetic alias. Validation is explicitly split so Stage 03 is judged on plumbing/compliance outcomes while Stage 04 is judged on premium UI polish and doctoring outcomes.

**Next Steps:**
- [ ] Monitor `repeat2_media_mapper_split_20260501` to completion
- [ ] Inspect outputs for Stage 03 mapping/plumbing effectiveness and Stage 04 icon/typography/overlay polish
- [ ] Decide whether to delete or retain legacy compatibility files such as `prompts/operators_v2/03_audio_integration.md`

**Status:** In Progress

---

### 2026-05-01 02:40 - Master plan for placeholder-safe media normalization and enforcement

**Goal:**
Eliminate IP-risky retained media references by forcing actionable media replacements to resolve into approved catalog-backed outputs with normalized placeholder-safe naming, then prevent later stages from reintroducing old references.

**Master Plan:**

#### Phase A — Detection and packet shaping
1. Keep Python detection focused on actionable source files only
2. Emit concise candidate lists into prompt packets
3. Distinguish:
   - original actionable refs to replace
   - approved icon vocabulary / catalog guidance to prefer
4. Keep richer structured metadata in Python reports for enforcement/debugging only

#### Phase B — Deterministic replacement normalization
1. Define a Python-owned naming scheme for approved replacement outputs, for example:
   - `infer-audio-01.mp3`
   - `infer-image-01.png`
   - `infer-gif-01.gif`
   - `infer-video-01.mp4`
2. Treat these as **destination placeholder-safe names**, not as the original candidates
3. Model the flow as:
   - `original_ref -> approved replacement -> normalized safe output name`
4. Ensure old asset references disappear from code after replacement

#### Phase C — Stage enforcement
1. Stage 03 should fail/retry when actionable media refs remain unresolved
2. Stage 04 should fail/retry when actionable font/icon refs remain unresolved
3. Persist unresolved candidate counts into stage results for observability
4. Add a final Stage 04 recheck so old refs cannot be reintroduced silently

#### Phase D — Cleanup and pruning
1. After verified replacement, prune obsolete actionable media refs/files where safe
2. Prefer post-replacement cleanup over pre-stage blanket deletion
3. Keep fallback-safe behavior while replacement is in progress, but do not allow risky refs in final outputs

#### Phase E — Validation
1. Re-run the three target variants:
   - no prompt
   - Harry Potter
   - flappy bird
2. Inspect:
   - Stage 03 local audio/media remap effectiveness
   - Stage 04 font/icon alignment
   - disappearance of original risky refs
   - appearance of normalized placeholder-safe replacement names

**Why this order:**
This preserves determinism, keeps the agent focused on approved catalog choice rather than ad hoc path invention, and gives Python final authority over safe naming and enforcement.

**Next Steps:**
- [ ] Implement the deterministic generic rename scheme for approved replacement media outputs
- [ ] Implement safer post-replacement cleanup/pruning for obsolete actionable media refs
- [ ] Add a final recheck so Stage 04 cannot reintroduce actionable media/font/icon candidates
- [ ] Revalidate across the three target variants after normalization enforcement is live

**Execution Plan:**
1. Extend `scripts/media_policy.py` to classify actionable media candidates into normalized placeholder-safe destination types and emit deterministic destination names such as `infer-audio-01.mp3`, `infer-image-01.png`, `infer-gif-01.gif`, and `infer-video-01.mp4`.
2. Persist the normalization mapping in the media-policy report so Stage 03 and Stage 04 can be evaluated against both the original actionable refs and the expected safe destination names.
3. Update `scripts/run_operator_pipeline_game.py` prompt-packet construction so Stage 03 receives concise actionable replacement targets plus the normalized destination-name contract, and Stage 04 can perform a final recheck against unresolved media/font/icon candidates.
4. Add safer post-replacement cleanup/pruning logic that only removes obsolete actionable refs/files after approved replacement has been verified, avoiding pre-stage blanket deletion.
5. Strengthen final enforcement so Stage 04 cannot pass while actionable media/font/icon candidates remain or while previously replaced risky refs are reintroduced.
6. Re-run the three target variants (`no prompt`, `Harry Potter`, `flappy bird`) and inspect whether original risky refs disappear and normalized placeholder-safe names appear consistently.

**Status:** In Progress

---

### 2026-05-01 11:02 - Concrete failure analysis after live Stage 03 retries

**Achievement:**
Captured the exact divergence between isolated detector/prompt fixture success and real Stage 03 retry behavior in a live no-prompt run, and documented the remaining policy mismatch.

**Implementation Details:**
- Added `docs/media_mapper_prompt_packet_spec.md` to formalize the intended packet shape and detector policy matrix
- Added fixture wrappers:
  - `scripts/test_media_policy_fixture.py`
  - `scripts/test_media_mapper_prompt_fixture.py`
- Verified fixture success against the captured Harry Potter Stage 03 workspace
- Traced a real live failure case:
  - run: `run_game_remixer_20260501T161133Z`
  - game: `67bcbe5b-f3fc-4675-b5ae-e8843bc2c46a`
- Confirmed all three Stage 03 attempts used the new REQUIRED packet wording and identical initial media candidate lists
- Confirmed post-stage rescans still reported unresolved media and font candidates after each attempt
- Confirmed attempt 3 was allowed to terminate with warning while unresolved candidates still remained

**Concrete Findings:**
1. The prompt packet/template fixes are present in the real pipeline output.
2. The detector improvements are real and validated by fixture tests.
3. The remaining failure is the post-stage policy/enforcement model:
   - the operator rewrites the workspace
   - Python rescans the modified workspace
   - unresolved refs still remain
4. The biggest active mismatch is policy inconsistency:
   - `_is_allowed_external_url()` allows `gamezone-virid.vercel.app`
   - but actionable media replacement logic still treats some `https://gamezone-virid.vercel.app/assets/audios/...` refs as unresolved replacement candidates
5. Font mirrored assets are also still unresolved, for example:
   - `assets/fonts.googleapis.com/css2-family_Fredoka_wght_400_600_family_VT323_display_swap.css`
   - mirrored `fonts.gstatic` binary refs

**Technical Decisions:**
The same classification logic must be shared pre and post:
- same actionable source-file filter
- same allowlist decision
- same media/font classification
- same exemptions

If a Vercel URL is allowed, it must be allowed both pre and post.
If a mirrored font stylesheet/file is actionable, it must be actionable both pre and post.

**Next Steps:**
- [ ] Align actionable media replacement logic with `_is_allowed_external_url()` so allowed Vercel refs are not treated as contradictory unresolved failures
- [ ] Generalize font stylesheet/file handling using the same pre/post classification model
- [ ] Re-run a fresh single no-prompt case after policy alignment
- [ ] Then rerun the broader experiments

**Status:** In Progress

---

### 2026-05-01 00:06 - Final-stage mobile typography and icon policy refinement

**Achievement:**
Refined the final repair stage prompt with explicit mobile typography hierarchy guidance and lightweight icon recommendations for UI simplification.

**Implementation Details:**
- Updated `prompts/operators_v2/04_final_code_ui_mobile_repair.md`
- Added a gameplay-first mobile typography policy favoring caption/body-sized HUD and gameplay text
- Added explicit exceptions for intro, modal, pause, and results screens
- Added sample sane mobile font hierarchy ranges
- Added guidance encouraging `Material Symbols Outlined` for compact mobile-friendly utility UI
- Clarified that gameplay visibility, graphics, and controls take priority unless the genre is text-based

**Technical Decisions:**
The final-stage operator should optimize mobile readability without letting HUD or helper copy dominate the playfield. Small, readable typography and lightweight iconography are preferred over bulky text-heavy interface chrome during active gameplay.

**Next Steps:**
- [ ] Mirror a short version of this typography policy into `docs/operator_pipeline_manual.md` if desired
- [ ] Observe future transformed outputs to see whether the operator follows the hierarchy guidance consistently
- [ ] Expand the icon recommendations only if specific repeated UI needs appear in live runs

**Status:** In Progress

---

### 2026-04-30 23:55 - Validation success, repeat runs, and media-policy hardening

**Achievement:**
Validated the updated media-mapper flow against recent runs, repeated the three main experiment variants through the CLI, and hardened the Python media-policy pass using broader sibling-project URL allowance knowledge.

**Implementation Details:**
- Validated recent no-prompt and prompt runs and inspected Stage 03 artifacts
- Recreated and launched repeated three-game variant runs through the CLI entrypoint
- Confirmed repeat5 no-prompt, flappy-bird, and harry-potter runs completed successfully
- Expanded `scripts/media_policy.py` to allow additional safe support/runtime hosts and CDN/package hosts
- Excluded metadata-only files like `mirror_build_summary.json` and `url_map.json` from `potential_urls_to_remove`
- Re-checked the previously noisy workspace and confirmed the resulting `potential_urls_to_remove` list was empty

**Technical Decisions:**
The media-policy pass should produce a clean runtime-relevant removal list, not a noisy inventory of every URL seen anywhere in the workspace. The deterministic Python pass now better reflects the sibling project's broader CDN/package knowledge while preserving custom hard-blocking for Rezona/Resona.

**Next Steps:**
- [ ] Update any remaining journal metadata fields such as the Last Updated timestamp if desired
- [ ] Consider additional host expansions only when a concrete noisy case appears again
- [ ] Keep validating Stage 03 hints against live experiment outputs as new variants are introduced

**Status:** In Progress

---

### 2026-04-30 23:00 - Native Python media-policy pass wired into Stage 03

**Achievement:**
Added native Python media-policy scanning and connected it to the media-mapper stage as a deterministic URL-removal hint and post-step enforcement signal.

**Implementation Details:**
- Created `scripts/media_policy.py` to scan workspace text files for external URLs
- Added deterministic allowlist handling for approved hosts and hard blacklist handling for Rezona/Resona URLs
- Updated `scripts/run_operator_pipeline_game.py` to write `media_policy_report.json` for each attempt
- Passed only `potential_urls_to_remove` into the operator prompt as a Python-generated hint
- Added a post-stage Python re-scan for Stage 03
- Configured Stage 03 retry behavior so remaining disallowed URLs force retries until the final attempt, then the stage passes with a warning summary if URLs still remain

**Technical Decisions:**
All whitelist and blacklist logic now stays in Python. The operator only receives exact URL removal hints and is not trusted to infer policy. This keeps enforcement deterministic while still letting the media-mapper attempt targeted cleanup.

**Next Steps:**
- [ ] Validate the new media-policy pass against a known run or fixture
- [ ] Consider expanding exact approved host coverage if Giphy needs additional subdomains
- [ ] Decide whether remaining URL warnings should be surfaced at run summary level as well as attempt result level

**Status:** In Progress

---

### 2026-04-30 22:51 - Prompt redesign and manual alignment

**Achievement:**
Rewrote Stage 02 and Stage 03 around the new architecture and aligned the operator pipeline manual with the workspace-local catalog contract.

**Implementation Details:**
- Updated `prompts/operators_v2/02_visual_emoji_identity.md` to become a character-first visual identity pass
- Updated `prompts/operators_v2/03_audio_integration.md` to become a media mapper and audio enhancement pass
- Created `prompts/operators_v2/03_media_mapper.md` as the new canonical Stage 03 prompt path
- Updated `docs/operator_pipeline_manual.md` so operator responsibilities now match the new prompt direction and workspace-local `catalogs/` contract

**Technical Decisions:**
The pipeline now separates creative visual authorship from media compliance more cleanly:
- Stage 02 owns visual language, character-first art direction, and coherent world design
- Stage 03 owns approved media replacement, media cleanup, and lightweight audio enhancement

**Next Steps:**
- [ ] Inspect the sibling `game_obfuscator` allowed-domain and media-detection logic
- [ ] Port whitelist policy for approved domains and relative assets
- [ ] Update validators or enforcement paths to use the new approved-media contract

**Status:** In Progress

---

### 2026-04-30 22:48 - Workspace catalog injection and prompt contract update

**Achievement:**
Implemented workspace-local catalog injection in the per-game operator runner and updated the prompt packet contract to point operators at workspace-local media catalogs.

**Implementation Details:**
- Modified `scripts/run_operator_pipeline_game.py` to copy root-level catalog files into each attempt workspace under `workspace/catalogs/`
- Replaced repo-root prompt fields for direct audio/emoji asset references with a workspace-local catalog block
- Updated the runner so every attempt prompt now references:
  - `catalogs/audios.json`
  - `catalogs/gifs.json`
  - `catalogs/sprites.json`

**Technical Decisions:**
Workspace-local catalogs are now the canonical operator-facing contract. This reduces ambiguity, removes dependency on repo-root catalog references during prompt execution, and sets up the later Stage 03 media-mapper redesign.

**Next Steps:**
- [ ] Rewrite `prompts/operators_v2/02_visual_emoji_identity.md` as a character-first visual creativity pass
- [ ] Rewrite `prompts/operators_v2/03_audio_integration.md` into a media-mapper and audio-enhancement pass
- [ ] Update docs to reflect workspace-local catalogs as the active operator contract

**Status:** In Progress

---

### 2026-04-30 22:43 - Master plan and bootstrap preparation

**What Changed:**
- Established the redesign direction for the operator pipeline
- Broke the work into milestones and explicit handoffs
- Selected root-level `catalogs/` as the new canonical media catalog location
- Identified catalog bootstrap as the first implementation slice

**Why:**
The current pipeline mixes prompt-time catalog references, older emoji/audio language, and signs of a migration toward workspace-local catalog usage. A stable `catalogs/` root creates a deterministic base for later runner, prompt, and validator refactors. The redesign also cleanly separates responsibilities:
- Stage 02 becomes a creative visual identity pass
- Stage 03 becomes the media-mapper / compliance pass

**Files Created:**
- `docs/journals/operator-pipeline-media-mapper-redesign.md` - Master planning and implementation journal for this redesign track

**Next Steps:**
- [ ] Create `catalogs/` at repo root
- [ ] Copy the current audio catalog into `catalogs/audios.json`
- [ ] Scaffold placeholder `catalogs/gifs.json`
- [ ] Scaffold placeholder `catalogs/sprites.json`
- [ ] Add `catalogs/README.md` documenting the intended contract

**Status:** In Progress

---

## 🐛 Known Issues

### Mixed catalog contract language

**Problem:** 
Current project materials show evidence of two different models:
- repo-root catalog path references
- workspace-local/inference-style catalog references in run artifacts

**Root Cause:** 
The pipeline appears to be mid-transition between older prompt contracts and newer workspace-oriented media enforcement patterns.

**Status:** 
- [x] Being investigated
- [ ] Blocked (waiting for...)
- [ ] Fixed

**Workaround:** 
Establish a new canonical root `catalogs/` directory and migrate runtime references to workspace-local copies from that source.

**Resolution:** 
Pending implementation.

---

## 📚 Quick Reference

### Key Files

- `assets/audio_library/audios.json` - Current source audio catalog
- `scripts/run_operator_pipeline_game.py` - Per-game operator runner now copying root catalogs into workspace-local `catalogs/`
- `prompts/operators_v2/02_visual_emoji_identity.md` - Character-first Stage 02 prompt
- `prompts/operators_v2/03_media_mapper.md` - Canonical Media-mapper Stage 03 prompt
- `prompts/operators_v2/03_audio_integration.md` - Legacy Stage 03 prompt path pending cleanup
- `docs/operator_pipeline_manual.md` - Operator pipeline manual aligned to workspace-local catalogs and new stage roles
- `scripts/media_policy.py` - Python-owned media-policy pass with expanded sibling-inspired allow behavior and metadata exclusion

### Immediate Milestones

1. Catalog bootstrap
2. Workspace catalog injection
3. Stage 02 visual-pass rewrite
4. Stage 03 media-mapper rewrite
5. Whitelist/enforcement integration
6. Validation and docs alignment

---

## 💭 Notes & Decisions

### Design Decisions

**Decision:** Use repo-root `catalogs/` as the canonical source for media catalog JSON files.  
**Rationale:** It creates a stable, human-editable contract that can be copied into each operator workspace at a deterministic location.  
**Alternatives Considered:** Continuing to reference scattered asset-library roots directly; rejected because it keeps prompt/runtime behavior ambiguous.

**Decision:** Make Stage 02 creativity-first and Stage 03 compliance-first.  
**Rationale:** Visual design and media-policy enforcement are different jobs and should not be mixed in one prompt responsibility.  
**Alternatives Considered:** Keeping audio-only responsibility for Stage 03; rejected because media cleanup/remapping needs a dedicated owner.

### Future Enhancements

**Nice to Have:**
- Shared schema documentation for all media catalogs
- Machine validation for catalog structure
- Automated fixture checks for workspace catalog injection
- Expanded approved-host coverage for any required Giphy delivery variants
- More precise runtime-source detection if future noisy sources appear

---

## ✅ Testing Checklist

- [x] Root `catalogs/` directory exists
- [x] `catalogs/audios.json` is valid JSON
- [x] `catalogs/gifs.json` is valid JSON
- [x] `catalogs/sprites.json` is valid JSON
- [x] Scaffold structure matches intended starting contract
- [x] Journal reflects implementation progress accurately
- [x] Runner copies root catalogs into each attempt workspace
- [x] Prompt contract references workspace-local catalogs
- [x] Python media-policy pass generates exact `potential_urls_to_remove` hints
- [x] Stage 03 retries on remaining URLs and passes with warning after final attempt
- [x] Media-policy hint noise reduced by excluding metadata-only files and allowing safe support/CDN hosts
- [x] Repeat5 no-prompt, flappy-bird, and harry-potter experiment runs completed successfully

---

## 🎯 Success Criteria

- [x] Root media catalogs are bootstrapped
- [x] Future runner work can target `catalogs/*.json`
- [x] Journal captures decisions and next milestones clearly
