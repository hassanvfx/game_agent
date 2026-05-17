<!-- REMIX V4 CLONE PRODUCTION PROMPT -->
# Remix v4 Clone — Stage 1 — Rebuild From Blueprint And Old References

You are performing the new clone-only rebuild step for `remix-v4-clone`.

This step runs **after** `clone_remix_inference_plus`.

## Prime directive

Build a new, stable, original game surface while preserving mechanic truth.

Your output should be:

- more original than the old source
- mechanically grounded in the upstream blueprint
- stability-first in architecture and implementation choices
- explicitly checked against the preserved old reference before risky rewrites land

## Inputs you must treat as authoritative

Use the outputs of `clone_remix_inference_plus` first:

- mechanic decomposition
- protected mechanics
- safe theming surfaces
- complexity profile
- remix premise
- 1.5-level core definition
- five-level progression intent
- procedural visual identity
- any `remix_plan_v4.json` or equivalent planning artifact

The blueprint and mechanic analysis are the main source of truth for this step.

## Hard delivery constraint — single rebuilt public surface

The new game must be delivered primarily through a **single rebuilt public `index.html`**.

Required:

- the new public `index.html` is the canonical rebuilt surface
- all newly authored application code should be written inline in that same `index.html` whenever feasible
- inline CSS in the rebuilt `index.html`
- inline JavaScript in the rebuilt `index.html`
- prefer a self-contained rebuilt surface over a scattered new file graph

Allowed exceptions only when truly justified by stability:

- existing local assets already required by the source game
- media selected from approved catalogs
- carefully chosen external OSS CDN libraries when they materially improve stability or execution quality

If you use an external library, justify it briefly in your planning notes before implementation.

## Engine/library selection rule

Before implementation, choose the most stable practical runtime approach for the job.

Examples that may be appropriate depending on the game:

- plain JavaScript + DOM/CSS
- Canvas + plain JavaScript
- Phaser from a stable CDN
- jQuery for light DOM/state glue
- a small combination of the above when justified

Selection criteria in order:

1. stability
2. mechanic fidelity
3. implementation clarity
4. ease of testing and repair
5. originality/expressiveness

Do not choose a heavier engine or library just because it is fashionable.

## Approved media/library sources

You may use:

- approved local audio catalogs
- approved local GIF/media catalogs
- popular open-source CDN libraries when stability and maintainability benefit

Do not introduce random, obscure, fragile, or poorly supported dependencies.

If stability is in doubt, prefer simpler technology.

## Mission

Using the upstream blueprint:

1. preserve the old runnable source under `_old` names
2. create a new public implementation surface
3. begin building an entirely new game from the blueprint/mechanics analysis
4. keep the `_old` files as reference-only fallback material

## Mandatory pre-build planning pass

Before you start creating the new public `index.html`, first produce a short implementation plan in the workspace describing how the blueprint and known mechanics interact with the old reference.

That plan must:

- cite relevant old code pieces when identifiable
- name the mechanic surfaces that matter most
- explain how the blueprint maps onto those mechanic surfaces
- identify what is fragile
- identify what is easy to update safely
- identify what should not be touched conceptually
- note where `_old` reference checks are required before rewriting

At minimum, the plan should comment on:

- player input/control handling
- movement/update loop
- collision/hit detection
- scoring/progression signals
- fail/win state handling
- UI/HUD surfaces
- media/asset wiring

This planning pass should exist before the main rebuild work proceeds.

## Required sequence

### A. Preserve old runtime surfaces

1. Find the current public entrypoint, especially `index.html`.
2. Rename it to an `_old` form.
   - Prefer `index_old.html`.
3. Inspect that preserved HTML and rename directly linked **local** CSS/JS files into `_old` forms too.
   - Prefer `styles_old.css`, `game_old.js`, etc.
4. Update the preserved HTML so it still resolves correctly against the renamed `_old` assets.

### B. Establish the new public surface

5. Create or overwrite a fresh public `index.html` as the new canonical implementation surface.
6. Start building the new game from the upstream blueprint rather than patching the old source in place.
7. Prefer newly authored structure, UI, art systems, scene construction, and code paths when safe.
8. Keep the rebuilt implementation inline in the same new `index.html` unless a clearly justified stability reason prevents it.

### C. Reference-only old surfaces

9. Treat `_old` files as evidence/reference only.
10. Inspect them only when:
   - mechanic behavior is ambiguous
   - edge-case expectations are unclear
   - you need to avoid accidental mechanic drift

### D. Component-by-component verification during rewrite

11. For each rewritten component or mechanic-facing subsystem, compare it against the old reference before finalizing.

This includes, where relevant:

- control/input behavior
- animation/update timing
- collision/contact behavior
- score/progress reporting
- fail/win transitions
- HUD feedback

If a rewritten component is more original but less stable, less testable, or mechanically less truthful, revise it.

## Rules

- Do not let `_old` files remain the main implementation surface.
- Do not anchor the rebuild around editing `_old` files.
- Do not delete the old source.
- Do not rename remote/CDN URLs.
- Rename only directly linked local CSS/JS assets you can trace safely.
- Use blueprint and mechanic analysis as the first decision source; use `_old` files only as fallback clarification.
- Stability is more important than flashy technology choices.
- Originality matters, but not at the cost of breaking gameplay.
- Every major rebuilt subsystem should be explainable in terms of the blueprint and the old mechanic truth.

## Testing plan requirement

You must follow a compact testing plan while rebuilding.

At minimum, test:

- boot/load success
- start/play flow
- active gameplay loop
- primary controls
- collision/hit behavior where relevant
- score/progress updates where relevant
- fail/win/restart behavior where relevant
- mobile-sized usability/readability

Record what was checked and what still feels fragile.

## Suggested artifacts

If feasible, write:

- `clone_surface_map.json`
  - old path
  - new `_old` path
  - role (`entry_html`, `css`, `js`)
  - reference-only flag
- `clone_rebuild_notes.md`
  - what was preserved
  - what new public surface was created
  - where `_old` references were actually needed
- `clone_rebuild_plan.md`
  - blueprint/mechanics/reference interaction plan
  - fragile surfaces
  - easy-update surfaces
  - do-not-touch conceptual surfaces
  - chosen engine/library approach and rationale
- `clone_rebuild_test_plan.md`
  - what was tested
  - what passed
  - what remains risky

## Success condition

This stage succeeds when:

- clone inference has already defined the blueprint
- a pre-build plan exists describing how blueprint, mechanics, and old references interact
- the old runtime has been preserved under `_old` naming
- a new public `index.html` exists as the canonical surface
- the new game has begun as a blueprint-driven rebuild
- `_old` files are clearly demoted to reference-only status
- the rebuilt surface is stability-oriented, mechanically checked, and guided by an explicit testing plan
