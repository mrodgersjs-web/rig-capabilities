"""Pydantic AI hello-world against a LOCAL OpenAI-compatible endpoint (L3).

Run: env -u PYTHONHOME -u PYTHONPATH ~/.rig/agentic-lab/pydantic-ai/.venv/bin/python hello_world_local.py
Expected: prints "RESULT: <non-empty model text>", exit 0. Fails loudly on empty content.
"""
import os

import importlib.metadata as m
from pydantic_ai import Agent
from pydantic_ai.models.openai import OpenAIChatModel
from pydantic_ai.providers.openai import OpenAIProvider

BASE = os.environ.get("LOCAL_LLM_BASE", "http://127.0.0.1:8771/v1")
MODEL = os.environ.get("LOCAL_LLM_MODEL", "qwen3.8-uncensored:27b")

print("VERSION: pydantic-ai", m.version("pydantic-ai"))

model = OpenAIChatModel(
    MODEL,
    provider=OpenAIProvider(base_url=BASE, api_key="local-not-a-secret"),
)
agent = Agent(
    model,
    output_type=str,
    model_settings={"extra_body": {"chat_template_kwargs": {"enable_thinking": False}}},
)
result = agent.run_sync("Reply with exactly the word READY and nothing else.")
text = (result.output or "").strip()
assert text, f"EMPTY content from {BASE} (thinking may be enabled, or endpoint down)"
print("RESULT:", text)
