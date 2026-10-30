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
  idp_integrity   idp.guard_report: issue→verify roundtrip on a gate-owned root; 3 forgeries refused
  acl_jake        policy grants jake "*", default stays "public"
  register        capability_register.csv validates; booked-KPI row weighted 5
  corpus_refusal  committed snapshot unclassified rate <= 0.10
  canary_detection  3/3 red-team decoys caught FABRICATED, distinct causes
  lease_exclusivity committed lease scenario replays; second acquire denied
  fable_dormant   rig-fable51 absent from every fixture fallback ladder
  stage_order     recorded IQRSQPI pass is in canonical seven-stage order
  evidence_ledger every fixture row clears rule 3 — no unverified résumé claim

All twelve gates are hermetic (law L1): the seven fable-2031 ones delegate to the gate
function owned by their module, resolving ONLY from files under repo.root — committed
fixtures in tests/fixtures/fable2031/ plus the root capability_register.csv. Live state
(~/.rig, ~/.hermes, ~/Downloads) is audited by CLI verbs, never by a certify gate.
`idp_integrity` was the replay-breaking exception: it read a gitignored `.signing.key`,
so a `git archive` of a good commit went RED for a reason no commit could fix; it now
exercises the scheme on a root it creates itself (see `_g_idp`).
Law L3: no gate here runs the suite except `suite` itself; the seven new gates
each cost milliseconds so `self_test`'s per-gate copytree stays cheap.
"""
from __future__ import annotations

import base64
import json
import os
import secrets
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path

IGNORE = shutil.ignore_patterns(".git", ".venvs", ".apodex", "__pycache__",
                                ".venv", "node_modules")


def _copytree(src: Path, dst: Path) -> None:
    """Clone the repository for a plant without dereferencing its catalog links.

    The estate intentionally contains path-index symlinks, including dangling links for
    assets not installed on this workstation. Dereferencing them makes certification crash
    before a single gate runs. Preserve the link itself: gates must judge the same tree shape
    as the live repo, and a missing target remains missing without breaking the copy phase.
    """
    shutil.copytree(src, dst, ignore=IGNORE, symlinks=True)



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
    """Delegate to the owning module — see `idp.guard_report` for why the logic
    lives beside `verify_token` rather than here.

    Hermetic (law L1): the scheme is exercised on a root this gate creates and
    destroys, never on `repo.root/.signing.key`. That gitignored secret fused
    "the scheme verifies" with "this machine happens to hold a key", so a
    `git archive` replay of a good commit went RED with `issue failed: no signing
    key` (observed at 7b413c4, 10/11 green). Key provisioning is an operator
    action, so it is reported as detail and never judged.
    """
    from .catalog import Repo
    from .idp import guard_report, issue_token
    from .surface import generate_key, load_key
    saved = os.environ.pop("RIG_CAPABILITIES_SIGNING_KEY", None)
    try:
        with tempfile.TemporaryDirectory(prefix="idp-gate-") as tmp:
            root = Path(tmp)
            probe = Repo(root)
            generate_key(probe)
            if not load_key(probe):
                return False, "scheme cannot load a key it just generated"
            other = root / "other-tenant"
            other.mkdir()
            (other / ".signing.key").write_bytes(os.urandom(32).hex().encode())
            foreign = issue_token(Repo(other), "jake")
            if not foreign.get("ok"):
                return False, f"cross-check issue failed: {foreign.get('error')}"
            rep = guard_report(probe, foreign["token"])
            if not rep.get("ok"):
                return False, str(rep.get("detail"))
            live = "live key present" if load_key(repo) else \
                "live key absent (provisioning, not verdict)"
            return True, f"{rep['detail']} | {live}"
    finally:
        if saved is not None:
            os.environ["RIG_CAPABILITIES_SIGNING_KEY"] = saved


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


def _g_cell_shape(repo) -> tuple[bool, str]:
    """Lattice coordinates: SHAPE is enforced, JEV'S JUDGMENT is not (grill Q6=B).

    Reads the published index and validates any `cell` coordinate it finds, in
    `cell` or `okf.cell`, against the strict lattice id
    (L1-7, D1-3, A1-4, IQRSQPI step code). A made-up or malformed coordinate is
    deterministic and fails the build; whether a skill is *really* A3 vs A2 is a
    0.649-confidence model opinion and stays advisory, so an absent coordinate
    reports coverage instead of failing. An unparseable index fails closed.
    """
    import os
    import re as _re
    strict = _re.compile(r"^L[1-7]-D[1-3]-A[1-4]-(I1|Q1|R|S|Q2|P|I2)$")
    path = os.environ.get("RIG_CELL_SHAPE_INDEX") or None
    if path:
        with open(path) as fh:
            assets = json.load(fh).get("assets", [])
    else:
        assets = repo.load_index().get("assets", []) if isinstance(repo.load_index(), dict) else repo.load_index()["assets"]
    total = len(assets)
    keyed, bad = 0, []
    for a in assets:
        raw = a.get("cell") or (a.get("okf") or {}).get("cell")
        if not raw:
            continue
        keyed += 1
        if not strict.match(str(raw).strip()):
            bad.append(f"{a.get('id')}={raw!r}")
    detail = (f"{keyed}/{total} indexed assets carry a cell coordinate; "
              f"{len(bad)} malformed{': ' + ', '.join(bad[:5]) if bad else ''}")
    return (not bad), detail

GATES = {"suite": _g_suite, "index_fresh": _g_index_fresh,
         "done_tests": _g_done_tests, "idp_integrity": _g_idp,
         "acl_jake": _g_acl,
         "register": _g_register, "corpus_refusal": _g_corpus_refusal,
         "canary_detection": _g_canary_detection,
         "lease_exclusivity": _g_lease_exclusivity,
         "fable_dormant": _g_fable_dormant,
         "stage_order": _g_stage_order,
         "evidence_ledger": _g_evidence_ledger,
         "cell_shape": _g_cell_shape}


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
        # Blind the refusal inside the OWNING module, not here. A plant that
        # edited `certify.py` would never execute: `self_test` runs inside the
        # process that already holds this module in `sys.modules`, so the copy's
        # text change is invisible and the gate reads GREEN forever — a plant that
        # cannot go RED is the exact theater the done_tests plant documents. Only a
        # lazily-imported module can be planted. The needle is assembled from
        # fragments so this file never contains it verbatim.
        p = tmp_root / "rig_capabilities" / "idp.py"
        lines = p.read_text().splitlines(keepends=True)
        # Fragments: this file must never contain the line it hunts for, or the
        # assertion counts its own plant (the done_tests self-reference trap).
        hit = "".join(["compare", "_digest"])
        idxs = [i for i, ln in enumerate(lines)
                if ln.strip().startswith("if ") and hit in ln]
        assert len(idxs) == 1, f"signature check not uniquely located ({len(idxs)})"
        pad = lines[idxs[0]][:len(lines[idxs[0]]) - len(lines[idxs[0]].lstrip())]
        lines[idxs[0]] = pad + "if False:  # planted: accept any signature\n"
        p.write_text("".join(lines))
        return ("signature comparison removed from idp.verify_token "
                "(3 forgeries must still be refused)")
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
    _copytree(backup, tmp_root)


def _gate_probe(work: Path, name: str, pkg: Path) -> bool | None:
    """Run ONE gate against `work` in a fresh interpreter.

    `self_test` runs in the process that imported `rig_capabilities.certify`, so
    the first in-process probe caches every gate module it touches in
    `sys.modules`. After that, a plant that edits a `.py` file cannot execute:
    `after` re-reads the cached bytecode, the gate stays GREEN, and
    `red_when_planted` is False — the plant is theater, which is precisely the
    failure mode this file's done_tests plant warns about. A subprocess is the
    only honest way to ask "what would a new process compute from these files?".

    Returns None when the probe cannot run, so the caller can fall back rather
    than report a phantom RED.
    """
    code = (
        "import json,sys;"
        "sys.path.insert(0, sys.argv[1]);"
        "from rig_capabilities.catalog import Repo;"
        "from rig_capabilities.certify import run_gates;"
        "r = run_gates(Repo(sys.argv[2]), only=[sys.argv[3]]);"
        "print(json.dumps(r[sys.argv[3]]['ok']))"
    )
    try:
        p = subprocess.run([sys.executable, "-c", code, str(pkg), str(work), name],
                           capture_output=True, text=True, timeout=600,
                           cwd=str(work))
    except subprocess.TimeoutExpired:
        return None
    out = (p.stdout or "").strip().splitlines()
    if not out:
        return None
    try:
        return bool(json.loads(out[-1]))
    except json.JSONDecodeError:
        return None


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
        _copytree(repo.root, backup)
        for name in sweep:
            shutil.rmtree(work, ignore_errors=True)
            _copytree(backup, work)
            from .catalog import Repo
            r1 = Repo(work)
            before = run_gates(r1, only=[name])[name]["ok"]
            note = _plant(name, work)
            # The plant may only bite in a process that has not already cached the
            # module it edits, so the planted state is measured in a subprocess.
            # before/restored stay in-process: they read the same files either way.
            after = _gate_probe(work, name, work)
            if after is None:
                note += " | probe could not run; plant unproven"
                after = True
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
