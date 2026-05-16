# Network Policy

## Purpose
Define the shared network and remote-resource policy that supports the `operators_v2/` pipeline, especially media mapping and HTML/CDN execution constraints where applicable.

## Authority Model
- The active `operators_v2/` stage prompts are the primary authority for operational behavior involving remote resources.
- This root policy defines shared guardrails, allowlist expectations, and validation concerns for publish readiness.
- Remote resources are allowed only when they are explicitly supported by the active operator workflow and remain within approved policy boundaries.

## Core Policy
- Arbitrary networking is not allowed.
- Remote assets, libraries, fonts, audio, GIFs, or similar resources must not be introduced unless they are explicitly allowed by the active operator stage or approved catalog authority.
- Network behavior must never change gameplay logic, controls, pacing, or boot flow.
- Remote dependencies must not make the game unusable if they fail, unless the stage explicitly depends on them and validation accepts that risk.
- Publish decisions should prefer predictable, low-fragility resource usage.

## Approved Resource Model
Remote usage is valid only when one of the following is true:
- it is selected from an approved workspace-local catalog that points to approved remote assets
- it is explicitly allowed by the active operator prompt
- it is approved by an allowlisted-host policy used by the runner or validator

## Allowlist Direction
Legacy allowlist source:
`/Volumes/Elements/full_7k_qa_release_whitelabel/config/allowed_remote_hosts.json`

Until a canonical machine-readable local policy is introduced:
- treat allowlisted-host behavior as a validator concern tied to the active pipeline
- do not assume open internet access is acceptable
- do not introduce arbitrary hosts outside the approved workflow

## Operator-Aligned Interpretation
- Stage 02 may use HTML/CDN-safe enhancement patterns when consistent with the active workflow.
- Stage 03 may use approved catalog-backed media references when consistent with media policy.
- Root policy should not prohibit operator-approved resource usage, but it should continue to block arbitrary or unsupported networking.

## Mobile-First Network Constraints
- Remote enhancements must not create blocking full-screen loaders, oversized consent UI, or obstructive banners on small screens.
- If a remote dependency fails, the game should degrade gracefully without trapping the player behind broken UI.
- Preserve the existing mobile-safe layout as closely as possible instead of adding heavy remote UI chrome.

## Validation Expectations
Validators should check:
- whether remote usage is actually allowed by the active stage and supporting policy
- whether hosts or remote URLs remain within approved boundaries
- whether the game remains usable when remote media partially fails
- whether added resource behavior stays compatible with small-screen usability
- whether remote usage introduced unnecessary fragility compared with a safer local or catalog-backed option

## Follow-Up
Add a canonical machine-readable policy file and validator wiring in a later milestone.