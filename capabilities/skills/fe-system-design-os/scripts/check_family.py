#!/usr/bin/env python3
"""Structural + no-verbatim gate for the FE System Design family.

For each skill directory:
  - SKILL.md exists with YAML frontmatter (name == dir name, description present);
  - its body contains "## JEV-first mandate";
  - every `references/<file>.md` the SKILL.md names exists and is >= 400 bytes;
  - no run of 12 consecutive words from any corpus transcript appears in its files
    (skills paraphrase and cite; transcript text stays in the local corpus).
Agents (capabilities/agents/fesd-*.md): frontmatter name matches file, "rig-s1gate" and
"DEFERRED" present, and every skill named in `skills:` exists.

usage: check_family.py            whole family
       check_family.py --self-test  plant a copied 12-word run and a missing reference in a temp
                                    copy; exit 0 only if both go RED and the real family is GREEN
exit: 0 clean | 2 findings"""
import json, re, shutil, sys, tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parents[4]
SK = REPO / "capabilities/skills"
AG = REPO / "capabilities/agents"
MANIFEST = REPO / "data/corpora/frontend-engineer/manifest.jsonl"
N = 12
WORD = re.compile(r"[a-z0-9']+")
REFS = re.compile(r"references/([A-Za-z0-9_./-]+\.md)")


def words(t):
    return WORD.findall(t.lower().replace("\u2019", "'"))


def corpus_grams():
    g = set()
    for line in MANIFEST.open():
        if not line.strip():
            continue
        f = REPO / json.loads(line)["file"]
        if f.exists():
            body = " ".join(re.sub(r"^\[[^\]]+\]\s*", "", l) for l in f.read_text(encoding="utf-8").splitlines() if l.startswith("["))
            ws = words(body)
            g |= {" ".join(ws[i:i + N]) for i in range(len(ws) - N + 1)}
    return g


def dirs(root):
    return sorted([p for p in root.glob("fesd-*") if p.is_dir()]
                  + [root / "fe-system-design-os", root / "fe-system-design-doctrine"])


def check(skill_dirs, agent_files, grams):
    out = []
    for d in skill_dirs:
        s = d / "SKILL.md"
        if not s.exists():
            out.append(f"{d.name}: SKILL.md missing"); continue
        t = s.read_text(encoding="utf-8")
        m = re.match(r"^---\n(.*?)\n---\n", t, re.S)
        if not m:
            out.append(f"{d.name}: no frontmatter"); continue
        fm = m.group(1)
        if not re.search(rf"^name:\s*{re.escape(d.name)}\s*$", fm, re.M):
            out.append(f"{d.name}: frontmatter name mismatch")
        if "description:" not in fm:
            out.append(f"{d.name}: no description")
        if "## JEV-first mandate" not in t:
            out.append(f"{d.name}: missing '## JEV-first mandate'")
        for r in sorted(set(REFS.findall(t))):
            p = d / "references" / r
            if not p.exists() or p.stat().st_size < 400:
                out.append(f"{d.name}: reference {r} missing or <400 bytes")
        for f in d.rglob("*.md"):
            ws = words(f.read_text(encoding="utf-8"))
            for i in range(len(ws) - N + 1):
                if " ".join(ws[i:i + N]) in grams:
                    out.append(f"{f.relative_to(d.parent)}: 12-word verbatim run from corpus"); break
    for a in agent_files:
        t = a.read_text(encoding="utf-8")
        if not re.search(rf"^name:\s*{re.escape(a.stem)}\s*$", t, re.M):
            out.append(f"agent {a.name}: name mismatch")
        for need in ("rig-s1gate", "DEFERRED"):
            if need not in t:
                out.append(f"agent {a.name}: missing {need}")
        m = re.search(r"^skills:\s*\[(.*?)\]", t, re.M)
        for sk in ([x.strip() for x in m.group(1).split(",")] if m else []):
            if sk and not (SK / sk / "SKILL.md").exists():
                out.append(f"agent {a.name}: names missing skill {sk}")
    return out


def main(argv):
    grams = corpus_grams()
    if not grams:
        print("RED corpus not found; cannot run no-verbatim check"); return 2
    real = check(dirs(SK), sorted(AG.glob("fesd-*.md")), grams)
    if argv and argv[0] == "--self-test":
        tmp = Path(tempfile.mkdtemp())
        src = SK / "fesd-performance"
        dst = tmp / "fesd-performance"
        shutil.copytree(src, dst)
        sample = sorted(grams)[len(grams) // 2]
        (dst / "references" / "planted.md").write_text("x " * 250 + sample + "\n")
        (dst / "SKILL.md").write_text((dst / "SKILL.md").read_text() + "\nSee references/does-not-exist.md\n")
        planted = check([dst], [], grams)
        caught_copy = any("verbatim" in p for p in planted)
        caught_ref = any("does-not-exist" in p for p in planted)
        shutil.rmtree(tmp)
        print(f"self-test: copy={'RED' if caught_copy else 'MISSED'} ref={'RED' if caught_ref else 'MISSED'} real_family={'GREEN' if not real else 'RED'}")
        return 0 if (caught_copy and caught_ref and not real) else 2
    for r in real:
        print("RED", r)
    print(f"{len(dirs(SK))} skill dirs, {len(list(AG.glob('fesd-*.md')))} agents, {len(real)} findings")
    return 2 if real else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
