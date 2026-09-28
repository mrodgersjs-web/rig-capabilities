#!/bin/sh
# outcome: code-engineering: App Studio SUB hook - blocks toolchain commands the Aside sandbox cannot run (Turbopack, next without --webpack, Tailwind v4 oxide, lightningcss) inside App Studio projects, with the fix in the message
# done_when: cmd:python3 capabilities/skills/app-studio/scripts/hook_cases.py app-native-binary-preflight.sh
# quality_floor: 0.7
# rig app-native-binary-preflight - PreToolUse (Bash) guard for App Studio projects.
# Canonical source: rig-capabilities repo. Parent: app-studio-hook.sh. DORMANT until wired.
# Lesson LA-01 (memory/episodic/2026-09-26.md#L3): the Aside sandbox refuses every native
# .node binary, so a Turbopack build or a Tailwind v4 install fails after minutes of work.
# Acts only when cwd sits inside a project holding .app-studio/; .app-studio/allow-native
# opts out for builds that run outside the sandbox. Exit 2 blocks with the fix; 0 proceeds.
set -u
APP_HOOK_PAYLOAD=$(cat 2>/dev/null || true)
export APP_HOOK_PAYLOAD
[ -n "$APP_HOOK_PAYLOAD" ] || exit 0
# A caller's PYTHONHOME or PYTHONPATH (the Aside runtime exports one) breaks the system python.
unset PYTHONHOME PYTHONPATH
exec /usr/bin/python3 - <<'PY'
import json, os, re, sys
from pathlib import Path
try:
    d = json.loads(os.environ.get("APP_HOOK_PAYLOAD", ""))
except Exception:
    sys.exit(0)
cmd = str((d.get("tool_input") or {}).get("command") or "")
if not cmd:
    sys.exit(0)
cwd = Path(d.get("cwd") or os.getcwd())
root = next((p for p in [cwd, *cwd.parents] if (p / ".app-studio").is_dir()), None)
if root is None or (root / ".app-studio" / "allow-native").exists():
    sys.exit(0)
problems = []
if re.search(r"\b(npm|pnpm|yarn|bun)\s+(i|install|add)\b", cmd) and re.search(r"(tailwindcss@\^?4|@tailwindcss/oxide|lightningcss)", cmd):
    problems.append("installs a native-only package (Tailwind v4 oxide or lightningcss); use tailwindcss@3")
if re.search(r"--turbo(pack)?\b", cmd):
    problems.append("uses Turbopack, whose native binding the sandbox blocks")
for m in re.finditer(r"\bnext\s+(dev|build)\b[^;&|]*", cmd):
    if "--webpack" not in m.group(0):
        problems.append("'%s' runs without --webpack" % m.group(0).strip())
if re.search(r"\b(npm|pnpm|yarn|bun)\s+(run\s+)?(dev|build)\b", cmd):
    try:
        scripts = json.loads((root / "package.json").read_text()).get("scripts", {})
    except Exception:
        scripts = {}
    for name in ("dev", "build"):
        s = str(scripts.get(name, ""))
        if re.search(r"\bnext\s+(dev|build)\b", s) and "--webpack" not in s:
            problems.append("package.json script '%s' is '%s' without --webpack" % (name, s))
if problems:
    sys.stderr.write("app-studio native-binary preflight BLOCKED (lesson LA-01): " + "; ".join(problems)
                     + ". Fix: next dev/build --webpack, Tailwind v3, npm i --ignore-scripts. If this build"
                     + " runs outside the Aside sandbox, create .app-studio/allow-native.\n")
    sys.exit(2)
sys.exit(0)
PY
