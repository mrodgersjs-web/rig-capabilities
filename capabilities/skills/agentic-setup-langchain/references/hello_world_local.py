"""LangChain hello-world against a LOCAL OpenAI-compatible endpoint (L3).

Run: env -u PYTHONHOME -u PYTHONPATH ~/.rig/agentic-lab/langchain/.venv/bin/python hello_world_local.py
Expected: prints "RESULT: <non-empty model text>", exit 0. Fails loudly on empty content.
"""
import os

import importlib.metadata as m
from langchain_openai import ChatOpenAI

BASE = os.environ.get("LOCAL_LLM_BASE", "http://127.0.0.1:8771/v1")
MODEL = os.environ.get("LOCAL_LLM_MODEL", "qwen3.8-uncensored:27b")

print("VERSION: langchain-openai", m.version("langchain-openai"))

llm = ChatOpenAI(
    model=MODEL,
    base_url=BASE,
    api_key="local-not-a-secret",
    model_kwargs={"extra_body": {"chat_template_kwargs": {"enable_thinking": False}}},
)
msg = llm.invoke("Reply with exactly the word READY and nothing else.")
text = (msg.content or "").strip()
assert text, f"EMPTY content from {BASE} (thinking may be enabled, or endpoint down)"
print("RESULT:", text)
