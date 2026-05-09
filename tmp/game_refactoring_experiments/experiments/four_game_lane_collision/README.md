# Four-Game Lane Collision Experiment

- experiment_name: `four_game_lane_collision`
- seed: `20260508`
- workflow_id: `creative_remix_v3`
- pipeline: `v2`
- source_mode: `inplace`
- runs_root: `/Volumes/backup/output/remixed`
- stagger_seconds: `60`

## Selected jobs

### job_01
- game_id: `gamezone-0f3dc736-8159-48cf-93d0-bd78a54b8cd0`
- prompt: `rick and morty`
- run_id: `run_lane_collision_20260509T002856Z_job_01_rick-and-morty`
- manifest: `/Users/hassan/repos/game_agent/tmp/game_refactoring_experiments/experiments/four_game_lane_collision/manifests/job_01__gamezone-0f3dc736-8159-48cf-93d0-bd78a54b8cd0.json`
- prompt_file: `/Users/hassan/repos/game_agent/tmp/game_refactoring_experiments/experiments/four_game_lane_collision/prompts/job_01__rick-and-morty.txt`
- launch_log: `/Users/hassan/repos/game_agent/tmp/game_refactoring_experiments/experiments/four_game_lane_collision/logs/job_01__launch.log`

### job_02
- game_id: `gamezone-27ce7533-9ca8-46f9-96b6-2463b3441495`
- prompt: `harry potter`
- run_id: `run_lane_collision_20260509T002856Z_job_02_harry-potter`
- manifest: `/Users/hassan/repos/game_agent/tmp/game_refactoring_experiments/experiments/four_game_lane_collision/manifests/job_02__gamezone-27ce7533-9ca8-46f9-96b6-2463b3441495.json`
- prompt_file: `/Users/hassan/repos/game_agent/tmp/game_refactoring_experiments/experiments/four_game_lane_collision/prompts/job_02__harry-potter.txt`
- launch_log: `/Users/hassan/repos/game_agent/tmp/game_refactoring_experiments/experiments/four_game_lane_collision/logs/job_02__launch.log`

### job_03
- game_id: `gamezone-021fa461-bb56-4b35-ab57-25d8b29813e1`
- prompt: `my mom is a meme`
- run_id: `run_lane_collision_20260509T002856Z_job_03_my-mom-is-a-meme`
- manifest: `/Users/hassan/repos/game_agent/tmp/game_refactoring_experiments/experiments/four_game_lane_collision/manifests/job_03__gamezone-021fa461-bb56-4b35-ab57-25d8b29813e1.json`
- prompt_file: `/Users/hassan/repos/game_agent/tmp/game_refactoring_experiments/experiments/four_game_lane_collision/prompts/job_03__my-mom-is-a-meme.txt`
- launch_log: `/Users/hassan/repos/game_agent/tmp/game_refactoring_experiments/experiments/four_game_lane_collision/logs/job_03__launch.log`

### job_04
- game_id: `gamezone-2b68136d-91f0-43a1-992b-4cef879ef733`
- prompt: `demon hunters anime`
- run_id: `run_lane_collision_20260509T002856Z_job_04_demon-hunters-anime`
- manifest: `/Users/hassan/repos/game_agent/tmp/game_refactoring_experiments/experiments/four_game_lane_collision/manifests/job_04__gamezone-2b68136d-91f0-43a1-992b-4cef879ef733.json`
- prompt_file: `/Users/hassan/repos/game_agent/tmp/game_refactoring_experiments/experiments/four_game_lane_collision/prompts/job_04__demon-hunters-anime.txt`
- launch_log: `/Users/hassan/repos/game_agent/tmp/game_refactoring_experiments/experiments/four_game_lane_collision/logs/job_04__launch.log`

## Launch

```bash
zsh /Users/hassan/repos/game_agent/tmp/game_refactoring_experiments/experiments/four_game_lane_collision/launch_staggered.sh
```

## Retry one job

```bash
python3 /Users/hassan/repos/game_agent/tmp/game_refactoring_experiments/experiments/four_game_lane_collision/retry_single_job.py job_01
```

## Alternate prompts not used in this scaffold

- `flappy bird`
- `harry  potter vibe with flappy birds gamepelay`

