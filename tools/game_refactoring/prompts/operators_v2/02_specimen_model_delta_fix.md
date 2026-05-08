# Node 2: Specimen Model-vs-Implementation Mental Simulation And Conservative Fix

Work only inside the provided workspace.

This node assumes node 1 already produced:
- `Blueprint.md`
- `Identity.json`
- the mechanics ranking
- the companion classification file
- the semantic tags file

Your job is to compare the abstracted model from node 1 against the actual implementation in the workspace, run written mental simulations of the gameplay flow, and apply only the smallest fixes justified by strong evidence of actual breakage.

## Main responsibilities

1. Read the analytical outputs from node 1.
2. Read the actual source files in the workspace.
3. Identify deltas between:
   - the inferred design / gameplay model
   - the actual implementation
4. Run mental simulations of the gameplay flow in writing.
5. Use ASCII-style sketches where useful to make the simulated flow legible.
6. Write out observations like an inner voice, for example:
   - "I see ..."
   - "I tap ..."
   - "I expect ..."
   - "This breaks because ..."
   - "A casual user would likely ..."
7. Build an issue ledger before editing anything.
8. Only apply focused minimal fixes for issues that are clearly broken or strongly evidenced.
9. Leave non-broken code alone.

## Core operating stance

Be conservative.

Your default assumption must be:
- the current implementation is acceptable unless there is strong evidence that something is actually broken

That means:
- do not proactively improve code that is already working
- do not rewrite for taste
- do not normalize style unless required for a concrete fix
- do not make speculative "better" behavior changes
- do not intervene just because the implementation differs from your preferred design
- if the evidence is weak, do not patch

## Issue ledger requirement

Before making edits, create a written issue ledger in the workspace named:

`delta_issue_ledger.md`

This artifact must include, for each candidate issue:

1. **Observed area**
   - file / feature / flow

2. **Evidence**
   - what specifically indicates the problem
   - code evidence
   - simulation evidence
   - contradiction with stage-1 inference, if relevant

3. **Confidence classification**
   - `confirmed`
   - `likely`
   - `uncertain`

4. **Proposed action**
   - `fix`
   - `leave_as_is`
   - `monitor_only`

5. **Why**
   - one short reason

### Edit policy tied to the issue ledger

- You may freely patch `confirmed` issues.
- You may patch `likely` issues only when the evidence is strong and the patch is minimal.
- You must not patch `uncertain` issues.
- If uncertain, document the concern and leave the code unchanged.

## Mental simulation requirement

You must explicitly simulate the likely player journey in writing.

That means:
- describe the screen/state you think the user sees
- describe the main action the user would take
- describe the expected transition
- describe where implementation and expectation diverge
- describe the likely user confusion or breakage
- then decide whether the divergence is truly broken or merely different

Use compact ASCII-style sketches if helpful to represent layout or state transitions.

## What counts as fix-worthy

Good reasons to intervene:
- obvious runtime-breaking defects
- broken event wiring
- dead buttons or dead actions
- impossible or contradictory state transitions
- missing handlers
- broken references
- clearly malformed logic that prevents expected play
- severe UX breakage strongly supported by evidence

Weak reasons that should usually be left alone:
- stylistic awkwardness
- architecture preference
- minor wording preference
- speculative polish
- “this could be cleaner”
- “I would have designed it differently”
- non-breaking deviations from the inferred model

## Minimal patch rule

When you do fix something:
- prefer the smallest possible patch
- patch the specific break, not the surrounding style
- avoid touching unrelated code
- do not bundle cleanup with the fix
- stop editing once the confirmed problem is addressed

## Audio safety guardrail

Treat looping or long-running audio as a hard safety constraint.

Rules:
- any looping background music, ambience bed, or other long-playing continuous audio must not exceed **20% volume**
- if you find looped or continuous music/audio above 20% volume, reduce it to 20% or lower
- do not increase looping or long-running music above 20% volume during any fix
- short one-shot sound effects are not automatically subject to this cap unless they are used as sustained loops or effectively function as background audio

If audio is otherwise working, do not redesign it beyond this safety rule.

## Requirements

- Do not perform a broad redesign.
- Do not depend on MCP or browser automation.
- Do not open an external/default browser.
- Do not rely on undeclared tooling outside the workspace unless strictly necessary for static/runtime inspection through normal local commands.
- Use the stage-1 artifacts as analytical context, not as unquestioned truth.
- Prefer concrete fixes to speculative rewrites.
- Make the written simulation part of the reasoning process, not just a final summary.
- Be evidence-first and conservative.
- If unsure, leave the code alone and document the uncertainty.

## Expected deliverables

By the end of this node, the workspace should contain:
- the original stage-1 inference artifacts
- the corrected implementation files, if any truly necessary fixes were made
- `delta_issue_ledger.md`
- clear written analytical artifacts or notes showing the simulated gameplay reasoning
- a short contract describing what delta(s) were fixed, if any

## Required contract artifact

Write a JSON file named `operator_result_contract.json` in the workspace.

If successful, write:

```json
{
  "status": "ok",
  "detail": "Ran a conservative evidence-first model-vs-implementation review, documented an issue ledger, and applied only minimal fixes for clearly broken behavior."
}
```

If no clearly justified code changes were needed, that is still a valid successful outcome as long as the issue ledger and reasoning are present.

## If blocked

If you cannot confidently identify and fix meaningful deltas, write:

```json
{
  "status": "error",
  "detail": "Could not complete the conservative model-vs-implementation fix pass reliably."
}
```

## Stdout contract

End stdout with exactly these lines:

```text
OPERATOR STATUS: completed|failed
CHANGED FILES: file1, file2 or NONE
SUMMARY: one short sentence
MECHANICS CHECK: preserved|issues
VISUAL CHECK: preserved|updated|issues
AUDIO CHECK: integrated|not_applicable|issues
MOBILE CHECK: safe|not_checked|issues
```
