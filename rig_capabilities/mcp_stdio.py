"""Minimal MCP stdio server: newline-delimited JSON-RPC 2.0, stdlib only.

Vendored from ~/Developer/jake-pai-mcp/jake_pai/mcp_stdio.py (same owner, MIT).
Implements the subset every harness (Claude Code, Codex, OMP, Hermes, Prime
Agent) exercises: initialize, notifications/initialized, ping, tools/list,
tools/call. Logs go to stderr — stdout is protocol-only, always.
"""
from __future__ import annotations

import json
import sys
from typing import Any, Callable, Dict, List

SUPPORTED_PROTOCOL_VERSIONS = ("2024-11-05", "2025-03-26", "2025-06-18")
LATEST_PROTOCOL_VERSION = "2025-06-18"

PARSE_ERROR = -32700
INVALID_REQUEST = -32600
METHOD_NOT_FOUND = -32601
INVALID_PARAMS = -32602
INTERNAL_ERROR = -32603


class ToolError(Exception):
    """Raised by a tool handler; surfaces as an isError tool result."""


def log(msg: str) -> None:
    sys.stderr.write(f"[rig-capabilities] {msg}\n")
    sys.stderr.flush()


class McpStdioServer:
    def __init__(self, name: str, version: str, tools: List[Dict[str, Any]],
                 handlers: Dict[str, Callable[[Dict[str, Any]], Any]]):
        self.name = name
        self.version = version
        self.tools = tools
        self.handlers = handlers
        self.initialized = False

    # -- protocol plumbing ------------------------------------------------

    def _send(self, payload: Dict[str, Any]) -> None:
        sys.stdout.write(json.dumps(payload, separators=(",", ":")) + "\n")
        sys.stdout.flush()

    def _result(self, rid: Any, result: Dict[str, Any]) -> None:
        self._send({"jsonrpc": "2.0", "id": rid, "result": result})

    def _error(self, rid: Any, code: int, message: str) -> None:
        self._send({"jsonrpc": "2.0", "id": rid,
                    "error": {"code": code, "message": message}})

    # -- dispatch ----------------------------------------------------------

    def handle_request(self, msg: Dict[str, Any]) -> None:
        method = msg.get("method")
        rid = msg.get("id")
        params = msg.get("params") or {}
        is_notification = "id" not in msg

        if method == "initialize":
            requested = params.get("protocolVersion") or LATEST_PROTOCOL_VERSION
            negotiated = (requested if requested in SUPPORTED_PROTOCOL_VERSIONS
                          else LATEST_PROTOCOL_VERSION)
            self.initialized = True
            self._result(rid, {
                "protocolVersion": negotiated,
                "capabilities": {"tools": {"listChanged": False}},
                "serverInfo": {"name": self.name, "version": self.version},
            })
            return
        if method == "notifications/initialized" or (is_notification and method and
                                                     method.startswith("notifications/")):
            return
        if method == "ping":
            if not is_notification:
                self._result(rid, {})
            return
        if method == "tools/list":
            self._result(rid, {"tools": self.tools})
            return
        if method == "tools/call":
            self._handle_tool_call(rid, params)
            return
        if is_notification:
            return  # unknown notifications are ignored per spec
        self._error(rid, METHOD_NOT_FOUND, f"unknown method: {method}")

    def _handle_tool_call(self, rid: Any, params: Dict[str, Any]) -> None:
        name = params.get("name")
        args = params.get("arguments") or {}
        handler = self.handlers.get(name)
        if handler is None:
            self._error(rid, INVALID_PARAMS, f"unknown tool: {name}")
            return
        try:
            result = handler(args)
            text = result if isinstance(result, str) else json.dumps(
                result, indent=1, ensure_ascii=False, default=str)
            self._result(rid, {"content": [{"type": "text", "text": text}],
                               "isError": False})
        except ToolError as exc:
            self._result(rid, {"content": [{"type": "text", "text": str(exc)}],
                               "isError": True})
        except Exception as exc:  # noqa: BLE001 — translate, never leak traceback
            log(f"tool {name} failed: {exc!r}")
            self._result(rid, {"content": [{"type": "text", "text":
                f"tool {name} failed: {exc}"}], "isError": True})

    # -- main loop ----------------------------------------------------------

    def serve_forever(self) -> None:
        for raw in sys.stdin:
            raw = raw.strip()
            if not raw:
                continue
            try:
                msg = json.loads(raw)
            except json.JSONDecodeError:
                self._error(None, PARSE_ERROR, "invalid JSON")
                continue
            if not isinstance(msg, dict):
                self._error(None, INVALID_REQUEST, "expected JSON object")
                continue
            try:
                self.handle_request(msg)
            except Exception as exc:  # keep the pipe alive
                log(f"dispatch error: {exc!r}")
                if "id" in msg:
                    self._error(msg.get("id"), INTERNAL_ERROR, "internal error")
