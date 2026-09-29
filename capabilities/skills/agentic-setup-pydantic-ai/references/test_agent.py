"""Unit test for the TestModel agent. PLANT=1 injects a wrong expectation (must go red).

Run: .../python test_agent.py            -> TEST_OK, exit 0
     PLANT=1 .../python test_agent.py    -> AssertionError, exit 1
"""
import os

from pydantic import BaseModel
from pydantic_ai import Agent
from pydantic_ai.models.test import TestModel


class Out(BaseModel):
    answer: str


def test_agent_validated_output() -> None:
    agent = Agent(TestModel(), output_type=Out)
    out = agent.run_sync("Say hi.").output
    assert isinstance(out, Out), f"expected Out, got {type(out).__name__}"
    expected_type = str if os.environ.get("PLANT") == "1" else Out
    assert type(out) is expected_type, (
        f"planted failure check: expected {expected_type.__name__}, got {type(out).__name__}"
    )


test_agent_validated_output()
print("TEST_OK")
