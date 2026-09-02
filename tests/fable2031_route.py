"""Fable 5.1 route tests: gated projection, byte-preserving writes, ladder dormancy."""
from __future__ import annotations

import difflib
import hashlib
import json
import os
import shutil
import tempfile
import unittest
from pathlib import Path
import sys

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))
FIX = REPO_ROOT / "tests" / "fixtures" / "fable2031"

import rig_capabilities.model_route as mod  # noqa: E402
from rig_capabilities.model_route import (  # noqa: E402
    FABLE_DEPLOYMENT, FABLE_MODEL_ID, FABLE_PROMOTION_GATE, RouteGateError,
    apply, audit_fallback_ladders, audit_forced_tool_choice, gate_fable_dormant, plan)

ROUTES = FIX / "routes"
_NAMES = {"registry": "model_registry.yaml",
          "hermes": "config.yaml",
          "litellm": "litellm.yaml"}
# Mirrors the OMP designer binding shape; expected lines are computed, not hardcoded.
OMP_FIXTURE = """\
extensions:
  - rig
modelRoles:
  default: openai-codex/gpt-5.6-terra
  slow: anthropic/claude-opus-4-8
  designer: anthropic/claude-fable-5
modelTags:
  designer:
    name: claude-fable-5
task:
  agentModelOverrides:
    scout: rig-256gb-qwen38/qwen3.8-27b
    designer: anthropic/claude-fable-5:high
enabledModels:
  - anthropic/claude-fable-5
"""
_LINES = OMP_FIXTURE.split("\n")
ROLE_LINE = _LINES.index("  designer: anthropic/claude-fable-5") + 1
OVERRIDE_LINE = _LINES.index("    designer: anthropic/claude-fable-5:high") + 1
MAX_TOKENS = mod.FABLE_MAX_OUTPUT


class _Repo:
    """Stand-in for catalog.Repo — this module only ever wants `.root`."""

    def __init__(self, root: Path) -> None:
        self.root = root


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _ops(before: str, after: str) -> list[tuple[str, list[str], list[str]]]:
    """(tag, before_lines, after_lines) for every non-'equal' region."""
    a, b = before.split("\n"), after.split("\n")
    sm = difflib.SequenceMatcher(a=a, b=b, autojunk=False)
    return [(tag, a[i1:i2], b[j1:j2])
            for tag, i1, i2, j1, j2 in sm.get_opcodes() if tag != "equal"]


def _planted_ladder() -> str:
    """The clean fixture with rig-fable51 injected into the fallbacks ladder."""
    return (ROUTES / "litellm.yaml").read_text().replace(
        "  fallbacks:\n    - rig-local-first:",
        f"  fallbacks:\n    - rig-local-first:\n        - {FABLE_DEPLOYMENT}", 1)


class ModelRouteTests(unittest.TestCase):
    """Fixture-only: every target is a tmpdir copy; the live files are never touched."""

    def setUp(self) -> None:
        self._saved = {k: os.environ.get(k)
                       for k in (mod.ROUTES_ENV, mod.PROOF_ENV, "RIG_OMP_CONFIG")}
        self.tmp = Path(tempfile.mkdtemp(prefix="f31route-"))
        self.routes = self.tmp / "routes"
        shutil.copytree(ROUTES, self.routes)
        self.proof = self.tmp / "proof"
        self.proof.mkdir()
        self.omp = self.tmp / "omp-config.yml"
        self.omp.write_text(OMP_FIXTURE, encoding="utf-8")
        os.environ[mod.ROUTES_ENV] = str(self.routes)
        os.environ[mod.PROOF_ENV] = str(self.proof)
        os.environ["RIG_OMP_CONFIG"] = str(self.omp)
        self.repo = _Repo(self.tmp)

    def tearDown(self) -> None:
        for key, val in self._saved.items():
            if val is None:
                os.environ.pop(key, None)
            else:
                os.environ[key] = val
        for path in self.routes.glob("*"):
            path.chmod(0o644)
        shutil.rmtree(self.tmp, ignore_errors=True)

    # -- helpers ----------------------------------------------------------
    def target(self, name: str) -> Path:
        return self.routes / _NAMES[name]

    def snapshot(self) -> dict[str, str]:
        return {n: _sha(self.target(n)) for n in _NAMES}

    def approve(self, run_id: str = "gd-route-1", *, cap=25.0,
                action="route-projection", status="APPROVED") -> None:
        (self.proof / f"gate-d-{run_id}.json").write_text(
            json.dumps({"status": status, "action": action,
                        "max_budget_usd": cap}), encoding="utf-8")

    def backups(self) -> list[Path]:
        return sorted(p for p in self.routes.iterdir() if ".bak-" in p.name)

    # -- plan -------------------------------------------------------------
    def test_plan_writes_nothing_and_discloses_ungoverned_route(self) -> None:
        before = {p: (_sha(p), p.stat().st_mtime_ns)
                  for p in sorted(self.routes.iterdir())}
        before_omp = (_sha(self.omp), self.omp.stat().st_mtime_ns)
        report = plan(self.repo)
        self.assertTrue(report["dry_run"])
        self.assertFalse(report["writes"])
        self.assertEqual(len(report["targets"]), 3)
        self.assertEqual(report["promotion"]["state"], "DORMANT")
        self.assertFalse(report["promotion"]["auto_fallback_to_earlier_family"])
        self.assertEqual(report["promotion_gate"], FABLE_PROMOTION_GATE)
        for path in sorted(self.routes.iterdir()):
            self.assertEqual((_sha(path), path.stat().st_mtime_ns), before[path],
                             f"plan() mutated {path.name}")
        self.assertEqual((_sha(self.omp), self.omp.stat().st_mtime_ns), before_omp,
                         "plan() must not edit the OMP binding")
        ungov = report["ungoverned_route_detected"]
        self.assertTrue(ungov["detected"])
        self.assertFalse(ungov["file_edited"])
        self.assertIn("gate-d", ungov["gate_d_followup"].lower().replace("_", "-"))
        self.assertIn("three route registries", ungov["scope"])
        by_path = {b["key_path"]: b for b in ungov["bindings"]}
        self.assertEqual(sorted(by_path),
                         ["modelRoles.designer",
                          "task.agentModelOverrides.designer"])
        self.assertEqual(by_path["modelRoles.designer"]["line"], ROLE_LINE)
        self.assertEqual(by_path["task.agentModelOverrides.designer"]["line"],
                         OVERRIDE_LINE)
        for binding in ungov["bindings"]:
            self.assertTrue(binding["fable_family"])
            self.assertIn("claude-fable-5", binding["value"])

    def test_plan_survives_a_missing_target_and_reports_it_blocked(self) -> None:
        self.target("litellm").unlink()
        report = plan(self.repo)
        self.assertIn("litellm:target_missing", report["blocked"])
        self.assertFalse(report["ok"])
        self.assertEqual(len(report["targets"]), 3)

    def test_plan_declares_the_starved_512_fix(self) -> None:
        report = plan(self.repo)
        self.assertEqual(report["hermes_starvation_fix"]["rig-fable5.max_tokens"],
                         [512, MAX_TOKENS])

    # -- apply: refusals --------------------------------------------------
    def test_apply_without_gate_d_writes_nothing(self) -> None:
        before = self.snapshot()
        with self.assertRaises(RouteGateError) as ctx:
            apply(self.repo, gate_d_run_id="gd-absent", max_budget_usd=10)
        self.assertIn("gate_d_required", str(ctx.exception))
        self.assertEqual(self.snapshot(), before)
        self.assertEqual(self.backups(), [])

    def test_apply_rejects_wrong_action_pending_status_and_overspend(self) -> None:
        before = self.snapshot()
        self.approve("gd-a", action="cross-harness-install")
        with self.assertRaises(RouteGateError) as ctx:
            apply(self.repo, gate_d_run_id="gd-a", max_budget_usd=10)
        self.assertIn("gate_d_action_mismatch", str(ctx.exception))

        self.approve("gd-p", status="PENDING")
        with self.assertRaises(RouteGateError) as ctx:
            apply(self.repo, gate_d_run_id="gd-p", max_budget_usd=10)
        self.assertIn("gate_d_required", str(ctx.exception))

        self.approve("gd-cap", cap=5.0)
        with self.assertRaises(RouteGateError) as ctx:
            apply(self.repo, gate_d_run_id="gd-cap", max_budget_usd=9.0)
        self.assertIn("budget_exceeds_gate_d_cap", str(ctx.exception))
        self.assertEqual(self.snapshot(), before)
        self.assertEqual(self.backups(), [])

    def test_apply_refuses_unwritable_target_before_any_write(self) -> None:
        self.approve()
        before = self.snapshot()
        self.target("registry").chmod(0o444)
        with self.assertRaises(RouteGateError) as ctx:
            apply(self.repo, gate_d_run_id="gd-route-1", max_budget_usd=10)
        self.assertIn("target_unwritable:registry", str(ctx.exception))
        self.assertEqual(self.snapshot(), before)
        self.assertEqual(self.backups(), [])

    def test_apply_aborts_on_stale_precondition_hash(self) -> None:
        self.approve()
        before = self.snapshot()
        with self.assertRaises(RouteGateError) as ctx:
            apply(self.repo, gate_d_run_id="gd-route-1", max_budget_usd=10,
                  expected_hashes={"registry": "0" * 64})
        self.assertIn("stale_precondition:registry", str(ctx.exception))
        self.assertEqual(self.snapshot(), before)
        self.assertEqual(self.backups(), [])

    # -- apply: the happy path -------------------------------------------
    def test_apply_writes_three_targets_with_backups(self) -> None:
        self.approve()
        report = apply(self.repo, gate_d_run_id="gd-route-1", max_budget_usd=10)
        self.assertTrue(report["ok"])
        self.assertFalse(report["dry_run"])
        self.assertEqual(sorted(report["applied"]), ["hermes", "litellm", "registry"])
        self.assertEqual(report["gate_d"]["requested_budget_usd"], 10)
        made = self.backups()
        self.assertEqual(len(made), 3)
        for bak in made:
            self.assertGreater(bak.stat().st_size, 0)
            self.assertNotIn(FABLE_DEPLOYMENT, bak.read_text())
        reg = self.target("registry").read_text()
        for probe in (f"\n  {FABLE_MODEL_ID}:\n",
                      f"promotion_gate: {FABLE_PROMOTION_GATE}",
                      "    default: false",
                      "    context_window: 1000000",
                      "    max_output_tokens: 128000",
                      "    effort: high",
                      "cost_per_mtok: { input: 10.0, output: 50.0 }"):
            self.assertIn(probe, reg)
        her = self.target("hermes").read_text()
        self.assertIn(f"\n  {FABLE_DEPLOYMENT}:\n", her)
        self.assertNotIn("max_tokens: 512", her)
        self.assertEqual(her.count(f"max_tokens: {MAX_TOKENS}"), 2)
        self.assertIn(f"default_model: anthropic/{FABLE_MODEL_ID}", her)
        lit = self.target("litellm").read_text()
        self.assertIn(f"  - model_name: {FABLE_DEPLOYMENT}\n", lit)
        self.assertIn(f"      model: anthropic/{FABLE_MODEL_ID}\n", lit)
        self.assertEqual(lit.count(FABLE_DEPLOYMENT), 1)
        self.assertTrue(report["fallback_audit"]["ok"])
        self.assertEqual(report["promotion"]["state"], "DORMANT")
        # re-apply is a no-op, not a duplicated block
        again = apply(self.repo, gate_d_run_id="gd-route-1", max_budget_usd=10)
        self.assertEqual(sorted(again["unchanged"]), ["hermes", "litellm", "registry"])
        self.assertEqual(again["applied"], [])
        self.assertEqual(self.target("registry").read_text(), reg)
        self.assertEqual(self.target("hermes").read_text(), her)

    def test_apply_leaves_unrelated_lines_byte_identical(self) -> None:
        self.approve()
        before = {n: self.target(n).read_text() for n in _NAMES}
        apply(self.repo, gate_d_run_id="gd-route-1", max_budget_usd=10)
        allowed_replace = {
            "registry": [],
            "litellm": [],
            "hermes": [(["        max_tokens: 512"], ["        max_tokens: 128000"])],
        }
        for name, text in before.items():
            ops = _ops(text, self.target(name).read_text())
            self.assertTrue(ops, f"{name}: expected a change")
            for tag, olds, news in ops:
                self.assertIn(tag, ("insert", "replace"),
                              f"{name}: {tag} drops original lines")
                if tag == "insert":
                    self.assertEqual(olds, [], f"{name}: insert removed {olds}")
                else:
                    self.assertIn((olds, news), allowed_replace[name],
                                  f"{name}: unexpected replacement {olds} -> {news}")
        lit = self.target("litellm").read_text()
        for probe in ("  routing_strategy: simple-shuffle",
                      "litellm_settings:\n  drop_params: true",
                      "        - rig-kimi\n  context_window_fallbacks:",
                      "      model: openrouter/moonshotai/kimi-k3"):
            self.assertIn(probe, lit)
        her = self.target("hermes").read_text()
        for probe in ("  - browser", "  max_turns: 60", "_config_version: 39",
                      "      anthropic/claude-opus-5:", "        max_tokens: 4096",
                      "  timezone: America/Denver"):
            self.assertIn(probe, her)
        reg = self.target("registry").read_text()
        for probe in ("  blackwell-daily:", "fable_training_candidates:", "      size: 27B",
                      "    measured_stream_decode_tokens_per_second_median: 208.20"):
            self.assertIn(probe, reg)

    def test_apply_restores_every_backup_on_mid_transaction_failure(self) -> None:
        self.approve()
        before = self.snapshot()
        original = mod._atomic_write
        calls = {"n": 0}

        def flaky(path, text):
            calls["n"] += 1
            if calls["n"] == 2:
                raise OSError("planted write failure")
            return original(path, text)

        mod._atomic_write = flaky
        try:
            with self.assertRaises(RouteGateError) as ctx:
                apply(self.repo, gate_d_run_id="gd-route-1", max_budget_usd=10)
        finally:
            mod._atomic_write = original
        self.assertIn("transaction_failed_restored", str(ctx.exception))
        self.assertEqual(calls["n"], 2, "the second write is where it failed")
        self.assertEqual(self.snapshot(), before, "every target must be restored")
        made = self.backups()
        self.assertEqual(len(made), 2,
                         "a backup precedes each write, including the one that failed")
        names = [bak.name.split(".bak-")[0] for bak in made]
        self.assertEqual(names, ["config.yaml", "model_registry.yaml"])
        for bak in made:
            stem = bak.name.split(".bak-")[0]
            self.assertEqual(bak.read_text(), (self.routes / stem).read_text(),
                             f"{stem}: restored file must match its backup byte-for-byte")


    # -- fallback ladders -------------------------------------------------
    def test_audit_fallback_ladders_green_on_clean_fixture(self) -> None:
        report = audit_fallback_ladders(ROUTES / "litellm.yaml")
        self.assertTrue(report["ok"], report["reasons"])
        self.assertFalse(report["governance_incident"])
        self.assertEqual(sorted(c["chain"] for c in report["chains"]),
                         ["router_settings.context_window_fallbacks",
                          "router_settings.fallbacks"])
        for chain in report["chains"]:
            self.assertIn("rig-kimi", chain["aliases"])
            self.assertEqual(chain["deployment_hits"], [])
            self.assertEqual(chain["resolved_model_hits"], [])
        self.assertEqual(report["alias_models"]["rig-anthropic"],
                         "anthropic/claude-opus-4-6")

    def test_audit_red_when_the_deployment_alias_enters_a_chain(self) -> None:
        path = self.routes / "litellm.yaml"
        planted = _planted_ladder()
        self.assertNotEqual(planted, path.read_text())
        path.write_text(planted, encoding="utf-8")
        report = audit_fallback_ladders(path)
        self.assertFalse(report["ok"])
        self.assertTrue(report["governance_incident"])
        self.assertIn("fallbacks:deployment_alias_reachable:rig-fable51",
                      report["reasons"])
        fb = [c for c in report["chains"] if c["chain"].endswith(".fallbacks")][0]
        self.assertEqual(fb["deployment_hits"], [FABLE_DEPLOYMENT])

    def test_audit_red_when_an_alias_resolves_through_litellm_params_model(self) -> None:
        path = self.routes / "litellm.yaml"
        text = path.read_text()
        planted = text.replace(
            "router_settings:",
            "  - model_name: rig-shadow\n"
            "    litellm_params:\n"
            f"      model: anthropic/{FABLE_MODEL_ID}\n"
            "      api_key: os.environ/ANTHROPIC_API_KEY\n"
            "      timeout: 180\n\n"
            "router_settings:", 1)
        planted = planted.replace(
            "  context_window_fallbacks:\n    - rig-local-first:",
            "  context_window_fallbacks:\n    - rig-local-first:\n"
            "        - rig-shadow", 1)
        path.write_text(planted, encoding="utf-8")
        report = audit_fallback_ladders(path)
        self.assertFalse(report["ok"])
        self.assertNotIn("context_window_fallbacks:deployment_alias_reachable:rig-fable51",
                         report["reasons"], "rig-shadow is not the deployment alias")
        self.assertIn("context_window_fallbacks:alias_resolves_to_fable:rig-shadow",
                      report["reasons"])
        self.assertEqual(report["alias_models"].get("rig-shadow"),
                         f"anthropic/{FABLE_MODEL_ID}")

    def test_audit_reports_missing_config_as_red_never_a_pass(self) -> None:
        report = audit_fallback_ladders(self.routes / "nope.yaml")
        self.assertFalse(report["ok"])
        self.assertFalse(report["exists"])
        self.assertTrue(report["reasons"][0].startswith("litellm_config_missing"))

    # -- the hermetic gate ------------------------------------------------
    def test_gate_fable_dormant_green_then_red_on_planted_copy(self) -> None:
        ok, detail = gate_fable_dormant(_Repo(REPO_ROOT))
        self.assertTrue(ok, detail)
        self.assertIn("absent from", detail)
        planted = self.tmp / "plant" / "tests" / "fixtures" / "fable2031" / "routes"
        planted.mkdir(parents=True)
        (planted / "litellm.yaml").write_text(_planted_ladder(), encoding="utf-8")
        bad, reason = gate_fable_dormant(_Repo(self.tmp / "plant"))
        self.assertFalse(bad)
        self.assertIn("deployment_alias_reachable", reason)
        missing, why = gate_fable_dormant(_Repo(self.tmp / "nothing-here"))
        self.assertFalse(missing)
        self.assertIn("fixture_missing", why)

    def test_gate_accepts_path_and_str_without_reading_filesystem_root(self) -> None:
        ok_path, detail = gate_fable_dormant(REPO_ROOT)
        self.assertTrue(ok_path, detail)
        ok_str, detail_str = gate_fable_dormant(str(REPO_ROOT))
        self.assertTrue(ok_str, detail_str)

    def test_gate_reads_only_the_fixture_never_live_config(self) -> None:
        red = self.tmp / "live"
        red.mkdir()
        (red / "litellm.yaml").write_text(_planted_ladder(), encoding="utf-8")
        os.environ[mod.ROUTES_ENV] = str(red)
        ok, detail = gate_fable_dormant(_Repo(REPO_ROOT))
        self.assertTrue(ok, "the gate must stay green on the fixture")
        self.assertFalse(audit_fallback_ladders()["ok"],
                         "the same red file is caught when read live")

    # -- forced tool_choice ----------------------------------------------
    def test_forced_tool_choice_blocks_a_fable_harness(self) -> None:
        root = self.tmp / "harness"
        root.mkdir()
        worker = root / "worker.yaml"
        worker.write_text("model: anthropic/claude-fable-5-1\n"
                          "tool_choice: {type: tool, name: send_email}\n",
                          encoding="utf-8")
        report = audit_forced_tool_choice([root])
        self.assertFalse(report["ok"])
        self.assertTrue(report["promotion_blocked"])
        self.assertEqual(report["fable_files"], 1)
        self.assertEqual(report["forced_tool_choice"][0]["line"], 2)
        worker.write_text("model: anthropic/claude-fable-5-1\n"
                          "tool_choice: auto\n"
                          "tool_choice: none\n", encoding="utf-8")
        self.assertTrue(audit_forced_tool_choice([root])["ok"])
        (root / "opus.yaml").write_text("model: anthropic/claude-opus-5\n"
                                        "tool_choice: required\n", encoding="utf-8")
        self.assertTrue(audit_forced_tool_choice([root])["ok"],
                        "not a reachable Fable harness")

    # -- frozen contract --------------------------------------------------
    def test_frozen_constants_and_untouched_surfaces(self) -> None:
        self.assertEqual(mod.FABLE_MODEL_ID, "claude-fable-5-1")
        self.assertEqual(mod.FABLE_DEPLOYMENT, "rig-fable51")
        self.assertEqual(mod.FABLE_CONTEXT, 1000000)
        self.assertEqual(mod.FABLE_MAX_OUTPUT, 128000)
        self.assertEqual(mod.FABLE_EFFORT, "high")
        self.assertEqual((mod.FABLE_COST_IN, mod.FABLE_COST_OUT), (10.0, 50.0))
        self.assertEqual(mod.FABLE_PROMOTION_GATE,
                         "DORMANT_PER_STUDIO_UNTIL_E_STAGE_LOWER_THAN_OPUS5")
        report = plan(self.repo)
        blob = json.dumps(report["targets"])
        for path in ("~/.claude/settings.json",
                     "~/.rig/lobe-gateway/rig_lobe_gateway.py",
                     "~/.rig/config/omp-flash-default.yml",
                     "~/.rig/route-table.json"):
            self.assertIn(path, report["untouched"])
            self.assertNotIn(path, blob)

    def test_verify_projection_reflects_the_dormant_state(self) -> None:
        before = mod.verify_projection(self.repo)
        self.assertFalse(before["ok"])
        self.assertFalse(before["checks"]["litellm_deployment_present"])
        self.assertTrue(before["checks"]["fallback_ladders_clean"])
        self.approve()
        apply(self.repo, gate_d_run_id="gd-route-1", max_budget_usd=10)
        after = mod.verify(self.repo)
        self.assertTrue(after["ok"], after["checks"])
        self.assertEqual(after["promotion_state"], "DORMANT")
        self.assertTrue(after["checks"]["registry_promotion_gate_dormant"])
        self.assertTrue(after["checks"]["hermes_starvation_fixed"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
