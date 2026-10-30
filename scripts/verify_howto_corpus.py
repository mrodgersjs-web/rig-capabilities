#!/usr/bin/env python3
"""Unlazy verifiers for the how-to corpus completion (scope: howto-corpus).

One subcommand per gate; each prints a success-only marker after every
assertion passes, and exits non-zero otherwise. Read-only over the corpus.
"""
from __future__ import annotations
import json
import os
import subprocess
import sys
from collections import Counter
from pathlib import Path

CAPS = Path("/Users/rig128gb/Developer/rig-capabilities")
HOWTO = CAPS / "data" / "corpora" / "how-to"
MANIFEST = HOWTO / "manifest.jsonl"
ERRORS = HOWTO / "errors.jsonl"
COVERAGE = HOWTO / "COVERAGE.md"
TARGETS = HOWTO / "TARGETS.md"

os.environ.setdefault("COMMS_CORPUS", "how-to")
sys.path.insert(0, str(CAPS / "scripts"))
from scrape_writing_craft import parse_targets, slugify  # noqa: E402


def rows(path: Path) -> list[dict]:
    if not path.is_file():
        return []
    out = []
    for line in path.read_text().splitlines():
        line = line.strip()
        if line:
            out.append(json.loads(line))
    return out






def gate_wave(surface: str, marker: str) -> int:
    """Every target channel resolves: its transcripts, or a documented terminal condition."""
    targets = [t for t in parse_targets() if t["surface"] == surface]
    want = {slugify(t["name"]) for t in targets}
    man = [r for r in rows(MANIFEST) if r.get("surface") == surface]
    err = [r for r in rows(ERRORS) if r.get("surface") == surface]
    by_man: Counter[str] = Counter()
    by_err: Counter[str] = Counter()
    term: set[str] = set()
    for r in man:
        by_man[slugify(r["channel"])] += 1
    for e in err:
        s = slugify(e.get("channel", ""))
        if not s:
            continue
        by_err[s] += 1
        if "id-list" in str(e.get("error", "")) and not e.get("video_id"):
            term.add(s)
    unresolved: list[str] = []
    documented: list[str] = []
    for s in sorted(want):
        m, e = by_man.get(s, 0), by_err.get(s, 0)
        if m == 0:
            if s in term:
                documented.append(f"{s}(terminal id-list, {e} error rows)")
            elif e > 0:
                documented.append(f"{s}(all {e} attempts failed, 0 transcripts)")
            else:
                unresolved.append(f"{s}(never attempted)")
        elif m + e >= 6:
            continue
        else:
            documented.append(f"{s}({m} transcripts, {e} errors, live candidates {m + e} < 6)")
    if unresolved:
        print(f"{surface} unresolved: {unresolved}", file=sys.stderr)
        return 1
    print(f"{surface} targets={len(want)} transcripts={sum(by_man.values())} documented={documented}")
    print(marker)
    return 0


def gate_attempt_complete() -> int:
    man_ids = {r["video_id"] for r in rows(MANIFEST)}
    err_ids = {r.get("video_id") for r in rows(ERRORS) if r.get("video_id")}
    overlap = man_ids & err_ids
    if overlap:
        print(f"videos both fetched and errored: {sorted(overlap)[:5]}", file=sys.stderr)
        return 1
    print(f"manifest={len(man_ids)} errors={len(err_ids)} overlap=0")
    print("ATTEMPT-COMPLETE-OK")
    return 0


def gate_coverage_regen() -> int:
    man = rows(MANIFEST)
    text = COVERAGE.read_text()
    for surface in ("agent-craft", "comms-craft"):
        n = sum(1 for r in man if r.get("surface") == surface)
        token = f"{surface}: {n} transcripts"
        if token not in text:
            print(f"COVERAGE.md missing live count token: {token!r}", file=sys.stderr)
            return 1
    print("COVERAGE-REGEN-OK")
    return 0


def gate_skill(slug: str, marker: str, min_cites: int) -> int:
    skill = CAPS / "capabilities" / "skills" / slug / "SKILL.md"
    if not skill.is_file():
        print(f"missing {skill}", file=sys.stderr)
        return 1
    body = skill.read_text()
    man_ids = {r["video_id"] for r in rows(MANIFEST)}
    cited = {i for i in man_ids if i in body}
    if len(cited) < min_cites:
        print(f"{slug}: cites {len(cited)} < {min_cites} manifest video_ids", file=sys.stderr)
        return 1
    t = subprocess.run(
        [str(CAPS / "bin" / "rig-capabilities"), "test", slug],
        cwd=str(CAPS), capture_output=True, text=True, timeout=300)
    try:
        ok = json.loads(t.stdout).get("pass") is True
    except (json.JSONDecodeError, ValueError):
        ok = False
    if not ok:
        print(f"done_when failed for {slug}: {(t.stdout or t.stderr)[-300:]}", file=sys.stderr)
        return 1
    print(f"{slug}: cites={len(cited)} done_when=pass")
    print(marker)
    return 0


def gate_wiring(marker: str, min_cites: int) -> int:
    man_ids = {r["video_id"] for r in rows(MANIFEST)}
    for rel in ("capabilities/agents/rig-comms-gev.md",
                "capabilities/loops/rig-comms-drafting-loop.md"):
        body = (CAPS / rel).read_text()
        cited = {i for i in man_ids if i in body}
        if len(cited) < min_cites:
            print(f"{rel}: cites {len(cited)} < {min_cites}", file=sys.stderr)
            return 1
        print(f"{rel}: cites={len(cited)}")
    print(marker)
    return 0


def gate_suite(marker: str) -> int:
    py = "/Users/rig128gb/.hermes/hermes-agent/venv/bin/python3"
    r = subprocess.run([py, "-m", "pytest", "tests", "-q"],
                       cwd=str(CAPS), capture_output=True, text=True, timeout=1200)
    tail = r.stdout.strip().splitlines()[-1] if r.stdout.strip() else ""
    if r.returncode != 0 or " failed" in tail or " error" in tail:
        print(f"suite not green: {tail}", file=sys.stderr)
        return 1
    print(tail)
    print(marker)
    return 0


def gate_mirror(marker: str) -> int:
    mir = Path("/Users/rig128gb/Developer/rig-communications")
    for slug in ("rig-comms-agent-craft", "rig-comms-conversation-craft"):
        if not (mir / "skills" / slug / "SKILL.md").is_file():
            print(f"mirror missing skills/{slug}", file=sys.stderr)
            return 1
    r = subprocess.run(["git", "status", "--porcelain"], cwd=str(mir),
                       capture_output=True, text=True)
    if r.stdout.strip():
        print("mirror tree dirty:", r.stdout[:200], file=sys.stderr)
        return 1
    print(marker)
    return 0


def main() -> int:
    gates = {
        "G1": lambda: gate_wave("agent-craft", "AGENTCRAFT-COVERAGE-OK"),
        "G2": lambda: gate_wave("comms-craft", "COMMSCRAFT-COVERAGE-OK"),
        "G3": gate_attempt_complete,
        "G4": gate_coverage_regen,
        "G5": lambda: gate_skill("rig-comms-agent-craft", "AGENTCRAFT-SKILL-OK", 10),
        "G6": lambda: gate_skill("rig-comms-conversation-craft", "COMMSCRAFT-SKILL-OK", 10),
        "G7": lambda: gate_wiring("CORPUS-WIRING-OK", 3),
        "G8": lambda: gate_suite("SUITE-GREEN-OK"),
        "G9": lambda: gate_mirror("MIRROR-SYNC-OK"),
    }
    if len(sys.argv) != 2 or sys.argv[1] not in gates:
        print(f"usage: verify_howto_corpus.py [{'|'.join(gates)}]", file=sys.stderr)
        return 2
    return gates[sys.argv[1]]()


if __name__ == "__main__":
    sys.exit(main())
