"""Tests for the D85 tool-selection standard: evidence records, decision table, checklist."""

from __future__ import annotations

import json
import shutil
import sys
import tempfile
import unittest
import unittest.mock
from pathlib import Path

SKILL_ROOT = Path(__file__).resolve().parent.parent / "capabilities/skills/rig-determinism-85"
sys.path.insert(0, str(SKILL_ROOT))

from tool_selection import (  # noqa: E402
    ToolSelectionBlock,
    certify_build,
    checklist_digest,
    check_build_checklist,
    derive_properties,
    select_framework,
)


def _live_inventory_sha256() -> str:
    from d85 import build_inventory

    return build_inventory("julie_synthetic")["inventory_sha256"]

CLOCK = {
    "named_consumer": "live pricing dashboard",
    "failure_mode": "stale prices breach the display SLA",
    "sla_start_latency_seconds": 15,
    "recovery_policy": "catch_up",
}
RESIDENT = {
    "resource_kind": "watched_directory",
    "resource_detail": "drops folder; react within 500ms of file creation",
}
NON_ENGINEER = {
    "maintainer": "Ops Lead",
    "maintainer_is_engineer": False,
    "expiry_date": None,
}
GRAPH = {
    "graph_shape": "cycle",
    "description": "planner -> parallel workers -> critic -> replan on critic verdict",
    "agent_count": 4,
}
REASONING = {
    "unstructured_input": "inbound email bodies",
    "deterministic_alternative": "regex over a known-sender list",
    "alternative_rejected_because": "novel senders and paraphrased intent defeat regex recall",
}


def _build(testcase, **overrides):
    tmp = tempfile.mkdtemp()
    testcase.addCleanup(shutil.rmtree, tmp, ignore_errors=True)
    diagram = Path(tmp) / "diagram.json"
    diagram.write_text(
        json.dumps({"schema_version": 2, "diagram_type": "workflow"}),
        encoding="utf-8",
    )
    base = {
        "properties": {},
        "process_id": "julie_synthetic",
        "inventory_sha256": _live_inventory_sha256(),
        "framework": "kestra_pydantic",
        "durable_system": True,
        "pydantic_models": ["Result"],
        "model_necessity_claims": ["typed agent output beats the keyword-frequency baseline on the graded replay set"],
        "archify_diagram_path": str(diagram),
        "d85_realized_pass": True,
        "orchestration_is_code": True,
    }
    base.update(overrides)
    return base, diagram


class EvidenceRecordTests(unittest.TestCase):
    def test_absent_properties_derive_false(self) -> None:
        derived = derive_properties({})
        self.assertEqual(
            derived,
            {
                "clock_critical": False,
                "resident_service": False,
                "non_engineer_surface": False,
                "multi_agent_graph": False,
                "agent_reasoning": False,
            },
        )

    def test_bare_boolean_claim_blocks(self) -> None:
        with self.assertRaises(ToolSelectionBlock) as caught:
            select_framework({"clock_critical": True})
        self.assertEqual(caught.exception.code, "TOOL_SELECTION_MALFORMED")
        self.assertIn("evidence record", caught.exception.detail)

    def test_missing_evidence_field_blocks(self) -> None:
        partial = dict(CLOCK)
        del partial["failure_mode"]
        with self.assertRaises(ToolSelectionBlock) as caught:
            select_framework({"clock_critical": partial})
        self.assertIn("missing fields", caught.exception.detail)

    def test_unknown_evidence_field_blocks(self) -> None:
        with self.assertRaises(ToolSelectionBlock) as caught:
            select_framework({"agent_reasoning": {**REASONING, "vibes": True}})
        self.assertIn("unknown fields", caught.exception.detail)

    def test_unknown_property_blocks(self) -> None:
        with self.assertRaises(ToolSelectionBlock) as caught:
            select_framework({"vibes": True})
        self.assertEqual(caught.exception.code, "TOOL_SELECTION_MALFORMED")

    def test_null_claim_blocks(self) -> None:
        with self.assertRaises(ToolSelectionBlock) as caught:
            select_framework({"resident_service": None})
        self.assertEqual(caught.exception.code, "TOOL_SELECTION_MALFORMED")

    # Lying claims: well-formed records whose evidence contradicts the claim.

    def test_loose_sla_claim_is_contradicted(self) -> None:
        lying = {**CLOCK, "sla_start_latency_seconds": 600}
        with self.assertRaises(ToolSelectionBlock) as caught:
            select_framework({"clock_critical": lying})
        self.assertIn("contradicted", caught.exception.detail)
        self.assertIn("Kestra", caught.exception.detail)

    def test_skip_on_miss_recovery_claim_is_contradicted(self) -> None:
        lying = {**CLOCK, "recovery_policy": "skip"}
        with self.assertRaises(ToolSelectionBlock) as caught:
            select_framework({"clock_critical": lying})
        self.assertIn("contradicted", caught.exception.detail)

    def test_two_agent_graph_claim_is_contradicted(self) -> None:
        lying = {**GRAPH, "agent_count": 2}
        with self.assertRaises(ToolSelectionBlock) as caught:
            select_framework({"multi_agent_graph": lying})
        self.assertIn("chain", caught.exception.detail)

    def test_engineer_maintainer_without_expiry_is_contradicted(self) -> None:
        lying = {**NON_ENGINEER, "maintainer_is_engineer": True}
        with self.assertRaises(ToolSelectionBlock) as caught:
            select_framework({"non_engineer_surface": lying})
        self.assertIn("contradicted", caught.exception.detail)

    def test_engineer_maintainer_with_expiry_passes_as_demo(self) -> None:
        demo = {**NON_ENGINEER, "maintainer_is_engineer": True, "expiry_date": "2026-12-31"}
        verdict = select_framework({"non_engineer_surface": demo})
        self.assertEqual(verdict["framework"], "flowise")

    def test_bad_expiry_date_blocks(self) -> None:
        bad = {**NON_ENGINEER, "expiry_date": "31-12-2026"}
        with self.assertRaises(ToolSelectionBlock):
            select_framework({"non_engineer_surface": bad})

    # Malformed value types: every one must raise a typed BLOCK, never TypeError.

    def test_unhashable_resource_kind_blocks_not_crash(self) -> None:
        with self.assertRaises(ToolSelectionBlock):
            select_framework({"resident_service": {**RESIDENT, "resource_kind": ["watched_directory"]}})

    def test_unhashable_graph_shape_blocks_not_crash(self) -> None:
        with self.assertRaises(ToolSelectionBlock):
            select_framework({"multi_agent_graph": {**GRAPH, "graph_shape": {"cycle": True}}})

    def test_non_string_consumer_blocks(self) -> None:
        with self.assertRaises(ToolSelectionBlock):
            select_framework({"clock_critical": {**CLOCK, "named_consumer": 42}})

    def test_properties_as_list_blocks(self) -> None:
        with self.assertRaises(ToolSelectionBlock):
            select_framework(["clock_critical"])

    def test_checklist_framework_not_in_registry_blocks(self) -> None:
        build, _ = _build(self, framework="fastapi")
        with self.assertRaises(ToolSelectionBlock) as caught:
            check_build_checklist(build)
        self.assertIn("framework", caught.exception.detail)

    def test_checklist_framework_non_string_blocks(self) -> None:
        build, _ = _build(self, framework=7)
        with self.assertRaises(ToolSelectionBlock):
            check_build_checklist(build)

    def test_checklist_durable_system_truthy_string_blocks(self) -> None:
        build, _ = _build(self, durable_system="yes")
        with self.assertRaises(ToolSelectionBlock):
            check_build_checklist(build)

    def test_checklist_pydantic_models_as_string_blocks(self) -> None:
        build, _ = _build(self, pydantic_models="Result")
        with self.assertRaises(ToolSelectionBlock):
            check_build_checklist(build)

    def test_checklist_claims_as_dict_blocks(self) -> None:
        build, _ = _build(self, model_necessity_claims={"claim": "better"})
        with self.assertRaises(ToolSelectionBlock):
            check_build_checklist(build)

    def test_checklist_diagram_path_non_string_blocks(self) -> None:
        build, _ = _build(self, archify_diagram_path=123)
        with self.assertRaises(ToolSelectionBlock):
            check_build_checklist(build)

    def test_checklist_models_list_with_empty_string_blocks(self) -> None:
        build, _ = _build(self, pydantic_models=["Result", "  "])
        with self.assertRaises(ToolSelectionBlock):
            check_build_checklist(build)


class SelectionTests(unittest.TestCase):
    def test_default_is_kestra_pydantic(self) -> None:
        verdict = select_framework({})
        self.assertEqual(verdict["framework"], "kestra_pydantic")

    def test_clock_critical_wins_over_everything(self) -> None:
        verdict = select_framework(
            {"clock_critical": CLOCK, "agent_reasoning": REASONING, "multi_agent_graph": GRAPH}
        )
        self.assertEqual(verdict["framework"], "temporal")

    def test_resident_service_is_launchd(self) -> None:
        self.assertEqual(
            select_framework({"resident_service": RESIDENT})["framework"], "launchd"
        )

    def test_keepalive_daemon_kind_is_outside_the_closed_enum(self) -> None:
        with self.assertRaises(ToolSelectionBlock) as ctx:
            select_framework(
                {"resident_service": {"resource_kind": "keepalive_daemon",
                                       "resource_detail": "KeepAlive truthy in plist"}}
            )
        self.assertIn("resident_service.resource_kind", str(ctx.exception))

    def test_non_engineer_surface_is_flowise_and_not_durable(self) -> None:
        verdict = select_framework({"non_engineer_surface": NON_ENGINEER})
        self.assertEqual(verdict["framework"], "flowise")
        self.assertFalse(verdict["d85_obligations"]["durable_admissible"])

    def test_multi_agent_graph_is_langchain(self) -> None:
        self.assertEqual(
            select_framework({"multi_agent_graph": GRAPH})["framework"], "langchain"
        )

    def test_agent_reasoning_is_orca_pydantic(self) -> None:
        self.assertEqual(
            select_framework({"agent_reasoning": REASONING})["framework"], "orca_pydantic"
        )

    def test_graph_outranks_reasoning(self) -> None:
        verdict = select_framework({"multi_agent_graph": GRAPH, "agent_reasoning": REASONING})
        self.assertEqual(verdict["framework"], "langchain")

    def test_every_verdict_carries_d85_obligations(self) -> None:
        for properties in (
            {},
            {"clock_critical": CLOCK},
            {"agent_reasoning": REASONING},
        ):
            obligations = select_framework(properties)["d85_obligations"]
            self.assertEqual(obligations["four_ratios_at_least"], 0.85)
            self.assertTrue(obligations["critical_controls_code_only"])


class ChecklistTests(unittest.TestCase):
    def test_green_build_passes_every_check(self) -> None:
        build, diagram = _build(self)
        result = check_build_checklist(build)
        self.assertTrue(all(check["pass"] for check in result["checks"]))
        self.assertEqual(result["verdict"], "CHECKLIST_PASS")
        # 8 since model_evidence_matches_classification joined the list.
        self.assertEqual(len(result["checks"]), 8)
        self.assertEqual(result["inventory_binding"], "unbound")
        self.assertIsNone(result["inventory_sha256"])

    def test_direct_api_pass_is_never_an_enforcement_verdict(self) -> None:
        build, _ = _build(self)
        result = check_build_checklist(build)
        self.assertEqual(result["verdict"], "CHECKLIST_PASS")
        self.assertEqual(result["inventory_binding"], "unbound")
        self.assertIsNone(result["inventory_sha256"])

    def test_certify_without_process_id_blocks(self) -> None:
        build, _ = _build(self)
        result = certify_build(build, None)
        self.assertEqual(result["verdict"], "CHECKLIST_BLOCK")
        self.assertEqual(result["inventory_binding"], "unbound")
        self.assertIn("binding_reason", result)

    def test_certify_process_mismatch_blocks(self) -> None:
        build, _ = _build(self)
        result = certify_build(build, "someone_elses_process")
        self.assertEqual(result["verdict"], "CHECKLIST_BLOCK")
        self.assertEqual(result["inventory_binding"], "mismatched")
        self.assertIn("binding_reason", result)

    def test_certify_binds_to_registry_inventory_hash(self) -> None:
        build, _ = _build(self)
        result = certify_build(build, "julie_synthetic")
        self.assertEqual(result["verdict"], "CHECKLIST_PASS")
        self.assertEqual(result["inventory_binding"], "bound")
        self.assertRegex(result["inventory_sha256"], r"^[0-9a-f]{64}$")

    def _certify_with_kinds(self, kind_counts, **overrides):
        """certify_build() against a stubbed authority: inventory bound, kinds dictated.

        Hermetic on purpose — the live registry's MODEL mix is not this test's subject, and
        processes that lock an external module hash differently per environment.
        """
        import d85
        import d85_gates
        import tool_selection

        build, _ = _build(self, **overrides)
        self.enterContext(
            unittest.mock.patch.object(
                d85, "build_inventory", lambda pid: {"inventory_sha256": build["inventory_sha256"]}
            )
        )
        self.enterContext(
            unittest.mock.patch.object(
                d85_gates, "classify_process", lambda pid: {"kind_counts": dict(kind_counts)}
            )
        )
        # The score is a separate gate with its own tests below; pin it green so these cases
        # measure only the model-evidence authority rule.
        self.enterContext(
            unittest.mock.patch.object(
                d85_gates, "score_process",
                lambda pid: {
                    "verdict": "REALIZED_PASS",
                    "process_id": pid,
                    "inventory_sha256": build["inventory_sha256"],
                    "ratios": {
                        "aggregate_unweighted": 1.0,
                        "aggregate_weighted": 1.0,
                        "min_path_unweighted": 1.0,
                        "min_path_weighted": 1.0,
                    },
                    "scored_operation_count": 1,
                },
            )
        )
        self.assertIs(tool_selection.certify_build, certify_build)
        return certify_build(build, build["process_id"])

    def test_zero_model_process_needs_no_model_evidence(self) -> None:
        # The cockpit_v2_vercel_deploy_v2 shape: one deterministic side effect, CODE:1 MODEL:0.
        # The default framework is kestra_pydantic, and the framework-name proxy used to demand
        # pydantic schemas plus a necessity record it can never honestly produce.
        result = self._certify_with_kinds(
            {"CODE": 1, "MODEL": 0, "MODEL_AGENT": 0, "MIXED": 0},
            pydantic_models=[],
            model_necessity_claims=[],
        )
        self.assertEqual(result["verdict"], "CHECKLIST_PASS")
        self.assertEqual(result["inventory_binding"], "bound")

    def test_zero_model_process_may_not_fabricate_model_evidence(self) -> None:
        result = self._certify_with_kinds(
            {"CODE": 1, "MODEL": 0, "MODEL_AGENT": 0, "MIXED": 0},
            pydantic_models=["Result"],
            model_necessity_claims=["a claim about work the authority says does not exist"],
        )
        self.assertEqual(result["verdict"], "CHECKLIST_BLOCK")
        failed = [c["check"] for c in result["checks"] if not c["pass"]]
        self.assertEqual(failed, ["model_evidence_matches_classification"])

    def test_hidden_model_ops_still_demand_evidence(self) -> None:
        # Empty `properties` cannot hide a MODEL op: the classification decides.
        result = self._certify_with_kinds(
            {"CODE": 3, "MODEL": 1, "MODEL_AGENT": 0, "MIXED": 0},
            properties={},
            pydantic_models=[],
            model_necessity_claims=[],
        )
        self.assertEqual(result["verdict"], "CHECKLIST_BLOCK")
        failed = [c["check"] for c in result["checks"] if not c["pass"]]
        self.assertEqual(
            failed,
            ["pydantic_models_present", "model_necessity_claims_present",
             "model_evidence_matches_classification"],
        )

    def test_one_claim_does_not_cover_many_model_ops(self) -> None:
        result = self._certify_with_kinds(
            {"CODE": 2, "MODEL": 2, "MODEL_AGENT": 1, "MIXED": 0},
            pydantic_models=["Result"],
            model_necessity_claims=["only one record for three model operations"],
        )
        self.assertEqual(result["verdict"], "CHECKLIST_BLOCK")
        failed = [c["check"] for c in result["checks"] if not c["pass"]]
        self.assertEqual(
            failed,
            ["model_necessity_claims_present", "model_evidence_matches_classification"],
        )

    def test_malformed_model_ops_argument_blocks(self) -> None:
        build, _ = _build(self)
        for bad in (True, False, -1, "1", 1.0):
            with self.subTest(model_ops=bad):
                with self.assertRaises(ToolSelectionBlock) as caught:
                    check_build_checklist(build, model_ops=bad)
                self.assertIn("model_ops must be None or an exact nonnegative int",
                              str(caught.exception))

    def test_claim_per_model_op_passes(self) -> None:
        result = self._certify_with_kinds(
            {"CODE": 2, "MODEL": 2, "MODEL_AGENT": 0, "MIXED": 0},
            pydantic_models=["Input", "Result"],
            model_necessity_claims=["record for op one", "record for op two"],
        )
        self.assertEqual(result["verdict"], "CHECKLIST_PASS")

    def test_model_properties_contradicting_zero_model_classification_blocks(self) -> None:
        result = self._certify_with_kinds(
            {"CODE": 4, "MODEL": 0, "MODEL_AGENT": 0, "MIXED": 0},
            properties={"agent_reasoning": REASONING},
            framework="orca_pydantic",
            pydantic_models=[],
            model_necessity_claims=[],
        )
        self.assertEqual(result["verdict"], "CHECKLIST_BLOCK")
        failed = [c["check"] for c in result["checks"] if not c["pass"]]
        self.assertEqual(failed, ["model_evidence_matches_classification"])

    def _certify_with_score(self, score, **overrides):
        """certify_build() with the classification stubbed CODE-only and the score dictated."""
        import d85
        import d85_gates

        build, _ = _build(self, pydantic_models=[], model_necessity_claims=[], **overrides)
        self.enterContext(
            unittest.mock.patch.object(
                d85, "build_inventory", lambda pid: {"inventory_sha256": build["inventory_sha256"]}
            )
        )
        self.enterContext(
            unittest.mock.patch.object(
                d85_gates, "classify_process",
                lambda pid: {"kind_counts": {"CODE": 1, "MODEL": 0, "MODEL_AGENT": 0, "MIXED": 0}},
            )
        )
        self.enterContext(
            unittest.mock.patch.object(d85_gates, "score_process", lambda pid: dict(score))
        )
        return build, certify_build(build, build["process_id"])

    def _passing_score(self, build, **overrides):
        score = {
            "verdict": "REALIZED_PASS",
            "process_id": build["process_id"],
            "inventory_sha256": build["inventory_sha256"],
            "ratios": {
                "aggregate_unweighted": 1.0,
                "aggregate_weighted": 1.0,
                "min_path_unweighted": 1.0,
                "min_path_weighted": 1.0,
            },
            "scored_operation_count": 1,
        }
        score.update(overrides)
        return score

    def test_declared_d85_pass_without_live_score_blocks(self) -> None:
        # The build says d85_realized_pass: true; the recomputed score says otherwise.
        build, _ = _build(self)
        blocked = self._certify_with_score(
            {"verdict": "REALIZED_BLOCK", "process_id": build["process_id"],
             "inventory_sha256": build["inventory_sha256"],
             "ratios": {"aggregate_unweighted": 0.4, "aggregate_weighted": 0.4,
                        "min_path_unweighted": 0.4, "min_path_weighted": 0.4},
             "scored_operation_count": 1},
        )[1]
        self.assertEqual(blocked["verdict"], "CHECKLIST_BLOCK")
        self.assertEqual(
            [c["check"] for c in blocked["checks"] if not c["pass"]], ["source_derived_d85"]
        )

    def test_sub_threshold_ratio_blocks(self) -> None:
        build, _ = _build(self)
        score = self._passing_score(build)
        score["ratios"]["min_path_weighted"] = 0.84
        blocked = self._certify_with_score(score)[1]
        self.assertEqual(blocked["verdict"], "CHECKLIST_BLOCK")
        self.assertIn(
            "source_derived_d85", [c["check"] for c in blocked["checks"] if not c["pass"]]
        )

    def test_score_bound_to_another_inventory_blocks(self) -> None:
        build, _ = _build(self)
        blocked = self._certify_with_score(
            self._passing_score(build, inventory_sha256="0" * 64)
        )[1]
        self.assertEqual(blocked["verdict"], "CHECKLIST_BLOCK")
        self.assertIn(
            "source_derived_d85", [c["check"] for c in blocked["checks"] if not c["pass"]]
        )

    def test_zero_scored_operations_blocks(self) -> None:
        build, _ = _build(self)
        blocked = self._certify_with_score(
            self._passing_score(build, scored_operation_count=0)
        )[1]
        self.assertEqual(blocked["verdict"], "CHECKLIST_BLOCK")

    def test_recomputed_score_passes(self) -> None:
        build, _ = _build(self)
        certified = self._certify_with_score(self._passing_score(build))[1]
        self.assertEqual(certified["verdict"], "CHECKLIST_PASS")
        self.assertEqual(certified["inventory_binding"], "bound")

    def test_wrong_framework_blocks(self) -> None:
        build, _ = _build(
            self,
            properties={"clock_critical": CLOCK},
            framework="kestra_pydantic",
        )
        result = check_build_checklist(build)
        self.assertEqual(result["verdict"], "CHECKLIST_BLOCK")
        failed = [c["check"] for c in result["checks"] if not c["pass"]]
        self.assertIn("framework_matches_standard", failed)
        self.assertEqual(result["expected_framework"], "temporal")

    def test_flowise_declared_durable_blocks(self) -> None:
        build, _ = _build(
            self,
            properties={"non_engineer_surface": NON_ENGINEER},
            framework="flowise",
            durable_system=True,
        )
        result = check_build_checklist(build)
        failed = [c["check"] for c in result["checks"] if not c["pass"]]
        self.assertIn("flowise_not_durable", failed)

    def test_missing_pydantic_models_block_model_builds(self) -> None:
        build, _ = _build(
            self,
            properties={"agent_reasoning": REASONING},
            framework="orca_pydantic",
            pydantic_models=[],
        )
        result = check_build_checklist(build)
        failed = [c["check"] for c in result["checks"] if not c["pass"]]
        self.assertEqual(failed, ["pydantic_models_present"])

    def test_missing_necessity_claims_block_model_builds(self) -> None:
        build, _ = _build(self, model_necessity_claims=[])
        result = check_build_checklist(build)
        failed = [c["check"] for c in result["checks"] if not c["pass"]]
        self.assertEqual(failed, ["model_necessity_claims_present"])

    def test_missing_archify_diagram_blocks(self) -> None:
        build, _ = _build(self, archify_diagram_path="/nonexistent/diagram.json")
        result = check_build_checklist(build)
        failed = [c["check"] for c in result["checks"] if not c["pass"]]
        self.assertIn("archify_diagram_present", failed)

    def test_malformed_archify_diagram_blocks(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            bad = Path(tmp) / "bad.json"
            bad.write_text('{"no_diagram_type": true}', encoding="utf-8")
            build, _ = _build(self, archify_diagram_path=str(bad))
            result = check_build_checklist(build)
        failed = [c["check"] for c in result["checks"] if not c["pass"]]
        self.assertIn("archify_diagram_present", failed)

    def test_missing_d85_pass_blocks(self) -> None:
        build, _ = _build(self, d85_realized_pass=False)
        result = check_build_checklist(build)
        failed = [c["check"] for c in result["checks"] if not c["pass"]]
        self.assertIn("d85_realized_pass", failed)

    def test_model_decided_orchestration_blocks(self) -> None:
        build, _ = _build(self, orchestration_is_code=False)
        result = check_build_checklist(build)
        failed = [c["check"] for c in result["checks"] if not c["pass"]]
        self.assertIn("orchestration_is_code", failed)

    def test_missing_checklist_field_blocks(self) -> None:
        build, _ = _build(self)
        del build["archify_diagram_path"]
        with self.assertRaises(ToolSelectionBlock) as caught:
            check_build_checklist(build)
        self.assertEqual(caught.exception.code, "TOOL_SELECTION_MALFORMED")

    def test_malformed_inventory_hash_blocks(self) -> None:
        for bad in ("not-hex", "A" * 64, "0" * 63, 123):
            with self.subTest(bad=bad):
                build, _ = _build(self, inventory_sha256=bad)
                with self.assertRaises(ToolSelectionBlock) as caught:
                    check_build_checklist(build)
                self.assertEqual(caught.exception.code, "TOOL_SELECTION_MALFORMED")
                self.assertIn("inventory_sha256", caught.exception.detail)

    def test_relative_diagram_resolves_against_root(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            diagram = Path(tmp) / "d.json"
            diagram.write_text(json.dumps({"diagram_type": "lifecycle"}), encoding="utf-8")
            build, _ = _build(self, archify_diagram_path="d.json")
            result = check_build_checklist(build, root=Path(tmp))
        self.assertEqual(result["verdict"], "CHECKLIST_PASS")

    def test_verify_rejects_post_cert_mutation_replay(self) -> None:
        from tool_selection import verify_certification

        build, _ = _build(self)
        certificate = certify_build(build, "julie_synthetic")
        self.assertEqual(certificate["verdict"], "CHECKLIST_PASS")
        # Replay: the saved PASS is re-presented against a mutated build.
        swapped = dict(build, framework="temporal")
        result = verify_certification(swapped, certificate)
        self.assertEqual(result["verdict"], "CERTIFICATION_BLOCK")
        self.assertIn("post-cert mutation", result["binding_reason"])
        mutated_props = dict(build, properties={"clock_critical": CLOCK})
        self.assertEqual(
            verify_certification(mutated_props, certificate)["verdict"], "CERTIFICATION_BLOCK"
        )

    def test_verify_accepts_honest_replay(self) -> None:
        from tool_selection import verify_certification

        build, _ = _build(self)
        certificate = certify_build(build, "julie_synthetic")
        result = verify_certification(build, certificate)
        self.assertEqual(result["verdict"], "CERTIFICATION_VERIFIED")
        self.assertEqual(result["checklist_sha256"], certificate["checklist_sha256"])

    def test_verify_rejects_unbound_certificate(self) -> None:
        from tool_selection import verify_certification

        build, _ = _build(self)
        unbound = check_build_checklist(build)
        unbound["checklist_sha256"] = checklist_digest(build)
        result = verify_certification(build, unbound)
        self.assertEqual(result["verdict"], "CERTIFICATION_BLOCK")
        self.assertIn("bound CHECKLIST_PASS", result["binding_reason"])

    def test_verify_malformed_certificate_blocks(self) -> None:
        from tool_selection import verify_certification

        build, _ = _build(self)
        for bad in (None, [], {"schema": "rig.d85.build-checklist.v1"}):
            with self.subTest(bad=bad):
                with self.assertRaises(ToolSelectionBlock) as caught:
                    verify_certification(build, bad)
                self.assertEqual(caught.exception.code, "CERTIFICATION_MALFORMED")

    def test_verify_rejects_tampered_certificate_payload(self) -> None:
        from tool_selection import verify_certification

        build, _ = _build(self)
        certificate = certify_build(build, "julie_synthetic")
        for mutation in (
            {"expected_framework": "langchain"},
            {"checks": certificate["checks"][:-1]},
            {"checks": "not-a-list"},
        ):
            with self.subTest(mutation=list(mutation)):
                tampered = dict(certificate, **mutation)
                result = verify_certification(build, tampered)
                self.assertEqual(result["verdict"], "CERTIFICATION_BLOCK")
                self.assertIn("tampered certificate", result["binding_reason"])

    def test_certificate_portable_across_identical_roots(self) -> None:
        from tool_selection import verify_certification

        build, fields = _build(self, archify_diagram_path="d.json")
        with tempfile.TemporaryDirectory() as root_a:
            Path(root_a, "d.json").write_text('{"diagram_type": "lifecycle"}', encoding="utf-8")
            certificate = certify_build(build, "julie_synthetic", root=Path(root_a))
            self.assertEqual(certificate["verdict"], "CHECKLIST_PASS")
            with tempfile.TemporaryDirectory() as root_b:
                Path(root_b, "d.json").write_text('{"diagram_type": "lifecycle"}', encoding="utf-8")
                result = verify_certification(build, certificate, root=Path(root_b))
        self.assertEqual(result["verdict"], "CERTIFICATION_VERIFIED")

    def test_verify_blocks_on_mutated_diagram_same_type(self) -> None:
        from tool_selection import verify_certification

        build, _ = _build(self, archify_diagram_path="d.json")
        with tempfile.TemporaryDirectory() as root_a:
            Path(root_a, "d.json").write_text(
                '{"diagram_type": "lifecycle", "stages": ["intake"]}', encoding="utf-8"
            )
            certificate = certify_build(build, "julie_synthetic", root=Path(root_a))
            self.assertEqual(certificate["verdict"], "CHECKLIST_PASS")
            # Same diagram_type, different bytes: without the content hash in
            # the check detail this replay would verify.
            with tempfile.TemporaryDirectory() as root_b:
                Path(root_b, "d.json").write_text(
                    '{"diagram_type": "lifecycle", "stages": ["intake", "export"]}',
                    encoding="utf-8",
                )
                result = verify_certification(build, certificate, root=Path(root_b))
        self.assertEqual(result["verdict"], "CERTIFICATION_BLOCK")


if __name__ == "__main__":
    unittest.main()
