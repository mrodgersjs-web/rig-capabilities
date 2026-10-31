#!/usr/bin/env python3
"""Label unlabelled code.diff decisions from verifiable git outcomes. No LLM, no judgement call.

Rule: a commit still reachable from a branch is 'good'; one that exists in the repo but is on no branch (reverted,
rebased away, abandoned) is 'bad'. Anything that cannot be resolved is skipped, never guessed.

Why the subject format matters. Until 2026-10-31 the pre-commit hook put HEAD in the subject, so the sha named the
PARENT commit; a reachable parent says nothing about the change being judged. The first run of this script labelled
751 decisions that way, all 'good', 0 'bad' - an artifact of measuring the wrong object, not evidence. Those labels
were deleted rather than left as false corpus. The hook now names the STAGED TREE and hooks/post-commit records
tree -> commit, which is what this script joins. Until enough bindings exist it reports no-binding-yet and changes
nothing, which is the honest state, not a failure.

An earlier draft also marked a commit 'bad' when any later commit within 24 hours touched the same files; that
mislabelled ordinary follow-up work (it flagged this session's own receipt commit), so reachability alone is the rule.

usage: label_codediff_from_outcomes.py [scan_limit] [--apply] [--write]
"""
import subprocess, sys, sqlite3, pathlib, collections, json

HOME = pathlib.Path.home()
DEV, S1 = HOME / "Developer", HOME / ".rig/s1gate/decisions.db"
BIND = HOME / ".rig/github-steward/commit_bindings.jsonl"
ARGS = [a for a in sys.argv[1:] if not a.startswith("--")]
LIMIT = int(ARGS[0]) if ARGS else 400
APPLY, WRITE = "--apply" in sys.argv, "--write" in sys.argv

repos = {}
for d in sorted(DEV.iterdir()):
    if not (d / ".git").exists(): continue
    u = subprocess.run(["git", "-C", str(d), "remote", "get-url", "origin"],
                       capture_output=True, text=True).stdout.strip()
    if "github.com" in u:
        repos[u.rstrip("/").removesuffix(".git").split("/")[-1]] = d

tree_to_commit = {}
if BIND.exists():
    for line in BIND.read_text().splitlines():
        try:
            r = json.loads(line)
            tree_to_commit[(r["repo"], r["tree"])] = r["commit"]
        except (json.JSONDecodeError, KeyError):
            continue

db = sqlite3.connect(S1)
rows = db.execute("select id, subject from decisions where rubric='code.diff' and label is null "
                  "and subject like 'code.diff:%@%' order by id desc limit ?", (LIMIT,)).fetchall()
stats, done = collections.Counter(), []
for did, subject in rows:
    if subject.count("@") != 1 or "code.diff:" not in subject:
        stats["unparsable"] += 1; continue
    repo, tree = subject.split("code.diff:", 1)[1].split("@")
    path = repos.get(repo)
    if not path: stats["repo-unresolved"] += 1; continue
    sha = tree_to_commit.get((repo, tree))
    if not sha: stats["no-binding-yet"] += 1; continue
    g = lambda *a: subprocess.run(["git", "-C", str(path), *a], capture_output=True, text=True)
    if g("cat-file", "-e", f"{sha}^{{commit}}").returncode: stats["commit-missing"] += 1; continue
    label = "good" if g("branch", "-a", "--contains", sha).stdout.split() else "bad"
    stats[label] += 1
    done.append((did, label, repo, sha))

print(f"scanned {len(rows)} | repos {len(repos)} | tree bindings {len(tree_to_commit)} | "
      + " ".join(f"{k}={v}" for k, v in stats.most_common()))
if not APPLY:
    print("dry run (pass --apply to write labels; --write to also calibrate)"); sys.exit(0)
n = sum(subprocess.run([str(HOME / ".rig/bin/rig-s1gate"), "label", str(did), lab, "--signal", "claims_match_diff.noul"],
                       capture_output=True, text=True).returncode == 0 for did, lab, _, _ in done)
print(f"labelled {n} of {len(done)} (good={stats['good']} bad={stats['bad']})")
if WRITE:
    r = subprocess.run([str(HOME / ".rig/bin/rig-s1gate"), "calibrate", "code.diff", "--signal", "claims_match_diff.noul",
                        "--direction", "above", "--max-false-block", "0.05", "--min-recall", "0.50", "--write"],
                       capture_output=True, text=True)
    print((r.stdout or r.stderr)[-1800:])
