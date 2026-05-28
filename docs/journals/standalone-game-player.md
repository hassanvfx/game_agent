# Standalone Game Player Implementation Journal

**Last Updated:** 2026-05-27  
**Feature Spec:** Standalone fullscreen HTML player extracted from `dashboard/annotator_template.html`  
**Backend Reference:** N/A

---

## 📊 Implementation Status Overview

### ✅ Phase 1: Extraction Planning - **COMPLETE**

- [x] Inspect fullscreen player shell in `dashboard/annotator_template.html`
- [x] Identify reusable layout, controls, and iframe behavior
- [x] Define standalone URL-driven player requirements

**Status:** ✅ Complete

### Phase 2: Standalone Player Build - **COMPLETE**

- [x] Create dedicated `tools/game_player/` workspace
- [x] Implement standalone HTML player with base64 URL input
- [x] Preserve player-shell UX including open-window action and connecting state
- [x] Add automatic portrait/landscape layout behavior based on browser size
- [x] Add minimal FriendJam-or-title chrome
- [x] Add settings modal with aspect ratio and pixelScale controls

**Status:** ✅ Complete

### Phase 3: Verification - **IN PROGRESS**

- [ ] Verify missing-param behavior shows "Connecting"
- [ ] Verify valid encoded URL renders iframe
- [ ] Verify title fallback remains FriendJam when iframe title is unavailable
- [ ] Verify ratio presets and pixelScale apply correctly

**Status:** In Progress

---

## 📝 Journal Entries

### 2026-05-27 19:08 - Initial Setup

**What Changed:**
- Created journal structure for the standalone game player task
- Documented extraction goal from the annotator fullscreen modal
- Captured the dedicated workspace requirement under `tools/game_player/`

**Why:**
The repo requires a task journal for all work. This task is a focused extraction of the fullscreen player shell into a self-contained HTML entry point that accepts a base64-encoded URL and renders it inside an iframe.

**Files Created:**
- `docs/journals/standalone-game-player.md` - Task journal for player extraction work

**Next Steps:**
- [x] Create `tools/game_player/` workspace files
- [x] Build standalone player HTML
- [ ] Verify loading, open-window, and invalid-input states

**Status:** In Progress

---

### 2026-05-27 19:22 - Responsive layout and modal settings refinement

**Achievement:**
Upgraded the standalone player from a single fixed shell into a responsive FriendJam-branded player that automatically switches layout by browser orientation and keeps advanced viewport controls inside a settings modal.

**Implementation Details:**
- Modified `tools/game_player/index.html` - Replaced the original single-column topbar layout with:
  - automatic portrait/landscape shell behavior
  - left title rail in landscape
  - minimal FriendJam-or-title chrome
  - settings modal for aspect ratio and `pixelScale`
- Preserved base64 URL loading and popup open behavior
- Added iframe-title probing with graceful fallback to `FriendJam` when cross-origin access blocks title reads

**Technical Decisions:**
- Layout is determined from browser dimensions rather than a user setting, matching the requested behavior.
- The visible chrome was reduced to only the title plus controls.
- Aspect ratio and scale remain user-controlled, but layout mode is no longer configurable.
- Title extraction attempts to read `iframe.contentWindow.document.title` only when possible, while safely degrading for cross-origin embeds.

**Testing:**
- Manual verification still pending in-browser.
- Expected checks:
  - no `url_b64` shows connecting card
  - valid `url_b64` loads iframe and enables Open button
  - landscape browser size shows left title rail
  - portrait browser size shows top title bar
  - settings modal updates ratio and `pixelScale`

**Next Steps:**
- [ ] Verify responsive layout in browser
- [ ] Verify settings modal changes apply correctly
- [ ] Verify title fallback behavior for cross-origin iframes

**Status:** In Progress

---

### 2026-05-27 19:25 - Dual query input support

**Achievement:**
Extended the player entrypoint to accept either a plain query URL or a base64-encoded one.

**Implementation Details:**
- Modified `tools/game_player/index.html` so target resolution now supports:
  - `?url=https%3A%2F%2Fexample.com%2Fgame%2F`
  - `?url_b64=...`
- Updated the empty-state helper copy so the supported formats are visible in the UI.

**Technical Decisions:**
- Plain `url` is checked first because it is easier to author manually in a browser.
- `url_b64` remains supported for safer transport when callers prefer opaque encoded values.
- Both flows still enforce `http:` / `https:` only.

**Next Steps:**
- [ ] Verify plain `?url=` launch works
- [ ] Verify `?url_b64=` launch still works

**Status:** In Progress

---

### 2026-05-27 20:09 - Professional dark-neon visual pass

**Achievement:**
Restyled the standalone player into a darker premium interface with restrained neon accents and integrated the provided FriendJam logo as a rounded-square app icon treatment.

**Implementation Details:**
- Modified `tools/game_player/index.html` visual system to use:
  - deep indigo / near-black backgrounds
  - soft cyan / violet glow accents
  - darker glass-style title rail, topbar, modal, and status cards
  - upgraded iframe stage framing with subtle neon edge lighting
- Added the provided external FriendJam logo URL into both title contexts:
  - portrait top bar
  - landscape title rail
- Styled the logo as a compact rounded-square app icon with a professional border and restrained glow

**Technical Decisions:**
- The theme was intentionally kept product-like and readable instead of overly playful.
- Neon accents are limited to edge-lighting, CTA emphasis, and background atmosphere.
- The visual pass did not alter player behavior, query parsing, layout switching, or settings logic.

**Next Steps:**
- [ ] Verify the dark visual system in browser
- [ ] Verify the remote logo renders reliably
- [ ] Verify contrast/readability in portrait and landscape

**Status:** In Progress

---

### 2026-05-27 20:38 - Share-first chrome and title polling refinement

**Achievement:**
Simplified the player chrome further and added a longer-lived iframe title watcher so the UI title and browser window title can update when the iframe title becomes available later during load.

**Implementation Details:**
- Modified `tools/game_player/index.html` to:
  - remove the visible settings UI and dynamic viewport controls
  - replace the Open action with a Share action that copies the current page URL
  - show temporary copied feedback using a checkmark state
  - remove the landscape top bar and keep landscape chrome in the left rail only
  - simplify the player frame to default to full parent height with a 9:16 shape
  - poll once per second for up to 60 seconds for an iframe title
  - shorten the visible app title to the first 18 characters when a title is found
  - set the browser title to `FriendJam - <full game title>` when available

**Technical Decisions:**
- Share was chosen over Open to better fit the simplified player shell.
- Continuous title polling is still best-effort because cross-origin iframes may block title access.
- The UI uses a shortened title for cleaner chrome while the browser tab preserves the full title.

**Next Steps:**
- [ ] Verify delayed iframe title updates are reflected within the 60s polling window
- [ ] Verify short UI title and full browser title formatting
- [ ] Verify share copied state works in both portrait and landscape

**Status:** In Progress

---

### 2026-05-27 21:05 - True contain sizing for portrait and landscape

**Achievement:**
Replaced the previous CSS-only frame sizing with proper contain sizing so the 9:16 player fits inside the available stage without portrait overflow.

**Implementation Details:**
- Modified `tools/game_player/index.html` to compute the largest 9:16 rectangle that fits within the available `iframe-wrap` area.
- Added a stage sizing function that:
  - measures available width and height
  - derives frame width from height first
  - falls back to width-constrained sizing when needed
  - applies exact pixel width/height to the player frame
- Added `ResizeObserver` support so the frame re-fits when the stage changes size.
- Removed the mobile override that was previously forcing the frame to stretch to full width and full height.

**Technical Decisions:**
- Using explicit contain math is more reliable than mixing `height: 100%`, `width: auto`, `max-width`, and mobile overrides.
- The frame remains horizontally centered by the flex parent while respecting hard bounds.

**Next Steps:**
- [ ] Verify portrait no longer overflows vertically
- [ ] Verify portrait width remains centered when constrained
- [ ] Verify landscape still fills height correctly

**Status:** In Progress

---

### 2026-05-27 21:11 - Darkened shell and flattened landscape panel chrome

**Achievement:**
Refined the visual shell so the main stage reads much darker and the landscape side panel no longer feels like a card nested inside another card.

**Implementation Details:**
- Modified `tools/game_player/index.html` to:
  - darken the global shell and main stage toward a near-pitch-black center
  - bring the top bar and landscape rail much closer to the same dark tone
  - remove the inner card treatment from the landscape rail content block
  - keep the viewport glow and frame outline intact

**Technical Decisions:**
- The viewport glow around the playable frame was preserved because it provides useful separation from the background.
- The landscape rail now behaves more like a true sidebar surface rather than a surface containing another floating card.

**Next Steps:**
- [ ] Verify the shell reads darker without hurting contrast
- [ ] Verify the landscape rail no longer feels double-layered
- [ ] Verify the frame glow still looks balanced against the darker background

**Status:** In Progress

---

### 2026-05-27 21:22 - Query-driven title handling and poller removal

**Achievement:**
Simplified the title system by removing unreliable iframe title polling and switching to an explicit optional `title` query parameter.

**Implementation Details:**
- Modified `tools/game_player/index.html` to:
  - add optional `?title=...` query support
  - use the first 18 characters of `title` for the visible UI title when provided
  - use `FriendJam - <full title>` for the browser title when provided
  - keep `Play Now` / `FriendJam` fallbacks when `title` is absent
  - remove cross-origin iframe title polling logic entirely
- Kept share behavior based on `window.location.href`, which preserves all currently loaded query params automatically.

**Technical Decisions:**
- Query-driven title state is deterministic and avoids the unreliability of cross-origin iframe title reads.
- Sharing the full current URL ensures `url`, `url_b64`, `title`, and any future params are preserved without custom URL rebuilding.

**Next Steps:**
- [ ] Verify `title` param updates visible title and browser title correctly
- [ ] Verify share keeps all query params intact
- [ ] Verify fallback title remains `Play Now` when `title` is omitted

**Status:** In Progress

---

### 2026-05-27 21:24 - Title param overwrite fix

**Achievement:**
Fixed a regression where the query-driven title was parsed correctly on startup but then overwritten during player load.

**Implementation Details:**
- Modified `tools/game_player/index.html` so both `showPlayer()` and `showStatus()` re-apply the active query-driven title instead of forcing the fallback title.
- Centralized query-title access through a small helper so the behavior stays consistent across initialization and state changes.

**Technical Decisions:**
- The player should treat the query param as the source of truth for title state whenever it exists.
- Fallback to `Play Now` now happens only when no explicit title was provided.

**Next Steps:**
- [ ] Verify the provided `title` param remains visible after iframe load
- [ ] Verify fallback still works when `title` is absent

**Status:** In Progress

---

### 2026-05-27 21:39 - Mixpanel heartbeat and lifecycle analytics

**Achievement:**
Added Mixpanel browser analytics to the standalone player with a 5-second alive heartbeat and lifecycle/share tracking.

**Implementation Details:**
- Modified `tools/game_player/index.html` to load Mixpanel from the browser CDN using token `919399d0433ce2ef7ba9e515b1c8567a`.
- Added tracked events:
  - `player_page_loaded`
  - `player_iframe_loaded`
  - `share_clicked`
  - `share_copied`
  - `play_alive` every 5 seconds
  - `player_session_ended`
- Added event properties on all analytics calls:
  - `product: "friendjam-webplayer"`
  - iframe target `url`
  - query-driven `title`
  - optional `gameId`
  - `page_url`
  - `layout_mode`
  - viewport width / height
  - elapsed time

**Technical Decisions:**
- `player_page_loaded` is sent immediately, while `play_alive` begins on the first 5-second interval rather than also firing at `0s`.
- Share analytics reuse `window.location.href`, so copied URLs and tracked context stay aligned.
- Session end is emitted on `pagehide` / `beforeunload` with duration.

**Next Steps:**
- [ ] Verify Mixpanel loads successfully from CDN
- [ ] Verify `play_alive` fires every 5 seconds after startup
- [ ] Verify `gameId`, `title`, and target `url` are attached to all events

**Status:** In Progress

---

### 2026-05-27 22:01 - Mixpanel bootstrap initialization fix

**Achievement:**
Fixed the standalone player's Mixpanel startup path so the browser SDK is initialized through a supported bootstrap flow instead of direct script injection.

**Implementation Details:**
- Modified `tools/game_player/index.html` to replace the previous custom `loadMixpanel()` script append approach with a bootstrap helper that mirrors Mixpanel's expected queued-init pattern.
- Added a dedicated named Mixpanel instance (`friendjam`) and updated analytics dispatch to track through that initialized instance instead of the global root object.
- Preserved the existing event model and shared event properties for:
  - `player_page_loaded`
  - `player_iframe_loaded`
  - `share_clicked`
  - `share_copied`
  - `play_alive`
  - `player_session_ended`

**Technical Decisions:**
- The prior approach loaded `mixpanel-2-latest.min.js` directly and then called `mixpanel.init(...)` after load, which can produce the `"mixpanel" object not initialized` error because it bypasses the expected bootstrap/stub queue.
- Using a named instance avoids ambiguity between the global bootstrap container and the actual tracker used for event emission.
- Browser-extension content-script errors and runtime warnings from the embedded game were treated as unrelated noise because they originate outside the standalone player shell.

**Next Steps:**
- [ ] Verify the Mixpanel initialization error no longer appears in the console
- [ ] Verify the named tracker still sends the existing lifecycle/share/heartbeat events
- [ ] Verify the embedded-game console noise is unchanged and non-blocking

**Status:** In Progress

---

### 2026-05-27 22:08 - App Store install CTA and tappable logo

**Achievement:**
Added a dedicated App Store install CTA to the standalone player and made the FriendJam logo itself open the iOS app listing.

**Implementation Details:**
- Modified `tools/game_player/index.html` to wrap the FriendJam logo in a tappable App Store link in both layouts:
  - portrait top bar
  - landscape title rail
- Added a new `Install App` CTA next to `Share` using an Apple-style white-on-black treatment.
- Reused a shared App Store target URL:
  - `https://apps.apple.com/us/app/id6745799162`
- Kept the CTA placement consistent with the existing chrome instead of moving actions into a separate section.

**Technical Decisions:**
- The install CTA was implemented as a normal anchor so it behaves predictably across mobile and desktop browsers.
- The logo link and the install button share the same destination to reduce ambiguity in the chrome.
- The visual styling intentionally contrasts with the colorful Share button so the install action reads as a platform/store action rather than a gameplay action.

**Next Steps:**
- [ ] Verify the logo opens the App Store link in both portrait and landscape layouts
- [ ] Verify the `Install App` button sits correctly next to `Share`
- [ ] Verify the white-on-black CTA remains readable against the dark shell

**Status:** In Progress

---

### 2026-05-27 22:10 - Install CTA Mixpanel tracking

**Achievement:**
Added Mixpanel tracking for App Store install taps so the install CTA now emits analytics in the same interaction style as the Share action.

**Implementation Details:**
- Modified `tools/game_player/index.html` to attach click handlers to all install links.
- Added a new analytics event:
  - `install_clicked`
- Included extra event context for install taps:
  - `destination_url`
  - `trigger` (`logo` or `button`)
- Kept the shared analytics payload intact so install events also inherit the existing player context:
  - `product`
  - `url`
  - `title`
  - `gameId`
  - `page_url`
  - `layout_mode`
  - viewport metadata
  - elapsed time

**Technical Decisions:**
- The install event mirrors the Share interaction pattern by firing on tap/click rather than on downstream store completion.
- Tracking is bound to both the logo link and the dedicated Install App button so either install surface is measurable.

**Next Steps:**
- [ ] Verify `install_clicked` fires for both logo and button taps
- [ ] Verify the event includes `trigger`, `destination_url`, and the shared player context

**Status:** In Progress

---

## 🐛 Known Issues

### Cross-Origin / Embedding Restrictions

**Problem:** 
Some target URLs may refuse to render in an iframe.

**Root Cause:** 
The destination site may send `X-Frame-Options` or CSP `frame-ancestors` headers.

**Status:** 
- [x] Being investigated
- [ ] Blocked (waiting for...)
- [ ] Fixed

**Workaround:** 
Use the standalone player's Open button to launch the target in a separate window/tab.

**Resolution:** 
Not a bug in the player shell itself; expected browser security behavior.

---

## 📚 Quick Reference

### Key Files

**Frontend:**
- `dashboard/annotator_template.html` - Source fullscreen player shell to extract from
- `tools/game_player/index.html` - Standalone responsive FriendJam player entrypoint
- `docs/journals/standalone-game-player.md` - Task journal

### Important Commands

```bash
# Serve the repo locally from the root
python -m http.server 8000

# Example target player URL pattern
# /tools/game_player/index.html?url_b64=BASE64_ENCODED_TARGET_URL
```

---

## ✅ Testing Checklist

- [ ] Manual testing scenarios:
  - [ ] No param shows "Connecting"
  - [ ] Valid base64 URL loads iframe
  - [ ] Valid plain `url` query loads iframe
  - [ ] Invalid base64 shows graceful status/error
  - [ ] Share button copies current page URL
  - [ ] Share button shows temporary copied checkmark state
  - [ ] Portrait browser shows topbar title layout
  - [ ] Landscape browser shows left title rail layout
  - [ ] Portrait 9:16 frame is fully contained by height/width without overflow
  - [ ] Portrait frame remains centered when width is reduced
  - [ ] Landscape frame remains height-contained
  - [ ] Cross-origin iframe falls back to FriendJam title
  - [ ] Rounded-square logo renders in both portrait and landscape chrome
  - [ ] Title polling updates UI title within 60 seconds when readable
  - [ ] Browser title becomes `FriendJam - <full game title>` when readable
- [ ] Mobile responsive
- [ ] Cross-browser tested

---

## 🎯 Success Criteria

- [x] Standalone fullscreen player extracted
- [x] Accepts base64-encoded URL parameter
- [x] Shows "Connecting" when nothing is passed
- [x] Preserves polished player controls
- [x] Documentation updated
- [ ] Responsive auto-layout verified in browser
- [ ] Settings modal behavior verified in browser
- [ ] Dark visual theme verified in browser

---

*This journal tracks extraction of the annotator fullscreen player into a standalone HTML-only game player.*