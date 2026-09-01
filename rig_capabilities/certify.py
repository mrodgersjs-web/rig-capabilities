"""V22: whole-surface certification with plant-failure proof.

Doctrine (rig-adversarial-verification): a gate that can't go RED is theater.
`certify` runs deterministic, no-LLM gates over the repo and seals a report;
`self_test` proves each gate actually fires by breaking the thing it guards
inside a throwaway copy of the repo — plant, expect RED, restore, expect GREEN.
The live tree is never mutated.

Gates (all deterministic):
  suite          unittest suite exits 0
  index_fresh    scan() (id,kind) set equals .index.json's
  done_tests     quality_run: >=50 ran, pass_rate == 1.0
  idp_integrity  token issue→verify roundtrip ok; tampered token rejected
  acl_jake       policy grants jake "*", default stays "public"
"""
from __future__ import annotations

import json
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path

IGNORE = shutil.ignore_patterns(".git", ".venvs", ".apodex", "__pycache__",
                                ".venv", "node_modules")


def _g_suite(repo) -> tuple[bool, str]:
    r = subprocess.run([sys.executable, "-m", "unittest", "tests.test_catalog"],
                       cwd=str(repo.root), capture_output=True, timeout=300,
                       text=True)
    return r.returncode == 0, (r.stderr or "")[-160:]


def _g_index_fresh(repo) -> tuple[bool, str]:
    live = {(a["id"], a.get("kind")) for a in repo.load_index()["assets"]}
    scanned = {(a["id"], a.get("kind")) for a in repo.scan()}
    missing = scanned - live
    stale = live - scanned
    return (not missing and not stale), f"missing={len(missing)} stale={len(stale)}"


def _g_done_tests(repo) -> tuple[bool, str]:
    from .done_tests import quality_run
    rep = quality_run(repo)
    return (rep["ran"] >= 50 and rep["pass_rate"] == 1.0), \
        f"ran={rep['ran']} rate={rep['pass_rate']} fails={rep['failures'][:3]}"


def _g_idp(repo) -> tuple[bool, str]:
    from .idp import issue_token, verify_token
    iss = issue_token(repo, "jake")
    if not iss.get("ok"):
        return False, f"issue failed: {iss.get('error')}"
    tok = iss["token"]
    if not verify_token(repo, tok)["ok"]:
        return False, "roundtrip rejected"
    parts = tok.split(".")
    tampered = f"{parts[0]}.{parts[1]}.{int(parts[2]) + 10}.{parts[3]}"
    if verify_token(repo, tampered)["ok"]:
        return False, "tampered token ACCEPTED"
    return True, "roundtrip ok, tamper rejected"


def _g_acl(repo) -> tuple[bool, str]:
    from .policy import load_policy
    agents = load_policy(repo).get("agents") or {}
    ok = agents.get("jake") == ["*"] and agents.get("default") == ["public"]
    return ok, json.dumps(agents)


GATES = {"suite": _g_suite, "index_fresh": _g_index_fresh,
         "done_tests": _g_done_tests, "idp_integrity": _g_idp,
         "acl_jake": _g_acl}


def run_gates(repo, only: list | None = None) -> dict:
    out = {}
    for name, fn in GATES.items():
        if only and name not in only:
            continue
        try:
            ok, detail = fn(repo)
        except Exception as e:  # noqa: BLE001 — a crash IS a red gate
            ok, detail = False, f"{type(e).__name__}: {e}"
        out[name] = {"ok": bool(ok), "detail": detail}
    return out


def certify(repo) -> dict:
    res = run_gates(repo)
    rep = {"ts": time.strftime("%Y-%m-%dT%H:%M:%S"), "gates": res,
           "verdict": all(g["ok"] for g in res.values())}
    out = Path(repo.root) / ".context" / "certify"
    out.mkdir(parents=True, exist_ok=True)
    (out / f"{rep['ts'].replace(':', '')}.json").write_text(
        json.dumps(rep, indent=1))
    return rep


# ---------------------------------------------------------------- plant tests

def _plant(name: str, tmp_root: Path) -> str:
    """Break exactly what the gate guards, inside the copy."""
    if name == "suite":
        p = tmp_root / "tests" / "test_catalog.py"
        t = p.read_text()
        assert 'self.assertEqual(0, rep["count"])' in t
        p.write_text(t.replace('self.assertEqual(0, rep["count"])',
                               'self.assertEqual(0.5, rep["count"])', 1))
        return "existing assertion broken"
    if name == "index_fresh":
        d = tmp_root / "capabilities" / "skills" / "zz-planted-skill"
        d.mkdir(parents=True, exist_ok=True)
        (d / "SKILL.md").write_text("---\nname: zz-planted-skill\n"
                                    "description: planted drift\n---\n# p\n")
        return "new asset absent from index"
    if name == "done_tests":
        # bad spec: index says grep a term the file never contained. Editing the
        # file itself would be self-referential (frontmatter carries done_when).
        ip = tmp_root / ".index.json"
        doc = json.loads(ip.read_text())
        hit = False
        for a in doc["assets"]:
            if a.get("id") == "semgrep" and a.get("source") == "canonical":
                dw = (a.get("quality") or {}).get("done_when") or []
                a["quality"]["done_when"] = [
                    e.replace("SKILL.md:Semgrep", "SKILL.md:zz-no-such-term")
                    for e in dw]
                hit = True
        assert hit
        ip.write_text(json.dumps(doc))
        return "done_when term that does not exist in the file"
    if name == "idp_integrity":
        kp = tmp_root / ".signing.key"
        if kp.exists():
            kp.write_text("")
        return "signing key zeroed (issue must fail)"
    if name == "acl_jake":
        (tmp_root / "acl_policy.json").write_text(
            json.dumps({"agents": {"jake": ["public"], "default": ["public"]}}))
        return "jake demoted to public scope"
    raise KeyError(name)


def _restore(name: str, tmp_root: Path, backup: Path) -> None:
    shutil.rmtree(tmp_root, ignore_errors=True)
    shutil.copytree(backup, tmp_root, ignore=IGNORE)


def self_test(repo) -> dict:
    """For every gate: green on copy → plant → RED → restore → GREEN."""
    rows = {}
    tmp = Path(tempfile.mkdtemp(prefix="certify-"))
    backup = tmp / "backup"
    work = tmp / "repo"
    try:
        shutil.copytree(repo.root, backup, ignore=IGNORE)
        for name in GATES:
            shutil.rmtree(work, ignore_errors=True)
            shutil.copytree(backup, work, ignore=IGNORE)
            from .catalog import Repo
            r1 = Repo(work)
            before = run_gates(r1, only=[name])[name]["ok"]
            note = _plant(name, work)
            # fresh Repo: gates must see post-plant state, like a new process
            after = run_gates(Repo(work), only=[name])[name]["ok"]
            _restore(name, work, backup)
            r2 = Repo(work)
            restored = run_gates(r2, only=[name])[name]["ok"]
            rows[name] = {"green": before, "red_when_planted": (not after),
                          "green_after_restore": restored, "plant": note,
                          "ok": before and (not after) and restored}
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    rep = {"gates": rows,
           "verdict": all(r["ok"] for r in rows.values())}
    out = Path(repo.root) / ".context" / "certify"
    out.mkdir(parents=True, exist_ok=True)
    (out / f"{time.strftime('%Y-%m-%dT%H%M%S')}-plantfail.json").write_text(
        json.dumps(rep, indent=1))
    return rep
