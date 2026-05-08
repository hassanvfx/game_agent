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

For this run, the target identity is an **original magical-academy adventure presentation**:
- mysterious but inviting
- scholarly rather than chaotic
- whimsical without becoming childish noise
- readable on mobile
- evocative of candlelit halls, enchanted libraries, astronomy towers, house crests, brass instruments, parchment interfaces, and glowing spellwork
- inspired by wizard-school fantasy as a cultural mood, not by direct franchise replication

### 1. Title / branding
- The visible game title must change.
- The document `<title>` must change.
- Visible branding text should be updated to the new identity where practical.
- The result should not preserve the original title unchanged unless there is a
  documented technical blocker.
- Favor titles and subtitles that imply magical study, spell trials, academy rivalries, enchanted archives, or apprentice adventure.
- Do not use protected franchise names, exact canon school names, copyrighted character names, or copied slogan phrasing.

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

Preferred palette direction for this run:
- deep midnight blue
- ink black
- parchment cream
- antique brass / warm gold
- burgundy or oxblood accents
- magical teal, violet, or emerald glows used sparingly for state emphasis
- candle-amber highlights for positive focus and onboarding emphasis

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
Use a consistent material language across the UI.

Preferred materials and motifs:
- parchment cards
- brass trims
- crest medallions
- beveled plaques
- observatory-glass highlights
- constellation dots
- rune circles
- spellbook dividers
- lantern glow edges
- subtle starfield or dust-like magical particles

Hard rules:
- motifs must be restrained and systematized rather than scattered randomly
- decorative cues must not reduce readability
- iconography should feel like a unified school-of-magic toolkit rather than mixed fantasy leftovers
- controls and HUD must remain more readable than decorative

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
- applying “magic” as random stars and purple gradients without a disciplined design system
- using direct copyrighted franchise identifiers as branding or decorative crutches

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
- the visual identity reads as a coherent magical-academy remix rather than a generic dark reskin

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
- decorative references imply a copyrighted franchise more strongly than an original fantasy-school identity

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
9. Create a clearly new magical-academy visual identity.

THEMATIC DIRECTION
10. Favor enchanted-school atmosphere, readable spellbook UI cues, and heraldic fantasy accents.
11. Prefer readability, clear hierarchy, and restrained decorative treatment.
12. Use symbolic wizard-school mood rather than direct franchise copying.

SAFETY REQUIREMENTS
13. No networking.
14. Remove audio files and audio references completely.

FAILURE CONDITIONS
15. Font-only cleanup is not enough.
16. Original title unchanged is failure.
17. Original palette mostly unchanged is failure.
18. Keeping audio files or audio references is failure.
19. Direct franchise naming or mimic branding is failure.