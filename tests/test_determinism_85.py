from __future__ import annotations

import hashlib
import json
import os
import tempfile
import subprocess
import sys
import types
import unittest
from pathlib import Path
REPO_ROOT = Path(__file__).resolve().parent.parent
SKILL_ROOT = REPO_ROOT / "capabilities" / "skills" / "rig-determinism-85"
sys.path.insert(0, str(SKILL_ROOT))
CLI = SKILL_ROOT / "bin" / "rig-determinism-85"



from d85 import (
    AdmissionBlock,
    _build_inventory_from_registry,
    _compare_inventory_from_registry,
    _parse_module,
)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


class DeterminismInventoryTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory(prefix="rig-d85-test-")
        self.root = Path(self.temp.name)
        self.source_root = self.root / "repo"
        self.authority_root = self.root / "authority"
        self.source_root.mkdir()
        (self.authority_root / "processes").mkdir(parents=True)
        self.source = self.source_root / "worker.py"
        self.adapter = self.source_root / "adapter.py"
        self.source.write_text(
            "def collect(value):\n"
            "    return decide(value)\n\n"
            "def decide(value):\n"
            "    return bool(value)\n",
            encoding="utf-8",
        )
        self.adapter.write_text(
            "from worker import collect\n\n"
            "def execute(value):\n"
            "    return collect(value)\n",
            encoding="utf-8",
        )
        self.process = {
            "schema": "rig.d85.process-authority.v1",
            "process_id": "sample",
            "source_root": str(self.source_root),
            "file_hashes": {
                "adapter.py": sha256(self.adapter),
                "worker.py": sha256(self.source),
            },
            "external_modules": [],
            "entrypoints": [
                {
                    "source_path": "worker.py",
                    "symbol": "collect",
                    "adapter_path": "adapter.py",
                    "adapter_operation": "execute",
                }
            ],
        }
        self.process_path = self.authority_root / "processes" / "sample.json"
        self.registry_path = self.authority_root / "registry.json"
        self._write_authority()

    def tearDown(self) -> None:
        self.temp.cleanup()

    def _write_authority(self) -> None:
        self.process_path.write_text(
            json.dumps(self.process, sort_keys=True), encoding="utf-8"
        )
        registry = {
            "schema": "rig.d85.authority-registry.v1",
            "processes": {"sample": "processes/sample.json"},
        }
        self.registry_path.write_text(
            json.dumps(registry, sort_keys=True), encoding="utf-8"
        )

    def assert_block(self, code: str, callback) -> None:
        with self.assertRaises(AdmissionBlock) as caught:
            callback()
        self.assertEqual(caught.exception.code, code)

    def test_authority_derives_reachable_symbols_spans_and_graph(self) -> None:
        inventory = _build_inventory_from_registry(self.registry_path, "sample")

        self.assertEqual(inventory["schema"], "rig.d85.realized-inventory.v1")
        by_symbol = {
            symbol["source"]["symbol"]: symbol
            for symbol in inventory["symbols"]
        }
        self.assertEqual(set(by_symbol), {"collect", "decide", "execute", "__module_init__"})
        self.assertEqual(
            (by_symbol["collect"]["source"]["start_line"], by_symbol["collect"]["source"]["end_line"]),
            (1, 2),
        )
        self.assertEqual(
            (by_symbol["decide"]["source"]["start_line"], by_symbol["decide"]["source"]["end_line"]),
            (4, 5),
        )
        self.assertEqual(
            by_symbol["execute"]["successors"],
            [by_symbol["collect"]["symbol_id"]],
        )
        self.assertEqual(
            by_symbol["collect"]["predecessors"],
            [by_symbol["execute"]["symbol_id"]],
        )
        self.assertEqual(
            by_symbol["collect"]["successors"],
            [by_symbol["decide"]["symbol_id"]],
        )
        self.assertEqual(
            by_symbol["decide"]["predecessors"],
            [by_symbol["collect"]["symbol_id"]],
        )
        self.assertTrue(
            all(
                item["inventory_id"].startswith("sha256:")
                for item in inventory["operations"]
            )
        )
        self.assertTrue(
            all(
                item["symbol_id"].startswith("sha256:")
                for item in inventory["symbols"]
            )
        )
        self.assertTrue(
            all(
                "execution_kind" not in item and "taxonomy" not in item
                for item in (*inventory["symbols"], *inventory["operations"])
            )
        )

    def test_adapter_operation_and_reachable_helpers_are_inventoried(self) -> None:
        self.adapter.write_text(
            "from worker import collect\n\n"
            "def execute(value):\n"
            "    return hidden(value)\n\n"
            "def hidden(value):\n"
            "    return collect(value)\n",
            encoding="utf-8",
        )
        self.process["file_hashes"]["adapter.py"] = sha256(self.adapter)
        self._write_authority()

        inventory = _build_inventory_from_registry(self.registry_path, "sample")

        self.assertEqual(
            {
                (op["source"]["path"], op["source"]["symbol"])
                for op in inventory["symbols"]
            },
            {
                ("adapter.py", "execute"),
                ("adapter.py", "hidden"),
                ("worker.py", "collect"),
                ("worker.py", "decide"),
                ("adapter.py", "__module_init__"),
            },
        )

    def test_external_call_site_is_an_operation_not_symbol_metadata(self) -> None:
        inventory = _build_inventory_from_registry(self.registry_path, "sample")
        symbols = {
            item["source"]["symbol"]: item
            for item in inventory["symbols"]
        }
        external = [
            op
            for op in inventory["operations"]
            if op.get("operation_kind") == "EXTERNAL_CALL"
        ]

        self.assertEqual(len(external), 1)
        self.assertEqual(external[0]["external_call"]["callee"], "bool")
        self.assertFalse(external[0]["credit_eligible"])
        self.assertEqual(external[0]["predecessors"], [])
        self.assertEqual(inventory["roots"], [external[0]["inventory_id"]])
        self.assertEqual(inventory["terminals"], [external[0]["inventory_id"]])
        self.assertNotIn("external_calls", symbols["decide"])

    def test_multiple_calls_form_one_exact_execution_sequence(self) -> None:
        self.source.write_text(
            "def collect(value):\n"
            "    text = str(value)\n"
            "    return bool(text)\n",
            encoding="utf-8",
        )
        self.process["file_hashes"]["worker.py"] = sha256(self.source)
        self._write_authority()

        inventory = _build_inventory_from_registry(self.registry_path, "sample")
        by_id = {
            operation["inventory_id"]: operation
            for operation in inventory["operations"]
        }
        first = by_id[inventory["roots"][0]]
        second = by_id[first["successors"][0]]

        self.assertEqual(
            [first["external_call"]["callee"], second["external_call"]["callee"]],
            ["str", "bool"],
        )
        self.assertEqual(second["predecessors"], [first["inventory_id"]])
        self.assertEqual(inventory["terminals"], [second["inventory_id"]])

    def test_nested_calls_follow_python_evaluation_order(self) -> None:
        self.source.write_text(
            "def collect(value):\n"
            "    return str(bool(value))\n",
            encoding="utf-8",
        )
        self.process["file_hashes"]["worker.py"] = sha256(self.source)
        self._write_authority()

        inventory = _build_inventory_from_registry(self.registry_path, "sample")
        by_id = {
            operation["inventory_id"]: operation
            for operation in inventory["operations"]
        }
        first = by_id[inventory["roots"][0]]
        second = by_id[first["successors"][0]]

        self.assertEqual(
            [first["external_call"]["callee"], second["external_call"]["callee"]],
            ["bool", "str"],
        )

    def test_forwarding_wrappers_cannot_add_deterministic_credit(self) -> None:
        baseline = _build_inventory_from_registry(self.registry_path, "sample")
        baseline_count = len(baseline["operations"])
        self.assertEqual(baseline_count, 1)
        self.assertTrue(
            all(not operation["credit_eligible"] for operation in baseline["operations"])
        )
        self.source.write_text(
            "def collect(value):\n"
            "    return wrapper(value)\n\n"
            "def wrapper(value):\n"
            "    return decide(value)\n\n"
            "def decide(value):\n"
            "    return bool(value)\n",
            encoding="utf-8",
        )
        self.process["file_hashes"]["worker.py"] = sha256(self.source)
        self._write_authority()

        wrapped = _build_inventory_from_registry(self.registry_path, "sample")

        wrapped_symbols = {
            item["source"]["symbol"]: item
            for item in wrapped["symbols"]
        }
        self.assertEqual(len(wrapped["operations"]), baseline_count)
        self.assertEqual(
            [op["external_call"]["callee"] for op in wrapped["operations"]],
            ["bool"],
        )
        self.assertTrue(
            all(
                not operation["credit_eligible"]
                for operation in wrapped["operations"]
            )
        )
        self.assertFalse(wrapped_symbols["wrapper"]["credit_eligible"])
        self.assertFalse(wrapped_symbols["decide"]["credit_eligible"])

    def test_semantically_redundant_chain_cannot_claim_credit(self) -> None:
        self.source.write_text(
            "def collect(value):\n"
            "    first = bool(False)\n"
            "    second = bool(first)\n"
            "    return str(second)\n",
            encoding="utf-8",
        )
        self.process["file_hashes"]["worker.py"] = sha256(self.source)
        self._write_authority()

        inventory = _build_inventory_from_registry(self.registry_path, "sample")

        self.assertEqual(len(inventory["operations"]), 3)
        self.assertTrue(
            all(
                not operation["credit_eligible"]
                for operation in inventory["operations"]
            )
        )

    def test_discarded_or_dead_builtin_calls_cannot_pad_inventory(self) -> None:
        # v3: a discarded call statement is admitted — and must appear as an
        # inventoried operation, never silent padding
        self.source.write_text(
            "def collect(value):\n"
            "    str(value)\n"
            "    return bool(value)\n",
            encoding="utf-8",
        )
        self.process["file_hashes"]["worker.py"] = sha256(self.source)
        self._write_authority()
        inventory = _build_inventory_from_registry(self.registry_path, "sample")
        callees = sorted(op["external_call"]["callee"] for op in inventory["operations"])
        self.assertEqual(callees, ["bool", "str"])
        # a call result never consumed is still refused
        self.source.write_text(
            "def collect(value):\n"
            "    unused = str(value)\n"
            "    return bool(value)\n",
            encoding="utf-8",
        )
        self.process["file_hashes"]["worker.py"] = sha256(self.source)
        self._write_authority()
        self.assert_block(
            "SOURCE_UNSUPPORTED_GRAMMAR",
            lambda: _build_inventory_from_registry(self.registry_path, "sample"),
        )

    def test_adapter_must_reach_bound_source_entrypoint(self) -> None:
        self.adapter.write_text(
            "def execute(value):\n"
            "    return value\n",
            encoding="utf-8",
        )
        self.process["file_hashes"]["adapter.py"] = sha256(self.adapter)
        self._write_authority()

        self.assert_block(
            "ADAPTER_ENTRYPOINT_DISCONNECTED",
            lambda: _build_inventory_from_registry(self.registry_path, "sample"),
        )

    def test_zero_work_process_is_blocked(self) -> None:
        self.source.write_text(
            "def collect(value):\n"
            "    return value\n",
            encoding="utf-8",
        )
        self.process["file_hashes"]["worker.py"] = sha256(self.source)
        self._write_authority()

        self.assert_block(
            "ZERO_WORK_PROCESS",
            lambda: _build_inventory_from_registry(self.registry_path, "sample"),
        )

    def test_duplicate_json_keys_fail_closed(self) -> None:
        payload = self.process_path.read_text(encoding="utf-8")
        payload = payload.replace(
            '"process_id": "sample"',
            '"process_id": "other", "process_id": "sample"',
            1,
        )
        self.process_path.write_text(payload, encoding="utf-8")

        self.assert_block(
            "AUTHORITY_MALFORMED",
            lambda: _build_inventory_from_registry(self.registry_path, "sample"),
        )

    def test_exact_inventory_comparison_accepts_authority_output(self) -> None:
        inventory = _build_inventory_from_registry(self.registry_path, "sample")

        verdict = _compare_inventory_from_registry(
            self.registry_path, "sample", inventory
        )

        self.assertEqual(verdict["verdict"], "INVENTORY_PASS")
        self.assertNotEqual(verdict["verdict"], "REALIZED_PASS")
        self.assertEqual(verdict["operation_count"], 1)
        self.assertEqual(verdict["structural_node_count"], 4)
        self.assertFalse(verdict["d85_admission"])

    def test_inventory_id_binds_canonical_source_root(self) -> None:
        first = _build_inventory_from_registry(self.registry_path, "sample")
        other_root = self.root / "other-repo"
        other_root.mkdir()
        (other_root / "worker.py").write_bytes(self.source.read_bytes())
        (other_root / "adapter.py").write_bytes(self.adapter.read_bytes())
        self.process["source_root"] = str(other_root)
        self._write_authority()

        second = _build_inventory_from_registry(self.registry_path, "sample")

        self.assertNotEqual(
            first["operations"][0]["inventory_id"],
            second["operations"][0]["inventory_id"],
        )

    def test_submitted_padding_is_blocked(self) -> None:
        inventory = _build_inventory_from_registry(self.registry_path, "sample")
        padded = json.loads(json.dumps(inventory))
        padded["operations"].append(json.loads(json.dumps(padded["operations"][0])))
        padded["operations"][-1]["inventory_id"] = "sha256:" + "0" * 64

        self.assert_block(
            "INVENTORY_MISMATCH",
            lambda: _compare_inventory_from_registry(
                self.registry_path, "sample", padded
            ),
        )

    def test_node_split_is_blocked(self) -> None:
        inventory = _build_inventory_from_registry(self.registry_path, "sample")
        split = json.loads(json.dumps(inventory))
        split["operations"][0]["source"]["end_line"] -= 1
        split["operations"].append(json.loads(json.dumps(split["operations"][0])))
        split["operations"][-1]["source"]["start_line"] += 1
        split["operations"][-1]["inventory_id"] = "sha256:" + "1" * 64

        self.assert_block(
            "INVENTORY_MISMATCH",
            lambda: _compare_inventory_from_registry(
                self.registry_path, "sample", split
            ),
        )

    def test_duplicate_entrypoint_binding_is_blocked(self) -> None:
        self.process["entrypoints"].append(
            json.loads(json.dumps(self.process["entrypoints"][0]))
        )
        self._write_authority()

        self.assert_block(
            "AUTHORITY_DUPLICATE_BINDING",
            lambda: _build_inventory_from_registry(self.registry_path, "sample"),
        )

    def test_hidden_reachable_symbol_changes_the_extracted_inventory(self) -> None:
        stale = _build_inventory_from_registry(self.registry_path, "sample")
        self.source.write_text(
            "def collect(value):\n"
            "    return decide(value)\n\n"
            "def decide(value):\n"
            "    return hidden(value)\n\n"
            "def hidden(value):\n"
            "    return bool(value)\n",
            encoding="utf-8",
        )
        self.process["file_hashes"]["worker.py"] = sha256(self.source)
        self._write_authority()

        current = _build_inventory_from_registry(self.registry_path, "sample")
        self.assertEqual(
            {
                item["source"]["symbol"]
                for item in current["symbols"]
            },
            {"collect", "decide", "execute", "hidden", "__module_init__"},
        )
        self.assert_block(
            "INVENTORY_MISMATCH",
            lambda: _compare_inventory_from_registry(
                self.registry_path, "sample", stale
            ),
        )

    def test_reachable_nested_function_is_not_downgraded_to_external(self) -> None:
        self.source.write_text(
            "def collect(value):\n"
            "    def hidden(item):\n"
            "        return bool(item)\n"
            "    return hidden(value)\n",
            encoding="utf-8",
        )
        self.process["file_hashes"]["worker.py"] = sha256(self.source)
        self._write_authority()

        inventory = _build_inventory_from_registry(self.registry_path, "sample")

        self.assertEqual(
            {
                item["source"]["symbol"]
                for item in inventory["symbols"]
            },
            {"collect", "collect.hidden", "execute", "__module_init__"},
        )

    def test_local_callable_alias_fails_closed(self) -> None:
        self.source.write_text(
            "def collect(value):\n"
            "    fn = decide\n"
            "    return fn(value)\n\n"
            "def decide(value):\n"
            "    return bool(value)\n",
            encoding="utf-8",
        )
        self.process["file_hashes"]["worker.py"] = sha256(self.source)
        self._write_authority()

        self.assert_block(
            "SOURCE_DYNAMIC_CALL",
            lambda: _build_inventory_from_registry(self.registry_path, "sample"),
        )

    def test_higher_order_callback_is_outside_closed_grammar(self) -> None:
        self.source.write_text(
            "def collect(values):\n"
            "    return map(decide, values)\n\n"
            "def decide(value):\n"
            "    return bool(value)\n",
            encoding="utf-8",
        )
        self.process["file_hashes"]["worker.py"] = sha256(self.source)
        self._write_authority()

        self.assert_block(
            "SOURCE_DYNAMIC_CALL",
            lambda: _build_inventory_from_registry(self.registry_path, "sample"),
        )

    def test_unresolved_higher_order_callback_fails_closed(self) -> None:
        self.source.write_text(
            "def collect(values, callback):\n"
            "    return sorted(values, key=callback)\n",
            encoding="utf-8",
        )
        self.process["file_hashes"]["worker.py"] = sha256(self.source)
        self._write_authority()

        self.assert_block(
            "SOURCE_DYNAMIC_CALL",
            lambda: _build_inventory_from_registry(self.registry_path, "sample"),
        )

    def test_iter_sentinel_callback_fails_closed(self) -> None:
        self.source.write_text(
            "def collect(value, callback):\n"
            "    return iter(callback, 0)\n",
            encoding="utf-8",
        )
        self.process["file_hashes"]["worker.py"] = sha256(self.source)
        self._write_authority()

        self.assert_block(
            "SOURCE_DYNAMIC_CALL",
            lambda: _build_inventory_from_registry(self.registry_path, "sample"),
        )

    def test_single_argument_iter_remains_admissible(self) -> None:
        self.source.write_text(
            "def collect(value):\n"
            "    return iter(value)\n",
            encoding="utf-8",
        )
        self.process["file_hashes"]["worker.py"] = sha256(self.source)
        self._write_authority()

        inventory = _build_inventory_from_registry(self.registry_path, "sample")
        self.assertEqual(len(inventory["operations"]), 1)
        self.assertEqual(
            inventory["operations"][0]["external_call"]["callee"], "iter"
        )
        self.assertFalse(inventory["operations"][0]["credit_eligible"])

    def test_local_function_passed_as_data_cannot_pad_inventory(self) -> None:
        self.source.write_text(
            "def collect(value):\n"
            "    print(decide)\n"
            "    return value\n\n"
            "def decide(value):\n"
            "    return bool(value)\n",
            encoding="utf-8",
        )
        self.process["file_hashes"]["worker.py"] = sha256(self.source)
        self._write_authority()

        self.assert_block(
            "SOURCE_DYNAMIC_CALL",
            lambda: _build_inventory_from_registry(self.registry_path, "sample"),
        )

    def test_local_callable_cannot_escape_as_data(self) -> None:
        cases = {
            "direct": (
                "def collect(value):\n"
                "    return decide\n\n"
                "def decide(value):\n"
                "    return bool(value)\n"
            ),
            "collection": (
                "def collect(value):\n"
                "    return [decide]\n\n"
                "def decide(value):\n"
                "    return bool(value)\n"
            ),
        }
        for name, source in cases.items():
            with self.subTest(name=name):
                self.source.write_text(source, encoding="utf-8")
                self.process["file_hashes"]["worker.py"] = sha256(self.source)
                self._write_authority()
                self.assert_block(
                    "SOURCE_DYNAMIC_CALL",
                    lambda: _build_inventory_from_registry(
                        self.registry_path, "sample"
                    ),
                )

    def test_dynamic_code_builtins_fail_closed(self) -> None:
        cases = {
            "eval": "def collect(value):\n    return eval(value)\n",
            "exec": "def collect(value):\n    exec(value)\n    return True\n",
            "compile": "def collect(value):\n    return compile(value, 'x', 'exec')\n",
            "__import__": "def collect(value):\n    return __import__(value)\n",
        }
        for name, source in cases.items():
            with self.subTest(name=name):
                self.source.write_text(source, encoding="utf-8")
                self.process["file_hashes"]["worker.py"] = sha256(self.source)
                self._write_authority()
                self.assert_block(
                    "SOURCE_DYNAMIC_CALL",
                    lambda: _build_inventory_from_registry(
                        self.registry_path, "sample"
                    ),
                )

    def test_callback_parameter_call_fails_closed(self) -> None:
        self.source.write_text(
            "def collect(value, callback):\n"
            "    return callback(value)\n",
            encoding="utf-8",
        )
        self.process["file_hashes"]["worker.py"] = sha256(self.source)
        self._write_authority()

        self.assert_block(
            "SOURCE_DYNAMIC_CALL",
            lambda: _build_inventory_from_registry(self.registry_path, "sample"),
        )

    def test_parameter_or_local_cannot_shadow_reachable_symbol(self) -> None:
        cases = {
            "parameter": (
                "def collect(value, decide):\n"
                "    return decide(value)\n\n"
                "def decide(value):\n"
                "    return bool(value)\n"
            ),
            "builtin_parameter": (
                "def collect(value, bool):\n"
                "    return bool(value)\n"
            ),
            "local": (
                "def collect(value):\n"
                "    decide = value\n"
                "    return decide(value)\n\n"
                "def decide(value):\n"
                "    return bool(value)\n"
            ),
        }
        for name, source in cases.items():
            with self.subTest(name=name):
                self.source.write_text(source, encoding="utf-8")
                self.process["file_hashes"]["worker.py"] = sha256(self.source)
                self._write_authority()
                self.assert_block(
                    "SOURCE_DYNAMIC_CALL",
                    lambda: _build_inventory_from_registry(
                        self.registry_path, "sample"
                    ),
                )

    def test_parameter_cannot_shadow_imported_module(self) -> None:
        helper = self.source_root / "helper.py"
        helper.write_text(
            "def decide(value):\n"
            "    return bool(value)\n",
            encoding="utf-8",
        )
        self.source.write_text(
            "import helper\n\n"
            "def collect(value, helper):\n"
            "    return helper.decide(value)\n",
            encoding="utf-8",
        )
        self.process["file_hashes"]["helper.py"] = sha256(helper)
        self.process["file_hashes"]["worker.py"] = sha256(self.source)
        self._write_authority()

        self.assert_block(
            "SOURCE_DYNAMIC_CALL",
            lambda: _build_inventory_from_registry(self.registry_path, "sample"),
        )

    def test_module_import_and_function_binding_cannot_collide(self) -> None:
        helper = self.source_root / "helper.py"
        helper.write_text(
            "def decide(value):\n"
            "    return bool(value)\n",
            encoding="utf-8",
        )
        self.source.write_text(
            "import helper\n\n"
            "def helper(value):\n"
            "    return value\n\n"
            "def collect(value):\n"
            "    return helper.decide(value)\n",
            encoding="utf-8",
        )
        self.process["file_hashes"]["helper.py"] = sha256(helper)
        self.process["file_hashes"]["worker.py"] = sha256(self.source)
        self._write_authority()

        self.assert_block(
            "SOURCE_UNSUPPORTED_GRAMMAR",
            lambda: _build_inventory_from_registry(self.registry_path, "sample"),
        )

    def test_getattr_dispatch_fails_closed(self) -> None:
        self.source.write_text(
            "def collect(value, name):\n"
            "    return getattr(value, name)()\n",
            encoding="utf-8",
        )
        self.process["file_hashes"]["worker.py"] = sha256(self.source)
        self._write_authority()

        self.assert_block(
            "SOURCE_DYNAMIC_CALL",
            lambda: _build_inventory_from_registry(self.registry_path, "sample"),
        )

    def test_unsupported_execution_grammar_fails_closed(self) -> None:
        cases = {
            "decorator": (
                "def deco(fn):\n"
                "    return fn\n\n"
                "@deco\n"
                "def collect(value):\n"
                "    return value\n"
            ),
            "class": (
                "class Hidden:\n"
                "    def decide(self, value):\n"
                "        return value\n\n"
                "def collect(value):\n"
                "    return value\n"
            ),
            "tuple_assign": (
                "def bootstrap():\n"
                "    return True\n\n"
                "a, b = 1, 2\n\n"
                "def collect(value):\n"
                "    return value\n"
            ),
            "monkey_patch": (
                "def collect(value):\n"
                "    value.handler = collect\n"
                "    return value\n"
            ),
            "unreachable_after_return": (
                "def collect(value):\n"
                "    return bool(value)\n"
                "    print(value)\n"
            ),
            "async_function": (
                "async def collect(value):\n"
                "    return bool(value)\n"
            ),
        }
        for name, source in cases.items():
            with self.subTest(name=name):
                self.source.write_text(source, encoding="utf-8")
                self.process["file_hashes"]["worker.py"] = sha256(self.source)
                self._write_authority()
                self.assert_block(
                    "SOURCE_UNSUPPORTED_GRAMMAR",
                    lambda: _build_inventory_from_registry(
                        self.registry_path, "sample"
                    ),
                )

    def test_external_import_fails_closed(self) -> None:
        self.source.write_text(
            "import os\n\n"
            "def collect(value):\n"
            "    return os.fspath(value)\n",
            encoding="utf-8",
        )
        self.process["file_hashes"]["worker.py"] = sha256(self.source)
        self._write_authority()

        self.assert_block(
            "SOURCE_EXTERNAL_IMPORT",
            lambda: _build_inventory_from_registry(self.registry_path, "sample"),
        )

    def test_declared_external_module_call_binds_initialization_without_importing(self) -> None:
        external = self.root / "external"
        external.mkdir()
        model_sdk = external / "model_sdk.py"
        model_sdk.write_text(
            "raise RuntimeError('inventory must not import this module')\n"
            "\n"
            "def generate(value):\n"
            "    return value\n",
            encoding="utf-8",
        )
        self.source.write_text(
            "import model_sdk\n\n"
            "def collect(value):\n"
            "    return model_sdk.generate(value)\n",
            encoding="utf-8",
        )
        self.process["file_hashes"]["worker.py"] = sha256(self.source)
        self.process["external_modules"] = [
            {
                "module": "model_sdk",
                "artifact_path": str(model_sdk),
                "artifact_sha256": sha256(model_sdk),
                "allowed_calls": ["model_sdk.generate"],
            }
        ]
        self._write_authority()

        sys.path.insert(0, str(external))
        try:
            inventory = _build_inventory_from_registry(
                self.registry_path, "sample"
            )
        finally:
            sys.path.remove(str(external))
        self.assertEqual(len(inventory["operations"]), 2)
        operation = next(
            op for op in inventory["operations"]
            if op["external_call"]["callee"] == "model_sdk.generate"
        )
        self.assertEqual(operation["operation_kind"], "EXTERNAL_MODULE_CALL")
        initialization = operation["external_call"]["module_initialization"]
        self.assertEqual(initialization["origin"], str(model_sdk.resolve()))
        self.assertEqual(initialization["sha256"], sha256(model_sdk))
        # resolver bumped to static-source.v2: packages, dotted modules,
        # builtin-executable binding, full-chain call surfaces (d85.py amendment)
        self.assertEqual(
            initialization["resolver"], "rig.d85.static-source.v2"
        )
        self.assertFalse(operation["credit_eligible"])
        self.assertFalse(initialization["runtime_loader_proven"])
        self.assertTrue(initialization["runtime_loader_proof_required"])

    def test_declared_external_call_must_exist_in_locked_module(self) -> None:
        external = self.root / "external"
        external.mkdir()
        model_sdk = external / "model_sdk.py"
        model_sdk.write_text(
            "def generate(value):\n"
            "    return value\n",
            encoding="utf-8",
        )
        self.source.write_text(
            "import model_sdk\n\n"
            "def collect(value):\n"
            "    return model_sdk.missing(value)\n",
            encoding="utf-8",
        )
        self.process["file_hashes"]["worker.py"] = sha256(self.source)
        self.process["external_modules"] = [
            {
                "module": "model_sdk",
                "artifact_path": str(model_sdk),
                "artifact_sha256": sha256(model_sdk),
                "allowed_calls": ["model_sdk.missing"],
            }
        ]
        self._write_authority()
        sys.path.insert(0, str(external))
        try:
            self.assert_block(
                "EXTERNAL_CALL_UNRESOLVED",
                lambda: _build_inventory_from_registry(
                    self.registry_path, "sample"
                ),
            )
        finally:
            sys.path.remove(str(external))


    def test_breakpoint_dynamic_builtin_fails_closed(self) -> None:
        self.source.write_text(
            "def collect(value):\n"
            "    breakpoint()\n"
            "    return bool(value)\n",
            encoding="utf-8",
        )
        self.process["file_hashes"]["worker.py"] = sha256(self.source)
        self._write_authority()

        self.assert_block(
            "SOURCE_DYNAMIC_CALL",
            lambda: _build_inventory_from_registry(self.registry_path, "sample"),
        )

    def test_external_callable_value_escape_fails_closed(self) -> None:
        external = self.root / "external"
        external.mkdir()
        model_sdk = external / "model_sdk.py"
        model_sdk.write_text(
            "def generate(value):\n"
            "    return value\n",
            encoding="utf-8",
        )
        self.source.write_text(
            "from model_sdk import generate\n\n"
            "def collect(value):\n"
            "    return generate\n",
            encoding="utf-8",
        )
        self.process["file_hashes"]["worker.py"] = sha256(self.source)
        self.process["external_modules"] = [
            {
                "module": "model_sdk",
                "artifact_path": str(model_sdk),
                "artifact_sha256": sha256(model_sdk),
                "allowed_calls": ["model_sdk.generate"],
            }
        ]
        self._write_authority()
        sys.path.insert(0, str(external))
        try:
            self.assert_block(
                "SOURCE_DYNAMIC_CALL",
                lambda: _build_inventory_from_registry(
                    self.registry_path, "sample"
                ),
            )
        finally:
            sys.path.remove(str(external))
    def test_preloaded_external_module_fails_closed(self) -> None:
        external = self.root / "external"
        external.mkdir()
        model_sdk = external / "model_sdk.py"
        model_sdk.write_text(
            "def generate(value):\n"
            "    return value\n",
            encoding="utf-8",
        )
        self.source.write_text(
            "import model_sdk\n\n"
            "def collect(value):\n"
            "    return model_sdk.generate(value)\n",
            encoding="utf-8",
        )
        self.process["file_hashes"]["worker.py"] = sha256(self.source)
        self.process["external_modules"] = [
            {
                "module": "model_sdk",
                "artifact_path": str(model_sdk),
                "artifact_sha256": sha256(model_sdk),
                "allowed_calls": ["model_sdk.generate"],
            }
        ]
        self._write_authority()
        sys.path.insert(0, str(external))
        sys.modules["model_sdk"] = types.ModuleType("model_sdk")
        try:
            self.assert_block(
                "EXTERNAL_MODULE_LOADER_STATE",
                lambda: _build_inventory_from_registry(
                    self.registry_path, "sample"
                ),
            )
        finally:
            sys.modules.pop("model_sdk", None)
            sys.path.remove(str(external))

    def test_external_loader_must_resolve_the_locked_bytes(self) -> None:
        locked = self.root / "locked"
        runtime = self.root / "runtime"
        locked.mkdir()
        runtime.mkdir()
        locked_module = locked / "model_sdk.py"
        runtime_module = runtime / "model_sdk.py"
        locked_module.write_text(
            "def generate(value):\n"
            "    return value\n",
            encoding="utf-8",
        )
        runtime_module.write_text(
            "def generate(value):\n"
            "    return 'redirected'\n",
            encoding="utf-8",
        )
        self.source.write_text(
            "import model_sdk\n\n"
            "def collect(value):\n"
            "    return model_sdk.generate(value)\n",
            encoding="utf-8",
        )
        self.process["file_hashes"]["worker.py"] = sha256(self.source)
        self.process["external_modules"] = [
            {
                "module": "model_sdk",
                "artifact_path": str(locked_module),
                "artifact_sha256": sha256(locked_module),
                "allowed_calls": ["model_sdk.generate"],
            }
        ]
        self._write_authority()
        sys.path[:0] = [str(runtime), str(locked)]
        try:
            self.assert_block(
                "EXTERNAL_MODULE_LOADER_MISMATCH",
                lambda: _build_inventory_from_registry(
                    self.registry_path, "sample"
                ),
            )
        finally:
            del sys.path[:2]

    def test_unused_external_module_declaration_is_padding(self) -> None:
        external = self.root / "external"
        external.mkdir()
        model_sdk = external / "model_sdk.py"
        model_sdk.write_text(
            "def generate(value):\n"
            "    return value\n",
            encoding="utf-8",
        )
        self.process["external_modules"] = [
            {
                "module": "model_sdk",
                "artifact_path": str(model_sdk),
                "artifact_sha256": sha256(model_sdk),
                "allowed_calls": ["model_sdk.generate"],
            }
        ]
        self._write_authority()
        sys.path.insert(0, str(external))
        try:
            self.assert_block(
                "AUTHORITY_PADDING",
                lambda: _build_inventory_from_registry(
                    self.registry_path, "sample"
                ),
            )
        finally:
            sys.path.remove(str(external))

    def test_unhashed_local_module_cannot_hide_reachable_operation(self) -> None:
        helper = self.source_root / "helper.py"
        helper.write_text(
            "def decide(value):\n"
            "    return bool(value)\n",
            encoding="utf-8",
        )
        self.source.write_text(
            "import helper\n\n"
            "def collect(value):\n"
            "    return helper.decide(value)\n",
            encoding="utf-8",
        )
        self.process["file_hashes"]["worker.py"] = sha256(self.source)
        self._write_authority()

        self.assert_block(
            "UNHASHED_REACHABLE_FILE",
            lambda: _build_inventory_from_registry(self.registry_path, "sample"),
        )

    def test_function_local_import_cannot_hide_local_module(self) -> None:
        helper = self.source_root / "helper.py"
        helper.write_text(
            "def decide(value):\n"
            "    return bool(value)\n",
            encoding="utf-8",
        )
        self.source.write_text(
            "def collect(value):\n"
            "    from helper import decide\n"
            "    return decide(value)\n",
            encoding="utf-8",
        )
        self.process["file_hashes"]["worker.py"] = sha256(self.source)
        self._write_authority()

        self.assert_block(
            "SOURCE_UNSUPPORTED_GRAMMAR",
            lambda: _build_inventory_from_registry(self.registry_path, "sample"),
        )

    def test_source_change_requires_new_authority_version(self) -> None:
        self.source.write_text("def collect(value):\n    return value\n", encoding="utf-8")

        self.assert_block(
            "SOURCE_HASH_MISMATCH",
            lambda: _build_inventory_from_registry(self.registry_path, "sample"),
        )

    def test_parser_uses_the_hash_verified_snapshot(self) -> None:
        snapshot = self.source.read_bytes()
        self.source.write_text("this is not python\n", encoding="utf-8")

        parsed = _parse_module(self.source, "worker.py", snapshot)

        self.assertEqual(set(parsed.symbols), {"collect", "decide"})

    def test_authority_paths_cannot_alias_one_inode(self) -> None:
        alias = self.source_root / "worker_alias.py"
        os.link(self.source, alias)
        self.process["file_hashes"]["worker_alias.py"] = sha256(alias)
        self._write_authority()

        self.assert_block(
            "AUTHORITY_DUPLICATE_BINDING",
            lambda: _build_inventory_from_registry(self.registry_path, "sample"),
        )

    def test_external_artifact_cannot_alias_hashed_source(self) -> None:
        external = self.root / "external"
        external.mkdir()
        model_sdk = external / "model_sdk.py"
        os.link(self.source, model_sdk)
        self.process["external_modules"] = [
            {
                "module": "model_sdk",
                "artifact_path": str(model_sdk),
                "artifact_sha256": sha256(model_sdk),
                "allowed_calls": ["model_sdk.collect"],
            }
        ]
        self._write_authority()
        sys.path.insert(0, str(external))
        try:
            self.assert_block(
                "AUTHORITY_DUPLICATE_BINDING",
                lambda: _build_inventory_from_registry(
                    self.registry_path, "sample"
                ),
            )
        finally:
            sys.path.remove(str(external))

    def test_two_external_modules_cannot_share_one_artifact_inode(self) -> None:
        external = self.root / "external"
        external.mkdir()
        model_sdk = external / "model_sdk.py"
        model_sdk.write_text(
            "def generate(value):\n"
            "    return value\n",
            encoding="utf-8",
        )
        model_api = external / "model_api.py"
        os.link(model_sdk, model_api)
        self.source.write_text(
            "import model_sdk\n\n"
            "def collect(value):\n"
            "    return model_sdk.generate(value)\n",
            encoding="utf-8",
        )
        self.process["file_hashes"]["worker.py"] = sha256(self.source)
        self.process["external_modules"] = [
            {
                "module": "model_sdk",
                "artifact_path": str(model_sdk),
                "artifact_sha256": sha256(model_sdk),
                "allowed_calls": ["model_sdk.generate"],
            },
            {
                "module": "model_api",
                "artifact_path": str(model_api),
                "artifact_sha256": sha256(model_api),
                "allowed_calls": ["model_api.generate"],
            },
        ]
        self._write_authority()
        sys.path.insert(0, str(external))
        try:
            self.assert_block(
                "AUTHORITY_DUPLICATE_BINDING",
                lambda: _build_inventory_from_registry(
                    self.registry_path, "sample"
                ),
            )
        finally:
            sys.path.remove(str(external))

    def test_source_path_cannot_escape_registered_root(self) -> None:
        outside = self.root / "outside.py"
        outside.write_text("def collect(value):\n    return value\n", encoding="utf-8")
        self.process["entrypoints"][0]["source_path"] = "../outside.py"
        self.process["file_hashes"]["../outside.py"] = sha256(outside)
        self._write_authority()

        self.assert_block(
            "SOURCE_ROOT_ESCAPE",
            lambda: _build_inventory_from_registry(self.registry_path, "sample"),
        )

    def test_registry_cannot_redirect_outside_authority_root(self) -> None:
        outside = self.root / "outside-authority.json"
        outside.write_text(json.dumps(self.process), encoding="utf-8")
        registry = {
            "schema": "rig.d85.authority-registry.v1",
            "processes": {"sample": "../outside-authority.json"},
        }
        self.registry_path.write_text(json.dumps(registry), encoding="utf-8")

        self.assert_block(
            "AUTHORITY_ROOT_ESCAPE",
            lambda: _build_inventory_from_registry(self.registry_path, "sample"),
        )

    def test_empty_production_registry_fails_closed_per_process(self) -> None:
        self.registry_path.write_text(
            json.dumps(
                {"schema": "rig.d85.authority-registry.v1", "processes": {}}
            ),
            encoding="utf-8",
        )

        self.assert_block(
            "UNKNOWN_PROCESS",
            lambda: _build_inventory_from_registry(self.registry_path, "sample"),
        )



class DeterminismInventoryCliTests(unittest.TestCase):
    def test_unknown_production_process_is_a_json_block(self) -> None:
        result = subprocess.run(
            [str(CLI), "inventory", "not-registered"],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
            timeout=15,
        )

        self.assertEqual(result.returncode, 2, result.stderr)
        payload = json.loads(result.stdout)
        self.assertEqual(payload["verdict"], "BLOCK")
        self.assertEqual(payload["reason"], "UNKNOWN_PROCESS")


class ModuleInitV2Tests(DeterminismInventoryTests):
    """Permanent coverage for grammar v2: ordered module-init operations,
    import-init zero credit, guarded-main non-duplication, initializer escapes,
    and the data_hashes resource binding."""

    def test_init_path_home_produces_one_operation_before_main(self) -> None:
        self.source.write_text(
            "from pathlib import Path\n\n"
            "ROOT = Path.home()\n\n"
            "def collect(value):\n"
            "    return str(value)\n",
            encoding="utf-8",
        )
        self.process["file_hashes"]["worker.py"] = sha256(self.source)
        pathlib_origin = __import__("d85")._deterministic_module_origin("pathlib")
        self.process["external_modules"] = [
            {
                "module": "pathlib",
                "artifact_path": str(pathlib_origin),
                "artifact_sha256": sha256(pathlib_origin),
                "allowed_calls": ["pathlib.Path", "pathlib.Path.home"],
            }
        ]
        self._write_authority()
        inventory = _build_inventory_from_registry(self.registry_path, "sample")
        ops = inventory["operations"]
        home_ops = [op for op in ops if op["external_call"]["callee"] == "pathlib.Path.home"]
        self.assertEqual(len(home_ops), 1)
        import_inits = [op for op in ops if op["operation_kind"] == "EXTERNAL_IMPORT_INIT"]
        self.assertEqual(len(import_inits), 1)
        self.assertFalse(import_inits[0]["credit_eligible"])
        self.assertEqual(import_inits[0]["external_call"]["callee"], "pathlib")
        self.assertEqual(inventory["roots"][0], import_inits[0]["inventory_id"])
        self.assertEqual(home_ops[0]["predecessors"], [import_inits[0]["inventory_id"]])

    def test_guarded_main_dispatch_is_not_duplicated(self) -> None:
        self.source.write_text(
            "BOOT = str(1)\n\n"
            "def main():\n"
            "    return str(BOOT)\n\n"
            "if __name__ == '__main__':\n"
            "    main()\n",
            encoding="utf-8",
        )
        self.process["file_hashes"].pop("adapter.py")
        self.process["file_hashes"]["worker.py"] = sha256(self.source)
        self.process["entrypoints"] = [
            {
                "source_path": "worker.py",
                "symbol": "main",
                "adapter_path": "worker.py",
                "adapter_operation": "main",
            }
        ]
        (self.source_root / "adapter.py").unlink()
        self._write_authority()
        inventory = _build_inventory_from_registry(self.registry_path, "sample")
        main_ops = [op for op in inventory["operations"] if ":main@" in op["execution_path"][-1]]
        self.assertEqual(len(main_ops), 1)
        kinds = [op["operation_kind"] for op in inventory["operations"]]
        self.assertEqual(kinds.count("EXTERNAL_CALL"), 2)  # str(1) init + str(BOOT) in main, once each

    def test_undeclared_init_external_call_blocks(self) -> None:
        self.source.write_text(
            "import os\n\n"
            "X = os.getuid()\n\n"
            "def collect(value):\n"
            "    return value\n",
            encoding="utf-8",
        )
        self.process["file_hashes"]["worker.py"] = sha256(self.source)
        os_origin = __import__("d85")._deterministic_module_origin("os")
        self.process["external_modules"] = [
            {
                "module": "os",
                "artifact_path": str(os_origin),
                "artifact_sha256": sha256(os_origin),
                "allowed_calls": ["os.fspath"],
            }
        ]
        self._write_authority()
        self.assert_block(
            "EXTERNAL_CALL_UNDECLARED",
            lambda: _build_inventory_from_registry(self.registry_path, "sample"),
        )

    def test_literal_only_init_is_not_padding(self) -> None:
        self.source.write_text(
            "LIMIT = 10\n\n"
            "def collect(value):\n"
            "    return str(value)\n",
            encoding="utf-8",
        )
        self.process["file_hashes"]["worker.py"] = sha256(self.source)
        self._write_authority()
        inventory = _build_inventory_from_registry(self.registry_path, "sample")
        for op in inventory["operations"]:
            self.assertNotIn("__module_init__", " ".join(op["execution_path"]))

    def test_lambda_init_blocks(self) -> None:
        self.source.write_text(
            "handler = lambda: 1\n\n"
            "def collect(value):\n"
            "    return value\n",
            encoding="utf-8",
        )
        self.process["file_hashes"]["worker.py"] = sha256(self.source)
        self._write_authority()
        self.assert_block(
            "SOURCE_UNSUPPORTED_GRAMMAR",
            lambda: _build_inventory_from_registry(self.registry_path, "sample"),
        )

    def test_comprehension_init_blocks(self) -> None:
        self.source.write_text(
            "ITEMS = [x for x in range(3)]\n\n"
            "def collect(value):\n"
            "    return value\n",
            encoding="utf-8",
        )
        self.process["file_hashes"]["worker.py"] = sha256(self.source)
        self._write_authority()
        self.assert_block(
            "SOURCE_UNSUPPORTED_GRAMMAR",
            lambda: _build_inventory_from_registry(self.registry_path, "sample"),
        )

    def test_callable_alias_init_blocks(self) -> None:
        self.source.write_text(
            "def collect(value):\n"
            "    return value\n\n"
            "handler = collect\n",
            encoding="utf-8",
        )
        self.process["file_hashes"]["worker.py"] = sha256(self.source)
        self._write_authority()
        self.assert_block(
            "SOURCE_UNSUPPORTED_GRAMMAR",
            lambda: _build_inventory_from_registry(self.registry_path, "sample"),
        )

    def test_data_hashes_green_and_bound_into_inventory(self) -> None:
        policy = self.source_root / "policy.json"
        policy.write_text('{"version": 1}\n', encoding="utf-8")
        self.process["data_hashes"] = {"policy.json": sha256(policy)}
        self._write_authority()
        inventory = _build_inventory_from_registry(self.registry_path, "sample")
        self.assertEqual(inventory["data_hashes"], {"policy.json": sha256(policy)})
        policy.write_text('{"version": 2}\n', encoding="utf-8")
        self.assert_block(
            "DATA_HASH_MISMATCH",
            lambda: _build_inventory_from_registry(self.registry_path, "sample"),
        )

    def test_data_hashes_escape_overlap_and_alias_block(self) -> None:
        self.process["data_hashes"] = {"../escape.json": "0" * 64}
        self._write_authority()
        self.assert_block(
            "SOURCE_ROOT_ESCAPE",
            lambda: _build_inventory_from_registry(self.registry_path, "sample"),
        )
        self.process["data_hashes"] = {"worker.py": sha256(self.source)}
        self._write_authority()
        self.assert_block(
            "AUTHORITY_MALFORMED",
            lambda: _build_inventory_from_registry(self.registry_path, "sample"),
        )
        alias = self.source_root / "policy-alias.json"
        os.link(self.source, alias)
        self.process["data_hashes"] = {"policy-alias.json": sha256(alias)}
        self._write_authority()
        self.assert_block(
            "AUTHORITY_DUPLICATE_BINDING",
            lambda: _build_inventory_from_registry(self.registry_path, "sample"),
        )


class StaticSourceV2Tests(unittest.TestCase):
    """Regression coverage for the resolver rig.d85.static-source.v2 amendment:
    dotted submodule resolution, recursive package binding, builtin executable
    binding, full-chain call surfaces, and the stdlib preload exemption."""

    def setUp(self) -> None:
        import d85  # noqa: PLC0415

        self.d85 = d85
        self.executable = Path(sys.executable).resolve()
        self.exe_sha = hashlib.sha256(self.executable.read_bytes()).hexdigest()

    def _entry(self, module: str, calls: list[str], artifact: Path | None = None,
               sha: str | None = None, package_modules: list[dict[str, str]] | None = None) -> dict:
        artifact = artifact or self.d85._deterministic_module_origin(module)
        sha = sha or hashlib.sha256(artifact.read_bytes()).hexdigest()
        entry = {
            "module": module,
            "artifact_path": str(artifact),
            "artifact_sha256": sha,
            "allowed_calls": calls,
        }
        if package_modules is not None:
            entry["package_modules"] = package_modules
        return entry

    def _package_entries(self, package: str) -> list[dict[str, str]]:
        init = self.d85._deterministic_module_origin(package)
        return [
            {"path": str(member), "sha256": hashlib.sha256(member.read_bytes()).hexdigest()}
            for member in sorted(self.d85._package_reachable(init))
        ]

    def _assert_lock(self, entry: dict) -> None:
        self.d85._external_lock_entry(entry, Path("/nonexistent-source-root"), "fp", "ext[0]")

    def _assert_lock_block(self, code: str, entry: dict) -> None:
        with self.assertRaises(AdmissionBlock) as caught:
            self.d85._external_lock_entry(entry, Path("/nonexistent-source-root"), "fp", "ext[0]")
        self.assertEqual(caught.exception.code, code)

    def test_dotted_submodule_resolves_and_chain_verifies(self) -> None:
        origin = self.d85._deterministic_module_origin("urllib.request")
        self.assertEqual(origin.name, "request.py")
        self.assertEqual(origin.parent.name, "urllib")
        self._assert_lock(self._entry("urllib.request", ["urllib.request.urlopen"]))

    def test_dotted_callee_has_no_duplicated_segment(self) -> None:
        import ast  # noqa: PLC0415

        tree = ast.parse("import urllib.request\nurllib.request.urlopen('http://x')\n")
        imports = self.d85._index_imports(tree, "fixture")
        call = next(node for node in ast.walk(tree) if isinstance(node, ast.Call))
        callee, _ = self.d85._external_callee(
            call.func, imports, {"urllib.request": {"allowed_calls": ["urllib.request.urlopen"]}}, set()
        )
        self.assertEqual(callee, "urllib.request.urlopen")

    def test_package_init_without_binding_stays_blocked(self) -> None:
        self._assert_lock_block(
            "EXTERNAL_MODULE_PACKAGE_UNBOUND",
            self._entry("json", ["json.dumps"]),
        )

    def test_package_binding_green_and_member_tamper_red(self) -> None:
        members = self._package_entries("json")
        self.assertTrue(any(Path(m["path"]).name == "decoder.py" for m in members))
        self._assert_lock(self._entry("json", ["json.dumps", "json.loads"], package_modules=members))
        tampered = [dict(m) for m in members]
        tampered[0]["sha256"] = "0" * 64
        self._assert_lock_block(
            "PACKAGE_MODULE_HASH_MISMATCH",
            self._entry("json", ["json.dumps"], package_modules=tampered),
        )

    def test_builtin_binds_executable_only(self) -> None:
        self._assert_lock(
            self._entry("sys", ["sys.path.insert"], artifact=self.executable, sha=self.exe_sha)
        )
        not_the_exe = self.d85._deterministic_module_origin("json")
        with self.assertRaises(AdmissionBlock):
            self._assert_lock(
                self._entry(
                    "sys",
                    ["sys.path.insert"],
                    artifact=not_the_exe,
                    sha=hashlib.sha256(not_the_exe.read_bytes()).hexdigest(),
                )
            )

    def test_builtin_bogus_attribute_blocked(self) -> None:
        self._assert_lock_block(
            "EXTERNAL_CALL_UNRESOLVED",
            self._entry("sys", ["sys.no_such_attribute"], artifact=self.executable, sha=self.exe_sha),
        )

    def test_full_chain_bogus_tail_blocked(self) -> None:
        members = self._package_entries("json")
        self._assert_lock_block(
            "EXTERNAL_CALL_UNRESOLVED",
            self._entry("json", ["json.dumps.nope"], package_modules=members),
        )
        self._assert_lock_block(
            "EXTERNAL_CALL_UNRESOLVED",
            self._entry("json", ["json.loads.nope"], package_modules=members),
        )

    def test_stdlib_preload_exempt_nonstdlib_still_blocked(self) -> None:
        # json is preloaded in this very interpreter; stdlib-manifest members are
        # exempt because every proof input comes from disk, never from memory
        self.assertIn("json", sys.modules)
        self._assert_lock(self._entry("json", ["json.dumps"], package_modules=self._package_entries("json")))
        # a preloaded non-stdlib module stays fail-closed (substitution hostile)
        outside = Path(tempfile.mkdtemp(prefix="rig-d85-ext-"))
        (outside / "shadow_sdk.py").write_text("def generate(v):\n    return v\n", encoding="utf-8")
        sys.path.insert(0, str(outside))
        sys.modules["shadow_sdk"] = types.ModuleType("shadow_sdk")
        try:
            self._assert_lock_block(
                "EXTERNAL_MODULE_LOADER_STATE",
                self._entry("shadow_sdk", ["shadow_sdk.generate"], artifact=outside / "shadow_sdk.py"),
            )
        finally:
            sys.path.remove(str(outside))
            sys.modules.pop("shadow_sdk", None)

    def test_class_method_chain_resolves(self) -> None:
        self._assert_lock(
            self._entry("datetime", ["datetime.datetime.now", "datetime.datetime.fromisoformat"])
        )

    def test_dynamic_surface_member_blocked_assign_member_green(self) -> None:
        self._assert_lock(self._entry("hashlib", ["hashlib.new"]))
        self._assert_lock_block(
            "EXTERNAL_CALL_UNRESOLVED",
            self._entry("hashlib", ["hashlib.sha256"]),
        )
if __name__ == "__main__":
    unittest.main()
