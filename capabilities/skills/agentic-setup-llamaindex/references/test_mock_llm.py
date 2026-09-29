"""Unit test for the MockLLM path. PLANT=1 injects a wrong expectation (must go red).

Run: .../python test_mock_llm.py            -> TEST_OK, exit 0
     PLANT=1 .../python test_mock_llm.py    -> AssertionError, exit 1
"""
import os

from llama_index.core.llms.mock import MockLLM


def test_mock_llm_deterministic() -> None:
    llm = MockLLM(max_tokens=4)
    got = llm.complete("ping").text
    expected = "WRONG_ON_PLANT" if os.environ.get("PLANT") == "1" else got
    assert got == expected, f"expected {expected!r}, got {got!r}"


test_mock_llm_deterministic()
print("TEST_OK")
