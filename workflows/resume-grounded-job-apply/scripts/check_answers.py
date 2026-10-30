"""Local structured-answer gate. No networking or submission capability.

Checks the supplied résumé bytes and declared prior-employer answers. It cannot
classify natural-language questions or independently prove narrative truth.
"""
import argparse
import hashlib
import json
import re
from pathlib import Path


def normalize(value):
    return re.sub(r"[^a-z0-9]", "", value.casefold())


def check(resume, facts, packet):
    errors = []
    digest = hashlib.sha256(resume).hexdigest()
    if digest != facts.get("source_sha256") or digest != packet.get("resume_sha256"):
        errors.append("resume_hash_mismatch")
    employers = facts.get("employers")
    if not isinstance(employers, list) or not employers:
        return errors + ["empty_employer_baseline"]
    aliases = {}
    for employer in employers:
        for name in [employer.get("name", ""), *employer.get("aliases", [])]:
            if name:
                aliases[normalize(name)] = employer.get("id")
    rows = packet.get("answers")
    if not isinstance(rows, list) or not rows:
        return errors + ["empty_answers"]
    if not str(packet.get("job_url", "")).startswith("https://"):
        errors.append("missing_exact_job_url")
    for i, row in enumerate(rows):
        if not isinstance(row, dict):
            errors.append(f"row_{i}:invalid_row")
            continue
        prefix = f"row_{i}:"
        if not row.get("question") or "REPLACE_" in str(row.get("question")):
            errors.append(prefix + "missing_question")
        answer, source = row.get("answer"), row.get("source")
        if answer in (None, ""):
            if row.get("required") is not False:
                errors.append(prefix + "required_answer_unknown")
            continue
        if row.get("kind") == "prior_employer":
            employer = row.get("employer")
            if not isinstance(employer, str) or not normalize(employer):
                errors.append(prefix + "missing_employer")
                continue
            known = aliases.get(normalize(employer))
            if known:
                if answer != "Yes" or source != "resume:employer:" + known:
                    errors.append(prefix + "resume_employer_requires_sourced_yes")
            elif answer != "No" or source != "standing_user_rule:resume_employment_only":
                errors.append(prefix + "unlisted_employer_requires_no")
        elif row.get("kind") == "other":
            if not isinstance(source, str) or not source.startswith(("resume:", "user-confirmed:", "application-record:")):
                errors.append(prefix + "unrelated_answer_requires_own_evidence")
        else:
            errors.append(prefix + "unknown_question_kind")
    return errors


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--resume", type=Path, required=True)
    parser.add_argument("--facts", type=Path, required=True)
    parser.add_argument("--answers", type=Path, required=True)
    args = parser.parse_args()
    try:
        errors = check(args.resume.read_bytes(), json.loads(args.facts.read_text()), json.loads(args.answers.read_text()))
    except (OSError, ValueError, TypeError, AttributeError) as exc:
        print(json.dumps({"status": "BLOCK", "error_type": type(exc).__name__}))
        return 2
    print(json.dumps({"status": "PASS_STRUCTURED_CHECK" if not errors else "BLOCK", "errors": errors,
                      "semantic_review_required": True, "submission_authorized": False}))
    return 2 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
