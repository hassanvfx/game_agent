# Clone Rebuild Test Plan

## Checks performed by Playwright
- Load preserved before surface at `/index_old.html` and capture `v5_before_index_trash.png`.
- Load canonical `/index.html` at the assigned root and capture `v5_after_entry.png`.
- Click start CTA, wait for Three.js canvas/gameplay, and capture `v5_after_spawn.png`.
- Confirm HUD reads BODY ARMOR and WANTED.
- Tap weapon switch, camera rotate, and interact/summon button, then capture `v5_after_merge.png`.
- Record console/page errors into `runtime_evidence.json`.

## Manual/code checks
- Verified mechanics-facing logic remains the same as the preserved source.
- Verified mobile controls remain visible and native CTA click paths are not globally suppressed.

## Remaining risk
External audio/GIF network failures may occur but are non-blocking because media play calls are failure-tolerant and visuals are procedural.