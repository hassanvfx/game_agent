# Game Publish and Maintenance Workflow

## Purpose

This document explains which tool owns each stage of the game lifecycle in this repo, how to move from experimentation to publishing, and how to repair already-published outputs without mixing responsibilities.

It is intended as an operator-facing reference, not a low-level implementation spec.

---

## Tool ownership

### `tools/game_refactoring`

Use `game_refactoring` for **creative refactor / remix execution**.

It owns:
- run creation
- per-game operator orchestration
- status and result contracts
- run-local outputs under `runs/<run_id>`

Use it when you are:
- testing remix prompts
- running experimental transformation batches
- iterating on creative output quality
- producing candidate outputs before publish/deploy steps

Think of `game_refactoring` as the **upstream transformation layer**.

---

### `tools/game_generator`

Use `game_generator` for **observable end-to-end generation orchestration**.

It owns:
- higher-level generation runs
- orchestration across matcher / refactoring / publish layers
- durable run state and events
- pipeline dashboards and observers

Primary entrypoint:

```bash
python3 tools/game_generator/scripts/run_pipeline.py "your prompt"
```

Relevant flow flags include:
- `--publish`
- `--upload`
- `--matcher-mode`
- `--resume-from-run`

Use it when you want a fuller production-style run rather than a single isolated refactor experiment.

Think of `game_generator` as the **top-level orchestration layer**.

---

### `tools/game_publish_pipeline`

Use `game_publish_pipeline` for **publishing, deployment, reconciliation, materialization, validation, and sync**.

It owns:
- publish batch orchestration
- deployment into published roots
- obfuscation follow-up handling
- refresh/materialization of root artifact views
- published-output validation
- GCS sync helpers

Primary entrypoint:

```bash
python3 tools/game_publish_pipeline/scripts/publish_games.py --inputs /path/to/game-a /path/to/game-b
```

Think of `game_publish_pipeline` as the **operational publish/deploy layer**.

---

### `tools/game_editorial`

Use `game_editorial` for **deterministic editorial batch planning and launch preparation**.

It owns:
- deterministic raw-game selection / prompt assignment
- editorial manifest generation
- launch planning for sequential remix batches
- handing prepared manifests to `game_refactoring`

Use it when the question is not “how do I publish this?” but instead:
- which raw games should be processed next?
- how should prompt variants be assigned consistently?
- how should large editorial batches be staged?

Think of `game_editorial` as the **selection and planning layer**.

---

## Recommended mental model

Use this split:

- **Experiment / transform** → `game_refactoring`
- **Run a fuller observable pipeline** → `game_generator`
- **Publish / deploy / sync / validate** → `game_publish_pipeline`
- **Plan deterministic editorial batches** → `game_editorial`

That boundary keeps the repo understandable and avoids putting final publish responsibilities in upstream tools.

---

## High-level publish recipes

### 1. Experimental remix path

Use this when the goal is exploration first.

1. Start in `game_refactoring`
2. Run creative remix / operator workflows
3. Review the run-local outputs
4. Decide which outputs are worth pushing toward publish
5. Hand selected outputs into publish/deploy steps only after they are considered publish candidates

This path is best for R&D, prompt work, and quality iteration.

---

### 2. End-to-end generation path

Use this when the goal is a fuller orchestrated pipeline.

1. Start in `game_generator`
2. Run the main pipeline with the desired prompt
3. Let the generator orchestrate matcher/refactor/publish stages as configured
4. Review final outputs and run artifacts under the generator run directory
5. If needed, continue with publish-pipeline operational steps for targeted follow-up or repair

This path is best when you want observable pipeline execution and durable run records.

---

### 3. Publish / deployment path

Use this when outputs are ready to become published artifacts.

1. Use `game_publish_pipeline`
2. Build or load the deploy/publish input set
3. Run deploy + obfuscation + artifact refresh steps
4. Materialize final root artifact views
5. Validate final published state
6. Sync to GCS if needed

This path owns the final published representation under local `games/published/...` roots.

---

## Important architecture rule

### Final published-state validation happens after materialization

The authoritative validation point is **after root artifact materialization**.

That means:
- validation should **not** be treated as a refresh-only concern
- validation should run against the **actual root published `app.json`**
- validation must compare that root catalog against the **real published folder state**

Operationally, this means the final correctness check belongs with the materialized root view, not with intermediate refresh logic.

### Why this matters

Before materialization, you may still be looking at intermediate or partially assembled state.

After materialization, you are checking the real published root view that downstream consumers depend on.

That is the correct place to ask:

> “Does the final root `app.json` match the actual published public/obfuscated outputs?”

---

## Published state concepts

The publish layer ultimately cares about:
- `games/published/public`
- `games/published/obfuscated`
- root artifacts such as `app.json`, `index.json`, `app_tags.json`, and related dashboards

The publish lifecycle is easiest to reason about as:

1. **deploy / publish** creates or updates concrete outputs
2. **materialize** assembles the root artifact view
3. **validate** confirms the root artifact view matches real files
4. **sync** mirrors the intended trees to remote storage if needed

---

## Maintenance recipe

Use this flow when published content already exists and something needs repair.

### Example: fixing audio problems

1. Fix the source problem first
   - repair the asset
   - repair metadata or mappings
   - regenerate the asset if required

2. Identify the affected published scope
   - public only
   - obfuscated only
   - both

3. Remove or replace affected published outputs as needed
   - in many cases the obfuscated side is the main republish target after a repaired build is produced

4. Re-publish the affected items

5. Re-materialize the root views **if the root published catalogs must reflect the repair**

6. Re-validate the final published state

7. Re-sync to GCS if the remote mirror should match the repaired local state

---

## When re-materialization is required

Do not think of materialization as “something to run after every tiny file touch.”

Instead, ask:

> “Do I need the root published artifact view to reflect the repaired or changed published set?”

If yes, re-materialize.

Typical reasons to re-materialize:
- the set of published items changed
- root `app.json` / `index.json` / `app_tags.json` should be refreshed
- cleanup removed published items and the root catalog must drop them
- repaired items should now appear correctly in the root artifact view

---

## Sync / GCS guidance

`game_publish_pipeline` also provides practical sync operations.

Use it when you need to sync:
- a public tree
- an obfuscated tree
- both trees
- targeted subsets / per-item publish results

Important nuance:
- sync behavior is operational convenience
- sync is not the same as validation
- sync should follow the local state you intend to preserve

In practice, this makes `game_publish_pipeline` the last-mile operations tool even when the work started in `game_refactoring` or `game_generator`.

---

## Editorial follow-up

After publish/deploy work, editorial-side follow-up may still be needed.

That is where `game_editorial` fits.

Typical editorial-side work includes:
- building deterministic remix manifests
- planning large sequential batches
- auditing what should be processed next
- preparing curated launch sets for downstream review or operations

So a broader lifecycle may look like:

1. create / remix
2. publish / deploy
3. materialize / validate
4. sync if needed
5. perform editorial planning or downstream batch selection

---

## Practical operator cheat sheet

- **Need experimental remixing?** → use `tools/game_refactoring`
- **Need a fuller observable generation flow?** → use `tools/game_generator`
- **Need to publish, deploy, materialize, validate, or sync?** → use `tools/game_publish_pipeline`
- **Need deterministic editorial batch planning?** → use `tools/game_editorial`
- **Need to repair published content?** → fix source, republish affected items, re-materialize if root views must change, then validate
- **Need the final correctness check?** → validate after materialization on the real root published `app.json`

---

## Summary

The cleanest way to reason about the repo is:

- upstream creative work belongs in `game_refactoring`
- top-level observable orchestration belongs in `game_generator`
- final published truth belongs in `game_publish_pipeline`
- editorial selection and deterministic planning belong in `game_editorial`

And for published-state correctness:

**materialize first, validate second**.