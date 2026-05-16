# Creative Remix Contract

## Purpose
This contract defines the first-stage recomposed creative brief for a meme-arcade reinterpretation of the game.

The creative agent should act like a senior game designer and creative director:
- preserve the mechanics
- preserve controls
- preserve win/loss logic
- preserve runtime boot flow
- redesign the opening identity, first playable experience, and player-facing presentation with a clearly comedic arcade intent
- translate the game into a coherent, high-energy meme-culture presentation without reducing clarity

This is not a random restyling pass.

## Scope
Applies only to the designated creative target path referenced by the task packet.
The original source and the first-stage compliant working clone must remain intact.

## Primary Success Definition
A successful remix:
- keeps the game playable
- keeps controls unobstructed
- preserves gameplay rules and interaction semantics
- materially changes the opening impression
- materially changes the first-level / initial-state feel or framing
- improves or preserves HUD readability
- reads as a coherent meme-arcade remix edition rather than a random patchwork
- applies a unified design system consistently across UI surfaces instead of styling widgets one by one
- delivers fast comedic feedback and absurd visual energy while keeping all gameplay information legible

## Non-Negotiable Rules
- Do not edit the original source path.
- Do not edit the first-stage compliant working clone in place.
- Only modify the creative target path.
- Preserve the main gameplay loop, rules, controls, win/loss behavior, and runtime boot flow.
- Prefer intentional redesign over large noisy rewrites.
- Keep the implementation generalizable across specimens instead of hard-coding one artifact layout.
- Do not sacrifice readability or playability just to create visible difference.
- Do not introduce networking or arbitrary remote dependencies.
- Treat the current run as silent-safe by default; do not make gameplay or presentation depend on audio.
- Apply compliant font and palette decisions as part of the remix rather than inheriting non-compliant legacy presentation.

## Required Remix Concept
The remix must have a coherent design concept.

Before editing, the agent should internally decide:
- a new thematic framing: chaotic meme arcade spectacle
- a new opening mood: instant punchline energy with bold, readable visual comedy
- a new HUD / feedback treatment: fast reaction-face accents, neon callouts, exaggerated success/fail beats
- a new first-level or initial-state presentation angle: the game should feel like a viral-joke cabinet skin wrapped around the existing mechanics

All visible changes should support that concept.

## Compliance-Carried Requirements
The creative remix must also carry forward these compliance rules:
- do not add audio, and do not make gameplay depend on audio playback
- use compliant fonts only; replace non-compliant fonts in CSS, canvas text, inline styles, or UI configuration where practical
- only approved fonts may remain in active use: `Baloo 2` and `Bangers`
- prefer `Baloo 2` for body/UI/general text and `Bangers` for display/title/emphasis text where appropriate
- any retained or introduced asset dependency must resolve either through a local relative path or an explicitly allowlisted source approved by invariant policy
- do not use arbitrary remote hosts or absolute filesystem paths in the final output
- apply a coherent palette system; do not leave the old color treatment untouched if it conflicts with the remix
- make color changes system-level and intentional, not random per-element drift
- preserve readability and contrast while applying the new palette
- translate the UI into a coherent design system instead of improvising per-widget visual logic

## Required Meaningful Difference
A valid remix must change at least **4** of these dimensions:
- opening screen identity
- title / subtitle / flavor framing
- HUD hierarchy and score/counter presentation
- decorative motif / atmosphere language
- first-level or initial-state framing
- onboarding / instructions tone
- feedback / reward / failure language
- early obstacle or stage presentation
- object styling / material language

Additional constraints:
- at least **1** change must affect the opening or intro experience
- at least **1** change must affect the first playable state or first level
- at least **1** change must affect player-facing readability or clarity
- if the first minute feels effectively unchanged, the remix is a failure

## Visual Remix Requirements
- The opening screen, opening state, or first playable impression must look materially different from the first-stage version.
- The remix should feel intentionally art-directed for strong mobile presentation, ideally with a portrait-friendly 9:16 composition when that can be achieved without breaking gameplay.
- The first 30–60 seconds should feel recognizably remixed in mood, framing, presentation, or feedback.
- Replace flat generic presentation with punchy meme-arcade identity cues such as caption-card framing, sticker-like badges, expressive iconography, and exaggerated celebratory/failure reactions.
- Use absurd visual gags intentionally, not as noise: each gag should reinforce feedback timing, state changes, or reward/failure readability.
- Prefer coherent motif systems such as reaction-face accents, comic burst shapes, neon glows, bold outlines, emoji-like symbolism, and text-driven joke framing instead of decorative clutter.
- Preserve only the graphic assets that are necessary for gameplay comprehension or runtime correctness.

## Design System Requirements
Translate the existing UI into a deliberate design system.
Do not leave the interface as a collection of unrelated widget styles.

The system must consistently define:
- panel materials
- bar materials
- button treatments
- capsule / inventory treatments
- typography scale and weight usage
- border / shadow rules
- spacing / inset rhythm
- icon framing language

The system should feel cohesive across:
- health / hunger bars
- score/counter blocks
- menus and overlays
- item buttons
- mobile controls
- status and instructional text

Required direction for this run:
- meme-arcade cabinet energy with disciplined readability
- bold neon contrast with dark anchoring surfaces
- exaggerated reaction accents used as punctuation, not wall-to-wall clutter
- sticker/caption/card framing that makes statuses feel like instant viral punchlines
- mobile-friendly spacing and ergonomics
- simple panel logic, clear bars, readable buttons, and controlled shadows despite the silly tone

## Layout and HUD Requirements
- Improve or preserve readability of score, counters, status text, and HUD surfaces.
- Reposition, invert, or rebalance layout only when it improves clarity, spacing, or ergonomics.
- Preserve strong contrast and clear visual hierarchy for primary play-state information.
- Do not count arbitrary widget shuffling as meaningful remixing.
- Prefer restyling existing anchor logic over arbitrary relocation when building the design-system remap.
- Default to clear mobile-first HUD spacing.
- Present critical HUD elements like a readable arcade broadcast package: headline values first, joke flavor second.
- Comedic overlays, stickers, and reaction graphics must never obscure score, timers, health, instructions, or interactable regions.

## Control-Safe-Zone Requirements
- Keep menus, counters, overlays, and HUD away from control hit zones.
- Do not cover buttons, joystick areas, drag regions, or other primary interaction zones.
- Preserve visibility of important gameplay space.
- If mobile controls exist, reorganize them only to improve ergonomics, spacing, and clarity without changing the underlying control semantics.
- Favor mobile-first framing and spacing decisions over desktop-centric layout assumptions when choosing viewport composition.
- Any meme flourish placed near controls must remain background-level and non-interactive unless it is already part of the gameplay-safe control design.

## Gameplay-Aware Remix Requirements
- Preserve the underlying rules, controls, and success/failure logic.
- You may alter scenario framing, first-level presentation, or initial-state setup if the core gameplay logic remains intact.
- You may adjust obstacle framing, level-start composition, or early feedback theme when those changes preserve the recognizable mechanics.
- The early experience should feel remixed, not merely recolored.
- Reframe rewards, misses, warnings, and state changes with fast comedic readouts that feel like arcade punchlines.
- Favor exaggerated but readable state communication: big wins should feel celebratory, mistakes should feel playfully dramatic, and neutral states should remain clean.
- Keep joke density subordinate to gameplay clarity; if a gag competes with timing, targeting, or input reading, remove or simplify the gag.

## Asset Policy
- Remove references to deleted assets.
- Do not leave broken asset paths.
- If replacing imagery with emoji-like symbols, CSS shapes, caption cards, or lightweight alternatives, ensure the replacement is visible, coherent, and functional in the live game.
- Preserve only the assets that are necessary for gameplay comprehension, readability, coherence, or runtime correctness.
- Prefer local relative asset references when bundling assets with the output.
- Remote assets are allowed only when explicitly approved by invariant policy; when uncertain, do not add them.

## Forbidden Behaviors
These are invalid remix outcomes:
- moving menus or HUD into the gameplay control area
- overlapping counters or overlays with controls
- random corner-swapping with no ergonomic benefit
- making readability worse to appear more different
- leaving the first level effectively the same while only restyling surface chrome
- making changes that feel noisy, incoherent, or accidental
- inserting memes, emojis, or reaction faces randomly without a strong thematic system
- reducing playability or control clarity
- styling each UI surface independently so the result feels patched together
- using a “chaotic” meme tone as an excuse for overlap, flashing clutter, or chaotic spacing
- introducing arbitrary remote asset hosts
- introducing audio dependencies or network-dependent presentation behavior

## Output Contract
The agent should make remix changes in place inside the creative target path and then return exactly:
- `CHANGED FILES: ...`
- `SUMMARY: ...`
- `REMIX CONCEPT: ...`
- `MEANINGFUL CHANGES: dim1, dim2, dim3, dim4`
- `DESIGN SYSTEM: panels|bars|buttons|type|shadow = short note`
- `PLAYABILITY CHECK: controls unobstructed|issues, HUD readable|issues, mechanics preserved|issues`

## Failure Rule
The remix must be considered a failure if:
- controls are obstructed
- readability is materially worse
- the opening / first-level experience is not materially different
- changes are mostly arbitrary layout noise
- the game becomes unstable
- the remix lacks a coherent concept
- arbitrary remote asset dependencies remain
- gameplay depends on audio, networking, or blocked external behavior
- the comedic presentation overwhelms gameplay clarity instead of supporting it