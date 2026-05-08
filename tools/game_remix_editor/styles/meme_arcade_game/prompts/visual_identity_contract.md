# Visual Identity Contract
#
# This single-file contract is the primary transformation standard for both
# refactor and judge steps. The agent should treat this as the authoritative
# visual-identity brief for seeded-clone in-place edits.

## Core execution model

- The source input is immutable.
- Work only on the seeded working clone.
- Edit existing files in place.
- Do not rebuild the project from zero unless strictly necessary.
- Preserve gameplay logic, structure, interaction flow, DOM structure, asset wiring,
  and behavioral intent as much as possible while changing identity.

## Required identity transformation

The result must look like a **new visual identity** of the same game, not merely a
minimal compliance cleanup.

For this run, the target identity is:
- meme arcade chaos with deliberate gameplay readability
- chaotic internet-humor energy expressed through disciplined visual systems
- absurd visual gags, bold reaction-face accents, neon meme-culture color, and playful arcade spectacle
- intentionally silly presentation that still reads immediately during play
- fast comedic feedback and viral-joke aesthetics without obscuring controls or game-state communication

### 1. Title / branding
- The visible game title must change.
- The document `<title>` must change.
- Visible branding text should be updated to the new identity where practical.
- The result should not preserve the original title unchanged unless there is a
  documented technical blocker.
- Branding should feel like a punchy meme-arcade cabinet, stream overlay, or joke-poster headline rather than a neutral prototype label.

### 2. Fonts
Only these two approved fonts may remain in declared font usage:
- `Baloo 2`
- `Bangers`

Hard rules:
- Replace all explicit font-family usage with only these approved fonts.
- UI/body/general text should use `Baloo 2`.
- Display/title/emphasis text should use `Bangers` where appropriate.
- Remove or replace all other named font families.
- Remove remote font dependencies and source-font references.
- Do not leave original source font names in active styling.
- Do not leave generic fallback declarations such as `sans-serif`, `serif`, `monospace`, `cursive`, `fantasy`, or `system-ui` in active font-family rules.
- Active font-family declarations in the final output should resolve only to `Baloo 2` and/or `Bangers`.

Typography direction for this run:
- `Bangers` should carry titles, punchlines, CTA emphasis, and reaction-card headlines.
- `Baloo 2` should carry HUD text, instructions, counters, labels, and readable body copy.
- Type should feel loud and comedic at display scale, but never muddy at HUD scale.

### 3. Color mapping / palette shift
All meaningful colors must be transformed into a new palette.

Hard rules:
- Apply a hue-shift or equivalent color remapping to the original palette.
- Preserve contrast, readability, status clarity, and outline legibility.
- Preserve gameplay clarity while changing the visual identity.
- Do not leave the original palette substantially unchanged.
- If an original color must remain for accessibility or clarity, keep it only as
  a narrow exception and document why.

Required palette direction for this run:
- dark anchor surfaces so neon accents remain readable
- high-energy magenta, electric cyan, acid lime, warning yellow, and hot orange used as controlled signal colors
- strong black or near-black outlines to preserve reaction-face readability and button clarity
- meme-sticker whites or light cards used sparingly for caption contrast
- success, failure, and warning states should feel immediate and arcade-bold rather than subtle

This applies to, where present:
- backgrounds
- panels
- buttons
- text accents
- HUD colors
- borders
- outlines
- highlights
- status bars
- overlays
- title treatments

### 4. Atmosphere / material language
The visual identity should express the meme-arcade prompt through coherent materials rather than random jokes.

Required material cues:
- sticker-like badges
- caption-card banners
- comic burst or impact shapes
- reaction-face medallions or accent icons
- chunky outlines
- playful glow treatments
- arcade-screen framing and celebratory pop states

Hard rules:
- Use absurd visual gags as punctuation, not background noise.
- Do not wallpaper the screen with unrelated memes.
- Decorative comedy should reinforce feedback timing, milestones, danger, rewards, or transitions.
- Critical gameplay information must always out-rank gag elements in scale, contrast, and placement.

### 5. Audio / network
- No networking or external resource fetching beyond invariant-allowed behavior.
- No remote fonts.
- Default to silent-safe presentation.
- Do not introduce new audio dependencies.
- Remove audio files from the working clone output where feasible if they are nonessential and violate the target specimen policy.
- Remove references to audio files from HTML, CSS, and JavaScript when the specimen allows.
- Remove `<audio>` elements, `new Audio(...)`, WebAudio usage, and playback/preload logic when they are not required by higher-priority invariant handling.
- Remove music/sfx toggles or audio UI if they only exist for removed audio behavior.

## What counts as insufficient transformation

The following should be treated as failure:
- only swapping fonts while leaving the rest of the identity largely intact
- leaving the original title unchanged
- leaving the original palette mostly unchanged
- preserving the original visual identity with only token edits
- replacing the game from zero rather than editing the seeded clone
- breaking gameplay or core interaction flow in the name of retheming
- keeping the presentation generic when the prompt clearly calls for meme-arcade identity
- splashing random internet jokes everywhere without a disciplined visual system
- making the interface noisier while reducing readability
- retaining nonessential audio files or audio references when they conflict with the target output package

## Refactor output expectation

The refactor step should return concise evidence describing:
- changed files
- summary of in-place edits
- notable identity changes applied
- any documented exceptions

## Required live progress tracking

During execution, the refactor worker must continuously update a single machine-readable progress file:

- `refactor_progress.json`

This file should be created inside the working clone root and updated in place as work advances.

Minimum required fields:
- `status`
- `current_step`
- `title_changed`
- `fonts_audited`
- `fonts_replaced`
- `colors_audited`
- `palette_shift_applied`
- `network_audited`
- `network_clean`
- `audio_audited`
- `audio_clean`
- `files_changed`
- `notes`
- `last_updated`

Suggested step progression:
1. `read_contract`
2. `audit_title`
3. `audit_fonts`
4. `replace_fonts`
5. `audit_colors`
6. `apply_palette_shift`
7. `audit_network`
8. `remove_network_dependencies`
9. `audit_audio`
10. `fix_audio_policy`
11. `verify_contract`
12. `complete`

The worker should also emit short progress lines to stdout prefixed exactly with:
- `PROGRESS:`

Examples:
- `PROGRESS: read_contract`
- `PROGRESS: replace_fonts`
- `PROGRESS: apply_palette_shift`
- `PROGRESS: verify_contract`

These progress updates must be short and structured rather than verbose narrative.

## Judge pass criteria

A judge pass should require all of the following:
- title changed
- only approved fonts remain in active use
- palette shift / color remapping is visibly present
- contrast and outline clarity remain acceptable
- no networking remains outside invariant-allowed behavior
- no blocked remote font behavior remains
- no noncompliant audio behavior remains
- seeded working clone still preserves core gameplay/structure contract
- `refactor_progress.json` exists and shows the required stages were meaningfully completed
- the resulting presentation clearly reads as a coherent meme-arcade retheme rather than a generic cleanup

## Judge failure examples

The judge should fail when it observes:
- original title unchanged
- original font family names still active
- more than the 2 approved fonts in active use
- generic fallback font families still present in active font declarations
- minimal font-only change with no meaningful palette shift
- original palette substantially preserved
- networking still present outside invariant allowances
- active audio behavior introduced or retained in conflict with policy
- any code still references noncompliant audio behavior
- obvious gameplay breakage introduced by retheme work
- missing `refactor_progress.json`
- progress file present but required stages never completed
- the result feels like random meme stickers on top of the old game instead of a new identity system

## Pseudocode reminder for workers

```text
SEEDED CLONE REFACTOR CONTRACT

1. Start from the mirrored working clone.
2. Edit existing files in place.
3. Preserve gameplay and structure as much as possible.

VISUAL IDENTITY REQUIREMENTS
4. Change the game title.
5. Only use Baloo 2 and Bangers.
6. Replace all other font usage.
7. Hue-shift/remap all meaningful colors.
8. Preserve contrast and outline readability.
9. Create a clearly new visual identity.
10. Make the identity read as meme-arcade chaos with controlled readability.

RUN-SPECIFIC DIRECTION
11. Use bold neon accents on dark anchors.
12. Express humor through reaction faces, captions, stickers, comic bursts, and playful exaggeration.
13. Keep joke layers secondary to gameplay information and control clarity.

SAFETY REQUIREMENTS
14. No networking beyond invariant allowances.
15. Do not introduce audio dependence.
16. Preserve silent-safe behavior and remove nonessential audio behavior when feasible.

FAILURE CONDITIONS
17. Font-only cleanup is not enough.
18. Original title unchanged is failure.
19. Original palette mostly unchanged is failure.
20. Random meme clutter without system coherence is failure.
21. Reduced readability or control clarity is failure.