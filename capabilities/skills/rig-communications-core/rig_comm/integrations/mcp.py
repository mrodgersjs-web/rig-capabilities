from __future__ import annotations

from typing import Dict

from .guard import CommunicationGuard
from ..core import evaluate


def tool_definition() -> Dict[str, object]:
    return {
        "name": "rig.evaluate",
        "description": "Evaluate or guard outbound communication using RIG doctrine.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "text": {"type": "string"},
                "channel": {"type": "string", "default": "email"},
                "guard": {"type": "boolean", "default": False},
            },
            "required": ["text"],
        },
    }


def tool_call(text: str, channel: str = "email", guard: bool = False) -> Dict[str, object]:
    if guard:
        return CommunicationGuard(channel=channel).guard(text).to_dict()
    return evaluate(text, channel=channel).to_dict()
