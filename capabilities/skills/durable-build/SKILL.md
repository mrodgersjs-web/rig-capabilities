---
name: durable-build
description: "RIG build lane for solutions, applications and durable systems — the one loop that cannot be marked done, sealed, or advanced past Proof without a freshly verified D85 certificate bound to the exact build bytes (non-forceable halt tier). Intent → Diagnosis+owner → Build → Verify → Proof, with the diagnosis/coordinate/owner recorded before any code. Research, ideation, review and repair loops stay open; use this one when the work leaves durable state behind."
when_to_use: "Starting any solution/app/durable-system build that must end certified: a new service, schema change, skill/agent/loop that ships to other agents, or any change you intend to call 'done' and push. Not for: pure research, diagnosis-only work, or a bounded repair you will not certify."
version: 1.1.0
owner: rig-intelligence
domain: Agent engineering / build lane
status: Candidate
verified_by: UNVERIFIED
verified_on: UNVERIFIED
acl: public
relates_to: rig-build-standard, rig-stackwright, iqrsqpi-v20, iqrsqpi-v20-slice, phase-discipline-loop, proof-loop, gate-d-loop, git-push-safety-loop
outcome: "code-engineering: a build either leaves this loop with a recomputed certificate and a sealed packet, or it is honestly BUILT_UNVERIFIED — there is no path from 'feels finished' to 'done'"
done_when:
  - file:capabilities/skills/durable-build/loop.yaml
  - file:capabilities/skills/durable-build/tests/cases.json
  - cmd:bin/rig-loop test durable-build
  - grep:capabilities/skills/durable-build/loop.yaml:d85_certified
  - grep:capabilities/skills/durable-build/loop.yaml:build_diagnosis
  - cmd:python3 -m unittest tests.test_durable_fixtures
  - cmd:python3 -m unittest tests.test_build_intake
quality_floor: 0.7
---

# durable-build

The build lane. Same IQRSQPI spine, one hard addition: **Proof is a certificate,
not a feeling.** `advance()` treats the `d85_certified` gate as halt-tier and
refuses `force`, so no note, no deadline and no deadline-pressure turns a red
ratio into a pass.

| Stage | What must exist before it advances |
|---|---|
| `I` Intent | goal, an **executable** done-test (`- cmd:…`), out-of-scope, budget |
| `D` Diagnosis | cell id, all seven level fits, four mode-necessity assessments, the T-rule owner from the contract, and the rejected fits |
| `B` Build | the change, the `inventory → classify → score` invocation, artifact list |
| `V` Verify | ≥1 green check, ≥1 planted failure proven RED→GREEN, ≥1 independent verdict |
| `P` Proof | `d85_certified` over `build.json` + `certificate.json` inside the declared root, `build_diagnosis` over a cell-bound `diagnosis.json` plus a live outcome-index row for that same cell, then a sealed ProofPacket |

## Minting the certificate (the only honest way)

```sh
D85=capabilities/skills/rig-determinism-85/bin/rig-determinism-85
python3 $D85 checklist  <root>/build.json --root <root> --process-id <id> > <root>/certificate.json   # exit 0 only
python3 $D85 verify-cert <root>/build.json <root>/certificate.json --root <root>                       # gate re-runs this
```

The gate re-executes `verify-cert` on every evaluation and re-hashes both files
before and after, so a certificate minted against a build you then edited fails
with `build or certificate changed during verification`. That is the intended
behaviour: edit → re-mint → re-verify.

## What this loop refuses

- `UNKNOWN_PROCESS` → register an immutable process version first (D85 `inventory`
  → `classify`), never re-run the same bytes hoping for a different verdict.
- exit 2 / BLOCK → terminal for that version; ship a genuinely revised version.
- A2–A4 builds → the certifier supports A1 only; name the gap, do not relabel.
- Any `force` on Proof → recorded, refused, run stays where it was.
- A certificate whose cell has no live outcome-index row → `build_diagnosis` refuses.
  A row bound to a stale criteria pack refuses too; the pack hash is recomputed, never read from the packet.

## The cell-bound outcome row (`build_diagnosis`)

Proof is bound to one lattice cell, so the certificate cannot be pasted onto a
different piece of work:

```py
from rig_capabilities import build_diagnose, build_index   # repo on sys.path
diag = build_diagnose.diagnose(payload)                     # cell must be in the 588
build_index.open_live(Path(repo), "diagnosis_index.jsonl").insert(diag["cell_id"], "build.json")
```

`insert` stamps the row with the live golden-pack sha, which is what the gate
compares — hand-written rows are rejected. `open_live` takes a `Path`, not a str.

Run it: `bin/rig-loop activate durable-build` (walk mode stops after each stage).
Test it: `bin/rig-loop test durable-build` — six planted cases: no certificate,
`force` attempted, a real mint clearing Proof, the builder certifying itself, the
build altered after minting, and a certificate with no cell-bound outcome row.
