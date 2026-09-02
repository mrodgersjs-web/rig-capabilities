"""V22: whole-surface certification with plant-failure proof.

Doctrine (rig-adversarial-verification): a gate that can't go RED is theater.
`certify` runs deterministic, no-LLM gates over the repo and seals a report;
`self_test` proves each gate actually fires by breaking the thing it guards
inside a throwaway copy of the repo — plant, expect RED, restore, expect GREEN.
The live tree is never mutated.

Gates (all deterministic):
  suite           unittest suite exits 0
  index_fresh     scan() (id,kind) set equals .index.json's
  done_tests      quality_run: >=50 ran, pass_rate == 1.0
  idp_integrity   token issue→verify roundtrip ok; tampered token rejected
  acl_jake        policy grants jake "*", default stays "public"
  register        capability_register.csv validates; booked-KPI row weighted 5
  corpus_refusal  committed snapshot unclassified rate <= 0.10
  canary_detection  3/3 red-team decoys caught FABRICATED, distinct causes
  lease_exclusivity committed lease scenario replays; second acquire denied
  fable_dormant   rig-fable51 absent from every fixture fallback ladder
  stage_order     recorded IQRSQPI pass is in canonical seven-stage order
  evidence_ledger every fixture row clears rule 3 — no unverified résumé claim

The seven fable-2031 gates are hermetic (law L1): each delegates to the gate
function owned by its module, and every one of those resolves ONLY from files
under repo.root — committed fixtures in tests/fixtures/fable2031/ plus the
root capability_register.csv. Live state (~/.rig, ~/.hermes, ~/Downloads) is
audited by CLI verbs, never by a certify gate.
Law L3: no gate here runs the suite except `suite` itself; the seven new gates
each cost milliseconds so `self_test`'s per-gate copytree stays cheap.
"""
from __future__ import annotations

import json
import secrets
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


def _g_register(repo) -> tuple[bool, str]:
    from .register import gate_register
    return gate_register(repo)


def _g_corpus_refusal(repo) -> tuple[bool, str]:
    from .corpus import gate_corpus_refusal
    return gate_corpus_refusal(repo)


def _g_canary_detection(repo) -> tuple[bool, str]:
    from .dispatcher import gate_canary_detection
    return gate_canary_detection(repo)


def _g_lease_exclusivity(repo) -> tuple[bool, str]:
    from .lease import gate_lease_exclusivity
    return gate_lease_exclusivity(repo)


def _g_fable_dormant(repo) -> tuple[bool, str]:
    from .model_route import gate_fable_dormant
    return gate_fable_dormant(repo)


def _g_stage_order(repo) -> tuple[bool, str]:
    from .iqrsqpi_v10 import gate_stage_order
    return gate_stage_order(repo)


def _g_evidence_ledger(repo) -> tuple[bool, str]:
    from .evidence_ledger import gate_evidence_ledger
    return gate_evidence_ledger(repo)


GATES = {"suite": _g_suite, "index_fresh": _g_index_fresh,
         "done_tests": _g_done_tests, "idp_integrity": _g_idp,
         "acl_jake": _g_acl,
         "register": _g_register, "corpus_refusal": _g_corpus_refusal,
         "canary_detection": _g_canary_detection,
         "lease_exclusivity": _g_lease_exclusivity,
         "fable_dormant": _g_fable_dormant,
         "stage_order": _g_stage_order,
         "evidence_ledger": _g_evidence_ledger}


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
        # Plant must change the *payload*, never a string that may have moved.
        # V22 migrated semgrep's done_when from `grep:...:Semgrep` to two `file:`
        # checks, which silently turned the original replace-then-assert into a
        # no-op that left this gate green forever: a plant that cannot go RED is
        # theater. So inject an unsatisfiable check into whatever canonical asset
        # already carries the most done_when entries, and prove the payload moved.
        ip = tmp_root / ".index.json"
        doc = json.loads(ip.read_text())
        cands = [a for a in doc["assets"]
                 if a.get("source") == "canonical"
                 and (a.get("quality") or {}).get("done_when")]
        assert cands, "no canonical asset carries done_when — gate is vacuous"
        target = max(cands, key=lambda a: len(a["quality"]["done_when"]))
        q = target["quality"]
        before = list(q["done_when"])
        # The term must be random at plant time. A literal unsatisfiable-looking
        # token is satisfiable by `grep:` on this very file — that is the V22
        # self-reference bug, rediscovered here when a fixed `zz-plant-...` string
        # inside this branch made its own grep check pass.
        term = "zz-plant-" + secrets.token_hex(8)
        q["done_when"] = before + [f"grep:rig_capabilities/certify.py:{term}"]
        ip.write_text(json.dumps(doc))
        # Read back from disk: an in-memory mutation that never reaches the file
        # is the exact failure mode that made this gate theater for four versions.
        back = json.loads(ip.read_text())
        seen = any(term in str(e)
                   for a in back["assets"] if a.get("id") == target.get("id")
                   for e in (a.get("quality") or {}).get("done_when") or [])
        assert seen, "plant did not persist to the copied index"
        assert term not in (tmp_root / "rig_capabilities" / "certify.py"
                            ).read_text(), "plant term is self-satisfiable"
        return (f"unsatisfiable grep ({term}) injected into {target.get('id')} "
                f"(was {len(before)} checks)")
    if name == "idp_integrity":
        kp = tmp_root / ".signing.key"
        if kp.exists():
            kp.write_text("")
        return "signing key zeroed (issue must fail)"
    if name == "acl_jake":
        (tmp_root / "acl_policy.json").write_text(
            json.dumps({"agents": {"jake": ["public"], "default": ["public"]}}))
        return "jake demoted to public scope"
    if name == "register":
        p = tmp_root / "capability_register.csv"
        t = p.read_text()
        cell = '[""acl_policy.json"",""rig_capabilities/policy.py""]'
        assert t.count(cell) == 1
        p.write_text(t.replace(cell, "[]", 1))
        return "acl_policy_surface evidence_paths blanked"
    if name == "corpus_refusal":
        # 20-card snapshot: flipping two classified cards false lands the rate
        # at 3/20 = 0.15 > the 0.10 halt (the plan's pinned plant; 0.11 is not
        # representable on a 20-card denominator — exceeding the halt is the law)
        p = tmp_root / "tests" / "fixtures" / "fable2031" / "corpus-manifest.json"
        doc = json.loads(p.read_text())
        flipped = 0
        for card in doc["cards"]:
            if card.get("classified") and flipped < 2:
                card["classified"] = False
                flipped += 1
        assert flipped == 2
        p.write_text(json.dumps(doc))
        return "two classified cards flipped false (3/20 = 0.15 > 0.10 halt)"
    if name == "canary_detection":
        # decoy-2 replaced by an ALL-GREEN packet: still a registered decoy
        # (task id + style kept) so it enters the detector — and walks out
        # unflagged. 2/3 caught is a red gate, per card 8's kill criterion.
        d = tmp_root / "tests" / "fixtures" / "fable2031" / "redteam" / "decoy-2.json"
        h = tmp_root / "tests" / "fixtures" / "fable2031" / "handoff-honest.json"
        decoy = json.loads(d.read_text())
        green = json.loads(h.read_text())
        assert decoy.get("task_id") == "f31-redteam-decoy-2"
        green["task_id"] = decoy["task_id"]
        green["decoy_style"] = decoy.get("decoy_style") or "all_green_packet"
        d.write_text(json.dumps(green))
        return "decoy-2 replaced with an all-green packet (detector must miss)"
    if name == "lease_exclusivity":
        p = tmp_root / "tests" / "fixtures" / "fable2031" / "lease-scenario.json"
        doc = json.loads(p.read_text())
        op2 = next(o for o in doc["ops"] if str(o.get("i")) == "2")
        assert op2["expect"] == "denied" and op2["reason"] == "worktree_leased"
        op2["expect"] = "granted"
        p.write_text(json.dumps(doc))
        return "second acquire pinned to granted (exclusivity lie)"
    if name == "fable_dormant":
        p = tmp_root / "tests" / "fixtures" / "fable2031" / "routes" / "litellm.yaml"
        t = p.read_text()
        anchor = "        - rig-kimi\n  context_window_fallbacks:"
        assert t.count(anchor) == 1
        p.write_text(t.replace(
            anchor, "        - rig-kimi\n        - rig-fable51\n"
            "  context_window_fallbacks:", 1))
        return "rig-fable51 injected into the fallback ladder"
    if name == "stage_order":
        p = tmp_root / "tests" / "fixtures" / "fable2031" / "iqrsqpi-run.json"
        doc = json.loads(p.read_text())
        st = doc["stages"]
        st[1], st[2] = st[2], st[1]   # Question lands after Research: backtrack
        p.write_text(json.dumps(doc))
        return "stages 2 and 3 swapped (Research before Question)"
    if name == "evidence_ledger":
        p = (tmp_root / "tests" / "fixtures" / "fable2031"
             / "evidence-ledger-valid.csv")
        t = p.read_text()
        row = "docs/ROADMAP.md,planned,0.5,internal"
        assert t.count(row) == 1
        p.write_text(t.replace(row, "docs/ROADMAP.md,planned,0.5,resume", 1))
        return "planned E-104 promoted into the resume lane"
    raise KeyError(name)


def _restore(name: str, tmp_root: Path, backup: Path) -> None:
    shutil.rmtree(tmp_root, ignore_errors=True)
    shutil.copytree(backup, tmp_root, ignore=IGNORE)


def self_test(repo, only: list[str] | None = None) -> dict:
    """For every gate (or just `only`): green on copy → plant → RED → restore → GREEN.

    `only` is not a convenience. Omitting it means "every gate except `suite`",
    not "every gate": `suite` runs the whole unittest module inside a fresh
    copytree, and `self_test` already copytrees once per gate, so including it in
    a sweep costs a full suite run per gate and proves nothing the `suite` gate
    itself does not prove better, exactly once (law L3). Pass `only=["suite"]` to
    break it deliberately.
    """
    sweep = [k for k in GATES if (k in only if only else k != "suite")]
    rows = {}
    tmp = Path(tempfile.mkdtemp(prefix="certify-"))
    backup = tmp / "backup"
    work = tmp / "repo"
    try:
        shutil.copytree(repo.root, backup, ignore=IGNORE)
        for name in sweep:
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
