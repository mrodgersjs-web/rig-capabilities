"""Pydantic AI hello-world (L2): TestModel with validated structured output, no network.

Run: env -u PYTHONHOME -u PYTHONPATH ~/.rig/agentic-lab/pydantic-ai/.venv/bin/python hello_world_testmodel.py
Expected: prints "RESULT: TESTMODEL_OK output=...", exit 0.
"""
import importlib.metadata as m

from pydantic import BaseModel
from pydantic_ai import Agent
from pydantic_ai.models.test import TestModel

print("VERSION: pydantic-ai", m.version("pydantic-ai"))


class Out(BaseModel):
    answer: str


agent = Agent(TestModel(), output_type=Out)
result = agent.run_sync("Say hi.")
out = result.output
assert isinstance(out, Out), f"output is not validated Out: {out!r}"
assert out.answer, "empty answer field"
print("RESULT: TESTMODEL_OK output=", out)
