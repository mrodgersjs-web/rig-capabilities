from __future__ import annotations

from typing import Dict

from .guard import CommunicationGuard
from ..core import evaluate


class AutoGenRigGuard:
    def __init__(self, channel: str = "email"):
        self.guard = CommunicationGuard(channel=channel)

    def evaluate_reply(self, text: str) -> Dict[str, object]:
        return evaluate(text, channel=self.guard.channel).to_dict()

    def filter_reply(self, text: str) -> Dict[str, object]:
        return self.guard.guard(text).to_dict()


def optional_autogen_hook():
    try:
        import autogen  # type: ignore # noqa: F401
    except Exception:
        return None
    return AutoGenRigGuard
