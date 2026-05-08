# Media Mapper Prompt Packet Spec

## Purpose

This document defines the intended Stage 03 media-mapper packet shape and enforcement language.

The goal is to make Python-detected media work explicit, actionable, and impossible for the operator to ignore.

This spec exists to ensure the real packet builder and Stage 03 prompt stay aligned with the intended contract.

---

## Core Principles

1. Relative asset/media references in HTML, JS, CSS, or other actionable source files must be surfaced into the prompt packet when they match media/file extension rules.
2. Python-detected URL/media findings are not optional suggestions. They are required stage work.
3. The media-mapper prompt should be simple and operational:
   - show the bad refs
   - show the approved replacement authority
   - show success examples
   - define failure clearly
4. The visible packet should prioritize concrete replacement candidate lists over extra abstract metadata.

---

## Required Packet Shape

```md
# Production Operator Pipeline v2 Prompt Packet

## Workspace Contract

The previous/latest-good workspace copied into this attempt was:

```text
/current
```

Do not modify files outside the working clone path.

## Production Run Context

- run_dir: {run_dir}
- selected_style_id: {selected_style_id}
- remix_prompt: {remix_prompt}
- adapted_spec_dir: {adapted_spec_dir}

## Workspace Catalogs

Use only the workspace-local catalog files listed below for catalog-guided media work:

- catalogs/audios.json:
- catalogs/gifs.json:
- catalogs/sprites.json:
- catalogs/fonts.json:

Do not rely on repo-root catalog paths or other host filesystem catalog references. If mapped media or approved icon/font systems need import plumbing, wire them against these workspace-local catalogs rather than leaving partial setup for a later stage.

## Python Media Policy Hint

REQUIRED URLs to remove for this attempt:

```json
{potential_urls_to_remove_json}
```

This list is computed by Python and is a required main task. Do not invent additional policy rules beyond the provided hint.

## Python Media Replacement Candidates

REQUIRED media references to replace or remap for this attempt:

```json
{media_replacement_candidates_json}
```

If a local or external media reference appears here, do not automatically treat it as acceptable just because it already works. These entries are required mapping/removal work for this stage.

## Generic Replacement Examples

This is what successful replacement looks like:

- audio
  - before: `assets/bgm/0002/old-track.mp3`
  - after: approved catalog-backed audio path or approved replacement wiring
- image
  - before: `assets/sprites/player.png`
  - after: approved sprite/background replacement path
- gif
  - before: `assets/effects/explosion.gif`
  - after: approved GIF replacement path
- video
  - before: `assets/cutscenes/intro.mp4`
  - after: approved replacement path or safe removal when not needed
- font stylesheet
  - before: `assets/fonts.googleapis.com/css2-family_Press_Start_2P_display_swap.css`
  - after: approved `catalogs/fonts.json` choice
- font file
  - before: `assets/fonts/custom.ttf`
  - after: approved catalog-backed font setup

## Python Font / Icon Candidates

Deterministic font and icon implementation candidates for final-pass alignment:

### Font candidates
```json
{font_replacement_candidates_json}
```

### Icon-font candidates (this section is fixed in the prompt)
```json
[
home
menu
close
search
settings
account_circle
person
group
favorite
favorite_border
star
star_border
check
check_circle
cancel
add
remove
edit
delete
arrow_back
arrow_forward
arrow_upward
arrow_downward
expand_more
expand_less
chevron_left
chevron_right
refresh
sync
download
upload
cloud
cloud_download
cloud_upload
notifications
notifications_none
email
mail
chat
chat_bubble
phone
call
videocam
camera_alt
image
photo
play_arrow
pause
stop
skip_next
skip_previous
volume_up
volume_off
mic
mic_off
lock
lock_open
visibility
visibility_off
shopping_cart
payment
attach_money
credit_card
store
location_on
map
gps_fixed
directions
calendar_today
event
schedule
access_time
alarm
help
info
warning
error
build
code
terminal
bug_report
api
language
public
link
attach_file
folder
folder_open
description
article
dashboard
analytics
bar_chart
pie_chart
trending_up
trending_down
wifi
bluetooth
battery_full
battery_charging_full
power
]
```

If these lists are non-empty, treat them as concrete signals that current font or icon implementations may need alignment with `catalogs/fonts.json` following the stage guidelines.

## Retry Context

{retry_context}

## Required Stdout Contract

End your response with exactly these lines, using one-line values:

```text
OPERATOR STATUS: completed|failed
CHANGED FILES: file1, file2 or NONE
SUMMARY: one short sentence
MECHANICS CHECK: preserved|issues
VISUAL CHECK: preserved|updated|issues
AUDIO CHECK: integrated|not_applicable|issues
MOBILE CHECK: safe|not_checked|issues
```

---

{stage_prompt_body}
```

---

## Failure Criteria

The Stage 03 media-mapper result should be treated as failure if any of the following remain in HTML, JS, CSS, or other actionable source files:

- Python-listed URLs to remove
- Python-listed media replacement candidates
- short legacy relative asset/media refs that were explicitly flagged
- local `assets/...` media refs that were required replacement work for the stage
- unchanged bad refs after the operator had a clear approved replacement path

Failure means we still see the bad refs in source files.

It is not enough for the operator to mention replacements in comments or summaries.

It is not enough for the operator to say assets are “already local.”

If the flagged refs are still present in source, the mapping failed.

---

## Detector Case Matrix

### Actionable source files
The detector should classify only actionable source files for enforcement:

- `.html`
- `.htm`
- `.css`
- `.js`
- `.jsx`
- `.ts`
- `.tsx`

The same actionable-source filter must be used both:
- before the operator runs, to build the prompt packet
- after the operator runs, to validate the result

### Media detection cases
Detect media refs from actionable source files using all available heuristics:

- HTML attributes
  - `src`
  - `href`
  - `poster`
  - `data-src`
  - `data-href`
- CSS `url(...)`
- quoted relative asset strings
- extension-driven fallback scanning

Media extension classes:
- audio
  - `.mp3`
  - `.wav`
  - `.ogg`
  - `.m4a`
  - `.aac`
  - `.flac`
- image
  - `.png`
  - `.jpg`
  - `.jpeg`
  - `.webp`
  - `.svg`
- gif
  - `.gif`
- video
  - `.mp4`
  - `.webm`
  - `.mov`
  - `.m4v`

Examples that should be detected:
- `assets/bgm/0001/Sci-fi/Midnight-Crawlers_Looping.mp3`
- `/assets/audios/music/action_loop_01.mp3`
- `https://gamezone-virid.vercel.app/assets/audios/music/action_loop_01.mp3`
- `assets/effects/explosion.gif`
- `assets/cutscenes/intro.mp4`

### Font detection cases
Detect font refs from actionable source files using all available heuristics:

- HTML `<link href="...">`
- CSS `@import url(...)`
- CSS `url(...)`
- quoted relative asset strings
- `font-family: ...`
- extension-driven fallback scanning for font binaries/stylesheets

Font extension classes:
- font stylesheet
  - `.css`
- font binary
  - `.ttf`
  - `.otf`
  - `.woff`
  - `.woff2`
  - `.eot`

Examples that should be detected:
- `assets/fonts.googleapis.com/css2-family_Fredoka_wght_400_600_family_VT323_display_swap.css`
- `assets/fonts.gstatic.com/...ttf`
- `'Fredoka'`
- `'VT323', monospace`

### Allowed vs actionable host/path logic

#### Allowed URL policy
Use the same allowlist function for both pre and post decisions:
- `_is_allowed_external_url(url)`

If a URL is allowed by that function, the detector/classifier must not contradict itself later.

#### Required invariants
- if `gamezone-virid.vercel.app` is allowed, it must be allowed in both pre and post
- if a font stylesheet is actionable, it must be actionable in both pre and post

#### `gamezone-virid.vercel.app`
`gamezone-virid.vercel.app` is a whitelisted domain.

That means:
- the detector must not allow it in URL policy but still mark the same allowed refs as unresolved replacement failures in post-scan
- allowed Vercel refs must be classified consistently before and after the operator step

#### Mirrored Google font assets
Mirrored font refs such as:
- `assets/fonts.googleapis.com/...css`
- `assets/fonts.gstatic.com/...ttf`
must be classified consistently both pre and post as font-related candidates unless explicitly exempted by final policy

---

## Relative Media Detection Expectations

The upstream detector should find relative media refs in:

- `index.html`
- `.js`
- `.jsx`
- `.ts`
- `.tsx`
- `.css`

Detection should not rely only on narrow HTML/CSS structural patterns.

The detector should also use extension-driven scanning so plain quoted relative asset strings in source text are surfaced.

Expected approach:

1. scan actionable source files for known media/font extensions
2. when an extension hit is found, walk outward to extract the full relative path token
3. normalize the ref
4. classify it by type
5. emit it into the media candidate list with source-file context

---

## Prompt Design Notes

The visible packet should remain simple.

Prefer:
- required URL list
- required media candidate list
- short success examples
- explicit failure criteria

Avoid overloading the operator-facing packet with excessive secondary metadata when the primary issue is that concrete bad refs must be replaced.