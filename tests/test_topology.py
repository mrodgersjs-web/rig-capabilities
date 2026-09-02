"""Declared-topology edge-check tests.

Three claims, none of which need a model or the network:

1. Every verdict class — undefined_edge, contract_mismatch, cycle_at, and the
   structural/reachability verdicts — fires on a graph that deserves it, and
   a legal declared graph validates to [].
2. `validate` is pure: same input object, unchanged, before and after.
3. The graph the adversarial-agent-orchestration loop actually DECLARES is
   legal, and each plant-failure mutation on it produces its named verdict —
   so the loop file's own done_when checks cannot be satisfied by a graph that
   only looks declared.

If cycle detection is broken (plant-failure), the cycle tests, the CLI
--expect cycle_at test, and the loop's `validate` check all go RED together.
"""
from __future__ import annotations

import contextlib
import copy
import io
import tempfile
import unittest
from pathlib import Path

from rig_capabilities import topology

REPO = Path(__file__).resolve().parent.parent
DOC = REPO / "capabilities/loops/adversarial-agent-orchestration.md"


def star() -> dict:
    """Orchestrator star: dispatch out, deliver back. The canonical legal shape."""
    return {
        "topology": "orchestrator",
        "root": "orchestrator",
        "agent_count": 3,
        "agents": [
            {"id": "orchestrator", "family": "harness",
             "input_contract": ["artifact", "findings"],
             "output_contract": ["artifact"]},
            {"id": "rev-a", "family": "codex",
             "input_contract": ["artifact"], "output_contract": ["findings"]},
            {"id": "rev-b", "family": "gemini",
             "input_contract": ["artifact"], "output_contract": ["findings"]},
        ],
        "edges": [
            {"from": "orchestrator", "to": "rev-a", "payload": "artifact", "kind": "dispatch"},
            {"from": "rev-a", "to": "orchestrator", "payload": "findings", "kind": "deliver"},
            {"from": "orchestrator", "to": "rev-b", "payload": "artifact", "kind": "dispatch"},
            {"from": "rev-b", "to": "orchestrator", "payload": "findings", "kind": "deliver"},
        ],
    }


def doc_graphs() -> list:
    return topology.extract_graphs(DOC.read_text(encoding="utf-8"))


def run_cli(argv) -> tuple:
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        rc = topology.main(argv)
    return rc, buf.getvalue()


class LegalGraphTests(unittest.TestCase):
    def test_star_validates_clean(self):
        self.assertEqual(topology.validate(star()), [])

    def test_response_edges_are_not_cycles(self):
        # deliver back to the root must not read as a cycle — only dispatch
        # edges open a wait, and a response closes one.
        self.assertFalse(any(v.startswith("cycle_at") for v in topology.validate(star())))

    def test_flat_swarm_without_root_is_legal(self):
        g = {
            "topology": "flat-swarm",
            "agent_count": 2,
            "agents": [
                {"id": "a", "family": "x", "input_contract": ["findings"],
                 "output_contract": ["artifact"]},
                {"id": "b", "family": "y", "input_contract": ["artifact"],
                 "output_contract": ["findings"]},
            ],
            "edges": [
                {"from": "a", "to": "b", "payload": "artifact", "kind": "dispatch"},
                {"from": "b", "to": "a", "payload": "findings", "kind": "deliver"},
            ],
        }
        self.assertEqual(topology.validate(g), [])

    def test_the_loop_declares_a_legal_graph(self):
        graphs = doc_graphs()
        self.assertEqual(len(graphs), 1,
                         "the loop must declare exactly one rig-topology block")
        self.assertEqual(
            topology.validate(graphs[0]), [],
            "the graph the loop file declares must validate clean")


class VerdictClassTests(unittest.TestCase):
    def _prefixes(self, verdicts):
        return [v.split(":")[0] for v in verdicts]

    def test_undefined_edge(self):
        g = star()
        g["edges"].append({"from": "rev-a", "to": "ghost", "payload": "artifact",
                           "kind": "dispatch"})
        self.assertIn("undefined_edge:rev-a->ghost", topology.validate(g))

    def test_contract_mismatch_not_in_input(self):
        g = star()
        g["agents"][1]["input_contract"] = []          # rev-a now accepts nothing
        self.assertIn("contract_mismatch:orchestrator->rev-a:artifact:not_in_input",
                      topology.validate(g))

    def test_contract_mismatch_not_in_output(self):
        g = star()
        g["agents"][0]["output_contract"] = ["brief"]  # orchestrator never promised artifact
        self.assertIn("contract_mismatch:orchestrator->rev-a:artifact:not_in_output",
                      topology.validate(g))

    def test_contract_mismatch_payload_missing(self):
        g = star()
        g["edges"][0].pop("payload")
        self.assertIn("contract_mismatch:orchestrator->rev-a:none:payload_missing",
                      topology.validate(g))

    def test_cycle_at_dispatch(self):
        g = star()
        g["agent_count"] = 4
        g["agents"].append({"id": "rev-c", "family": "kimi",
                            "input_contract": ["findings"],
                            "output_contract": ["findings"]})
        # rev-a -> rev-c -> orchestrator, both dispatch: a real deadlock chain.
        g["edges"].append({"from": "rev-a", "to": "rev-c", "payload": "findings",
                           "kind": "dispatch"})
        g["edges"].append({"from": "rev-c", "to": "orchestrator", "payload": "findings",
                           "kind": "dispatch"})
        verdicts = topology.validate(g)
        cyc = [v for v in verdicts if v.startswith("cycle_at:")]
        self.assertEqual(len(cyc), 1, verdicts)
        nodes = set(cyc[0].split(":", 1)[1].split(","))
        self.assertEqual(nodes, {"orchestrator", "rev-a", "rev-c"})

    def test_self_dispatch_is_a_cycle(self):
        g = star()
        g["edges"].append({"from": "rev-a", "to": "rev-a", "payload": "artifact",
                           "kind": "dispatch"})
        g["agents"][1]["input_contract"].append("artifact")  # contract-wise fine; cycle isn't
        self.assertIn("cycle_at:rev-a", topology.validate(g))

    def test_unreachable_agent(self):
        g = star()
        g["edges"] = [e for e in g["edges"] if not (e["to"] == "rev-b"
                                                    and e["kind"] == "dispatch")]
        self.assertIn("unreachable_agent:rev-b", topology.validate(g))

    def test_declaration_missing_short_circuits(self):
        g = star()
        g.pop("agent_count")
        self.assertEqual(topology.validate(g), ["declaration_missing:agent_count"])

    def test_topology_enum_is_closed(self):
        g = star()
        g["topology"] = "hive-mind"
        self.assertIn("topology_undeclared:hive-mind", topology.validate(g))

    def test_agent_count_is_fixed(self):
        g = star()
        g["agent_count"] = 5
        self.assertIn("agent_count_mismatch:5!=3", topology.validate(g))

    def test_boss_requires_root(self):
        g = star()
        g["topology"] = "boss"
        g.pop("root")
        self.assertIn("root_undeclared:none", topology.validate(g))

    def test_duplicate_agent(self):
        g = star()
        g["agents"].append(dict(g["agents"][2]))  # a second rev-b
        self.assertIn("duplicate_agent:rev-b", topology.validate(g))

    def test_edge_kind_enum_is_closed(self):
        g = star()
        g["edges"][0]["kind"] = "carrier-pigeon"
        self.assertIn("edge_kind_invalid:orchestrator->rev-a:carrier-pigeon",
                      topology.validate(g))

    def test_duplicate_edge(self):
        g = star()
        g["edges"].append(dict(g["edges"][0]))
        self.assertIn("duplicate_edge:orchestrator->rev-a:artifact", topology.validate(g))


class PurityTests(unittest.TestCase):
    def test_validate_never_mutates_its_graph(self):
        g = star()
        g["edges"].append({"from": "rev-a", "to": "ghost", "payload": "x"})
        before = copy.deepcopy(g)
        topology.validate(g)
        self.assertEqual(g, before)

    def test_mutate_returns_a_copy_and_leaves_the_original_clean(self):
        g = doc_graphs()[0]
        before = copy.deepcopy(g)
        m = topology.mutate(g, "cycle")
        self.assertEqual(g, before, "mutate must not touch the caller's graph")
        self.assertEqual(topology.validate(g), [])
        self.assertNotEqual(m, g)


class DispatchTests(unittest.TestCase):
    def test_legal_hop_passes(self):
        self.assertEqual(topology.check_dispatch(star(), "orchestrator", "rev-a", "artifact"), [])

    def test_undeclared_hop_refuses(self):
        v = topology.check_dispatch(star(), "rev-a", "rev-b", "findings")
        self.assertIn("undefined_edge:rev-a->rev-b", v,
                      "reviewers must not talk to each other on any edge")

    def test_contract_violating_hop_refuses(self):
        v = topology.check_dispatch(star(), "orchestrator", "rev-a", "verdict")
        self.assertIn("contract_mismatch:orchestrator->rev-a:verdict:not_in_input", v)


class MutationFixtureTests(unittest.TestCase):
    """Every named defect must produce its named verdict ON THE LOOP'S OWN GRAPH."""

    def check(self, kind: str, prefix: str):
        g = doc_graphs()[0]
        verdicts = topology.validate(topology.mutate(g, kind))
        self.assertTrue(
            any(v.startswith(prefix) for v in verdicts),
            f"mutation {kind!r} produced {verdicts}, none starting {prefix!r}")

    def test_cycle_plant(self):
        self.check("cycle", "cycle_at:")

    def test_ghost_plant(self):
        self.check("ghost", "undefined_edge:")

    def test_contract_plant(self):
        self.check("contract", "contract_mismatch:")

    def test_unreachable_plant(self):
        self.check("unreachable", "unreachable_agent:")


class CliTests(unittest.TestCase):
    def test_validate_declared_graph_exits_zero(self):
        rc, out = run_cli(["validate", str(DOC)])
        self.assertEqual(rc, 0, out)

    def test_planted_defect_without_expect_exits_one(self):
        rc, out = run_cli(["validate", str(DOC), "--mutate", "cycle"])
        self.assertEqual(rc, 1, out)
        self.assertIn("cycle_at:", out)

    def test_planted_defect_with_expect_exits_zero(self):
        for kind, prefix in (("cycle", "cycle_at"), ("ghost", "undefined_edge"),
                             ("contract", "contract_mismatch"),
                             ("unreachable", "unreachable_agent")):
            rc, out = run_cli(["validate", str(DOC), "--mutate", kind, "--expect", prefix])
            self.assertEqual(rc, 0, f"--mutate {kind}: {out}")

    def test_expect_absent_exits_one(self):
        # A graph that validates clean cannot satisfy a planted-failure expect.
        rc, out = run_cli(["validate", str(DOC), "--expect", "cycle_at"])
        self.assertEqual(rc, 1, out)

    def test_dispatch_legal_exits_zero(self):
        g = doc_graphs()[0]
        e = g["edges"][0]
        rc, out = run_cli(["dispatch", str(DOC), e["from"], e["to"], e["payload"]])
        self.assertEqual(rc, 0, out)

    def test_dispatch_undeclared_refuses_with_exit_one(self):
        rc, out = run_cli(["dispatch", str(DOC), "adversarial-1", "adversarial-2", "findings"])
        self.assertEqual(rc, 1, out)
        self.assertIn("undefined_edge:adversarial-1->adversarial-2", out)

    def test_dispatch_refusal_with_expect_exits_zero(self):
        rc, out = run_cli(["dispatch", str(DOC), "adversarial-1", "adversarial-2",
                           "findings", "--expect", "undefined_edge"])
        self.assertEqual(rc, 0, out)

    def test_unparseable_declaration_is_never_green(self):
        with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as f:
            f.write("{ not json")
            path = f.name
        rc, out = run_cli(["validate", path])
        self.assertEqual(rc, 2, out)
        self.assertIn("graph_unparseable", out)
        Path(path).unlink()

    def test_md_without_declaration_is_never_green(self):
        with tempfile.NamedTemporaryFile("w", suffix=".md", delete=False) as f:
            f.write("# some loop\n\nno graph here\n")
            path = f.name
        rc, out = run_cli(["validate", path])
        self.assertEqual(rc, 2, out)
        Path(path).unlink()




if __name__ == "__main__":
    unittest.main()
