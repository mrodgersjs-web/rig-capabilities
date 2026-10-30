#!/usr/bin/env python3
"""Exercise the portable install and receipt boundaries in a temporary home."""
import argparse
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile
import zipfile
from datetime import datetime, timezone


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def tree(root):
    return {p.relative_to(root).as_posix(): sha(p) for p in root.rglob("*") if p.is_file()}


def main():
    sys.dont_write_bytecode = True
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("bundle", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    bundle = args.bundle.resolve()
    results = []

    def run(*argv, code=0, env=None):
        result = subprocess.run([sys.executable, *map(str, argv)], capture_output=True, text=True, timeout=60, env=env)
        if result.returncode != code:
            raise AssertionError({"args": list(map(str, argv)), "expected": code, "actual": result.returncode, "stdout": result.stdout, "stderr": result.stderr})
        return json.loads(result.stdout) if result.stdout.strip() else result.stderr

    def passed(name):
        results.append({"case": name, "status": "PASS"})

    run(bundle / "install.py", "verify")
    passed("archive file manifest verified")
    for path in bundle.glob("skills/*/SKILL.md"):
        text = path.read_text()
        assert text.startswith("---\n") and re.search(r"^name: .+", text, re.M) and re.search(r"^description: .+", text, re.M)
    broken = []
    for path in bundle.rglob("*.md"):
        for target in re.findall(r"\]\(([^)]+)\)", path.read_text()):
            if target.startswith(("http:", "https:", "#")):
                continue
            if not (path.parent / target).exists():
                broken.append({"source": str(path.relative_to(bundle)), "target": target})
    assert not broken, broken
    passed("five skills and every bundled markdown link resolve")
    with tempfile.TemporaryDirectory(prefix="job-applier-smoke-") as temporary:
        base = Path(temporary)
        home = base / "home"
        home.mkdir()
        first = run(bundle / "install.py", "install", "--home", home)
        assert first["status"] == "installed"
        root = home / ".aside/u/0/skills/user"
        assert tree(root) == tree(bundle / "skills")
        passed("fresh home receives all five complete skill trees")
        unchanged = run(bundle / "install.py", "install", "--home", home)
        assert unchanged["status"] == "already-installed"
        passed("repeat install is idempotent")
        changed = root / "lucy-skills/SKILL.md"
        changed.write_text(changed.read_text() + "\nRecipient edit.\n")
        run(bundle / "install.py", "uninstall", "--home", home, "--receipt", first["receipt"], code=2)
        assert "Recipient edit." in changed.read_text()
        passed("uninstall refuses to discard recipient edits")
        run(bundle / "install.py", "uninstall", "--home", home, "--receipt", first["receipt"], "--preserve-edits")
        removed = Path(first["receipt"]).parent / "removed/lucy-skills/SKILL.md"
        assert "Recipient edit." in removed.read_text() and not list(root.iterdir())
        assert run(bundle / "install.py", "uninstall", "--home", home, "--receipt", first["receipt"])["status"] == "already-uninstalled"
        passed("uninstall preserves changed copy and is idempotent")
        legacy = root / "lucy-skills"
        legacy.mkdir()
        (legacy / "SKILL.md").write_text("Existing recipient Lucy skills\n")
        original = tree(root)
        run(bundle / "install.py", "install", "--home", home, code=2)
        assert tree(root) == original
        passed("differing existing skill blocks before any writes")
        replacement = run(bundle / "install.py", "install", "--home", home, "--replace")
        assert tree(root) == tree(bundle / "skills")
        run(bundle / "install.py", "uninstall", "--home", home, "--receipt", replacement["receipt"])
        assert tree(root) == original
        passed("explicit replacement backs up and restores exact prior content")
        damaged = base / "damaged"
        shutil.copytree(bundle, damaged)
        (damaged / "skills/job-applier/SKILL.md").write_text("Tampered content\n")
        other = base / "other-home"
        other.mkdir()
        run(damaged / "install.py", "install", "--home", other, code=2)
        assert not (other / ".aside").exists()
        passed("tampered package fails closed without target changes")
        link_home = base / "link-home"
        link_home.mkdir()
        (link_home / ".aside").symlink_to(base / "outside", target_is_directory=True)
        run(bundle / "install.py", "install", "--home", link_home, code=2)
        passed("symlinked target root refused")
        ledger = base / "pilot.json"
        ledger.write_text('{"applications": []}')
        result = run(bundle / "skills/job-applier/tools/pilot_receipts.py", ledger)
        assert result["pilot_progress"] == "0/5" and result["autonomous_submission_authorized"] is False
        ledger.write_text('{"applications": [{"status": "drafted"}, {"status": "approved"}]}')
        result = run(bundle / "skills/job-applier/tools/pilot_receipts.py", ledger)
        assert result["pilot_progress"] == "0/5" and len(result["rejected"]) == 2
        passed("drafts and approvals cannot increment pilot")
        def evidence(name, content):
            path = base / name
            path.write_text(json.dumps(content) if not isinstance(content, str) else content)
            return {"path": name, "sha256": sha(path)}
        draft = evidence("working.md", "Synthetic working resume")
        final = evidence("final.docx", "Synthetic final bytes for offline receipt binding test")
        answers = evidence("answers.json", {})
        identity = {"employer": "Synthetic fixture employer", "requisition_id": "TEST-001", "destination": "https://example.invalid/test-only"}
        review = {"status": "factually_confirmed", "draft_sha256": draft["sha256"], "final_resume_sha256": final["sha256"], "human_response_reference": "synthetic:test-review", "human_page_approval_reference": "synthetic:test-page-approval", "reviewed_at": "2026-01-01T12:00:00Z"}
        approval = {**identity, "action": "submit_this_application", "human_response_reference": "synthetic:test-submit-approval", "final_resume_sha256": final["sha256"], "answers_sha256": answers["sha256"], "approved_at": "2026-01-01T12:01:00Z"}
        receipt_data = {**identity, "status": "submitted", "provider_receipt_id": "synthetic-test-only-1", "submitted_at": "2026-01-01T12:02:00Z", "provider_evidence": evidence("provider.txt", "Synthetic test-only confirmation, not a real application")}
        record = {**identity, "draft": draft, "final_resume": final, "answers": answers, "evidence_review": evidence("review.json", review), "submission_approval": evidence("approval.json", approval), "submission_receipt": evidence("receipt.json", receipt_data)}
        ledger.write_text(json.dumps({"applications": [record, record]}))
        result = run(bundle / "skills/job-applier/tools/pilot_receipts.py", ledger)
        assert result["pilot_progress"] == "1/5" and len(result["rejected"]) == 1
        passed("synthetic bound chain counts once and duplicate rejected")
        approval["approved_at"] = "2026-01-01T11:59:00Z"
        record["submission_approval"] = evidence("approval.json", approval)
        ledger.write_text(json.dumps({"applications": [record]}))
        result = run(bundle / "skills/job-applier/tools/pilot_receipts.py", ledger)
        assert result["pilot_progress"] == "0/5"
        passed("submission approval before resume review rejected")
        approval["approved_at"] = "2026-01-01T12:01:00Z"
        record["submission_approval"] = evidence("approval.json", approval)
        (base / "final.docx").write_text("Changed after approval")
        ledger.write_text(json.dumps({"applications": [record]}))
        result = run(bundle / "skills/job-applier/tools/pilot_receipts.py", ledger)
        assert result["pilot_progress"] == "0/5"
        passed("changed final attachment cannot count")
        context = base / "context.json"
        text = "Example role responsibilities and qualifications."
        context.write_text(json.dumps({"posting": {"text": text, "sha256": hashlib.sha256(text.encode()).hexdigest(), "target": {"company": "Synthetic fixture", "role": "Synthetic role", "id": "TEST-001", "url": "https://example.invalid/test-only"}, "activity_evidence": {"checked_at": datetime.now(timezone.utc).isoformat(), "http_status": 200, "application_form_present": True, "response_fields": {"test_only": "synthetic no-network fixture"}}}, "quality_context": {"hosted_authorized": True, "redaction_reviewed": True}}))
        environment = dict(os.environ)
        environment.pop("TYPESAFE_API_KEY", None)
        receipt = base / "quality.json"
        result = run(bundle / "skills/job-applier/tools/resume_quality.py", "posting", "--context", context, "--output", receipt, code=2, env=environment)
        assert result["status"] == "DEFER" and result["can_advance"] is False and json.loads(receipt.read_text())["receipts"][0]["provider_live"] is False
        before = sha(receipt)
        run(bundle / "skills/job-applier/tools/resume_quality.py", "posting", "--context", context, "--output", receipt, code=2, env=environment)
        assert sha(receipt) == before
        passed("missing provider key defers and existing receipt cannot be overwritten")
        spec = importlib.util.spec_from_file_location("portable_install_test", bundle / "install.py")
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        partial_home = base / "partial-home"
        partial_root = partial_home / ".aside/u/0/skills/user"
        for name in ("job-applier", "lucy-skills"):
            path = partial_root / name
            path.mkdir(parents=True)
            (path / "SKILL.md").write_text("Preexisting " + name)
        original = tree(partial_root)
        copytree = module.shutil.copytree
        def fail_copy(*args, **kwargs):
            raise OSError("Injected copy failure before second skill starts")
        module.shutil.copytree = fail_copy
        try:
            try:
                module.install(bundle, partial_home, True)
                raise AssertionError("Injected copy failure did not fire")
            except OSError:
                pass
        finally:
            module.shutil.copytree = copytree
        partial_receipt = next((partial_home / ".job-applier-installs").glob("*/receipt.json"))
        module.uninstall(partial_receipt, partial_home, False)
        assert tree(partial_root) == original
        passed("interrupted install restores first backup and preserves untouched later originals")
        recovery = module.install(bundle, partial_home, True)
        recovery_receipt = Path(recovery["receipt"])
        rename = Path.rename
        fired = []
        def fail_after_restore(path, target):
            result = rename(path, target)
            if path.parent.name == "backups" and not fired:
                fired.append(True)
                raise OSError("Injected crash after original restored, before receipt checkpoint")
            return result
        Path.rename = fail_after_restore
        try:
            try:
                module.uninstall(recovery_receipt, partial_home, False)
                raise AssertionError("Injected restore failure did not fire")
            except OSError:
                pass
        finally:
            Path.rename = rename
        assert fired
        module.uninstall(recovery_receipt, partial_home, False)
        assert tree(partial_root) == original
        passed("interrupted uninstall recognizes restored original and resumes remaining skills")
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps({"status": "PASS", "cases": results, "count": len(results), "recipient_machine_runtime": "NOT_TESTED", "live_provider_called": False}, indent=2) + "\n")
    print(json.dumps({"status": "PASS", "count": len(results), "evidence": str(args.output)}, indent=2))


if __name__ == "__main__":
    main()
