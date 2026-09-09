"""Tests for D85 classification, scoring, Gate-D, and surface-wiring gates."""

import json
import os
import sys
import tempfile
import unittest
from hashlib import sha256
from pathlib import Path

SKILL_ROOT = Path(__file__).resolve().parent.parent / (
    "capabilities/skills/rig-determinism-85"
)
sys.path.insert(0, str(SKILL_ROOT))

from d85 import (  # noqa: E402
    AdmissionBlock,
    _build_inventory_from_registry,
)
from d85_gates import (  # noqa: E402
    _canonical_hash,
    check_wiring,
    classify_inventory,
    gate_d,
    mint_approval,
    score_realized,
)


def sha256_file(path: Path) -> str:
    return sha256(Path(path).read_bytes()).hexdigest()


class GateTestBase(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory(prefix="rig-d85-gates-")
        self.root = Path(self.temp.name)
        self.source_root = self.root / "repo"
        self.authority_root = self.root / "authority"
        self.gate_root = self.root / "gate_d"
        self.source_root.mkdir()
        (self.authority_root / "processes").mkdir(parents=True)
        (self.source_root / "worker.py").write_text(
            "def s1(value):\n"
            "    return s2(str(value))\n\n"
            "def s2(value):\n"
            "    return s3(len(value))\n\n"
            "def s3(value):\n"
            "    return s4(bool(value))\n\n"
            "def s4(value):\n"
            "    return s5(repr(value))\n\n"
            "def s5(value):\n"
            "    return s6(abs(value))\n\n"
            "def s6(value):\n"
            "    return s7(round(value))\n\n"
            "def s7(value):\n"
            "    return hex(value)\n",
            encoding="utf-8",
        )
        (self.source_root / "adapter.py").write_text(
            "from worker import s1\n\n"
            "def execute(value):\n"
            "    return s1(value)\n",
            encoding="utf-8",
        )
        self.process = {
            "schema": "rig.d85.process-authority.v1",
            "process_id": "sample",
            "source_root": str(self.source_root),
            "file_hashes": {
                "adapter.py": sha256_file(self.source_root / "adapter.py"),
                "worker.py": sha256_file(self.source_root / "worker.py"),
            },
            "external_modules": [],
            "classification_path": "processes/sample.classification.json",
            "entrypoints": [
                {
                    "source_path": "worker.py",
                    "symbol": "s1",
                    "adapter_path": "adapter.py",
                    "adapter_operation": "execute",
                }
            ],
        }
        self.registry_path = self.authority_root / "registry.json"
        self.process_path = self.authority_root / "processes" / "sample.json"
        self.write_authority()

    def tearDown(self) -> None:
        self.temp.cleanup()

    def write_authority(self, classification: dict | None = None) -> None:
        if classification is not None:
            (
                self.authority_root / "processes" / "sample.classification.json"
            ).write_text(json.dumps(classification, sort_keys=True), encoding="utf-8")
        self.process_path.write_text(
            json.dumps(self.process, sort_keys=True), encoding="utf-8"
        )
        self.registry_path.write_text(
            json.dumps(
                {
                    "schema": "rig.d85.authority-registry.v1",
                    "processes": {"sample": "processes/sample.json"},
                },
                sort_keys=True,
            ),
            encoding="utf-8",
        )

    def inventory(self) -> dict:
        return _build_inventory_from_registry(self.registry_path, "sample")

    def chain_ids(self) -> list[str]:
        """Extracted inventory ids in execution order (single chain)."""
        inventory = self.inventory()
        by_id = {op["inventory_id"]: op for op in inventory["operations"]}
        current = by_id[inventory["roots"][0]]
        order = [current["inventory_id"]]
        while current["successors"]:
            current = by_id[current["successors"][0]]
            order.append(current["inventory_id"])
        return order

    def classification(
        self,
        kinds: dict[int, str] | None = None,
        taxonomies: dict[int, str] | None = None,
        edges: dict[int, list[int]] | None = None,
        necessity: list[dict] | None = None,
        drop: int | None = None,
        extra: dict | None = None,
        inventory_sha256: str | None = None,
    ) -> dict:
        ids = self.chain_ids()
        kinds = kinds or {}
        taxonomies = taxonomies or {}
        records = [
            {
                "inventory_id": inventory_id,
                "runtime_kind": kinds.get(index, "CODE"),
                "taxonomy": taxonomies.get(index, "transformation"),
                "predecessors": [],
                "successors": [],
            }
            for index, inventory_id in enumerate(ids)
        ]
        if edges is None:
            edges = {index: [index + 1] for index in range(len(ids) - 1)}
            edges[len(ids) - 1] = []
        for source, targets in edges.items():
            records[source]["successors"] = [ids[target] for target in targets]
            for target in targets:
                records[target]["predecessors"].append(ids[source])
        if drop is not None:
            records.pop(drop)
        if extra is not None:
            records.append(extra)
        return {
            "schema": "rig.d85.classification.v1",
            "process_id": "sample",
            "inventory_sha256": inventory_sha256
            or self.inventory()["inventory_sha256"],
            "operations": records,
            "model_necessity": necessity or [],
        }

    def necessity(self, index: int, ids: list[str], **overrides) -> dict:
        record = {
            "inventory_id": ids[index],
            "necessity_claim": "ranking beats the keyword heuristic on graded cases",
            "deterministic_alternative": "score = len(keywords) / len(tokens)",
            "expected_improvement": 0.4,
            "input_schema": {"query": "string"},
            "output_schema": {"rank": "number"},
            "attempt_ceiling": 3,
            "tool_ceiling": 5,
            "token_ceiling": 8000,
            "time_ceiling_seconds": 120,
            "cost_ceiling_usd": 0.5,
            "validator_operation": ids[min(index + 1, len(ids) - 1)],
            "fallback_operation": ids[min(index + 2, len(ids) - 1)],
            "failure_state_operation": ids[min(index + 3, len(ids) - 1)],
        }
        record.update(overrides)
        return record

    def assert_block(self, code: str, callback):
        with self.assertRaises(AdmissionBlock) as caught:
            callback()
        self.assertEqual(caught.exception.code, code)
        return caught.exception


class ClassificationTests(GateTestBase):
    def test_classification_passes_and_mints_operation_ids(self) -> None:
        self.write_authority(
            self.classification(taxonomies={0: "control plane", 1: "decision"})
        )

        result = classify_inventory(self.registry_path, "sample")

        self.assertEqual(result["schema"], "rig.d85.classified-inventory.v1")
        self.assertFalse(result["d85_admission"])
        self.assertEqual(len(result["operations"]), 7)
        self.assertTrue(
            all(op["operation_id"].startswith("sha256:") for op in result["operations"])
        )
        self.assertEqual(result["kind_counts"]["CODE"], 7)
        for op in result["operations"]:
            for binding in (*op["predecessors"], *op["successors"]):
                self.assertTrue(binding.startswith("sha256:"))

    def test_classification_rejects_stale_inventory_binding(self) -> None:
        self.write_authority(
            self.classification(inventory_sha256="sha256:" + "0" * 64)
        )

        self.assert_block(
            "CLASSIFICATION_STALE",
            lambda: classify_inventory(self.registry_path, "sample"),
        )

    def test_classification_requires_process_record_path(self) -> None:
        self.process.pop("classification_path", None)
        self.write_authority(self.classification())

        self.assert_block(
            "CLASSIFICATION_MISSING",
            lambda: classify_inventory(self.registry_path, "sample"),
        )

    def test_classification_rejects_missing_unknown_and_duplicate_ids(self) -> None:
        self.write_authority(self.classification(drop=3))
        self.assert_block(
            "CLASSIFICATION_MISSING_ID",
            lambda: classify_inventory(self.registry_path, "sample"),
        )

        self.write_authority(
            self.classification(
                extra={
                    "inventory_id": "sha256:" + "9" * 64,
                    "runtime_kind": "CODE",
                    "taxonomy": "retrieval",
                    "predecessors": [],
                    "successors": [],
                }
            )
        )
        self.assert_block(
            "CLASSIFICATION_UNKNOWN_ID",
            lambda: classify_inventory(self.registry_path, "sample"),
        )

        duplicate = self.classification()
        duplicate["operations"][4]["inventory_id"] = duplicate["operations"][3][
            "inventory_id"
        ]
        self.write_authority(duplicate)
        self.assert_block(
            "CLASSIFICATION_DUPLICATE_ID",
            lambda: classify_inventory(self.registry_path, "sample"),
        )

    def test_classification_rejects_unknown_kind_or_taxonomy(self) -> None:
        self.write_authority(self.classification(kinds={2: "AGENT"}))
        self.assert_block(
            "CLASSIFICATION_MALFORMED",
            lambda: classify_inventory(self.registry_path, "sample"),
        )
        self.write_authority(self.classification(taxonomies={2: "magic"}))
        self.assert_block(
            "CLASSIFICATION_MALFORMED",
            lambda: classify_inventory(self.registry_path, "sample"),
        )

    def test_critical_control_must_be_code(self) -> None:
        self.write_authority(
            self.classification(kinds={3: "MODEL"}, taxonomies={3: "control plane"})
        )

        self.assert_block(
            "CRITICAL_CONTROL_NOT_CODE",
            lambda: classify_inventory(self.registry_path, "sample"),
        )

    def test_classification_rejects_broken_graphs(self) -> None:
        asymmetric = self.classification()
        asymmetric["operations"][2]["successors"].append(
            asymmetric["operations"][5]["inventory_id"]
        )
        self.write_authority(asymmetric)
        self.assert_block(
            "CLASSIFICATION_GRAPH_ASYMMETRIC",
            lambda: classify_inventory(self.registry_path, "sample"),
        )
        cyclic = self.classification(
            edges={0: [1], 1: [2], 2: [1], 3: [4], 4: [5], 5: [6], 6: []}
        )
        self.write_authority(cyclic)
        self.assert_block(
            "CLASSIFICATION_GRAPH_CYCLIC",
            lambda: classify_inventory(self.registry_path, "sample"),
        )

        self_edge = self.classification()
        self_edge["operations"][3]["successors"] = [
            self_edge["operations"][3]["inventory_id"]
        ]
        self.write_authority(self_edge)
        self.assert_block(
            "CLASSIFICATION_SELF_EDGE",
            lambda: classify_inventory(self.registry_path, "sample"),
        )


class ModelNecessityTests(GateTestBase):
    def test_model_operation_requires_necessity(self) -> None:
        self.write_authority(self.classification(kinds={3: "MODEL"}))

        self.assert_block(
            "MODEL_NECESSITY_MISSING",
            lambda: classify_inventory(self.registry_path, "sample"),
        )

    def test_necessity_rejects_non_model_operation(self) -> None:
        ids = self.chain_ids()
        self.write_authority(
            self.classification(necessity=[self.necessity(0, ids)])
        )

        self.assert_block(
            "MODEL_NECESSITY_MALFORMED",
            lambda: classify_inventory(self.registry_path, "sample"),
        )

    def test_necessity_field_validation(self) -> None:
        ids = self.chain_ids()
        for field, value, code in (
            ("expected_improvement", 0, "MODEL_NECESSITY_MALFORMED"),
            ("expected_improvement", 1.5, "MODEL_NECESSITY_MALFORMED"),
            ("expected_improvement", True, "MODEL_NECESSITY_MALFORMED"),
            ("attempt_ceiling", 0, "MODEL_NECESSITY_MALFORMED"),
            ("attempt_ceiling", True, "MODEL_NECESSITY_MALFORMED"),
            ("time_ceiling_seconds", -1, "MODEL_NECESSITY_MALFORMED"),
            ("input_schema", {}, "MODEL_NECESSITY_MALFORMED"),
            ("necessity_claim", "", "AUTHORITY_MALFORMED"),
        ):
            with self.subTest(field=field, value=value):
                self.write_authority(
                    self.classification(
                        kinds={3: "MODEL"},
                        necessity=[self.necessity(3, ids, **{field: value})],
                    )
                )
                self.assert_block(
                    code,
                    lambda: classify_inventory(self.registry_path, "sample"),
                )

    def test_model_support_must_be_reachable_code(self) -> None:
        ids = self.chain_ids()
        self.write_authority(
            self.classification(
                kinds={3: "MODEL"},
                necessity=[
                    self.necessity(3, ids, validator_operation=ids[0])
                ],
            )
        )
        self.assert_block(
            "MODEL_VALIDATOR_UNREACHABLE",
            lambda: classify_inventory(self.registry_path, "sample"),
        )

        self.write_authority(
            self.classification(
                kinds={3: "MODEL", 4: "MODEL"},
                necessity=[
                    self.necessity(3, ids, fallback_operation=ids[4]),
                    self.necessity(4, ids),
                ],
            )
        )
        self.assert_block(
            "CRITICAL_CONTROL_NOT_CODE",
            lambda: classify_inventory(self.registry_path, "sample"),
        )

    def test_necessity_rejects_duplicate_records(self) -> None:
        ids = self.chain_ids()
        self.write_authority(
            self.classification(
                kinds={3: "MODEL"},
                necessity=[self.necessity(3, ids), self.necessity(3, ids)],
            )
        )
        self.assert_block(
            "CLASSIFICATION_DUPLICATE_ID",
            lambda: classify_inventory(self.registry_path, "sample"),
        )


class ScoringTests(GateTestBase):
    def passing_classification(self) -> dict:
        ids = self.chain_ids()
        return self.classification(
            kinds={5: "MODEL"},
            taxonomies={
                0: "control plane",
                1: "control plane",
                2: "decision",
                3: "transformation",
                4: "retrieval",
                5: "retrieval",
                6: "presentation",
            },
            necessity=[self.necessity(5, ids)],
        )

    def test_realized_pass_when_all_ratios_hold(self) -> None:
        self.write_authority(self.passing_classification())

        verdict = score_realized(self.registry_path, "sample")

        self.assertEqual(verdict["verdict"], "REALIZED_PASS")
        self.assertTrue(verdict["d85_admission"])
        self.assertEqual(verdict["credit_operation_count"], 6)
        self.assertEqual(verdict["scored_operation_count"], 7)
        for ratio in verdict["ratios"].values():
            self.assertGreaterEqual(ratio, 0.85)

    def test_below_threshold_blocks(self) -> None:
        ids = self.chain_ids()
        classification = self.classification(
            kinds={4: "MODEL", 5: "MODEL"},
            necessity=[self.necessity(4, ids, validator_operation=ids[6])],
        )
        classification["model_necessity"].append(
            self.necessity(5, ids, validator_operation=ids[6])
        )
        self.write_authority(classification)

        self.assert_block(
            "BLOCK_DETERMINISM_RATIO",
            lambda: score_realized(self.registry_path, "sample"),
        )

    def test_minimum_path_ratio_blocks_despite_passing_aggregate(self) -> None:
        ids = self.chain_ids()
        edges = {
            0: [1, 3],
            1: [2],
            2: [6],
            3: [4],
            4: [5],
            5: [6],
            6: [],
        }
        self.write_authority(
            self.classification(
                kinds={2: "MODEL"},
                edges=edges,
                necessity=[
                    self.necessity(
                        2,
                        ids,
                        validator_operation=ids[6],
                        fallback_operation=ids[6],
                        failure_state_operation=ids[6],
                    )
                ],
            )
        )

        blocked = self.assert_block(
            "BLOCK_DETERMINISM_RATIO",
            lambda: score_realized(self.registry_path, "sample"),
        )
        self.assertIn("min_path_unweighted", str(blocked))

    def test_human_operations_are_excluded_from_scoring(self) -> None:
        (self.source_root / "worker.py").write_text(
            "def s1(value):\n"
            "    return s2(str(value))\n\n"
            "def s2(value):\n"
            "    return s3(len(value))\n\n"
            "def s3(value):\n"
            "    return s4(bool(value))\n\n"
            "def s4(value):\n"
            "    return s5(repr(value))\n\n"
            "def s5(value):\n"
            "    return s6(abs(value))\n\n"
            "def s6(value):\n"
            "    return s7(round(value))\n\n"
            "def s7(value):\n"
            "    return s8(abs(value))\n\n"
            "def s8(value):\n"
            "    return hex(value)\n",
            encoding="utf-8",
        )
        self.process["file_hashes"]["worker.py"] = sha256_file(
            self.source_root / "worker.py"
        )
        self.write_authority()
        ids = self.chain_ids()
        self.assertEqual(len(ids), 8)
        self.write_authority(
            self.classification(
                kinds={5: "MODEL", 6: "HUMAN"},
                taxonomies={
                    0: "control plane",
                    1: "decision",
                    5: "retrieval",
                    7: "presentation",
                },
                necessity=[
                    self.necessity(
                        5,
                        ids,
                        validator_operation=ids[7],
                        fallback_operation=ids[7],
                        failure_state_operation=ids[7],
                    )
                ],
            )
        )

        verdict = score_realized(self.registry_path, "sample")

        self.assertEqual(verdict["verdict"], "REALIZED_PASS")
        self.assertEqual(verdict["scored_operation_count"], 7)
        self.assertEqual(verdict["credit_operation_count"], 6)


class GateDTests(GateTestBase):
    def setUp(self) -> None:
        super().setUp()
        ids = self.chain_ids()
        self.write_authority(
            self.classification(
                kinds={5: "MODEL"},
                taxonomies={5: "retrieval"},
                necessity=[self.necessity(5, ids)],
            )
        )
        self.proof = score_realized(self.registry_path, "sample")
        self.action = {"tool": "git", "arguments": ["push", "origin", "main"]}

    def mint(self, action: dict | None = None, **kwargs) -> dict:
        inventory_sha256 = kwargs.pop(
            "inventory_sha256", self.proof["inventory_sha256"]
        )
        return mint_approval(
            self.gate_root,
            process_id="sample",
            inventory_sha256=inventory_sha256,
            classification_sha256=self.proof["classification_sha256"],
            realized_sha256=_canonical_hash(self.proof),
            action=action or self.action,
            approver="mike",
            **kwargs,
        )

    def arm(self, action: dict | None = None, **kwargs) -> dict:
        return gate_d(
            self.registry_path,
            "sample",
            action or self.action,
            test_gate_root=self.gate_root,
            **kwargs,
        )

    def test_armed_once_then_replay_blocks(self) -> None:
        self.mint()

        verdict = self.arm()

        self.assertEqual(verdict["verdict"], "ARMED")
        self.assertEqual(verdict["approver"], "mike")
        self.assertTrue(Path(verdict["consumed_marker"]).exists())

        self.assert_block("BLOCK_GATE_D_CONSUMED", self.arm)

    def test_unapproved_action_blocks(self) -> None:
        self.mint()
        other = {"tool": "git", "arguments": ["push", "origin", "other"]}

        self.assert_block("BLOCK_GATE_D_UNAPPROVED", lambda: self.arm(other))

    def test_missing_approval_store_blocks(self) -> None:
        self.assert_block("BLOCK_GATE_D_MISSING", self.arm)

    def test_expired_approval_blocks(self) -> None:
        entry = self.mint(lifetime_seconds=60)

        self.assert_block(
            "BLOCK_GATE_D_EXPIRED",
            lambda: self.arm(now=entry["expires_at"] + 1),
        )

    def test_proof_mismatch_blocks(self) -> None:
        self.mint(inventory_sha256="sha256:" + "0" * 64)

        self.assert_block("BLOCK_GATE_D_MISMATCH", self.arm)

    def test_corrupt_approval_line_blocks(self) -> None:
        self.mint()
        path = self.gate_root / "approvals.jsonl"
        path.write_text(
            path.read_text(encoding="utf-8") + '{"schema": "garbage"}\n',
            encoding="utf-8",
        )

        self.assert_block("BLOCK_GATE_D_CORRUPT", self.arm)

    def test_tampered_approval_field_blocks(self) -> None:
        self.mint()
        path = self.gate_root / "approvals.jsonl"
        line = json.loads(path.read_text(encoding="utf-8").splitlines()[0])
        line["approver"] = "attacker"
        path.write_text(json.dumps(line, sort_keys=True) + "\n", encoding="utf-8")

        self.assert_block("BLOCK_GATE_D_CORRUPT", self.arm)

    def test_production_rejects_root_override(self) -> None:
        self.mint()
        previous = os.environ.get("RIG_LOOP_STATE")
        os.environ["RIG_LOOP_STATE"] = str(self.root / "rogue")
        try:
            with self.assertRaises(AdmissionBlock) as caught:
                gate_d(self.registry_path, "sample", self.action)
            self.assertEqual(caught.exception.code, "BLOCK_GATE_D_ROOT_OVERRIDE")
        finally:
            if previous is None:
                os.environ.pop("RIG_LOOP_STATE", None)
            else:
                os.environ["RIG_LOOP_STATE"] = previous


class WiringTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory(prefix="rig-d85-wiring-")
        self.root = Path(self.temp.name)
        self.authority_root = self.root / "authority"
        self.authority_root.mkdir(parents=True)
        self.doctrine = "a" * 64
        self.marker = f"rig-determinism-85@{self.doctrine}"
        self.surface_paths: dict[str, Path] = {}
        for name in ("claude", "hermes", "omp", "prime"):
            path = self.root / f"{name}.md"
            path.write_text(f"# surface {name}\n{self.marker}\n", encoding="utf-8")
            self.surface_paths[name] = path
        self.write_surfaces()

    def tearDown(self) -> None:
        self.temp.cleanup()

    def write_surfaces(self) -> None:
        (self.authority_root / "surfaces.json").write_text(
            json.dumps(
                {
                    "schema": "rig.d85.surfaces.v1",
                    "doctrine_sha256": self.doctrine,
                    "surfaces": {
                        "claude_code": str(self.surface_paths["claude"]),
                        "hermes": str(self.surface_paths["hermes"]),
                        "omp": str(self.surface_paths["omp"]),
                        "prime_agent": str(self.surface_paths["prime"]),
                    },
                },
                sort_keys=True,
            ),
            encoding="utf-8",
        )

    def registry_path(self) -> Path:
        return self.authority_root / "registry.json"

    def assert_block(self, code: str, callback) -> None:
        with self.assertRaises(AdmissionBlock) as caught:
            callback()
        self.assertEqual(caught.exception.code, code)

    def test_wiring_pass_when_all_surfaces_carry_the_marker(self) -> None:
        result = check_wiring(self.registry_path())

        self.assertEqual(result["verdict"], "WIRING_PASS")
        self.assertEqual(
            set(result["surfaces"]), {"claude_code", "hermes", "omp", "prime_agent"}
        )

    def test_wiring_blocks_on_divergent_marker(self) -> None:
        self.surface_paths["omp"].write_text(
            "# surface omp\nrig-determinism-85@" + "b" * 64 + "\n", encoding="utf-8"
        )
        self.assert_block(
            "BLOCK_WIRING_SURFACE_DIVERGENT",
            lambda: check_wiring(self.registry_path()),
        )

    def test_wiring_blocks_on_missing_surface(self) -> None:
        self.surface_paths["hermes"].unlink()
        self.assert_block(
            "BLOCK_WIRING_SURFACE_MISSING",
            lambda: check_wiring(self.registry_path()),
        )

    def test_wiring_requires_exactly_four_surfaces(self) -> None:
        surfaces = json.loads(
            (self.authority_root / "surfaces.json").read_text(encoding="utf-8")
        )
        del surfaces["surfaces"]["prime_agent"]
        (self.authority_root / "surfaces.json").write_text(
            json.dumps(surfaces, sort_keys=True), encoding="utf-8"
        )
        self.assert_block(
            "BLOCK_WIRING_SURFACE_DIVERGENT",
            lambda: check_wiring(self.registry_path()),
        )


if __name__ == "__main__":
    unittest.main()
