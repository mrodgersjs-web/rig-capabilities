"""ReadOnlyToolTests: the five fable2031 MCP tools read and never write."""
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

from rig_capabilities import afproof, canary, dispatcher, evidence_ledger
from rig_capabilities import model_route, realign, register
from rig_capabilities.catalog import Repo
from rig_capabilities.server import TOOLS, build_server

NEW_TOOLS = ("capabilities_fabrication", "capabilities_register",
             "capabilities_evidence", "capabilities_converge",
             "capabilities_dispatch_verify")
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
    # The prefilter must not materialise the claimed tree or turn the canary:
    # both are the full ladder's business, and a tool that did either would be
    # reporting on a checkout it built itself.
    ("dispatcher", "verifier_checkout_plan"),
    ("canary", "mint"),
    ("canary", "rotate"),
)
_MODULES = {"afproof": afproof, "realign": realign, "model_route": model_route,
            "register": register, "evidence_ledger": evidence_ledger,
            "dispatcher": dispatcher, "canary": canary}


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

    def test_five_tools_registered_with_valid_schemas(self):
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

    def test_no_writer_is_reachable_from_any_handler(self):
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

    # ---- capabilities_converge ------------------------------------------

    def test_converge_answers_empty_args_from_the_fixture_scope_and_says_so(self):
        """The live corpus roots include ~/mnt/RIGLake, a stale mount whose walk
        dies with TimeoutError after ~160 s. A tool called with `{}` cannot
        default to them, so it scores the committed 20-card corpus and labels the
        answer instead of pretending it scanned the real corpus."""
        self._forbid_writers()
        out = self.srv.handlers["capabilities_converge"]({})
        self.assertIs(out["read_only"], True)
        self.assertEqual(out["corpus_scope"], "fixture_snapshot")
        self.assertIs(out["live_corpus_scanned"], False)
        self.assertEqual(out["verdict"], "BASELINE_ONLY",
                         "no prior sealed week exists, so no dC_t PASS is available")
        self.assertIn("booked_qualified_conversations", out["gate"]["causes"])
        self.assertEqual(out["score"]["bookings"]["count"], 0)
        json.dumps(out, sort_keys=True)

    def test_converge_reports_a_dead_mount_as_data(self):
        """~/mnt/RIGLake reports `is_dir() == True` and its walk then dies with
        TimeoutError around 160 s. Injecting the failure keeps the assertion
        honest and instant: the tool must answer with data, not raise."""
        from rig_capabilities import corpus as corpus_mod
        def dying(*_a, **_k):
            raise TimeoutError("[Errno 60] Operation timed out: '/mnt/RIGLake'")
        original = corpus_mod.corpus_report
        corpus_mod.corpus_report = dying
        self.addCleanup(setattr, corpus_mod, "corpus_report", original)
        self._forbid_writers()
        out = self.srv.handlers["capabilities_converge"]({"roots": ["~/mnt/RIGLake"]})
        self.assertIs(out["read_only"], True)
        self.assertIn("corpus_scan_failed:TimeoutError", out["error"])
        self.assertIn("stale mount", out["hint"])
        self.assertNotIn("verdict", out)

    def test_converge_survives_a_scoring_failure_without_raising(self):
        from rig_capabilities import convergence
        def boom(*_a, **_k):
            raise RuntimeError("register unreadable")
        original = convergence.score_week
        convergence.score_week = boom
        self.addCleanup(setattr, convergence, "score_week", original)
        self._forbid_writers()
        out = self.srv.handlers["capabilities_converge"]({})
        self.assertIs(out["read_only"], True)
        self.assertIn("register unreadable", out["error"])

    def test_converge_operator_scope_is_labelled_as_such(self):
        self._forbid_writers()
        out = self.srv.handlers["capabilities_converge"](
            {"roots": ["tests/fixtures/fable2031/corpus"]})
        self.assertEqual(out["corpus_scope"], "operator_supplied")
        self.assertIs(out["live_corpus_scanned"], True)
        self.assertIsNotNone(out["verdict"])

    # ---- capabilities_dispatch_verify ------------------------------------

    def test_dispatch_verify_empty_args_return_the_ladder_not_an_error(self):
        self._forbid_writers()
        out = self.srv.handlers["capabilities_dispatch_verify"]({})
        self.assertIs(out["read_only"], True)
        self.assertEqual(out["mode"], "no_packet")
        self.assertIsNone(out["verdict"])
        self.assertEqual(len(out["fixtures"]), 5)
        honest = [f for f in out["fixtures"] if "honest" in f["packet"]]
        self.assertEqual([f["expected_exit"] for f in honest], [3],
                         "the honest packet must not advertise exit 0")

    def test_dispatch_verify_rejects_every_bad_packet_offline(self):
        self._forbid_writers()
        for name in ("handoff-fabricated.json", "handoff-phantom.json",
                     "handoff-tampered.json", "handoff-isolation.json"):
            with self.subTest(packet=name):
                out = self.srv.handlers["capabilities_dispatch_verify"](
                    {"packet": f"tests/fixtures/fable2031/{name}"})
                self.assertIn(out["verdict"],
                              ("FABRICATED", "ISOLATION_BREACH", "BLOCKED"))
                self.assertIs(out["checkout_performed"], False)
                self.assertIs(out["reexecution_performed"], False)

    def test_dispatch_verify_cannot_emit_pass_even_if_admit_regresses(self):
        """The rung's whole purpose is that an offline run cannot verify. If
        `admit` ever regresses to handing out PASS, the tool reports a violation
        rather than forwarding the word."""
        original = dispatcher.admit
        def lying_admit(packet, checkout, **_kw):
            return {"verdict": "PASS", "reasons": [], "checks": {},
                    "verifier_family": "gpt", "packet_sha256": "0" * 64}
        dispatcher.admit = lying_admit
        self.addCleanup(setattr, dispatcher, "admit", original)
        out = self.srv.handlers["capabilities_dispatch_verify"](
            {"packet": "tests/fixtures/fable2031/handoff-honest.json"})
        self.assertEqual(out["verdict"], "BLOCKED")
        self.assertEqual(out["invariant_violation"], "offline_pass_emitted")

    def test_dispatch_verify_missing_packet_is_data(self):
        for arg in ({}, {"packet": "tests/fixtures/fable2031/nope.json"}):
            out = self.srv.handlers["capabilities_dispatch_verify"](
                dict(arg, packet="tests/fixtures/fable2031/nope.json"))
            self.assertEqual(out["error"], "packet_missing")
            self.assertEqual(out["expected_exit"], 2)

    def test_dispatch_verify_declares_the_offline_rung_in_the_ladder(self):
        from rig_capabilities.afproof import verdict_ladder
        ladder = verdict_ladder()
        rung2 = next(r for r in ladder["rungs"] if r["name"] == "dispatcher_admit")
        self.assertIn("PASS", rung2["never_emits_offline"])
        self.assertIn("PREFILTER_CLEAR", rung2["offline_emits"])
        self.assertTrue(any("PREFILTER_CLEAR" in i for i in ladder["invariants"]))


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
