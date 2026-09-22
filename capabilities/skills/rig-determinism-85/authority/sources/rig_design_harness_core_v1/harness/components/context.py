from __future__ import annotations

import json
from pathlib import Path

from harness.components import apply_mutation, render_template, report
from harness.packet import DesignPacket, Proposal, Report

_COMPONENT = "context"


def render(packet: DesignPacket, out: Path) -> list[Path]:
    root = out / _COMPONENT
    agents = render_template(
        "AGENTS.md.j2",
        root / "AGENTS.md",
        instance=packet.instance,
        cell_id=packet.cell_id,
        corpus_paths=packet.context.corpus_paths,
        memory_ns=packet.context.memory_ns,
    )
    corpus = root / "corpus.json"
    corpus.parent.mkdir(parents=True, exist_ok=True)
    corpus.write_text(json.dumps(packet.context.model_dump(mode="json"), indent=2, sort_keys=True) + "\n")
    return [agents, corpus]


def validate(files: list[Path]) -> Report:
    findings: list[str] = []
    by_name = {path.name: path for path in files if path.exists()}
    for name in ("AGENTS.md", "corpus.json"):
        if name not in by_name:
            findings.append(f"{name}:missing:file")
    if agents := by_name.get("AGENTS.md"):
        text = agents.read_text()
        for phrase in ("det_ratio", "LINKEDIN_DRY=1", "Models may propose typed output"):
            if phrase not in text:
                findings.append(f"AGENTS.md:missing:{phrase}")
    if corpus := by_name.get("corpus.json"):
        try:
            data = json.loads(corpus.read_text())
            required = {"corpus_paths", "memory_ns", "personas", "doctrines"}
            if not required.issubset(data):
                findings.append(f"corpus.json:schema:missing {','.join(sorted(required - set(data)))}")
        except (OSError, json.JSONDecodeError) as exc:
            findings.append(f"corpus.json:json:{exc}")
    return report(findings)


def mutate(files: list[Path], proposal: Proposal) -> list[Path]:
    return apply_mutation(files, proposal, _COMPONENT)
