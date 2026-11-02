# Tools Workspace Overview

This directory contains CLI-oriented repositories used in the game pipeline/tooling stack.

## Pipeline map

```text
game_generator coordinates the main chain:

prompt -> game_matcher_v2 -> game_refactoring -> game_publish_pipeline
                                   ^                    |
                                   |              game_deploy
                             game_editorial             |
                                                  game_obfuscator
                                                        |
                                             artifacts / reports / GCS

Separate supporting paths:
URL manifest -> game_downloader -> local mirrors for source preparation
Local files  -> game_uploader_r2 -> Cloudflare R2
API / CLI    -> game_actor_mock -> Redis / Celery -> simulated results
Media work   -> giphy_api / kie-api / library
```

The generator matches and refactors by default. Publishing is enabled with
`--publish`; GCS upload after publishing is enabled with `--upload`. Editorial
batches provide an alternative input to refactoring. Downloader ingestion and R2
uploads are invoked separately.

Each linked README explains its inputs, outputs, position in the chain, and command
working directory. Start with the [repository overview](../README.md) for setup and
the API/worker architecture.

## Active CLI Tool Repositories

- [game_deploy](game_deploy/README.md):
  Deploy-packaging CLI used by `game_publish_pipeline` to convert refactor outputs into published public remix bundles.

- [game_generator](game_generator/README.md):
  Orchestration pipeline for generation runs, run-state/event observability, and dashboard serving.

- [game_matcher_v2](game_matcher_v2/README.md):
  Deterministic matcher toolchain (artifact build, selected-tag scoring, prompt matching).

- [game_obfuscator](game_obfuscator/README.md):
  Deterministic obfuscation/minification CLI with sync `start` contract.

- [game_publish_pipeline](game_publish_pipeline/README.md):
  Higher-order publish orchestration (deploy + obfuscation + report + optional validation/sync helpers).

- [game_refactoring](game_refactoring/README.md):
  Operator-pipeline refactor/transformation CLI surfaces (`start-batch`, `status`, `result`, etc.).

- [game_editorial](game_editorial/README.md):
  Deterministic themed prompt assignment, remix manifest expansion, and raw-corpus batch planning.

- [game_downloader](game_downloader/README.md):
  Manifest-driven game mirroring with queue execution, local replay packages, and offline-readiness QA.

- [giphy_api](giphy_api/README.md):
  Thin wrapper CLI around Giphy (`giphy` command).

- [kie-api](kie-api/README.md):
  Focused KIE CLI (`kie-cli`) for upload/image/video/llm/suno/job polling workflows.

## Additional Repositories

- [game_uploader_r2](game_uploader_r2/README.md):
  Included as part of artifact/pipeline support. Treated as **WIP** in the broader API abstraction effort.

- [game_actor_mock](game_actor_mock/README.md):
  Included as artifact support and mock/runtime experimentation. Also treated as **WIP** for API abstraction.

## Deprecated Repositories

Legacy tools moved under:

- `deprecated/game_matcher`
- `deprecated/game_remix_editor`
- `deprecated/gamezone_crawler`
