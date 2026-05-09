en
- `ok`
- `warning`
- `error`

Use:
- `ok` when the narrative remix is coherent and safely aligned to `#PROMPT#`
- `warning` when the remix mostly works but is limited by the existing game structure
- `error` when you cannot complete the narrative adaptation safely or truthfully

End stdout with exactly these lines:
```text
OPERATOR STATUS: completed|failed
CHANGED FILES: file1, file2 or NONE
SUMMARY: one short sentence
MECHANICS CHECK: preserved|issues
VISUAL CHECK: preserved|updated|issues
AUDIO CHECK: integrated|not_applicable|issues
MOBILE CHECK: safe|not_checked|issues
```

For this stage:
- `MECHANICS CHECK` should normally be `preserved`
- `VISUAL CHECK` should normally be `preserved`
- `AUDIO CHECK` should normally be `not_applicable`

## Animated Background Concept Rule

When `#PROMPT#` suggests a strong world or scene identity, idealize a cool animated background concept early as part of the narrative fantasy.

Treat that background as:
- a worldbuilding and atmosphere layer
- supportive of the focal identity and primary play fantasy
- visually secondary to gameplay readability, action clarity, and core interactives
- a true authored world concept rather than a stock backdrop with themed wording layered on top

You may suggest background-facing ideas such as:
- ambient motion
- subtle scene animation
- palette or lighting shifts
- secondary particle atmospherics
- reactive environmental mood changes tied to player activity
- signature world cues that later stages can build into a recognizable animated scene foundation

Do not frame the background as:
- the main mechanic
- the main objective source
- the dominant source of visual weight during play
- a justification for clutter, distraction, or reduced readability
- a cheap static stock image that merely gets tolerated or decorated later

When useful, leave concise guidance for later stages that the background may react to interaction in subtle, non-mechanical ways while remaining decorative and secondary.

The narrative stage should imagine the authored world clearly enough that later stages can replace generic stock scene ownership rather than merely polish around it.

## Remix Theme Design System Artifact

In addition to the normal narrative outputs, create a compact design-system artifact named:

`remix_theme.json`

This file should describe the intended visual system for the remix in a way that later visual stages can apply consistently instead of improvising one-off styling decisions.

`remix_theme.json` should include compact, implementation-oriented guidance for:
- core palette roles
- the mapping from current/default colors into remix-appropriate colors
- primary shape language
- border radius / corner logic
- panel / card / button treatment
- line / stroke feel
- shadow / glow feel
- typography tone
- texture / pattern guidance
- focal actor styling cues
- background / environment styling cues
- hazard / collectible / CTA differentiation rules
- visual do / do-not rules so later stages preserve consistency

When possible, define this as a role-based mapping system rather than a loose mood board.

Good examples of the kind of mapping logic you should define:
- current neutral UI grays -> aged parchment, brass, smoke, or deep spellbook tones
- current bright arcade accents -> slime green, portal cyan, toxic violet, or neon hazard signals
- current rounded toy shapes -> sharper occult geometry, soft cartoon blobs, industrial bevels, or clean sci-fi capsules depending on `#PROMPT#`
- current generic button treatment -> specific remix CTA style with fill, border, highlight, and pressed-state guidance

Requirements:
- keep `remix_theme.json` compact but concrete
- prefer role names and transformation rules over raw exhaustive values alone
- the artifact must help later stages map existing colors, shapes, and UI treatments into the target authored style
- the artifact must stay visually subordinate to gameplay clarity and mobile readability
- the artifact should reinforce the authored world, focal identity, and animated background philosophy already defined above

Later visual stages should be able to read `remix_theme.json` and immediately understand how to restyle the current game into a coherent design system.

If you cannot safely complete the stage:
- still write `operator_result_contract.json`
- set its `status` to `error`
- describe the blocker in `detail`
