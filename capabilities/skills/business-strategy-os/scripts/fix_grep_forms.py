#!/usr/bin/env python3
"""Drop the regex anchors from every `grep:` done_when form in the strategy family.

The repo's done-test runner treats the pattern after the last colon as a LITERAL substring,
so a form like `^## Router$` can never match. Anchors are silently dead weight: the check
looks like it verifies a heading and in fact never passes. This rewrites the family to the
literal form, which both the runner and a human reader agree on.
"""
import pathlib, re, sys
REPO = pathlib.Path("/Users/rig128gb/Developer/rig-capabilities/capabilities")
FILES = [REPO / "skills/business-strategy-os/SKILL.md"] + sorted(REPO.glob("skills/strategy-*/SKILL.md"))
AGENTS = sorted(REPO.glob("agents/strategy-*.md"))
QUOTED = re.compile(r'"(grep:[^"]+)"')
BARE = re.compile(r"(?m)^(\s*-\s+)(grep:\S.*)$")
def fix(m):
    """A done_when entry is either `grep:<path>:<pattern>` quoted (skills) or bare (agent YAML)."""
    entry = m.group(1)
    quoted = entry[:1] in "\"'"
    body = entry[1:-1] if quoted else entry
    path, _, pat = body.rpartition(":")
    new = f"{path}:{pat.strip('^$')}"
    return f'"{new}"' if quoted else new
def main() -> int:
    n = 0
    for p in FILES + AGENTS:
        t = p.read_text(encoding="utf-8")
        if "^" not in t:
            print("skip", p.parent.name); continue
        out = QUOTED.sub(lambda m: fix(m), t)
        out = BARE.sub(lambda m: m.group(1) + fix(re.match(r"(.*)", m.group(2))), out)
        if out != t:
            p.write_text(out, encoding="utf-8"); print("fixed", p.parent.name); n += 1
    print(f"{n} files rewritten")
    for p in FILES + AGENTS:
        for line in p.read_text(encoding="utf-8").splitlines():
            if "grep:" in line and "capabilities/skills" in line:
                print("  " + line.strip())
    return 0
if __name__ == "__main__":
    sys.exit(main())
