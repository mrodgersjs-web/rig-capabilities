"""The two surface tools that expose this increment's verdicts to any agent.

Both tools run the committed modules' own `main()` in-process, so the test's job
is not to re-check the verdicts — `tests/test_paired_runs.py`, `test_topology.py`
and the rest do that. What is tested here is the *surface* contract:

* registered with a schema, handled without writing anything;
* repo-relative paths resolve against the repo, not the process cwd;
* `ran` (it executed) is not `clean` (it found nothing to complain about), and a
  fixture that is supposed to be RED reads as debt, never as refusal;
* the numbers it publishes are the numbers the CLI prints — a tool that quietly
  disagrees with `./bin/rig-capabilities` is the `40.0.0` bug wearing a new hat;
* a scanner whose output shape moved produces a named refusal, not a `0` that
  reads as "no debt".
"""
from __future__ import annotations

import io
import json
import os
import re
import subprocess
import sys
import tempfile
import types
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from rig_capabilities import surface_tools as ST            # noqa: E402
from rig_capabilities.catalog import Repo                   # noqa: E402
from rig_capabilities.done_tests import MCP_MUTATING        # noqa: E402
from rig_capabilities.server import TOOLS, build_server     # noqa: E402

NEW = ("capabilities_asset_hygiene", "capabilities_verdict")
REPO = Repo(REPO_ROOT)


def _run(cmd: list) -> subprocess.CompletedProcess:
    return subprocess.run(cmd, cwd=REPO_ROOT, capture_output=True, text=True,
                          env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"}, timeout=600)


class RegistrationTests(unittest.TestCase):
    def test_registered_with_typed_schemas(self):
        schema = {t["name"]: t["inputSchema"] for t in TOOLS}
        for name in NEW:
            self.assertIn(name, schema)
            self.assertEqual(schema[name].get("type"), "object", name)
            props = schema[name].get("properties", {})
            self.assertIsInstance(props, dict, name)
            for key, spec in props.items():
                self.assertIn("type", spec, f"{name}.{key}")
            for key in schema[name].get("required", []):
                self.assertIn(key, props, f"{name} requires unknown {key}")

    def test_every_new_tool_has_a_handler(self):
        srv = build_server(REPO)
        named = {t["name"] for t in TOOLS}
        self.assertEqual(named ^ set(srv.handlers), set(),
                         "TOOLS and the handler table disagree")
        for name in NEW:
            self.assertIn(name, srv.handlers)

    def test_new_tools_are_not_listed_as_mutating(self):
        for name in NEW:
            self.assertNotIn(name, MCP_MUTATING)


class HandlerVerdictTests(unittest.TestCase):
    """A refusal must reach the MCP surface, not just the returned dict.

    This is the same hole `round` had: `isError` comes from `ToolError`, so a
    handler that returns a refusal as data lets a client that only checks the
    flag record red as green. Debt (exit 1) stays data — it is an answer.
    """

    @classmethod
    def setUpClass(cls):
        cls.srv = build_server(REPO)

    def test_unknown_check_raises(self):
        from rig_capabilities.mcp_stdio import ToolError
        with self.assertRaises(ToolError) as cm:
            self.srv.handlers["capabilities_verdict"]({"check": "vibes"})
        self.assertIn("unknown_check:vibes", str(cm.exception))

    def test_a_plant_is_debt_not_an_outage(self):
        """`--plant revocation` exits 2 by design — the asset's own `done_when`
        asserts `test $rc -eq 2`. The surface must show the guard firing, not
        pretend the module failed to run."""
        out = self.srv.handlers["capabilities_verdict"](
            {"check": "lifecycle",
             "argv": ["plan", "--example", "--now", "2026-09-02",
                      "--plant", "revocation"]})
        self.assertIs(out["ran"], True)
        self.assertIs(out["clean"], False)
        self.assertEqual(out["exit_code"], 2)
        self.assertIn("revocation", out["text"])

    def test_debt_is_returned_not_raised(self):
        out = self.srv.handlers["capabilities_verdict"](
            {"check": "paired_runs",
             "argv": ["examples/fixtures/paired-runs/two_variables.jsonl"]})
        self.assertIs(out["ran"], True)
        self.assertIs(out["clean"], False)

    def test_hygiene_refusal_raises(self):
        from rig_capabilities.mcp_stdio import ToolError
        orig = ST._load_script
        ST._load_script = lambda root, name: types.SimpleNamespace(
            main=lambda argv=None: 0)
        try:
            with self.assertRaises(ToolError) as cm:
                self.srv.handlers["capabilities_asset_hygiene"]({})
        finally:
            ST._load_script = orig
        self.assertIn("counts_unreadable", str(cm.exception))

class AssetHygieneTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.out = ST.asset_hygiene(REPO, {})

    def test_ran_and_reported_its_scope(self):
        self.assertIs(self.out["read_only"], True)
        self.assertIs(self.out["ran"], True, self.out.get("reason"))
        self.assertEqual(self.out["scope"], "capabilities")

    def test_counts_agree_with_the_cli_verbatim(self):
        """The tool and the command must not be two implementations of one fact."""
        cli = _run(["python3", "scripts/exemplar_resolution.py", "--root", ".", "--json"])
        rep = json.loads(cli.stdout)
        c = self.out["surfaces"]["counts"]
        self.assertEqual(c["declared_great_example"], rep["declared"])
        self.assertEqual(c["resolved_great_example"], rep["resolved"])
        self.assertEqual(c["dangling_great_example"], len(rep["missing"]))

        scan = _run(["python3", "-m", "rig_capabilities.skill_contract", "capabilities"])
        m = re.search(r"(\d+) finding\(s\) across (\d+) file\(s\)", scan.stdout)
        self.assertIsNotNone(m, scan.stdout[-200:])
        self.assertEqual(c["contract_findings"], int(m.group(1)))
        self.assertEqual(c["contract_files_scanned"], int(m.group(2)))

        vis = _run(["python3", "scripts/frontmatter_visibility.py"])
        v = dict(re.findall(r"(\w+)=(\d+)", vis.stdout))
        self.assertEqual(c["frontmatter_truncation_hidden"], int(v["truncation_hidden"]))

    def test_debt_is_named_not_hidden_behind_a_pass(self):
        """74 dangling exemplars is a known ratchet. `clean` must say false and
        `debt` must name the number — a green here would mean the debt vanished
        or the tool stopped looking."""
        self.assertGreater(self.out["surfaces"]["counts"]["dangling_great_example"], 0)
        self.assertIs(self.out["clean"], False)
        self.assertEqual(self.out["debt"]["dangling_great_example"],
                         self.out["surfaces"]["counts"]["dangling_great_example"])

    def test_a_scanner_whose_shape_moved_is_a_refusal_not_a_zero(self):
        quiet = types.SimpleNamespace(main=lambda argv=None: 0)   # prints nothing
        orig = ST._load_script
        ST._load_script = lambda root, name: quiet
        try:
            out = ST.asset_hygiene(REPO, {})
        finally:
            ST._load_script = orig
        self.assertIs(out["ran"], False)
        self.assertIn("counts_unreadable", out.get("reason", ""))
        self.assertIs(out["clean"], False)

    def test_a_scoped_path_outside_the_repo_is_refused(self):
        out = ST.asset_hygiene(REPO, {"scope": "/etc"})
        self.assertIs(out["surfaces"]["contract"]["ran"], False)
        self.assertIn("scope_unusable", out["surfaces"]["contract"]["reason"])


class VerdictTests(unittest.TestCase):
    def test_repo_relative_paths_resolve_against_the_repo(self):
        """In-process handlers otherwise resolve against whatever cwd the agent
        process has, and report missing files that are sitting in the repo."""
        v = ST.verdict(REPO, {"check": "paired_runs",
                              "argv": ["examples/fixtures/paired-runs/valid_pair.jsonl"]})
        self.assertIs(v["ran"], True, v)
        self.assertIs(v["clean"], True, v)

    def test_a_red_fixture_reads_as_debt_not_failure(self):
        v = ST.verdict(REPO, {"check": "paired_runs",
                              "argv": ["examples/fixtures/paired-runs/two_variables.jsonl"]})
        self.assertIs(v["ran"], True, "the ledger was adjudicated")
        self.assertIs(v["clean"], False, "and it found the defect")
        self.assertEqual(v["exit_code"], 1)

    def test_topology_expect_assertions_travel_with_the_call(self):
        loop = "capabilities/loops/adversarial-agent-orchestration.md"
        clean = ST.verdict(REPO, {"check": "topology", "argv": ["validate", loop]})
        self.assertIs(clean["clean"], True, clean)
        plant = ST.verdict(REPO, {"check": "topology",
                                  "argv": ["validate", loop, "--mutate", "cycle",
                                           "--expect", "cycle_at"]})
        self.assertIs(plant["clean"], True, "expected mutation, so still green")
        naked = ST.verdict(REPO, {"check": "topology",
                                  "argv": ["validate", loop, "--mutate", "cycle"]})
        self.assertIs(naked["clean"], False, "un-expected cycle must go red")

    def test_a_guard_firing_is_visible_and_named(self):
        v = ST.verdict(REPO, {"check": "lifecycle",
                              "argv": ["plan", "--example", "--now", "2026-09-02",
                                       "--plant", "revocation"]})
        self.assertIs(v["ran"], True, v)
        self.assertIs(v["clean"], False)
        self.assertEqual(v["exit_code"], 2)
        self.assertIn("revocation", v["text"])

    def test_a_true_refusal_names_what_the_module_said(self):
        """Empty stdout + exit 2 = the module never got to judge. The reason must
        carry its own words, not a bare `exit_code_2`."""
        v = ST.verdict(REPO, {"check": "lifecycle",
                              "argv": ["plan", "--assets",
                                       ".context/definitely-missing.json",
                                       "--now", "2026-09-02"]})
        self.assertIs(v["ran"], False, v)
        self.assertTrue(v["reason"].startswith("assets_unreadable"), v["reason"])
        self.assertEqual(v["exit_code"], 2)

    def test_identity_stamp_never_writes(self):
        """`acceptance_identity` has a `--stamp` that writes a file. This tool
        must not: it goes through `evaluate()`, never `main()`. The record lives
        in the repo's gitignored `.context/` so the path guard accepts it, and
        the assertion is that nothing appears beside it or in the cwd."""
        record = {
            "asset_id": "surface-tools-self-test", "verdict": "pass",
            "executed_by": {"model": "openrouter/anthropic/claude-opus-4",
                            "model_version": "4-20260115", "process_id": "pid-111"},
            "harness_ref": {"harness_id": "hA-01", "config_hash": "a" * 64},
            "verifier": {"model": "openrouter/openai/gpt-5-codex",
                         "process_id": "pid-222", "harness_id": "hB-04"},
        }
        ctx = REPO_ROOT / ".context"
        ctx.mkdir(exist_ok=True)
        before = sorted(p.name for p in ctx.iterdir())
        p = ctx / "_identity_probe_record.json"
        p.write_text(json.dumps(record), encoding="utf-8")
        self.addCleanup(p.unlink)
        expect = sorted(before + [p.name])     # the record itself is allowed
        with tempfile.TemporaryDirectory() as td:
            cwd = os.getcwd()
            os.chdir(td)                      # prove the process cwd is irrelevant
            try:
                v = ST.verdict(REPO, {"check": "acceptance_identity",
                                      "argv": [str(p.relative_to(REPO_ROOT))]})
            finally:
                os.chdir(cwd)
            self.assertEqual(list(Path(td).iterdir()), [], "wrote nothing into cwd")
        self.assertIs(v["ran"], True, v)
        self.assertEqual(v["data"]["stamp"]["externality_basis"],
                         ["different_process", "different_model_family",
                          "different_harness"])
        self.assertIs(v["clean"], True, "verdicts are clean; the caller judges")
        self.assertEqual(sorted(q.name for q in ctx.iterdir()), expect,
                         "no *_identity.json appeared beside the record")

    def test_self_verification_is_refused_through_the_surface(self):
        record = {"executed_by": {"model": "gpt-5", "model_version": "1",
                                  "process_id": "same-pid"},
                  "harness_ref": {"harness_id": "h1", "config_hash": "b" * 64},
                  "verifier": {"model": "gpt-5", "process_id": "same-pid",
                               "harness_id": "h1"}}
        p = REPO_ROOT / ".context" / "_identity_probe_self.json"
        p.write_text(json.dumps(record), encoding="utf-8")
        self.addCleanup(p.unlink)
        v = ST.verdict(REPO, {"check": "acceptance_identity",
                             "argv": [str(p.relative_to(REPO_ROOT))]})
        self.assertTrue(any("self_verification" in x for x in v["data"]["refusals"]),
                        v["data"])

    def test_paths_outside_the_repo_are_refused_without_reading(self):
        v = ST.verdict(REPO, {"check": "lifecycle",
                              "argv": ["plan", "--assets", "/etc/hosts",
                                       "--now", "2026-09-02"]})
        self.assertIs(v["ran"], False)
        self.assertTrue(v["reason"].startswith("path_outside_repo"), v["reason"])
        self.assertNotIn("root:", json.dumps(v))

    def test_unknown_check_names_the_alternatives(self):
        v = ST.verdict(REPO, {"check": "vibes"})
        self.assertIs(v["ran"], False)
        self.assertIn("unknown_check:vibes", v["reason"])
        self.assertEqual(set(v["checks"]), set(ST.CHECKS))


if __name__ == "__main__":
    unittest.main()
