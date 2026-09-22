"""Local structured-answer gate. No networking or submission capability.

Checks the supplied résumé bytes and declared prior-employer answers. It cannot
classify natural-language questions or independently prove narrative truth.
"""
import argparse
import hashlib
import json
import re
from pathlib import Path
from urllib.parse import urlsplit

# Independent binding to the reviewed employer facts. Changing a résumé/fact
# baseline requires an explicit review and a new pin; editing facts alone fails.
TRUSTED_FACTS_SHA256 = "2604c909d03ae9e9721b2518a564088bc68fa56b73b7f84015cc4235c1f163c7"


def normalize(value):
    return re.sub(r"[^a-z0-9]", "", value.casefold())


def check(resume, facts, packet):
    errors = []
    facts_digest = hashlib.sha256(json.dumps(facts, sort_keys=True, separators=(',', ':')).encode()).hexdigest()
    if facts_digest != TRUSTED_FACTS_SHA256:
        errors.append("employer_baseline_hash_mismatch")
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
    try:
        target = urlsplit(str(packet.get("job_url", "")))
        valid_url = target.scheme == 'https' and bool(target.hostname) and '.' in target.hostname and len(target.path) > 1 and not target.username and not target.password and not target.fragment
    except ValueError:
        valid_url = False
    if not valid_url:
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
            elif source.startswith('resume:') and source not in {'resume:employer:' + str(e['id']) for e in employers}:
                errors.append(prefix + "unverified_resume_reference_requires_semantic_review")
            elif not source.partition(':')[2].strip():
                errors.append(prefix + "empty_evidence_reference")
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
