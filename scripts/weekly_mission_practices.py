#!/usr/bin/env python3
"""Stage public agent/prompt practice signals and run local routing regressions.

Stage only: this script never edits an agent, skill, prompt champion, install,
or live runtime. The fetched HTML is hashed and discarded. Reports keep only
source URL, title, headings, status, and evaluation exit codes.
"""
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import subprocess
import sys
import urllib.request
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parent.parent
SOURCES = ROOT / "data/mission-practice-sources.json"
OUTPUT = ROOT / ".context/mission-practices"
MAX_BYTES = 1_000_000


class _Titles(HTMLParser):
    def __init__(self):
        super().__init__()
        self.active = None
        self.title = ""
        self.headings = []

    def handle_starttag(self, tag, attrs):
        if tag in ("title", "h1", "h2"):
            self.active = tag

    def handle_endtag(self, tag):
        if tag == self.active:
            self.active = None

    def handle_data(self, data):
        text = " ".join(data.split())
        if not text:
            return
        if self.active == "title":
            self.title += text + " "
        elif self.active in ("h1", "h2") and len(self.headings) < 12:
            self.headings.append(text[:160])


def fetch_public(url: str) -> bytes:
    parsed = urlparse(url)
    if parsed.scheme != "https" or parsed.hostname not in {
        "www.anthropic.com", "developers.openai.com", "www.promptfoo.dev", "github.com"}:
        raise ValueError("source_not_allowlisted")
    req = urllib.request.Request(url, headers={"User-Agent": "RIGMissionPracticeScout/1.0"})
    with urllib.request.urlopen(req, timeout=20) as response:
        final = urlparse(response.geturl())
        if final.scheme != "https" or final.hostname not in {
            "www.anthropic.com", "developers.openai.com", "www.promptfoo.dev", "github.com"}:
            raise ValueError("redirect_not_allowlisted")
        content = response.read(MAX_BYTES + 1)
    if len(content) > MAX_BYTES:
        raise ValueError("source_too_large")
    return content


def stage(sources: list[dict], fetcher=fetch_public) -> dict:
    rows = []
    for source in sources:
        row = {"id": source["id"], "url": source["url"], "topic": source["topic"]}
        try:
            content = fetcher(source["url"])
            parser = _Titles()
            parser.feed(content.decode("utf-8", "replace"))
            row.update({"status": "candidate", "sha256": hashlib.sha256(content).hexdigest(),
                        "title": parser.title.strip()[:240], "headings": parser.headings})
        except (OSError, ValueError, TimeoutError) as exc:
            row.update({"status": "unavailable", "reason": type(exc).__name__})
        rows.append(row)
    return {"schema": "rig.mission-practice-stage.v1",
            "generated_at": dt.datetime.now(dt.timezone.utc).isoformat(),
            "promotion_authorized": False, "sources": rows}


def evaluate() -> dict:
    suite = ROOT / "capabilities/evals/mission-router"
    commands = [
        ([sys.executable, "-m", "unittest", "-v", "tests.test_mission_composition",
          "tests.test_weekly_mission_practices", "tests.test_completion_gate"], ROOT),
        (["/Users/rig128gb/.hermes/node/bin/promptfoo", "eval", "-c", "promptfooconfig.yaml",
          "--no-cache", "--no-share"], suite),
    ]
    checks = []
    for command, cwd in commands:
        try:
            result = subprocess.run(command, cwd=cwd, capture_output=True, text=True,
                                    timeout=120, check=False)
            checks.append({"command": command, "exit_code": result.returncode,
                           "stdout_sha256": hashlib.sha256(result.stdout.encode()).hexdigest(),
                           "stderr_sha256": hashlib.sha256(result.stderr.encode()).hexdigest()})
        except (OSError, subprocess.TimeoutExpired) as exc:
            checks.append({"command": command, "exit_code": None, "error": type(exc).__name__})
    return {"status": "pass" if all(c["exit_code"] == 0 for c in checks) else "fail",
            "checks": checks, "outcome_quality_proven": False}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("stage", "evaluate", "run"))
    parser.add_argument("--sources", type=Path, default=SOURCES)
    parser.add_argument("--output", type=Path, default=OUTPUT)
    args = parser.parse_args()
    report = {"schema": "rig.mission-weekly.v1",
              "generated_at": dt.datetime.now(dt.timezone.utc).isoformat(),
              "promotion_authorized": False}
    if args.command in ("stage", "run"):
        sources = json.loads(args.sources.read_text(encoding="utf-8"))["sources"]
        report["stage"] = stage(sources)
    if args.command in ("evaluate", "run"):
        report["evaluation"] = evaluate()
    args.output.mkdir(parents=True, exist_ok=True)
    week = dt.datetime.now(dt.timezone.utc).strftime("%G-W%V")
    stamp = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
    path = args.output / f"{week}-{stamp}.json"
    path.write_text(json.dumps(report, sort_keys=True, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"report": str(path), "sources": len(report.get("stage", {}).get("sources", [])),
                      "evaluation": report.get("evaluation", {}).get("status", "not_run"),
                      "promotion_authorized": False}, sort_keys=True))
    if report.get("evaluation", {}).get("status") == "fail":
        return 1
    if any(s["status"] == "unavailable" for s in report.get("stage", {}).get("sources", [])):
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
