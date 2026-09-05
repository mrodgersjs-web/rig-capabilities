---
name: harness-assembly-contract
description: >-
  Emit, per canonical harness YAML, the assembly contract — ports[] (each
  stage's required behaviour declared as a socket, not an implementation),
  bindings[] (which named atom fills it), swap_points[] (interfaces where one
  compatible atom may replace another), fingerprint (sha256 over the canonical
  stage list), edges[] (flow plus consume/produce, each with data kind and
  hook-chain order) — and verify the contract against the YAML. RED exit 2 on
  a stage with no declared port, a binding referencing an undeclared port, a
  fingerprint that does not match the YAML content, or an edge to a
  nonexistent stage. Deterministic: same bytes in, same bytes out.
argument-hint: "--emit <harness.yaml ...> | --verify <contract.json> <harness.yaml>"
allowed-tools: Read, Bash
category: meta
outcome: "meta: harness variants become mechanically diffable contracts with permission policy as a named, attributable port — gate dependency stops being implied and a denial names the policy that produced it"
done_when:
  - cmd:python3 scripts/harness_assembly_contract.py --emit capabilities/harnesses/*.yaml > /dev/null; test $? -eq 0
  - cmd:python3 scripts/harness_assembly_contract.py --emit examples/fixtures/harness-assembly-contract/harness_valid.yaml > /dev/null; test $? -eq 0
  - cmd:python3 scripts/harness_assembly_contract.py --verify examples/fixtures/harness-assembly-contract/contract_valid.json examples/fixtures/harness-assembly-contract/harness_valid.yaml; test $? -eq 0
  - cmd:python3 scripts/harness_assembly_contract.py --verify examples/fixtures/harness-assembly-contract/contract_missing_port.json examples/fixtures/harness-assembly-contract/harness_valid.yaml; rc=$?; test $rc -eq 2
  - cmd:python3 scripts/harness_assembly_contract.py --verify examples/fixtures/harness-assembly-contract/contract_dangling_binding.json examples/fixtures/harness-assembly-contract/harness_valid.yaml; rc=$?; test $rc -eq 2
  - cmd:python3 scripts/harness_assembly_contract.py --verify examples/fixtures/harness-assembly-contract/contract_wrong_fingerprint.json examples/fixtures/harness-assembly-contract/harness_valid.yaml; rc=$?; test $rc -eq 2
  - cmd:python3 scripts/harness_assembly_contract.py --verify examples/fixtures/harness-assembly-contract/contract_edge_to_nowhere.json examples/fixtures/harness-assembly-contract/harness_valid.yaml; rc=$?; test $rc -eq 2
  - file:scripts/harness_assembly_contract.py
  - grep:capabilities/commands/harness-assembly-contract.md:Never edit the fingerprint to close a mismatch
great_example: examples/great/agent-engineering/harness-assembly-contract.md
acl: public
quality_floor: 0.7
---

# harness-assembly-contract

THE LAW: **a harness is a set of sockets with bound atoms, not an ordered pile
of gate ids.** If the required behaviour of a stage is not declared as a port,
no atom can be bound to it, swapped in it, or diffed against a variant — the
dependency is implied, and implied dependencies are invisible to every
mechanical check until the day the order breaks.

Run the emitter over the estate:

```bash
python3 scripts/harness_assembly_contract.py --emit capabilities/harnesses/*.yaml
```

Exit 0, one contract per file, all five fields populated for all 66 canonical
harnesses. The emission is deterministic: contracts sort by source path, ports
and bindings sort by port id, edges sort by (hook_order, from, to, data_kind,
artifact), the stage list is document order, and the fingerprint — `sha256:`
over the stage list joined by newlines — anchors it. Two variants of the same
harness are diffed by sorting the two emissions and reading the fingerprint
drift; no prose comparison participates.

## The contract

| field | what it is |
|-------|------------|
| `stages[]` | the canonical stage list: every declared gate in document order, across all five shapes the estate writes (identity_lock.gates, identity_gates, grouped/flat capability_gates, top-level gates) |
| `ports[]` | one socket per stage declaring the required behaviour (`requires`) as an interface `(kind, data_kind, failure_tier)`; artifacts the stage's proof writes are `produces`, paths its requirement/proof cite from upstream are `consumes` |
| `bindings[]` | which named atom fills the port — `harness_id::stage` — with its YAML locator (`via`) and whether the port sits on a swap interface |
| `swap_points[]` | every interface carrying ≥2 ports: the places one compatible atom may replace another without touching the contract |
| `fingerprint` | sha256 of the canonical stage list — the stable identity of the gate set |
| `edges[]` | the flow graph: `sequence` edges between consecutive stages plus `artifact` consume/produce edges, each carrying data kind and hook-chain order |

A gate whose tier is `stop` gets a port of `kind: permission`. That is the
mechanism's consequence: permission policy is a named port whose bound atom is
on the contract record, so a denial is attributable to the policy that
produced it — not just logged as an approval event. The estate's tool-boundary
guards (`guard-dangerous-commands.sh`, `guard-secret-write.sh`) hard-wire this
at the tool boundary; here the policy is visible in the diffable contract.

The RIG delta: `mh-02-harness-forge-session.yaml` hand-forges whole YAMLs with
no port/atom interface and no fingerprint, so two variants cannot be diffed
mechanically; the 66 YAMLs declare ordered gate ids and `iqrsqpi_steps` but no
consume/produce edges, leaving gate-order dependency implied across every file
(mechanism derived from arXiv:2608.13951; video 5S9NemR7Fwo; OSS
`HKUDS/HELIX`).

## Verify: the four clauses that go RED

```bash
python3 scripts/harness_assembly_contract.py --verify CONTRACT.json HARNESS.yaml
```

The verifier recomputes the stage list and the fingerprint from the YAML and
holds the contract against it. Exit 2, naming every violation, when:

1. **STAGE_NO_PORT** — a stage in the YAML has no declared port (the contract
   and YAML gate ids have diverged); an ORPHAN_PORT, a port naming a stage the
   YAML does not contain, is the same divergence seen from the other side.
2. **DANGLING_BINDING** — a binding references an undeclared port: an atom is
   bound to a socket that does not exist.
3. **FINGERPRINT_MISMATCH** — the contract fingerprint does not equal the
   sha256 recomputed from the YAML's stage list. Never edit the fingerprint to
   close a mismatch; fix the stage list it describes.
4. **EDGE_TO_NONEXISTENT_STAGE** — an edge endpoint names a stage the YAML
   does not contain: the flow graph claims a dependency on nothing.

A harness declaring no stages at all is `NO_STAGES` (exit 2 — there is no flow
graph to contract), a duplicated stage id is `DUPLICATE_STAGE` (edge endpoints
must resolve to one socket), and unreadable/unparsable input is exit 1: a
refusal to judge, never conflated with a verdict.

## Procedure

1. `--emit` the YAMLs you touched; quote the fingerprint from the emission in
   the change note — it is what the next variant diffs against.
2. Keep the emitted contract for a harness beside its fixture estate and
   `--verify` it after any YAML edit; a green emit proves the derivation, a
   green verify proves the contract still describes the YAML.
3. The five fixtures under `examples/fixtures/harness-assembly-contract/` are
   the permanent regression set: `harness_valid.yaml` and
   `contract_valid.json` at exit 0, and one plant per clause
   (`contract_missing_port.json`, `contract_dangling_binding.json`,
   `contract_wrong_fingerprint.json`, `contract_edge_to_nowhere.json`) at exit
   2 — each plant trips exactly one clause, so a future edit that stops a
   clause biting turns a green red immediately.
4. To forge a harness variant, emit both contracts and diff the sorted JSON:
   the port set is the interface diff, the binding diff names the atoms that
   moved, and the fingerprint tells you whether the stage list itself changed.

No LLM participates in the emit or the verify. If deciding a port needs
judgment, the harness YAML is wrong.
