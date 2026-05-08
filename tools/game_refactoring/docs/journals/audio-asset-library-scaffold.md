# Audio Asset Library Scaffold Implementation Journal

**Last Updated:** 2026-04-29  
**Feature Spec:** Future operator pipeline audio mapping support  
**Backend Reference:** N/A

---

## 📊 Implementation Status Overview

### ✅ Phase 1: Audio Library Scaffold - **Complete**

- [x] Create repo-level audio source library folder
- [x] Define stable event-to-file naming contract
- [x] Add manifest for operator consumption
- [x] Add empty category folders for user-provided assets

**Status:** ✅ Complete

### Phase 2: Operator Pipeline Integration - **Planned**

- [ ] Wire `assets/audio_library/manifest.json` into the future audio mapping operator
- [ ] Copy selected source audio files into generated target game outputs
- [ ] Add validation for missing audio files and safe fallback behavior

**Status:** Planned

---

## 📝 Journal Entries

### 2026-04-29 09:33 - Audio Source Library Scaffold

**What Changed:**
- Created a repo-level audio source library under `assets/audio_library/`.
- Added a README explaining the exact file names and folders the user should populate.
- Added `manifest.json` as the canonical event-to-file mapping for future audio operators.
- Added `.gitkeep` placeholders for empty audio category directories.

**Why:**
The planned multi-step remix pipeline needs a deterministic local audio stash so a focused audio operator can map common game events to reusable local SFX/music without guessing filenames or relying on remote audio. The library is intentionally separate from generated game outputs: operators will copy selected assets into each target game and reference only local copied files.

**Files Created:**
- `assets/audio_library/README.md` - Human-facing placement guide and audio policy.
- `assets/audio_library/manifest.json` - Machine-readable event mapping for future operators.
- `assets/audio_library/sfx/.gitkeep` - Placeholder for short gameplay SFX.
- `assets/audio_library/ui/.gitkeep` - Placeholder for UI interaction sounds.
- `assets/audio_library/music/.gitkeep` - Placeholder for longer music loops.
- `assets/audio_library/ambience/.gitkeep` - Placeholder for reusable ambience loops.

**Technical Decisions:**
- SFX/UI are specified as `.wav` for short, responsive one-shots.
- Music/ambience are specified as `.mp3` for longer loops.
- The manifest uses stable semantic event keys such as `damage`, `pickup`, `game_over`, and `ambient_loop`.
- Runtime rules explicitly require copying audio into target game outputs and avoiding repo-level runtime references.
- Remote audio URLs remain disallowed.

**Testing:**
- Verify `assets/audio_library/manifest.json` parses as JSON.
- Verify required directories and placeholder files exist.

**Next Steps:**
- [ ] Add actual audio files using the README naming contract.
- [ ] Build the future audio mapping operator against `manifest.json`.
- [ ] Add static validation for missing audio files before operator runs.

**Status:** Complete

---

### 2026-04-29 09:39 - Generative Audio Prompt Guide

**Achievement:**
Added prompt guidance for generating every required audio asset in the audio library naming contract.

**Implementation Details:**
- Updated `assets/audio_library/README.md` with a `Generative AI Audio Prompts` section.
- Added per-file prompts for all SFX, UI, music, and ambience assets listed in `manifest.json`.
- Included global generation constraints for clean, game-ready audio:
  - no vocals
  - no copyrighted melodies
  - no brand/franchise references
  - no clipping
  - loopable output for music and ambience

**Technical Decisions:**
The prompts stay generic arcade/fantasy rather than franchise-specific so the resulting audio stash can be reused across many remix styles and game fixtures. SFX are short one-shots, while music and ambience prompts request seamless loops.

**Testing:**
README was updated in place and will be verified by checking for representative prompt headings.

**Status:** Complete

---

### 2026-04-29 12:48 - CDN Audio Index and Sanitizer

**Achievement:**
Added a simple CDN-backed grouped audio index workflow and sanitizer for prompt-named generated MP3 files.

**Implementation Details:**
- Created `scripts/sanitize_audio_library.py`.
  - Reads generated MP3s from `assets/audio_library/incoming/`.
  - Matches prompt-like filenames to semantic audio intents.
  - Copies matched files into clean variant names such as `sfx/jump_01.mp3`.
  - Writes grouped `assets/audio_library/audios.json`.
  - Copies unmatched files into `assets/audio_library/unmatched/`.
  - Supports `--dry-run` and `--apply`.
- Created `assets/audio_library/audios.json` as an object of grouped arrays.
- Added `assets/audio_library/incoming/.gitkeep` and `assets/audio_library/unmatched/.gitkeep`.
- Updated `assets/audio_library/README.md` to document:
  - all-MP3 convention
  - CDN base URL
  - grouped `audios.json` schema
  - `audio_type` values: `one_shot` and `loop`
  - sanitizer commands
  - shortened generation prompts
- Updated `assets/audio_library/manifest.json` so all canonical event paths use `.mp3`.

**Technical Decisions:**
- `audios.json` uses grouped arrays instead of a flat list because multiple generated versions can exist for the same intent.
- Each audio item uses only:
  - `name`
  - `url`
  - `location`
  - `usage`
  - `audio_type`
- Remote URLs are allowed only when they come from the trusted audio index and use the agreed CDN base:
  `https://gamezone-virid.vercel.app/assets/audios/`.

**Testing:**
- Run Python syntax validation for `scripts/sanitize_audio_library.py`.
- Validate `assets/audio_library/manifest.json` and `assets/audio_library/audios.json` as JSON.
- Run sanitizer dry-run.
- Run a temporary sample sanitizer pass to confirm prompt-like filenames map to clean grouped MP3 entries.

**Status:** Complete

---

### 2026-04-29 15:25 - Real Audio Import Applied

**Achievement:**
Ran the audio sanitizer against the real generated MP3 files in `assets/audios/` and populated the grouped CDN audio index.

**Implementation Details:**
- Replaced fuzzy filename matching with deterministic prompt-prefix matching in `scripts/sanitize_audio_library.py`.
- Sanitized 53 generated MP3 files from `assets/audios/`.
- Copied matched files into clean categorized paths under `assets/audio_library/`.
- Populated `assets/audio_library/audios.json` with grouped CDN-backed entries.
- Verified ambiguous prompt names map correctly:
  - `Enemy Hit Cue...` -> `enemy_hits`
  - `Whimsical Enemy Defeat...` -> `enemy_defeats`
  - `Short Level-complete...` -> `level_completes`
  - `Gentle Game-over...` -> `game_overs`
  - `Resume Cue...` -> `resumes`

**Verification:**
- `planned_copy_count`: 53
- `unmatched_count`: 0
- `audios.json` item count: 53
- All indexed local files exist.
- All indexed URLs use `https://gamezone-virid.vercel.app/assets/audios/`.
- All indexed items contain exactly:
  - `name`
  - `url`
  - `location`
  - `usage`
  - `audio_type`
- Empty groups after import:
  - `jumps`
  - `lands`
  - `shoots`
  - `projectiles`
  - `hits`

**Status:** Complete

---

### 2026-04-29 15:39 - Complete Audio Coverage Verified

**Achievement:**
Rebuilt the sanitized audio library after additional generated MP3s were added and verified every audio group has at least two variants.

**Implementation Details:**
- Re-ran sanitizer dry-run against `assets/audios/`.
- Confirmed `planned_copy_count` increased to 65 and `unmatched_count` remained 0.
- Rebuilt generated MP3 outputs under:
  - `assets/audio_library/sfx/`
  - `assets/audio_library/ui/`
  - `assets/audio_library/music/`
  - `assets/audio_library/ambience/`
- Re-populated `assets/audio_library/audios.json`.

**Verification:**
- `audios.json` item count: 65
- Every expected group has at least 2 items.
- `lands` has 3 items.
- All local files referenced by `audios.json` exist.
- All URLs use `https://gamezone-virid.vercel.app/assets/audios/`.
- Every item has exactly:
  - `name`
  - `url`
  - `location`
  - `usage`
  - `audio_type`
- `audio_type` values are valid: `one_shot` or `loop`.

**Status:** Complete

---

### 2026-04-29 15:52 - Audio Catalog Prompt Integration

**Achievement:**
Integrated the trusted CDN audio catalog into the creative refactor prompt flow so workers can read `audios.json` and add catalog-backed audio.

**Implementation Details:**
- Updated `prompts/audio_policy.md` to define catalog-driven audio enhancement.
- Updated active creative refactor templates:
  - `prompts/creative_refactor_agent_template.md`
  - `styles/neutral_prototype/prompts/creative_refactor_agent_template.md`
  - `styles/cyberpunk/prompts/creative_refactor_agent_template.md`
- Updated active style creative remix contracts:
  - `styles/neutral_prototype/specs/creative_remix_contract.md`
  - `styles/cyberpunk/specs/creative_remix_contract.md`
- Updated `scripts/generate_task_packet.py` to copy `assets/audio_library/audios.json` into attempt refs and expose `audio_catalog_path`.
- Updated `scripts/run_single_game.py` prompt construction to print `Audio Catalog Path` and instruct the worker to read the catalog JSON before editing.

**Technical Decisions:**
- Audio is now conditionally allowed through trusted catalog URLs only.
- Workers must not invent remote audio URLs.
- Gameplay must not depend on successful playback.
- The security/network model should allow `https://gamezone-virid.vercel.app/assets/audios/` only as a trusted audio catalog prefix.

**Verification:**
- Generated a temporary creative refactor task packet.
- Confirmed `audio_catalog_path` points to copied `refs/audios.json`.
- Confirmed copied `audios.json` includes populated groups such as `jumps` and `ambient_loops`.
- Confirmed `build_refactor_prompt()` includes `Audio Catalog Path` and the instruction to read the audio catalog JSON.

**Status:** Complete

---

## 🐛 Known Issues

None.

---

## 📚 Quick Reference

### Key Files

- `assets/audio_library/README.md` - Audio placement, sanitizer, CDN index, and prompt instructions.
- `assets/audio_library/manifest.json` - Canonical audio event mapping.
- `assets/audio_library/audios.json` - Grouped CDN-backed runtime audio index.
- `scripts/sanitize_audio_library.py` - Sanitizes prompt-named MP3s into grouped audio variants.
- `assets/audio_library/incoming/` - Staging folder for generated prompt-named MP3 files.
- `assets/audio_library/unmatched/` - Safe destination for MP3s that cannot be matched.
- `assets/audio_library/sfx/` - Short gameplay effects.
- `assets/audio_library/ui/` - Interface effects.
- `assets/audio_library/music/` - Music loops.
- `assets/audio_library/ambience/` - Atmosphere loops.

### Expected Asset Names

```text
sfx/jump_01.mp3
sfx/land_01.mp3
sfx/shoot_01.mp3
sfx/projectile_01.mp3
sfx/hit_01.mp3
sfx/damage_01.mp3
sfx/enemy_hit_01.mp3
sfx/enemy_defeat_01.mp3
sfx/pickup_01.mp3
sfx/bonus_01.mp3
sfx/powerup_01.mp3
sfx/explosion_01.mp3
sfx/blocked_01.mp3
sfx/warning_01.mp3
sfx/success_01.mp3
sfx/failure_01.mp3
sfx/game_over_01.mp3
sfx/level_complete_01.mp3

ui/click_01.mp3
ui/hover_01.mp3
ui/start_01.mp3
ui/pause_01.mp3
ui/resume_01.mp3
ui/menu_open_01.mp3
ui/menu_close_01.mp3

music/ambient_loop_01.mp3
music/action_loop_01.mp3
music/victory_loop_01.mp3
music/defeat_loop_01.mp3

ambience/soft_magic_loop_01.mp3
ambience/spooky_loop_01.mp3
ambience/arcade_loop_01.mp3
```

---

## 💭 Notes & Decisions

### Design Decision: Trusted CDN Runtime Audio Index

**Decision:** `assets/audio_library/audios.json` is the runtime-facing trusted CDN audio index.  
**Rationale:** A shared CDN catalog avoids copying every audio variant into every game and lets remix operators choose from grouped semantic audio variants.  
**Alternatives Considered:** Local-only audio copies were safer for offline portability but created more per-game asset management overhead. The agreed compromise is to allow only trusted CDN audio URLs listed in `audios.json`.
