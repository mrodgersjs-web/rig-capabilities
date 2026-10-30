#!/usr/bin/env python3
"""Build a clean allowlisted Aside edition without personal career material."""
import argparse
import hashlib
import json
import re
import shutil
import zipfile
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--quality-module", type=Path, required=True)
    parser.add_argument("--quality-guide", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    source = Path(__file__).resolve().parent
    local = source.parent
    canonical = local.parent
    output = args.output.resolve()
    output.mkdir(parents=True, exist_ok=False)
    bundle = output / "Job-Applier-Aside"
    bundle.mkdir()
    names = ["job-applier", "lucy-skills", "lucyskills", "lucy-executive-evidence", "lucy-resume-evidence"]

    def put(relative, body):
        path = bundle / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(body.rstrip() + "\n")

    def template(name):
        return (source / name).read_text()

    def generic(body):
        body = re.sub(r"\bMike(?:['’]s)?\b", lambda m: "the candidate's" if any(c in m.group() for c in "'’") else "the candidate", body, flags=re.I)
        return body.replace("the candidate-specific", "candidate-specific").replace("the candidate's preparation convention", "this package's preparation convention")

    put("install.py", template("install.py"))
    put("README.md", template("portable-readme.md"))
    put("skills/job-applier/SKILL.md", template("portable-job-applier.md"))
    for leaf in sorted((local / "steps").glob("*/SKILL.md")):
        body = generic(leaf.read_text()).replace("../../references/quality-gates.md", "../../references/quality.md")
        put("skills/job-applier/" + leaf.relative_to(local).as_posix(), body)
    family = generic((local / "references/family-packet.md").read_text()).split("## Existing app compatibility")[0]
    family += "\n## Portable runtime boundary\n\nThe nested leaves are instructions loaded through Job Applier. This package does not install a separate application or automatically run eight stages. Use your existing Aside tools to produce the artifacts and actual receipts. The local validator checks structure and hashes only; it cannot authenticate approvals or certify semantic truth.\n"
    put("skills/job-applier/references/family-packet.md", family)
    for relative in ("scripts/validate_packet.py", "tests/test_validate_packet.py"):
        put("skills/job-applier/" + relative, (local / relative).read_text())
    put("skills/job-applier/references/process.md", template("portable-process.md"))
    put("skills/job-applier/references/quality.md", template("portable-quality.md"))
    quality_guide = args.quality_guide.read_text().replace("work/resume_quality.py", "tools/resume_quality.py")
    quality_guide = quality_guide.split("## Verification contract")[0]
    put("skills/job-applier/references/quality-api.md", quality_guide)
    put("skills/job-applier/references/pilot-and-recovery.md", generic((local / "references/pilot-and-recovery.md").read_text()))
    for script in ["render_resume.py", "pilot_receipts.py"]:
        put("skills/job-applier/tools/" + script, template(script))
    put("skills/job-applier/tools/resume_quality.py", args.quality_module.read_text())
    put("skills/lucy-skills/SKILL.md", template("portable-lucy-router.md"))
    put("skills/lucy-skills/references/resume-guidance.md", template("portable-resume-guidance.md"))
    put("skills/lucy-executive-evidence/references/source-map.md", template("portable-source-map.md"))
    put("skills/lucy-resume-evidence/references/before-after.md", template("portable-before-after.md"))
    put("skills/lucy-executive-evidence/references/evidence-contract.md", generic((canonical / "lucy-executive-evidence/references/evidence-contract.md").read_text()))
    executive = generic((canonical / "lucy-executive-evidence/SKILL.md").read_text())
    executive = executive.replace("Read [worked examples](references/worked-examples.md) only when metrics, industry transfer, or proposed scenarios need clarification.", "Read the evidence contract when metrics, industry transfer, or proposed scenarios need clarification.")
    put("skills/lucy-executive-evidence/SKILL.md", executive)
    resume = generic((canonical / "lucy-resume-evidence/SKILL.md").read_text())
    resume = resume.replace("For Lucy's resume-specific advice, use the installed sibling `../lucy-skills/SKILL.md` and its relevant resume leaf; cite that leaf's actual SRC IDs.", "For Lucy's resume-specific advice, read [the portable resume guidance](../lucy-skills/references/resume-guidance.md) and cite its actual SRC IDs.")
    put("skills/lucy-resume-evidence/SKILL.md", resume)
    put("skills/lucyskills/SKILL.md", """---
name: lucyskills
description: Route Lucy resume and executive interview requests to the portable evidence skills, or use Job Applier for a reviewed application packet.
---

# Lucy skills alias

For resume drafting or evidence review, use [Lucy resume evidence](../lucy-resume-evidence/SKILL.md). For executive interview preparation, use [Lucy executive evidence](../lucy-executive-evidence/SKILL.md). For a full application packet, use [Job Applier](../job-applier/SKILL.md). For the source guide and scope, use [Lucy skills](../lucy-skills/SKILL.md).

Use the host's supported skill invocation. This alias does not register a bare slash command. With no task supplied, ask whether the candidate wants resume work, executive interview preparation, or an application packet. Do not silently invent an assignment.

No route grants submission, message, profile-edit, or publishing authority.
""")
    for name in names:
        title = "Job Applier" if name == "job-applier" else name.replace("-", " ").title()
        prompt = "Use $" + name + " with my supplied job description and evidence; preserve factual uncertainty and stop before any external action."
        put(f"skills/{name}/agents/openai.yaml", "interface:\n  display_name: " + json.dumps(title) + "\n  short_description: \"Source-bound resume and application preparation\"\n  default_prompt: " + json.dumps(prompt) + "\npolicy:\n  allow_implicit_invocation: true\n")
    put("SOURCES.md", """# Sources and distribution scope

This bundle contains authored process guidance, claim-handling rules, and local Python helpers. The source links and nineteen-word interview anchor set are in the Lucy references. No full video transcripts or scraped corpus are included.

The resume and executive evidence guidance is adapted from the author's reviewed local skill packages. Candidate names, resumes, examples, employer records, application history, interview notes, credentials, and machine-specific source paths are excluded. The portable workflow uses the recipient's own materials and provider configuration.

The Jev adapter calls the recipient-configured TypeSafe provider. The installer performs no network calls. The package contains no model weights, API keys, service installation, recurring jobs, browser profile, or application submission tool. Installation does not prove end-to-end execution on the recipient's machine.
""")
    bad = []
    for path in bundle.rglob("*"):
        if not path.is_file():
            continue
        body = path.read_text()
        for pattern in [r"/Users/", r"rig128gb", r"Mike", r"Rodgers", r"jloehr2131", r"\.applypilot", r"Operation Get a Job", r"Intellibus", r"EmOpti", r"Caterpillar", r"Choreo", r"Oracle", r"BEGIN .*PRIVATE KEY", r"sk-[A-Za-z0-9]{20,}"]:
            if re.search(pattern, body, re.I):
                bad.append({"file": str(path.relative_to(bundle)), "pattern": pattern})
    if bad:
        raise ValueError("Portable privacy scan failed: " + json.dumps(bad))
    files = {p.relative_to(bundle).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(bundle.rglob("*")) if p.is_file()}
    manifest = {"version": "1.1.0", "name": "Job Applier, portable Aside edition", "skills": names, "files": files}
    put("MANIFEST.json", json.dumps(manifest, indent=2))
    archive = output / "Job-Applier-Aside.zip"
    with zipfile.ZipFile(archive, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for path in sorted(bundle.rglob("*")):
            if path.is_file():
                info = zipfile.ZipInfo("Job-Applier-Aside/" + path.relative_to(bundle).as_posix(), (2026, 10, 28, 0, 0, 0))
                info.compress_type = zipfile.ZIP_DEFLATED
                info.external_attr = 0o100644 << 16
                zf.writestr(info, path.read_bytes())
    checksum = hashlib.sha256(archive.read_bytes()).hexdigest()
    (output / "SHA256SUMS.txt").write_text(checksum + "  Job-Applier-Aside.zip\n")
    print(json.dumps({"archive": str(archive), "sha256": checksum, "files": len(files) + 1, "skills": names, "privacy_scan": "PASS", "quality_module_sha256": hashlib.sha256(args.quality_module.read_bytes()).hexdigest()}, indent=2))


if __name__ == "__main__":
    main()
