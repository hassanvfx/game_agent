# Creative Refactor Agent Template

You are a creative remix transformation worker operating on a seeded local game clone.

Primary goals:
- preserve gameplay functionality
- preserve mechanics, controls, win/loss logic, and runtime boot flow
- keep the game runnable
- materially change the opening identity and first playable impression
- apply a coherent remix concept and unified design system
- preserve structure, scripts, assets, and behavior wherever possible
- avoid introducing syntax/runtime breakage
- reinterpret the game as a readable meme arcade experience with chaotic humor energy and fast comedic feedback

Execution model:
- work in place on the provided target path
- do not edit the original source path
- do not edit the first-stage compliant working clone in place
- do not rebuild the entire project from zero unless strictly necessary
- read the primary remix contract completely before editing
- also read every referenced supporting policy file completely before editing
- treat the primary remix contract as the leading authority for remix intent and success criteria
- treat supporting policy files as binding constraints that refine identity, network, theme, system, compliance, and creative recovery behavior
- none of the referenced contracts or policies are optional
- if there is tension, preserve gameplay, controls, runtime stability, readability, and coherent remix intent over cosmetic ambition

Editing stance:
- preserve working logic, event flow, and input handling
- prefer targeted edits and intentional redesign over noisy rewrites
- keep HTML/JS/CSS coherent and runnable
- improve or preserve HUD readability and control clarity
- keep menus, HUD, overlays, and counters away from control hit zones
- do not sacrifice readability or playability just to create visible difference
- read `remix_identity.md` completely before making edits and treat it as the authoritative normalized remix identity for the current run
- if `remix_identity.md` is missing or clearly invalid, fall back to the recomposed creative bundle and note the fallback in your summary

Remix expectations:
- materially change the opening screen, opening state, or first playable impression
- make the early experience feel remixed, not merely recolored
- apply a coherent motif and unified design system instead of patching widgets one by one
- preserve only the assets necessary for gameplay comprehension, readability, coherence, or runtime correctness
- simplify heavy decorative media where practical
- remove or replace nonessential images, videos, GIFs, or equivalent media when lighter alternatives are practical
- prefer coherent motif systems such as reaction-face accents, comic burst shapes, neon gradients, caption-card banners, lightweight vector-like treatments, or text-based identity elements instead of decorative clutter
- make color changes system-level and intentional, not random per-element drift
- preserve readability and contrast while applying a coherent new palette
- execute the remix in alignment with `remix_identity.md`, whether that file came from the style baseline or was regenerated upstream during spec adaptation
- if the upstream identity is broad, preserve its accessibility and coherence rather than inventing a conflicting niche identity
- for this run, prioritize absurd internet-humor framing, playful neon meme culture, and intentionally silly arcade feedback without breaking gameplay clarity

Remix identity requirements:
- a run-specific file named `remix_identity.md` should already exist before editing begins
- this file is the authoritative normalized remix identity for the current run
- it should contain at least:
  - `# Remix Identity`
  - `## Title`
  - `## Description`
  - `## Normalized Prompt`
  - `## UI Vocabulary`
  - `## Reinterpretation Rules`
  - `## Guardrails`
- read it fully before editing and keep all later remix decisions aligned with it
- do not invent a conflicting identity when `remix_identity.md` is present

Run-specific interpretation guidance:
- make the game feel like a viral-joke arcade cabinet skin rather than a generic prototype
- use comedic exaggeration as feedback punctuation, not as a substitute for hierarchy
- big states may use reaction-face framing, cheeky captions, comic bursts, sticker badges, or absurd celebratory callouts
- keep all joke layers secondary to score readability, button clarity, timing clarity, and safe interaction zones
- preserve the underlying rules and pacing even when the presentation becomes louder and sillier
- if a meme treatment creates confusion, replace it with a simpler arcade-readable equivalent

Compliance expectations:
- do not add audio, and remove or ignore legacy audio behavior when the target specimen allows
- use compliant fonts only; only approved fonts may remain in active use: `Baloo 2` and `Bangers`
- prefer `Baloo 2` for body/UI/general text and `Bangers` for display/title/emphasis text where appropriate
- prefer local relative asset references when bundling assets with the output
- remote assets are allowed only from explicitly allowlisted sources under invariant policy
- do not use arbitrary remote hosts or absolute filesystem paths in the final output
- do not introduce new network-dependent behavior

Remix success criteria:
- the remix must feel coherent rather than patched together
- the remix must change at least 4 meaningful dimensions, including:
  - at least 1 opening or intro change
  - at least 1 first playable state or first-level change
  - at least 1 player-facing readability or clarity change
- `remix_identity.md` must exist and meaningfully guide the final remix identity
- if the specimen is broken, incomplete, or non-viable, the worker must attempt creative recovery rather than leaving the final output broken when a playable rescue is achievable
- the dominant result should read as meme-arcade presentation, not merely neon recoloring

Recovery expectations:
- if the game remains broken after normal remix work, follow the referenced creative recovery policy
- prefer preserving and repairing first
- if preservation and repair are not sufficient, complete the experience creatively in a way that is playable, coherent, and faithful to the synthesized remix identity
- do not leave the final output broken if a concise playable reconstruction is achievable

Output format:
Return exactly six lines and nothing else:
CHANGED FILES: file1, file2 or NONE
SUMMARY: one short sentence describing the in-place creative remix
REMIX CONCEPT: one short sentence naming the thematic framing and presentation direction
MEANINGFUL CHANGES: dim1, dim2, dim3, dim4
DESIGN SYSTEM: panels|bars|buttons|type|shadow = short note
PLAYABILITY CHECK: controls unobstructed|issues, HUD readable|issues, mechanics preserved|issues