#!/usr/bin/env python3
"""Generate traject-os/hierarchy.json: the Traject OS org chart across six kinds
(skills, agents, harnesses, loops, hooks, jev), each with one META, its MAIN tier, and
its SUB tier. Edit the tier tables in THIS file, not the JSON.

Skills MAIN tier = the job-lane skills the stages reach for (installed under
~/.aside/u/0/skills/user). Paths resolve from the canonical tree, then the Aside user
root; an unresolvable name is written with path null so validate_hierarchy.py fails loudly.

Usage: build_hierarchy.py [--out PATH]. Stdlib only.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
SKILL = HERE.parent
REPO = SKILL.parents[2]
HOME = Path.home()
S = "capabilities/skills/"
A = "~/.aside/u/0/skills/user/"

STAGES = [
    ("target-qualify", "Is this role in Mike's band and shape, and is it worth a slot?"),
    ("source-dedupe", "Has this employer+role+req already been applied to or receipted?"),
    ("tailor", "Does the lane resume say only source-bound, verified things about this role?"),
    ("apply", "Is the form filled from confirmed facts and held before the one click Mike owns?"),
    ("reach", "Is this note linted, gated, one-ask one-nudge, and held at Gate-D?"),
    ("room-build", "Is the room Lucy-ordered and built only from resume-verified claims?"),
    ("drill", "Does every drilled answer carry a number or NONE?"),
    ("interview-day", "Does every live answer carry a number or NONE, with no floor or banned claim?"),
    ("debrief", "Is the 5-line debrief captured within 2h and saved to both stores?"),
    ("follow-up-negotiate", "Is the thank-you/nudge/negotiation drafted, one ask one nudge, held at Gate-D?"),
    ("learn", "Did every new failure become a typed lesson that reached its owning sub-skill?"),
]

SUB_SKILLS = [  # id, primary stage, stages covered
    ("traject-target-qualify", "target-qualify", ["target-qualify", "source-dedupe"]),
    ("traject-apply-bridge", "apply", ["tailor", "apply"]),
    ("traject-reach", "reach", ["reach"]),
    ("traject-room-build", "room-build", ["room-build"]),
    ("traject-drill", "drill", ["drill", "interview-day"]),
    ("traject-debrief", "debrief", ["debrief"]),
    ("traject-follow-up", "follow-up-negotiate", ["follow-up-negotiate"]),
    ("traject-proof", "cross-cutting", []),
    ("traject-learn", "learn", ["learn"]),
]

MAIN_SKILLS = [  # id, path, stages covered
    ("lucy-skills", A + "lucy-skills", ["tailor", "room-build", "drill", "interview-day", "follow-up-negotiate"]),
    ("aside-job-operator", "~/.aside/u/0/skill-library/aside-job-operator", ["target-qualify", "source-dedupe", "tailor", "apply", "reach", "debrief", "learn"]),
    ("lv-outreach", "capabilities/skills/lv-outreach", ["reach", "follow-up-negotiate"]),
    ("lv-engage", "capabilities/skills/lv-engage", ["reach"]),
    ("lv-profile", "capabilities/skills/lv-profile", ["cross-cutting"]),
    ("linkedin-viral", A + "linkedin-viral", ["cross-cutting"]),
]

AGENTS = {
    "meta": ("traject-conductor", "capabilities/agents/traject-conductor.md"),
    "main": [
        ("traject-room-builder", "capabilities/agents/traject-room-builder.md", "room-build"),
        ("traject-apply-operator", "capabilities/agents/traject-apply-operator.md", "apply"),
        ("traject-outreach-drafter", "capabilities/agents/traject-outreach-drafter.md", "reach"),
        ("traject-coach-grader", "capabilities/agents/traject-coach-grader.md", "drill"),
        ("traject-proof-curator", "capabilities/agents/traject-proof-curator.md", "cross-cutting"),
        ("traject-debrief-clerk", "capabilities/agents/traject-debrief-clerk.md", "debrief"),
    ],
    "sub": [  # id, path, parent, stage
        ("traject-company-researcher", "capabilities/agents/traject-company-researcher.md", "traject-room-builder", "room-build"),
        ("traject-jd-decoder", "capabilities/agents/traject-jd-decoder.md", "traject-room-builder", "room-build"),
        ("traject-claim-verifier", "capabilities/agents/traject-claim-verifier.md", "traject-proof-curator", "cross-cutting"),
        ("traject-dedupe-checker", "capabilities/agents/traject-dedupe-checker.md", "traject-apply-operator", "source-dedupe"),
        ("traject-recency-checker", "capabilities/agents/traject-recency-checker.md", "traject-outreach-drafter", "reach"),
    ],
}

H = "capabilities/harnesses/"
HARNESSES = {
    "meta": ("traject-session", H + "traject-session.yaml"),
    "main": [
        ("traject-interview-prep-session", H + "traject-interview-prep-session.yaml", "interview-day"),
        ("traject-application-session", H + "traject-application-session.yaml", "apply"),
        ("traject-outreach-session", H + "traject-outreach-session.yaml", "reach"),
        ("traject-proof-publish-session", H + "traject-proof-publish-session.yaml", "cross-cutting"),
    ],
    "sub": [  # id, path, parent, stage
        ("traject-room-build", H + "traject-room-build.yaml", "traject-interview-prep-session", "room-build"),
        ("traject-drill-rep", H + "traject-drill-rep.yaml", "traject-interview-prep-session", "drill"),
        ("traject-debrief-capture", H + "traject-debrief-capture.yaml", "traject-interview-prep-session", "debrief"),
        ("traject-apply-one-role", H + "traject-apply-one-role.yaml", "traject-application-session", "apply"),
    ],
}

L = "capabilities/loops/"
LOOPS = {
    "meta": ("traject-daily-loop", L + "traject-daily-loop.md"),
    "main": [
        ("iqrsqpi-v20", S + "iqrsqpi-v20", "learn"),
        ("gate-d-loop", S + "gate-d-loop", "apply"),
        ("proof-loop", S + "proof-loop", "cross-cutting"),
        ("done-claim-verification", S + "done-claim-verification", "learn"),
        ("rig-realign-weekly", L + "rig-realign-weekly.md", "learn"),
    ],
    "sub": [
        ("traject-interview-loop", L + "traject-interview-loop.md", "traject-daily-loop", "interview-day"),
        ("traject-weekly-learn-loop", L + "traject-weekly-learn-loop.md", "traject-daily-loop", "learn"),
    ],
}

K = "capabilities/hooks/"
HOOKS = {  # reused governance hooks only; nothing here is new to this family
    "meta": ("guard-secret-write", K + "guard-secret-write.sh"),
    "main": [
        ("guard-dangerous-commands", K + "guard-dangerous-commands.sh", "apply"),
        ("immutable-surface-guard", K + "immutable-surface-guard.sh", "cross-cutting"),
    ],
    "sub": [],
}

R = "capabilities/harnesses/s1gate/rubrics/"
JEV = {
    "meta": ("job.fit", R + "job.fit.json", ["job.fit"]),
    "main": [
        ("resume.ats", "tailor", ["resume.ats"]),
        ("resume.recruiter", "tailor", ["resume.recruiter"]),
        ("resume.screen", "tailor", ["resume.screen"]),
        ("jobhunt.select", "target-qualify", ["jobhunt.select"]),
        ("jobhunt.resume", "tailor", ["jobhunt.resume"]),
        ("job.navigate", "apply", ["job.navigate"]),
        ("interview.answer", "drill", ["interview.answer"]),
        ("outreach.first", "reach", ["outreach.first"]),
        ("email.outreach", "reach", ["email.outreach"]),
        ("offer.eval", "follow-up-negotiate", ["offer.eval"]),
        ("story.bank", "room-build", ["story.bank"]),
        ("company.fit", "target-qualify", ["company.fit"]),
        ("contact.pick", "reach", ["contact.pick"]),
        ("jd.decode", "room-build", ["jd.decode"]),
        ("hm.technical", "interview-day", ["hm.technical"]),
        ("screen.pitch", "interview-day", ["screen.pitch"]),
        ("mission.completion", "learn", ["mission.completion"]),
        ("atomic.claim", "cross-cutting", ["atomic.claim"]),
    ],
    "sub": [  # id, stage, kinds
        ("job.formfill", "apply", ["job.formfill"]),
        ("form.field", "apply", ["form.field"]),
        ("outreach.intro", "reach", ["outreach.intro"]),
        ("reply.intent", "reach", ["reply.intent"]),
        ("jobhunt.warm", "reach", ["jobhunt.warm"]),
        ("followup.note", "follow-up-negotiate", ["followup.note"]),
        ("rejection.cause", "debrief", ["rejection.cause"]),
        ("training.readiness", "drill", ["training.readiness"]),
    ],
}


def rel(p: Path) -> str:
    try:
        return str(p.relative_to(REPO))
    except ValueError:
        return "~/" + str(p.relative_to(HOME)) if str(p).startswith(str(HOME)) else str(p)


def resolve(kind: str, name_or_path: str) -> str | None:
    """Resolve an id or a path: canonical repo first, then the Aside user root."""
    raw = name_or_path
    cands = []
    if raw.startswith("~/"):
        cands = [HOME / raw[2:]]
    elif raw.startswith("/"):
        cands = [Path(raw)]
    elif raw.startswith("capabilities/"):
        cands = [REPO / raw]
    else:
        cands = [REPO / S / raw, HOME / ".aside/u/0/skills/user" / raw]
    for c in cands:
        if c.is_dir() and (c / "SKILL.md").is_file():
            return rel(c)
        if c.is_file():
            return rel(c)
    return None


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=str(SKILL / "hierarchy.json"))
    a = ap.parse_args(argv)

    subs = []
    for sid, stage, covers in SUB_SKILLS:
        subs.append({"id": sid, "stage": stage, "covers": covers,
                     "path": resolve("skill", sid), "parent": "traject-os", "new": True})
    mains = []
    for mid, path, covers in MAIN_SKILLS:
        mains.append({"id": mid, "stage": covers[0] if covers else "cross-cutting", "covers": covers,
                      "path": resolve("skill", path), "reused": True})

    def agent_rows(rows, parent_key=None):
        out = []
        for row in rows:
            if parent_key:
                i, p, pa, st = row
                out.append({"id": i, "path": resolve("agent", p), "parent": pa, "stage": st, "new": True})
            else:
                i, p, st = row
                out.append({"id": i, "path": resolve("agent", p), "stage": st, "reused": True})
        return out

    def flat(rows, parent_key=None):
        out = []
        for row in rows:
            if parent_key:
                i, p, pa, st = row
                out.append({"id": i, "path": resolve("file", p), "parent": pa, "stage": st, "new": True})
            else:
                i, p, st = row
                out.append({"id": i, "path": resolve("file", p), "stage": st, "reused": True})
        return out

    def jev_rows(rows, sub=False):
        out = []
        for row in rows:
            i, st, kinds = row
            e = {"id": i, "path": R + i + ".json", "stage": st, "kinds": kinds, "new": True}
            if sub:
                e["parent"] = "job.fit"
            out.append(e)
        return out

    tiers = {
        "skills": {"meta": {"id": "traject-os", "path": S + "traject-os", "new": True},
                   "main": mains, "sub": subs},
        "agents": {"meta": {"id": AGENTS["meta"][0], "path": AGENTS["meta"][1], "new": True},
                   "main": agent_rows(AGENTS["main"]),
                   "sub": agent_rows(AGENTS["sub"], parent_key=True)},
        "harnesses": {"meta": {"id": HARNESSES["meta"][0], "path": HARNESSES["meta"][1], "new": True},
                      "main": flat(HARNESSES["main"]),
                      "sub": flat(HARNESSES["sub"], parent_key=True)},
        "loops": {"meta": {"id": LOOPS["meta"][0], "path": LOOPS["meta"][1], "new": True},
                  "main": flat(LOOPS["main"]),
                  "sub": flat(LOOPS["sub"], parent_key=True)},
        "hooks": {"meta": {"id": HOOKS["meta"][0], "path": HOOKS["meta"][1], "new": False, "wired_live": False},
                  "main": flat(HOOKS["main"]),
                  "sub": flat(HOOKS["sub"])},
        "jev": {"meta": {"id": JEV["meta"][0], "path": JEV["meta"][1], "kinds": JEV["meta"][2], "new": True},
                "main": jev_rows(JEV["main"]),
                "sub": jev_rows(JEV["sub"], sub=True)},
    }
    out = {"family": "traject-os", "version": "1.0.0", "generated_by": "scripts/build_hierarchy.py",
           "stages": [{"id": s, "question": q} for s, q in STAGES],
           "lessons": "references/lessons.jsonl", "tiers": tiers}
    Path(a.out).write_text(json.dumps(out, indent=1) + "\n")
    counts = {k: {"meta": 1, "main": len(v["main"]), "sub": len(v["sub"])} for k, v in tiers.items()}
    unresolved = [e["id"] for v in tiers.values() for t in ("main", "sub") for e in v[t] if not e.get("path")]
    unresolved += [tiers["skills"]["meta"]["id"]] if not tiers["skills"]["meta"].get("path") else []
    print(json.dumps({"out": rel(Path(a.out)), "counts": counts, "unresolved": unresolved}, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
