#!/usr/bin/env python3
"""Build a labelled diff corpus for calibrating the s1gate code.diff rubric.

Labelling rules (each row records the rule that produced its label, so a bad
operating point can be traced back to a bad label):

  bad  -- the commit was later reverted, or a later commit explicitly names it
          as the thing being fixed, or its own message admits a regression.
  good -- every file it touched survived untouched for >= 30 days afterwards,
          and the commit itself was never reverted or fixed up.

Commits that are neither are dropped. An unlabelled commit is worth more
outside the corpus than guessed at inside it.
"""
from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

SURVIVE_DAYS = 30
MAX_DIFF = 8000
BAD_MSG = re.compile(
    r"\b(revert|regression|hotfix|broke|broken|oops|bad merge|accidentally|"
    r"wrong fix|re-fix|refix|undo)\b", re.I)
REVERT_OF = re.compile(r'revert\s+"?(.+?)"?$', re.I | re.M)
FIXES_SHA = re.compile(r"\b(?:fixes|fix(?:up)?(?:es)? for|follow-?up to|amends)\s+([0-9a-f]{7,40})\b", re.I)


def git(repo: Path, *args: str, timeout: int = 60) -> str:
    try:
        out = subprocess.run(["git", "-C", str(repo), *args],
                             capture_output=True, text=True, timeout=timeout)
        return out.stdout
    except (OSError, subprocess.SubprocessError):
        return ""


def commits(repo: Path, limit: int = 1200):
    raw = git(repo, "log", "--no-merges", "-n", str(limit),
              "--pretty=format:%H%x1f%at%x1f%s%x1f%b%x1e")
    for rec in raw.split("\x1e"):
        rec = rec.strip("\n")
        if not rec:
            continue
        parts = rec.split("\x1f")
        if len(parts) < 3:
            continue
        sha, ts, subject = parts[0], parts[1], parts[2]
        body = parts[3] if len(parts) > 3 else ""
        try:
            yield sha, int(ts), subject, body
        except ValueError:
            continue


def build(repo: Path, per_repo_cap: int = 200):
    rows = []
    all_c = list(commits(repo))
    if not all_c:
        return rows
    by_sha = {c[0]: c for c in all_c}
    newest = max(c[1] for c in all_c)

    # Which commits are named as broken by a later commit?
    blamed = set()
    reverted_subjects = set()
    for sha, ts, subject, body in all_c:
        text = subject + "\n" + body
        for m in FIXES_SHA.finditer(text):
            target = m.group(1)
            for full in by_sha:
                if full.startswith(target):
                    blamed.add(full)
        m = REVERT_OF.search(subject)
        if m:
            reverted_subjects.add(m.group(1).strip().lower())

    for sha, ts, subject, body in all_c:
        if len(rows) >= per_repo_cap:
            break
        if subject.lower().startswith("revert"):
            continue  # the revert itself is not the defect
        label = None
        rule = ""
        if sha in blamed:
            label, rule = "bad", "a later commit names this sha as the thing it fixes"
        elif subject.strip().lower() in reverted_subjects:
            label, rule = "bad", "this commit was later reverted by subject match"
        elif BAD_MSG.search(subject):
            label, rule = "bad", "commit subject admits a regression or hotfix"

        files = [f for f in git(repo, "show", "--name-only", "--pretty=format:", sha).split("\n") if f.strip()]
        if not files:
            continue

        if label is None:
            # good only if nothing it touched was changed again for 30 days,
            # and enough time has actually elapsed to observe that.
            if newest - ts < SURVIVE_DAYS * 86400:
                continue
            horizon = ts + SURVIVE_DAYS * 86400
            churn = git(repo, "log", "--pretty=format:%H", f"--since=@{ts + 1}",
                        f"--until=@{horizon}", "--", *files[:40])
            if churn.strip():
                continue
            label, rule = "good", "no file it touched was modified again for %d days" % SURVIVE_DAYS

        diff = git(repo, "show", "--unified=3", "--pretty=format:", sha)
        if not diff.strip():
            continue
        rows.append({
            "id": "%s:%s" % (repo.name, sha[:10]),
            "label": label,
            "repo": repo.name,
            "sha": sha,
            "task_text": subject.strip(),
            "diff_text": diff[:MAX_DIFF],
            "provenance": rule,
        })
    return rows


def main(argv):
    repos = [Path(p).expanduser() for p in argv[1:]]
    if not repos:
        print("usage: s1gate_build_corpus.py <repo> [repo...]", file=sys.stderr)
        return 3
    out_path = Path.home() / "Developer/rig-capabilities/capabilities/golden/s1gate/code-diff-corpus.jsonl"
    out_path.parent.mkdir(parents=True, exist_ok=True)

    rows, seen = [], set()
    for r in repos:
        if not (r / ".git").exists():
            print("skip (not a git repo): %s" % r, file=sys.stderr)
            continue
        got = build(r)
        n_bad = sum(1 for g in got if g["label"] == "bad")
        print("%-34s %4d rows (%d bad / %d good)" % (r.name, len(got), n_bad, len(got) - n_bad))
        for g in got:
            if g["id"] in seen:
                continue
            seen.add(g["id"])
            rows.append(g)

    bad = [r for r in rows if r["label"] == "bad"]
    good = [r for r in rows if r["label"] == "good"]
    # Keep the classes from being wildly lopsided: good commits vastly outnumber
    # bad ones, and an unbalanced sweep produces a flattering, useless threshold.
    cap = max(len(bad) * 3, 30)
    good = good[:cap]
    rows = bad + good

    with out_path.open("w", encoding="utf-8") as fh:
        for r in rows:
            fh.write(json.dumps(r) + "\n")
    print("\nwrote %d rows -> %s" % (len(rows), out_path))
    print("  bad : %d" % len(bad))
    print("  good: %d" % len(good))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
