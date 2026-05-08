# KIE CLI Prototype

Focused Python CLI for production-facing KIE workflows across:

- image generation and editing
- video generation
- multimodal LLM usage
- Suno music, lyrics, and sounds
- durable async polling and saved job records

## Production-ready documented surface

This repository’s production-facing documentation currently covers:

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

Gemini support exists experimentally in the codebase, but it is currently provider-blocked / unreliable in live validation and is intentionally excluded from the production-facing documentation set.

## Read the full guide

Primary documentation:

- [`docs/kie-cli/comprehensive-guide.md`](docs/kie-cli/comprehensive-guide.md)

The comprehensive guide includes:

- executive overview and capability matrix
- installation and environment setup
- CLI mental model and async lifecycle
- command-by-command usage and examples
- payload and response contracts
- durable job record schema
- Suno-specific live findings and callback caveats
- troubleshooting and product positioning notes

## Quick setup

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -e ".[dev]"
cp .env.example .env
```

Populate `.env` with:

```env
KIE_API_KEY=your_kie_api_key
KIE_BASE_URL=https://api.kie.ai
KIE_UPLOAD_BASE_URL=https://kieai.redpandaai.co
```

## Quick examples

### Image generation

```bash
.venv/bin/kie-cli image gpt-image-2 \
  --prompt "A cinematic night city poster" \
  --save-job outputs/jobs/gpt-image2.json \
  --json
```

### Video generation

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

### Wait for an async result

```bash
.venv/bin/kie-cli wait \
  --job-file outputs/jobs/suno-music.json \
  --poll-interval 5 \
  --timeout 900 \
  --json
```

## Verification

```bash
.venv/bin/python -m pytest -q
```
