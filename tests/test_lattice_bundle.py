"""The RIG Lattice System bundle, as this repo's own gate.

Five claims, each one a thing a reader would otherwise have to trust:

1. The payload's 403 ported tests pass — run as a subprocess, exit 0.
2. The three skills, the command, the agent and the harness are all in the
   catalog as canonical assets.
3. The register still validates with the three new rows in it.
4. mh-07 compiles and the compiled GoalSpec carries all six gate ids G1..G6.
5. The installed-facing CLI reports the lattice truth (588/84/28/40).
"""
from __future__ import annotations

import json
import re
import subprocess
import sys
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from rig_capabilities.catalog import Repo  # noqa: E402

SKILL = REPO_ROOT / "capabilities" / "skills" / "rig-lattice-system"
CLI = SKILL / "bin" / "rig-lattice"
HARNESS = (
    REPO_ROOT / "capabilities" / "harnesses"
    / "mh-07-lattice-application-session.yaml"
)


def _cli(*args: str, timeout: int = 120) -> dict:
    proc = subprocess.run(
        [str(CLI), *args, "--json"],
        capture_output=True, text=True, cwd=str(REPO_ROOT), timeout=timeout,
    )
    if proc.returncode != 0:
        raise AssertionError(f"{args} exited {proc.returncode}: {proc.stderr}")
    return json.loads(proc.stdout)


class TestPayloadSuite(unittest.TestCase):
    """The payload's own suite is this repo's gate on the vendored code.

    The suite takes minutes, so it runs once for the class and both claims
    read the same result.
    """

    @classmethod
    def setUpClass(cls):
        cls.proc = subprocess.run(
            [sys.executable, str(SKILL / "tests" / "run_all.py")],
            capture_output=True, text=True, cwd=str(REPO_ROOT), timeout=1800,
        )

    def test_run_all_exits_zero(self):
        self.assertEqual(
            self.proc.returncode, 0,
            self.proc.stdout[-4000:] + self.proc.stderr[-4000:],
        )
        self.assertRegex(self.proc.stdout, r"RESULT: (\d+)/\1 passed")

    def test_suite_is_not_trivially_small(self):
        """A green suite of three tests would prove nothing."""
        match = re.search(r"RESULT: (\d+)/(\d+) passed", self.proc.stdout)
        self.assertIsNotNone(match, self.proc.stdout[-2000:])
        passed, total = int(match.group(1)), int(match.group(2))
        self.assertEqual(passed, total)
        self.assertGreaterEqual(total, 300, f"only {total} tests collected")


class TestCatalogRegistration(unittest.TestCase):
    # Directory kinds are addressed by bare name; single-file kinds keep the
    # extension in their id, which is how catalog.Repo.scan() reports them.
    EXPECTED = {
        "skill": ("rig-lattice-system", "rig-deviation-engines",
                   "rig-idea-generator"),
        "command": ("rig-lattice-system.md",),
        "agent": ("rig-lattice-router.md",),
        "harness": ("mh-07-lattice-application-session.yaml",),
    }

    @classmethod
    def setUpClass(cls):
        cls.assets = Repo(REPO_ROOT).scan()
        cls.by_kind: dict[str, dict[str, dict]] = {}
        for asset in cls.assets:
            cls.by_kind.setdefault(asset["kind"], {})[asset["id"]] = asset

    def test_all_six_assets_present_and_canonical(self):
        for kind, ids in self.EXPECTED.items():
            for asset_id in ids:
                with self.subTest(kind=kind, id=asset_id):
                    found = self.by_kind.get(kind, {}).get(asset_id)
                    self.assertIsNotNone(
                        found, f"{kind} {asset_id} not in catalog scan"
                    )
                    self.assertEqual(found["source"], "canonical")

    def test_every_asset_carries_the_quality_contract(self):
        """outcome / done_when / quality_floor, as the indexer parsed them."""
        for kind, ids in self.EXPECTED.items():
            for asset_id in ids:
                with self.subTest(kind=kind, id=asset_id):
                    quality = self.by_kind[kind][asset_id]["quality"]
                    outcome = quality.get("outcome") or ""
                    # A YAML block scalar the indexer cannot fold comes back as
                    # the literal ">-" — an outcome that says nothing.
                    self.assertNotIn(outcome.strip(), (">-", "|", ">", "|-"))
                    self.assertGreater(len(outcome), 40, f"thin outcome: {outcome!r}")
                    self.assertTrue(quality.get("done_when"), "done_when missing")
                    self.assertIsNotNone(
                        quality.get("quality_floor"), "quality_floor missing"
                    )

    # Harness assets carry `outcome` but no `description` — mh-02 indexes an
    # empty description too, so this claim applies to the kinds that have one.
    DESCRIBED_KINDS = ("skill", "command", "agent")

    def test_descriptions_are_indexed_not_placeholders(self):
        for kind in self.DESCRIBED_KINDS:
            for asset_id in self.EXPECTED[kind]:
                with self.subTest(kind=kind, id=asset_id):
                    description = self.by_kind[kind][asset_id]["description"]
                    self.assertNotIn(description.strip(), (">-", "|", ">", "|-"))
                    self.assertGreater(len(description), 40, description)

    def test_payload_directory_is_the_skill_asset(self):
        asset = self.by_kind["skill"]["rig-lattice-system"]
        self.assertTrue(
            asset["path"].endswith("capabilities/skills/rig-lattice-system"),
            asset["path"],
        )


class TestRegister(unittest.TestCase):
    def test_register_validates_with_the_new_rows(self):
        from rig_capabilities import register

        # gate_register returns (ok, detail) and never raises.
        ok, detail = register.gate_register(Repo(REPO_ROOT))
        self.assertTrue(ok, detail)

    def test_three_new_ids_present(self):
        import csv

        rows = list(csv.DictReader(
            (REPO_ROOT / "capability_register.csv").read_text().splitlines()
        ))
        ids = {r["id"] for r in rows}
        for expected in ("rig_lattice_system", "rig_deviation_engines_40",
                          "rig_idea_generator"):
            self.assertIn(expected, ids)

    def test_evidence_paths_resolve(self):
        import csv

        rows = list(csv.DictReader(
            (REPO_ROOT / "capability_register.csv").read_text().splitlines()
        ))
        for row in rows:
            if not row["id"].startswith(("rig_lattice", "rig_deviation",
                                          "rig_idea")):
                continue
            for rel in json.loads(row["evidence_paths"]):
                with self.subTest(id=row["id"], path=rel):
                    self.assertTrue((REPO_ROOT / rel).exists(), rel)


class TestHarnessCompiles(unittest.TestCase):
    GATE_TOKENS = ("G1", "G2", "G3", "G4", "G5", "G6")

    @classmethod
    def setUpClass(cls):
        proc = subprocess.run(
            [sys.executable, "scripts/compile_harnesses.py", "parse",
             str(HARNESS.relative_to(REPO_ROOT))],
            capture_output=True, text=True, cwd=str(REPO_ROOT), timeout=180,
        )
        if proc.returncode != 0:
            raise AssertionError(f"parse failed: {proc.stderr[-2000:]}")
        cls.spec = json.loads(proc.stdout)

    def test_envelope_complete(self):
        for key in ("harness_id", "harness_name", "session_type",
                     "coordinate_space", "harness_tuple", "bms_bias"):
            self.assertIn(key, self.spec, f"{key} missing from the GoalSpec")

    def test_coordinate_space_is_the_full_lattice(self):
        space = self.spec["coordinate_space"]
        self.assertEqual(len(space["levels"]), 7)
        self.assertEqual(len(space["diamonds"]), 3)
        self.assertEqual(len(space["bms_modes"]), 4)
        self.assertEqual(len(space["iqrsqpi_steps"]), 7)

    def test_five_canonical_sections_present(self):
        for section in ("identity_lock", "capability_gates",
                         "definition_of_done", "failure_protocol",
                         "self_improvement"):
            self.assertIn(section, self.spec)

    def test_all_six_named_gates_carried(self):
        requirements = " ".join(
            gate["requirement"]
            for category in self.spec["capability_gates"]
            for gate in category["gates"]
        )
        for token in self.GATE_TOKENS:
            with self.subTest(gate=token):
                self.assertRegex(requirements, rf"\b{token}\b")

    def test_every_gate_has_an_executable_proof(self):
        command_shaped = re.compile(
            r"(python3|bash|git|grep|ls|exit|sha256|shasum|diff|env|test)"
        )
        for category in self.spec["capability_gates"]:
            for gate in category["gates"]:
                with self.subTest(gate=gate["id"]):
                    proof = gate.get("command") or gate.get("proof") or ""
                    self.assertTrue(proof, f"gate {gate['id']} has no proof")
                    self.assertRegex(proof, command_shaped)

    def test_failure_tiers_partition_the_gates(self):
        declared = {
            gate["id"]
            for category in self.spec["capability_gates"]
            for gate in category["gates"]
        }
        protocol = self.spec["failure_protocol"]
        listed = set(protocol.get("halt_gates", []))
        listed |= set(protocol.get("degrade_gates", []))
        listed |= set(protocol.get("stop_gates", []))
        self.assertEqual(declared, listed, declared ^ listed)

    def test_a1_first_is_load_bearing_text(self):
        body = HARNESS.read_text()
        self.assertIn("A1-first", body)
        self.assertRegex(body, r"L\[1-7\]-D\[1-3\]-A\[1-4\]")


class TestCompiledGoalSpec(unittest.TestCase):
    """The compiled artifact, not just the parsed source.

    `compile` emits {goals: [{id, gates: [...]}]} — a different shape from
    `parse`, and the shape the goal engine actually loads. The six named gates
    G1..G6 must survive compilation with an executable command attached.
    """

    COMPILED = (
        REPO_ROOT / "out" / "harness-goalspecs"
        / "mh-07-lattice-application-session.json"
    )

    @classmethod
    def setUpClass(cls):
        proc = subprocess.run(
            [sys.executable, "scripts/compile_harnesses.py", "compile"],
            capture_output=True, text=True, cwd=str(REPO_ROOT), timeout=300,
        )
        if proc.returncode != 0:
            raise AssertionError(f"compile failed: {proc.stderr[-2000:]}")
        cls.goal = json.loads(cls.COMPILED.read_text())["goals"][0]
        cls.gates = cls.goal["gates"]

    def test_goal_id_derived_from_harness_id(self):
        self.assertEqual(
            self.goal["id"], "GL-MH-07-LATTICE-APPLICATION-SESSION"
        )

    def test_all_22_gates_compiled(self):
        ids = [g["id"] for g in self.gates]
        self.assertEqual(len(ids), 22)
        self.assertEqual(len(set(ids)), 22)
        # 5 identity-lock gates + 17 capability gates
        self.assertEqual(sum(1 for i in ids if i.startswith("0.")), 5)

    def test_every_compiled_gate_carries_a_command(self):
        without = [g["id"] for g in self.gates if not g.get("command")]
        self.assertEqual(without, [], f"gates without a command: {without}")

    def test_six_named_gates_survive_compilation(self):
        """G1..G6 each resolve to exactly one compiled gate id."""
        for n in range(1, 7):
            token = f"G{n}"
            with self.subTest(gate=token):
                matched = [
                    g["id"] for g in self.gates
                    if re.search(rf"\b{token}\b", g.get("description") or "")
                ]
                self.assertEqual(
                    len(matched), 1,
                    f"{token} matched {matched}, expected exactly one gate",
                )

    def test_named_gate_mapping_is_the_expected_one(self):
        expected = {
            "G1": "1.1",   # coordinate before code
            "G2": "2.1",   # A1-first
            "G3": "2.4",   # refactor budget
            "G4": "3.1",   # engine verdict
            "G5": "4.1",   # planted failure
            "G6": "4.3",   # sealed proof
        }
        for token, gate_id in expected.items():
            with self.subTest(gate=token):
                matched = [
                    g["id"] for g in self.gates
                    if re.search(rf"\b{token}\b", g.get("description") or "")
                ]
                self.assertEqual(matched, [gate_id])


class TestCliTruth(unittest.TestCase):
    def test_lattice_summary(self):
        data = _cli("lattice", "summary")
        self.assertEqual(data["cells"], 588)
        self.assertEqual(data["primary"], 84)
        self.assertEqual(data["archetypes"], 28)
        self.assertEqual(data["levels"], 7)
        self.assertEqual(data["diamonds"], 3)
        self.assertEqual(data["bms_modes"], 4)
        self.assertEqual(data["steps"], 7)
        self.assertEqual(data["version"], "3.0")

    def test_engines_roster(self):
        engines = _cli("engines")
        self.assertEqual(len(engines), 40)
        layers: dict[str, int] = {}
        for engine in engines:
            layers[engine["layer"]] = layers.get(engine["layer"], 0) + 1
        self.assertEqual(layers, {"cognitive": 20, "nature": 10, "physics": 10})
        self.assertTrue(
            all(e["is_gate"] for e in engines if e["layer"] == "physics")
        )

    def test_doctor_is_ok(self):
        self.assertTrue(_cli("doctor")["ok"])

    def test_dialects_resolve_to_one_cell(self):
        canonical = _cli("lattice", "cell", "L1-D1-A1-I1")
        bare = _cli("lattice", "cell", "L1-1-A1-I1")
        self.assertEqual(canonical["cell_id"], "L1-D1-A1-I1")
        self.assertEqual(bare["cell_id"], "L1-D1-A1-I1")
        self.assertEqual(canonical["archetype"], "A1.1")
        self.assertEqual(canonical["fallback_archetype"], "A3.A1.1")
        self.assertTrue(canonical["deterministic"])
        self.assertFalse(canonical["model_in_decision_path"])
        self.assertEqual(canonical["cost_band"], "$0.001")

    def test_out_of_range_cell_exits_nonzero(self):
        proc = subprocess.run(
            [str(CLI), "lattice", "cell", "L8-D1-A1-I1"],
            capture_output=True, text=True, cwd=str(REPO_ROOT), timeout=60,
        )
        self.assertNotEqual(proc.returncode, 0)
        for shape in ("canonical", "bare-digit", "dotted"):
            self.assertIn(shape, proc.stderr)

    def test_bms_altitude_changes_the_band(self):
        # Fail-closed (s9, 62c50fb): bms score takes no defaults; every receipt
        # must be stated. Values match the repo convention elsewhere; only
        # --level varies so the confidence delta is attributable to altitude.
        low = _cli("bms", "score", "--failure-cost", "0.9", "--reversibility",
                    "0.8", "--mechanism-clarity", "0.9",
                    "--past-failure-rate", "0.0", "--data-volume", "0.5",
                    "--level", "L1")
        high = _cli("bms", "score", "--failure-cost", "0.9", "--reversibility",
                     "0.8", "--mechanism-clarity", "0.9",
                     "--past-failure-rate", "0.0", "--data-volume", "0.5",
                     "--level", "L7")
        self.assertEqual(low["mode"], "A1")
        self.assertTrue(low["deterministic"])
        self.assertFalse(low["approval_required"])
        self.assertGreater(low["confidence"], high["confidence"])
        # The altitude term spans exactly 0.70 between L1 (+0.35) and L7 (-0.35)
        self.assertAlmostEqual(
            low["adjustments"]["altitude"] - high["adjustments"]["altitude"],
            0.70, places=6,
        )

    def test_idea_gates_discriminate(self):
        generic = _cli(
            "idea", "score",
            "--title", "AI-powered synergy platform",
            "--content",
            "Our best-in-class end-to-end solution leverages cutting-edge AI "
            "to unlock growth and revolutionize your business with seamless "
            "world-class results.",
            "--claims", "3",
        )
        self.assertEqual(generic["verdict"], "reject")
        self.assertTrue(
            {"generic_usefulness", "anti_randomness"}
            & set(generic["failed_gates"]),
            generic["failed_gates"],
        )

    def test_idea_scoring_is_reproducible(self):
        args = ("idea", "score", "--title", "t", "--content", "c")
        self.assertEqual(_cli(*args), _cli(*args))


if __name__ == "__main__":
    unittest.main()
