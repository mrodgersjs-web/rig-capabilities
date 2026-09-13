"""Plant-failure tests for the build-standard surfaces: context packet, instruction
surfaces, and the durable-build certificate gate. Each test breaks the exact thing
a guard claims to protect and requires the guard to go red."""
import json
import subprocess
import sys
import tempfile
import time
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

from rig_capabilities import context_packet as cp           # noqa: E402
from rig_capabilities import loops as lp                    # noqa: E402
from rig_capabilities import surfaces_render as sr          # noqa: E402
sys.path.insert(0, str(REPO / "tests"))
from test_d85_gates import GateTestBase                                    # noqa: E402
from d85_gates import _canonical_hash, mint_approval, score_realized       # noqa: E402

DIAG = {"goal": "wire the build standard into four runtimes",
        "cell_id": "L4-D2-A1-R",
        "done_test": ["bin/rig-build-standard test"],
        "out_of_scope": ["outward sends"],
        "effort_budget": {"cpu_minutes": 30, "usd": 5, "wallclock_seconds": 1800},
        "evidence_refs": ["file:runs/agentic-stack-buildout/iqrsqpi-intent.md"]}

BUILD_CASES = json.loads((REPO / "capabilities/skills/durable-build/tests/cases.json")
                         .read_text(encoding="utf-8"))


def _packet_body(root: Path) -> dict:
    (root / "src.py").write_text("print(1)\n", encoding="utf-8")
    return {"diagnosis": DIAG, "skills": ["rig-build-standard"], "sources": ["src.py"],
            "gates": [{"id": "d85_certified", "status": "RED"}], "approvals": [],
            "next_action": "bin/rig-build-standard packet --out p.json"}


class PacketTests(unittest.TestCase):
    def test_incomplete_diagnosis_is_refused(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            good = _packet_body(root)
            cp.compile_packet(good, root=root)
            for label, bad in (
                ("empty next action", {**good, "next_action": "  "}),
                ("no bound sources", {**good, "sources": []}),
                ("gate without status", {**good, "gates": [{"id": "d85"}]}),
                ("invented cell", {**good, "diagnosis": {**DIAG, "cell_id": "L9-D9-A9-Z"}}),
                ("dropped budget", {**good, "diagnosis": {k: v for k, v in DIAG.items()
                                                          if k != "effort_budget"}}),
            ):
                with self.subTest(label), self.assertRaises(cp.PacketError):
                    cp.compile_packet(bad, root=root)

    def test_stale_and_tampered_are_different_verdicts(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            packet = cp.compile_packet(_packet_body(root), root=root)
            self.assertEqual(cp.verify(packet, root=root)["status"], "FRESH")
            (root / "src.py").write_text("print(2)\n", encoding="utf-8")
            self.assertEqual(cp.verify(packet, root=root)["status"], "STALE")
            (root / "src.py").write_text("print(1)\n", encoding="utf-8")
            self.assertEqual(cp.verify(packet, root=root)["status"], "FRESH")
            self.assertEqual(cp.verify({**packet, "next_action": "rm -rf /"},
                                       root=root)["status"], "INVALID")

    def test_cli_exit_codes(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            diag = root / "diag.json"
            diag.write_text(json.dumps(DIAG), encoding="utf-8")
            packet = root / "p.json"
            (root / "src.py").write_text("print(1)\n", encoding="utf-8")
            run = lambda *a: subprocess.run(  # noqa: E731
                [sys.executable, str(REPO / "rig_capabilities/context_packet.py"), *a],
                cwd=root, capture_output=True, text=True)
            r = run("compile", "--diagnosis", str(diag), "--root", str(root),
                    "--sources", "src.py", "--skills", "rig-build-standard",
                    "--next-action", "echo hi", "--out", str(packet))
            self.assertEqual((r.returncode, packet.is_file()), (0, True), r.stderr[-300:])
            r = run("verify", "--packet", str(packet), "--root", str(root))
            self.assertEqual(r.returncode, 0, r.stdout[-300:])
            broken = json.loads(packet.read_text())
            broken["packet_sha256"] = "0" * 64
            packet.write_text(json.dumps(broken), encoding="utf-8")
            r = run("verify", "--packet", str(packet), "--root", str(root))
            self.assertEqual(r.returncode, 2, r.stdout[-300:])
            self.assertIn("INVALID", r.stdout)
            diag.write_text(json.dumps({k: v for k, v in DIAG.items() if k != "done_test"}),
                            encoding="utf-8")
            r = run("compile", "--diagnosis", str(diag), "--root", str(root),
                    "--sources", "src.py", "--next-action", "echo hi")
            self.assertEqual(r.returncode, 2, r.stdout[-200:])


class _SurfaceSandbox(GateTestBase):
    """Fake target files plus a sandbox Gate-D store. The authorization is real:
    rows are HMAC-signed by d85_gates against a registered process that genuinely
    scores D85-eligible. Nothing here is an approval this test wrote by hand."""

    def setUp(self):
        GateTestBase.setUp(self)
        self.write_authority(self.classification())
        self._orig = (sr.SURFACES, sr.STAGE_DIR, sr.AUTHORITY, sr.GATE_ROOT,
                      sr.GATE_D_PROCESS)
        surfaces = {name: str(self.root / f"targets/{name}/AGENTS.md") for name in sr.RUNTIMES}
        cfg = self.root / "surfaces.json"
        cfg.write_text(json.dumps({"surfaces": surfaces}), encoding="utf-8")
        sr.SURFACES = cfg
        sr.STAGE_DIR = self.root / "stage"
        sr.AUTHORITY = self.registry_path
        sr.GATE_ROOT = self.gate_root
        sr.GATE_D_PROCESS = "sample"
        self.hand = "# Hand written\n\ndo not clobber me\n"

    def tearDown(self):
        sr.SURFACES, sr.STAGE_DIR, sr.AUTHORITY, sr.GATE_ROOT, sr.GATE_D_PROCESS = self._orig
        GateTestBase.tearDown(self)

    def seed(self, name="omp"):
        path = sr.surfaces()[name]
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(self.hand, encoding="utf-8")
        return path

    def approve(self, name="omp", action=None):
        """Mike's keystroke modelled honestly: mint_approval signs the row."""
        proof = score_realized(self.registry_path, "sample")
        return mint_approval(
            Path(sr.GATE_ROOT), process_id="sample",
            inventory_sha256=proof["inventory_sha256"],
            classification_sha256=proof["classification_sha256"],
            realized_sha256=_canonical_hash(proof),
            action=action or sr.action_for(name), approver="mike",
            lifetime_seconds=900)["run_id"]


class SurfaceStageTests(_SurfaceSandbox):
    def test_stage_never_touches_a_target(self):
        path = self.seed()
        before = path.read_bytes()
        rows = sr.stage()
        self.assertEqual(len(rows), len(sr.RUNTIMES))
        self.assertEqual(path.read_bytes(), before, "stage mutated a target surface")
        for name in sr.RUNTIMES:
            cand = sr.STAGE_DIR / f"{name}.candidate.md"
            self.assertTrue(cand.is_file(), cand)
            self.assertIn(sr.CLOSE, cand.read_text(encoding="utf-8"))
        self.assertIn(self.hand.strip(), (sr.STAGE_DIR / "omp.candidate.md").read_text(),
                      "candidate dropped hand-written content")

    def test_status_reports_the_real_state(self):
        rows = {r["surface"]: r for r in sr.status()}
        self.assertEqual(set(rows), set(sr.RUNTIMES))
        self.assertEqual(rows["omp"]["status"], "MISSING")
        path = self.seed()
        self.assertEqual({r["surface"]: r["status"] for r in sr.status()}["omp"], "UNWIRED")
        path.write_text(sr.splice(self.hand, sr.block()), encoding="utf-8")
        self.assertEqual({r["surface"]: r["status"] for r in sr.status()}["omp"], "WIRED")
        path.write_text(path.read_text().replace(sr.policy_sha(), "0" * 64), encoding="utf-8")
        drift = next(r for r in sr.status() if r["surface"] == "omp")
        self.assertEqual(drift["status"], "DRIFT")
        self.assertIn("policy", drift["detail"])


class SurfaceInstallTests(_SurfaceSandbox):
    def test_install_without_a_signed_approval_leaves_bytes_untouched(self):
        path = self.seed()
        before = path.read_bytes()
        other = {"kind": "wiring:instruction-surface", "surface": "hermes",
                 "policy_sha256": sr.policy_sha()}
        for attempt in (None, "never-issued", self.approve(action=other)):
            with self.assertRaises(sr.SurfaceError) as ctx:
                sr.install("omp", attempt)
            self.assertIn("GATE-D BLOCKED", str(ctx.exception))
            self.assertEqual(path.read_bytes(), before)
        self.assertEqual(list((self.gate_root / "consumed").iterdir()), [],
                         "a refused install consumed a marker")

    def test_a_self_written_approval_row_is_refused(self):
        """Plant the old design's trust model: an unsigned row naming the right
        action, written by the module that would spend it. Must not install."""
        self.seed()
        self.approve(name="hermes")  # mints the store key with one genuinely signed row
        now = int(time.time())
        row = {"run_id": "sha256:" + "a" * 64, "process_id": "sample",
               "action_sha256": "sha256:" + "b" * 64,
               "inventory_sha256": "sha256:" + "c" * 64,
               "classification_sha256": "sha256:" + "d" * 64,
               "realized_sha256": "sha256:" + "e" * 64, "approver": "mike",
               "issued_at": now, "expires_at": now + 900, "signature": "0" * 64}
        self.gate_root.mkdir(parents=True, exist_ok=True)
        with (self.gate_root / "approvals.jsonl").open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(row, sort_keys=True) + "\n")
        with self.assertRaises(sr.SurfaceError) as ctx:
            sr.install("omp", row["run_id"])
        self.assertIn("bad signature", str(ctx.exception))

    def test_install_splices_once_and_consumes_its_approval(self):
        path = self.seed()
        appr = self.approve()
        out = sr.install("omp", appr)
        text = path.read_text(encoding="utf-8")
        self.assertEqual(out["status"], "WIRED")
        self.assertTrue(Path(out["gate_d"]["consumed_marker"]).is_file(),
                        "install did not surface the Gate-D consumption evidence")
        self.assertEqual(text.count(sr.CLOSE), 1, "managed block spliced more than once")
        self.assertIn("do not clobber me", text, "unrelated content lost")
        self.assertEqual({r["surface"]: r["status"] for r in sr.status()}["omp"], "WIRED")
        self.assertTrue(any(p.name.startswith("omp.pre-install-") for p in sr.STAGE_DIR.iterdir()),
                        "no pre-install backup")
        with self.assertRaises(sr.SurfaceError) as ctx:
            sr.install("omp", appr)
        self.assertIn("consumed", str(ctx.exception).lower())
        # drift then repair: the block sha decides, not mere presence. Gate-D binds one
        # consumption per (process, action), so re-approving needs a fresh store — which
        # is exactly a re-approval after a policy change.
        path.write_text(text.replace(sr.policy_sha(), "0" * 64), encoding="utf-8")
        self.assertEqual({r["surface"]: r["status"] for r in sr.status()}["omp"], "DRIFT")
        sr.GATE_ROOT = self.root / "gate_d_2"
        self.assertEqual(sr.install("omp", self.approve())["status"], "WIRED")
        self.assertEqual({r["surface"]: r["status"] for r in sr.status()}["omp"], "WIRED")

    def test_receipts_never_claim_loaded_or_enforced(self):
        self.seed()
        for row in sr.receipts():
            for state in ("loaded", "exercised", "enforced"):
                self.assertEqual(row[state], "UNVERIFIED", f"{row['surface']} invented {state}")
            self.assertNotEqual(row["surface_wired"], "UNKNOWN")
            self.assertNotEqual(row["status"], "READY_TO_LOAD",
                                "surface not wired, so nothing may be reported load-ready")


class DurableBuildCertTests(unittest.TestCase):
    def test_certificate_gate_is_halt_tier_and_non_forceable(self):
        self.assertIn("d85_certified", lp.GATE_TYPES)
        spec = lp.load_spec("durable-build")
        proof = next(s for s in spec["stages"] if s["id"] == "P")
        types = [g["type"] for g in proof["gate"]]
        self.assertIn("d85_certified", types, "Proof lost its certificate gate")
        tiers = {g["type"]: ("halt" if g["type"] in ("d85_certified", "build_diagnosis")
                             else g.get("failure_tier", "halt")) for g in proof["gate"]}
        self.assertEqual(tiers["d85_certified"], "halt")

    def test_every_planted_case_passes(self):
        res = lp.run_loop_tests("durable-build")
        failed = [c["name"] for c in res["cases"] if not c["ok"]]
        n = len(BUILD_CASES) + 1  # + the engine's own durability/TOCTOU case
        self.assertEqual(res["summary"], f"{n}/{n} cases pass", f"failed: {failed}")

    def test_certificate_refusal_is_recomputed_not_cached(self):
        """Same run, same stage: red with no certificate, green after a real mint,
        red again once the build bytes move under the certificate."""
        res = lp.run_loop_tests("durable-build")
        names = {c["name"]: c["ok"] for c in res["cases"]}
        self.assertEqual(len(names), len(BUILD_CASES) + 1)
        for claim in ("Proof refuses without a certificate, and force cannot buy the gate",
                      "Altering the build after certification blocks Proof",
                      "a certificate with no cell-bound outcome row still blocks Proof"):
            self.assertTrue(names[claim], f"{claim} stopped being enforced")


class InstalledShapeTests(unittest.TestCase):
    """`installed` must mean the bytes are on disk, in either real shape."""

    def test_both_install_shapes_are_detected(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            self.assertFalse(sr._has(str(root), "rig-stackwright", "rig-stackwright.md"))
            (root / "SKILL.md").write_text("stray\n", encoding="utf-8")
            self.assertFalse(sr._has(str(root), "rig-stackwright", "SKILL.md"),
                             "a stray root SKILL.md made an agent look installed")
            (root / "rig-stackwright.md").write_text("# agent\n", encoding="utf-8")
            self.assertTrue(sr._has(str(root), "rig-stackwright", "rig-stackwright.md"))
            nested = root / "nested"
            (nested / "durable-build").mkdir(parents=True)
            (nested / "durable-build" / "SKILL.md").write_text("# s\n", encoding="utf-8")
            self.assertTrue(sr._has(str(nested), "durable-build", "SKILL.md"))
            self.assertFalse(sr._has(None, "durable-build", "SKILL.md"))


if __name__ == "__main__":
    unittest.main(verbosity=2)
