"""D85 adapter for the CoSell Copilot Strategy Studio MCP integration."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from cosell_worker import execute_impl  # noqa: E402


def execute(action: str, question: str = "", case_path: str | None = None) -> dict:
    return execute_impl(action, question, case_path)
