#!/bin/zsh
set -euo pipefail

# Batch 01: raw offset 0 limit 100
python3 /Users/hassan/repos/game_agent/tools/game_editorial/scripts/launch_seeded_raw_remix_batch.py --game-limit 100 --raw-game-offset 0 --prompts-per-game 2 --seed-offset 0 --source-mode copy --runs-root /Volumes/HDD2026/output-May17th --workspace-root /Users/hassan/repos/game_agent/tools/game_editorial/scripts/workspace --model gpt-5.5 --agent-timeout 3600 --max-concurrency 2 --poll-seconds 5.0 --stale-heartbeat-seconds 900 --pipeline v2 --json

# Batch 02: raw offset 100 limit 100
python3 /Users/hassan/repos/game_agent/tools/game_editorial/scripts/launch_seeded_raw_remix_batch.py --game-limit 100 --raw-game-offset 100 --prompts-per-game 2 --seed-offset 0 --source-mode copy --runs-root /Volumes/HDD2026/output-May17th --workspace-root /Users/hassan/repos/game_agent/tools/game_editorial/scripts/workspace --model gpt-5.5 --agent-timeout 3600 --max-concurrency 2 --poll-seconds 5.0 --stale-heartbeat-seconds 900 --pipeline v2 --json

# Batch 03: raw offset 200 limit 100
python3 /Users/hassan/repos/game_agent/tools/game_editorial/scripts/launch_seeded_raw_remix_batch.py --game-limit 100 --raw-game-offset 200 --prompts-per-game 2 --seed-offset 0 --source-mode copy --runs-root /Volumes/HDD2026/output-May17th --workspace-root /Users/hassan/repos/game_agent/tools/game_editorial/scripts/workspace --model gpt-5.5 --agent-timeout 3600 --max-concurrency 2 --poll-seconds 5.0 --stale-heartbeat-seconds 900 --pipeline v2 --json

# Batch 04: raw offset 300 limit 100
python3 /Users/hassan/repos/game_agent/tools/game_editorial/scripts/launch_seeded_raw_remix_batch.py --game-limit 100 --raw-game-offset 300 --prompts-per-game 2 --seed-offset 0 --source-mode copy --runs-root /Volumes/HDD2026/output-May17th --workspace-root /Users/hassan/repos/game_agent/tools/game_editorial/scripts/workspace --model gpt-5.5 --agent-timeout 3600 --max-concurrency 2 --poll-seconds 5.0 --stale-heartbeat-seconds 900 --pipeline v2 --json

# Batch 05: raw offset 400 limit 100
python3 /Users/hassan/repos/game_agent/tools/game_editorial/scripts/launch_seeded_raw_remix_batch.py --game-limit 100 --raw-game-offset 400 --prompts-per-game 2 --seed-offset 0 --source-mode copy --runs-root /Volumes/HDD2026/output-May17th --workspace-root /Users/hassan/repos/game_agent/tools/game_editorial/scripts/workspace --model gpt-5.5 --agent-timeout 3600 --max-concurrency 2 --poll-seconds 5.0 --stale-heartbeat-seconds 900 --pipeline v2 --json

# Batch 06: raw offset 500 limit 100
python3 /Users/hassan/repos/game_agent/tools/game_editorial/scripts/launch_seeded_raw_remix_batch.py --game-limit 100 --raw-game-offset 500 --prompts-per-game 2 --seed-offset 0 --source-mode copy --runs-root /Volumes/HDD2026/output-May17th --workspace-root /Users/hassan/repos/game_agent/tools/game_editorial/scripts/workspace --model gpt-5.5 --agent-timeout 3600 --max-concurrency 2 --poll-seconds 5.0 --stale-heartbeat-seconds 900 --pipeline v2 --json

# Batch 07: raw offset 600 limit 100
python3 /Users/hassan/repos/game_agent/tools/game_editorial/scripts/launch_seeded_raw_remix_batch.py --game-limit 100 --raw-game-offset 600 --prompts-per-game 2 --seed-offset 0 --source-mode copy --runs-root /Volumes/HDD2026/output-May17th --workspace-root /Users/hassan/repos/game_agent/tools/game_editorial/scripts/workspace --model gpt-5.5 --agent-timeout 3600 --max-concurrency 2 --poll-seconds 5.0 --stale-heartbeat-seconds 900 --pipeline v2 --json

# Batch 08: raw offset 700 limit 100
python3 /Users/hassan/repos/game_agent/tools/game_editorial/scripts/launch_seeded_raw_remix_batch.py --game-limit 100 --raw-game-offset 700 --prompts-per-game 2 --seed-offset 0 --source-mode copy --runs-root /Volumes/HDD2026/output-May17th --workspace-root /Users/hassan/repos/game_agent/tools/game_editorial/scripts/workspace --model gpt-5.5 --agent-timeout 3600 --max-concurrency 2 --poll-seconds 5.0 --stale-heartbeat-seconds 900 --pipeline v2 --json

# Batch 09: raw offset 800 limit 33
python3 /Users/hassan/repos/game_agent/tools/game_editorial/scripts/launch_seeded_raw_remix_batch.py --game-limit 33 --raw-game-offset 800 --prompts-per-game 2 --seed-offset 0 --source-mode copy --runs-root /Volumes/HDD2026/output-May17th --workspace-root /Users/hassan/repos/game_agent/tools/game_editorial/scripts/workspace --model gpt-5.5 --agent-timeout 3600 --max-concurrency 2 --poll-seconds 5.0 --stale-heartbeat-seconds 900 --pipeline v2 --json
