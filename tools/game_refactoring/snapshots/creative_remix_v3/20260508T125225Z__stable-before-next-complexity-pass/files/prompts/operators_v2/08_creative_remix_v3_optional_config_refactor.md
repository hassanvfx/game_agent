# Operator v2 Stage 08: Creative Remix V3 Optional Config Refactor

You are the optional-config refactor operator for the `creative_remix_v3` workflow.

Work only inside the provided workspace.

## Optional Workflow Artifacts (Use If Present)

These are optional reference artifacts created by earlier or adjacent stages.

Use them when present to stay aligned.
Do not fail just because some are missing unless your current stage is explicitly responsible for creating them.

### From `remix_inference`
- `Blueprint.md`
- `Identity.json`
- `RecreationPrompt.md`
- `RemixDelta.md`

### From `gameplay_refine`
- `gameplay_refine_simulation.md`

### From `visuals_refine`
- `visuals_refine_state_machine.md`
- `screens_01`, `screens_02`, etc. if present
- screenshots / captured screen references if present

### From `optional_config_refactor`
- `asset_slot_bounding_boxes.md`
- `optional_config_usage.md`

## Mission

Replace the idea of human-readable obfuscation with a more useful runtime-ready refactor.

Your job is to refactor the current game so it can opportunistically accept a normalized `optional_config` contract at runtime, while preserving gameplay, preserving existing bounding boxes, and preserving a valid fallback experience when no external assets or theme values are provided.

This is not a pipeline-infrastructure task.
Do not modify the pipeline engine.
Implement the scaffold, runtime parsing, merge logic, docs, and fallback behavior inside the game workspace itself.

## Core Outcome

By the end of this stage, the game should be clearer, more configurable, and better prepared to accept theme/catalog-style runtime overrides through:

- URL params
- a browser event named `game-configs`

The game must still work normally without any provided config.

You must read optional config inputs from URL reliably and apply recognized fields consistently.
You must also expose a small host-observer event contract for native/embed layers when convenient and safe.

This stage should now be conservative by default:
- do not destabilize controls
- do not reshape gameplay-facing DOM unless clearly necessary
- do not let config plumbing alter core interaction behavior
- prefer adding optional hooks over invasive restructuring

## Hard Constraints

- DO NOT change core mechanics, rules, or win/loss behavior
- DO NOT require external config for the game to function
- DO NOT force every slot to be used
- DO NOT map assets to unsafe or semantically mismatched roles
- DO NOT break mobile layout
- DO NOT break control reachability, gesture behavior, or input actionability
- DO NOT grow gameplay bounding boxes just to fit replacement art
- DO NOT turn the game into a framework rewrite
- DO NOT depend on pipeline/runtime infrastructure changes outside the workspace
- DO NOT restructure control wrappers, gameplay-facing containers, or interaction zones unless absolutely necessary

## Main Refactor Goals

You must:

1. scaffold a normalized `optional_config`
2. implement URL param parsing
3. implement a `game-configs` event listener
4. merge defaults + URL config + runtime event config safely
5. apply theme and asset overrides only where safe
6. preserve a fully valid procedural/native fallback when overrides are absent
7. create documentation and ASCII diagrams for:
   - replaceable asset regions / bounding boxes
8. keep the result repairable by the final mobile repair stage

## Required Runtime Contract

Create and use a normalized object named `optional_config`.

It should support fields like:

```js
const defaultOptionalConfig = {
  music: true,
  primaryColor: null,
  secondaryColor: null,
  accentColor: null,
  sceneBgImage: null,
  sceneBgOverlayImage: null,
  logoImage: null,

  heroSpriteActive: null,
  heroSpriteIdle: null,
  opponentSpriteActive: null,
  opponentSpriteIdle: null,
  npcSprite1: null,
  npcSprite2: null,
  pickupSprite: null,
  hazardSprite: null,
  toolSprite: null,
  projectileSprite: null,
  vehicleSprite: null,
  petSprite: null,
  scenePropSprite1: null,
  scenePropSprite2: null,
  scenePropSprite3: null,
  buttonIconPrimary: null,
  buttonIconSecondary: null,
  badgeIcon: null,
  portraitImage: null,
};
```

You may add small adjacent fields if the game clearly needs them, but stay conservative.

## Required Injection Paths

### 1. URL params

Support reading config from URL params.

Use code like:

```js
function parseBoolean(value, fallback) {
  if (value == null) return fallback;
  const v = String(value).toLowerCase().trim();
  if (["1", "true", "yes", "on"].includes(v)) return true;
  if (["0", "false", "no", "off"].includes(v)) return false;
  return fallback;
}

function parseString(value, fallback = null) {
  if (value == null) return fallback;
  const v = String(value).trim();
  return v ? v : fallback;
}

function readOptionalConfigFromUrl(search = window.location.search) {
  const params = new URLSearchParams(search);
  return {
    music: parseBoolean(params.get("music"), defaultOptionalConfig.music),
    primaryColor: parseString(params.get("primaryColor")),
    secondaryColor: parseString(params.get("secondaryColor")),
    accentColor: parseString(params.get("accentColor")),
    sceneBgImage: parseString(params.get("sceneBgImage")),
    sceneBgOverlayImage: parseString(params.get("sceneBgOverlayImage")),
    logoImage: parseString(params.get("logoImage")),
    heroSpriteActive: parseString(params.get("heroSpriteActive")),
    heroSpriteIdle: parseString(params.get("heroSpriteIdle")),
    opponentSpriteActive: parseString(params.get("opponentSpriteActive")),
    opponentSpriteIdle: parseString(params.get("opponentSpriteIdle")),
    npcSprite1: parseString(params.get("npcSprite1")),
    npcSprite2: parseString(params.get("npcSprite2")),
    pickupSprite: parseString(params.get("pickupSprite")),
    hazardSprite: parseString(params.get("hazardSprite")),
    toolSprite: parseString(params.get("toolSprite")),
    projectileSprite: parseString(params.get("projectileSprite")),
    vehicleSprite: parseString(params.get("vehicleSprite")),
    petSprite: parseString(params.get("petSprite")),
    scenePropSprite1: parseString(params.get("scenePropSprite1")),
    scenePropSprite2: parseString(params.get("scenePropSprite2")),
    scenePropSprite3: parseString(params.get("scenePropSprite3")),
    buttonIconPrimary: parseString(params.get("buttonIconPrimary")),
    buttonIconSecondary: parseString(params.get("buttonIconSecondary")),
    badgeIcon: parseString(params.get("badgeIcon")),
    portraitImage: parseString(params.get("portraitImage")),
  };
}
```

Do not read only a narrow subset if the game can safely support more recognized fields.
Recognized URL parameters should be normalized consistently through the same pass.

### 2. `game-configs` event

Support runtime override via a browser event named `game-configs`.

Use code like:

```js
let runtimeEventConfig = {};

window.addEventListener("game-configs", (event) => {
  const detail = event?.detail && typeof event.detail === "object" ? event.detail : {};
  runtimeEventConfig = { ...runtimeEventConfig, ...detail };
  applyOptionalConfig(resolveOptionalConfig());
});
```

## Required Merge / Normalization Logic

Use a safe normalization pass.

Use code like:

```js
function normalizeOptionalConfig(raw = {}) {
  return {
    ...defaultOptionalConfig,
    ...raw,
    music: parseBoolean(raw.music, defaultOptionalConfig.music),
    primaryColor: parseString(raw.primaryColor),
    secondaryColor: parseString(raw.secondaryColor),
    accentColor: parseString(raw.accentColor),
  };
}

function resolveOptionalConfig() {
  const fromUrl = readOptionalConfigFromUrl();
  return normalizeOptionalConfig({
    ...defaultOptionalConfig,
    ...fromUrl,
    ...runtimeEventConfig,
  });
}
```

Precedence rule must be:

1. defaults
2. URL params
3. runtime `game-configs` event overrides URL values

If `music=false` is supplied through URL or the runtime event, treat it as a hard mute instruction.
That means:
- mute active audio immediately when feasible
- prevent autoplay/background loop start
- suppress future sound playback until re-enabled
- do not merely lower volume cosmetically while leaving sound behavior effectively active

## Theme Application Rule

Theme changes must remain safe and readable.

Use code like:

```js
function getContrastTextColor(hex, fallback = "#ffffff") {
  if (!hex || typeof hex !== "string") return fallback;
  const normalized = hex.replace("#", "").trim();
  if (!/^[0-9a-fA-F]{6}$/.test(normalized)) return fallback;

  const r = parseInt(normalized.slice(0, 2), 16);
  const g = parseInt(normalized.slice(2, 4), 16);
  const b = parseInt(normalized.slice(4, 6), 16);
  const luminance = (0.299 * r + 0.587 * g + 0.114 * b) / 255;

  return luminance > 0.6 ? "#111111" : "#ffffff";
}

function applyThemeConfig(config) {
  const root = document.documentElement;

  if (config.primaryColor) {
    root.style.setProperty("--theme-primary", config.primaryColor);
    root.style.setProperty("--theme-primary-contrast", getContrastTextColor(config.primaryColor));
  }

  if (config.secondaryColor) {
    root.style.setProperty("--theme-secondary", config.secondaryColor);
    root.style.setProperty("--theme-secondary-contrast", getContrastTextColor(config.secondaryColor));
  }

  if (config.accentColor) {
    root.style.setProperty("--theme-accent", config.accentColor);
    root.style.setProperty("--theme-accent-contrast", getContrastTextColor(config.accentColor));
  }

  if (config.sceneBgImage) {
    root.style.setProperty("--theme-scene-bg-image", `url("${config.sceneBgImage}")`);
  }
}
```

## Asset Override Rule

Use asset overrides opportunistically and conservatively.

If a safe semantic match exists, apply it.
If not, ignore that slot.

Never force a weapon-like slot into a puzzle-only role.
Never force a hazard slot into a hero slot.
Never replace a working game visual with semantically mismatched art just because an asset was provided.

## Dual Display Rule: Sprite or Native Fallback

Every overrideable visual role should support:

- asset-backed rendering when a valid asset URL is provided
- procedural/native rendering when no override is provided

Use code like:

```js
function applyVisualSlot({
  element,
  assetUrl,
  fallbackClass,
  backgroundSize = "cover",
}) {
  if (!element) return;

  element.classList.remove("use-procedural-fallback", fallbackClass);

  if (assetUrl) {
    element.style.backgroundImage = `url("${assetUrl}")`;
    element.style.backgroundRepeat = "no-repeat";
    element.style.backgroundPosition = "center";
    element.style.backgroundSize = backgroundSize;
    element.dataset.renderMode = "asset";
    return;
  }

  element.style.backgroundImage = "";
  element.dataset.renderMode = "fallback";
  element.classList.add("use-procedural-fallback");
  if (fallbackClass) element.classList.add(fallbackClass);
}
```

## Bounding-Box Preservation Rule

Asset replacement must preserve the current gameplay footprint.

Use code like:

```js
function lockBoundingBox(element, width, height) {
  if (!element) return;
  element.style.width = `${width}px`;
  element.style.height = `${height}px`;
  element.style.minWidth = `${width}px`;
  element.style.minHeight = `${height}px`;
  element.style.maxWidth = `${width}px`;
  element.style.maxHeight = `${height}px`;
  element.style.flex = "0 0 auto";
  element.style.overflow = "hidden";
}
```

If the current game already has reliable sizing, preserve it rather than replacing it blindly.

## Gameplay Preservation Rule

Do not introduce synthetic runtime difficulty progression.
Do not layer an abstract level-scaling system on top of the game if the original game does not already support it naturally.

This stage should not invent a new progression model.
Keep gameplay behavior close to the natural baseline and focus on safe optional theme/asset/config hooks only.

## Required Asset Mapping Documentation

Create a workspace artifact named:

`asset_slot_bounding_boxes.md`

This file must include ASCII diagrams showing:
- replaceable visual roles
- their approximate bounding boxes
- whether they currently render procedurally or via image/sprite
- what optional config slot can safely replace them
- whether fallback rendering remains valid

Example style:

```text
[ hero box 64x64 ]  -> heroSpriteActive | fallback: procedural hero shape
[ enemy box 56x56 ] -> opponentSpriteActive | fallback: native enemy art
[ prop box 40x40 ]  -> scenePropSprite1 | fallback: decorative primitive
```

## Required Usage Documentation

Create a workspace artifact named:

`optional_config_usage.md`

It must explain:
- supported URL params
- supported `game-configs` event payload
- precedence rules
- fallback rules
- examples for runtime usage

Include example event dispatch:

```js
window.dispatchEvent(new CustomEvent("game-configs", {
  detail: {
    music: false,
    primaryColor: "#6a3dad",
    secondaryColor: "#f4c542",
    heroSpriteActive: "https://example.com/hero.png",
    sceneBgImage: "https://example.com/bg.jpg"
  }
}));
```

## Native / Host Observer Event Contract

In addition to reading optional config, expose a small host-observer event contract for native/embed layers.

Use these names:

- `start-level`
- `up-coin`
- `up-bonus`
- `down-damage`
- `up-progress`
- `fail-level`
- `complete-level`

Rules:
- `start-level` should be emitted when a real level/session/run starts
- `complete-level` should be emitted on successful completion
- `fail-level` should be emitted on death, fail state, or loss-screen entry
- the others are opportunistic and should be emitted only when the actual mechanic exists
- do not fabricate events for mechanics the game does not have
- keep payloads small, structured, and useful
- do not let event plumbing destabilize gameplay

Use code like:

```js
function emitGameEvent(name, detail = {}) {
  window.dispatchEvent(new CustomEvent(name, { detail }));
}
```

Example emissions:

```js
emitGameEvent("start-level", {});

emitGameEvent("up-coin", {
  amount: 1,
  totalCoins
});

emitGameEvent("up-bonus", {
  type: "powerup",
  totalBonuses
});

emitGameEvent("down-damage", {
  amount: 1,
  remainingHealth
});

emitGameEvent("up-progress", {
  progress: 0.45,
  checkpoint: "midway"
});

emitGameEvent("fail-level", {
  reason: "health_depleted",
  score
});

emitGameEvent("complete-level", {
  score,
  result: "win"
});
```

When present, align these event semantics with the actual game loop and visible runtime states.

## Required Code Integration

There should be a clear single entrypoint for applying the config.

Use code like:

```js
function applyOptionalConfig(config) {
  applyThemeConfig(config);

  applyVisualSlot({
    element: document.querySelector(".hero"),
    assetUrl: config.heroSpriteActive,
    fallbackClass: "hero-fallback",
    backgroundSize: "cover",
  });

  applyVisualSlot({
    element: document.querySelector(".enemy"),
    assetUrl: config.opponentSpriteActive,
    fallbackClass: "enemy-fallback",
    backgroundSize: "cover",
  });
}

const activeOptionalConfig = resolveOptionalConfig();
applyOptionalConfig(activeOptionalConfig);
```

## Visual Indicator Rule

If the game already has a safe lightweight status cue, you may preserve it.
Do not introduce new progression/HUD indicators unless they are clearly safe, already supported, and do not add clutter or actionability risk.

## Final Safety Rule

This stage should make the game:
- more configurable
- more reusable for theme/catalog injection
- more understandable
- observable by native/embed layers through small stable events
- still safe without config
- still repairable by the final mobile repair stage

If a config-related enhancement introduces meaningful risk to controls, taps, gesture flow, or mobile actionability, skip or reduce that enhancement.
Stable controls are more important than config completeness.

## Required Output Artifacts

At minimum, create or update:
- code implementing the optional config scaffold
- `optional_config_usage.md`
- `asset_slot_bounding_boxes.md`
- `operator_result_contract.json`

## Output Requirements

Write a JSON file named `operator_result_contract.json` in the workspace.

Minimum required shape:
```json
{
  "status": "ok",
  "detail": "Implemented a normalized optional_config runtime scaffold with conservative theme/asset overrides and documentation."
}
```

Allowed `status` values:
- `ok`
- `warning`
- `error`

Use:
- `ok` when the refactor safely added runtime config scaffolding, fallback-safe asset/theme overrides, and documentation
- `warning` when only partial implementation was possible due to structural constraints
- `error` when you could not safely perform the refactor

End stdout with exactly these lines:
```text
OPERATOR STATUS: completed|failed
CHANGED FILES: file1, file2 or NONE
SUMMARY: one short sentence
MECHANICS CHECK: preserved|issues
VISUAL CHECK: preserved|updated|issues
AUDIO CHECK: integrated|not_applicable|issues
MOBILE CHECK: safe|not_checked|issues