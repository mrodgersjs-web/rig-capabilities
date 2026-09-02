---
name: great-harness-assembly-contract
lane: agent-engineering
source: canonical-curated
exemplar_of: harness-assembly-contract.md
description: Reference exemplar — the assembly contract emitter GREEN on all 66 canonical harness YAMLs and on the fixture harness, GREEN on verify of the emitted contract, and RED (exit 2, one distinct clause each) on the four planted divergences (stage without a port, binding to an undeclared port, fingerprint that does not match the YAML, edge to a nonexistent stage)
---

# harness-assembly-contract — reference

Canonical asset `harness-assembly-contract` (command). Body:
`capabilities/commands/harness-assembly-contract.md`; emitter/checker:
`scripts/harness_assembly_contract.py`.

> A harness is a set of sockets with bound atoms, not an ordered pile of gate
> ids. The emitter turns each canonical YAML into ports / bindings / swap
> points / fingerprint / edges — deterministically, sorted, fingerprint =
> sha256 over the canonical stage list — and the verifier recomputes the stage
> list from the YAML and goes RED when the contract diverges.

## What good looks like

The real port the emitter derives for fixture stage `1.2` — the stage's
requirement declared as a socket, with the artifact it consumes upstream and
the artifact it hands downstream, visible as data rather than prose:

```json
{
  "category": "Scope",
  "consumes": [".rig/asm/scope.md"],
  "data_kind": "artifact",
  "failure_tier": "halt",
  "kind": "capability",
  "port": "p::1.2",
  "produces": [".rig/asm/findings.json"],
  "requires": "Every finding is anchored to a path listed in .rig/asm/scope.md",
  "stage": "1.2"
}
```

The cross-port edge that makes the dependency checkable — gate `3.1` consumes
`.rig/asm/findings.json`; the verifier goes RED when no upstream stage
produces it, and this edge is the evidence that one does:

```json
{
  "artifact": ".rig/asm/findings.json",
  "data_kind": "artifact",
  "from_port": "p::1.2",
  "from_stage": "1.2",
  "hook_order": 4,
  "to_port": "p::3.1",
  "to_stage": "3.1"
}
```

And the permission consequence: the fixture's `stop`-tier gate becomes a
port of `kind: permission` whose `bound_atom` is recorded, so a denial names
the policy that produced it:

```json
{
  "bound_atom": "fixture-assembly-valid::2.1",
  "interface": {"data_kind": "artifact", "failure_tier": "stop", "kind": "permission"},
  "port": "p::2.1",
  "swappable": false,
  "via": "capability_gates[1].gates[0]"
}
```

`--emit capabilities/harnesses/*.yaml` → **exit 0**, 66 contracts, every one
carrying populated `ports[]`, `bindings[]`, `fingerprint`, `edges[]`; the
fixture contract's fingerprint is
`sha256:8aee983c110573e96d77d795bbe4bde2c01a0fa99d19697a663b488e4a3409ee` and
two consecutive emits are byte-identical.

## The seven done-test forms

| command | exit | why |
|---------|------|-----|
| `--emit capabilities/harnesses/*.yaml` | 0 | the real estate derives clean — 66 contracts, all fields populated |
| `--emit fixtures…/harness_valid.yaml` | 0 | a valid fixture harness builds a contract |
| `--verify contract_valid.json harness_valid.yaml` | 0 | the contract still describes the YAML |
| `--verify contract_missing_port.json …` | 2 | stage `1.2` has no socket — diverged gate ids |
| `--verify contract_dangling_binding.json …` | 2 | an atom bound to port `p::9.9`, which was never declared |
| `--verify contract_wrong_fingerprint.json …` | 2 | the fingerprint does not match the YAML's stage list |
| `--verify contract_edge_to_nowhere.json …` | 2 | an edge runs to stage `7.7`, which the YAML does not contain |

Each plant trips exactly one clause (`STAGE_NO_PORT`, `DANGLING_BINDING`,
`FINGERPRINT_MISMATCH`, `EDGE_TO_NONEXISTENT_STAGE`) — verified by parsing the
`RED [CODE]` lines — so a future edit that blunts any clause turns a green
red on the specific thing it was written to catch. Missing input is exit 1:
a refusal to judge, never a verdict.

Provenance: video `5S9NemR7Fwo`; arXiv:2608.13951; OSS `HKUDS/HELIX`.
