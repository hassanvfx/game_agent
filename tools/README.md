# Tools Workspace Overview

This directory contains CLI-oriented repositories used in the game pipeline/tooling stack.

## Active CLI Tool Repositories

- `game_deploy`  
  Deploy-packaging CLI used by `game_publish_pipeline` to convert refactor outputs into published public remix bundles.

- `game_generator`  
  Orchestration pipeline for generation runs, run-state/event observability, and dashboard serving.

- `game_matcher_v2`  
  Deterministic matcher toolchain (artifact build, selected-tag scoring, prompt matching).

- `game_obfuscator`  
  Deterministic obfuscation/minification CLI with sync `start` contract.

- `game_publish_pipeline`  
  Higher-order publish orchestration (deploy + obfuscation + report + optional validation/sync helpers).

- `game_refactoring`  
  Operator-pipeline refactor/transformation CLI surfaces (`start-batch`, `status`, `result`, etc.).

- `giphy_api`  
  Thin wrapper CLI around Giphy (`giphy` command).

- `kie-api`  
  Focused KIE CLI (`kie-cli`) for upload/image/video/llm/suno/job polling workflows.

## Additional Repositories

- `game_uploader_r2`  
  Included as part of artifact/pipeline support. Treated as **WIP** in the broader API abstraction effort.

- `game_actor_mock`  
  Included as artifact support and mock/runtime experimentation. Also treated as **WIP** for API abstraction.

## Deprecated Repositories

Legacy tools moved under:

- `deprecated/game_matcher`
- `deprecated/game_remix_editor`
- `deprecated/gamezone_crawler`
