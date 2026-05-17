from pathlib import Path
from textwrap import dedent


def replace_once(text: str, old: str, new: str, label: str) -> str:
    if old not in text:
        raise RuntimeError(f"Missing expected text for {label}")
    return text.replace(old, new, 1)


def patch_semantic_prompt() -> None:
    path = Path("tools/game_refactoring/prompts/operators_v2/00_creative_remix_v6_semantic_inference_plus.md")
    text = path.read_text()

    text = replace_once(
        text,
        """<!-- CREATIVE REMIX V4 PRODUCTION PROMPT -->
<!-- This file is new v4 material. Existing v3/v1 source prompts remain source-only and are not modified. -->
<!-- Generated: 2026-05-09T07:01:09.236175Z -->""",
        """<!-- CREATIVE REMIX V6 SEMANTIC INFERENCE PLUS -->
<!-- Adapted for creative_remix_v6 semantic-first regeneration. -->
<!-- Updated: 2026-05-17T02:19:00-06:00 -->""",
        "semantic header",
    )
    text = replace_once(
        text,
        "# Creative Remix v4 — Stage 0 — Remix Inference Plus",
        "# Creative Remix v6 — Stage 1 — Semantic Inference Plus",
        "semantic title",
    )
    text = replace_once(
        text,
        "This stage must output a planning contract that downstream v4 stages can obey without needing a separate level adapter.",
        "This stage must output a planning contract that the downstream v6 regeneration stage can obey without needing preserved runtime references.",
        "semantic stage purpose",
    )
    text = replace_once(
        text,
        """Write a compact contract for later v4 stages:

- what Stage 1 must preserve and execute
- what Stage 2 must draw/build
- what Stage 3 must refine
- what Stage 4 must verify and repair""",
        """Write a compact contract for the later v6 regeneration stage:

- what this semantic stage established as mechanic truth and target identity
- what the super operator must rebuild from semantic abstraction alone
- what runtime surfaces are intentionally disposable
- what regeneration risks must be verified and repaired""",
        "semantic downstream contract",
    )

    tail_marker = """<!-- ====================================================================== -->
<!-- SOURCE: 10_creative_remix_v3_level_adapter.md -->
<!-- ====================================================================== -->"""
    idx = text.find(tail_marker)
    if idx == -1:
        raise RuntimeError("Missing semantic tail marker")

    replacement_tail = dedent(
        """
        ## Remix v6 Semantic Handoff and Destructive Regeneration Contract

        This semantic node is the last abstraction/planning pass before the v6 super operator rebuilds the runtime.

        It is **not** a level-adapter stage and it is **not** a preservation stage.

        Its job is to:
        - analyze the source truthfully
        - write the semantic/regeneration artifacts that define the intended remixed result
        - preserve mechanic truth in artifacts rather than in legacy runtime files
        - intentionally sever dependence on the original public runtime surface before the next stage begins

        ## v6-specific non-negotiables

        - Do not create `index_level_*.html` variants in this node.
        - Do not preserve the current `index.html` as a canonical runtime output of this node.
        - Do not assume the next stage should inherit the current `assets/` directory unchanged.
        - Do not generate a replacement playable runtime surface here just to keep the old implementation alive.
        - The super operator that follows must regenerate from semantic abstraction alone.

        ## Required semantic handoff artifacts

        At minimum this node must leave the workspace with aligned regeneration artifacts such as:
        - `Blueprint.md`
        - `Identity.json`
        - `RecreationPrompt.md`
        - `RemixDelta.md`
        - mechanics ranking / companion classification outputs if requested by the stage contract
        - semantic tags output
        - `operator_result_contract.json`

        These artifacts are the authoritative handoff for downstream regeneration.

        ## Destructive runtime-surface handoff rule

        After the semantic artifacts are written, intentionally demote the original runtime surfaces so the next stage cannot depend on them.

        If present in the current workspace:
        1. rename `index.html` to `index_trash.html`
        2. rename `assets/` to `assets_trash/`

        If original or baseline screenshots are kept only temporarily and are intentionally non-canonical, rename each one to `*_trash.<ext>` so cleanup can remove it after success.

        Important consequence:
        - successful stage completion triggers runtime cleanup that deletes `*_trash.*` files and `*_trash/` directories before the next stage workspace is promoted
        - this means the original `index.html`, original `assets/`, and any deliberately trashed baseline screenshots will be gone before the super operator starts
        - this deletion is intentional

        ## Downstream expectation contract for the super operator

        The downstream super operator must assume:
        - semantic artifacts are the source of truth
        - mechanic truth is documented in artifacts, not preserved via legacy runtime files
        - the original public runtime surface may already be removed
        - any rebuilt `index.html` and any rebuilt assets must be freshly authored canonical outputs

        ## Output requirements for v6 semantic handoff

        Write a JSON file named `operator_result_contract.json` in the workspace.

        Minimum required shape:
        ```json
        {
          "status": "ok",
          "detail": "Generated semantic regeneration artifacts and intentionally trashed legacy runtime surfaces so downstream v6 regeneration rebuilds from semantic abstraction.",
          "semantic_regeneration_ready": true,
          "trashed_runtime_surfaces": ["index.html", "assets/"]
        }
        ```

        Allowed `status` values:
        - `ok`
        - `warning`
        - `error`

        Use:
        - `ok` when the semantic artifacts are coherent and any legacy runtime surfaces that existed were intentionally trashed for cleanup
        - `warning` when the semantic artifacts are usable but one or more expected runtime surfaces were absent or only partially demoted
        - `error` when the semantic artifacts are not reliable enough for downstream regeneration
        """
    ).strip()

    text = text[:idx].rstrip() + "\n\n" + replacement_tail + "\n"
    path.write_text(text)


def patch_super_operator() -> None:
    path = Path("tools/game_refactoring/prompts/operators_v2/00_creative_remix_v6_super_operator.md")
    text = path.read_text()

    replacements = [
        (
            "<!-- Generated from Remix v6 skill catalogs + direct clone rebuild phase (v6 wiring variant). -->",
            "<!-- Generated from Remix v6 skill catalogs + direct semantic regeneration phase. -->",
            "super header",
        ),
        (
            """This operator reconciles two upstream truths:
- the non-clone v4 expert creator stack: forensic game analysis, mechanic-aware authored world design, procedural/browser-native technical art direction, and ruthless mobile-first evidence-driven QA
- the clone rebuild kernel: blueprint-first regeneration, `_old` as evidence-only legacy, a new canonical public surface, stability-first implementation selection, subsystem-by-subsystem verification, and explicit testing discipline

These are not competing ideas. The clone rebuild kernel is the regeneration spine. The non-clone v4 stack is the intelligence wrapped around that spine.""",
            """This operator reconciles two upstream truths:
- the non-clone v4 expert creator stack: forensic game analysis, mechanic-aware authored world design, procedural/browser-native technical art direction, and ruthless mobile-first evidence-driven QA
- the semantic regeneration kernel: blueprint-first regeneration, semantic abstraction as the authoritative brief, a freshly rebuilt canonical public surface, stability-first implementation selection, subsystem-by-subsystem verification, and explicit testing discipline

These are not competing ideas. The semantic regeneration kernel is the regeneration spine. The non-clone v4 stack is the intelligence wrapped around that spine.""",
            "super reconciliation doctrine",
        ),
        (
            "- Phase 1 prepares the rebuild kernel with source truth and planning contracts.",
            "- Phase 1 prepares the semantic regeneration kernel with source truth and planning contracts.",
            "super phase relationship",
        ),
        (
            "- run the direct rebuild phase that preserves `_old` runtime references and creates a new canonical public surface",
            "- run the direct regeneration phase that rebuilds from semantic artifacts and creates a new canonical public surface",
            "super execution phases",
        ),
        (
            "- The rebuild / `_old` preservation phase lives directly in this prompt, not in a skill catalog.",
            "- The regeneration phase lives directly in this prompt, not in a skill catalog.",
            "super non-negotiable regeneration phase",
        ),
        (
            "- Every major transformation should be explainable in terms of source truth, rebuild doctrine, and runtime evidence.",
            "- Every major transformation should be explainable in terms of source truth, semantic regeneration doctrine, and runtime evidence.",
            "super doctrine wording",
        ),
        (
            """## `_trash` Lifecycle Contract (Single Deletion Convention)

- Use `_trash` for anything explicitly deletable.
- File pattern: `*_trash.*` (examples: `index_trash.html`, `game_trash.js`, `screen_intro_trash.png`).
- Directory pattern: `*_trash/` (example: `assets_trash/`).
- Apply this contract to obsolete surfaces **and** original-version screenshots that are intentionally non-canonical.
- Do not mix delete-marker conventions for explicit deletion (for example, avoid ad-hoc suffixes).
- The runtime post-step cleanup deletes `*_trash.*` files and `*_trash/` directories before workspace promotion on successful stage completion.""",
            """## Original Screenshot Cleanup Rule

- If original input screenshots or other baseline screenshot captures are kept only temporarily for comparison, rename them to `*_trash.<ext>` once they are no longer needed.
- This explicit rename rule exists so runtime cleanup removes non-canonical screenshot evidence after a successful stage.
- Do not treat original screenshots as live runtime dependencies or as canonical deliverables of the rebuilt game.""",
            "super screenshot cleanup rule",
        ),
        (
            "- Phase 2: Direct rebuild phase (the regeneration spine: preserve old runtime / create new canonical surface)",
            "- Phase 2: Semantic regeneration phase (the regeneration spine: rebuild from semantic abstraction / create new canonical surface)",
            "super phase layout",
        ),
        (
            """**Notes:**

- Rebuild and _old-surface preservation are intentionally excluded from skill catalogs and belong to the direct super-prompt phase flow.
- These skills define how the operator must behave while applying analysis, world, visual, media, and QA skills.""",
            """**Notes:**

- Regeneration-phase implementation details are intentionally excluded from skill catalogs and belong to the direct super-prompt phase flow.
- These skills define how the operator must behave while applying analysis, world, visual, media, and QA skills.""",
            "super notes",
        ),
        (
            "- the direct rebuild phase has preserved `_old` surfaces and created a new canonical public surface",
            "- the semantic regeneration phase has rebuilt a new canonical public surface from semantic artifacts rather than preserved runtime references",
            "super completion standard",
        ),
    ]
    for old, new, label in replacements:
        text = replace_once(text, old, new, label)

    start = text.find("## Phase 2 — Direct Rebuild Phase (Regeneration Spine, Non-Catalogized)")
    end = text.find("## Phase 3 — Authored World, Design-System, and Media Mapping")
    if start == -1 or end == -1 or end <= start:
        raise RuntimeError("Could not locate Phase 2 block for super operator")

    new_phase_2 = dedent(
        """
        ## Phase 2 — Semantic Regeneration Phase (Regeneration Spine, Non-Catalogized)

        This phase is the regeneration spine of the workflow. Phase 1 prepares a semantic abstraction of the game. Phases 3–5 enrich, realize, and prove the rebuilt surface. This phase is intentionally **not** represented as a skill catalog.

        The semantic regeneration phase owns fresh canonical `index.html` creation, blueprint-first regeneration, semantic-artifact propagation, subsystem-by-subsystem mechanic verification, and stability-first runtime selection.

        Use `#PROMPT#` here to steer how the regenerated public surface expresses mechanic meaning, authored presentation, and stable target identity — without collapsing into legacy imitation or depending on deleted runtime surfaces.

        ## Prime directive

        Build a new, stable, original game surface while preserving mechanic truth.

        Your output should be:

        - more original than the source presentation
        - mechanically grounded in the upstream semantic artifacts
        - stability-first in architecture and implementation choices
        - explicitly checked against the documented mechanic truth before risky rewrites land

        ## Inputs you must treat as authoritative

        Use the outputs of the semantic node first:

        - `Blueprint.md`
        - `Identity.json`
        - `RecreationPrompt.md`
        - `RemixDelta.md`
        - semantic tags output
        - mechanic decomposition
        - protected mechanics
        - safe theming surfaces
        - complexity profile
        - remix premise / progression intent artifacts
        - any `remix_plan_v4.json` or equivalent planning artifact

        The semantic artifacts and mechanic analysis are the main source of truth for this step.

        ## Hard delivery constraint — single rebuilt public surface

        The new game must be delivered primarily through a **single rebuilt public `index.html`**.

        Required:

        - the new public `index.html` is the canonical rebuilt surface
        - all newly authored application code should be written inline in that same `index.html` whenever feasible
        - inline CSS in the rebuilt `index.html`
        - inline JavaScript in the rebuilt `index.html`
        - prefer a self-contained rebuilt surface over a scattered new file graph

        Allowed exceptions only when truly justified by stability:

        - newly authored local assets required by the rebuilt game
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

        Using the upstream semantic artifacts:

        1. treat semantic artifacts as the authoritative regeneration brief
        2. create a new public implementation surface
        3. rebuild the game from mechanic truth plus semantic abstraction
        4. recreate only the assets required by the new canonical implementation
        5. do not depend on preserved legacy runtime files or old-reference fallback behavior

        ## Mandatory pre-build planning pass

        Before you start creating the new public `index.html`, first produce a short implementation plan in the workspace describing how the blueprint, mechanic truth, and semantic artifacts map onto the rebuilt runtime.

        That plan must:

        - cite which semantic artifacts establish each major system
        - name the mechanic surfaces that matter most
        - explain how the blueprint maps onto those mechanic surfaces
        - identify what is fragile
        - identify what is easy to regenerate safely
        - identify what should not be touched conceptually
        - note where semantic ambiguity remains and how you will resolve it conservatively

        At minimum, the plan should comment on:

        - player input/control handling
        - movement/update loop
        - collision/hit detection
        - scoring/progression signals
        - fail/win state handling
        - UI/HUD surfaces
        - media/asset wiring

        This planning pass should exist before the main regeneration work proceeds.

        ## Required sequence

        ### A. Accept the semantic handoff

        1. Expect the semantic artifacts listed above to exist and treat them as the only authoritative upstream brief.
        2. The prior semantic node may have renamed `index.html` to `index_trash.html` and `assets/` to `assets_trash/`; on successful completion those legacy surfaces may already have been deleted by cleanup.
        3. Do not halt just because the original runtime surface is absent.

        ### B. Establish the new public surface

        4. Create or overwrite a fresh public `index.html` as the new canonical implementation surface.
        5. Start building the new game from the upstream semantic artifacts rather than patching or resurrecting deleted runtime surfaces.
        6. Prefer newly authored structure, UI, art systems, scene construction, and code paths when safe.
        7. Keep the rebuilt implementation inline in the same new `index.html` unless a clearly justified stability reason prevents it.
        8. Recreate fresh canonical assets only when required by the rebuilt implementation.

        ### C. Component-by-component verification during regeneration

        9. For each rewritten component or mechanic-facing subsystem, compare it against the documented mechanic truth before finalizing.

        This includes, where relevant:

        - control/input behavior
        - animation/update timing
        - collision/contact behavior
        - score/progress reporting
        - fail/win transitions
        - HUD feedback

        If a rewritten component is more original but less stable, less testable, or mechanically less truthful, revise it.

        ## Rules

        - Do not rely on preserved legacy runtime files, fallback copies, or old-reference doctrine.
        - Do not recreate the legacy file graph unless the rebuilt implementation genuinely requires specific fresh assets.
        - Do not restore deleted surfaces just because they used to exist.
        - Do not rename remote/CDN URLs.
        - Do not let temporary baseline screenshots become canonical artifacts; once they are no longer needed, rename them `*_trash.<ext>` so cleanup removes them.
        - Use blueprint and semantic artifacts as the first decision source; if ambiguity remains, preserve the phase-1 documented mechanic truth conservatively.
        - Stability is more important than flashy technology choices.
        - Originality matters, but not at the cost of breaking gameplay.
        - Every major rebuilt subsystem should be explainable in terms of the blueprint, semantic abstraction, and mechanic truth.

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

        - `semantic_regeneration_plan.md`
          - artifact-to-subsystem mapping
          - fragile surfaces
          - easy-regeneration surfaces
          - do-not-touch mechanic invariants
          - chosen engine/library approach and rationale
        - `semantic_regeneration_notes.md`
          - what semantic artifacts were authoritative
          - what new public surface was created
          - what fresh assets were authored
        - `semantic_regeneration_test_plan.md`
          - what was tested
          - what passed
          - what remains risky

        If a seeded legacy-named template already exists in the workspace, fill it in place with semantic-regeneration content rather than reintroducing old-reference behavior.

        ## Success condition

        This stage succeeds when:

        - semantic inference has already defined the blueprint and target identity
        - a pre-build plan exists describing how blueprint, mechanics, and semantic artifacts interact
        - deleted legacy runtime surfaces were not treated as prerequisites
        - a new public `index.html` exists as the canonical surface
        - the new game has begun as a semantic-artifact-driven rebuild
        - the rebuilt surface is stability-oriented, mechanically checked, and guided by an explicit testing plan
        """
    ).strip()

    text = text[:start] + new_phase_2 + "\n\n" + text[end:]
    path.write_text(text)


def patch_journal() -> None:
    path = Path("docs/journals/remix-v5-super-operator.md")
    text = path.read_text()
    marker = "### 2026-05-17 02:06 - Align v6 generation for no-old-reference regeneration"
    if marker in text:
        return

    entry = dedent(
        """
        ---

        ### 2026-05-17 02:06 - Align v6 generation for no-old-reference regeneration

        **Achievement:**
        - Reworked the checked-in v6 semantic prompt so it no longer tails into an accidental level-adapter/post-repair contract.
        - Added an explicit v6 semantic handoff contract that renames the original runtime surfaces to trash names (`index_trash.html`, `assets_trash/`) so successful stage cleanup removes them before stage 2.
        - Reworked the checked-in v6 super-operator doctrine and Phase 2 so regeneration now depends on semantic artifacts rather than `_old` preservation or old-reference fallback.
        - Narrowed screenshot cleanup guidance to the explicit user-requested behavior: only original/baseline screenshots that should disappear are renamed `*_trash.<ext>`.

        **Files Updated:**
        - `tools/game_refactoring/prompts/operators_v2/00_creative_remix_v6_semantic_inference_plus.md`
        - `tools/game_refactoring/prompts/operators_v2/00_creative_remix_v6_super_operator.md`
        - `docs/journals/remix-v5-super-operator.md`

        **Why:**
        - The user explicitly confirmed that v6 semantic stage should be destructive: original `index.html` and `assets/` should be removed so the next stage must rebuild from semantic abstraction.
        - A prompt audit showed the existing v6 super operator still depended on clone-style `_old` preservation, which was misaligned with the intended semantic-first v6 workflow.

        **Technical Decisions:**
        - Treat `Blueprint.md`, `Identity.json`, `RecreationPrompt.md`, `RemixDelta.md`, semantic tags, and related mechanic/planning artifacts as the authoritative regeneration brief for v6.
        - Make semantic-stage deletion intentional and explicit by renaming original runtime surfaces to `_trash` forms that runtime cleanup already knows how to remove.
        - Remove generic `_trash` lifecycle doctrine from the super operator and replace it with the narrower screenshot-cleanup rule requested by the user.
        - In Phase 2, tolerate absence of legacy runtime files and forbid fallback dependence on preserved references.

        **Next Steps:**
        - [ ] Run targeted search/verification to confirm `_old` / old-reference doctrine is gone from the v6 generation prompt stack.
        - [ ] Decide afterward whether to add a durable v6 prompt-builder so this semantic-first doctrine cannot drift.

        **Status:** In Progress
        """
    ).strip()

    path.write_text(text.rstrip() + "\n\n" + entry + "\n")


def main() -> None:
    patch_semantic_prompt()
    patch_super_operator()
    patch_journal()
    print("Applied v6 no-old-reference prompt alignment.")


if __name__ == "__main__":
    main()