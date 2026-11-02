# kie-api

## Overview and pipeline position

This optional media utility provides CLI access to KIE image, video, language,
and audio workflows. It constructs requests, stores job information, and supports
status checks and polling for asynchronous work.

```text
prompt / media / upload
          |
       kie-cli -> payload + client -> KIE backend
          ^                               |
          |                            job / result
          +------ status / wait ----------+
                         |
                   JSON / media output
```

This is a separately invoked integration; the generator does not require it as a
fixed pipeline stage. Install this Python package and configure its service
credentials before using the installed `kie-cli` command.

See the [workspace overview](../../README.md) and [tool inventory](../README.md).

Focused Python CLI for KIE API workflows.

## Installed CLI command

From `pyproject.toml`:

- `kie-cli = kie_cli.cli:main`

## Command surface

From `src/kie_cli/cli.py`:

- `kie-cli upload`
- `kie-cli image <model>` (`nano-banana-pro` | `gpt-image-2`)
- `kie-cli video <model>` (`grok` | `veo3`)
- `kie-cli llm <model>` (`gpt-5-2`)
- `kie-cli gemini <model>` (`gemini-3-pro`)
- `kie-cli suno music`
- `kie-cli suno lyrics`
- `kie-cli suno sounds`
- `kie-cli job-status`
- `kie-cli wait`

Most commands support `--json` for machine-readable output.

## Prompt/media argument pattern

Prompted commands use exactly one of:

- `--prompt`
- `--prompt-file`

Image-capable commands accept repeatable:

- `--image`

## Examples

```bash
kie-cli image gpt-image-2 --prompt "A cinematic night city poster" --json
kie-cli video grok --prompt "A neon corridor dolly shot" --json
kie-cli llm gpt-5-2 --prompt "Describe this image" --image ./image.png --json
kie-cli suno music --prompt "A dreamy synth-pop song" --json
kie-cli wait --job-file outputs/jobs/sample.json --poll-interval 5 --timeout 900 --json
```

## Architecture boundary

`kie-api` provides a CLI orchestration layer over internal modules (`client`, `payloads`, `status`, `polling`, `jobs`, `media`). It owns command contracts, payload wiring, and output normalization; backend execution is delegated to KIE endpoints.
