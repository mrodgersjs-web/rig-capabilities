"""LlamaIndex hello-world against a LOCAL OpenAI-compatible endpoint (L3).

Run: env -u PYTHONHOME -u PYTHONPATH ~/.rig/agentic-lab/llamaindex/.venv/bin/python hello_world_local.py
Expected: prints "RESULT: <non-empty model text>", exit 0. Fails loudly on empty content.
"""
import os

import importlib.metadata as m
from llama_index.llms.openai_like import OpenAILike

BASE = os.environ.get("LOCAL_LLM_BASE", "http://127.0.0.1:8771/v1")
MODEL = os.environ.get("LOCAL_LLM_MODEL", "qwen3.8-uncensored:27b")

print("VERSION: llama-index-llms-openai-like", m.version("llama-index-llms-openai-like"))

llm = OpenAILike(
    model=MODEL,
    api_base=BASE,
    api_key="local-not-a-secret",
    is_chat_model=True,
    max_tokens=16,
    additional_kwargs={"extra_body": {"chat_template_kwargs": {"enable_thinking": False}}},
)
resp = llm.complete("Reply with exactly the word READY and nothing else.")
text = (resp.text or "").strip()
assert text, f"EMPTY content from {BASE} (thinking may be enabled, or endpoint down)"
print("RESULT:", text)
