from __future__ import annotations

from typing import Dict

from .guard import CommunicationGuard
from ..core import evaluate


def evaluate_tool(text: str, channel: str = "email") -> Dict[str, object]:
    return evaluate(text, channel=channel).to_dict()


def guard_tool(text: str, channel: str = "email") -> Dict[str, object]:
    result = CommunicationGuard(channel=channel).guard(text)
    return result.to_dict()


def optional_crewai_tool():
    try:
        import crewai  # type: ignore # noqa: F401
    except Exception:
        return None
    return guard_tool
