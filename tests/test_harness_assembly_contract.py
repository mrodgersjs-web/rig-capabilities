"""The harness assembly contract: emit determinism and the four RED clauses.

`harness-assembly-contract` turns each canonical harness YAML into
ports/bindings/swap_points/fingerprint/edges so two harness variants can be
diffed mechanically. The load-bearing behaviour is the verify direction: the
verifier recomputes the canonical stage list and the fingerprint from the YAML
and must go exit 2 on a stage with no declared port, a binding referencing an
undeclared port, a fingerprint that does not match the YAML content, or an edge
to a nonexistent stage. Each planted fixture trips exactly ONE clause — if a
fixture ever names two codes, the plants have stopped isolating their defects.

These tests are the permanent regression harness for that contract. The estate
emit (all canonical harness YAMLs, currently 66 files) must stay green: a
harness shape the derivation cannot read has to fail here, not silently vanish
from a future diff.
"""
from __future__ import annotations

import hashlib
import json
import subprocess
import sys
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
SCRIPT = "scripts/harness_assembly_contract.py"
FIX = "examples/fixtures/harness-assembly-contract"


def _run(*args: str) -> subprocess.CompletedProcess:
    return subprocess.run([sys.executable, SCRIPT, *args],
                          cwd=REPO_ROOT, capture_output=True, text=True,
                          timeout=120)


def _codes(proc: subprocess.CompletedProcess) -> set:
    return {line.split("[", 1)[1].split("]", 1)[0]
            for line in proc.stdout.splitlines() if line.startswith("RED [")}


class EmitTests(unittest.TestCase):
    def test_estate_emits_clean(self):
        harnesses = sorted(str(p.relative_to(REPO_ROOT))
                           for p in (REPO_ROOT / "capabilities" / "harnesses")
                           .glob("*.yaml"))
        self.assertGreater(len(harnesses), 60,
                           "the estate shrank below the emitted baseline")
        proc = _run("--emit", *harnesses)
        self.assertEqual(proc.returncode, 0, proc.stdout[-400:])
        doc = json.loads(proc.stdout)
        self.assertEqual(doc["n_contracts"], len(harnesses))
        for c in doc["contracts"]:
            for field in ("ports", "bindings", "fingerprint", "edges"):
                self.assertTrue(c[field],
                                f"{c['source']}: {field} is empty — the "
                                "matrix done-test requires all populated")
            self.assertEqual(c["fingerprint"],
                             "sha256:" + hashlib.sha256(
                                 "\n".join(c["stages"]).encode()).hexdigest(),
                             f"{c['source']}: fingerprint is not the sha256 "
                             "of the canonical stage list as declared")

    def test_emit_is_deterministic(self):
        a, b = _run("--emit", f"{FIX}/harness_valid.yaml"), \
               _run("--emit", f"{FIX}/harness_valid.yaml")
        self.assertEqual(a.returncode, 0, a.stdout)
        self.assertEqual(a.stdout, b.stdout, "two emits of the same bytes "
                                             "diverged — the contract is not "
                                             "diffable")

    def test_fixture_contract_derives_the_real_edges(self):
        proc = _run("--emit", f"{FIX}/harness_valid.yaml")
        self.assertEqual(proc.returncode, 0, proc.stdout[-400:])
        c = json.loads(proc.stdout)["contracts"][0]
        self.assertEqual(c["stages"], ["0.1", "1.1", "1.2", "2.1", "3.1"],
                         "the canonical stage list lost document order")
        self.assertTrue(any(e["from_stage"] == "1.2"
                            and e["to_stage"] == "3.1"
                            and e["artifact"] == ".rig/asm/findings.json"
                            for e in c["edges"]),
                        "the consume edge that proves gate 3.1 consumes an "
                        "upstream-produced artifact is missing")
        self.assertTrue(any(p["port"] == "p::2.1" and p["kind"] == "permission"
                            for p in c["ports"]),
                        "the stop-tier gate did not become a permission port")

    def test_missing_file_is_a_refusal_not_a_verdict(self):
        proc = _run("--emit", "does-not-exist-2031.yaml")
        self.assertEqual(proc.returncode, 1, proc.stdout)
        self.assertIn("REFUSE", proc.stdout)


class VerifyTests(unittest.TestCase):
    def _verify(self, contract: str, harness: str = f"{FIX}/harness_valid.yaml"):
        return _run("--verify", contract, harness)

    def test_valid_contract_verifies(self):
        proc = self._verify(f"{FIX}/contract_valid.json")
        self.assertEqual(proc.returncode, 0, proc.stdout[-400:])
        self.assertIn("GREEN", proc.stdout)

    def test_each_plant_trips_exactly_its_own_clause(self):
        plants = {
            "contract_missing_port.json": "STAGE_NO_PORT",
            "contract_dangling_binding.json": "DANGLING_BINDING",
            "contract_wrong_fingerprint.json": "FINGERPRINT_MISMATCH",
            "contract_edge_to_nowhere.json": "EDGE_TO_NONEXISTENT_STAGE",
        }
        for fixture, code in plants.items():
            proc = self._verify(f"{FIX}/{fixture}")
            self.assertEqual(proc.returncode, 2,
                             f"{fixture}: gate went blind — rc={proc.returncode}")
            self.assertEqual(_codes(proc), {code},
                             f"{fixture}: tripped {_codes(proc)}, expected "
                             f"only {code}")

    def test_valid_contract_against_the_wrong_harness_reds(self):
        """The verifier judges the YAML it is handed, not the contract's own
        claims: a contract for the fixture must not verify a gap harness."""
        proc = self._verify(f"{FIX}/contract_valid.json",
                            "capabilities/harnesses/"
                            "gap-wild_card-agent-engineering.yaml")
        self.assertEqual(proc.returncode, 2, proc.stdout[-400:])
        self.assertIn("FINGERPRINT_MISMATCH", _codes(proc))

    def test_missing_inputs_are_refusals(self):
        for args in ((f"{FIX}/nope.json", f"{FIX}/harness_valid.yaml"),
                     (f"{FIX}/contract_valid.json", f"{FIX}/nope.yaml")):
            proc = _run("--verify", *args)
            self.assertEqual(proc.returncode, 1, proc.stdout)


if __name__ == "__main__":
    unittest.main()
