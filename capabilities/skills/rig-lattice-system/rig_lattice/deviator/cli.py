"""rig-strict CLI — terminal entrypoint for the v3 strict auditor.

Subcommands:
  audit <file|->        Run 40-engine strict audit, print scorecard + failures
  patch <file> [out]    Apply structural overlays (v2.2→v2.5 style) for strict pass
  render                Render strict-audit HTML from saved audit JSONs
  criteria [engine]     List criteria packs or print one engine's YAML
  explain <engine>      Explain an engine + its 5-10 criteria questions
  fix <file>            Audit, then apply minimum unblocks for failing required Qs
  diff <a> <b>          Audit two files, print engine-by-engine delta

Examples:
  python -m rig_engines_v3 audit my_proposal.md
  python -m rig_engines_v3 patch draft.md draft_strict.md
  python -m rig_engines_v3 explain ANCHOR
  cat strategy.md | python -m rig_engines_v3 audit -
"""
from __future__ import annotations
import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).parent

from rig_lattice.deviator.auditor import audit_all, _load_yaml, CRITERIA_DIR, CALIBRATION_FILE  # noqa: E402

ANSI = {"red": "\033[31m", "green": "\033[32m", "yellow": "\033[33m",
        "blue": "\033[34m", "cyan": "\033[36m", "bold": "\033[1m",
        "dim": "\033[2m", "reset": "\033[0m"}


def _color(text: str, c: str) -> str:
    if not sys.stdout.isatty():
        return text
    return f"{ANSI.get(c,'')}{text}{ANSI['reset']}"


def _read_text(target: str) -> str:
    if target == "-":
        return sys.stdin.read()
    p = Path(target).expanduser().resolve()
    if not p.exists():
        sys.exit(f"file not found: {p}")
    return p.read_text()


# ── audit ──────────────────────────────────────────────────────────────────
def cmd_audit(args) -> int:
    text = _read_text(args.file)
    engines = args.engines.split(",") if args.engines else None
    out = audit_all(text, llm_enabled=not args.no_llm, engines=engines)

    rig_l_color = "green" if out["rig_l"] >= 5 else "yellow" if out["rig_l"] >= 0 else "red"
    hb_color = "red" if out["hard_blocks"] > 0 else "green"
    status_color = "green" if out["status"] == "PASS" else "red" if out["status"] == "HARD_BLOCK" else "yellow"

    print(_color("=" * 76, "dim"))
    print(_color(f"RIG Deviator™ v3 Strict Audit — {len(out['engines'])} engines", "bold"))
    print(_color("=" * 76, "dim"))
    print(f"  RIG-L:        {_color(f'{out["rig_l"]:+.2f}', rig_l_color)}")
    print(f"  BDF:          {out['bdf']:+.2f}")
    print(f"  Status:       {_color(out['status'], status_color)}")
    print(f"  HARD_BLOCKs:  {_color(f'{out["hard_blocks"]}/{len(out["engines"])}', hb_color)}")
    if out["strongest"]:
        print(f"  Strongest:    {out['strongest']['codename']} {_color(f'{out["strongest"]["sigma"]:+.1f}σ', 'green')}")
    if out["weakest"]:
        print(f"  Weakest:      {out['weakest']['codename']} {_color(f'{out["weakest"]["sigma"]:+.1f}σ', 'red')}")
    print()

    if not args.summary_only:
        print(_color(f"{'codename':14} {'engine':32} {'σ':>8}  {'tier':22}  status", "dim"))
        print(_color("-" * 96, "dim"))
        for slug, r in sorted(out["engines"].items(), key=lambda x: -x[1]["sigma"]):
            c = "green" if r["sigma"] >= 14 else "yellow" if r["sigma"] >= 0 else "red"
            sc = "green" if r["status"] == "PASS" else "red" if r["status"] == "HARD_BLOCK" else "yellow"
            print(f"{r['codename']:14} {slug:32} {_color(f'{r["sigma"]:+8.2f}', c)}σ  "
                  f"{r['sigma_label']:22}  {_color(r['status'], sc)}")
        print()

    # Failed-required summary
    blockers = [(s, r) for s, r in out["engines"].items() if r["failed_required"]]
    if blockers:
        print(_color(f"=== {len(blockers)} engines with failed required questions ===", "red"))
        for slug, r in sorted(blockers, key=lambda x: x[1]["sigma"]):
            print(f"\n  {_color(r['codename'], 'red')} ({slug}) — {r['status']}")
            for qid in r["failed_required"][:3]:
                q = next(qq for qq in r["questions"] if qq["id"] == qid)
                ev = (q.get("evidence") or "—")[:90]
                print(f"    {_color('✗', 'red')} {qid}: {q['question'][:80]}")
                print(f"      {_color('ev:', 'dim')} {ev}")

    if args.json:
        Path(args.json).write_text(json.dumps(out, indent=2, default=str))
        print(f"\n{_color('saved:', 'cyan')} {args.json}")

    return 0 if out["status"] == "PASS" else 1


# ── criteria ───────────────────────────────────────────────────────────────
def cmd_criteria(args) -> int:
    packs = sorted(CRITERIA_DIR.glob("*.yaml"))
    if not args.engine:
        # List all
        print(_color(f"40 criteria packs at {CRITERIA_DIR}:", "bold"))
        print()
        for p in packs:
            d = _load_yaml(p)
            codename = d.get("codename", "?")
            layer = d.get("layer", "?")
            n_q = len(d.get("questions", []))
            n_req = sum(1 for q in d["questions"] if q.get("required"))
            print(f"  {_color(codename, 'cyan'):20} {p.stem:32} "
                  f"{layer:10} {n_q} qs ({n_req} required)")
        return 0

    # Print single engine pack
    target = args.engine.lower()
    found = None
    for p in packs:
        d = _load_yaml(p)
        if d["codename"].lower() == target or p.stem.lower() == target:
            found = (p, d)
            break
    if not found:
        sys.exit(f"engine not found: {args.engine}")
    p, d = found
    print(_color(f"=== {d['codename']} ({d['slug']}) — {d['layer']} ===", "bold"))
    print(_color(f"axis: {d.get('axis','—')}", "dim"))
    print()
    for i, q in enumerate(d["questions"], 1):
        req = _color(" [REQ]", "red") if q.get("required") else ""
        print(f"  {i:2}. {q['id']}{req}")
        print(f"      {q['question']}")
        print(_color(f"      mode={q['mode']}", "dim"))
        if "pattern" in q:
            print(_color(f"      pattern: {q['pattern'][:80]}", "dim"))
    return 0


# ── explain ────────────────────────────────────────────────────────────────
def cmd_explain(args) -> int:
    args.engine = args.engine
    return cmd_criteria(args)


# ── patch ──────────────────────────────────────────────────────────────────
def cmd_patch(args) -> int:
    text = _read_text(args.file)
    print(_color(f"Auditing input file: {len(text.split())} words / {len(text):,} chars", "dim"))
    audit = audit_all(text, llm_enabled=False)
    print(f"  current: RIG-L {audit['rig_l']:+.2f}  hard_blocks {audit['hard_blocks']}/40")
    print()
    print(_color("Applying structural overlay patches...", "cyan"))

    # Pull the patch overlay logic — keep this in-process for the CLI
    from rig_lattice.deviator.patch_overlays import build_overlay
    patched = build_overlay(text, audit)

    # Re-audit
    new_audit = audit_all(patched, llm_enabled=False)
    print(f"  patched: RIG-L {new_audit['rig_l']:+.2f}  hard_blocks {new_audit['hard_blocks']}/40")
    print(_color(f"  delta: RIG-L {new_audit['rig_l']-audit['rig_l']:+.2f}  "
                 f"hard_blocks {new_audit['hard_blocks']-audit['hard_blocks']:+d}", "green"))

    out_path = Path(args.out).expanduser() if args.out else Path(args.file).with_suffix(".strict.md")
    out_path.write_text(patched)
    print(f"\n{_color('wrote:', 'cyan')} {out_path} ({len(patched):,} bytes)")
    return 0


# ── render ─────────────────────────────────────────────────────────────────
def cmd_render(args) -> int:
    import subprocess
    rc = subprocess.call([sys.executable, str(ROOT / "render_strict_audit.py")])
    return rc


# ── fix ────────────────────────────────────────────────────────────────────
def cmd_fix(args) -> int:
    """Audit, then print copy-paste-ready edits for failed required questions."""
    text = _read_text(args.file)
    audit = audit_all(text, llm_enabled=False)

    blockers = [(s, r) for s, r in audit["engines"].items() if r["failed_required"]]
    if not blockers:
        print(_color("No required failures. Document is strict-passing.", "green"))
        return 0

    print(_color(f"=== {len(blockers)} engines have failed required questions ===", "red"))
    print()
    print(_color("Copy-paste-ready edits (insert anywhere in the document):", "bold"))
    print()

    from rig_lattice.deviator.fix_suggestions import suggest_for
    for slug, r in sorted(blockers, key=lambda x: x[1]["sigma"]):
        for qid in r["failed_required"][:3]:
            q = next(qq for qq in r["questions"] if qq["id"] == qid)
            suggestion = suggest_for(slug, qid, q)
            if suggestion:
                print(_color(f"  [{r['codename']} / {qid}]", "yellow"))
                print(_color(f"  Q: {q['question'][:90]}", "dim"))
                print(f"  → {suggestion}")
                print()
    return 0


# ── diff ───────────────────────────────────────────────────────────────────
def cmd_diff(args) -> int:
    a_audit = audit_all(_read_text(args.a), llm_enabled=False)
    b_audit = audit_all(_read_text(args.b), llm_enabled=False)
    print(_color(f"a: {args.a}", "dim"))
    print(_color(f"b: {args.b}", "dim"))
    print()
    print(f"  RIG-L:    {a_audit['rig_l']:+.2f}  →  {b_audit['rig_l']:+.2f}  "
          f"Δ {_color(f'{b_audit["rig_l"]-a_audit["rig_l"]:+.2f}', 'green' if b_audit['rig_l']>a_audit['rig_l'] else 'red')}")
    print(f"  BDF:      {a_audit['bdf']:+.2f}  →  {b_audit['bdf']:+.2f}  "
          f"Δ {b_audit['bdf']-a_audit['bdf']:+.2f}")
    print(f"  Hard-blocks: {a_audit['hard_blocks']}/40  →  {b_audit['hard_blocks']}/40  "
          f"Δ {_color(f'{b_audit["hard_blocks"]-a_audit["hard_blocks"]:+d}', 'green' if b_audit['hard_blocks']<a_audit['hard_blocks'] else 'red')}")
    print()
    print(_color(f"{'codename':14} {'σ A':>8}  {'σ B':>8}  {'Δ':>8}", "dim"))
    print(_color("-" * 50, "dim"))
    for slug in sorted(a_audit["engines"], key=lambda s: -(b_audit["engines"][s]["sigma"] - a_audit["engines"][s]["sigma"])):
        ra = a_audit["engines"][slug]
        rb = b_audit["engines"][slug]
        d = rb["sigma"] - ra["sigma"]
        c = "green" if d > 0 else "red" if d < 0 else "dim"
        print(f"{ra['codename']:14} {ra['sigma']:+8.2f}  {rb['sigma']:+8.2f}  "
              f"{_color(f'{d:+8.2f}σ', c)}")
    return 0


# ── arg parser ─────────────────────────────────────────────────────────────
def main() -> int:
    p = argparse.ArgumentParser(prog="rig-strict",
                                  description="RIG Deviator™ v3 strict-mode auditor")
    sub = p.add_subparsers(dest="cmd", required=True)

    a = sub.add_parser("audit", help="Run strict 40-engine audit on a file or stdin")
    a.add_argument("file")
    a.add_argument("--engines", help="comma-separated engine slugs to limit audit")
    a.add_argument("--no-llm", action="store_true")
    a.add_argument("--json", help="write full audit JSON to this path")
    a.add_argument("--summary-only", action="store_true")
    a.set_defaults(func=cmd_audit)

    c = sub.add_parser("criteria", help="List criteria packs or inspect one")
    c.add_argument("engine", nargs="?", help="engine codename or slug (omit to list all)")
    c.set_defaults(func=cmd_criteria)

    e = sub.add_parser("explain", help="Explain an engine + its criteria")
    e.add_argument("engine")
    e.set_defaults(func=cmd_explain)

    pa = sub.add_parser("patch", help="Apply structural overlays to make file strict-passing")
    pa.add_argument("file")
    pa.add_argument("out", nargs="?")
    pa.set_defaults(func=cmd_patch)

    r = sub.add_parser("render", help="Render strict-audit HTML from saved audits")
    r.set_defaults(func=cmd_render)

    f = sub.add_parser("fix", help="Print copy-paste-ready edits for failed required Qs")
    f.add_argument("file")
    f.set_defaults(func=cmd_fix)

    d = sub.add_parser("diff", help="Audit two files, print engine-by-engine delta")
    d.add_argument("a")
    d.add_argument("b")
    d.set_defaults(func=cmd_diff)

    args = p.parse_args()
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
