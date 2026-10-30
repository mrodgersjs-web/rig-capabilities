# Mission composition behavior

## Read-only composition

Given a natural-language coding request and runtime, the system SHALL return
either a hash-bound proposal or an explicit abstention. The proposal SHALL
identify the meta-agent, one primary writer, a read-only verifier, an exact
meta-skill file, prompt layers and their statuses, Memory OS reference
metadata, and a disabled execution boundary. It SHALL never treat a draft
prompt as calibrated.

## Drift and authority

Before use, validation SHALL recompute referenced file hashes and reject a
second writer, duplicate roles, packet mutation, or unauthorized execution.
Memory failure SHALL be reported as degraded with no backend fallback and no
claim that context was loaded.

## Jev boundary and completion

The system SHALL use local Jev for a typed, logged shadow meta-lane decision.
It SHALL NOT silently send the request to a hosted provider when local Jev is
unavailable. Jev SHALL NOT execute a tool, select an unpermitted asset, approve
an outward action, or certify a coding-agent completion claim. A completion
claim SHALL require current artifact and behavioral evidence, independent
verification, and a calibrated semantic gate; missing or degraded evidence
SHALL prevent an automatic DONE status.

## Weekly evidence

The weekly cycle SHALL report inaccessible sources and failing regressions.
It SHALL keep public source metadata rather than full bodies and SHALL not
promote, install, or dispatch a candidate. A route-suite pass alone SHALL NOT
count as an agent or prompt outcome pass.
