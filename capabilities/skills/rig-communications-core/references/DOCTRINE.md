# RIG Systems Engineering Doctrine (V11)

Machine-enforceable and operational principles for this repository and adopters.

## Canonical contract

Every communication follows:

`Wound → Mirror → Autonomy → Qualification → Open Loop`

## Testable doctrine invariants

1. Every ship candidate is scored and gated (no neutral output).
2. Banned phrases are fail-closed (`BLOCK`).
3. Formula weights are deterministic and reproducible (weights sum to ~1.0).
4. Evidence-cite claims or do not make them.
5. On uncertainty, fail closed.
6. No secrets/credentials/tokens/cookies committed.
7. Backward compatibility with existing `src/` engines is preserved.
8. Every decision is observable and traceable through structured reports.

## Enforced in code

`rig_comm.doctrine.validate_doctrine()` checks:
- Formula weight sum invariants
- Banned phrase violations in provided artifacts

CI runs doctrine checks via:

```bash
rig doctrine-check --artifact templates/cold-email.md --artifact templates/reply.md
```
