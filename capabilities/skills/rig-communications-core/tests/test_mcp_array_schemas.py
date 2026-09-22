"""Gemini rejects the entire request if any advertised array omits items."""
import copy
import unittest

from rig_comms.mcp import handle


def check_array_items(node, path="schema"):
    if isinstance(node, dict):
        if node.get("type") == "array" and not node.get("items"):
            raise AssertionError(f"{path}: array requires an item schema")
        for key, value in node.items():
            check_array_items(value, f"{path}.{key}")
    elif isinstance(node, list):
        for index, value in enumerate(node):
            check_array_items(value, f"{path}[{index}]")


class GeminiSchemaTests(unittest.TestCase):
    def test_advertised_arrays_and_original_failure(self):
        tools = handle({"method": "tools/list"})["tools"]
        for tool in tools:
            check_array_items(tool["inputSchema"], tool["name"])
        audience = copy.deepcopy(next(t for t in tools if t["name"] == "comms.audience"))
        del audience["inputSchema"]["properties"]["known"]["items"]
        with self.assertRaisesRegex(AssertionError, "known: array requires"):
            check_array_items(audience["inputSchema"])


if __name__ == "__main__":
    unittest.main()
