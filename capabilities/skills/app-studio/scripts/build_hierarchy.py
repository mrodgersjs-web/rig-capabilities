#!/usr/bin/env python3
"""Generate app-studio/hierarchy.json: the App Studio org chart across six kinds
(skills, agents, harnesses, loops, hooks, jev), each with one META, its MAIN tier, and
its SUB tier. Edit the tier tables in THIS file, not the JSON.

Skills MAIN tier = every skill the inventory included (JEV app.inventory-fit > 0.9) plus
every estate skill a sub-skill extends (marked reused). Paths resolve from the recorded
inventory, the canonical tree, the Aside user root, then the capability index; an
unresolvable name is written with path null so validate_hierarchy.py fails loudly.

Usage: build_hierarchy.py [--out PATH]. Stdlib only.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
SKILL = HERE.parent
REPO = SKILL.parents[2]
HOME = Path.home()

STAGES = [
    ("intake-spec", "What are we building, from what source, and how will we know it is done?"),
    ("architecture-stack", "Which stack fits this lane, and where will it actually build?"),
    ("design-ux", "What do the screens look like, and do real captures pass the judge?"),
    ("scaffold-setup", "Does a first slice build, serve, and screenshot in this sandbox?"),
    ("backend-data", "Are schema, auth, gates, and jobs proven by executed checks?"),
    ("web-frontend", "Does each route or component pass its check in the production build?"),
    ("mobile", "Does the real app on a clean simulator or device do what the spec says?"),
    ("ai-features", "Do AI features run without paid keys, validate outputs, and stay deterministic where they must?"),
    ("verify-qa", "Can the verification fail, and did someone other than the builder run it?"),
    ("ship-release", "Is the release request complete and held at Gate-D?"),
    ("operate-learn", "Did the mission's lessons reach the ledger and the owning skills?"),
]

SUB_SKILLS = [  # id, stage
    ("app-intake-spec", "intake-spec"), ("app-stack-select", "architecture-stack"),
    ("app-ui-design", "design-ux"), ("app-sandbox-survival", "scaffold-setup"),
    ("app-web-scaffold", "scaffold-setup"), ("app-data-layer", "backend-data"),
    ("app-web-frontend", "web-frontend"), ("app-mobile-build", "mobile"),
    ("app-ai-features", "ai-features"), ("app-verify-evidence", "verify-qa"),
    ("app-ship-web", "ship-release"), ("app-ship-mobile", "ship-release"),
    ("app-close-and-learn", "operate-learn"),
]

AGENTS = {
    "meta": ("app-studio-conductor", "capabilities/agents/app-studio-conductor.md"),
    "main": [  # id, path-or-None (resolve), stage, reused
        ("tg-web-builder", "capabilities/agents/tg-web-builder.md", "web-frontend", False),
        ("tg-mobile-builder", "capabilities/agents/tg-mobile-builder.md", "mobile", False),
        ("tg-ship-verifier", "capabilities/agents/tg-ship-verifier.md", "verify-qa", False),
        ("voltagent-nextjs-developer", None, "web-frontend", True),
        ("voltagent-frontend-developer", None, "web-frontend", True),
        ("voltagent-fullstack-developer", None, "backend-data", True),
        ("voltagent-mobile-app-developer", None, "mobile", True),
        ("ae-frontend-engineer", None, "web-frontend", True),
    ],
    "sub": [  # id, path-or-None, parent, stage, new
        ("tg-corpus-miner", "capabilities/agents/tg-corpus-miner.md", "app-studio-conductor", "intake-spec", False),
        ("tg-integration-fitter", "capabilities/agents/tg-integration-fitter.md", "tg-web-builder", "backend-data", False),
        ("tg-deploy-check-runner", "capabilities/agents/tg-deploy-check-runner.md", "tg-ship-verifier", "ship-release", False),
        ("app-sandbox-preflight", "capabilities/agents/app-sandbox-preflight.md", "app-studio-conductor", "scaffold-setup", True),
        ("app-ui-judge", "capabilities/agents/app-ui-judge.md", "app-studio-conductor", "design-ux", True),
        ("app-lesson-filer", "capabilities/agents/app-lesson-filer.md", "app-studio-conductor", "operate-learn", True),
    ],
}

H = "capabilities/harnesses/"
HARNESSES = {
    "meta": ("app-studio-session", H + "app-studio-session.yaml"),
    "main": [
        ("tg-app-studio-session", H + "tg-app-studio-session.yaml", "intake-spec"),
        ("hA-09-api-design", H + "hA-09-api-design.yaml", "backend-data"),
        ("hA-10-schema-design", H + "hA-10-schema-design.yaml", "backend-data"),
        ("hA-03-code-test-writing", H + "hA-03-code-test-writing.yaml", "verify-qa"),
        ("hA-04-code-debug", H + "hA-04-code-debug.yaml", "verify-qa"),
        ("hA-06-code-perf-audit", H + "hA-06-code-perf-audit.yaml", "verify-qa"),
        ("hA-12-ci-cd-design", H + "hA-12-ci-cd-design.yaml", "ship-release"),
        ("hA-13-code-security-audit", H + "hA-13-code-security-audit.yaml", "verify-qa"),
        ("hC-02-ui-design", H + "hC-02-ui-design.yaml", "design-ux"),
        ("hC-06-accessibility-audit", H + "hC-06-accessibility-audit.yaml", "design-ux"),
        ("hC-07-mobile-design", H + "hC-07-mobile-design.yaml", "mobile"),
    ],
    "sub": [  # id, path, parent, stage, new
        ("app-sandbox-build-verify", H + "app-sandbox-build-verify.yaml", "app-studio-session", "scaffold-setup", True),
        ("app-web-release", H + "app-web-release.yaml", "app-studio-session", "ship-release", True),
        ("app-mobile-release", H + "app-mobile-release.yaml", "app-studio-session", "ship-release", True),
        ("tg-corpus-mining", H + "tg-corpus-mining.yaml", "tg-app-studio-session", "intake-spec", False),
        ("tg-skeleton-implementation", H + "tg-skeleton-implementation.yaml", "tg-app-studio-session", "scaffold-setup", False),
        ("tg-ship-verify", H + "tg-ship-verify.yaml", "tg-app-studio-session", "verify-qa", False),
        ("tg-auth-schema-wiring", H + "tg-auth-schema-wiring.yaml", "tg-skeleton-implementation", "backend-data", False),
        ("tg-background-jobs", H + "tg-background-jobs.yaml", "tg-skeleton-implementation", "backend-data", False),
        ("tg-deploy-checklist", H + "tg-deploy-checklist.yaml", "tg-ship-verify", "ship-release", False),
    ],
}

L = "capabilities/loops/"
S = "capabilities/skills/"
LOOPS = {
    "meta": ("app-studio-mission-loop", L + "app-studio-mission-loop.md"),
    "main": [
        ("iqrsqpi-v20", S + "iqrsqpi-v20", "intake-spec"),
        ("phase-discipline-loop", S + "phase-discipline-loop", "verify-qa"),
        ("proof-loop", S + "proof-loop", "operate-learn"),
        ("adversarial-verification-loop", S + "adversarial-verification-loop", "verify-qa"),
        ("gate-d-loop", S + "gate-d-loop", "ship-release"),
        ("git-push-safety-loop", S + "git-push-safety-loop", "ship-release"),
        ("coding-harness-loop", L + "coding-harness.md", "verify-qa"),
        ("doer-checker-validator", L + "doer-checker-validator.md", "verify-qa"),
    ],
    "sub": [
        ("app-slice-loop", L + "app-slice-loop.md", "app-studio-mission-loop", "scaffold-setup", True),
        ("app-ui-judge-loop", L + "app-ui-judge-loop.md", "app-studio-mission-loop", "design-ux", True),
        ("app-lesson-promotion-loop", L + "app-lesson-promotion-loop.md", "app-studio-mission-loop", "operate-learn", True),
        ("iqrsqpi-v20-slice", S + "iqrsqpi-v20-slice", "iqrsqpi-v20", "scaffold-setup", False),
    ],
}

K = "capabilities/hooks/"
HOOKS = {
    "meta": ("app-studio-hook", K + "app-studio-hook.sh"),
    "main": [
        ("guard-secret-write", K + "guard-secret-write.sh", "backend-data"),
        ("guard-dangerous-commands", K + "guard-dangerous-commands.sh", "scaffold-setup"),
        ("s1gate-stage-gate", K + "s1gate-stage-gate.sh", "verify-qa"),
        ("rig-loop-hook", K + "rig-loop-hook.sh", "verify-qa"),
        ("tac-plan-gate", K + "tac-plan-gate.sh", "intake-spec"),
    ],
    "sub": [
        ("app-native-binary-preflight", K + "app-native-binary-preflight.sh", "app-studio-hook", "scaffold-setup", True),
        ("app-single-builder-guard", K + "app-single-builder-guard.sh", "app-studio-hook", "scaffold-setup", True),
        ("app-env-commit-guard", K + "app-env-commit-guard.sh", "app-studio-hook", "ship-release", True),
    ],
}

R = "capabilities/harnesses/s1gate/rubrics/"
JEV = {
    "meta": ("app.stage-gate", R + "app.stage-gate.json", ["app.stage-gate", "app", "app-studio", "app-stage", "web-app", "mobile-app"]),
    "main": [
        ("plan.readiness", "intake-spec"), ("code.diff", "verify-qa"), ("code.review", "verify-qa"),
        ("api.backend", "backend-data"), ("ui.design", "design-ux"), ("website.buyer", "web-frontend"),
        ("mission.completion", "operate-learn"), ("atomic.claim", "operate-learn"), ("doctrine.surface", "operate-learn"),
    ],
    "sub": [
        ("app.spec", "intake-spec", ["app.spec", "app-spec"]),
        ("app.stack", "architecture-stack", ["app.stack", "app-stack"]),
        ("app.ship", "ship-release", ["app.ship", "app-ship", "app-release"]),
        ("app.inventory-fit", "operate-learn", ["app.inventory-fit", "app-inventory"]),
    ],
}


def rel(p: Path) -> str:
    try:
        return str(p.relative_to(REPO))
    except ValueError:
        return "~/" + str(p.relative_to(HOME)) if str(p).startswith(str(HOME)) else str(p)


def build_resolver():
    inv = json.loads((SKILL / "references" / "inventory.json").read_text())["rows"]
    idx = json.loads((REPO / ".index.json").read_text())["assets"]
    by_name: dict[tuple[str, str], str] = {}
    rank = {"canonical": 0, "claude-agents": 1, "claude-skills": 1, "hermes-skills": 2}
    for a in sorted(idx, key=lambda a: rank.get(a.get("source"), 5)):
        nm = (a.get("name") or "").lower()
        p = a.get("abs_path") or (str(REPO / a["path"]) if a.get("source") == "canonical" and a.get("path") else None)
        if not (nm and p):
            continue
        if a["kind"] == "skill" and p.endswith("/SKILL.md"):
            p = p[: -len("/SKILL.md")]
        by_name.setdefault((a["kind"], nm), p)
        by_name.setdefault((a["kind"], re.sub(r"\.(md|toml|json)$", "", Path(p).name).lower()), p)
    for r in inv:
        p = r.get("path") or ""
        if p.startswith(("/", "~/", "capabilities/")):
            by_name.setdefault((r["kind"], r["name"].lower()), str(Path.home() / p[2:]) if p.startswith("~/") else p)

    def resolve(kind: str, name: str):
        if kind == "skill":
            for cand in (REPO / S / name, HOME / ".aside/u/0/skills/user" / name):
                if (cand / "SKILL.md").is_file():
                    return rel(cand)
        p = by_name.get((kind, name.lower()))
        if p:
            pp = Path(p) if p.startswith("/") else REPO / p
            return rel(pp)
        return None
    return inv, resolve


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=str(SKILL / "hierarchy.json"))
    a = ap.parse_args(argv)
    inv, resolve = build_resolver()

    main_skills: dict[str, dict] = {}
    for r in inv:
        if r["kind"] == "skill" and r["decision"] == "include":
            main_skills[r["name"]] = {"id": r["name"], "stage": r["stage"], "path": resolve("skill", r["name"]),
                                      "source": r["source"], "jev_noul": r["jev"].get("noul"),
                                      "jev_decision_id": r["jev"].get("decision_id"), "why": "inventory include"}
    subs = []
    for sid, stage in SUB_SKILLS:
        text = (REPO / S / sid / "SKILL.md").read_text()
        m = re.search(r'^\s*extends:\s*"([^"]*)"', text, re.M)
        ext = [e.strip() for e in (m.group(1) if m else "").split(",") if e.strip()]
        subs.append({"id": sid, "stage": stage, "path": S + sid, "parent": "app-studio", "new": True, "extends": ext})
        for e in ext:
            if e not in main_skills:
                main_skills[e] = {"id": e, "stage": stage, "path": resolve("skill", e), "source": "estate",
                                  "reused": True, "why": f"extended by {sid}"}

    tiers = {
        "skills": {"meta": {"id": "app-studio", "path": S + "app-studio", "new": True},
                   "main": sorted(main_skills.values(), key=lambda x: (x["stage"], x["id"])), "sub": subs},
        "agents": {"meta": {"id": AGENTS["meta"][0], "path": AGENTS["meta"][1], "generalized": "2026-09-27"},
                   "main": [{"id": i, "path": p or resolve("agent", i), "stage": st, "reused": ru} for i, p, st, ru in AGENTS["main"]],
                   "sub": [{"id": i, "path": p or resolve("agent", i), "parent": pa, "stage": st, "new": nw} for i, p, pa, st, nw in AGENTS["sub"]]},
        "harnesses": {"meta": {"id": HARNESSES["meta"][0], "path": HARNESSES["meta"][1], "new": True},
                      "main": [{"id": i, "path": p, "stage": st} for i, p, st in HARNESSES["main"]],
                      "sub": [{"id": i, "path": p, "parent": pa, "stage": st, "new": nw} for i, p, pa, st, nw in HARNESSES["sub"]]},
        "loops": {"meta": {"id": LOOPS["meta"][0], "path": LOOPS["meta"][1], "new": True},
                  "main": [{"id": i, "path": p, "stage": st} for i, p, st in LOOPS["main"]],
                  "sub": [{"id": i, "path": p, "parent": pa, "stage": st, "new": nw} for i, p, pa, st, nw in LOOPS["sub"]]},
        "hooks": {"meta": {"id": HOOKS["meta"][0], "path": HOOKS["meta"][1], "new": True, "wired_live": False},
                  "main": [{"id": i, "path": p, "stage": st} for i, p, st in HOOKS["main"]],
                  "sub": [{"id": i, "path": p, "parent": pa, "stage": st, "new": nw, "wired_live": False} for i, p, pa, st, nw in HOOKS["sub"]]},
        "jev": {"meta": {"id": JEV["meta"][0], "path": JEV["meta"][1], "kinds": JEV["meta"][2], "new": True},
                "main": [{"id": i, "path": R + i + ".json", "stage": st} for i, st in JEV["main"]],
                "sub": [{"id": i, "path": R + i + ".json", "parent": "app.stage-gate", "stage": st, "kinds": k, "new": True} for i, st, k in JEV["sub"]]},
    }
    out = {"family": "app-studio", "version": "1.0.0", "generated_by": "scripts/build_hierarchy.py",
           "stages": [{"id": s, "question": q} for s, q in STAGES],
           "lessons": "references/lessons.jsonl", "inventory": "references/inventory.json", "tiers": tiers}
    Path(a.out).write_text(json.dumps(out, indent=1) + "\n")
    counts = {k: {"meta": 1, "main": len(v["main"]), "sub": len(v["sub"])} for k, v in tiers.items()}
    unresolved = [e["id"] for v in tiers.values() for t in ("main", "sub") for e in v[t] if not e.get("path")]
    print(json.dumps({"out": rel(Path(a.out)), "counts": counts, "unresolved": unresolved}, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
