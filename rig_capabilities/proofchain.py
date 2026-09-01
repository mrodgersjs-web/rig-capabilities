"""V36: verify ROADMAP packet prefixes against ~/.rig/proof.

A prefix in the ROADMAP that matches no proof_hash on disk is a lie.
Missing files are reported, never invented.
"""
from __future__ import annotations

import json
import re
from pathlib import Path

PROOF_DIR = Path.home() / ".rig" / "proof"
SHA_RE = re.compile(r"sha256:([0-9a-f]{8,})")


def _packet_prefixes(text: str) -> list[str]:
    """Third table column is the packet prefix — not the commit column."""
    out = []
    for line in text.splitlines():
        if not line.startswith("|"):
            continue
        cols = [c.strip() for c in line.split("|")]
        # ['', V, commit, packet, what, proof, '']
        if len(cols) < 5:
            continue
        pkt = cols[3].strip("`")
        if pkt.startswith("sha256:"):
            pkt = pkt[7:]
        pkt = pkt.lower()
        if len(pkt) >= 8 and all(c in "0123456789abcdef" for c in pkt[:8]):
            out.append(pkt[:8])
    out.extend(m[:8] for m in SHA_RE.findall(text.lower()))
    return sorted(set(out))


def _hashes(proof_dir: Path) -> set[str]:
    out = set()
    if not proof_dir.is_dir():
        return out
    for p in proof_dir.rglob("*.json"):
        try:
            d = json.loads(p.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            continue
        if not isinstance(d, dict):
            continue
        h = str(d.get("proof_hash") or d.get("hash") or "")
        if h.startswith("sha256:"):
            h = h[7:]
        if h:
            out.add(h.lower())
    return out


def verify_roadmap(repo, proof_dir: Path | None = None) -> dict:
    md = Path(repo.root) / "docs" / "ROADMAP.md"
    text = md.read_text(encoding="utf-8") if md.exists() else ""
    prefixes = _packet_prefixes(text)
    hashes = _hashes(proof_dir or PROOF_DIR)
    found, missing = [], []
    for pre in prefixes:
        hit = any(h.startswith(pre) for h in hashes)
        (found if hit else missing).append(pre)
    return {"ok": not missing, "prefixes": len(prefixes),
            "found": found, "missing": missing,
            "proof_files": len(hashes),
            "roadmap": str(md) if md.exists() else None}
