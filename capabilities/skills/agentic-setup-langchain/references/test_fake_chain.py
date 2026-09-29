"""Unit test for the fake-model chain. PLANT=1 injects a wrong expectation (must go red).

Run: .../python test_fake_chain.py            -> TEST_OK, exit 0
     PLANT=1 .../python test_fake_chain.py    -> AssertionError, exit 1
"""
import os

from langchain_core.language_models.fake_chat_models import FakeListChatModel
from langchain_core.prompts import ChatPromptTemplate


def test_chain_scripted_reply() -> None:
    fake = FakeListChatModel(responses=["FAKE_REPLY_1"])
    chain = ChatPromptTemplate.from_messages([("human", "ping")]) | fake
    got = chain.invoke({}).content
    expected = "WRONG_ON_PLANT" if os.environ.get("PLANT") == "1" else "FAKE_REPLY_1"
    assert got == expected, f"expected {expected!r}, got {got!r}"


test_chain_scripted_reply()
print("TEST_OK")
