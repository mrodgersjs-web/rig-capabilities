"""Behavioral checks for the read-only mission composer."""
import json
import hashlib
import shutil
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from subprocess import CompletedProcess

from rig_capabilities.mission import compose, validate_packet
from rig_capabilities import mission


class MissionCompositionTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        redactor = self.root / "capabilities/hooks/redact_state.py"
        redactor.parent.mkdir(parents=True)
        shutil.copyfile(Path(mission.__file__).resolve().parents[1] /
                        "capabilities/hooks/redact_state.py", redactor)
        for name in ("rig-agent.toml", "voltagent-python-pro.toml",
                     "voltagent-code-reviewer.toml", "when-shipping-code/SKILL.md"):
            p = self.root / name
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text(name, encoding="utf-8")
        self.assets = [
            self.asset("rig-agent.toml", "agent", "Generic agent router and meta-agent", "codex-agents"),
            self.asset("voltagent-python-pro.toml", "agent", "Python implementation and debugging", "codex-agents"),
            self.asset("voltagent-code-reviewer.toml", "agent", "Independent code review", "codex-agents"),
            self.asset("when-shipping-code/SKILL.md", "skill", "Build debug test and review software", "canonical"),
        ]

    def asset(self, path, kind, description, source):
        return {"id": Path(path).name, "kind": kind, "source": source,
                "path": path, "abs_path": str(self.root / path),
                "name": Path(path).stem, "description": description}

    def test_three_tiers_and_no_execution(self):
        packet = compose("Fix the Python parser bug", "codex", self.root,
                         self.assets, {"prompts": []}, lambda _: {"package_hash": "sha256:abc", "retrieved_items": []})
        self.assertEqual(packet["schema"], "rig.mission.v1")
        self.assertEqual(packet["agent_stack"]["meta"]["asset"]["id"], "rig-agent.toml")
        self.assertEqual(packet["agent_stack"]["agent"]["asset"]["id"], "voltagent-python-pro.toml")
        self.assertEqual(packet["agent_stack"]["subagents"][0]["asset"]["id"], "voltagent-code-reviewer.toml")
        self.assertTrue(packet["agent_stack"]["subagents"][0]["read_only"])
        self.assertFalse(packet["execution"]["authorized"])
        self.assertEqual(packet["prompt_stack"]["task"]["status"], "missing")
        self.assertEqual(validate_packet(packet, self.root, self.assets), [])

    def test_memory_failure_never_falls_back(self):
        def broken(_):
            raise TimeoutError("unavailable")
        packet = compose("Fix the Python parser bug", "codex", self.root,
                         self.assets, {"prompts": []}, broken)
        self.assertEqual(packet["memory"]["status"], "degraded")
        self.assertFalse(packet["memory"]["fallback_used"])
        self.assertEqual(packet["memory"]["references"], [])

    def test_draft_prompt_cannot_be_called_calibrated(self):
        p = self.root / "draft.md"
        p.write_text("Draft task prompt", encoding="utf-8")
        registry = {"prompts": [{"id": "python-fix", "task": "Fix Python parser bug",
                                 "triggers": ["Python parser"], "status": "draft",
                                 "path": "draft.md", "version": 1}]}
        packet = compose("Fix the Python parser bug", "codex", self.root,
                         self.assets, registry, lambda _: {"package_hash": "sha256:abc", "retrieved_items": []})
        self.assertEqual(packet["prompt_stack"]["task"]["status"], "draft")
        self.assertIn("draft_prompt", packet["blocks"])

    def test_asset_drift_fails_validation(self):
        packet = compose("Fix the Python parser bug", "codex", self.root,
                         self.assets, {"prompts": []}, lambda _: {"package_hash": "sha256:abc", "retrieved_items": []})
        (self.root / "voltagent-python-pro.toml").write_text("mutated", encoding="utf-8")
        self.assertTrue(any(x.startswith("asset_drift:") for x in validate_packet(packet, self.root, self.assets)))

    def test_ambiguous_or_unsupported_abstains(self):
        packet = compose("Do the thing", "codex", self.root, self.assets,
                         {"prompts": []}, lambda _: {"package_hash": "sha256:abc", "retrieved_items": []})
        self.assertEqual(packet["status"], "abstain")
        self.assertEqual(validate_packet(packet, self.root, self.assets), [])
        unsupported = compose("Fix the Python parser bug", "aside", self.root,
                              self.assets, {"prompts": []}, lambda _: {"package_hash": "sha256:abc", "retrieved_items": []})
        self.assertEqual(unsupported["status"], "abstain")

    def test_vague_intent_does_not_name_an_incidental_agent(self):
        for intent in ("Make it better", "Build something useful"):
            with self.subTest(intent=intent):
                packet = compose(intent, "codex", self.root, self.assets,
                                 {"prompts": []}, lambda _: {"package_hash": "sha256:abc"})
                self.assertEqual(packet["status"], "abstain")
                self.assertIsNone(packet["agent_stack"]["agent"])
                self.assertEqual(packet["candidates"], [])

    def test_technology_name_beats_generic_migration_role(self):
        from rig_capabilities.mission import _rank
        agents = [
            {"id": "voltagent-postgres-pro.toml", "name": "voltagent-postgres-pro", "description": "", "source": "codex-agents"},
            {"id": "codex-refactor-migration-engineer.toml", "name": "codex-refactor-migration-engineer", "description": "", "source": "codex-agents"},
        ]
        self.assertEqual(_rank("Design a PostgreSQL migration with rollback", agents)[0][1]["id"],
                         "voltagent-postgres-pro.toml")

    def test_api_task_does_not_select_smart_contract_specialist(self):
        from rig_capabilities.mission import _rank
        agents = [
            {"id": "agency-api-tester.toml", "name": "agency-api-tester", "description": "", "source": "codex-agents"},
            {"id": "agency-solidity-smart-contract-engineer.toml",
             "name": "agency-solidity-smart-contract-engineer", "description": "", "source": "codex-agents"},
        ]
        self.assertEqual(_rank("Explain this API contract and add OpenAPI tests", agents)[0][1]["id"],
                         "agency-api-tester.toml")

    def test_child_ranking_prefers_specific_migration_and_general_python_skill(self):
        from rig_capabilities.mission import _child_skill, _rank
        cases = [
            ("when-working-with-data", "Design a PostgreSQL migration with rollback",
             [("database-migration", "Execute database migrations across ORMs"),
              ("database-migrations", "Database migrations, rollbacks and zero downtime")],
             "database-migrations"),
            ("when-shipping-code", "Write a Python migration utility for these records",
             [("python-patterns", "Pythonic idioms and patterns"),
              ("python-design-patterns", "Python design patterns"),
              ("python-packaging", "Python packaging")], "python-patterns"),
        ]
        for meta, intent, children, expected in cases:
            with self.subTest(meta=meta):
                table = self.root / f"capabilities/skills/{meta}/references/routing.md"
                table.parent.mkdir(parents=True, exist_ok=True)
                table.write_text("| Skill | Source | One-liner | Sub-skills |\n|---|---|---|---|\n" +
                                 "".join(f"| {name} | canonical | {desc} | - |\n"
                                         for name, desc in children), encoding="utf-8")
                assets = [{"id": name, "kind": "skill", "source": "canonical",
                           "path": f"{name}/SKILL.md", "name": name, "description": desc}
                          for name, desc in children]
                self.assertEqual(_rank(intent, assets)[0][1]["id"], expected)
                if meta == "when-shipping-code":
                    selected = _child_skill(intent, {"id": meta}, assets, self.root)
                    self.assertIsNotNone(selected)
                    self.assertEqual(selected["id"], expected)

    def test_unresolved_child_skill_cannot_claim_complete_candidate(self):
        packet = compose("Write Python code to parse CSV data", "codex", self.root,
                         self.assets, {"prompts": []},
                         lambda _: {"package_hash": "sha256:abc"})
        self.assertIn("child_skill_unresolved", packet["blocks"])
        self.assertEqual(packet["status"], "abstain")

    def test_child_selection_uses_declared_meta_route(self):
        from rig_capabilities.mission import _child_skill
        route = self.root / "capabilities/skills/when-working-with-data/references/routing.md"
        route.parent.mkdir(parents=True)
        route.write_text("| Skill | Source | One-liner | Sub-skills |\n"
                         "|---|---|---|---|\n"
                         "| sql-optimization-patterns | canonical | Optimize SQL joins and indexes | - |\n"
                         "| data-storytelling | canonical | Tell data stories | - |\n")
        sql = self.asset("sql-optimization-patterns/SKILL.md", "skill",
                         "Optimize SQL joins and indexes", "canonical")
        sql["id"] = "sql-optimization-patterns"
        sql["name"] = "sql-optimization-patterns"
        story = self.asset("data-storytelling/SKILL.md", "skill",
                           "Tell data stories", "canonical")
        story["id"] = "data-storytelling"
        story["name"] = "data-storytelling"
        meta = {"id": "when-working-with-data", "kind": "skill",
                "path": "capabilities/skills/when-working-with-data/SKILL.md"}
        selected = _child_skill("Optimize this SQL join", meta, [sql, story], self.root)
        self.assertEqual(selected["id"], "sql-optimization-patterns")

    def test_authentication_terms_identify_security_domain(self):
        from rig_capabilities.mission import _tokens
        self.assertIn("security", _tokens("Audit authentication middleware"))
        self.assertIn("security", _tokens("Privilege escalation in authorization"))
        self.assertIn("application", _tokens("Authentication middleware"))

    def test_second_writer_is_rejected(self):
        packet = compose("Fix the Python parser bug", "codex", self.root,
                         self.assets, {"prompts": []}, lambda _: {"package_hash": "sha256:abc", "retrieved_items": []})
        packet["agent_stack"]["subagents"][0]["read_only"] = False
        self.assertIn("writer_count_invalid", validate_packet(packet, self.root, self.assets))

    def test_memory_content_not_serialized(self):
        packet = compose("Fix the Python parser bug", "codex", self.root,
                         self.assets, {"prompts": []}, lambda _: {
                             "package_hash": "sha256:abc", "retrieved_items": [
                                 {"id": "memory-1", "status": "candidate", "content": "private memory body"}]})
        self.assertNotIn("private memory body", json.dumps(packet))
        self.assertEqual(packet["memory"]["references"][0]["status"], "candidate")

    def test_validator_rejects_rehashed_authority_flags(self):
        from rig_capabilities.mission import _canonical, _sha
        packet = compose("Fix the Python parser bug", "codex", self.root,
                         self.assets, {"prompts": []}, lambda _: {"package_hash": "sha256:abc"})
        packet["execution"]["authorized"] = True
        packet["packet_sha256"] = _sha(_canonical({k: v for k, v in packet.items() if k != "packet_sha256"}))
        self.assertIn("execution_boundary_invalid", validate_packet(packet, self.root, self.assets))

    def test_validator_rejects_uncatalogued_path_and_malformed_nesting(self):
        packet = compose("Fix the Python parser bug", "codex", self.root,
                         self.assets, {"prompts": []}, lambda _: {"package_hash": "sha256:abc"})
        packet["agent_stack"]["agent"]["asset"]["path"] = "/etc/hosts"
        self.assertTrue(any(x.startswith("asset_not_catalogued:") for x in
                            validate_packet(packet, self.root, self.assets)))
        packet["agent_stack"] = ["not a stack"]
        self.assertIn("agent_stack_invalid", validate_packet(packet, self.root, self.assets))

    def test_jev_shadow_failure_is_visible_and_never_authorizes(self):
        def broken(_intent, _root):
            raise TimeoutError("offline")
        packet = compose("Fix the Python parser bug", "codex", self.root,
                         self.assets, {"prompts": []}, lambda _: {"package_hash": "sha256:abc"},
                         jev_loader=broken)
        self.assertEqual(packet["jev"]["status"], "degraded")
        self.assertIn("jev_degraded", packet["blocks"])
        self.assertFalse(packet["execution"]["authorized"])
        self.assertEqual(validate_packet(packet, self.root, self.assets), [])

    def test_catalog_drift_and_forged_jev_are_rejected(self):
        packet = compose("Fix the Python parser bug", "codex", self.root,
                         self.assets, {"prompts": []}, lambda _: {"package_hash": "sha256:abc"})
        packet["jev"] = {"status": "observed", "choice": "when-shipping-code",
                         "confidence": 1.0, "advisory": True, "enforced": False}
        self.assertIn("jev_evidence_invalid", validate_packet(packet, self.root, self.assets))
        self.assets.append(self.asset("new.toml", "agent", "New", "codex-agents"))
        self.assertIn("catalog_drift", validate_packet(packet, self.root, self.assets))

    def test_rehashed_catalogued_agent_route_swap_rejected(self):
        from rig_capabilities.mission import _canonical, _sha
        other = self.root / "agency-3d-scene-developer.toml"
        other.write_text("3D agent", encoding="utf-8")
        self.assets.append(self.asset(other.name, "agent", "3D scenes", "codex-agents"))
        packet = compose("Fix the Python parser bug", "codex", self.root,
                         self.assets, {"prompts": []}, lambda _: {"package_hash": "sha256:abc"})
        packet["agent_stack"]["agent"]["asset"] = {
            "id": other.name, "kind": "agent", "source": "codex-agents",
            "path": str(other), "sha256": _sha(other.read_bytes())}
        packet["packet_sha256"] = _sha(_canonical({k: v for k, v in packet.items()
                                                    if k != "packet_sha256"}))
        self.assertIn("route_mismatch:agent_stack", validate_packet(packet, self.root, self.assets))

    def test_forged_observed_jev_receipt_rejected(self):
        from rig_capabilities.mission import _canonical, _sha
        packet = compose("Fix the Python parser bug", "codex", self.root,
                         self.assets, {"prompts": []}, lambda _: {"package_hash": "sha256:abc"})
        packet["jev"] = {"status": "observed", "choice": "when-shipping-code",
                         "confidence": 0.9, "decision_id": 999999999, "model": "jev-1.13.0",
                         "provider": "hosted-jev", "endpoint": "https://api.typesafe.ai/v1/systemone",
                         "state_sha256": packet["intent_sha256"],
                         "intent_sha256": packet["intent_sha256"],
                         "advisory": True, "enforced": False}
        packet["packet_sha256"] = _sha(_canonical({k: v for k, v in packet.items()
                                                    if k != "packet_sha256"}))
        self.assertIn("jev_receipt_unverified", validate_packet(packet, self.root, self.assets))

    def test_hosted_loader_redacts_and_records_provider_provenance(self):
        intent = "Fix the Python parser using sk-" + "a" * 32
        sanitized = "Fix the Python parser using [REDACTED-TOKEN]"
        sha = hashlib.sha256(sanitized.encode()).hexdigest()
        response = {"verdict": "PASS", "answers": {"lane": {
            "choice": "when-shipping-code", "confidence": 0.99}},
            "decision_id": 42, "model": "jev-1.13.0", "latency_ms": 123,
            "state_sha256": sha}
        calls = []

        def run(command, **kwargs):
            calls.append((command, kwargs))
            return CompletedProcess(command, 0, stdout=sanitized if str(command[1]).endswith("redact_state.py")
                                    else json.dumps(response))

        loader = mission.hosted_jev_loader
        with patch.object(mission.subprocess, "run", side_effect=run):
            result = loader(intent, self.root)
        self.assertEqual(result["provider"], "hosted-jev")
        self.assertEqual(result["state_sha256"], sha)
        self.assertEqual(calls[1][1]["input"], sanitized)
        self.assertEqual(calls[1][1]["env"]["S1GATE_JEV_ENDPOINT"],
                         "https://api.typesafe.ai/v1/systemone")
        self.assertEqual(calls[1][1]["env"]["S1GATE_JEV_MODEL"], "jev-latest")
        self.assertNotEqual(calls[1][1]["env"].get("TYPESAFE_API_KEY"), "local")
        self.assertIn("--subject", calls[1][0])
        self.assertFalse(result["enforced"])

    def test_private_intent_defers_before_classifier_call(self):
        loader = mission.hosted_jev_loader

        def safe_only(command, **kwargs):
            self.assertTrue(str(command[1]).endswith("redact_state.py"), "Private intent reached classifier")
            return CompletedProcess(command, 0, stdout="Fix Python code for a patient medical record")

        with patch.object(mission.subprocess, "run", side_effect=safe_only) as run:
            packet = compose("Fix Python code for a patient medical record", "codex", self.root,
                             self.assets, {"prompts": []}, memory_loader=None, jev_loader=loader)
        self.assertEqual(packet["jev"]["status"], "degraded")
        self.assertIn("jev_degraded", packet["blocks"])
        self.assertEqual(run.call_count, 1)
        self.assertFalse(packet["execution"]["authorized"])

    def test_missing_redactor_never_reaches_classifier(self):
        loader = mission.hosted_jev_loader
        (self.root / "capabilities/hooks/redact_state.py").unlink()
        with patch.object(mission.subprocess, "run", return_value=CompletedProcess(
                [], 0, stdout=json.dumps({"verdict": "PASS", "answers": {"lane": {
                    "choice": "when-shipping-code", "confidence": 0.99}}, "model": "jev-1.13.0"}))) as run:
            packet = compose("Fix Python code", "codex", self.root,
                             self.assets, {"prompts": []}, memory_loader=None, jev_loader=loader)
        self.assertEqual(packet["jev"]["status"], "degraded")
        self.assertEqual(run.call_count, 0)

    def test_hosted_receipt_binds_sanitized_state_and_original_intent(self):
        from rig_capabilities import s1gate
        intent = "Fix the Python parser using sk-" + "a" * 32
        sanitized = "Fix the Python parser using [REDACTED-TOKEN]"
        intent_sha = hashlib.sha256(intent.encode()).hexdigest()
        endpoint = "https://api.typesafe.ai/v1/systemone"
        subject = f"mission.route hosted-jev {endpoint} intent-sha256:{intent_sha}"
        db = self.root / "decisions.db"
        with patch.object(s1gate, "ask", return_value={"answers": {"lane": {
                "type": "choice", "choice": "when-shipping-code", "confidence": 0.99}},
                "model": "jev-1.13.0"}), patch.object(s1gate, "CACHE_ENABLED", False):
            log = s1gate.DecisionLog(db)
            try:
                result = s1gate.evaluate(s1gate.Rubric(
                    name="mission.route", stage="plan", lane="agent-composition", description="test",
                    questions={"lane": {"type": "choice"}}, rules=[]),
                    sanitized, subject=subject, log=log, model="jev-latest")
            finally:
                log.close()
        receipt = {"status": "observed", "choice": "when-shipping-code", "confidence": 0.99,
                   "decision_id": result.decision_id, "model": "jev-1.13.0", "provider": "hosted-jev",
                   "endpoint": endpoint, "state_sha256": hashlib.sha256(sanitized.encode()).hexdigest(),
                   "intent_sha256": intent_sha, "advisory": True, "enforced": False}
        packet = compose(intent, "codex", self.root, self.assets, {"prompts": []},
                         memory_loader=None, jev_loader=lambda *_: dict(receipt))
        with patch.object(mission, "DB_PATH", db):
            self.assertEqual(validate_packet(packet, self.root, self.assets), [])
            forged = dict(receipt, model="openjev-0.1")
            self.assertFalse(mission._jev_receipt_valid(forged, intent, self.root))
            self.assertFalse(mission._jev_receipt_valid(receipt, "Fix the Python parser", self.root))

    def test_catalogued_asset_cannot_be_recast_as_meta_skill(self):
        packet = compose("Fix the Python parser bug", "codex", self.root,
                         self.assets, {"prompts": []}, lambda _: {"package_hash": "sha256:abc"})
        packet["skills"] = [packet["agent_stack"]["agent"]["asset"]]
        self.assertIn("skill_kind_invalid", validate_packet(packet, self.root, self.assets))
        packet = compose("Fix the Python parser bug", "codex", self.root,
                         self.assets, {"prompts": []}, lambda _: {"package_hash": "sha256:abc"})
        packet["agent_stack"]["meta"] = packet["agent_stack"]["agent"]
        self.assertIn("meta_agent_invalid", validate_packet(packet, self.root, self.assets))


if __name__ == "__main__":
    unittest.main()
