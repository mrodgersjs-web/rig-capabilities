from __future__ import annotations

import json
from pathlib import Path

from harness.components import apply_mutation, render_template, report, validate_python
from harness.packet import DesignPacket, Proposal, Report

_COMPONENT = "tools"


def render(packet: DesignPacket, out: Path) -> list[Path]:
    root = out / _COMPONENT
    adapters = render_template("adapters.py.j2", root / "adapters.py")
    manifest = root / "mcp_manifest.json"
    manifest.write_text(json.dumps({
        "schema": "rig.design-harness.mcp.v1",
        "source": packet.tools.mcp_manifest,
        "adapters": packet.tools.adapters,
    }, indent=2, sort_keys=True) + "\n")
    return [adapters, manifest]


def validate(files: list[Path]) -> Report:
    findings: list[str] = []
    by_name = {path.name: path for path in files if path.exists()}
    for name in ("adapters.py", "mcp_manifest.json"):
        if name not in by_name:
            findings.append(f"{name}:missing:file")
    if adapters := by_name.get("adapters.py"):
        validate_python(adapters, findings)
        text = adapters.read_text()
        for symbol in ("def postiz(", "def higgsfield(", "def telegram(", "def linkedin_action(", "LINKEDIN_DRY"):
            if symbol not in text:
                findings.append(f"adapters.py:missing:{symbol}")
        if "NotImplementedError" in text:
            findings.append("adapters.py:forbidden:NotImplementedError")
    if manifest := by_name.get("mcp_manifest.json"):
        try:
            data = json.loads(manifest.read_text())
            if data.get("schema") != "rig.design-harness.mcp.v1":
                findings.append("mcp_manifest.json:schema:invalid")
        except (OSError, json.JSONDecodeError) as exc:
            findings.append(f"mcp_manifest.json:json:{exc}")
    return report(findings)


def mutate(files: list[Path], proposal: Proposal) -> list[Path]:
    return apply_mutation(files, proposal, _COMPONENT)
