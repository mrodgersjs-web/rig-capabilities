# What good looks like: declared topology, edge-checked dispatch

Source asset: `capabilities/loops/adversarial-agent-orchestration.md`
Adjudicator: `rig_capabilities/topology.py` (stdlib, pure, never writes)
Attribution: Discover AI videos `lNlMXsUQggc`, `Z90xlttVx3Y`; arXiv 2608.21156,
arXiv 2608.27969. Every output below is a real run in this repo, not a sketch.

The failure this asset exists to make impossible: a loop whose team is described
in prose. The orchestrator "sends findings to the merger" because that is what
the prose said last sprint, and the payload carried a key nobody declared. The
loop runs, the numbers move, and nobody can say which hop was supposed to check
what. A graph that is *declared* can be validated before a single agent is
invoked; a graph that is *implied* can only fail at run time.

## 1. The graph is in the file, machine-readable

```rig-topology
{"topology": "orchestrator", "root": "orchestrator", "agent_count": 6,
 "agents": [{"id": "orchestrator", "family": "harness", ...},
            {"id": "primary", "family": "claude", "input_contract": ["brief"],
             "output_contract": ["artifact"]},
            {"id": "adversarial-1", "family": "codex", "input_contract": ["artifact"],
             "output_contract": ["findings"]}, ...],
 "edges": [{"from": "orchestrator", "to": "primary", "payload": "brief",
            "kind": "dispatch"}, ...]}
```

Two edge kinds. `dispatch` opens an obligation and can deadlock; `deliver`
closes one. Only `dispatch` edges are checked for cycles, because a node waiting
on its own descendant is the real bug and a delivery returning up the tree is not.

## 2. Validation is a command with an exit code

```
$ python3 rig_capabilities/topology.py validate capabilities/loops/adversarial-agent-orchestration.md
OK capabilities/loops/adversarial-agent-orchestration.md (1 declared graph(s), acyclic on dispatch)
```

Exit 0. Any verdict prints and exits 1. `validate` writes nothing.

## 3. A legal hop, a refusal, and the refusal that matters

```
$ python3 rig_capabilities/topology.py dispatch <file> orchestrator primary brief
LEGAL orchestrator -> primary : brief                                    rc=0

$ python3 rig_capabilities/topology.py dispatch <file> adversarial-1 adversarial-2 findings
refuse undefined_edge:adversarial-1->adversarial-2                       rc=1
```

The second line is the point of the whole asset. Two reviewers exchanging
findings before the merger tiers them is the socially plausible thing to do and
the structurally wrong thing: they converge on one prior, and the ensemble's
diversity was the only reason there were two. No edge is declared between them,
so the hop cannot be *forgotten* into existence. Refusal is `exit 1` with a
named verdict — the loop never silently re-routes, drops the hop, or reorders.

The payload is a **label** from the edge, not a blob. `orchestrator primary
findings` refuses, because `findings` is not in the orchestrator's output
contract for that edge: `contract_mismatch:...:not_in_output`.

## 4. The guards go RED

```
$ python3 rig_capabilities/topology.py validate <file> --mutate cycle --expect cycle_at
duplicate_edge:human->orchestrator:verdict
cycle_at:orchestrator,human                                              rc=0
```

`--mutate` injects a defect into an in-memory copy; `--expect` asserts the named
verdict class fires, and exit 0 means *the guard fired*. Emptying the mutation
table is not allowed to read as a pass — `tests/test_topology.py` pins the
counts, so a gutted table fails (36 tests, one per verdict class, plus the
loop's own graph, purity, and the CLI exit codes).

Verdict vocabulary: `undefined_edge`, `contract_mismatch`
(`not_in_output` / `not_in_input` / `payload_missing`), `cycle_at:<nodes>`,
`duplicate_edge`, `unreachable_agent`. `unreachable_agent` is what makes a
reviewer who is declared but never addressed a build failure rather than a
meeting.

## 5. What is *not* claimed

The checker adjudicates the declared graph. It cannot know the graph is the
right graph: a team declared as a star when it should be a pipeline passes
every check here. The loop's `solo-loop baseline` clause exists because of that —
if the team beats the solo run by nothing measurable, the topology is decoration.
Kill switches suppress dispatches; they never invent edges. `REVISE` is round
control, not an edge back into an ancestor.
