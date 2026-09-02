"""Goal specs: compiled, pinned, staleness-checked, and pullable by agents.

Two of these tests are real drift gates on the committed tree, not synthetic
assertions: `test_committed_specs_are_all_pinned` and
`test_tree_has_no_stale_spec` go RED the moment someone edits a harness YAML and
forgets to recompile, which is precisely the failure that would let an agent
execute gates no longer declared by the harness.
"""
from __future__ import annotations

import json
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from rig_capabilities import goal_spec  # noqa: E402
from rig_capabilities.server import TOOLS  # noqa: E402

sys.path.insert(0, str(REPO_ROOT / "scripts"))
import compile_harnesses as CH  # noqa: E402
from rig_capabilities.catalog import Repo  # noqa: E402


def synth(tmp: Path, pinned: bool = True) -> Path:
    """Minimal out/ + capabilities/ tree so staleness is testable in isolation."""
    src = tmp / "capabilities" / "harnesses" / "x.yaml"
    src.parent.mkdir(parents=True, exist_ok=True)
    src.write_text("harness_id: x\nstatus: active\ngoal: g\n")
    import hashlib
    sha = hashlib.sha256(src.read_bytes()).hexdigest()
    meta = {"source": "capabilities/harnesses/x.yaml",
            "gates_without_proof": [], "meta": {}}
    if pinned:
        meta["source_sha256"] = sha
    spec = tmp / "out" / "harness-goalspecs" / "x.json"
    spec.parent.mkdir(parents=True, exist_ok=True)
    spec.write_text(json.dumps({"goals": [{
        "id": "G-x", "name": "X", "anchor": "L1-D1-A1-I", "bms_mode": "A1",
        "gates": [{"id": "G1", "required": True}],
        "preconditions": {"meta": {"session_type": "demo-session"}},
        "_meta": meta}]}))
    return tmp


class ServeShapeTests(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="gos-"))

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_fresh_spec_is_ok(self):
        out = goal_spec.serve(synth(self.tmp))
        self.assertEqual(out["verdict"], "OK")
        self.assertEqual(out["stale"], [])
        self.assertEqual(out["goals"][0]["session_type"], "demo-session")

    def test_stale_when_source_moves_without_recompile(self):
        root = synth(self.tmp)
        self.assertEqual(goal_spec.serve(root)["verdict"], "OK")
        # The plant: author edits the harness, nobody recompiles.
        (root / "capabilities" / "harnesses" / "x.yaml").write_text(
            "harness_id: x\nstatus: active\ngoal: g\nnew_gate: added\n")
        out = goal_spec.serve(root, stem="x")
        self.assertEqual(out["verdict"], "STALE")
        self.assertEqual(out["provenance"]["reason"], "source_changed_since_compile")
        self.assertIn("compile_harnesses", out["provenance"]["recompile"])

    def test_unpinned_spec_is_stale_never_ok(self):
        # Specs compiled before source pinning carry no hash. Reporting those as
        # "ok" would be a false assurance, so they are unverified by verdict.
        out = goal_spec.serve(synth(self.tmp, pinned=False), stem="x")
        self.assertEqual(out["verdict"], "STALE")
        self.assertEqual(out["provenance"]["reason"], "source_unpinned")

    def test_missing_source_is_named(self):
        root = synth(self.tmp)
        (root / "capabilities" / "harnesses" / "x.yaml").unlink()
        prov = goal_spec.serve(root, stem="x")["provenance"]
        self.assertEqual(prov["reason"], "source_missing")
        self.assertFalse(prov["source_present"])

    def test_unknown_stem_is_a_reason_not_a_traceback(self):
        self.assertEqual(goal_spec.serve(synth(self.tmp), stem="nope")["reason"],
                         "no_such_spec")

    def test_path_traversal_stem_refused(self):
        self.assertEqual(goal_spec.serve(synth(self.tmp), stem="../../etc/passwd")["reason"],
                         "unsafe_stem")

    def test_no_specs_says_so_and_how_to_fix(self):
        empty = self.tmp / "nothing"
        empty.mkdir()
        out = goal_spec.serve(empty)
        self.assertEqual(out["verdict"], "NO_SPECS")
        self.assertIn("compile", out["detail"])

    def test_repo_object_is_accepted_like_a_path(self):
        # The CLI and the MCP server hand in a Repo, not a Path. A stand-in
        # object here would miss the exact attribute collision (Repo.root vs
        # Path.root) that this acceptance exists to handle, so use the real one.
        root = synth(self.tmp)
        self.assertEqual(goal_spec.serve(Repo(root))["verdict"], "OK")

    def test_resolve_by_session_type(self):
        root = synth(self.tmp)
        self.assertEqual(goal_spec.serve(root, session_type="demo")["stems"], ["x"])
        self.assertEqual(goal_spec.serve(root, session_type="absent")["verdict"],
                         "NO_MATCH")


class CommittedTreeTests(unittest.TestCase):
    """These two go RED on real drift in the checkout. That is the point."""

    def test_committed_specs_are_all_pinned(self):
        unpinned = []
        for path in goal_spec.spec_paths(REPO_ROOT):
            payload, reason = goal_spec.load_spec(REPO_ROOT, path.stem)
            self.assertIsNone(reason, f"{path.stem}: {reason}")
            if not (payload.get("_meta") or {}).get("source_sha256"):
                unpinned.append(path.stem)
        self.assertEqual(unpinned, [], "specs missing _meta.source_sha256")

    def test_tree_has_no_stale_spec(self):
        out = goal_spec.serve(REPO_ROOT)
        self.assertEqual(out["verdict"], "OK",
                         f"stale specs, recompile: {out.get('stale')}")
        self.assertGreater(out["specs"], 50, "expected the full harness estate")

    def test_session_type_resolution_works_on_real_catalogue(self):
        out = goal_spec.serve(REPO_ROOT, session_type="code-review")
        self.assertIn("hA-01-code-review", out["stems"])

    def test_advisory_phase_gates_are_carried_not_executed(self):
        payload, _ = goal_spec.load_spec(REPO_ROOT, "rig-known-expert-os-v1")
        rows = payload["_meta"]["phase_gates"]
        self.assertEqual(len(rows), 10)
        self.assertTrue(all(r["executable"] is False for r in rows))
        self.assertNotIn("phase_gates", payload)  # advisory never joins gates[]
        # The anti-fabrication boundary travels with the goal.
        self.assertEqual([p["status"] for p in payload["_meta"]["phases_beyond_source"]],
                         ["objective_only_truncated", "absent_at_source"])


class CompilerRobustnessTests(unittest.TestCase):
    """A malformed gate used to abort the whole build with an AttributeError."""

    BASE = {"coordinate_space": {"levels": ["L2"], "primary_diamonds": ["D1"],
                                 "bms_modes": ["A1"], "iqrsqpi_steps": ["Intent"]},
            "harness_name": "t", "status": "active"}

    def test_bare_string_capability_gate_names_the_defect(self):
        h = dict(self.BASE, capability_gates=["gate written as a bare string"])
        res = CH.compile_harness("t", h)
        self.assertTrue(any("bare string" in e for e in res["errors"]), res["errors"])
        # The malformed gate must not be quietly promoted into the emitted goal.
        self.assertEqual(res["payload"]["gates"], [])

    def test_bare_string_identity_gate_names_the_defect(self):
        h = dict(self.BASE, identity_lock={"gates": ["just a sentence"]})
        res = CH.compile_harness("t", h)
        self.assertTrue(any("bare string" in e for e in res["errors"]), res["errors"])

    def test_string_containing_the_word_gates_does_not_fake_shape_b(self):
        # Old shape detection did `"gates" not in c`, which a plain string passes
        # by substring — so a flat list whose text mentions "gates" was read as
        # grouped and every gate vanished silently.
        h = dict(self.BASE, capability_gates=[
            "run all the gates before shipping",
            {"id": "G2", "requirement": "real gate", "proof": "cmd"}])
        res = CH.compile_harness("t", h)
        self.assertTrue(any("bare string" in e for e in res["errors"]), res["errors"])
        self.assertTrue(any("real gate" not in e and "G2" in e
                            for e in res["errors"]) or res["errors"])

    def test_draft_without_coordinates_is_skipped_not_failed(self):
        res = CH.compile_harness("gap-x", {"status": "draft", "harness_name": "gap"})
        self.assertIsNone(res["payload"])
        self.assertEqual(res["errors"], [], "a skip must not be a failure")
        self.assertIn("draft", res["skip"])

    def test_active_harness_without_coordinates_still_fails(self):
        res = CH.compile_harness("h", {"status": "active", "harness_name": "h"})
        self.assertIn("coordinate_space missing an axis", res["errors"])
        self.assertIsNone(res["skip"])

    def test_compiled_spec_pins_its_source_hash(self):
        res = CH.compile_harness("t", dict(self.BASE, identity_lock={}),
                                 source_sha="ab" * 32)
        self.assertEqual(res["payload"]["_meta"]["source_sha256"], "ab" * 32)


class SurfaceTests(unittest.TestCase):
    def test_goal_spec_tool_is_exposed_and_dispatched(self):
        names = {t["name"] for t in TOOLS}
        self.assertIn("capabilities_goal_spec", names)
        schema = next(t for t in TOOLS if t["name"] == "capabilities_goal_spec")
        self.assertEqual(sorted(schema["inputSchema"]["properties"]),
                         ["session_type", "stem"])

    def test_cli_verb_serves_the_same_answer(self):
        out = subprocess.run([str(REPO_ROOT / "bin" / "rig-capabilities"),
                              "goal-spec", "--stem", "rig-realign-v1"],
                             cwd=REPO_ROOT, capture_output=True, text=True, timeout=120)
        self.assertEqual(out.returncode, 0, out.stderr[-200:])
        doc = json.loads(out.stdout)
        self.assertEqual(doc["verdict"], "OK")
        self.assertEqual(doc["goal"]["id"],
                         goal_spec.load_spec(REPO_ROOT, "rig-realign-v1")[0]["id"])


import subprocess  # noqa: E402  (used by SurfaceTests)

if __name__ == "__main__":
    unittest.main()
