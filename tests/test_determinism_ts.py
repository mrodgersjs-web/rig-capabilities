from __future__ import annotations

import hashlib
import json
import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
SKILL_ROOT = REPO_ROOT / "capabilities" / "skills" / "rig-determinism-85"
sys.path.insert(0, str(SKILL_ROOT))

from d85 import (  # noqa: E402
    AdmissionBlock,
    _build_inventory_from_registry,
)
from d85_gates import classify_inventory, score_realized  # noqa: E402


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


WORKER_TS = (
    "export function collect(value: string): boolean {\n"
    "    return decide(value)\n"
    "}\n"
    "\n"
    "function decide(value: string): boolean {\n"
    "    return Boolean(value)\n"
    "}\n"
)

ADAPTER_TS = (
    'import { collect } from "./worker"\n'
    "\n"
    "export function execute(value: string): boolean {\n"
    "    return collect(value)\n"
    "}\n"
)


class TypeScriptInventoryTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory(prefix="rig-d85-ts-test-")
        self.root = Path(self.temp.name)
        self.source_root = self.root / "repo"
        self.authority_root = self.root / "authority"
        self.source_root.mkdir()
        (self.authority_root / "processes").mkdir(parents=True)
        self.write("worker.ts", WORKER_TS)
        self.write("adapter.ts", ADAPTER_TS)
        self.process = {
            "schema": "rig.d85.process-authority.v1",
            "process_id": "sample",
            "source_root": str(self.source_root),
            "file_hashes": {
                "adapter.ts": self.hash_of("adapter.ts"),
                "worker.ts": self.hash_of("worker.ts"),
            },
            "external_modules": [],
            "entrypoints": [
                {
                    "source_path": "worker.ts",
                    "symbol": "collect",
                    "adapter_path": "adapter.ts",
                    "adapter_operation": "execute",
                }
            ],
        }
        self.registry_path = self.authority_root / "registry.json"
        self._write_authority()

    def tearDown(self) -> None:
        self.temp.cleanup()

    def write(self, name: str, source: str) -> None:
        (self.source_root / name).write_text(source, encoding="utf-8")

    def hash_of(self, name: str) -> str:
        return sha256(self.source_root / name)

    def _write_authority(self) -> None:
        (self.authority_root / "processes" / "sample.json").write_text(
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

    def refresh(self, name: str) -> None:
        self.process["file_hashes"][name] = self.hash_of(name)
        self._write_authority()

    def assert_block(self, code: str, callback) -> None:
        with self.assertRaises(AdmissionBlock) as caught:
            callback()
        self.assertEqual(caught.exception.code, code)

    def inventory(self) -> dict:
        return _build_inventory_from_registry(self.registry_path, "sample")

    def test_ts_inventory_derives_symbols_spans_and_execution_order(self) -> None:
        inventory = self.inventory()

        self.assertEqual(inventory["schema"], "rig.d85.realized-inventory.v1")
        by_symbol = {
            symbol["source"]["symbol"]: symbol for symbol in inventory["symbols"]
        }
        self.assertEqual(set(by_symbol), {"collect", "decide", "execute"})
        self.assertEqual(
            (
                by_symbol["collect"]["source"]["start_line"],
                by_symbol["collect"]["source"]["end_line"],
            ),
            (1, 3),
        )
        self.assertEqual(
            (
                by_symbol["decide"]["source"]["start_line"],
                by_symbol["decide"]["source"]["end_line"],
            ),
            (5, 7),
        )
        self.assertEqual(
            by_symbol["execute"]["successors"],
            [by_symbol["collect"]["symbol_id"]],
        )
        self.assertEqual(
            by_symbol["collect"]["successors"],
            [by_symbol["decide"]["symbol_id"]],
        )
        self.assertEqual(
            by_symbol["decide"]["predecessors"],
            [by_symbol["collect"]["symbol_id"]],
        )
        self.assertEqual(len(inventory["operations"]), 1)
        operation = inventory["operations"][0]
        self.assertEqual(operation["operation_kind"], "EXTERNAL_CALL")
        self.assertEqual(operation["external_call"]["callee"], "Boolean")
        self.assertEqual(operation["source"]["symbol"], "decide")
        self.assertEqual(operation["source"]["start_line"], 6)

    def test_ts_classifies_and_scores_end_to_end(self) -> None:
        self.process["classification_path"] = (
            "processes/sample.classification.json"
        )
        self._write_authority()
        inventory = self.inventory()
        operations = {
            item["inventory_id"]: item for item in inventory["operations"]
        }
        classification = {
            "schema": "rig.d85.classification.v1",
            "process_id": "sample",
            "inventory_sha256": inventory["inventory_sha256"],
            "operations": [
                {
                    "inventory_id": inventory_id,
                    "runtime_kind": "CODE",
                    "taxonomy": "transformation",
                    "predecessors": list(item["predecessors"]),
                    "successors": list(item["successors"]),
                }
                for inventory_id, item in operations.items()
            ],
            "model_necessity": [],
        }
        (self.authority_root / "processes" / "sample.classification.json").write_text(
            json.dumps(classification, sort_keys=True), encoding="utf-8"
        )

        classified = classify_inventory(self.registry_path, "sample")
        self.assertEqual(classified["process_id"], "sample")
        verdict = score_realized(self.registry_path, "sample")
        self.assertEqual(verdict["verdict"], "REALIZED_PASS")
        for name, ratio in verdict["ratios"].items():
            self.assertGreaterEqual(ratio, 0.85, name)

    def test_tsx_jsx_calls_are_inventoried(self) -> None:
        self.write(
            "board.tsx",
            'export function render(title: string): object {\n'
            '    return <div className="board">{helper(title)}</div>\n'
            "}\n"
            "\n"
            "function helper(title: string): string {\n"
            "    return String(title)\n"
            "}\n",
        )
        self.write(
            "adapter.ts",
            'import { collect } from "./worker"\n'
            'import { render } from "./board"\n'
            "\n"
            "export function execute(value: string): boolean {\n"
            "    const rendered = render(value)\n"
            "    return collect(rendered)\n"
            "}\n",
        )
        self.process["file_hashes"]["board.tsx"] = self.hash_of("board.tsx")
        self.refresh("adapter.ts")

        inventory = self.inventory()
        by_symbol = {
            symbol["source"]["symbol"]: symbol for symbol in inventory["symbols"]
        }
        self.assertEqual(
            set(by_symbol), {"collect", "decide", "execute", "helper", "render"}
        )
        self.assertEqual(
            by_symbol["render"]["successors"],
            [by_symbol["helper"]["symbol_id"]],
        )
        callees = sorted(
            item["external_call"]["callee"] for item in inventory["operations"]
        )
        self.assertEqual(callees, ["Boolean", "String"])

    def test_ts_namespace_import_resolves_locally(self) -> None:
        self.write(
            "adapter.ts",
            'import * as worker from "./worker"\n'
            "\n"
            "export function execute(value: string): boolean {\n"
            "    return worker.collect(value)\n"
            "}\n",
        )
        self.refresh("adapter.ts")

        inventory = self.inventory()
        by_symbol = {
            symbol["source"]["symbol"]: symbol for symbol in inventory["symbols"]
        }
        self.assertEqual(
            by_symbol["execute"]["successors"],
            [by_symbol["collect"]["symbol_id"]],
        )

    def test_ts_default_export_alias_resolves(self) -> None:
        self.write(
            "worker.ts",
            "export default function collect(value: string): boolean {\n"
            "    return decide(value)\n"
            "}\n"
            "\n"
            "function decide(value: string): boolean {\n"
            "    return Boolean(value)\n"
            "}\n",
        )
        self.write(
            "adapter.ts",
            'import collect from "./worker"\n'
            "\n"
            "export function execute(value: string): boolean {\n"
            "    return collect(value)\n"
            "}\n",
        )
        self.process["entrypoints"][0]["symbol"] = "default"
        self.refresh("worker.ts")
        self.refresh("adapter.ts")

        inventory = self.inventory()
        by_symbol = {
            symbol["source"]["symbol"]: symbol for symbol in inventory["symbols"]
        }
        self.assertIn("default", by_symbol)
        self.assertEqual(
            by_symbol["execute"]["successors"],
            [by_symbol["default"]["symbol_id"]],
        )

    def test_ts_dynamic_calls_fail_closed(self) -> None:
        cases = {
            "eval": (
                "export function collect(value: string): boolean {\n"
                "    return eval(value)\n"
                "}\n"
            ),
            "function_constructor": (
                "export function collect(value: string): boolean {\n"
                "    return Function(value)\n"
                "}\n"
            ),
            "require": (
                "export function collect(value: string): boolean {\n"
                "    return require(value)\n"
                "}\n"
            ),
        }
        for name, source in cases.items():
            with self.subTest(name=name):
                self.write("worker.ts", source)
                self.refresh("worker.ts")
                self.assert_block("SOURCE_DYNAMIC_CALL", self.inventory)

    def test_ts_unsupported_grammar_fails_closed(self) -> None:
        cases = {
            "control_flow": (
                "export function collect(value: string): boolean {\n"
                "    if (value) {\n"
                "        return true\n"
                "    }\n"
                "    return false\n"
                "}\n"
            ),
            "async": (
                "export async function collect(value: string): boolean {\n"
                "    return Boolean(value)\n"
                "}\n"
            ),
            "class": (
                "class Hidden {\n"
                "    value: string\n"
                "}\n"
                "\n"
                "export function collect(value: string): boolean {\n"
                "    return Boolean(value)\n"
                "}\n"
            ),
            "module_level_value": (
                "const flag: boolean = true\n"
                "\n"
                "export function collect(value: string): boolean {\n"
                "    return Boolean(value)\n"
                "}\n"
            ),
            "template_substitution": (
                "export function collect(value: string): boolean {\n"
                "    return Boolean(`x${value}`)\n"
                "}\n"
            ),
            "statement_after_return": (
                "export function collect(value: string): boolean {\n"
                "    return Boolean(value)\n"
                "    const out = Boolean(value)\n"
                "}\n"
            ),
            "discarded_expression": (
                "export function collect(value: string): boolean {\n"
                "    Boolean(value)\n"
                "    return true\n"
                "}\n"
            ),
            "reassigned_local": (
                "export function collect(value: string): boolean {\n"
                "    let out = Boolean(value)\n"
                "    out = Boolean(out)\n"
                "    return out\n"
                "}\n"
            ),
            "dead_call_result": (
                "export function collect(value: string): boolean {\n"
                "    const out = Boolean(value)\n"
                "    return true\n"
                "}\n"
            ),
            "call_in_default_parameter": (
                "export function collect(\n"
                "    value: string = String(1)\n"
                "): boolean {\n"
                "    return Boolean(value)\n"
                "}\n"
            ),
            "regex_literal": (
                "export function collect(value: string): boolean {\n"
                "    return Boolean(/x/)\n"
                "}\n"
            ),
        }
        for name, source in cases.items():
            with self.subTest(name=name):
                self.write("worker.ts", source)
                self.refresh("worker.ts")
                self.assert_block("SOURCE_UNSUPPORTED_GRAMMAR", self.inventory)

    def test_ts_callable_escape_fails_closed(self) -> None:
        self.write(
            "worker.ts",
            "export function collect(value: string): boolean {\n"
            "    const out = decide\n"
            "    return decide(value)\n"
            "}\n"
            "\n"
            "function decide(value: string): boolean {\n"
            "    return Boolean(value)\n"
            "}\n",
        )
        self.refresh("worker.ts")
        self.assert_block("SOURCE_DYNAMIC_CALL", self.inventory)

    def test_ts_external_import_fails_closed(self) -> None:
        self.write(
            "worker.ts",
            'import { useState } from "react"\n'
            "\n"
            "export function collect(value: string): boolean {\n"
            "    return Boolean(value)\n"
            "}\n",
        )
        self.refresh("worker.ts")
        self.assert_block("SOURCE_EXTERNAL_IMPORT", self.inventory)

    def test_ts_unhashed_reachable_file_fails_closed(self) -> None:
        self.write("ghost.ts", "export function haunt(): boolean {\n    return true\n}\n")
        self.write(
            "worker.ts",
            'import { haunt } from "./ghost"\n'
            "\n"
            "export function collect(value: string): boolean {\n"
            "    return haunt()\n"
            "}\n",
        )
        self.refresh("worker.ts")
        self.assert_block("UNHASHED_REACHABLE_FILE", self.inventory)

    def test_ts_external_module_lock_is_python_only(self) -> None:
        self.process["external_modules"] = [
            {
                "module": "path",
                "artifact_path": str(self.root / "path.py"),
                "artifact_sha256": "0" * 64,
                "allowed_calls": ["path.join"],
            }
        ]
        self._write_authority()
        self.assert_block("EXTERNAL_MODULE_LANGUAGE_UNSUPPORTED", self.inventory)

    def test_unsupported_source_language_fails_closed(self) -> None:
        self.write("legacy.js", "function execute(value) {\n    return value\n}\n")
        self.process["file_hashes"] = {
            "legacy.js": self.hash_of("legacy.js"),
            "worker.ts": self.hash_of("worker.ts"),
        }
        self.process["entrypoints"][0]["adapter_path"] = "legacy.js"
        self._write_authority()
        self.assert_block("SOURCE_LANGUAGE_UNSUPPORTED", self.inventory)


if __name__ == "__main__":
    unittest.main()
