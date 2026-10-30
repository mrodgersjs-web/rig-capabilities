#!/usr/bin/env python3
"""Build the Skool community family (skool-growth-os + sk-* stages + skool-doctrine) from
the verified corpus notes in data/corpora/skool/notes/ plus the hand-written stage specs in
scripts/stage_specs.py.

Laws are copied from the notes WITHOUT their verbatim quotes: skills carry paraphrased rules with
CLAIM(videoId) citations; transcript text stays in the local corpus. Re-run after any notes edit.
usage: build_family.py            write every skill that has notes
       build_family.py --check    exit 2 if any generated file would change (drift gate)
"""
import re, sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[3]
SK = REPO / "capabilities/skills"
NOTES = REPO / "data/corpora/skool/notes"
sys.path.insert(0, str(HERE))
from stage_specs import STAGES, ORDER, JEV, GATES  # noqa: E402


def section(text, name):
    m = re.search(rf"^## {re.escape(name)}[^\n]*\n(.*?)(?=^## |\Z)", text, re.S | re.M)
    return m.group(1).strip() if m else ""


QSPAN = re.compile(r'["\u201c][^"\u201d\n]{20,}["\u201d]')


def strip_quotes(block):
    """Drop quote lines and inline quoted spans: transcript wording stays in the corpus notes."""
    keep = [l for l in block.splitlines() if not l.lstrip().startswith(">")]
    return QSPAN.sub("[quote in corpus notes]", "\n".join(keep)).strip()


def parse(stage):
    p = NOTES / f"{stage}.md"
    if not p.exists():
        return None
    t = p.read_text(encoding="utf-8")
    laws = [QSPAN.sub("[quote in corpus notes]", l.strip()) for l in section(t, "Laws").splitlines() if re.match(r"^L\d+\.", l.strip())]
    return {
        "laws": laws,
        "contested": strip_quotes(section(t, "Contested")),
        "creator": strip_quotes(section(t, "Creator result claims")),
        "platform": strip_quotes(section(t, "Platform mechanics")),
        "rig": strip_quotes(section(t, "RIG application")),
    }


def frontmatter(name, desc, tags, outcome, done_when, meta):
    dw = "\n".join(f"  - {d}" for d in done_when)
    md = "\n".join(f'  {k}: "{v}"' for k, v in meta.items())
    return (f"---\nname: {name}\ndescription: >-\n  {desc}\nowner: rig-intelligence\ndomain: Communications\n"
            f"status: Stable\nacl: internal\ntags: [{', '.join(tags)}]\noutcome: \"{outcome}\"\n"
            f"done_when:\n{dw}\nquality_floor: 0.6\nmetadata:\n{md}\n---\n")


# Stages that carry no CLAIM() tokens: claims_check exits 2 on zero claims, so their test is a grep on the stage's own procedure rule.
ZERO_CLAIM_RULE = {'sk-ads': 'Kill fast\\*\\*', 'sk-distribute': 'Route-back rule', 'sk-gate': 'content about a minor \\(Jacob\\) is STOP', 'sk-lessons': 'strip credentials, personal names, client names', 'sk-measure': 'Name what is not measurable'}


def stage_skill(stage, spec, n):
    jev = JEV.format(judgments=spec["judgments"], rubric=spec.get("rubric", "post.viral"))
    law_rows = "\n".join(f"- {l}" for l in n["laws"])
    subs = "\n".join(f"| `references/{f}` | {d} |" for f, d, _ in spec["subs"])
    body = f"""{frontmatter(stage, 'JEV-FIRST MANDATE, findable at task start: every typed judgment in this stage goes to rig-s1gate (Jev) BEFORE any frontier LLM call, and DEFERRED is the only answer when the classifier is down. ' + spec['desc'] + ' Child of skool-growth-os.',
        ['skool', 'skool-growth-os', stage.split('-', 1)[1]], spec['outcome'],
        [(f'grep:capabilities/skills/{stage}/SKILL.md:{ZERO_CLAIM_RULE[stage]}' if stage in ZERO_CLAIM_RULE else f'cmd:python3 capabilities/skills/skool-growth-os/scripts/claims_check.py capabilities/skills/{stage}/SKILL.md'),
         f'cmd:python3 capabilities/skills/skool-growth-os/scripts/check_family.py {stage}'],
        {'parent': 'skool-growth-os', 'laws': str(len(n['laws'])), 'corpus': 'data/corpora/skool (1,405 videos enumerated across 10 channels; transcripts captured incrementally)'})}
# {stage}: {spec['title']}

{jev}

## When to use / when not to

{spec['when']}

## Procedure

{spec['procedure']}

## Hands the next stage

{spec['handoff']}

## Laws (corpus doctrine, cite by id)

Each law is a paraphrase with the videos that carry it. `consensus` = two or more channels; `single-source` = one channel, treat as a hypothesis to test, not a rule. Verbatim quotes for every law are in `data/corpora/skool/notes/{stage}.md` (local corpus, not republished).

{law_rows or '(no laws captured yet for this stage - see data/corpora/skool/BUILD-LOG.md for capture status)'}

## Where the creators disagree

{n['contested'] or '(none recorded)'}

## Creator result claims (UNVERIFIED, never repeat as fact)

{n['creator'] or '(none recorded)'}

## Platform mechanics (Skool's own behavior)

{n['platform'] or '(none recorded)'}

## RIG application (RIG synthesis, not corpus claims)

{n['rig'] or 'See the procedure above.'}

## Sub-skills (load at most one)

| File | Use for |
|---|---|
{subs}

## Hard rules

{spec['rules']}

## Done-test

`python3 capabilities/skills/skool-growth-os/scripts/claims_check.py capabilities/skills/{stage}/SKILL.md` is GREEN only when every CLAIM id resolves to a captured transcript. `check_family.py {stage}` is GREEN only when the JEV section opens the body, every sub-skill file exists and is over 400 bytes, and no 12-word run of any transcript appears in the stage.
"""
    return body


def main(argv):
    check = "--check" in argv
    changed, built, pending = [], [], []
    doctrine_parts = []
    for stage in ORDER:
        spec = STAGES[stage]
        n = parse(stage) if not spec.get("no_notes") else {"laws": [], "contested": "", "creator": "", "platform": "", "rig": spec.get("rig", "")}
        if n is None:
            pending.append(stage)
            continue
        files = {SK / stage / "SKILL.md": stage_skill(stage, spec, n)}
        for f, _, text in spec["subs"]:
            files[SK / stage / "references" / f] = text.strip() + "\n"
        for path, text in files.items():
            if not path.exists() or path.read_text(encoding="utf-8") != text:
                changed.append(str(path.relative_to(REPO)))
                if not check:
                    path.parent.mkdir(parents=True, exist_ok=True)
                    path.write_text(text, encoding="utf-8")
        built.append(stage)
        if n["laws"]:
            doctrine_parts.append((stage, spec["title"], n))
    # doctrine index
    lines = []
    for stage, title, n in doctrine_parts:
        lines.append(f"## {stage}: {title}\n")
        lines += [f"- {l}" for l in n["laws"]]
        lines.append("")
    idx = SK / "skool-doctrine/references/law-index.md"
    text = "# Skool community doctrine: every law by stage\n\nGenerated by `skool-growth-os/scripts/build_family.py` from `data/corpora/skool/notes/`. Do not hand-edit.\n\n" + "\n".join(lines)
    if not idx.exists() or idx.read_text(encoding="utf-8") != text:
        changed.append(str(idx.relative_to(REPO)))
        if not check:
            idx.parent.mkdir(parents=True, exist_ok=True)
            idx.write_text(text, encoding="utf-8")
    print(f"built: {', '.join(built)}\npending notes: {', '.join(pending) or 'none'}\n{'would change' if check else 'wrote'}: {len(changed)} files")
    for c in changed:
        print("  ", c)
    return 2 if (check and changed) else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
