# Audio Library

Reusable MP3 audio catalog for the operator-pipeline audio mapping pass.

This folder supports two things:

1. A local/staging workflow for messy generated audio filenames.
2. A CDN-backed runtime index at `assets/audio_library/audios.json`.

The trusted CDN base URL is:

```text
https://gamezone-virid.vercel.app/assets/audios/
```

## Folder Layout

```text
assets/audio_library/
  README.md
  manifest.json
  audios.json
  incoming/
  unmatched/
  sfx/
  ui/
  music/
  ambience/
```

## Sanitizer Workflow

Place generated MP3 files with prompt-like filenames in:

```text
assets/audio_library/incoming/
```

Preview what will happen:

```bash
python3 scripts/sanitize_audio_library.py --dry-run
```

Apply the sanitizer:

```bash
python3 scripts/sanitize_audio_library.py --apply
```

The sanitizer copies files into clean locations and updates:

```text
assets/audio_library/audios.json
```

Original files in `incoming/` are not deleted.

## Output Naming

All audio files are MP3.

Examples:

```text
sfx/jump_01.mp3
sfx/jump_02.mp3
sfx/damage_01.mp3
ui/click_01.mp3
music/action_loop_01.mp3
ambience/spooky_loop_01.mp3
```

The matching CDN URLs are derived from the local location:

```text
sfx/jump_01.mp3
```

becomes:

```text
https://gamezone-virid.vercel.app/assets/audios/sfx/jump_01.mp3
```

## `audios.json` Shape

`audios.json` is grouped by semantic audio category.

Each audio item has exactly:

```text
name
url
location
usage
audio_type
```

`audio_type` is one of:

```text
one_shot
loop
```

Example:

```json
{
  "jumps": [
    {
      "name": "jump_01",
      "url": "https://gamezone-virid.vercel.app/assets/audios/sfx/jump_01.mp3",
      "location": "sfx/jump_01.mp3",
      "usage": "Player jump, bounce, upward movement",
      "audio_type": "one_shot"
    }
  ],
  "ambient_loops": [
    {
      "name": "ambient_loop_01",
      "url": "https://gamezone-virid.vercel.app/assets/audios/music/ambient_loop_01.mp3",
      "location": "music/ambient_loop_01.mp3",
      "usage": "Default background music",
      "audio_type": "loop"
    }
  ]
}
```

## Groups

```text
jumps
lands
shoots
projectiles
hits
damages
enemy_hits
enemy_defeats
pickups
bonuses
powerups
explosions
blocked_actions
warnings
successes
failures
game_overs
level_completes
clicks
hovers
starts
pauses
resumes
menu_opens
menu_closes
ambient_loops
action_loops
victory_loops
defeat_loops
soft_magic_loops
spooky_loops
arcade_loops
```

## Audio Type Rules

```text
sfx/*      -> one_shot
ui/*       -> one_shot
music/*    -> loop
ambience/* -> loop
```

## Runtime Rules

- Audio URLs must come from `assets/audio_library/audios.json`.
- The audio operator must not invent remote audio URLs.
- The approved CDN prefix is `https://gamezone-virid.vercel.app/assets/audios/`.
- Missing optional audio should degrade safely without crashing.
- Do not add autoplay behavior that blocks game boot.
- User gesture requirements should be respected by initializing audio after click/tap/start.
- The audio operator should preserve existing gameplay mechanics.

## Canonical Events

The older `manifest.json` still records the canonical event names and preferred clean locations. `audios.json` is the runtime-friendly grouped index for multiple variants.

Canonical events:

```text
ui_click
ui_hover
start_game
pause
resume
menu_open
menu_close
jump
land
shoot
projectile
hit
damage
enemy_hit
enemy_defeat
pickup
bonus
powerup
explosion
blocked
warning
success
fail
game_over
level_complete
ambient_loop
action_loop
victory_loop
defeat_loop
soft_magic_loop
spooky_loop
arcade_loop
```

## Short Generative Prompts

Use these short prompts when generating source MP3s. After generation, drop the files into `incoming/`; the sanitizer will infer the clean category from the prompt-like filename.

### One-Shots

#### `jump`

```text
Playful upward jump sound with a quick pitch rise, light bounce, and tiny magical sparkle. Clean arcade-fantasy feel.
```

#### `land`

```text
Soft landing thump with a padded impact and subtle dust puff. Gentle, non-violent, game-ready.
```

#### `shoot`

```text
Magical casting shot with a quick wand-like whoosh and bright sparkle attack. Not gun-like.
```

#### `projectile`

```text
Fast magical projectile zip with airy shimmer and tiny particle sparkle. Lightweight and energetic.
```

#### `hit`

```text
Compact arcade hit sound with a soft bonk impact and slight sparkle. Clear but non-violent.
```

#### `damage`

```text
Player damage cue with a short descending blip and soft impact. Mild, readable, family-friendly.
```

#### `enemy_hit`

```text
Enemy hit cue with a quick magical pop, small crunchy impact, and sparkle dust.
```

#### `enemy_defeat`

```text
Whimsical enemy defeat poof with sparkles and a tiny descending vanish tail.
```

#### `pickup`

```text
Bright collectible pickup chime with a small upward sparkle. Rewarding and lightweight.
```

#### `bonus`

```text
Joyful bonus reward burst with ascending sparkles. Celebratory, original, and arcade-like.
```

#### `powerup`

```text
Power-up activation with rising magical energy, glittering highlights, and a confident resolve.
```

#### `explosion`

```text
Soft arcade explosion pop with rounded burst, dust, and sparkle debris. Non-realistic and non-violent.
```

#### `blocked`

```text
Blocked action cue with a short dull tick or wooden clack and slight downward pitch.
```

#### `warning`

```text
Brief warning pulse with soft magical tension. Noticeable but not harsh or alarmist.
```

#### `success`

```text
Positive success chime with a clean sparkle tail. Short, satisfying, and original.
```

#### `fail`

```text
Gentle fail cue with a soft descending wobble or muted thunk. Mild and non-annoying.
```

#### `game_over`

```text
Gentle game-over sting with descending notes and a soft magical fade. Bittersweet, not dramatic.
```

#### `level_complete`

```text
Short level-complete flourish with bright sparkles and upbeat arcade-fantasy resolution.
```

#### `click`

```text
Tiny UI click with a crisp soft tap and subtle sparkle. Clean and responsive.
```

#### `hover`

```text
Subtle UI hover cue with a very short airy tick or shimmer. Quiet and non-intrusive.
```

#### `start`

```text
Start-game confirmation with a short magical whoosh-chime. Inviting and energetic.
```

#### `pause`

```text
Pause cue with a short soft downward blip and gentle stop feeling.
```

#### `resume`

```text
Resume cue with a short upward blip or light shimmer restart feeling.
```

#### `menu_open`

```text
Menu-open cue with a quick card unfold or magical reveal shimmer. Friendly and clean.
```

#### `menu_close`

```text
Menu-close cue with a quick soft fold-away or reverse shimmer. Pairs naturally with menu open.
```

### Loops

#### `ambient_loop`

```text
Seamless casual game ambient loop with light fantasy arcade mood, soft plucks, warm pads, and gentle rhythm. Original, no vocals.
```

#### `action_loop`

```text
Seamless action gameplay loop with upbeat arcade-fantasy energy, light percussion, plucky synths, and magical sparkle accents. Original, no vocals.
```

#### `victory_loop`

```text
Seamless victory/results loop with cheerful fantasy arcade mood, bright harmony, and celebratory light percussion. Original, no vocals.
```

#### `defeat_loop`

```text
Seamless defeat/results loop with gentle bittersweet arcade-fantasy mood, soft descending harmony, and calm emotional tone. Original, no vocals.
```

#### `soft_magic_loop`

```text
Seamless soft magic ambience loop with airy shimmer, distant twinkles, warm pad, and calm enchanted atmosphere. No vocals.
```

#### `spooky_loop`

```text
Seamless family-friendly spooky ambience loop with soft wind, playful ghostly tones, subtle creaks, and magical mystery. No screams, no vocals.
```

#### `arcade_loop`

```text
Seamless arcade ambience loop with gentle retro room tone, soft synth bed, and tiny electronic sparkle textures. Energetic but unobtrusive.
```
