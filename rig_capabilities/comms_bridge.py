"""Bridge from this MCP server to the rig_comms runtime (Communications OS).

rig_comms lives in this repo at
``capabilities/skills/rig-communications-core/``. The bridge lazy-imports it
only when a comms tool is first called, so a checkout without the skill still
serves the capability estate.

The one hard rule: stdout is the JSON-RPC channel. rig_comms' ``cli.cmd_*``
functions print straight to stdout, so the bridge imports the library surface
(``surfaces``, ``packets``, ``gates``, ``voice``, ``ledger``) and calls
functions, never the CLI — with the single exception of ``doctor``, whose
report is captured through an explicit stdout redirect.

Privacy contract (v19.6) survives the bridge: the private lane (love-notes /
PRIVATE-james) is never drafted, scored, or machine-read through MCP without
``human: true``. The refusal is the tool error, never a silent fallback.
"""
from __future__ import annotations

import contextlib
import io
import json
import sys
from pathlib import Path
from typing import Any, Dict

from .mcp_stdio import ToolError

COMMS_HOME = (Path(__file__).resolve().parent.parent
              / "capabilities" / "skills" / "rig-communications-core")

_mods: Dict[str, Any] | None = None


def _load() -> Dict[str, Any]:
    global _mods
    if _mods is None:
        if not (COMMS_HOME / "rig_comms" / "__init__.py").is_file():
            raise ToolError(f"comms-core missing at {COMMS_HOME}")
        if str(COMMS_HOME) not in sys.path:
            sys.path.insert(0, str(COMMS_HOME))
        try:
            from rig_comms import gates, ledger, packets, surfaces, voice  # type: ignore
        except Exception as exc:  # noqa: BLE001 — honest absence, no mock
            raise ToolError(f"comms-core import failed: {exc}") from exc
        _mods = {"gates": gates, "ledger": ledger, "packets": packets,
                 "surfaces": surfaces, "voice": voice}
    return _mods


def _private_guard(surf: Any, human: bool, what: str) -> None:
    if surf.lane == "private" and not human:
        raise ToolError(
            f"PRIVACY_LOCK: {what} of the private lane requires human:true "
            "(exit-3 semantics, v19.6). Human writes, human ships.")


def surfaces_catalog(_a: Dict[str, Any]) -> Dict[str, Any]:
    m = _load()
    return {sid: {"lane": s.lane, "engines": list(s.engines),
                  "budget": s.budget, "sigma_target": s.sigma_target,
                  "agf_min": getattr(s, "agf_min", None)}
            for sid, s in m["surfaces"].SURFACES.items()}


def route(args: Dict[str, Any]) -> Dict[str, Any]:
    m = _load()
    intent = (args.get("intent") or "").strip()
    if not intent:
        raise ToolError("intent required")
    return {"route": m["surfaces"].route(intent)}


def packet(args: Dict[str, Any]) -> Dict[str, Any]:
    m = _load()
    surf = m["surfaces"].resolve(args.get("surface") or "")
    if surf is None:
        raise ToolError(f"unknown surface '{args.get('surface')}'")
    _private_guard(surf, bool(args.get("human")), "drafting")
    brief = args.get("brief") or ""
    if not brief.strip():
        raise ToolError("brief required")
    return {"packet": m["packets"].build_packet(
        surf.id, brief, args.get("persona", ""))}


def score(args: Dict[str, Any]) -> Dict[str, Any]:
    m = _load()
    surf = m["surfaces"].resolve(args.get("surface") or "")
    if surf is None:
        raise ToolError(f"unknown surface '{args.get('surface')}'")
    if surf.lane == "private":
        raise ToolError("PRIVACY_LOCK: machine scoring of the private lane is refused "
                        "(v19.6). Human writes, human ships.")
    st = m["gates"].evaluate_stack(surf, args.get("artifact") or "")
    return {**st, "exit": 0 if st["can_ship"] else 2}


def voice_check(args: Dict[str, Any]) -> Dict[str, Any]:
    m = _load()
    text = args.get("artifact") or ""
    if not text.strip():
        raise ToolError("artifact required")
    return {"voice": m["voice"].score_voice(text),
            "drift": m["voice"].drift(text)}


def ledger_report(_a: Dict[str, Any]) -> Dict[str, Any]:
    m = _load()
    return {"loops": m["ledger"].loop_report(),
            "drafted_vs_shipped": m["ledger"].drafted_vs_shipped(),
            "calibration": m["ledger"].calibration_report()}


def doctor(_a: Dict[str, Any]) -> Dict[str, Any]:
    _load()
    from rig_comms import cli  # type: ignore  # noqa: E402
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):  # stdout here is protocol-critical
        rc = cli.cmd_doctor(None)
    try:
        payload = json.loads(buf.getvalue())
    except json.JSONDecodeError:
        raise ToolError(f"doctor output unparseable: {buf.getvalue()[:200]}") from None
    return {**payload, "exit": rc}
