# Evidence-First Refactor Process

This document defines the working process for large refactor, cleanup, and repurposing tasks in `game_refactoring`.

It exists to reduce assumption-driven mistakes and preserve a stable audit trail while the repository is being re-understood and gradually reshaped.

## Purpose

The repository is large, historically layered, and partially transitional.

That means memory, intuition, and first impressions are not reliable enough for major edits.

The working rule for this repo is:

**measure 3 times, edit once**

More concretely:

- code is current evidence
- docs are structured observation logs
- both may be wrong and must be re-evaluated
- no broad changes should be made from assumption
- every major change should be grounded in inspected files and written observations

## Core operating principles

### 1. Code is evidence, not memory
When a claim matters, verify it against the actual code path instead of relying on:
- previous conversations
- remembered architecture
- existing documentation alone
- naming assumptions

### 2. Docs are mutable observation logs
Documentation should be treated as:
- structured external memory
- correction-friendly
- revisable as new evidence appears

Docs are not sacred truth. They should be updated when code evidence contradicts them.

### 3. Confidence must be explicit
For architecture and behavior claims, use labels such as:
- **Confirmed**
- **Unconfirmed**
- **Unknown**

When useful, also record:
- evidence source files
- interpretation
- open questions
- risks if wrong

### 4. Smallest safe change only
Do not make large sweeping edits when a smaller validated change can achieve the goal.

Prefer:
- one subsystem at a time
- one boundary at a time
- one risk surface at a time

### 5. Re-evaluate constantly
Assume both the operator and the human may be wrong at times.

That means:
- revisit earlier conclusions
- update docs when contradictions appear
- ask for clarification when architecture could be interpreted in multiple ways
- treat all understanding as provisional until sufficiently evidenced

## Required sequence for major work

For large cleanup, architecture, or repurposing work, follow this order.

### Phase 1 — Evidence extraction
Read the narrowest files that define actual control flow and state transitions.

Goal:
- extract facts only
- avoid design conclusions too early

Outputs:
- notes or code-fact docs

### Phase 2 — Code-facts documentation
Write explicit code-grounded observation docs.

Recommended section structure:
- Observation
- Status
- Evidence
- Interpretation
- Open questions

Outputs may include:
- runtime flow facts
- spec adaptor facts
- operator pipeline facts
- media-policy facts
- legacy path facts

### Phase 3 — Intent vs reality comparison
Compare the intended architecture to the code facts.

Required distinctions:
- confirmed alignment
- confirmed delta
- partial / needs more evidence

Do not jump directly from intent to code changes.

### Phase 4 — Dry-run and validation design
Before changing worker behavior or prompt guidance, define a dry-run strategy that can validate orchestration without depending on the agent.

This should separate:
- run-level behavior
- per-game orchestration
- worker invocation
- state/artifact writing

### Phase 5 — Minimal implementation
Only after the evidence docs and dry-run plan exist should implementation begin.

Start with:
- the smallest useful non-destructive change
- the smallest validation slice
- the lowest-risk abstraction step

### Phase 6 — Re-validate after every change
After each implementation step:
- inspect outputs
- verify state transitions
- update docs
- record deltas
- revise next steps

## Documentation requirements per major pass

Each major pass should produce or update some combination of the following:

### 1. Journal entry
Update the active task journal with:
- what was read
- what was changed
- why
- what remains uncertain
- next steps

### 2. Code-facts docs
Examples:
- `docs/code_facts_runtime_flow.md`
- `docs/code_facts_spec_adaptor.md`

These should stay evidence-oriented and low-assumption.

### 3. Delta docs
Example:
- `docs/intent_vs_code_deltas.md`

These compare intended architecture against observed code behavior.

### 4. Risk or next-step docs
Examples:
- dry-run plans
- migration delta docs
- quarantine manifests
- runtime naming audits

## Editing rules

### Allowed early
- documentation cleanup
- evidence docs
- taxonomy and quarantine docs
- naming audits
- non-behavioral classification work

### Delayed until validated
- behavior-sensitive refactors
- code symbol renames
- runtime identifier changes
- prompt contract changes
- retry logic changes
- orchestration changes

### Avoid
- assumption-based bulk edits
- architecture rewrites from memory
- deleting “suspicious” directories before dependency validation
- blending historical artifacts with current canonical docs

## Dry-run policy

Dry-run exists to isolate orchestrator correctness from worker correctness.

### Dry-run should validate
- run creation
- input preparation
- run/game state transitions
- bounded concurrency scheduling
- stage ordering
- attempt artifact layout
- promotion flow
- dashboard/launcher integration

### Dry-run should not pretend to validate
- worker intelligence
- prompt quality
- creative transformation quality
- media mapping quality
- final gameplay correctness

### Preferred separation
Dry-run design should distinguish:
- run-level spec-adaptor bypass/simulation
- per-game operator-stage bypass/simulation

That preserves the existing architecture boundary between:
- shared run-scope preparation
- per-game stage execution

## Architecture-boundary rule

The current working architectural rule is:

### Run-level scope
- run creation
- input preparation
- optional spec adaptation
- shared bundle creation
- run-level status and orchestration

### Game-level scope
- per-game workspace execution
- ordered stage chain
- retries within stage boundaries
- promotion from stage workspace to current workspace
- final game output generation

These scopes should not be casually collapsed together.

## Decision protocol when uncertainty remains

If a question materially affects architecture, safety, or compatibility:

1. record the uncertainty in docs
2. identify the exact files that could answer it
3. inspect those files before editing
4. if ambiguity still remains, ask the user for help
5. do not force a guess into code

## What success looks like

A successful large refactor process in this repo should produce:

- a trail of concrete observations
- explicit deltas between intent and implementation
- smaller, safer edits
- fewer accidental regressions from assumption
- docs that improve with each correction instead of pretending to be final from the start

## Short operating checklist

Before editing:
- [ ] Have the relevant control-flow files been read?
- [ ] Are the important claims documented as confirmed/unconfirmed/unknown?
- [ ] Is the intended change supported by actual code evidence?
- [ ] Is this the smallest safe change?
- [ ] Do we need a dry-run or simulation first?

After editing:
- [ ] Was the effect verified?
- [ ] Were the observation docs updated?
- [ ] Was the journal updated?
- [ ] Were new uncertainties recorded instead of ignored?

## Current implication for this repo

For the current `game_refactoring` effort, this process means:

- keep building code-fact docs
- design dry-run before major worker/orchestrator edits
- preserve the run-level spec adaptor boundary unless evidence proves otherwise
- simplify the per-game operator chain only after its current specialization is fully mapped
- prefer manifest/prompt abstraction over new hard-coded Python stage semantics