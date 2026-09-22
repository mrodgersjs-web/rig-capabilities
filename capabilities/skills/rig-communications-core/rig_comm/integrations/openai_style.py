from __future__ import annotations

from typing import Dict

from .guard import CommunicationGuard
from ..core import evaluate


def tool_schema() -> Dict[str, object]:
    return {
        "type": "function",
        "function": {
            "name": "rig_evaluate",
            "description": "Evaluate outbound text using RIG protocol, formulas, and hard gates.",
            "parameters": {
                "type": "object",
                "properties": {
                    "text": {"type": "string"},
                    "channel": {"type": "string", "default": "email"},
                    "mode": {"type": "string", "enum": ["evaluate", "guard"], "default": "evaluate"},
                },
                "required": ["text"],
            },
        },
    }


def tool_handler(text: str, channel: str = "email", mode: str = "evaluate") -> Dict[str, object]:
    if mode == "guard":
        return CommunicationGuard(channel=channel).guard(text).to_dict()
    return evaluate(text, channel=channel).to_dict()
