from __future__ import annotations

from typing import Dict

from .guard import CommunicationGuard
from ..core import evaluate


def evaluate_node(state: Dict[str, object], text_key: str = "draft", channel: str = "email") -> Dict[str, object]:
    text = str(state.get(text_key, ""))
    report = evaluate(text, channel=channel)
    return {**state, "rig_report": report.to_dict(), "rig_can_ship": report.can_ship}


def guard_node(state: Dict[str, object], text_key: str = "draft", channel: str = "email") -> Dict[str, object]:
    guard = CommunicationGuard(channel=channel)
    result = guard.guard(str(state.get(text_key, "")))
    return {**state, text_key: result.text, "rig_report": result.report.to_dict(), "rig_can_ship": result.passed}


def optional_langgraph_callable():
    try:
        import langgraph  # type: ignore # noqa: F401
    except Exception:
        return None
    return guard_node
