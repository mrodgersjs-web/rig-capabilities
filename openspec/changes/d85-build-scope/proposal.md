# Restore D85 to build quality

## Intent

Mike clarified on 2026-09-11 that D85 exists to ensure solution and app builds are at least 85% deterministic and follow RIG Lattice. It must not prevent ordinary authorized work. This current-task instruction supersedes older universal D85 tool-admission policy.

## Change

- Remove D85's universal pre-tool interception from rig-loop. Keep the existing loop stage, kill-switch, and Gate-D checks.
- Preserve source-derived inventory, classification, four-ratio scoring, certification, and certificate verification. Recompute the live score during certification instead of trusting a submitted boolean.
- Require validated Lattice routing context during build certification, including recomputed BMS evidence and an A1 failure record when escalating.
- Correct shared policy and startup messaging. Keep explicit legacy signed admission and launcher commands for already configured consumers; they are not a prerequisite for normal tools.

## Boundaries

This does not authorize sends, spend, deployment, credential changes, destructive actions, or data export. Those retain their own scoped authorization rules. D85 remains an artifact-quality boundary, not a replacement permission system.

## Verification

Routine shell, memory, Python, read, and edit calls must pass the D85 layer without a build certificate. An active loop's Gate-D and stage policies must still apply. A build with missing or inconsistent Lattice context, a failing live D85 score, stale source, or altered certificate must fail certification. Test failures must remain visible.
