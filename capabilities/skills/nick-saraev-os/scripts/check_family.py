#!/usr/bin/env python3
"""Family check for nick-saraev-os. Exit 0 = pass.
Checks: all 26 skills exist with frontmatter name == dir; every CLAIM(id@Nm) tag resolves to a
video in references/sources.json and the minute is inside that video's length; every SKILL.md has a
done-test section; the meta routes only (no Procedure section).
--plant: inject a bad tag into a copy and prove the check fails (exit 0 if it was caught)."""
import json, os, re, sys, shutil, tempfile
HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SKILLS_DIR = os.path.dirname(HERE)
FAMILY = ["nick-saraev-os",
  "ns-agentic-workflows","ns-directive-writer","ns-execution-scripts","ns-agent-evals-verifier","ns-agent-security",
  "ns-automation-builds","ns-api-http-integration","ns-scenario-architecture","ns-data-transformation",
  "ns-lead-gen-outbound","ns-lead-scraping","ns-email-enrichment","ns-cold-email-personalization",
  "ns-offer-and-sales","ns-niche-and-offer","ns-value-pricing","ns-sales-call-and-proposal","ns-retainer-conversion",
  "ns-agency-scale","ns-bottleneck-diagnosis","ns-productization","ns-delegation",
  "ns-ai-career-and-content","ns-content-engine","ns-career-positioning"]
TAG = re.compile(r"CLAIM\(([^)]*)\)")
LOC = re.compile(r"^([A-Za-z0-9_-]{11})@(\d+)m$")

def check(root):
    errs = []
    src = {v["id"]: v for v in json.load(open(os.path.join(root, "nick-saraev-os/references/sources.json")))}
    tags = 0
    for name in FAMILY:
        d = os.path.join(root, name)
        p = os.path.join(d, "SKILL.md")
        if not os.path.isfile(p):
            errs.append(f"missing {name}/SKILL.md"); continue
        text = open(p).read()
        m = re.search(r"^name:\s*\"?([^\s\"]+)", text, re.M)
        if not m or m.group(1) != name: errs.append(f"{name}: frontmatter name mismatch")
        if "## Done-test" not in text: errs.append(f"{name}: no done-test")
        if name == "nick-saraev-os" and "## Procedure" in text: errs.append("meta must route only")
        files = [p] + [os.path.join(dp, f) for dp, _, fs in os.walk(os.path.join(d, "references")) for f in fs if f.endswith(".md") and f != "build-card.md"]
        for fp in files:
            for inner in TAG.findall(open(fp).read()):
                tags += 1
                lm = LOC.match(inner.strip())
                if not lm: errs.append(f"{os.path.relpath(fp, root)}: malformed CLAIM({inner})"); continue
                vid, minute = lm.group(1), int(lm.group(2))
                v = src.get(vid)
                if not v: errs.append(f"{os.path.relpath(fp, root)}: unknown video {vid}")
                elif minute > v["minutes"] + 1: errs.append(f"{os.path.relpath(fp, root)}: {vid}@{minute}m past end ({v['minutes']}m)")
    return errs, tags

if __name__ == "__main__":
    if "--plant" in sys.argv:
        tmp = tempfile.mkdtemp()
        try:
            for n in FAMILY:
                if os.path.isdir(os.path.join(SKILLS_DIR, n)): shutil.copytree(os.path.join(SKILLS_DIR, n), os.path.join(tmp, n))
            p = os.path.join(tmp, "ns-value-pricing/SKILL.md")
            open(p, "a").write("\n- planted law CLAIM(ZZZZZZZZZZZ@999m)\n")
            errs, _ = check(tmp)
            caught = any("ZZZZZZZZZZZ" in e for e in errs)
            print("PLANT", "CAUGHT" if caught else "MISSED"); sys.exit(0 if caught else 1)
        finally: shutil.rmtree(tmp)
    errs, tags = check(SKILLS_DIR)
    for e in errs: print("FAIL", e)
    print(f"RESULT skills={len(FAMILY)} tags_checked={tags} errors={len(errs)}")
    sys.exit(1 if errs else 0)
