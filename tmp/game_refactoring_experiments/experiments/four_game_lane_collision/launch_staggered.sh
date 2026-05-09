#!/bin/zsh
set -euo pipefail

EXPERIMENT_DIR=/Users/hassan/repos/game_agent/tmp/game_refactoring_experiments/experiments/four_game_lane_collision
echo "[experiment] dir=$EXPERIMENT_DIR"
echo "[experiment] plan=$EXPERIMENT_DIR/metadata/experiment_plan.json"

echo "[launch] job_01 game_id=gamezone-0f3dc736-8159-48cf-93d0-bd78a54b8cd0 prompt='rick and morty'"
python3 /Users/hassan/repos/game_agent/tools/game_refactoring/scripts/creative_refactor_cli.py --json start-batch --manifest /Users/hassan/repos/game_agent/tmp/game_refactoring_experiments/experiments/four_game_lane_collision/manifests/job_01__gamezone-0f3dc736-8159-48cf-93d0-bd78a54b8cd0.json --run-id run_lane_collision_20260509T002856Z_job_01_rick-and-morty --runs-root /Volumes/backup/output/remixed --pipeline v2 --source-mode inplace --model gpt-5.4 --max-concurrency 1 --agent-timeout 3600 --remix-prompt-file /Users/hassan/repos/game_agent/tmp/game_refactoring_experiments/experiments/four_game_lane_collision/prompts/job_01__rick-and-morty.txt 2>&1 | tee /Users/hassan/repos/game_agent/tmp/game_refactoring_experiments/experiments/four_game_lane_collision/logs/job_01__launch.log

echo "[sleep] waiting 60s before next launch"
sleep 60

echo "[launch] job_02 game_id=gamezone-27ce7533-9ca8-46f9-96b6-2463b3441495 prompt='harry potter'"
python3 /Users/hassan/repos/game_agent/tools/game_refactoring/scripts/creative_refactor_cli.py --json start-batch --manifest /Users/hassan/repos/game_agent/tmp/game_refactoring_experiments/experiments/four_game_lane_collision/manifests/job_02__gamezone-27ce7533-9ca8-46f9-96b6-2463b3441495.json --run-id run_lane_collision_20260509T002856Z_job_02_harry-potter --runs-root /Volumes/backup/output/remixed --pipeline v2 --source-mode inplace --model gpt-5.4 --max-concurrency 1 --agent-timeout 3600 --remix-prompt-file /Users/hassan/repos/game_agent/tmp/game_refactoring_experiments/experiments/four_game_lane_collision/prompts/job_02__harry-potter.txt 2>&1 | tee /Users/hassan/repos/game_agent/tmp/game_refactoring_experiments/experiments/four_game_lane_collision/logs/job_02__launch.log

echo "[sleep] waiting 60s before next launch"
sleep 60

echo "[launch] job_03 game_id=gamezone-021fa461-bb56-4b35-ab57-25d8b29813e1 prompt='my mom is a meme'"
python3 /Users/hassan/repos/game_agent/tools/game_refactoring/scripts/creative_refactor_cli.py --json start-batch --manifest /Users/hassan/repos/game_agent/tmp/game_refactoring_experiments/experiments/four_game_lane_collision/manifests/job_03__gamezone-021fa461-bb56-4b35-ab57-25d8b29813e1.json --run-id run_lane_collision_20260509T002856Z_job_03_my-mom-is-a-meme --runs-root /Volumes/backup/output/remixed --pipeline v2 --source-mode inplace --model gpt-5.4 --max-concurrency 1 --agent-timeout 3600 --remix-prompt-file /Users/hassan/repos/game_agent/tmp/game_refactoring_experiments/experiments/four_game_lane_collision/prompts/job_03__my-mom-is-a-meme.txt 2>&1 | tee /Users/hassan/repos/game_agent/tmp/game_refactoring_experiments/experiments/four_game_lane_collision/logs/job_03__launch.log

echo "[sleep] waiting 60s before next launch"
sleep 60

echo "[launch] job_04 game_id=gamezone-2b68136d-91f0-43a1-992b-4cef879ef733 prompt='demon hunters anime'"
python3 /Users/hassan/repos/game_agent/tools/game_refactoring/scripts/creative_refactor_cli.py --json start-batch --manifest /Users/hassan/repos/game_agent/tmp/game_refactoring_experiments/experiments/four_game_lane_collision/manifests/job_04__gamezone-2b68136d-91f0-43a1-992b-4cef879ef733.json --run-id run_lane_collision_20260509T002856Z_job_04_demon-hunters-anime --runs-root /Volumes/backup/output/remixed --pipeline v2 --source-mode inplace --model gpt-5.4 --max-concurrency 1 --agent-timeout 3600 --remix-prompt-file /Users/hassan/repos/game_agent/tmp/game_refactoring_experiments/experiments/four_game_lane_collision/prompts/job_04__demon-hunters-anime.txt 2>&1 | tee /Users/hassan/repos/game_agent/tmp/game_refactoring_experiments/experiments/four_game_lane_collision/logs/job_04__launch.log

