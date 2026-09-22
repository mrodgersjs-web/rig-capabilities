from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Dict

from .core import evaluate
from .doctrine import validate_doctrine
from .agentforge.runner import run_workflow


def _read_text(path: str) -> str:
    return Path(path).read_text(encoding="utf-8")


def _collect_artifacts(paths: list[str]) -> Dict[str, str]:
    return {p: _read_text(p) for p in paths}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="rig", description="RIG communication protocol CLI")
    sub = parser.add_subparsers(dest="command", required=True)

    p_eval = sub.add_parser("evaluate", help="Evaluate text")
    p_eval.add_argument("text")
    p_eval.add_argument("--channel", default="email")

    p_gate = sub.add_parser("gate", help="Evaluate file and return ship/block verdict")
    p_gate.add_argument("file")
    p_gate.add_argument("--channel", default="email")

    p_score = sub.add_parser("score", help="Score file and return formula values")
    p_score.add_argument("file")
    p_score.add_argument("--channel", default="email")

    p_doctrine = sub.add_parser("doctrine-check", help="Run doctrine invariants")
    p_doctrine.add_argument("--artifact", action="append", default=[])

    p_workflow = sub.add_parser("run-workflow", help="Run AgentForge workflow")
    p_workflow.add_argument("workflow")
    p_workflow.add_argument("--draft", default="")
    p_workflow.add_argument("--approved", action="store_true")

    p_wt = sub.add_parser("writing-tools", help="External writing linters (alex, write-good, markdownlint) + full awesome-writing-tools catalog")
    p_wt.add_argument("file", nargs="?", help="File to analyze; omit with --list to print the catalog")
    p_wt.add_argument("--list", action="store_true", help="Print the tool catalog and exit")
    p_wt.add_argument("--text", help="Analyze literal text instead of a file")
    p_wt.add_argument("--tool", action="append", default=[], help="Restrict to specific wired tools (repeatable)")

    args = parser.parse_args(argv)

    if args.command == "evaluate":
        report = evaluate(args.text, channel=args.channel)
        print(json.dumps(report.to_dict(), indent=2))
        return 0 if report.can_ship else 2

    if args.command == "gate":
        report = evaluate(_read_text(args.file), channel=args.channel)
        print(json.dumps({"can_ship": report.can_ship, "blocks": report.blocks, "warnings": report.warnings}, indent=2))
        return 0 if report.can_ship else 2

    if args.command == "score":
        report = evaluate(_read_text(args.file), channel=args.channel)
        print(json.dumps({
            "comm_raw_score": report.comm_raw_score,
            "channel_formula": report.channel_formula,
            "channel_score": report.channel_score,
            "phase_detection": report.phase_detection,
        }, indent=2))
        return 0

    if args.command == "doctrine-check":
        doctrine = validate_doctrine(_collect_artifacts(args.artifact))
        print(json.dumps(doctrine.to_dict(), indent=2))
        return 0 if doctrine.passed else 1

    if args.command == "run-workflow":
        run = run_workflow(args.workflow, inputs={"draft": args.draft, "approved": args.approved})
        print(json.dumps(run.to_dict(), indent=2))
        return 0 if run.status == "ok" else 2

    if args.command == "writing-tools":
        from .integrations import writing_tools as wt
        if args.list or (not args.file and args.text is None):
            print(json.dumps(wt.catalog(), indent=2))
            return 0
        text = args.text if args.text is not None else _read_text(args.file)
        results = wt.analyze(text, tools=args.tool or None)
        print(json.dumps({name: r.to_dict() for name, r in results.items()}, indent=2))
        return 0

    return 1


if __name__ == "__main__":
    raise SystemExit(main())
