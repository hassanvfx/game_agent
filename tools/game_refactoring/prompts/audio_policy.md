# Audio Policy

## Purpose
Define the shared audio policy that supports `operators_v2/03_media_mapper.md` as the leading authority for audio mapping and integration.

## Authority Model
- `operators_v2/03_media_mapper.md` is the primary operational authority for audio integration behavior.
- This root policy defines shared constraints, catalog authority, runtime safety rules, and validation expectations.
- Audio is allowed when implemented in a way that remains consistent with the operator pipeline, preserves mechanics, and stays safe on small mobile screens.

## Core Policy
- Audio may be added or repaired as part of the media-mapping stage.
- Audio integration must preserve gameplay, controls, pacing, boot flow, and win/loss behavior.
- Audio must never be required for the game to remain understandable or playable.
- Audio must not block interaction, delay startup, or interfere with the game loop.
- Mobile-first thinking applies to audio UI and audio behavior as well as layout.

## Approved Audio Catalog Authority
Workers must read the task packet field:

```text
audio_catalog_path
```

This path points to a copied `audios.json` file containing approved grouped audio variants.

Primary workspace-local authority:
```text
catalogs/audios.json
```

Legacy canonical source when referenced by the runner:
```text
assets/audio_library/audios.json
```

## Catalog Rules
- Use approved catalog entries as the source of truth when selecting audio.
- Do not invent, fetch, search for, or synthesize arbitrary audio URLs.
- Do not use unapproved remote audio hosts.
- Do not use absolute filesystem paths in final game code.
- If a desired event has no exact match, choose the closest semantic group from the approved catalog or skip that sound.
- Missing or failed audio playback must never break gameplay.

## Integration Goals
Align audio with meaningful gameplay moments while preserving mechanics.

Preferred mappings include:
```text
starts / clicks / hovers / menu_opens / menu_closes -> UI interactions
jumps / lands -> movement
shoots / projectiles -> firing, casting, spawned projectiles
hits -> generic collisions
damages -> player hurt feedback
enemy_hits / enemy_defeats -> enemy combat feedback
pickups / bonuses / powerups -> rewards and upgrades
blocked_actions / warnings / failures -> invalid, danger, or failed actions
successes / level_completes / game_overs -> state transitions
ambient_loops / action_loops -> gameplay background loops
victory_loops / defeat_loops -> result screens
soft_magic_loops / spooky_loops / arcade_loops -> atmosphere-specific ambience
```

## Runtime Safety Rules
- Initialize playback safely after a user gesture when browser autoplay policy requires it.
- Keep loop volume modest and one-shot volume balanced.
- Use non-blocking playback patterns such as `audio.play().catch(() => {})` or equivalent safe handling.
- Do not block startup, rendering, input, pause/resume, or result flow on audio loading.
- Do not add audio in a way that obscures, alters, or re-times mechanics.
- Do not remove existing gameplay behavior to add sound.
- Repeated SFX should avoid runaway stacking, memory leaks, or clipping artifacts.
- Loop lifecycle should be explicit and controllable.

## Mobile-First Audio Constraints
- Do not introduce bulky audio controls, banners, or overlays that obstruct gameplay.
- If audio controls exist, they must remain compact, readable, and safe for narrow screens.
- Do not let audio prompts cover controls, HUD, or core play space.
- If the game is already mobile-safe without visible audio UI, prefer minimal or no new audio chrome.

## Validation Expectations
When audio is added or repaired, validators should confirm:
- audio came from approved catalog authority when applicable
- gameplay remains playable even if audio fails
- startup and interaction remain non-blocking
- integrated sounds map to meaningful events
- looped audio has a safe lifecycle
- mobile usability is not degraded by audio UI or playback behavior

## Evidence Expectations
When audio is added, summarize:
```text
- which game events received audio
- which catalog groups were used
- whether loop playback waits for user gesture
- whether all audio selections came from approved catalog authority