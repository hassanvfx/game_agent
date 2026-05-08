# Theme Policy

## Purpose
Define the shared theme policy that supports the `operators_v2/` pipeline, especially narrative adaptation, visual identity work, media mapping, and mobile-first UI safety.

## Authority Model
- The active `operators_v2/` stage prompts are the leading authority for applied theme decisions.
- This root policy defines shared defaults, readability constraints, and mobile-first theme guardrails.
- Theme choices must support stage behavior rather than override it.

## Core Direction
- Reuse inherited theme knowledge from the legacy workspace while keeping this project orchestration-first and operator-driven.
- Theme adaptation should reinforce the remixed concept without changing gameplay truth.
- When the active operator stage calls for stronger thematic transformation, follow the operator prompt.
- When the incoming layout is already readable and mobile-friendly, preserve it as closely as possible.

## Typography Direction
- Font choices should follow the active operator workflow and any approved catalog authority.
- Primary fonts should support branding, titles, and thematic framing.
- Secondary fonts should support HUD, UI, instructions, and mobile readability.
- Decorative typography must never reduce clarity, crowd controls, or bloat the layout on narrow screens.
- If the existing type scale is already compact and functional on mobile, prefer preserving it with minimal change.

## Color and Identity Direction
- Palette and identity work should be coherent rather than random per-element drift.
- Theme changes should preserve contrast, gameplay readability, and control clarity.
- Character, HUD, panels, buttons, overlays, and feedback states should feel like part of the same world when visually adapted.
- Decorative treatment must remain subordinate to readability and playfield visibility.

## Mobile-First Theme Constraints
- Mobile-first thinking is mandatory.
- Keep HUD, counters, modals, overlays, and panels compact on small screens.
- Avoid oversized headings, inflated padding, thick chrome, or decorative bulk that reduces usable play space.
- Preserve safe tap targets without expanding UI containers more than necessary.
- If a choice is between a more expressive theme treatment and a more compact readable mobile layout, choose the compact readable option.
- Avoid unnecessary layout movement when the original structure is already mobile-safe.

## Validation Expectations
Validators should confirm:
- theme work stays consistent with the active operator stage
- typography remains readable on small screens
- decorative decisions do not obstruct controls or gameplay
- theme changes remain coherent across title, HUD, overlays, and key feedback states
- layout remains close to the original when the original was already mobile-friendly

## Follow-Up
Later milestones may formalize:
- palette references
- theme token expectations
- machine-readable compliance checks for branding, typography, and compact mobile behavior