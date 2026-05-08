# Intent vs Code Deltas

This document compares the current user-stated architectural intent against the code evidence inspected so far.

It is deliberately provisional and should be updated as more files are read.

## Confidence rule

Every delta below is tagged as:

- **Confirmed delta**: code directly disagrees with the intended model
- **Confirmed alignment**: code directly supports the intended model
- **Partial / needs more evidence**: current evidence is suggestive but incomplete

## Intent statements being checked

These intent statements came from the current planning conversation and should be treated as hypotheses to validate, not final truth.

1. The spec adaptor is separate from the operator pipeline.
2. The spec adaptor runs once per run.
3. The spec adaptor optionally adapts system specs to user prompt input.
4. If there is no user prompt, specs should pass through as-is.
5. The operator pipeline runs per game.
6. Games run in parallel with bounded concurrency.
7. The operator chain should become simpler and more generic.
8. Stage order/count should be easy to change later via config/prompt structure.
9. Special-case Python logic inside operator execution should be minimized or removed.

## Confirmed alignments

### Alignment 1 — spec adaptor is separate from the operator chain
**Status:** Confirmed alignment

**Code evidence:**
- `run_operator_pipeline_batch.py` invokes `spec_adaptor.py` before game worker launch
- `run_operator_pipeline_game.py` does not invoke the adaptor; it only reads adapted context from run state

**Meaning:**
Your architectural distinction is already real in the current code.

### Alignment 2 — spec adaptor is run-scoped, not game-scoped
**Status:** Confirmed alignment

**Code evidence:**
- adaptor output lives under `run_dir/spec_adaptor/`
- per-game workers reference adapted spec path from run state

**Meaning:**
The adaptor already behaves like a run-level subsystem.

### Alignment 3 — operator execution is game-scoped and sequential within a game
**Status:** Confirmed alignment

**Code evidence:**
- `run_operator_pipeline_game.py` resolves ordered operators and runs them stage by stage
- retries happen inside the current game worker for the current stage

**Meaning:**
The operator chain is indeed per-game.

### Alignment 4 — concurrency is across games
**Status:** Confirmed alignment

**Code evidence:**
- `run_operator_pipeline_batch.py` schedules one worker process per game up to `max_concurrency`

**Meaning:**
The current orchestration already matches your desired “parallel across games” model.

### Alignment 5 — stage order is already partially abstracted through config + prompts
**Status:** Confirmed alignment

**Code evidence:**
- `configs/operator_pipeline_v2.json`
- `scripts/operator_registry_v2.py`

**Meaning:**
The current system is already closer to manifest-driven execution than a fully hard-coded chain.

## Confirmed deltas

### Delta 1 — “optional adaptor” currently means skip-or-run, not adapt-or-pass-through bundle generation
**Status:** Confirmed delta

**Code evidence:**
- batch runner only invokes adaptor if remix prompt exists
- adaptor script itself requires `--remix-prompt`

**Meaning:**
Your intended model sounds like:
- with prompt → adapt
- without prompt → produce unchanged shared bundle

Current code does:
- with prompt → adapt
- without prompt → no adaptor workspace at all

This is a real architectural difference.

### Delta 2 — operator execution still contains stage-specific Python logic
**Status:** Confirmed delta

**Code evidence:**
- `run_operator_pipeline_game.py`
  - explicit special handling for `operator.id == "media_mapper"`
  - prompt packet embeds stage-specific media/font/icon policy instructions

**Meaning:**
The current runtime is not yet a fully generic stage executor.

### Delta 3 — current prompt-packet construction is heavily specialized
**Status:** Confirmed delta

**Code evidence:**
- `build_operator_prompt_text(...)` includes:
  - media-policy hints
  - replacement candidates
  - font/icon candidate lists
  - stage-specific failure criteria

**Meaning:**
Even though the registry/config abstracts stage order, the operator prompt assembly still strongly assumes the current stage semantics.

## Partial / needs more evidence

### Delta candidate 4 — retry logic may be too tied to current media/static-observation behavior
**Status:** Partial / needs more evidence

**Current evidence:**
- media policy scanning feeds operator prompt content
- `media_mapper` has explicit result override behavior based on remaining refs

**What still needs reading:**
- `scripts/media_policy.py`
- operator prompt files under `prompts/operators_v2/`

**Why not fully confirmed yet:**
We have enough evidence to say specialization exists, but not yet enough to fully map how much retry behavior is generic vs stage-specific across the whole chain.

### Delta candidate 5 — invariant contracts may not yet be cleanly separated from operator-local instructions
**Status:** Partial / needs more evidence

**Current evidence:**
- spec adaptor has clear invariant-vs-editable split
- game operator prompt packet injects many task-specific instructions directly

**What still needs reading:**
- system/spec/style/prompt files
- operator prompt files

## Preliminary interpretation

Based on code inspected so far, your intended architecture is **not fantasy**. Large parts of it already exist:

- separate run-level adaptor
- per-game sequential pipeline
- concurrency across games
- manifest/config-driven stage order

The main gap is not “the architecture is wrong.”  
The main gap is:

- the per-game operator executor is **not abstract enough yet**
- some stage semantics are still embedded in Python
- optional adaptor behavior is implemented as skip-or-run, not adapt-or-pass-through
- prompt packet construction is still highly tuned to the current remix/media workflow

## Safe next conclusions

These are the most defensible conclusions so far:

1. **Do not collapse spec adaptor into the operator chain.**  
   Current code already supports your separation instinct.

2. **The operator chain should be further abstracted, not rewritten from scratch.**  
   The registry/config foundation already exists.

3. **The biggest cleanup target is the game-stage executor and prompt assembly path.**  
   That is where current specialization remains strongest.

4. **We still need more evidence before changing retry semantics.**  
   Media-policy and prompt-layer inspection are still required.

## Next files to inspect before any behavioral proposal

- `scripts/media_policy.py`
- `prompts/operators_v2/01_gameplay_narrative.md`
- `prompts/operators_v2/02_visual_emoji_identity.md`
- `prompts/operators_v2/03_media_mapper.md`
- `prompts/operators_v2/04_final_code_ui_mobile_repair.md`
- `scripts/prepare_inputs.py`
- `scripts/run_parallel_batch.py`
- `scripts/run_single_game.py`

## Working summary

Current code says:

- your core separation between run-level spec adaptation and per-game operator execution is already mostly real
- the current pipeline is already partly manifest-driven
- the current executor is still too specialized to be called a clean general-purpose stage engine
- further claims about simplification should wait until prompt/media-policy and legacy-path evidence are added