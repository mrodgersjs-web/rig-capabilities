"""LangChain hello-world (L2): deterministic fake model, no network, no key.

Run: env -u PYTHONHOME -u PYTHONPATH ~/.rig/agentic-lab/langchain/.venv/bin/python hello_world_fake.py
Expected: prints "RESULT: FAKE_REPLY_1", exit 0.
"""
import importlib.metadata as m

from langchain_core.language_models.fake_chat_models import FakeListChatModel
from langchain_core.prompts import ChatPromptTemplate

print("VERSION: langchain-core", m.version("langchain-core"))

fake = FakeListChatModel(responses=["FAKE_REPLY_1"])
chain = ChatPromptTemplate.from_messages([("human", "ping {x}")]) | fake
out = chain.invoke({"x": "hi"})
text = out.content if hasattr(out, "content") else str(out)
assert text == "FAKE_REPLY_1", f"unexpected content: {text!r}"
print("RESULT: FAKE_REPLY_1")
