#!/bin/sh
# outcome: security-review: App Studio SUB hook - blocks git add or commit of real env files (.env, .env.local, .env.production) while allowing .env.example, so app keys never reach a repo
# done_when: cmd:python3 capabilities/skills/app-studio/scripts/hook_cases.py app-env-commit-guard.sh
# quality_floor: 0.7
# rig app-env-commit-guard - PreToolUse (Bash) guard, active in any git repo.
# Canonical source: rig-capabilities repo. Parent: app-studio-hook.sh. DORMANT until wired.
# App Studio keeps every key name in a committed .env.example and every value in an
# uncommitted .env.local (app-web-scaffold step 3). Blocks: git add of an env file by path,
# git add -A / --all / . while an untracked, non-ignored env file exists, and git commit -a
# with a modified tracked env file. .example, .sample and .template files always pass.
# Complements guard-secret-write.sh, which catches key patterns in file writes.
set -u
APP_HOOK_PAYLOAD=$(cat 2>/dev/null || true)
export APP_HOOK_PAYLOAD
[ -n "$APP_HOOK_PAYLOAD" ] || exit 0
# A caller's PYTHONHOME or PYTHONPATH (the Aside runtime exports one) breaks the system python.
unset PYTHONHOME PYTHONPATH
exec /usr/bin/python3 - <<'PY'
import json, os, re, subprocess, sys
try:
    d = json.loads(os.environ.get("APP_HOOK_PAYLOAD", ""))
except Exception:
    sys.exit(0)
cmd = str((d.get("tool_input") or {}).get("command") or "")
if not re.search(r"\bgit\s+(add|commit)\b", cmd):
    sys.exit(0)
cwd = d.get("cwd") or os.getcwd()
ENV = re.compile(r"(^|/)\.env(\.[\w.-]+)?$")
SAFE = re.compile(r"\.(example|sample|template)$")
def secretish(p):
    p = p.strip().strip('"')
    return bool(ENV.search(p)) and not SAFE.search(p)
def git(*args):
    try:
        return subprocess.run(["git", "-C", cwd, *args], capture_output=True, text=True, timeout=10).stdout
    except Exception:
        return ""
bad = []
for m in re.finditer(r"\bgit\s+add\s+([^;&|]*)", cmd):
    args = m.group(1).split()
    bad += [a for a in args if not a.startswith("-") and secretish(a)]
    if any(a in (".", "-A", "--all", "*") for a in args):
        for line in git("status", "--porcelain", "--untracked-files=all").splitlines():
            path = line[3:]
            if secretish(path):
                bad.append(path)
if re.search(r"\bgit\s+commit\b[^;&|]*\s-[a-zA-Z]*a", cmd):
    bad += [p for p in git("diff", "--name-only").splitlines() if secretish(p)]
if bad:
    sys.stderr.write("app-studio env guard BLOCKED: this would stage env files %s. Commit .env.example only and"
                     " add .env* (with !.env.example) to .gitignore.\n" % sorted(set(bad)))
    sys.exit(2)
sys.exit(0)
PY
