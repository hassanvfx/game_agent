# KIE CLI Comprehensive Guide

**Production-facing documentation for image, video, LLM, and Suno workflows**

## Executive overview

`kie-cli` is a focused Python command-line interface for working with a curated set of KIE-backed creative and language services from a single local workflow.

It exists to make the KIE service surface usable in three different ways at once:

- as a practical engineering tool for immediate task submission and polling
- as a product surface map that shows what the platform can vend today
- as a durable operations contract for asynchronous automation

In its current production-facing scope, `kie-cli` supports:

- **file upload** to KIE temporary storage
- **image generation and editing**
  - `nano-banana-pro`
  - `gpt-image-2` with automatic mode switching
- **video generation**
  - `grok`
  - `veo3` with explicit Veo model variants
- **OpenAI-compatible multimodal LLM inference**
  - `gpt-5-2`
- **Suno audio workflows**
  - music generation
  - lyrics generation
  - sounds generation
- **durable async job tracking**
  - one-shot status checks
  - wait-until-terminal polling
  - saved job records for later automation and resumption

The CLI intentionally exposes a **small, sellable, high-confidence surface** instead of trying to mirror every KIE endpoint at once.

### Production-ready scope

This guide covers the currently strong and presentable command families:

- `kie-cli upload`
- `kie-cli image nano-banana-pro`
- `kie-cli image gpt-image-2`
- `kie-cli video grok`
- `kie-cli video veo3`
- `kie-cli llm gpt-5-2`
- `kie-cli suno music`
- `kie-cli suno lyrics`
- `kie-cli suno sounds`
- `kie-cli job-status`
- `kie-cli wait`

### Explicit exclusion: Gemini

Gemini support exists in the codebase experimentally, but it is **currently provider-blocked / unreliable in live validation** and is **excluded from this production-facing documentation**.

For positioning purposes, do not present the Gemini family as part of the supported production-ready CLI surface.

---

## Supported capabilities matrix

| Command family | User-facing command / alias | Underlying model or route | Prompt input | Image input | Sync vs async | `--save-job` | Live-tested status | Notable caveats |
|---|---|---|---|---|---|---|---|---|
| Upload | `kie-cli upload` | KIE temp upload API | N/A | local file path | Sync | No | Covered by implementation path; used in live multimodal/generation tests | Returns temporary `downloadUrl` for later submission |
| Image | `kie-cli image nano-banana-pro` | `nano-banana-pro` | Yes | Yes | Async | Yes | Yes | Market async route |
| Image | `kie-cli image gpt-image-2` | `gpt-image-2-text-to-image` or `gpt-image-2-image-to-image` | Yes | Optional | Async | Yes | Yes | Mode switches automatically based on presence of `--image` |
| Video | `kie-cli video grok` | `grok-imagine/text-to-video` or `grok-imagine/image-to-video` | Yes | Optional | Async | Yes | Yes | Duration type changes between text-only and image mode |
| Video | `kie-cli video veo3` | `veo3`, `veo3_fast`, or `veo3_lite` | Yes | Optional | Async | Yes | Core async contract covered; route and payload logic implemented | Generation type must match workflow intent |
| LLM | `kie-cli llm gpt-5-2` | `/gpt-5-2/v1/chat/completions` | Yes | Optional, repeated | Sync | No | Yes, including multimodal live test | Uses OpenAI-compatible request/response shape |
| Suno | `kie-cli suno music` | `/api/v1/generate` | Yes | No | Async | Yes | Yes | Live provider required explicit provider `--model` |
| Suno | `kie-cli suno lyrics` | `/api/v1/lyrics` | Yes | No | Async | No | Yes | Live provider required `--callback-url` |
| Suno | `kie-cli suno sounds` | `/api/v1/generate/sounds` | Yes | No | Async | Yes | Yes | Polled through Suno music status endpoint |
| Async lifecycle | `kie-cli job-status` | model-routed status check | N/A | N/A | Sync status read | N/A | Covered | Prefer `--model`; `--kind` is legacy |
| Async lifecycle | `kie-cli wait` | model-routed polling | N/A | N/A | Async wait loop | Reads saved job files | Covered and live-used | Returns `timeout` result if terminal state is not reached |

### What “live-tested” means here

“Live-tested” means the CLI behavior has been exercised against real KIE-backed network calls through the gated integration suite under `tests/integration/test_live_kie.py`, not only unit tests.

Confirmed live-pass areas include:

- GPT Image 2 prompt-only generation
- GPT Image 2 image+prompt generation
- Grok prompt-only video generation
- Grok image+prompt video generation
- GPT-5.2 text completion
- GPT-5.2 multimodal image input
- Suno music generation
- Suno lyrics generation
- Suno sounds generation

---

## Installation and setup

## Requirements

- Python 3.10+ recommended
- KIE API credentials
- a virtual environment for isolated local execution

## Virtualenv setup

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -e ".[dev]"
```

## Environment configuration

Create a local `.env` file:

```bash
cp .env.example .env
```

Populate it with at least:

```env
KIE_API_KEY=your_kie_api_key
KIE_BASE_URL=https://api.kie.ai
KIE_UPLOAD_BASE_URL=https://kieai.redpandaai.co
```

### Required environment variables

- `KIE_API_KEY`
  - required for any real network request
  - used for upload, generation, status polling, and LLM calls

### Optional environment variables

- `KIE_BASE_URL`
  - defaults to `https://api.kie.ai`
  - override only if your deployment targets a different KIE API base
- `KIE_UPLOAD_BASE_URL`
  - defaults to `https://kieai.redpandaai.co`
  - used for temporary file upload resolution

### Live-test / callback-related variables

These are mainly relevant when validating the CLI against real services:

- `RUN_KIE_LIVE_TESTS=1`
  - enables gated integration tests
- `KIE_LIVE_SCOPE=llm|gemini|image|video|suno|generation|all`
  - scopes live test execution
- `KIE_LIVE_POLL_INTERVAL`
  - polling interval used by integration tests
- `KIE_LIVE_TIMEOUT`
  - timeout used by integration tests
- `KIE_SUNO_CALLBACK_URL`
  - required in practice for live Suno validation flows
  - especially important for lyrics, which failed live without `callBackUrl`

### How config is loaded

`kie-cli` loads configuration by:

1. attempting `python-dotenv` if installed
2. falling back to a minimal local `.env` parser if needed
3. reading:
   - `KIE_API_KEY`
   - `KIE_BASE_URL`
   - `KIE_UPLOAD_BASE_URL`

That means dry-run usage remains practical even before the full dependency stack is installed.

---

## CLI mental model

Understanding `kie-cli` is easiest if you separate it into five concepts:

1. **submission commands**
2. **upload-first media resolution**
3. **synchronous vs asynchronous behavior**
4. **normalized CLI outputs**
5. **durable job persistence**

## 1. Submission commands

Submission commands are the top-level task initiators:

- `upload`
- `image`
- `video`
- `llm`
- `suno`

Some return a final answer immediately. Others return a queued job.

## 2. Upload-first media handling

Any command that accepts `--image` follows the same media resolution model:

- if the value starts with `http://` or `https://`, it is passed through directly
- if the value is a local path, the CLI uploads it first to KIE temporary storage
- the returned `downloadUrl` becomes the URL included in the generation or chat payload

This behavior is reused across:

- image generation
- video generation
- GPT-5.2 multimodal LLM calls

## 3. Synchronous vs asynchronous commands

### Synchronous command families

These return final content directly:

- `kie-cli upload`
- `kie-cli llm gpt-5-2`

### Asynchronous command families

These submit a task and return a `jobId`:

- all `image` commands
- all `video` commands
- `suno music`
- `suno lyrics`
- `suno sounds`

Those async commands are designed to be followed by either:

- `kie-cli job-status`
- `kie-cli wait`

## 4. Alias model vs provider model

The CLI uses a mix of:

- **user-facing aliases**
- **underlying routed model names**

Examples:

- `kie-cli image gpt-image-2`
  - becomes:
    - `gpt-image-2-text-to-image` when no image is supplied
    - `gpt-image-2-image-to-image` when one or more images are supplied
- `kie-cli video grok`
  - becomes:
    - `grok-imagine/text-to-video`
    - `grok-imagine/image-to-video`
- `kie-cli video veo3 --veo-model veo3_fast`
  - uses `veo3_fast` as the actual async model contract
- `kie-cli suno music`
  - persists as synthetic async routing model `suno-music`
- `kie-cli suno sounds`
  - persists as synthetic async routing model `suno-sounds`
- `kie-cli suno lyrics`
  - persists as synthetic async routing model `suno-lyrics`

This matters because **saved job files and polling are model-routed**.

## 5. Dry-run behavior

Commands that support `--dry-run` emit the exact payload and resolved media contract without making a network request.

Dry-run is especially useful for:

- checking upload-first resolution
- confirming mode selection
- validating payload shape before spending credits
- showing payload contracts in documentation or demos

Dry-run output always uses:

- `status: "dry_run"`
- `payload`
- `resolvedMedia`
- a route descriptor

## JSON output conventions

With `--json`, the CLI emits structured JSON suitable for automation.

Common top-level fields include:

- `ok`
- `status`
- `model`
- `jobId`
- `outputUrl`
- `outputUrls`
- `payload`
- `resolvedMedia`
- `error`
- `raw`
- `usage`
- `response`
- `polls`
- `elapsedSeconds`

## Human output conventions

Without `--json`, the CLI chooses the shortest useful text form:

- chat completion text is printed directly
- async submissions print `status: JOB_ID`
- upload prints the `downloadUrl`
- dry-run falls back to full JSON

That makes the tool usable in both shell pipelines and human-first terminal sessions.

---

## Upload command

## Purpose

`kie-cli upload` uploads a local file to KIE temporary storage and returns a temporary downloadable URL that can be fed into other workflows.

## Syntax

```bash
kie-cli upload FILE [--upload-path PATH] [--dry-run] [--json]
```

## Arguments and options

- `FILE`
  - required local file path
- `--upload-path`
  - logical destination path inside temporary storage
  - default: `kie-cli/uploads`
- `--dry-run`
  - do not upload; show what would happen
- `--json`
  - emit structured JSON

## Example

```bash
.venv/bin/kie-cli upload ./reference.png \
  --upload-path kie-cli/uploads/demo \
  --json
```

## Sample request contract

The upload endpoint is multipart rather than JSON.

Logical contract:

```json
{
  "endpoint": "/api/file-stream-upload",
  "method": "POST",
  "headers": {
    "Authorization": "Bearer <KIE_API_KEY>"
  },
  "form": {
    "uploadPath": "kie-cli/uploads/demo",
    "file": "<binary stream>"
  }
}
```

## Sample success JSON

```json
{
  "ok": true,
  "downloadUrl": "https://example.com/temp/reference.png",
  "fileName": "reference.png",
  "filePath": "kie-cli/uploads/demo/reference.png",
  "mimeType": "image/png",
  "fileSize": 12345,
  "expiresInDays": 3
}
```

## Dry-run JSON

```json
{
  "ok": true,
  "status": "dry_run",
  "file": "./reference.png",
  "uploadPath": "kie-cli/uploads/demo",
  "uploaded": false
}
```

## Notes

- upload is the primitive that enables local-image workflows elsewhere in the CLI
- upload failures are surfaced as API/config/file errors
- the returned URL is intended as temporary KIE-hosted media, not long-term asset storage

---

## Image commands

## Command family overview

Image workflows are submitted through:

- `kie-cli image nano-banana-pro`
- `kie-cli image gpt-image-2`

Both are asynchronous.

### Shared syntax

```bash
kie-cli image MODEL \
  (--prompt TEXT | --prompt-file FILE) \
  [--image URL_OR_PATH ...] \
  [--aspect-ratio VALUE] \
  [--resolution VALUE] \
  [--callback-url URL] \
  [--upload-path PATH] \
  [--save-job FILE] \
  [--dry-run] \
  [--json]
```

### Shared options

- `--prompt` or `--prompt-file`
  - exactly one is required
- `--image`
  - may be repeated
  - local paths upload first
  - remote URLs pass through
- `--aspect-ratio`
- `--resolution`
- `--callback-url`
  - sent as `callBackUrl` when provided
- `--upload-path`
  - defaults to `kie-cli/images`
- `--save-job`
  - write durable job record for async polling
- `--dry-run`
- `--json`

---

## `kie-cli image nano-banana-pro`

## Purpose

Submits an async `nano-banana-pro` image generation or image-referenced editing task.

## Example: prompt-only

```bash
.venv/bin/kie-cli image nano-banana-pro \
  --prompt "Create a cinematic perfume product poster with glossy reflections" \
  --aspect-ratio 1:1 \
  --resolution 1K \
  --output-format png \
  --save-job outputs/jobs/nano-banana.json \
  --json
```

## Example: image + prompt

```bash
.venv/bin/kie-cli image nano-banana-pro \
  --prompt "Turn this source into a premium advertising visual with dramatic lighting" \
  --image ./reference.png \
  --aspect-ratio 1:1 \
  --resolution 1K \
  --output-format png \
  --json
```

## Request payload shape

```json
{
  "model": "nano-banana-pro",
  "input": {
    "prompt": "Turn this source into a premium advertising visual with dramatic lighting",
    "image_input": [
      "https://example.com/temp/reference.png"
    ],
    "aspect_ratio": "1:1",
    "resolution": "1K",
    "output_format": "png"
  },
  "callBackUrl": "https://example.com/callback"
}
```

`callBackUrl` is omitted when not provided.

## Submit success JSON

```json
{
  "ok": true,
  "jobId": "task_123",
  "status": "queued",
  "model": "nano-banana-pro",
  "resolvedMedia": [
    {
      "source": "./reference.png",
      "kind": "image",
      "uploaded": true,
      "resolved_url": "https://example.com/temp/reference.png"
    }
  ],
  "jobFile": "outputs/jobs/nano-banana.json"
}
```

## Notes

- this command always persists the async model as `nano-banana-pro`
- local image references are converted into uploaded URLs before submission
- default aspect ratio for this command is `1:1`
- default resolution is `1K`
- default output format is `png`

---

## `kie-cli image gpt-image-2`

## Purpose

Submits GPT Image 2 in one of two routed modes:

- **text-to-image** when no `--image` is supplied
- **image-to-image** when one or more `--image` values are supplied

This mode switch is automatic.

## Example: prompt-only

```bash
.venv/bin/kie-cli image gpt-image-2 \
  --prompt "A cinematic night city poster in glossy sci-fi style" \
  --aspect-ratio 16:9 \
  --resolution 1K \
  --save-job outputs/jobs/gpt-image2-text.json \
  --json
```

## Example: image + prompt

```bash
.venv/bin/kie-cli image gpt-image-2 \
  --prompt "Transform this product shot into a premium launch campaign image" \
  --image ./reference.png \
  --aspect-ratio auto \
  --resolution 1K \
  --json
```

## Request payload shape: prompt-only

```json
{
  "model": "gpt-image-2-text-to-image",
  "input": {
    "prompt": "A cinematic night city poster in glossy sci-fi style",
    "aspect_ratio": "16:9",
    "resolution": "1K"
  }
}
```

## Request payload shape: image+prompt

```json
{
  "model": "gpt-image-2-image-to-image",
  "input": {
    "prompt": "Transform this product shot into a premium launch campaign image",
    "aspect_ratio": "auto",
    "resolution": "1K",
    "input_urls": [
      "https://example.com/temp/reference.png"
    ]
  }
}
```

## Submit success JSON

```json
{
  "ok": true,
  "jobId": "task_456",
  "status": "queued",
  "model": "gpt-image-2-image-to-image"
}
```

## GPT Image 2 deep dive: mode switching

`gpt-image-2` is a user-friendly alias, not the final provider model string.

Routing logic is:

- no images:
  - `gpt-image-2-text-to-image`
- at least one image:
  - `gpt-image-2-image-to-image`

This affects:

- the actual submission payload
- the model stored in any job file
- the model that should be reused for later `job-status` or `wait` calls if not using a job file

That means the safest async workflow is:

1. submit with `--save-job`
2. reuse the saved job file
3. avoid guessing which concrete model was chosen later

---

## Video commands

## Command family overview

Video workflows are submitted through:

- `kie-cli video grok`
- `kie-cli video veo3`

Both are asynchronous.

### Shared syntax

```bash
kie-cli video MODEL \
  (--prompt TEXT | --prompt-file FILE) \
  [--image URL_OR_PATH ...] \
  [--aspect-ratio VALUE] \
  [--callback-url URL] \
  [--upload-path PATH] \
  [--save-job FILE] \
  [--dry-run] \
  [--json]
```

---

## `kie-cli video grok`

## Purpose

Submits a Grok Imagine video generation task.

Like GPT Image 2, Grok uses automatic mode switching:

- `grok-imagine/text-to-video` with prompt only
- `grok-imagine/image-to-video` with one or more reference images

## Example: prompt-only

```bash
.venv/bin/kie-cli video grok \
  --prompt "A camera slowly dollies through a neon-lit corridor with drifting fog" \
  --aspect-ratio 16:9 \
  --mode normal \
  --duration 6 \
  --resolution 480p \
  --save-job outputs/jobs/grok-text-video.json \
  --json
```

## Example: image + prompt

```bash
.venv/bin/kie-cli video grok \
  --prompt "@image1 animate the subject with subtle camera motion and soft atmosphere" \
  --image ./reference.png \
  --mode normal \
  --duration 6 \
  --resolution 720p \
  --json
```

## Options

Additional Grok-specific flags:

- `--mode fun|normal|spicy`
- `--duration INT`
- `--resolution VALUE`
- `--nsfw-checker`

## Request payload shape: text-to-video

```json
{
  "model": "grok-imagine/text-to-video",
  "input": {
    "prompt": "A camera slowly dollies through a neon-lit corridor with drifting fog",
    "aspect_ratio": "16:9",
    "mode": "normal",
    "duration": 6,
    "resolution": "480p",
    "nsfw_checker": false
  }
}
```

## Request payload shape: image-to-video

```json
{
  "model": "grok-imagine/image-to-video",
  "input": {
    "prompt": "@image1 animate the subject with subtle camera motion and soft atmosphere",
    "aspect_ratio": "16:9",
    "mode": "normal",
    "duration": "6",
    "resolution": "720p",
    "nsfw_checker": false,
    "image_urls": [
      "https://example.com/temp/reference.png"
    ]
  }
}
```

## Important Grok nuance

The payload builder intentionally changes the `duration` type:

- **text-to-video**: integer
- **image-to-video**: string

That is not a documentation typo; it mirrors the currently encoded CLI contract and should be preserved in examples and expectations.

## Submit success JSON

```json
{
  "ok": true,
  "jobId": "task_789",
  "status": "queued",
  "model": "grok-imagine/image-to-video"
}
```

## Grok deep dive: text-to-video vs image-to-video

The Grok branch behaves similarly to GPT Image 2:

- if no images are resolved, the command submits a pure text-to-video task
- if one or more images are resolved, the command submits image-to-video and includes `image_urls`

This means the same public command can support:

- simple motion concept generation
- reference-driven animation from a still image

That makes Grok a strong “single entrypoint” product surface for both ideation and image-grounded video generation.

---

## `kie-cli video veo3`

## Purpose

Submits a Veo generation task through the dedicated Veo API route.

The user-facing command is `video veo3`, but the actual routed async model is chosen with `--veo-model`.

## Veo-specific options

- `--veo-model veo3|veo3_fast|veo3_lite`
  - default: `veo3_fast`
- `--generation-type TEXT_2_VIDEO|FIRST_AND_LAST_FRAMES_2_VIDEO|REFERENCE_2_VIDEO`
- `--disable-translation`
- `--watermark`
- `--resolution`
  - default: `720p`
- `--aspect-ratio`
  - default: `16:9`

## Example: prompt-only text-to-video

```bash
.venv/bin/kie-cli video veo3 \
  --prompt "A serene aerial shot above a futuristic coastal city at sunrise" \
  --veo-model veo3_fast \
  --generation-type TEXT_2_VIDEO \
  --aspect-ratio 16:9 \
  --resolution 720p \
  --save-job outputs/jobs/veo3-fast.json \
  --json
```

## Example: first-and-last-frame workflow

```bash
.venv/bin/kie-cli video veo3 \
  --prompt "Create a smooth cinematic transition between the two supplied frames" \
  --image ./first.png \
  --image ./last.png \
  --veo-model veo3_fast \
  --generation-type FIRST_AND_LAST_FRAMES_2_VIDEO \
  --aspect-ratio 16:9 \
  --resolution 720p \
  --json
```

## Request payload shape

```json
{
  "prompt": "Create a smooth cinematic transition between the two supplied frames",
  "model": "veo3_fast",
  "aspect_ratio": "16:9",
  "enableTranslation": true,
  "resolution": "720p",
  "imageUrls": [
    "https://example.com/temp/first.png",
    "https://example.com/temp/last.png"
  ],
  "generationType": "FIRST_AND_LAST_FRAMES_2_VIDEO",
  "watermark": "KIE"
}
```

## Submit success JSON

```json
{
  "ok": true,
  "jobId": "veo_task_123",
  "status": "queued",
  "model": "veo3_fast"
}
```

## Veo deep dive: generation type behavior

Veo has an important inferred-default rule:

- if `--generation-type` is provided, the CLI uses it directly
- else if one or more images are present, it defaults to `FIRST_AND_LAST_FRAMES_2_VIDEO`
- else it defaults to `TEXT_2_VIDEO`

This means the CLI is optimized for the most common two modes:

- prompt-only generation
- frame-conditioned interpolation / transition generation

If you need a different provider behavior, set `--generation-type` explicitly.

---

## OpenAI-compatible LLM command

## `kie-cli llm gpt-5-2`

## Purpose

Runs a synchronous OpenAI-compatible chat completion against KIE GPT-5.2.

This command supports:

- text-only chat completion
- multimodal text + image input
- reasoning effort
- KIE/OpenAI-style web search tool injection

## Syntax

```bash
kie-cli llm gpt-5-2 \
  (--prompt TEXT | --prompt-file FILE) \
  [--image URL_OR_PATH ...] \
  [--reasoning-effort low|high] \
  [--web-search] \
  [--upload-path PATH] \
  [--dry-run] \
  [--json]
```

## Example: text-only

```bash
.venv/bin/kie-cli llm gpt-5-2 \
  --prompt "Write a concise launch description for a premium smartwatch." \
  --reasoning-effort high \
  --json
```

## Example: prompt file

```bash
.venv/bin/kie-cli llm gpt-5-2 \
  --prompt-file ./prompt.txt \
  --reasoning-effort low \
  --json
```

## Example: multimodal image input

```bash
.venv/bin/kie-cli llm gpt-5-2 \
  --prompt "What do you see in this image?" \
  --image ./image.png \
  --reasoning-effort low \
  --json
```

## Example: web search grounding

```bash
.venv/bin/kie-cli llm gpt-5-2 \
  --prompt "Summarize today's AI news in five bullets." \
  --web-search \
  --json
```

## Request payload shape: text-only

```json
{
  "messages": [
    {
      "role": "user",
      "content": [
        {
          "type": "text",
          "text": "Write a concise launch description for a premium smartwatch."
        }
      ]
    }
  ],
  "reasoning_effort": "high"
}
```

## Request payload shape: multimodal with image

```json
{
  "messages": [
    {
      "role": "user",
      "content": [
        {
          "type": "text",
          "text": "What do you see in this image?"
        },
        {
          "type": "image_url",
          "image_url": {
            "url": "https://example.com/temp/image.png"
          }
        }
      ]
    }
  ],
  "reasoning_effort": "low"
}
```

## Request payload shape: with web search

```json
{
  "messages": [
    {
      "role": "user",
      "content": [
        {
          "type": "text",
          "text": "Summarize today's AI news in five bullets."
        }
      ]
    }
  ],
  "reasoning_effort": "high",
  "tools": [
    {
      "type": "function",
      "function": {
        "name": "web_search"
      }
    }
  ]
}
```

## Success JSON

```json
{
  "ok": true,
  "model": "gpt-5-2",
  "status": "succeeded",
  "text": "A premium smartwatch built for people who want luxury design and modern intelligence in one device.",
  "finishReason": "stop",
  "usage": {
    "prompt_tokens": 42,
    "completion_tokens": 27,
    "total_tokens": 69
  },
  "raw": {
    "id": "chatcmpl_123",
    "choices": [
      {
        "message": {
          "role": "assistant",
          "content": "..."
        },
        "finish_reason": "stop"
      }
    ]
  }
}
```

## Human-mode behavior

Without `--json`, this command prints only the returned text.

That makes it suitable for shell composition like:

```bash
summary=$(.venv/bin/kie-cli llm gpt-5-2 --prompt "Summarize..." )
```

## Notes

- local image paths are uploaded first and inserted as `image_url`
- provider model names may sometimes come back as `gpt-5.2` instead of `gpt-5-2`
- response normalization extracts text from either:
  - `choices[0].message.content` string
  - list-based content parts

---

## Suno command family

## Overview

The CLI currently exposes three focused Suno surfaces:

- `kie-cli suno music`
- `kie-cli suno lyrics`
- `kie-cli suno sounds`

All three are asynchronous, but they do not behave identically.

### High-level differences

| Suno command | Submit endpoint | Poll endpoint | Save-job supported | Final content type |
|---|---|---|---|---|
| `suno music` | `/api/v1/generate` | `/api/v1/generate/record-info` | Yes | audio/media URLs |
| `suno lyrics` | `/api/v1/lyrics` | `/api/v1/lyrics/record-info` | No | lyrics objects |
| `suno sounds` | `/api/v1/generate/sounds` | `/api/v1/generate/record-info` | Yes | audio/media URLs |

### Critical live findings

The Suno family has the most important provider-side caveats in the current CLI:

- **music** required an explicit provider model during live validation
- **lyrics** required `callBackUrl` during live validation
- **sounds** follows the music polling route, not a separate sounds status route

These findings are operationally important and should be treated as part of the product contract.

---

## `kie-cli suno music`

## Purpose

Submits a Suno music generation task.

## Syntax

```bash
kie-cli suno music \
  (--prompt TEXT | --prompt-file FILE) \
  [--custom-mode] \
  [--instrumental] \
  [--model MODEL] \
  [--style TEXT] \
  [--title TEXT] \
  [--negative-tags TEXT] \
  [--callback-url URL] \
  [--save-job FILE] \
  [--dry-run] \
  [--json]
```

## Example: basic

```bash
.venv/bin/kie-cli suno music \
  --prompt "A dreamy synth-pop song about neon rain" \
  --model V5_5 \
  --save-job outputs/jobs/suno-music.json \
  --json
```

## Example: custom options

```bash
.venv/bin/kie-cli suno music \
  --prompt "A dreamy synth-pop song about neon rain" \
  --custom-mode \
  --instrumental \
  --model V5_5 \
  --style "synth-pop" \
  --title "Neon Rain" \
  --negative-tags "harsh, noisy" \
  --callback-url https://example.com/kie-callback \
  --json
```

## Request payload shape

```json
{
  "prompt": "A dreamy synth-pop song about neon rain",
  "customMode": true,
  "instrumental": true,
  "model": "V5_5",
  "style": "synth-pop",
  "title": "Neon Rain",
  "negativeTags": "harsh, noisy",
  "callBackUrl": "https://example.com/kie-callback"
}
```

## Submit success JSON

```json
{
  "ok": true,
  "jobId": "suno_music_123",
  "status": "queued",
  "model": "suno-music",
  "jobFile": "outputs/jobs/suno-music.json"
}
```

## Poll success JSON

```json
{
  "ok": true,
  "jobId": "suno_music_123",
  "status": "succeeded",
  "model": "suno-music",
  "outputUrls": [
    "https://example.com/song.mp3"
  ],
  "outputUrl": "https://example.com/song.mp3",
  "response": {
    "sunoData": [
      {
        "audioUrl": "https://example.com/song.mp3"
      }
    ]
  },
  "polls": 6,
  "elapsedSeconds": 50.0
}
```

## Live caveat

In live validation, music generation failed when no provider `model` was specified. The provider returned a validation-style message indicating that `model` cannot be null and must be one of the accepted Suno variants.

**Operational recommendation:** always pass `--model` for production Suno music usage.

---

## `kie-cli suno lyrics`

## Purpose

Submits a lyrics-generation task and later polls for a final structured lyrics response.

## Syntax

```bash
kie-cli suno lyrics \
  (--prompt TEXT | --prompt-file FILE) \
  [--callback-url URL] \
  [--dry-run] \
  [--json]
```

## Example

```bash
.venv/bin/kie-cli suno lyrics \
  --prompt "A nostalgic song about childhood memories in a small town" \
  --callback-url https://example.com/kie-callback \
  --json
```

## Request payload shape

```json
{
  "prompt": "A nostalgic song about childhood memories in a small town",
  "callBackUrl": "https://example.com/kie-callback"
}
```

## Submit success JSON

```json
{
  "ok": true,
  "jobId": "suno_lyrics_123",
  "status": "queued",
  "model": "suno-lyrics"
}
```

## Wait success JSON

```json
{
  "ok": true,
  "jobId": "suno_lyrics_123",
  "status": "succeeded",
  "model": "suno-lyrics",
  "lyrics": [
    {
      "text": "Verse 1...",
      "title": "Small Town Memories",
      "status": "complete"
    }
  ],
  "response": {
    "data": [
      {
        "text": "Verse 1...",
        "title": "Small Town Memories",
        "status": "complete"
      }
    ]
  },
  "polls": 4,
  "elapsedSeconds": 31.2
}
```

## Important behavior difference

Unlike music and sounds:

- lyrics does **not** currently support `--save-job`
- live polling is performed by task ID plus explicit model:
  - `kie-cli wait TASK_ID --model suno-lyrics`

## Live caveat

Live provider validation showed that lyrics generation required `callBackUrl`. Without it, the provider returned an error equivalent to:

- `Please enter callBackUrl.`

**Operational recommendation:** always pass `--callback-url` for production Suno lyrics usage.

---

## `kie-cli suno sounds`

## Purpose

Submits a Suno sounds-generation task for effects, ambience, or non-song audio generation.

## Syntax

```bash
kie-cli suno sounds \
  (--prompt TEXT | --prompt-file FILE) \
  [--model V5|V5_5] \
  [--sound-loop] \
  [--sound-tempo INT] \
  [--sound-key TEXT] \
  [--grab-lyrics] \
  [--callback-url URL] \
  [--save-job FILE] \
  [--dry-run] \
  [--json]
```

## Example

```bash
.venv/bin/kie-cli suno sounds \
  --prompt "A looping cyberpunk city ambience with distant sirens" \
  --model V5_5 \
  --sound-loop \
  --sound-tempo 110 \
  --sound-key Am \
  --grab-lyrics \
  --save-job outputs/jobs/suno-sounds.json \
  --json
```

## Request payload shape

```json
{
  "prompt": "A looping cyberpunk city ambience with distant sirens",
  "soundLoop": true,
  "grabLyrics": true,
  "model": "V5_5",
  "soundTempo": 110,
  "soundKey": "Am"
}
```

## Submit success JSON

```json
{
  "ok": true,
  "jobId": "suno_sounds_123",
  "status": "queued",
  "model": "suno-sounds",
  "jobFile": "outputs/jobs/suno-sounds.json"
}
```

## Poll success JSON

```json
{
  "ok": true,
  "jobId": "suno_sounds_123",
  "status": "succeeded",
  "model": "suno-sounds",
  "outputUrls": [
    "https://example.com/ambience.mp3"
  ],
  "outputUrl": "https://example.com/ambience.mp3",
  "response": {
    "sunoData": [
      {
        "audioUrl": "https://example.com/ambience.mp3"
      }
    ]
  }
}
```

## Important behavior difference

Even though sounds submits to `/api/v1/generate/sounds`, it is polled through the **same status endpoint as music**:

- `/api/v1/generate/record-info`

This is encoded into the route model and saved job contract.

---

## Async lifecycle documentation

The async lifecycle is one of the most important parts of `kie-cli`.

## Standard lifecycle

### 1. Submit a task

Use an async command:

- `image ...`
- `video ...`
- `suno music ...`
- `suno lyrics ...`
- `suno sounds ...`

Example:

```bash
.venv/bin/kie-cli image gpt-image-2 \
  --prompt "A cinematic night city poster" \
  --save-job outputs/jobs/gpt-image2.json \
  --json
```

Typical result:

```json
{
  "ok": true,
  "jobId": "task_123",
  "status": "queued",
  "model": "gpt-image-2-text-to-image",
  "jobFile": "outputs/jobs/gpt-image2.json"
}
```

### 2. Persist the job contract if supported

For supported async commands, `--save-job` writes a durable record that captures:

- job ID
- routed model
- submit endpoint
- status endpoint
- submitted payload
- resolved uploaded media
- raw submit response

This is the safest way to resume polling later without reconstructing model details manually.

### 3. Poll once with `job-status` or block with `wait`

#### One-shot polling

```bash
.venv/bin/kie-cli job-status task_123 \
  --model gpt-image-2-text-to-image \
  --json
```

#### Wait until terminal

```bash
.venv/bin/kie-cli wait \
  --job-file outputs/jobs/gpt-image2.json \
  --poll-interval 5 \
  --timeout 900 \
  --json
```

### 4. Observe terminal states

The CLI treats these as terminal:

- `succeeded`
- `failed`
- `timeout`

### 5. Extract outputs

For image/video/music/sounds tasks, successful results typically expose:

- `outputUrls`
- `outputUrl` as the first item

For lyrics, the final content is exposed as:

- `lyrics`
- mirrored under `response.data`

## Terminal-state semantics

### `queued`

Task exists but has not started meaningful processing.

### `running`

Task is in progress.

### `succeeded`

Task completed successfully and should include final content or output URLs.

### `failed`

Provider reported a terminal failure. The CLI includes an `error` object.

### `timeout`

The CLI polling loop stopped waiting before the provider reached a terminal result.

`timeout` is a **client-side polling result**, not necessarily a provider failure.

---

## Durable job records

## Why job files matter

Async submission and async polling are intentionally decoupled. A saved job record makes the CLI durable across:

- shell sessions
- CI steps
- human handoff
- later re-polling
- automation retries and auditability

## Supported commands for `--save-job`

- `kie-cli image nano-banana-pro`
- `kie-cli image gpt-image-2`
- `kie-cli video grok`
- `kie-cli video veo3`
- `kie-cli suno music`
- `kie-cli suno sounds`

Not currently supported:

- `kie-cli suno lyrics`
- `kie-cli llm gpt-5-2`
- `kie-cli upload`

## Saved job file structure

Representative saved job JSON:

```json
{
  "schemaVersion": 1,
  "jobId": "task_123",
  "model": "gpt-image-2-image-to-image",
  "status": "queued",
  "submittedAt": "2026-04-29T00:00:00Z",
  "submitEndpoint": "/api/v1/jobs/createTask",
  "statusEndpoint": "/api/v1/jobs/recordInfo",
  "submittedPayload": {
    "model": "gpt-image-2-image-to-image",
    "input": {
      "prompt": "Transform this product shot into a premium launch campaign image",
      "aspect_ratio": "auto",
      "resolution": "1K",
      "input_urls": [
        "https://example.com/temp/reference.png"
      ]
    }
  },
  "resolvedMedia": [
    {
      "source": "./reference.png",
      "kind": "image",
      "uploaded": true,
      "resolved_url": "https://example.com/temp/reference.png"
    }
  ],
  "rawSubmitResponse": {
    "code": 200,
    "msg": "success",
    "data": {
      "taskId": "task_123"
    }
  }
}
```

## Model-routed polling contract

Polling does not depend on task ID prefixes alone. Instead, the CLI chooses the correct status route from the saved `model`.

That is why a job file is more reliable than trying to infer routing later.

Route resolution today:

- market route:
  - `nano-banana-pro`
  - `gpt-image-2-text-to-image`
  - `gpt-image-2-image-to-image`
  - `grok-imagine/text-to-video`
  - `grok-imagine/image-to-video`
- veo route:
  - `veo3`
  - `veo3_fast`
  - `veo3_lite`
- suno music route:
  - `suno-music`
  - `suno-sounds`
- suno lyrics route:
  - `suno-lyrics`

---

## `job-status` command

## Purpose

Fetch the current state of an async task exactly once.

## Syntax

```bash
kie-cli job-status JOB_ID [--model MODEL] [--kind auto|market|veo] [--json]
```

## Preferred usage

Always prefer `--model`.

```bash
.venv/bin/kie-cli job-status TASK_ID --model nano-banana-pro --json
.venv/bin/kie-cli job-status TASK_ID --model veo3_fast --json
.venv/bin/kie-cli job-status TASK_ID --model suno-music --json
.venv/bin/kie-cli job-status TASK_ID --model suno-sounds --json
.venv/bin/kie-cli job-status TASK_ID --model suno-lyrics --json
```

## Legacy usage

`--kind` exists only for backward compatibility with market/veo polling heuristics.

```bash
.venv/bin/kie-cli job-status TASK_ID --kind market --json
```

## Sample success JSON: market image

```json
{
  "ok": true,
  "jobId": "task_123",
  "status": "succeeded",
  "model": "nano-banana-pro",
  "outputUrls": [
    "https://example.com/out.png"
  ],
  "outputUrl": "https://example.com/out.png"
}
```

## Sample success JSON: Veo

```json
{
  "ok": true,
  "jobId": "veo_task_123",
  "status": "succeeded",
  "kind": "veo",
  "outputUrls": [
    "https://example.com/out.mp4"
  ],
  "outputUrl": "https://example.com/out.mp4"
}
```

## Sample success JSON: Suno lyrics

```json
{
  "ok": true,
  "jobId": "suno_lyrics_123",
  "status": "succeeded",
  "model": "suno-lyrics",
  "lyrics": [
    {
      "text": "Verse 1...",
      "title": "Example Song",
      "status": "complete"
    }
  ]
}
```

---

## `wait` command

## Purpose

Poll an async task until:

- it succeeds
- it fails
- it times out

## Syntax

### By job file

```bash
kie-cli wait --job-file PATH [--poll-interval SECONDS] [--timeout SECONDS] [--json]
```

### By explicit job ID and model

```bash
kie-cli wait JOB_ID --model MODEL [--poll-interval SECONDS] [--timeout SECONDS] [--json]
```

## Examples

### Wait using a saved job

```bash
.venv/bin/kie-cli wait \
  --job-file outputs/jobs/nano-banana-pro.json \
  --poll-interval 5 \
  --timeout 900 \
  --json
```

### Wait by explicit ID + model

```bash
.venv/bin/kie-cli wait task_123 \
  --model grok-imagine/text-to-video \
  --poll-interval 5 \
  --timeout 900 \
  --json
```

### Wait for Suno lyrics

```bash
.venv/bin/kie-cli wait suno_lyrics_123 \
  --model suno-lyrics \
  --poll-interval 5 \
  --timeout 900 \
  --json
```

## Polling result fields

Successful or terminal wait results may include:

- `ok`
- `jobId`
- `model`
- `status`
- `outputUrls`
- `outputUrl`
- `lyrics`
- `response`
- `polls`
- `elapsedSeconds`
- `error`

---

## Contract and reference section

This section is intended to serve as CLI contract documentation.

## Submit success contract

Representative async submit result:

```json
{
  "ok": true,
  "jobId": "task_123",
  "status": "queued",
  "model": "nano-banana-pro"
}
```

Optional fields:

```json
{
  "resolvedMedia": [],
  "jobFile": "outputs/jobs/example.json"
}
```

## Submit failure contract

When submit normalization fails or an exception is converted to JSON output:

```json
{
  "ok": false,
  "status": "failed",
  "error": {
    "code": "ConfigurationError",
    "message": "KIE_API_KEY is required. Add it to .env or the environment."
  }
}
```

Provider/API failures use the returned provider code/message when available.

## Async wait success contract

Representative media-generation success:

```json
{
  "ok": true,
  "jobId": "task_123",
  "status": "succeeded",
  "model": "grok-imagine/text-to-video",
  "outputUrls": [
    "https://example.com/out.mp4"
  ],
  "outputUrl": "https://example.com/out.mp4",
  "polls": 3,
  "elapsedSeconds": 14.2
}
```

Representative lyrics success:

```json
{
  "ok": true,
  "jobId": "suno_lyrics_123",
  "status": "succeeded",
  "model": "suno-lyrics",
  "lyrics": [
    {
      "text": "Verse 1...",
      "title": "Example Song",
      "status": "complete"
    }
  ],
  "response": {
    "data": [
      {
        "text": "Verse 1...",
        "title": "Example Song",
        "status": "complete"
      }
    ]
  },
  "polls": 4,
  "elapsedSeconds": 31.2
}
```

## Async wait failure contract

Representative failure:

```json
{
  "ok": false,
  "jobId": "veo_task_123",
  "status": "failed",
  "model": "veo3_fast",
  "error": {
    "code": "FAILED",
    "message": "failed for test"
  },
  "polls": 1,
  "elapsedSeconds": 0.0
}
```

## Timeout contract

Representative timeout result:

```json
{
  "ok": false,
  "jobId": "task_123",
  "model": "nano-banana-pro",
  "status": "timeout",
  "polls": 2,
  "elapsedSeconds": 6.0,
  "lastStatus": {
    "ok": true,
    "jobId": "task_123",
    "status": "running",
    "model": "nano-banana-pro"
  },
  "error": {
    "code": "POLL_TIMEOUT",
    "message": "Task did not complete within 5 seconds"
  }
}
```

## Saved job schema contract

```json
{
  "schemaVersion": 1,
  "jobId": "string",
  "model": "string",
  "status": "queued|running|succeeded|failed",
  "submittedAt": "ISO-8601 UTC timestamp",
  "submitEndpoint": "string",
  "statusEndpoint": "string",
  "submittedPayload": {},
  "resolvedMedia": [],
  "rawSubmitResponse": {}
}
```

## Representative payloads by command family

### Nano Banana Pro

```json
{
  "model": "nano-banana-pro",
  "input": {
    "prompt": "make a poster",
    "image_input": ["https://example.com/ref.png"],
    "aspect_ratio": "1:1",
    "resolution": "1K",
    "output_format": "png"
  }
}
```

### GPT Image 2 prompt-only

```json
{
  "model": "gpt-image-2-text-to-image",
  "input": {
    "prompt": "make an image",
    "aspect_ratio": "auto",
    "resolution": "1K"
  }
}
```

### GPT Image 2 image-to-image

```json
{
  "model": "gpt-image-2-image-to-image",
  "input": {
    "prompt": "edit this image",
    "aspect_ratio": "16:9",
    "resolution": "2K",
    "input_urls": [
      "https://example.com/input.png"
    ]
  }
}
```

### Grok prompt-only

```json
{
  "model": "grok-imagine/text-to-video",
  "input": {
    "prompt": "camera moves forward",
    "aspect_ratio": "2:3",
    "mode": "normal",
    "duration": 6,
    "resolution": "480p",
    "nsfw_checker": false
  }
}
```

### Grok image-to-video

```json
{
  "model": "grok-imagine/image-to-video",
  "input": {
    "prompt": "@image1 animate this",
    "aspect_ratio": "16:9",
    "mode": "normal",
    "duration": "8",
    "resolution": "720p",
    "nsfw_checker": false,
    "image_urls": [
      "https://example.com/ref.png"
    ]
  }
}
```

### Veo

```json
{
  "prompt": "transition between frames",
  "model": "veo3_fast",
  "aspect_ratio": "16:9",
  "enableTranslation": true,
  "resolution": "720p",
  "imageUrls": [
    "https://example.com/a.png",
    "https://example.com/b.png"
  ],
  "generationType": "FIRST_AND_LAST_FRAMES_2_VIDEO"
}
```

### GPT-5.2 multimodal chat

```json
{
  "messages": [
    {
      "role": "user",
      "content": [
        {
          "type": "text",
          "text": "What is in this image?"
        },
        {
          "type": "image_url",
          "image_url": {
            "url": "https://example.com/reference.png"
          }
        }
      ]
    }
  ],
  "reasoning_effort": "low"
}
```

### Suno music

```json
{
  "prompt": "dreamy synth-pop under neon rain",
  "customMode": true,
  "instrumental": true,
  "model": "V3_5",
  "style": "synth-pop",
  "title": "Neon Rain",
  "negativeTags": "harsh, noisy",
  "callBackUrl": "https://example.com/callback"
}
```

### Suno lyrics

```json
{
  "prompt": "a nostalgic song about small town summers"
}
```

### Suno sounds

```json
{
  "prompt": "looping cyberpunk ambience",
  "soundLoop": true,
  "grabLyrics": true,
  "model": "V5_5",
  "soundTempo": 110,
  "soundKey": "Am",
  "callBackUrl": "https://example.com/callback"
}
```

---

## Service-specific deep dives

## GPT Image 2 mode switching

The `gpt-image-2` command is intentionally simplified for operators.

Instead of making users memorize two provider model names, the CLI accepts one family alias and derives:

- `gpt-image-2-text-to-image`
- `gpt-image-2-image-to-image`

This is valuable operationally because it lets the CLI present GPT Image 2 as:

- a text-only generation tool
- an image-conditioned editing tool

without splitting the user experience into two different commands.

## Grok text-to-video vs image-to-video

Grok is also a dual-mode family under one command alias.

This makes it easy to present Grok as:

- a lightweight prompt-led video ideation route
- a reference-driven animation route

This is useful for product positioning because the same command family covers both pure generation and source-guided motion.

## Veo generation type behavior

Veo has a different mental model from Grok:

- explicit Veo model variants
- explicit generation type support
- distinct Veo status route

The CLI keeps the user-facing entrypoint simple but still exposes the details operators need:

- `--veo-model`
- `--generation-type`
- translation toggle
- watermark
- image-conditioned workflows

## Suno music and sounds polling

Music and sounds both normalize through the Suno music polling branch.

Status mappings include states such as:

- `PENDING` → `queued`
- `TEXT_SUCCESS` → `running`
- `FIRST_SUCCESS` → `running`
- `SUCCESS` → `succeeded`
- several provider failure states → `failed`

When successful, URL extraction looks across:

- `response.sunoData[*].audioUrl`
- `sourceAudioUrl`
- `streamAudioUrl`
- `imageUrl`
- `videoUrl`
- `resultUrls`
- `audioUrls`

That makes the CLI resilient to slightly different Suno result shapes.

## Suno lyrics polling shape

Lyrics polling is distinct:

- dedicated submit endpoint
- dedicated status endpoint
- final useful data exposed under `response.data`
- normalized top-level `lyrics` list for convenience

This difference is why lyrics requires its own routing model and its own poll normalizer.

## Suno callback constraints from live validation

The most important Suno operational learnings are:

- callback support is not just decorative in provider docs
- lyrics effectively required callback in live validation
- music also had provider-side validation sensitivity around explicit provider model selection

These findings should influence both demos and production scripting.

**Recommended production stance:**

- always pass `--model` for Suno music and sounds
- always pass `--callback-url` for all Suno families, especially lyrics
- use `--save-job` for music and sounds to preserve exact async context

---

## Live validation and reliability notes

## What has been live-validated

The current gated live test harness has successfully exercised:

- GPT-5.2 text-only completion
- GPT-5.2 multimodal image input
- GPT Image 2 prompt-only generation
- GPT Image 2 image+prompt generation
- Grok prompt-only video generation
- Grok image+prompt video generation
- Suno music generation
- Suno lyrics generation
- Suno sounds generation

Artifacts are persisted under:

```text
outputs/live_tests/<timestamp>/<case>/
```

These fixtures include:

- submitted argv
- stdout JSON
- stderr
- saved job records where applicable
- final polled result
- extracted output URLs or lyrics payloads

## Specific provider findings

### Suno music

Live provider behavior required an explicit provider model and produced validation errors when omitted.

### Suno lyrics

Live provider behavior required `callBackUrl`.

### Suno sounds

Live validation passed using the save-job + wait workflow.

### Gemini

Gemini support was implemented but observed provider maintenance / availability issues in live usage and is excluded from this production-facing guide.

## Reliability interpretation

This does **not** mean the providers are perfectly stable. It means:

- the CLI request contracts are correct enough to complete real tasks
- the routing/polling model works end to end
- the CLI surfaces are credible for engineering use and internal product positioning

---

## Troubleshooting

## Missing API key

### Symptom

Commands fail with a configuration error.

### Cause

`KIE_API_KEY` is not set in `.env` or the environment.

### Resolution

Set:

```env
KIE_API_KEY=your_kie_api_key
```

Then rerun the command.

## Local image path fails

### Symptom

Upload or multimodal/generation commands fail before submission.

### Cause

The local file path does not exist.

### Resolution

Verify the path is correct and points to a readable local file.

## Remote vs local image misunderstanding

### Symptom

Unexpected upload behavior.

### Cause

The CLI treats:
- `http://` and `https://` values as already-remote
- everything else as a local path

### Resolution

If you want pass-through behavior, provide a full remote URL. If you want local upload-first behavior, provide a valid local path.

## Invalid model choices

### Symptom

Argument parsing fails or payload building raises an error.

### Cause

Unsupported values were passed for:
- `--veo-model`
- Suno sounds `--model`
- command aliases

### Resolution

Use only the supported values documented in this guide.

## Async timeout

### Symptom

`kie-cli wait` returns:

```json
{
  "status": "timeout"
}
```

### Cause

The task did not reach `succeeded` or `failed` before the CLI timeout limit.

### Resolution

- increase `--timeout`
- increase `--poll-interval` if desired
- inspect `lastStatus`
- retry later if provider latency is high

## Callback URL requirements

### Symptom

Suno provider rejects a request.

### Cause

Some Suno flows require `callBackUrl` provider-side even if the CLI does not enforce it locally.

### Resolution

Pass:

```bash
--callback-url https://example.com/kie-callback
```

## Provider maintenance / transient failures

### Symptom

A provider responds with maintenance or temporary availability errors.

### Cause

Upstream provider instability.

### Resolution

Retry later, avoid positioning the unstable family as production-ready, and prefer the command families validated in this guide.

---

## Positioning: what we can vend

This section is intended for internal platform, solutions, and business-development positioning.

`kie-cli` currently represents a compact but commercially meaningful AI service surface.

## 1. Image creation and editing

The CLI can vend:

- prompt-to-image creation
- reference-image editing
- campaign-style visual generation
- product visualization workflows

Backed by:

- `nano-banana-pro`
- GPT Image 2 prompt-only and image-conditioned modes

## 2. Video generation

The CLI can vend:

- text-to-video concept generation
- image-to-video animation
- transition-style frame-conditioned motion generation
- alternative video model families under one interface

Backed by:

- Grok text/image-to-video
- Veo with variant selection and generation-type controls

## 3. Multimodal LLM workflows

The CLI can vend:

- text generation
- prompt-file driven automation
- image-grounded visual analysis
- optional web-search grounded responses

Backed by:

- `gpt-5-2`

## 4. Music generation

The CLI can vend:

- prompt-driven song generation
- instrumental generation
- style- and title-conditioned music generation
- async automations around generated songs

Backed by:

- `suno music`

## 5. Lyrics generation

The CLI can vend:

- structured lyrics ideation
- async lyric drafting pipelines
- callback-aware provider workflows

Backed by:

- `suno lyrics`

## 6. Sounds generation

The CLI can vend:

- ambience generation
- loopable sound design
- tempo/key-conditioned effects generation
- reusable async non-song audio automation

Backed by:

- `suno sounds`

## 7. Reusable async automation workflows

One of the strongest platform features is not a single model, but the shared operational pattern:

- submit
- persist
- poll
- recover later
- normalize outputs

That gives `kie-cli` value as an automation primitive, not only a demo tool.

It is suitable for:

- CI/ops orchestration
- human-in-the-loop creative workflows
- pipeline handoff between submitter and finisher processes
- audit-friendly job persistence

---

## Verification sources for this guide

This guide is grounded in the repository’s current implementation and test corpus, especially:

- `src/kie_cli/cli.py`
- `src/kie_cli/client.py`
- `src/kie_cli/payloads.py`
- `src/kie_cli/status.py`
- `src/kie_cli/polling.py`
- `src/kie_cli/routes.py`
- `src/kie_cli/jobs.py`
- `src/kie_cli/llm.py`
- `tests/test_payloads.py`
- `tests/test_cli_jobs.py`
- `tests/test_jobs_polling.py`
- `tests/test_llm.py`
- `tests/integration/test_live_kie.py`
- `docs/journals/kie-cli-prototype.md`

## Quick-start recommendation

For most production usage, start with one of these patterns:

### Image

```bash
.venv/bin/kie-cli image gpt-image-2 \
  --prompt "A cinematic night city poster" \
  --save-job outputs/jobs/gpt-image2.json \
  --json
```

### Video

```bash
.venv/bin/kie-cli video grok \
  --prompt "A camera slowly dollies through a neon corridor" \
  --save-job outputs/jobs/grok-video.json \
  --json
```

### Multimodal LLM

```bash
.venv/bin/kie-cli llm gpt-5-2 \
  --prompt "What do you see in this image?" \
  --image ./image.png \
  --json
```

### Suno music

```bash
.venv/bin/kie-cli suno music \
  --prompt "A dreamy synth-pop song about neon rain" \
  --model V5_5 \
  --callback-url https://example.com/kie-callback \
  --save-job outputs/jobs/suno-music.json \
  --json
```

### Wait for completion

```bash
.venv/bin/kie-cli wait \
  --job-file outputs/jobs/suno-music.json \
  --poll-interval 5 \
  --timeout 900 \
  --json
```
