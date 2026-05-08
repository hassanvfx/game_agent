# Creative Recovery Policy

## Purpose
Define the recovery policy for the operator-driven remix system when the specimen is broken, incomplete, empty, or still non-viable after normal staged work.

## Authority Model
- The `operators_v2/` pipeline is the leading operational authority.
- This root policy defines how recovery should behave when a safe playable result cannot be achieved through ordinary stage execution alone.
- Recovery must support the stage model rather than compete with it.
- `operators_v2/04_final_code_ui_mobile_repair.md` remains the authority for strict non-gameplay repair behavior during the final repair stage.

## Recovery Standard
The worker should not stop at superficial restyling if the final result is still broken or non-viable. When a playable, coherent recovery is possible, the worker should complete the experience in a way that preserves gameplay truth where possible and remains faithful to the active remix direction.

Recovery must remain:
- playable
- coherent
- faithful to implemented or inferable mechanics
- faithful to the active remix direction
- consistent with platform safety and mobile-first requirements

## Recovery Order Of Operations
Follow this order strictly:

1. **Preserve**
   - Preserve the original gameplay structure, mechanics class, controls, progression shape, runtime boot flow, and interaction semantics whenever the specimen is already viable.
   - Preserve the existing layout structure as closely as possible when it is already readable and mobile-safe.
   - Prefer in-place recovery over replacement.

2. **Repair**
   - If the specimen is partially broken, repair runtime-critical issues first.
   - Prioritize:
     - syntax/runtime errors
     - missing UI flow required to start play
     - broken control paths
     - unreadable or obstructed HUD
     - overlap or mobile-layout failures
     - broken or dangling asset references
     - audio/network/dependency issues that block the active operator workflow

3. **Complete Conservatively**
   - If the specimen remains broken, empty, or non-viable after reasonable repair attempts, complete the missing experience conservatively in a way that restores a usable game shell without inventing unnecessary redesign.
   - Reconstruct only what is necessary to restore a playable, coherent experience.
   - Keep the recovered structure as close as practical to the original or inferable design.

4. **Remix-Coherent Recovery**
   - If reconstruction is necessary, align the repaired experience with the active remix direction and operator-stage intent.
   - Do not leave the final output broken if a concise playable recovery is achievable.

## Mobile-First Recovery Rules
Even in recovery mode:
- mobile-first thinking is mandatory
- assume the incoming layout may already be reasonably mobile-friendly
- preserve existing mobile-safe structure whenever possible
- use the smallest layout intervention needed to restore safety and readability
- avoid UI overlap, blocked controls, off-screen actions, and oversized overlays
- protect play space and control zones before decorative ambition
- if a recovered layout choice is readable but bulky, prefer the more compact readable option

## Recovery Constraints
Even during recovery:
- preserve mechanics when they are inferable and salvageable
- preserve controls or close control semantics when possible
- preserve the intended game type when reasonably inferable from the specimen
- keep the result runnable and readable
- keep menus, counters, overlays, and HUD away from control hit zones
- obey audio, network, system, and compliance constraints as interpreted through the operator pipeline
- avoid arbitrary remote dependencies outside approved workflow rules
- do not rebuild from zero unless recovery truly requires it

## Evidence Expectations
Recovery work should leave reviewable evidence of:
- what was preserved
- what was repaired
- what had to be reconstructed
- why reconstruction was necessary
- how mobile safety and gameplay continuity were protected

## Failure Rule
Treat the run as a failure only when:
- the specimen cannot be made playable without violating core platform or stage constraints
- the intended mechanics are too ambiguous to recover responsibly
- the runtime remains unstable after reasonable repair and recovery attempts
- recovery would require a misleading or unjustified redesign that no longer reflects the specimen

In that case, the worker should still:
- leave clear evidence
- preserve generated artifacts
- return an honest completion summary rather than pretending success

## Prompt Discipline
Workers must read and honor all referenced materials before editing:
- active operator stage prompt(s)
- system contract
- refactor compliance spec
- supporting root policies relevant to the current stage
- this creative recovery policy when recovery is needed

None of these materials should be treated as optional context.