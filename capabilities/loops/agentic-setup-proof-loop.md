---
outcome: "agent-engineering: the agentic setup loop carries one framework from request to closed receipt - probe, select, install, secrets, hello on fake then local model, durable or observed feature, tests with a planted failure, Gate-D - and ends DONE, HELD, or HALTED with the gate named."
done_when:
  - file:capabilities/loops/agentic-setup-proof-loop.md
  - cmd:python3 scripts/assert_loop_termination.py capabilities/loops/agentic-setup-proof-loop.md
  - cmd:python3 capabilities/skills/agentic-systems-setup/scripts/validate_hierarchy.py
quality_floor: 0.7
---

# Agentic Setup Proof Loop - META loop

Owner: `agentic-setup-conductor`. Harness: `capabilities/harnesses/agentic-setup-session.yaml`.
Skill: `agentic-systems-setup`. Main loops reused: `proof-loop`, `adversarial-verification-loop`,
`phase-discipline-loop`, `gate-d-loop`, `git-push-safety-loop`.

JEV first: every gate transition is a typed judgment routed to `rig-s1gate check agentic.setup`
(and `plan.readiness` for the selection) BEFORE any frontier review. Classifier down: DEFER the
transition; the loop waits, it never guesses.

## Loop

```
PROBE -> SELECT (+L0 docs) -> INSTALL (L1) -> SECRETS -> HELLO FAKE (L2) -> HELLO LOCAL (L3)
  -> DURABLE/OBSERVED (L4) -> TESTS + PLANT -> VALIDATE (proof_ladder.py) -> JUDGE (agentic.setup)
  -> GATE-D (L5 or HELD) -> CLOSE (lessons) -> DONE | HELD | HALTED
```

Kill switch: three consecutive failures at the same gate, any credential value found by
leak_scan.py, or any outward action attempted without an approval id ends the loop with
`status: HALTED` and the gate named.

## Gates

| Gate | Step | Pass Condition | On fail |
|---|---|---|---|
| G1 | probe | probe.json dated today; a local model route ANSWERED_OK or recorded BLOCKED | re-probe once from an Orca terminal, then BLOCKED |
| G2 | select | matrix row named, when-not answered, L0 docs fetched today with sha and pin | rewrite selection, max 3, then ESCALATE |
| G3 | install | L1 receipt exit 0 in the named route | fix per lessons AS-01 to AS-06, max 3, then BLOCKED |
| G4 | secrets | leak_scan.py exit 0; env files ignored by git | HALT: remove the value, rotate under Gate-D |
| G5 | hello | L2 on a fake and L3 on a local endpoint, content asserted | fix wiring, max 3, then BLOCKED |
| G6 | durable or observed | L4 with run id read back | degrade: close with L3 and the reason |
| G7 | tests | assertions counted; planted failure RED then GREEN with bytes moved | fix tests, max 3, then ESCALATE |
| G8 | judge and gate | proof_ladder.py exit 0; agentic.setup clears or DEFERS; outward held or approved | fix receipt; wait for Mike |

**On-fail:** G1, G2, G3, G5, G7 are halt-tier: HALT the session at that gate and name the failing check.
**On-fail:** G4 is halt-tier with no retry: HALT on any credential value and hold rotation for Gate-D.
**On-fail:** G8 is stop-tier: HALT outward work until Mike's approval id exists; the session may close HELD.

## Definition of Done

A session is done when:
1. `proof_ladder.py <run>/receipt.json` exits 0 and names the highest proven level;
2. every level not reached is in `blocked` with its failing command or in `not_attempted` with a reason;
3. `leak_scan.py` exits 0 over the project and the run folder;
4. the receipt has an agentic.setup decision id or an explicit DEFERRED record;
5. anything outward carries Mike's approval id or is recorded in `held_at_gate`;
6. the session's lessons were fired with `validate_lessons.py` and new failures were appended.
