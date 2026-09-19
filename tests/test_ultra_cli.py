"""The shell entry point into the ULTRA router.

These assert exit codes and route names, because callers and CI read the code,
not the prose. The invariant that matters most: a code-only pass is never 0.
"""
from __future__ import annotations

import json
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BIN = ROOT / "bin" / "rig-ultra"


def run(*argv, stdin=""):
    return subprocess.run([sys.executable, str(BIN), *argv], cwd=ROOT,
                          capture_output=True, text=True, input=stdin)


class TestCLISurface(unittest.TestCase):
    def test_gates_lists_every_declared_gate(self):
        r = run("gates")
        self.assertEqual(r.returncode, 0, r.stderr)
        listed = [ln.split()[0] for ln in r.stdout.splitlines() if "." in ln and " " in ln]
        self.assertGreaterEqual(len(listed), 10, f"expected >=10 gates, got:\n{r.stdout}")
        self.assertIn("outward.gate_d", listed)

    def test_contract_json_parses_and_carries_pack_state(self):
        r = run("contract", "--json")
        self.assertEqual(r.returncode, 0, r.stderr)
        rows = json.loads(r.stdout)
        self.assertGreaterEqual(len(rows), 10)
        self.assertTrue(all("id" in x and "checks" in x for x in rows))
        gate_d = [x for x in rows if x["id"] == "outward.gate_d"]
        self.assertEqual(gate_d[0]["pack"], None, "gate D is code + human authority by design")

    def test_help_mentions_route(self):
        r = run("--help")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("route", r.stdout)


class TestRouteExitCodes(unittest.TestCase):
    def test_missing_facts_is_a_defect(self):
        r = run("route", "plan.dq_before_build", "--state", "one plan, no alternatives")
        self.assertEqual(r.returncode, 1, r.stdout + r.stderr)
        self.assertIn("missing required facts", r.stdout)

    def test_unknown_gate_is_blocked_not_invented(self):
        r = run("route", "nope.nope", "--state", "x")
        self.assertEqual(r.returncode, 1, r.stdout)
        self.assertIn("blocked_unknown_gate", r.stdout)

    def test_offline_code_pass_never_exits_zero(self):
        """The load-bearing one: five documented alternatives, clean code checks,
        Jev not consulted. A caller must not be able to read that as cleared."""
        # The S gate demands five *mechanically* different plans plus a sourced
        # outside view, so the fixture has to supply both or this test is
        # proving the wrong thing (it would exit 1 on a defect, not 2 on Jev).
        facts = json.dumps([{"title": "t%d" % i, "mechanism": "different mechanism %d" % i} for i in range(5)])
        r = run("route", "plan.dq_before_build", "--state", "spec text",
                "--set", f"alternatives={facts}",
                "--set", "reference_class=governed AI studios, first 12 months to repeat revenue",
                "--set", "base_rate=0.28",
                "--set", "base_rate_source=measured 2026-09 class ai-services-first-year",
                "--set", "n_in_class=41", "--json")
        self.assertEqual(r.returncode, 2, r.stdout)
        d = json.loads(r.stdout)
        self.assertEqual(d["route"], "offline_code_only")
        self.assertFalse(d["cleared"])
        self.assertFalse(d["advance"])
        self.assertTrue(any(c["ok"] for c in d["code_checks"]),
                        "the code check should have passed -- the 2 is about Jev, not the code")

    def test_facts_file_and_set_merge(self):
        import tempfile, os
        fd, path = tempfile.mkstemp(suffix=".json")
        with os.fdopen(fd, "w") as fh:
            json.dump({"citation_url": "https://example.com/a",
                       "citation_fetched_at": "2026-09-18",
                       "source_text": "the passage being cited, quoted",
                       "citation_live": True}, fh)                       # caller-supplied; no network in tests
        r = run("route", "research.citation_before_cite", "--state", "claim",
                "--facts", path, "--set", "claim_text=hello hello hello", "--json")
        os.unlink(path)
        self.assertEqual(r.returncode, 2, r.stdout)         # offline, so not cleared
        d = json.loads(r.stdout)
        self.assertEqual(d["route"], "offline_code_only")
        self.assertNotIn("missing required facts", " ".join(d["reasons"]))
        self.assertTrue(all(c["ok"] for c in d["code_checks"]), d["code_checks"])

    def test_bad_facts_json_fails_usage_not_silently(self):
        import tempfile, os
        fd, path = tempfile.mkstemp(suffix=".json")
        with os.fdopen(fd, "w") as fh:
            fh.write("[1,2,3]")
        r = run("route", "plan.dq_before_build", "--state", "x", "--facts", path)
        os.unlink(path)
        self.assertNotEqual(r.returncode, 0)
        self.assertNotEqual(r.returncode, 2, "a malformed facts file is a usage error, not a route")

    def test_metrics_trimmed_is_deterministic(self):
        r = run("metrics", "trimmed", "--values", "0.1,0.5,0.5,0.5,0.95", "--trim", "1")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertAlmostEqual(json.loads(r.stdout)["value"], 0.5, places=9)


if __name__ == "__main__":
    unittest.main()
