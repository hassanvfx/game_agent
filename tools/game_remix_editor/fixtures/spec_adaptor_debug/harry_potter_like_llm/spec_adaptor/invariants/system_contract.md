# System Contract

## Purpose
Define the shared operating contract for the standalone whitelabel agent orchestration platform.

## Core Guarantees
- Source game folders are immutable inputs.
- Every transformation operates on a working clone.
- Refactor, judge, and identity are separate roles.
- Publish occurs only after validation and judge pass.
- Important state transitions must be persisted to disk.

## Execution Model
1. ingest manifest
2. validate inputs
3. create run workspace
4. clone source to working area
5. execute refactor attempt
6. execute judge pass
7. retry up to three attempts if needed
8. validate outputs
9. publish compliant output
10. optionally run identity enrichment
11. refresh dashboard state

## Observability Contract
Canonical state lives in JSON / JSONL on disk.
HTML views are read-only polling surfaces over those canonical files.
