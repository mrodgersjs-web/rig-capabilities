#!/usr/bin/env python3
"""Offline gates for trace.py. Run: python3 test_trace.py  (TRACE_PY=<path> tests another copy)."""
import json
import os
import subprocess
import sys
import tempfile
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
TRACE = os.environ.get("TRACE_PY", os.path.join(HERE, "trace.py"))

MAP = """# Section 1: Demo Workouts
## 1.1 Logging
| Area | Capability | How it behaves | Source URL | Confidence |
|---|---|---|---|---|
| Logging | Set types | warm-up, drop, failure sets | https://example.com/a | documented |
| Logging | RIR | reps in reserve per set | https://example.com/b | documented |
## 1.2 Rest
| Area | Capability | How it behaves | Source URL | Confidence |
|---|---|---|---|---|
| Rest | Rest timer | countdown between sets | https://example.com/c | documented |
# Section 2: Demo Nutrition
## 2.1 Food
| Area | Capability | How it behaves | Source URL | Confidence |
|---|---|---|---|---|
| Food | Barcode scan | scan a barcode | https://example.com/d | documented |
"""
AUDIT = """# GAP
## Device-confirmed additions
| ID | Item | Rank | Why |
|---|---|---|---|
| D-01 | Habits section | should | x |
| D-18 | Map correction | correction (no build rank) | y |
## Must items (1-2)
### 1. Fast set logging UI — PARTIAL
### 2. Program builder — MISSING
"""


def run(*args):
    r = subprocess.run([sys.executable, TRACE, *args], capture_output=True, text=True)
    return r.returncode, r.stdout + r.stderr


class Trace(unittest.TestCase):
    def setUp(self):
        self.d = tempfile.mkdtemp()
        self.L = os.path.join(self.d, "TRACE.jsonl")
        self.repo = os.path.join(self.d, "repo")
        os.makedirs(os.path.join(self.repo, "test"))
        open(os.path.join(self.repo, "test", "set_types_test.dart"), "w").write("// test\n")
        g = ["git", "-C", self.repo]
        subprocess.run(g + ["init", "-q"], check=True)
        subprocess.run(g + ["add", "."], check=True)
        # A fixture commit object via plumbing (write-tree + commit-tree): no branch, no hooks
        # involved, nothing "lands" anywhere; it exists only so `cat-file -e` has a real sha.
        tree = subprocess.run(g + ["write-tree"], capture_output=True, text=True, check=True).stdout.strip()
        full = subprocess.run(g + ["-c", "user.name=t", "-c", "user.email=t@t", "commit-tree", tree, "-m", "S1 set types"],
                              capture_output=True, text=True, check=True).stdout.strip()
        self.sha = full[:7]
        open(os.path.join(self.d, "map.md"), "w").write(MAP)
        open(os.path.join(self.d, "audit.md"), "w").write(AUDIT)
        rc, out = run("import-map", "--ledger", self.L, "--map", os.path.join(self.d, "map.md"),
                      "--apps", "Demo Workouts=demo-w,Demo Nutrition=demo-n", "--prefix", "Demo Workouts=DW,Demo Nutrition=DN",
                      "--target", "tf")
        self.assertEqual(rc, 0, out)
        rc, out = run("import-audit", "--ledger", self.L, "--audit", os.path.join(self.d, "audit.md"),
                      "--app", "demo-audit", "--target", "tf", "--prefix", "TF")
        self.assertEqual(rc, 0, out)

    def rows(self):
        return {json.loads(x)["id"]: json.loads(x) for x in open(self.L) if x.strip()}

    def cov(self):
        return run("coverage", "--ledger", self.L, "--repo", self.repo)

    def test_import_ids_and_audit(self):
        r = self.rows()
        self.assertEqual(sorted(k for k in r if k.startswith("D")), ["DN-D2.1-01", "DW-D1.1-01", "DW-D1.1-02", "DW-D1.2-01"])
        self.assertEqual(r["TF-AM01"]["status"], "TRIAGED")
        self.assertEqual(r["TF-AM01"]["priority"], "must")
        self.assertEqual(r["TF-D-01"]["priority"], "should")
        self.assertEqual(r["TF-D-18"]["status"], "SKIP")

    def test_fresh_ledger_is_valid_but_incomplete(self):
        self.assertEqual(self.cov()[0], 1)

    def test_reimport_never_overwrites_a_decision(self):
        run("set", "--ledger", self.L, "--id", "DN-D2.1-01", "--status", "SKIP", "--reason", "no nutrition in v1")
        run("import-map", "--ledger", self.L, "--map", os.path.join(self.d, "map.md"),
            "--apps", "Demo Workouts=demo-w,Demo Nutrition=demo-n", "--prefix", "Demo Workouts=DW,Demo Nutrition=DN", "--target", "tf")
        self.assertEqual(self.rows()["DN-D2.1-01"]["status"], "SKIP")

    def test_built_needs_a_real_commit(self):
        run("set", "--ledger", self.L, "--id", "DW-D1.1-01", "--status", "BUILT")
        self.assertEqual(self.cov()[0], 2, "BUILT without commit evidence passed")
        run("set", "--ledger", self.L, "--id", "DW-D1.1-01", "--evidence", "commit:deadbee")
        rc, out = self.cov()
        self.assertEqual(rc, 2, "a commit that is not in the repo passed")
        self.assertIn("not in target repo", out)

    def test_skip_needs_a_reason(self):
        run("set", "--ledger", self.L, "--id", "DW-D1.2-01", "--status", "SKIP")
        self.assertEqual(self.cov()[0], 2)

    def test_verified_needs_proof_that_exists(self):
        run("set", "--ledger", self.L, "--id", "DW-D1.1-01", "--status", "VERIFIED", "--evidence", f"commit:{self.sha}",
            "--evidence", "test:test/missing_test.dart")
        self.assertEqual(self.cov()[0], 2)

    def test_mapped_screen_is_done_only_when_what_it_covers_is_done(self):
        rows = self.rows()
        rows["SCR-1"] = {**rows["DW-D1.1-01"], "id": "SCR-1", "kind": "screen", "status": "MAPPED",
                         "covers": ["DW-D1.1-01"], "evidence": []}
        with open(self.L, "w") as f:
            for r in rows.values():
                f.write(json.dumps(r) + "\n")
        _, out = run("coverage", "--ledger", self.L, "--repo", self.repo, "--json")
        self.assertEqual(json.loads(out)["done"], 1, "MAPPED screen counted done while its row is OPEN")
        run("set", "--ledger", self.L, "--id", "DW-D1.1-01", "--status", "VERIFIED", "--evidence", f"commit:{self.sha}",
            "--evidence", "test:test/set_types_test.dart")
        _, out = run("coverage", "--ledger", self.L, "--repo", self.repo, "--json")
        self.assertEqual(json.loads(out)["done"], 3)

    def test_everything_decided_exits_zero(self):
        ids = [i for i, r in self.rows().items() if r["status"] != "SKIP"]
        run("set", "--ledger", self.L, "--id", ",".join(ids), "--status", "VERIFIED", "--evidence", f"commit:{self.sha}",
            "--evidence", "test:test/set_types_test.dart")
        rc, out = self.cov()
        self.assertEqual(rc, 0, out)


if __name__ == "__main__":
    unittest.main(verbosity=1)
