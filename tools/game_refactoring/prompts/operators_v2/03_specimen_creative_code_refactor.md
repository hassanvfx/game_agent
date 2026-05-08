# Node 3: Specimen Creative Code Refactor

Work only inside the provided workspace.

This node assumes the earlier stages already:
- inferred the game and codebase
- identified/fixed the main model-vs-implementation deltas

Your job is to perform a playful, harmless, creative refactor of the code.

## Goal

Make the code visibly different at the source level while preserving the actual operational behavior.

This is not a bug-fix stage and not a redesign stage.
It is a controlled creative refactor stage.

## Desired character

Be:
- playful
- a bit naive
- a little creative
- visibly different in code texture
- but functionally equivalent

## Primary requirement

You must be much stricter than a light touch-up.

The main transformation goal is:
- change the internal code-level language across the editable codebase into explicit **espanol mexicano de barrio/rancho**
- use Mexican-Spanish synonym-based replacements for variables, functions, helpers, temporary names, and other developer-facing identifiers
- avoid mixed partial renaming where only a few names change and the rest stay in the old naming language
- keep all renamed identifiers ASCII alphanumeric only, with no accents, no enye, and no non-ASCII characters

In other words:
- do not rename just a few scattered symbols
- do not do shallow cosmetic swaps
- perform a broad, coherent internal identifier rewrite wherever it is safe

## Mandatory two-phase process

You must do this in two phases.

### Phase 1: Build a rename plan first

Before applying broad renames, create a planning artifact in the workspace named:

`rename_map_reference.md`

This file must be an analytical reference used before the main rename pass.

It must include clearly separated sections for:

1. **Target naming direction**
   - state the source naming tendency you observed
   - state the target naming tendency you will apply
   - the target naming direction must be explicit: **espanol mexicano de barrio/rancho**
   - all proposed renamed identifiers must stay ASCII alphanumeric only
   - use readable Mexican-Spanish wording with sabor, but keep it technically stable

2. **High-order vocabulary map**
   - list the higher-order domain words first
   - include proposed replacements for major gameplay / UI / state concepts
   - prefer coherent vocabulary families over random one-off substitutions

3. **Safe symbol rename map**
   - enumerate specific internal symbols you intend to rename
   - include old name -> new name
   - include a short reason
   - favor simple readable replacements

4. **Protected / do-not-rename symbols**
   - list names that must remain unchanged because they appear externally referenced or contract-sensitive

5. **Collision and ambiguity review**
   - detect collisions, near-collisions, misleading synonym choices, or replacements that would reduce clarity
   - resolve them in the map before the main edit pass

6. **Rejected rename candidates**
   - symbols considered but intentionally skipped
   - include a short reason for skipping

7. **Linked local file cluster scope**
   - identify each HTML entry file you are using as a rename anchor
   - list all locally linked CSS and JS files referenced from that HTML
   - treat that connected local HTML/CSS/JS set as one rename scope
   - note any linked files intentionally excluded because they are third-party, vendor, generated, or otherwise unsafe to rename

You must use this file as the source of truth for the final rename pass.

## Rename strategy requirements

When constructing the rename map and applying the refactor, follow these rules:

- rename higher-order words first, then lower-level symbols
- use whole-identifier replacements, not blind substring replacements
- prefer semantically appropriate Mexican-Spanish synonyms, not random dictionary swaps
- keep one old concept mapped to one consistent new concept
- favor simple replacements over clever ones
- avoid silly or ambiguous renames if a clearer Mexican-Spanish synonym exists
- preserve readability
- keep naming internally consistent within each file and across related files when safe
- if a replacement would create a collision or unclear distinction, choose a simpler safer name
- if a symbol is only partially safe to rename, skip it and document why in the rename map
- start from the HTML entry file(s), discover all locally linked JS and CSS files, and treat that connected local file set as a shared rename scope
- apply one consistent rename map across the entire linked local HTML/CSS/JS cluster rather than renaming each file in isolation
- when a CSS class, id, custom property, JS hook, or shared developer-facing symbol is intentionally renamed, update all affected linked local files consistently and safely
- all renamed developer-facing identifiers must use ASCII alphanumeric characters only
- do not use accents, enye, unicode stylization, or punctuation-heavy joke names in identifiers
- keep the tone mexicano de barrio/rancho, but if a slangy option becomes confusing or unstable, prefer a cleaner Mexican-Spanish synonym

## What to rename aggressively when safe

Across the codebase, strongly prefer renaming these when they are internal and safely editable, translating them into consistent ASCII-only Mexican-Spanish naming:

- local variables
- local constants
- helper functions
- private/internal functions
- temporary objects and arrays
- loop variables with meaningful names
- internal state containers
- internal configuration variable names
- developer-facing intermediate names

Also apply harmless code-texture refactors such as:
- reorder harmless declarations
- split obvious expressions into slightly more explicit steps
- combine obvious expressions into slightly more abstract forms
- introduce tiny harmless refactor texture
- keep the code readable and intentional

## Target naming style

The target rename language is not ambiguous.

Use:
- **espanol mexicano de barrio/rancho**
- ASCII alphanumeric identifiers only
- readable Mexican-Spanish developer-facing wording
- consistent symbolic translation across the full safe rename scope

Allowed flavor:
- barrio / rancho sabor
- colloquial Mexican-Spanish energy
- playful names with attitude

Not allowed for identifiers:
- accents
- `ñ`
- unicode script variants
- inconsistent half-English leftovers when a safe Mexican-Spanish rename exists
- names so slangy that they become hard to understand or collision-prone

If a stronger albur/joke term would reduce clarity, choose the cleaner cabron-but-readable Mexican-Spanish option instead.

## Linked local HTML/CSS/JS cluster rule

You must explicitly inspect the HTML entry file(s) in the workspace and identify all locally linked CSS and JS files referenced from those HTML files.

Rules:
- local linked CSS and JS files referenced by the HTML must be considered part of the same creative rename scope
- perform cross-file renaming consistently across that linked local cluster
- do not treat those linked local files as isolated rename targets if they clearly participate in one shared UI/runtime surface
- use the rename map to track cross-file symbol usage before editing

Do **not** extend this scope to:
- external CDN resources
- third-party/vendor files
- remote URLs
- generated/minified bundles unless you are certain they are intended local editable source files

## What must be treated as protected unless proven safe

Do **not** rename these blindly:

- browser / platform API names
- library / framework API names
- DOM APIs
- event names
- CSS selectors that may be externally referenced
- HTML ids/classes that may be externally referenced
- linked selectors, classes, ids, hooks, or naming surfaces that span local HTML/CSS/JS files unless all linked local references are updated consistently
- filenames
- asset paths
- URLs
- import/export names that may be consumed elsewhere
- JSON schema / contract fields
- serialized storage keys
- message names
- object keys used dynamically
- public / externally referenced symbols

For these categories, only rename if you can prove the rename is safe everywhere it matters inside the workspace.

## Guardrails

You must preserve:
- gameplay behavior
- control flow meaning
- data flow meaning
- user-facing functionality
- file structure assumptions unless a tiny safe adjustment is needed

Do **not**:
- introduce logic drift
- change mechanics
- change schemas
- obfuscate the code
- make the code harder to understand
- rewrite the whole project into a different architecture
- do dumb search/replace mutations
- perform substring swaps that corrupt words, selectors, APIs, or contracts

## Important success condition

You should be able to say all of the following:

- the code looks different
- the code feels reworked
- the internal naming language was broadly transformed
- the rename map was checked before applying edits
- but in reality the operational meaning remains the same

## Use prior artifacts

Use the outputs from previous stages as rails:
- `Blueprint.md`
- `Identity.json`
- mechanics ranking / companion classification
- any delta-analysis artifacts

These are there to help ensure the refactor stays on-behavior.

## Required artifacts

You must write both:

1. `rename_map_reference.md`
2. `operator_result_contract.json`

## Required contract artifact

Write a JSON file named `operator_result_contract.json` in the workspace.

If successful, write:

```json
{
  "status": "ok",
  "detail": "Applied a broad but safe creative code refactor using a checked rename map and behavior-preserving identifier transformations."
}
```

## If blocked

If you cannot refactor safely without risking behavior drift, write:

```json
{
  "status": "error",
  "detail": "Could not apply the planned identifier-language refactor safely after reviewing collisions, external contracts, or unsafe rename boundaries."
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
