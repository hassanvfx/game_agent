# Large Raw Catalog Four-Prompt Batch Journal

**Last Updated:** 2026-05-08  
**Feature Spec:** N/A  
**Backend Reference:** See [clineflow/index.json](./index.json) for API file paths

---

## 📊 Implementation Status Overview

### ✅ Phase 1: Source Audit and Batch Shape - **IN PROGRESS**

- [x] Confirm the attached favorites JSON contains the selected `gamezone-{id}` entries
- [x] Verify the raw catalog contains the same selected games
- [x] Decide batch shape as four separate prompt-specific manifests with concurrency 1

**Status:** 🔧 In Progress

### Phase 2: Manifest Generation - **PLANNED**

- [ ] Generate one manifest per remix prompt
- [ ] Point every manifest entry at `/Volumes/backup/game_maker/catalogs/raw/gamezone-{id}`
- [ ] Store generated manifests under `fixtures/`

**Status:** Planned

### Phase 3: Launch Preparation - **PLANNED**

- [ ] Prepare one `creative_remix_v3` launch command per prompt
- [ ] Use `--max-concurrency 1` for each batch
- [ ] Capture the run IDs / output locations for later tracking

**Status:** Planned

---

## 📝 Journal Entries

### 2026-05-08 09:10 - Initial Setup

**What Changed:**
- Created journal for the larger raw-catalog batch task
- Confirmed the attached favorites list contains 107 selected `gamezone-{id}` entries
- Confirmed all 107 selected IDs exist under `/Volumes/backup/game_maker/catalogs/raw`
- Locked execution shape to 4 separate batches, one per remix prompt, each with concurrency 1

**Why:**
- The batch needs to scale from earlier single-game and small-manifest experiments to a broader raw-catalog run while preserving retryability and easier monitoring per prompt.

**Files Created:**
- `docs/journals/large-raw-catalog-four-prompt-batch.md` - Task journal for source audit, manifest generation, and batch launching

**Next Steps:**
- [ ] Generate four prompt-specific manifests for the 107 selected games
- [ ] Launch the four `creative_remix_v3` batches with `--max-concurrency 1`

**Status:** In Progress

---

## 💭 Notes & Decisions

### Design Decisions

**Decision:** Use four separate manifests instead of one combined manifest.  
**Rationale:** This keeps runs easier to retry, compare, and inspect per prompt.  
**Alternatives Considered:** One combined manifest spanning all prompts, rejected because prompt-specific reruns and monitoring would be less clean.

### Batch Prompts

- `harry potter`
- `rick and morty`
- `flappy bird`
- `harry potter with angrybrids mehcnics in 3d`
- `mothers day, but your mom hates you`

---

### 2026-05-08 09:28 - Single Prompt Follow-Up Batch

**What Changed:**
- Started a follow-up batch configuration for the prompt `mothers day, but your mom hates you`
- Reused the same verified 107-game raw-catalog source set from the prior four-prompt batch
- Planned a dedicated manifest and launcher path for this single additional prompt with concurrency 1

**Why:**
- This prompt should run as an independent batch so it can be tracked, retried, and compared without affecting the existing four launched runs.

**Next Steps:**
- [ ] Generate the dedicated manifest for `mothers day, but your mom hates you`
- [ ] Create a disposable launcher script for the prompt
- [ ] Launch the new `creative_remix_v3` batch with `--max-concurrency 1`

**Status:** In Progress

---

## ✅ Testing Checklist

- [ ] Source audit confirmed
- [ ] Four manifests generated
- [ ] Four launch commands prepared
- [ ] Four runs launched with concurrency 1

---

## 🎯 Success Criteria

- [ ] All 107 selected raw games are included in generated manifests
- [ ] One manifest exists for each of the 4 prompts
- [ ] Each batch is configured for `--max-concurrency 1`
- [ ] Documentation updated

---

*This journal tracks the raw-catalog four-prompt batch setup and launch workflow.*