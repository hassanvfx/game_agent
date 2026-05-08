# Refactor Compliance Spec

## Purpose
Define the baseline compliance targets for the refactor agent before machine-readable schemas are introduced.

## Required Compliance Themes
- output remains reconstructable from saved evidence
- transformed result is produced from a working clone
- required artifacts exist for each attempt
- judge-facing evidence is sufficient for structured review
- publish is blocked until validators pass

## Retry Loop
- Attempt 1: initial refactor
- Attempt 2: remediation using judge feedback
- Attempt 3: final remediation pass
- Preserve all attempt artifacts even when superseded

## Non-Goals For This Milestone
- bounded concurrency
- multi-worker scheduling
- final schema enforcement logic
