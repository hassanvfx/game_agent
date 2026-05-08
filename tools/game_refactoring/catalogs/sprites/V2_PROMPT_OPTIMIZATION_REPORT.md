# V2 Prompt Optimization Report

## Summary

The V2 sprite prompt optimization work upgraded `sprites_expanded_v2.json` into a cleaner, more generation-ready catalog for the game remix editor asset pipeline.

The final optimized catalog contains 600 sprite/background asset entries, with all prompt optimization chunks completed successfully.

Final optimizer result:

- Completed chunks: 10 / 10
- Overall progress: 100%
- Failed chunks: 0
- Pending chunks: 0
- Running chunks: 0
- Active optimizer/KIE processes: none

The optimized catalog is saved in:

```txt
sprites_expanded_v2.json
```

The V2 dashboard was also regenerated at:

```txt
sprites/dashboard_v2.html
```

## What This Achieves

### 1. Better Generation Prompts

The main achievement is improving the text prompts used to generate sprite and background assets.

The optimizer rewrote the `usage` and `prompt` fields for every asset so that they are more specific, more visual, and more useful for image generation.

This helps generated assets become:

- More consistent with the intended gameplay role
- More readable as game sprites
- Better aligned with their taxonomy/category
- Less generic
- Easier for an image model to interpret
- More suitable for transparent sprite assets and opaque background assets

### 2. Full V2 Catalog Coverage

The optimizer processed the full flat V2 catalog:

```txt
sprites_expanded_v2.json
```

The catalog contains 600 asset records. Each record includes fields such as:

```json
{
  "name": "...",
  "url": "...",
  "style": "...",
  "usage": "...",
  "prompt": "..."
}
```

All records were covered by the optimization run.

### 3. Chunked, Resumable Optimization

A robust worker was created for the optimization process:

```txt
sprites/v2_optimize_prompts.py
```

The worker does not try to process the entire catalog in one fragile request. Instead, it groups and processes the catalog in chunks.

The V2 catalog is flat, so the optimizer groups assets by URL taxonomy folder. For example, from a URL like:

```txt
/assets/images/sprites/block_builder/builder_avatar.png
```

the optimizer extracts the group:

```txt
block_builder
```

The worker then processes these groups in chunks of 10 query groups.

Final processing structure:

- 97 URL-derived query groups
- 10 query groups per main chunk
- 10 total chunks
- Smaller internal asset batches used to avoid oversized LLM responses

This makes the system safer, easier to resume, and less likely to lose progress.

### 4. KIE-Backed LLM Prompt Editing

The optimizer uses the neighboring KIE API CLI instead of local manual edits.

The LLM command used by the worker is based on:

```bash
../../kie-api/.venv/bin/kie-cli llm gpt-5-2
```

The worker sends each batch to the KIE-backed LLM and requests optimized `usage` and `prompt` text.

This means the catalog improvements were generated through the actual KIE LLM path that the project can reuse later.

### 5. State Tracking and Retry Safety

The optimization process saves progress in:

```txt
sprites/v2_prompt_optimize/state.json
```

It also records historical failures in:

```txt
sprites/v2_prompt_optimize/failures.json
```

Per-job artifacts are stored under:

```txt
sprites/v2_prompt_optimize/jobs/
```

This gives the pipeline important operational benefits:

- Failed chunks can be retried
- Interrupted runs can resume
- Completed chunks are not repeated unnecessarily
- Raw LLM responses are preserved
- Prompt files and optimized batch outputs are saved for review
- The final status can be audited

The final state shows every chunk completed successfully.

### 6. Safer Merge Behavior

The worker does not blindly replace the entire catalog with raw LLM output.

Instead, it validates the returned patches and only merges the fields that should change:

- `usage`
- `prompt`

The original catalog structure, asset names, URLs, and styles are preserved.

This reduces the risk of corrupting the asset list, losing URLs, or changing identifiers required by the rest of the pipeline.

### 7. Prompt Validation and Normalization

The optimizer includes validation and cleanup logic to keep prompts consistent.

It checks for common problems such as:

- Missing transparent background wording for sprite assets
- Transparent background wording accidentally applied to opaque backgrounds
- Overly generic banned phrases
- Invalid or incomplete LLM output
- Truncated or malformed JSON responses

It also normalizes several generic phrases into better game-art wording.

Examples:

| Generic Phrase | Replacement |
| --- | --- |
| `core task object` | `primary objective prop` |
| `interactive environment` | `readable gameplay scene` |
| `simulator character` | `simulation avatar` |
| `high quality asset` | `polished production sprite` |
| `game asset` | `game-ready visual element` |

This helps keep the optimized catalog cleaner and more useful for downstream generation.

### 8. Dashboard Support for V2 Catalogs

The dashboard renderer was updated so it can understand both the older nested catalog format and the newer flat V2 catalog format.

Updated file:

```txt
sprites/render_dashboard.py
```

The regenerated V2 dashboard is:

```txt
sprites/dashboard_v2.html
```

This allows review of the optimized V2 catalog in a browser-friendly format.

### 9. KIE CLI Improvements

The neighboring KIE API CLI was improved to better support long LLM prompt optimization jobs.

Updated files:

```txt
../../kie-api/src/kie_cli/client.py
../../kie-api/src/kie_cli/cli.py
../../kie-api/src/kie_cli/llm.py
```

The KIE client and CLI now support:

- Configurable request timeout
- Larger completion token limits
- Passing `max_completion_tokens` into the GPT 5.2 chat payload

These changes helped prevent the optimizer from failing on larger catalog chunks.

## Final Optimizer State

The final state recorded all chunks as completed:

```txt
chunk_001: completed
chunk_002: completed
chunk_003: completed
chunk_004: completed
chunk_005: completed
chunk_006: completed
chunk_007: completed
chunk_008: completed
chunk_009: completed
chunk_010: completed
```

Some chunks required retries due to timeout, malformed response, or validation failures, but all were eventually completed and merged.

## Files Produced or Updated

### Main Optimized Catalog

```txt
sprites_expanded_v2.json
```

This is the final optimized V2 sprite/background catalog.

### Optimizer Worker

```txt
sprites/v2_optimize_prompts.py
```

This is the resumable KIE-backed optimization worker.

### Optimizer State and Artifacts

```txt
sprites/v2_prompt_optimize/state.json
sprites/v2_prompt_optimize/failures.json
sprites/v2_prompt_optimize/jobs/
```

These files preserve progress, failures, prompts, raw responses, and optimized batch outputs.

### Dashboard

```txt
sprites/dashboard_v2.html
```

This is the regenerated review dashboard for the optimized V2 catalog.

### Dashboard Renderer

```txt
sprites/render_dashboard.py
```

This was updated to support flat V2 catalog entries.

### KIE CLI Support Files

```txt
../../kie-api/src/kie_cli/client.py
../../kie-api/src/kie_cli/cli.py
../../kie-api/src/kie_cli/llm.py
```

These were updated to support longer and more controllable LLM optimization requests.

## Why This Matters

This work moves the project from a basic expanded sprite catalog toward a more production-ready content pipeline.

Before this work, the V2 catalog had asset entries, but the prompts were not yet systematically optimized for high-quality generation.

After this work:

- The full 600-entry catalog has optimized prompt text
- The editing process is reproducible
- The optimizer can resume after interruptions
- Failures are logged instead of silently lost
- The dashboard can display the V2 catalog
- The KIE LLM tooling is better prepared for future batch jobs
- The catalog is better suited for image generation and review

## Recommended Next Steps

Possible next stages are:

1. Review `sprites/dashboard_v2.html` visually.
2. Run a validation report over `sprites_expanded_v2.json`.
3. Begin generating images from the optimized V2 prompts.
4. Adapt the live image generation pipeline to use the V2 catalog and `sprites/live_v2`.
5. Use the optimizer workflow again if more catalog entries are added later.