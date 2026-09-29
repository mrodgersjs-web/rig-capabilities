"""Pydantic AI durable path (L4): serialize message history and continue the conversation.

Run: env -u PYTHONHOME -u PYTHONPATH ~/.rig/agentic-lab/pydantic-ai/.venv/bin/python hello_world_persist.py
Expected: prints "RESULT: HISTORY_OK turns=N", exit 0.
"""
from pydantic_ai import Agent
from pydantic_ai.messages import ModelMessagesTypeAdapter
from pydantic_ai.models.test import TestModel

agent = Agent(TestModel(), output_type=str)

r1 = agent.run_sync("First turn.")
msgs = r1.all_messages()

blob = ModelMessagesTypeAdapter.dump_json(msgs)
assert blob, "history serialized to empty bytes"
msgs2 = ModelMessagesTypeAdapter.validate_json(blob)
assert len(msgs2) == len(msgs), "history lost messages across the round-trip"

r2 = agent.run_sync("Second turn.", message_history=msgs2)
assert r2.output is not None, "no output on the continued run"
print(f"RESULT: HISTORY_OK turns={len(msgs2)} bytes={len(blob)}")
