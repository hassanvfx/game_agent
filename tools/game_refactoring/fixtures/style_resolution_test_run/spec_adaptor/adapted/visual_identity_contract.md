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

For this run, the identity should read as an original magical-academy adventure:
- mysterious but readable
- candlelit rather than horror-dark
- whimsical, studious, and adventurous
- inspired by boarding-school fantasy symbolism without copying protected franchise elements

### 1. Title / branding
- The visible game title must change.
- The document `<title>` must change.
- Visible branding text should be updated to the new identity where practical.
- The result should not preserve the original title unchanged unless there is a
  documented technical blocker.
- Prefer titles and subtitles that imply spellcraft, hidden halls, enchanted study, house rivalry, wizard-school trials, owls, stars, vaults, or secret lessons without using direct Harry Potter naming.

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

Run-specific palette direction:
- midnight navy
- deep indigo
- parchment cream
- aged gold / brass
- lantern amber
- ink black
- restrained emerald or burgundy accents only when useful for contrast or role coding

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

### 4. Materials / motif language
The visual system should feel like a lightweight magical-study kit rather than a literal film tie-in.

Preferred materials and motif cues:
- parchment cards
- brass trim
- inked dividers
- glowing rune-like accents
- constellation dots
- starbursts
- keyholes
- tower silhouettes
- owl or feather motifs
- subtle spell-trace lines

Hard rules:
- use motifs sparingly and systematically
- avoid random sticker-like decoration
- avoid direct copies of franchise typography, lightning-bolt logos, house shields, or recognizable proprietary iconography
- keep the interface readable at gameplay scale
- preserve clean hit zones and HUD clarity

### 5. Audio / network
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
- making it read as generic fantasy clutter instead of a coherent magical-academy presentation
- directly copying Harry Potter logos, names, crests, character cues, or unmistakable franchise signifiers

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
- the resulting identity reads as an original magical-academy reinterpretation instead of direct franchise mimicry

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
- direct Harry Potter franchise copying instead of symbolic inspiration

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
9. Create a clearly new magical-academy identity.
10. Use parchment, brass, ink, glow, and celestial cues with restraint.
11. Avoid direct franchise names or proprietary iconography.

SAFETY REQUIREMENTS
12. No networking.
13. Remove audio files and audio references completely.

FAILURE CONDITIONS
14. Font-only cleanup is not enough.
15. Original title unchanged is failure.
16. Original palette mostly unchanged is failure.
17. Keeping audio files or audio references is failure.
18. Direct Harry Potter copying is failure.