# Autonomy Ladder (v19) — who may do what, in code

| level | capability | lanes that hold it | enforced by |
|---|---|---|---|
| L0 | draft on request | every surface | `/write` flow — packet first, always |
| L1 | score + gate autonomously | public + internal | `rig_comms score` — deterministic, no side effects |
| L2 | ship to internal lanes (specs, prompts, code, research) | internal | `ship` writes a sha256 packet; gate must be green NOW |
| L3 | ship outward (linkedin, emails, substack…) | public | gate green + Gate-D typed approval (one context ≠ next) |
| L4 | love-notes | private | **machine never reaches L4**: exit 3 without `--human`; no scoring, no ledger outcome, no federation |

The ladder is not prose: `surfaces.py` lane fields, `gates.run()` exit 3,
`mcp.py` PRIVACY_LOCK, and the packet `--human` requirement are the same rule
in four places. Red-team proofs in RED-TEAM.md.

Readiness (v19.9): the highest attempt recorded is
`run-d24ea776cb2eadeeef66` — Strategy Studio HOLD at `owner.explicit_disposition`
(by design: the owner gate is the point, not an obstacle). The live readiness
state of Comms OS v2.0 is exactly: doctor green, gate suite green, push frozen
at `gd_1788739011063` until Mike types approval.
