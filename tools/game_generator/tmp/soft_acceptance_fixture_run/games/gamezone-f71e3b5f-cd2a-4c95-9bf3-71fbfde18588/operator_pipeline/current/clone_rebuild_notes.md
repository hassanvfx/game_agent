# Clone Rebuild Notes

## Preserved runtime
Original public entrypoint was renamed to `index_old.html`. No directly linked local CSS/JS files needed renaming because CSS/JS application code was inline and the only local script is the existing Three.js support asset.

## New canonical surface
A new `index.html` was authored from the preserved mechanics with updated identity, HUD, materials, procedural textures, lighting, fog, and mobile copy.

## Reference-only usage
The old file was inspected for actual mechanics and retained as reference-only evidence. The canonical gameplay path is the new `index.html`.

## Presentation transformation
Day/generic city surfaces were changed into a neon crime-chase district with cyan/magenta asphalt lines, emissive towers, wanted/body-armor HUD, overdrive district copy, and a compact sandbox brand badge.

## Mechanic preservation
State machine, controls, collision, combat, vehicle behavior, wanted logic, death, and restart were left intact.