# Playwright Observation Log

- Launch method: local Node static HTTP server rooted at workspace
- Host: 127.0.0.1
- Port: 57258
- Served entry URL: http://127.0.0.1:57258/index.html
- Mobile context: viewport 400x700, screen 400x700, touch enabled, mobile Android-style user agent
- Runtime identity verification: passed

## Interaction steps

### initial load
- Expected: Neon Vault title screen visible
- Actual: title=Neon Relic Vault; heading=NEON VAULT
- Assessment: fails_to_support_bug_hypothesis

### open vault
- Expected: Gameplay screen opens with funds HUD and scan button
- Actual: balance=$2000
- Assessment: fails_to_support_bug_hypothesis

### first scan
- Expected: Button spends $100, reveals relic card, updates balance, remains interactive
- Actual: revealed=SCRAP RELAY; rarity=NORMAL; before=$2000; after=$1900
- Assessment: fails_to_support_bug_hypothesis

### audio safety check
- Expected: Looping background audio volume is at or below 0.2
- Actual: bgm.volume=0.2
- Assessment: confirms_fix

### archive view
- Expected: Archive opens and reflects unlocked progress
- Actual: archive_count=1/5
- Assessment: fails_to_support_bug_hypothesis

## Screenshots captured
- playwright_initial.png: initial_state (neutral) - title=Neon Relic Vault; heading=NEON VAULT
- playwright_game_open.png: opened_game (neutral) - balance=$2000
- playwright_first_reveal.png: first_reveal (neutral) - revealed=SCRAP RELAY; rarity=NORMAL; balance=$1900
- playwright_archive.png: archive_view (neutral) - archive_count=1/5
