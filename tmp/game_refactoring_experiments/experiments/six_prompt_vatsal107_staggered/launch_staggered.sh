#!/usr/bin/env bash
set -euo pipefail

cd /Users/hassan/repos/game_agent

echo "Launching job_01 (Harry Potter)"
python3 /Users/hassan/repos/game_agent/tools/game_refactoring/scripts/game_workflow.py --json --id creative_remix_v3 --games-manifest-source /Users/hassan/repos/game_agent/tmp/game_refactoring_experiments/experiments/six_prompt_vatsal107_staggered/manifests/job_01__gamezone-0f3dc736-8159-48cf-93d0-bd78a54b8cd0.json --run-id run_vatsal107_20260509T035800Z_job_01_harry-potter --runs-root /Volumes/HDD2026/output --pipeline v2 --source-mode copy --model gpt-5.4 --max-concurrency 1 --agent-timeout 3600 --remix-prompt-file /Users/hassan/repos/game_agent/tmp/game_refactoring_experiments/experiments/six_prompt_vatsal107_staggered/prompts/job_01__harry-potter.txt > /Users/hassan/repos/game_agent/tmp/game_refactoring_experiments/experiments/six_prompt_vatsal107_staggered/logs/job_01__launch.log 2>&1 &

sleep 60

echo "Launching job_02 (Rick and Morty)"
python3 /Users/hassan/repos/game_agent/tools/game_refactoring/scripts/game_workflow.py --json --id creative_remix_v3 --games-manifest-source /Users/hassan/repos/game_agent/tmp/game_refactoring_experiments/experiments/six_prompt_vatsal107_staggered/manifests/job_02__gamezone-27ce7533-9ca8-46f9-96b6-2463b3441495.json --run-id run_vatsal107_20260509T035800Z_job_02_rick-and-morty --runs-root /Volumes/HDD2026/output --pipeline v2 --source-mode copy --model gpt-5.4 --max-concurrency 1 --agent-timeout 3600 --remix-prompt-file /Users/hassan/repos/game_agent/tmp/game_refactoring_experiments/experiments/six_prompt_vatsal107_staggered/prompts/job_02__rick-and-morty.txt > /Users/hassan/repos/game_agent/tmp/game_refactoring_experiments/experiments/six_prompt_vatsal107_staggered/logs/job_02__launch.log 2>&1 &

sleep 60

echo "Launching job_03 (Flappy Bird)"
python3 /Users/hassan/repos/game_agent/tools/game_refactoring/scripts/game_workflow.py --json --id creative_remix_v3 --games-manifest-source /Users/hassan/repos/game_agent/tmp/game_refactoring_experiments/experiments/six_prompt_vatsal107_staggered/manifests/job_03__gamezone-021fa461-bb56-4b35-ab57-25d8b29813e1.json --run-id run_vatsal107_20260509T035800Z_job_03_flappy-bird --runs-root /Volumes/HDD2026/output --pipeline v2 --source-mode copy --model gpt-5.4 --max-concurrency 1 --agent-timeout 3600 --remix-prompt-file /Users/hassan/repos/game_agent/tmp/game_refactoring_experiments/experiments/six_prompt_vatsal107_staggered/prompts/job_03__flappy-bird.txt > /Users/hassan/repos/game_agent/tmp/game_refactoring_experiments/experiments/six_prompt_vatsal107_staggered/logs/job_03__launch.log 2>&1 &

sleep 60

echo "Launching job_04 (brain rot mom’s day)"
python3 /Users/hassan/repos/game_agent/tools/game_refactoring/scripts/game_workflow.py --json --id creative_remix_v3 --games-manifest-source /Users/hassan/repos/game_agent/tmp/game_refactoring_experiments/experiments/six_prompt_vatsal107_staggered/manifests/job_04__gamezone-2b68136d-91f0-43a1-992b-4cef879ef733.json --run-id run_vatsal107_20260509T035800Z_job_04_brain-rot-mom-s-day --runs-root /Volumes/HDD2026/output --pipeline v2 --source-mode copy --model gpt-5.4 --max-concurrency 1 --agent-timeout 3600 --remix-prompt-file /Users/hassan/repos/game_agent/tmp/game_refactoring_experiments/experiments/six_prompt_vatsal107_staggered/prompts/job_04__brain-rot-mom-s-day.txt > /Users/hassan/repos/game_agent/tmp/game_refactoring_experiments/experiments/six_prompt_vatsal107_staggered/logs/job_04__launch.log 2>&1 &

sleep 60

echo "Launching job_05 (Rick and Morty vibe flappy bird gameplay)"
python3 /Users/hassan/repos/game_agent/tools/game_refactoring/scripts/game_workflow.py --json --id creative_remix_v3 --games-manifest-source /Users/hassan/repos/game_agent/tmp/game_refactoring_experiments/experiments/six_prompt_vatsal107_staggered/manifests/job_05__gamezone-4abe94f0-33b8-4d81-9a80-01c86f2d8acb.json --run-id run_vatsal107_20260509T035800Z_job_05_rick-and-morty-vibe-flappy-bird-gameplay --runs-root /Volumes/HDD2026/output --pipeline v2 --source-mode copy --model gpt-5.4 --max-concurrency 1 --agent-timeout 3600 --remix-prompt-file /Users/hassan/repos/game_agent/tmp/game_refactoring_experiments/experiments/six_prompt_vatsal107_staggered/prompts/job_05__rick-and-morty-vibe-flappy-bird-gameplay.txt > /Users/hassan/repos/game_agent/tmp/game_refactoring_experiments/experiments/six_prompt_vatsal107_staggered/logs/job_05__launch.log 2>&1 &

sleep 60

echo "Launching job_06 (Harry Potter vibe flappy bird gameplay)"
python3 /Users/hassan/repos/game_agent/tools/game_refactoring/scripts/game_workflow.py --json --id creative_remix_v3 --games-manifest-source /Users/hassan/repos/game_agent/tmp/game_refactoring_experiments/experiments/six_prompt_vatsal107_staggered/manifests/job_06__gamezone-ef78bde8-ff87-4fe3-a29d-cad5fc92b485.json --run-id run_vatsal107_20260509T035800Z_job_06_harry-potter-vibe-flappy-bird-gameplay --runs-root /Volumes/HDD2026/output --pipeline v2 --source-mode copy --model gpt-5.4 --max-concurrency 1 --agent-timeout 3600 --remix-prompt-file /Users/hassan/repos/game_agent/tmp/game_refactoring_experiments/experiments/six_prompt_vatsal107_staggered/prompts/job_06__harry-potter-vibe-flappy-bird-gameplay.txt > /Users/hassan/repos/game_agent/tmp/game_refactoring_experiments/experiments/six_prompt_vatsal107_staggered/logs/job_06__launch.log 2>&1 &
