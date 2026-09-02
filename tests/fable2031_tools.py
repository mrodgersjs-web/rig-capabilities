"""ReadOnlyToolTests: the three fable2031 MCP tools read and never write."""
from __future__ import annotations

import json
import os
import re
import tempfile
import unittest
from pathlib import Path
import sys

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))
FIX = REPO_ROOT / "tests" / "fixtures" / "fable2031"

from rig_capabilities import afproof, evidence_ledger, model_route, realign
from rig_capabilities import register
from rig_capabilities.catalog import Repo
from rig_capabilities.server import TOOLS, build_server

NEW_TOOLS = ("capabilities_fabrication", "capabilities_register",
             "capabilities_evidence")
# Every writer these tools are forbidden to reach. Patched to raise before
# each handler call, so a future edit that wires a writer in fails HERE.
FORBIDDEN = (
    ("afproof", "seal_packet"),
    ("afproof", "write_sentinel_evidence"),
    ("afproof", "log_fabrication"),
    ("realign", "run_week"),
    ("model_route", "apply"),
    ("register", "write_register"),
    ("evidence_ledger", "write_ledger"),
)
_MODULES = {"afproof": afproof, "realign": realign, "model_route": model_route,
            "register": register, "evidence_ledger": evidence_ledger}


def _boom(module: str, name: str):
    def raiser(*_args, **_kwargs):
        raise AssertionError(f"read-only tool reached writer {module}.{name}")
    return raiser


class ReadOnlyToolTests(unittest.TestCase):
    """Handlers are called directly, never over HTTP; no writer survives."""

    def setUp(self):
        self.srv = build_server(Repo(REPO_ROOT))
        self.schema = {t["name"]: t["inputSchema"] for t in TOOLS}

    # ---- registration ---------------------------------------------------

    def test_three_tools_registered_with_valid_schemas(self):
        for name in NEW_TOOLS:
            self.assertIn(name, self.schema, f"{name} missing from TOOLS")
            schema = self.schema[name]
            self.assertEqual(schema.get("type"), "object", name)
            props = schema.get("properties")
            self.assertIsInstance(props, dict, name)
            for key, spec in props.items():
                self.assertIsInstance(spec, dict, f"{name}.{key}")
                self.assertIn("type", spec, f"{name}.{key}")
            for key in schema.get("required", []):
                self.assertIn(key, props, f"{name} requires unknown {key}")

    def test_every_tool_has_a_handler(self):
        named = {t["name"] for t in TOOLS}
        self.assertEqual(named ^ set(self.srv.handlers), set(),
                         "TOOLS and the handler table disagree")

    def test_certify_only_passthrough_survives(self):
        import inspect
        src = inspect.getsource(build_server)
        self.assertIn("self_test(repo, only=", src,
                      "the certify only= pass-through was reverted")

    def test_server_never_binds_a_writer_at_import_time(self):
        # The monkeypatch guard catches a writer imported INSIDE a handler,
        # because the module attribute is resolved at call time. A top-of-file
        # binding resolves once, before any patch lands — so forbid that form.
        lines = (REPO_ROOT / "rig_capabilities" / "server.py").read_text()
        for line in lines.splitlines():
            if not re.match(r"^(from|import)\s", line):
                continue
            for _module, name in FORBIDDEN:
                self.assertNotIn(
                    name, line,
                    f"server.py binds writer {name} at import time, where no "
                    "patch can intercept it")


    def test_new_names_are_not_mutating_mcp(self):
        from rig_capabilities.done_tests import MCP_MUTATING
        for name in NEW_TOOLS:
            self.assertNotIn(name, MCP_MUTATING,
                             f"{name} is read-only; the reentrancy guard "
                             "must not gate it")

    # ---- writers are unreachable ----------------------------------------

    def _forbid_writers(self):
        for module, name in FORBIDDEN:
            target = _MODULES[module]
            original = getattr(target, name)
            setattr(target, name, _boom(module, name))
            self.addCleanup(setattr, target, name, original)

    def test_no_writer_is_reachable_from_the_three_handlers(self):
        self._forbid_writers()
        for name in NEW_TOOLS:
            with self.subTest(tool=name):
                out = self.srv.handlers[name]({})
                self.assertIs(out["read_only"], True)

    # ---- capabilities_fabrication ---------------------------------------

    def test_fabrication_reports_the_ladder_and_never_invents_a_rate(self):
        out = self.srv.handlers["capabilities_fabrication"]({})
        self.assertEqual(set(out) >= {"read_only", "rates", "verdict_ladder"},
                         True)
        json.dumps(out, sort_keys=True)  # must be serialisable as-is
        ladder = out["verdict_ladder"]
        self.assertEqual(ladder["schema"], "rig.verdict-ladder.v1")
        self.assertNotIn("PASS", ladder["rungs"][0]["emits"],
                         "the TAC prefilter may never say PASS")
        self.assertIn("PASS", ladder["rungs"][0]["never_emits"])

    def test_fabrication_absent_ledger_is_zeroed_not_guessed(self):
        before = os.environ.get("RIG_LEASE_STATE_ROOT")
        tmp = tempfile.TemporaryDirectory(prefix="tools-ledger-")
        self.addCleanup(tmp.cleanup)
        os.environ["RIG_LEASE_STATE_ROOT"] = tmp.name

        def restore():
            if before is None:
                os.environ.pop("RIG_LEASE_STATE_ROOT", None)
            else:
                os.environ["RIG_LEASE_STATE_ROOT"] = before
        self.addCleanup(restore)
        self.srv = build_server(Repo(REPO_ROOT))

        rates = self.srv.handlers["capabilities_fabrication"]({})["rates"]
        self.assertIs(rates["ledger_present"], False)
        self.assertIsNone(rates["fabrication_rate"])
        self.assertEqual(rates["total"], 0)
        self._forbid_writers()
        self.srv.handlers["capabilities_fabrication"]({"since_days": 7})

    # ---- capabilities_register ------------------------------------------

    def test_register_reports_metrics_and_the_real_booking_state(self):
        out = self.srv.handlers["capabilities_register"]({})
        self.assertEqual(
            set(out) >= {"read_only", "rows_total", "row_errors", "metrics",
                         "booked_qualified_conversations", "sealed_weeks",
                         "delta_c_t"}, True)
        json.dumps(out, sort_keys=True)

        rows = register.load_register(Repo(REPO_ROOT))
        self.assertEqual(out["rows_total"], len(rows))
        self.assertEqual(out["row_errors"], register.row_errors(rows))
        self.assertEqual(out["metrics"], self._metrics(rows))

        booked = out["booked_qualified_conversations"]
        self.assertEqual(booked["id"], "booked_qualified_conversations")
        # The count is the module's, never this tool's.
        try:
            doc = register.load_bookings(
                register.bookings_path(Repo(REPO_ROOT), booked["week"]))
            self.assertEqual(booked["qualified"], doc["count"])
        except register.RegisterError as exc:
            self.assertIsNone(booked["qualified"])
            self.assertIn("bookings_artifact", booked["error"])
            self.assertIn(str(exc), booked["error"])

        prior = self._sealed_series(Repo(REPO_ROOT))
        self.assertEqual(out["sealed_weeks"], [w["week"] for w in prior])
        if prior:
            self.assertEqual(out["delta_c_t"]["previous"], prior[-1]["c_t"])
            self.assertEqual(out["delta_c_t"]["current"],
                             out["metrics"]["c_t"])
        else:
            self.assertIsNone(out["delta_c_t"],
                              "no sealed week means no dC_t, not dC_t = 0")

    def test_register_missing_store_is_reported_not_repaired(self):
        with tempfile.TemporaryDirectory(prefix="tools-register-") as tmp:
            srv = build_server(Repo(Path(tmp)))
            self._forbid_writers()
            out = srv.handlers["capabilities_register"]({})
            self.assertEqual(out["rows_total"], 0)
            booked = out["booked_qualified_conversations"]
            self.assertIs(booked["row_present"], False)
            self.assertEqual(
                booked["error"],
                "booked_qualified_conversations_missing_or_underweighted")
            json.dumps(out, sort_keys=True)

    # ---- capabilities_evidence ------------------------------------------

    def test_evidence_resumable_set_is_the_ledger_modules_own(self):
        out = self.srv.handlers["capabilities_evidence"]({})
        self.assertEqual(
            set(out) >= {"read_only", "ledger", "rows_total",
                         "resume_eligible", "claims"}, True)
        json.dumps(out, sort_keys=True)
        rows = evidence_ledger.load_ledger(Repo(REPO_ROOT))
        self.assertEqual(out["rows_total"], len(rows))
        self.assertEqual(
            out["resume_eligible"],
            sorted(r["id"] for r in evidence_ledger.resume_claims(
                rows, root=REPO_ROOT)))
        for claim in out["claims"]:
            if claim["resume"]:
                self.assertEqual(claim["type"], "direct")
                self.assertGreaterEqual(float(claim["confidence"]),
                                        evidence_ledger.RESUME_MIN_CONFIDENCE)
                self.assertEqual(claim["errors"], [])

    def test_evidence_never_calls_a_planned_claim_resumable(self):
        with tempfile.TemporaryDirectory(prefix="tools-ledger-") as tmp:
            root = Path(tmp)
            (root / "proof.txt").write_text("receipt\n", encoding="utf-8")
            (root / evidence_ledger.LEDGER_PATH).write_text(
                "id,claim,evidence,type,confidence,allowed_use\n"
                "P-1,Planned work labelled for a resume,proof.txt,planned,"
                "0.9,resume\n"
                "D-1,A direct claim with a real receipt,proof.txt,direct,"
                "0.95,resume\n", encoding="utf-8")
            srv = build_server(Repo(root))
            self._forbid_writers()
            out = srv.handlers["capabilities_evidence"]({})
            self.assertEqual(out["resume_eligible"], ["D-1"])
            planned = next(c for c in out["claims"] if c["id"] == "P-1")
            self.assertIs(planned["resume"], False)
            self.assertEqual(planned["errors"], ["unverified_claim_on_resume"])
            json.dumps(out, sort_keys=True)

    # -- the modules the tool reports through, read straight --------------
    @staticmethod
    def _metrics(rows):
        from rig_capabilities.convergence import metrics
        return metrics(rows)

    @staticmethod
    def _sealed_series(repo):
        from rig_capabilities.convergence import sealed_series
        return sealed_series(repo)


if __name__ == "__main__":
    unittest.main()
