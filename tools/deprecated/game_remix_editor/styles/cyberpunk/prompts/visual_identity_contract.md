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

### 1. Title / branding
- The visible game title must change.
- The document `<title>` must change.
- Visible branding text should be updated to the new identity where practical.
- The result should not preserve the original title unchanged unless there is a
  documented technical blocker.

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

### 3. Color mapping / palette shift
All meaningful colors must be transformed into a new palette.

Hard rules:
- Apply a hue-shift or equivalent color remapping to the original palette.
- Preserve contrast, readability, status clarity, and outline legibility.
- Preserve gameplay clarity while changing the visual identity.
- Do not leave the original palette substantially unchanged.
- If an original color must remain for accessibility or clarity, keep it only as
  a narrow exception and document why.

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

### 4. Audio / network
- No networking or external resource fetching.
- No remote fonts.
- Audio must be removed entirely.
- Do not keep local audio assets.
- Remove audio files from the working clone output where feasible.
- Remove references to audio files from HTML, CSS, and JavaScript.
- Remove `<audio>` elements, `new Audio(...)`, WebAudio usage, and playback/preload logic.
- Remove music/sfx toggles or audio UI if they only exist for removed audio behavior.

## What counts as insufficient transformation

The following should be treated as failure:
- only swapping fonts while leaving the rest of the identity largely intact
- leaving the original title unchanged
- leaving the original palette mostly unchanged
- preserving the original visual identity with only token edits
- replacing the game from zero rather than editing the seeded clone
- breaking gameplay or core interaction flow in the name of retheming
- retaining audio files or audio references in the output package

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
- no networking remains
- no audio files remain in the output package
- no audio references remain in code
- seeded working clone still preserves core gameplay/structure contract
- `refactor_progress.json` exists and shows the required stages were meaningfully completed

## Judge failure examples

The judge should fail when it observes:
- original title unchanged
- original font family names still active
- more than the 2 approved fonts in active use
- generic fallback font families still present in active font declarations
- minimal font-only change with no meaningful palette shift
- original palette substantially preserved
- networking still present
- any audio asset files remain
- any code still references audio assets
- any active audio playback APIs remain
- obvious gameplay breakage introduced by retheme work
- missing `refactor_progress.json`
- progress file present but required stages never completed

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

SAFETY REQUIREMENTS
10. No networking.
11. Remove audio files and audio references completely.

FAILURE CONDITIONS
12. Font-only cleanup is not enough.
13. Original title unchanged is failure.
14. Original palette mostly unchanged is failure.
15. Keeping audio files or audio references is failure.