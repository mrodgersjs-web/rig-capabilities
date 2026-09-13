"""Shared build context packet: the handoff between diagnose, route and build.

One packet per bounded build. It carries ONLY what a builder must not re-derive:
the frozen diagnosis (validated by build_diagnose, never restated), the skills/agents
selected for it, source/evidence bindings with the hashes they were read at, the
gates that must clear, the approvals on record, and exactly one next action.

Two properties are enforced, because both failure modes are how builds go wrong:
  * completeness — a packet with no next action, or whose diagnosis did not
    resolve, is refused at compile time (a missing field is a rejection, not a 0.5);
  * freshness — `verify` re-hashes every bound source. A packet whose source moved
    is STALE and a builder must refuse it; a packet is never silently trusted.

Usage: python3 rig_capabilities/context_packet.py selftest
"""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from rig_capabilities.build_diagnose import DiagnoseError, diagnose  # noqa: E402

SCHEMA = "rig.context-packet.v1"
BUDGET_NOTE = "budgets come from the diagnosis; the packet never invents one"


class PacketError(ValueError):
    pass


def _sha(path: Path) -> str:
    return "sha256:" + hashlib.sha256(Path(path).read_bytes()).hexdigest()


def _bind_sources(sources: list, root: Path) -> list[dict]:
    if not isinstance(sources, list) or not sources:
        raise PacketError("sources must be a non-empty list of {path[,sha256]}")
    bound = []
    for item in sources:
        if isinstance(item, str):
            item = {"path": item}
        if not isinstance(item, dict) or "path" not in item:
            raise PacketError(f"source needs a path: {item!r}")
        p = (root / item["path"]).resolve()
        if not p.is_file():
            raise PacketError(f"source does not exist: {item['path']}")
        now = _sha(p)
        declared = item.get("sha256")
        if declared and declared != now:
            raise PacketError(
                f"source stale at compile time: {item['path']} declared {declared} "
                f"actual {now}")
        bound.append({"path": str(item["path"]), "sha256": now})
    return bound


def compile_packet(payload: dict, *, root: Path | None = None) -> dict:
    """Validate and freeze a packet; raise PacketError on any gap."""
    if not isinstance(payload, dict):
        raise PacketError("payload must be a mapping")
    root = Path(root or Path.cwd()).resolve()
    for field in ("diagnosis", "skills", "sources", "next_action"):
        if field not in payload:
            raise PacketError(f"missing required field: {field}")

    try:
        diag = diagnose(payload["diagnosis"])
    except DiagnoseError as exc:
        raise PacketError(f"diagnosis did not resolve: {exc}") from exc

    skills = payload["skills"]
    if not isinstance(skills, list) or not all(isinstance(s, str) and s.strip() for s in skills):
        raise PacketError("skills must be a non-empty list of capability ids")

    gates = payload.get("gates", [])
    if not isinstance(gates, list) or not all(
            isinstance(g, dict) and g.get("id") and g.get("status") for g in gates):
        raise PacketError("each gate needs id and status (never assume a gate passed)")

    approvals = payload.get("approvals", [])
    if not isinstance(approvals, list) or not all(
            isinstance(a, dict) and a.get("id") and a.get("action") for a in approvals):
        raise PacketError("each approval needs id and the exact approved action")

    action = payload["next_action"]
    if not isinstance(action, str) or not action.strip():
        raise PacketError("next_action must be a non-empty command or decision")

    core: dict = {
        "schema": SCHEMA,
        "diagnosis": diag,
        "skills": sorted(set(skills)),
        "sources": _bind_sources(payload["sources"], root),
        "gates": gates,
        "approvals": approvals,
        "next_action": action.strip(),
        "blocked_on": payload.get("blocked_on", []),
    }
    return {**core, "packet_sha256": "sha256:" + hashlib.sha256(
        json.dumps(core, sort_keys=True).encode()).hexdigest()}


def verify(packet: dict, *, root: Path | None = None) -> dict:
    """Re-check integrity and freshness. Never mutates; reports closed statuses."""
    root = Path(root or Path.cwd()).resolve()
    if not isinstance(packet, dict) or packet.get("schema") != SCHEMA:
        return {"status": "INVALID", "reason": "schema"}
    body = {k: v for k, v in packet.items() if k != "packet_sha256"}
    want = "sha256:" + hashlib.sha256(json.dumps(body, sort_keys=True).encode()).hexdigest()
    if packet.get("packet_sha256") != want:
        return {"status": "INVALID", "reason": "self hash"}
    stale = [s["path"] for s in packet["sources"]
             if not (root / s["path"]).is_file() or _sha(root / s["path"]) != s["sha256"]]
    if stale:
        return {"status": "STALE", "sources": stale,
                "action": "re-compile the packet against current sources"}
    missing_gate = [g["id"] for g in packet["gates"] if g["status"] not in ("PASS", "GREEN")]
    return {"status": "FRESH", "packet_sha256": want,
            "cell_id": packet["diagnosis"]["cell_id"],
            "next_action": packet["next_action"],
            "gates_not_green": missing_gate}


def selftest() -> int:
    import tempfile
    diag = {"goal": "wire the build standard into four runtimes",
            "cell_id": "L4-D2-A1-R", "done_test": ["bin/rig-build-standard test"],
            "out_of_scope": ["outward sends"],
            "effort_budget": {"cpu_minutes": 30, "usd": 5, "wallclock_seconds": 1800},
            "evidence_refs": ["file:runs/agentic-stack-buildout/iqrsqpi-intent.md"]}
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        (root / "src.py").write_text("print(1)\n")
        good = {"diagnosis": diag, "skills": ["rig-build-standard"],
                "sources": ["src.py"], "gates": [{"id": "d85_certified", "status": "RED"}],
                "approvals": [], "next_action": "bin/rig-build-standard packet --out p.json"}
        p = compile_packet(good, root=root)
        assert verify(p, root=root)["status"] == "FRESH"
        (root / "src.py").write_text("print(2)\n")
        assert verify(p, root=root)["status"] == "STALE"
        for label, bad in (
            ("no next action", {**good, "next_action": "  "}),
            ("no sources", {**good, "sources": []}),
            ("invented gate status", {**good, "gates": [{"id": "d85"}]}),
            ("bad cell", {**good, "diagnosis": {**diag, "cell_id": "L9-D9-A9-Z"}}),
        ):
            try:
                compile_packet(bad, root=root)
            except PacketError:
                continue
            raise AssertionError(f"compiled despite {label}")
        tampered = dict(p); tampered["next_action"] = "rm -rf /"
        assert verify(tampered, root=root)["status"] == "INVALID"
    print("context-packet selftest OK")
    return 0


def main(argv: list[str]) -> int:
    if not argv or argv[0] in ("-h", "--help", "help"):
        print(__doc__)
        return 0
    if argv[0] == "selftest":
        return selftest()
    import argparse
    ap = argparse.ArgumentParser(prog="context_packet", exit_on_error=False)
    ap.add_argument("verb", choices=["compile", "verify"])
    ap.add_argument("--diagnosis", help="diagnosis JSON file (compile)")
    ap.add_argument("--packet", help="packet JSON file (verify)")
    ap.add_argument("--skills", nargs="*", default=[])
    ap.add_argument("--sources", nargs="*", default=[])
    ap.add_argument("--next-action", default="")
    ap.add_argument("--root", default=".")
    ap.add_argument("--out")
    try:
        args = ap.parse_args(argv)
    except Exception as exc:  # noqa: BLE001
        print(f"BLOCKED: {exc}", file=sys.stderr)
        return 2
    root = Path(args.root)
    try:
        if args.verb == "compile":
            diag = json.loads(Path(args.diagnosis).read_text()) if args.diagnosis else None
            if diag is None:
                raise PacketError("--diagnosis is required")
            packet = compile_packet(
                {"diagnosis": diag, "skills": args.skills, "sources": args.sources,
                 "next_action": args.next_action}, root=root)
        else:
            packet = verify(json.loads(Path(args.packet).read_text()), root=root)
    except (PacketError, OSError, json.JSONDecodeError) as exc:
        print(f"BLOCKED: {exc}", file=sys.stderr)
        return 2
    text = json.dumps(packet, indent=1, sort_keys=True)
    if args.out:
        Path(args.out).write_text(text + "\n")
    print(text)
    return 0 if packet.get("status") in (None, "FRESH") else 2


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
