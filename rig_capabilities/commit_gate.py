"""Commit gate v2: four receipts; every load-bearing number is RECOMPUTED or
re-run through a PINNED canonical authority. A receipt is a pointer plus
expectations — never evidence.

  d85      -> the certifier path is pinned code (receipts cannot choose it);
              `verify-cert BUILD CERT` must exit 0 AND the build record must
              carry commit_sha == the commit under review; build/cert must
              resolve inside the repo
  joint    -> trial ledger rows are re-read and the one-sided Wilson lower
              bound recomputed via measure.wilson_lb; rows must carry a
              record-time bind.commit_sha == this commit; stated numbers in
              any receipt are never consulted
  gate-d   -> delegated to rig-determinism-85 gate-d (HMAC-signed,
              action-hash-bound, expiry-bounded, consume-once ledger); the
              exact action must bind the commit sha; the mutable rig-loop
              run.json mirror is never consulted
  verdict  -> digest-bound artifact inside repo-trusted roots, decision=pass,
              verifier family != builder family; residual trust is stated
              honestly below

RESIDUAL TRUST (honest, not fixed by this module): on a single machine, an
attacker who can write repo files can also plant a fake certifier at the
pinned path and fake trial rows. What this gate defeats: receipt-level
substitution, stale/mismatched approvals, same-family self-certification,
cross-commit evidence laundering, and stated-number lies. Defeating the rest
requires an out-of-band verifier (cross-machine signature or human).

Missing artifact / unavailable authority / escape attempt = refusal.

Usage: python3 rig_capabilities/commit_gate.py selftest
"""
from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from pathlib import Path

if __package__ in (None, ""):  # direct script invocation: the repo root
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from rig_capabilities.measure import wilson_lb

# Pinned authorities — resolved relative to the repo argument, never supplied
# by receipt input (a receipt-chosen binary is the bypass, proven in s6).
D85_BIN = "capabilities/skills/rig-determinism-85/bin/rig-determinism-85"
JOINT_FLOOR = 0.95
TRIAL_MIN = 72          # >=73/72 clears the floor; the floor is real
VERDICT_DIR = "proof/verdicts"  # repo dir verdict artifacts must live under
ANCHOR_FILE = ".rig/d85/certifier.digest"  # out-of-tree, human-sealed


class GateRefused(ValueError):
    pass

def _inside(repo: Path, rel: str) -> Path | None:
    """Resolve `rel` and require it stays inside repo. Absolute paths, ..
    escapes, and symlinked-out paths all return None."""
    if not rel or Path(rel).is_absolute():
        return None
    p = (repo / rel).resolve()
    try:
        p.relative_to(repo.resolve())
    except ValueError:
        return None
    return p


def certifier_digest(exe: Path) -> str:
    """Canonical digest of the certifier authority: its own bytes plus every
    *.py it executes as a library, path-sorted (a modified d85_gates.py is
    as dangerous as a modified launcher)."""
    h = hashlib.sha256()
    files = [exe] + sorted(exe.parent.parent.glob("*.py"))
    for f in files:
        h.update(f.name.encode())
        h.update(f.read_bytes())
    return h.hexdigest()

def _anchor_errors(repo: Path, anchor: str | None) -> list[str]:
    """The certifier must match a digest pinned OUTSIDE the candidate tree.
    The candidate commit can rewrite the in-repo certifier (self-certification);
    it does not get to rewrite ~/.rig. The anchor is human-sealed: bumping it
    is a deliberate, separately approved act, and this module NEVER writes it."""
    exe = _inside(repo, D85_BIN)
    if exe is None or not exe.exists():
        return [f"d85: pinned certifier missing at {D85_BIN}"]
    if anchor is None:
        f = Path.home() / ANCHOR_FILE
        try:
            anchor = f.read_text().strip()
        except OSError:
            return [f"authority: certifier anchor {f} missing — fail closed; "
                    "a human must seal it (see pin-certifier) before any "
                    "certified claim"]
    if anchor != certifier_digest(exe):
        return ["authority: certifier bytes do not match the out-of-tree "
                "anchor — the certifier was modified against its sealed "
                "version; refusing to execute it"]
    return []

def _verify_d85(repo: Path, r: dict, sha: str, *,
                anchor: str | None = None) -> list[str]:
    errs = _anchor_errors(repo, anchor)
    if errs:
        return errs
    exe = _inside(repo, D85_BIN)
    build, cert = _inside(repo, r.get("build", "")), _inside(repo, r.get("cert", ""))
    if build is None or cert is None:
        return ["d85: build/cert path escapes the repo"]
    if not build.exists() or not cert.exists():
        return [f"d85: build/cert artifact missing ({build.name}/{cert.name})"]
    try:
        record = json.loads(build.read_text())
    except (json.JSONDecodeError, OSError) as e:
        return [f"d85: build record unreadable: {e}"]
    if record.get("commit_sha") != sha:
        return [f"d85: certified build is for "
                f"{str(record.get('commit_sha'))[:12]!r}, not {sha[:12]}"]
    try:
        p = subprocess.run([sys.executable, str(exe), "verify-cert",
                            str(build), str(cert)],
                           capture_output=True, text=True, timeout=120)
    except (OSError, subprocess.TimeoutExpired) as e:
        return [f"d85: certifier could not run: {e}"]
    if p.returncode != 0:
        return [f"d85: verify-cert exit {p.returncode}: {p.stdout[-200:]}"]
    return []


def verify_joint(repo: Path, r: dict, sha: str) -> list[str]:
    """Recompute the Wilson LB from rows bound AT RECORD TIME to this
    commit; rows bound elsewhere (or unbound) never count."""
    art = _inside(repo, r.get("trials", ""))
    if art is None or not art.exists():
        return [f"joint: trial ledger missing or escaping ({r.get('trials')!r})"]
    want_cells = set(r.get("cells", []))
    ok = n = unbound = 0
    try:
        for line in art.read_text().splitlines():
            if not line.strip():
                continue
            row = json.loads(line)
            if row.get("cell") not in want_cells:
                continue
            if (row.get("bind") or {}).get("commit_sha") != sha:
                unbound += 1
                continue
            n += 1
            ok += row.get("outcome") == "success"
    except (json.JSONDecodeError, OSError) as e:
        return [f"joint: ledger unreadable: {e}"]
    if n < r.get("min_trials", TRIAL_MIN):
        return [f"joint: only {n} rows bound to {sha[:12]} "
                f"(+{unbound} bound elsewhere/unbound) for those cells"]
    lb = wilson_lb(ok, n, 0.05)
    if lb < JOINT_FLOOR:
        return [f"joint: recomputed lower_bound {lb} < {JOINT_FLOOR} "
                f"({ok}/{n}) — receipt stated value ignored"]
    return []

def _load_authority(repo: Path):
    """Load the canonical gate modules by FILE SPEC from the pinned skill
    root (bin/ holds only the CLI wrapper). sys.modules reuse only when the
    cached module's __file__ IS this root's file — a pre-imported lookalike
    or another repo's copy never masks the pinned authority."""
    import importlib.util
    root = _inside(repo, D85_BIN).parent.parent

    def load(name):
        want = (root / f"{name}.py").resolve()
        cached = sys.modules.get(name)
        if cached is not None and Path(getattr(cached, "__file__", "")).resolve() == want:
            return cached
        if not want.exists():
            raise GateRefused(f"authority {name}.py missing at {root}")
        spec = importlib.util.spec_from_file_location(name, str(want))
        mod = importlib.util.module_from_spec(spec)
        sys.modules[name] = mod          # d85_gates does `from d85 import ...`
        try:
            spec.loader.exec_module(mod)
        except Exception as e:
            sys.modules.pop(name, None)
            raise GateRefused(f"authority {name} failed to load: {e}")
        return mod

    d85 = load("d85")
    d85_gates = load("d85_gates")
    return d85, d85_gates


def _verify_gate_d(repo: Path, r: dict, sha: str, *,
                   gate_root: Path | None = None, proof_fn=None,
                   anchor: str | None = None) -> list[str]:
    """NON-CONSUMING readiness read of the canonical Gate-D ledger
    (HMAC-signed, proof-bound, action-hash-bound, expiry-bounded,
    consume-once). Calling gate_d() here would CONSUME the approval, so we
    replay its verification steps read-only. Arm (`arm_gate_d`) is a
    separate call made exactly once at the authorized effect; its ARMED
    verdict is the execution receipt. Mirrors d85_gates.gate_d() without
    the marker write."""
    aerr = _anchor_errors(repo, anchor)
    if aerr:
        return aerr  # never import/exec authority from an unanchored tree
    try:
        d85, d85_gates = _load_authority(repo)
    except (ImportError, GateRefused) as e:
        return [f"gate-d: canonical authority unavailable: {e}"]
    pid = r.get("process_id")
    action_file = _inside(repo, r.get("action_file", ""))
    if not pid or action_file is None or not action_file.exists():
        return ["gate-d: receipt must carry process_id and an in-repo action_file"]
    try:
        action = json.loads(action_file.read_text())
    except (json.JSONDecodeError, OSError) as e:
        return [f"gate-d: action file unreadable: {e}"]
    if not isinstance(action, dict) or action.get("commit_sha") != sha:
        return [f"gate-d: action file does not bind commit {sha[:12]}"]
    registry = ((repo / D85_BIN).parent.parent
                / "authority" / "registry.json")
    root = gate_root or (registry.resolve(strict=False).parent / "gate_d")
    import time as _t
    import hmac as _h
    import hashlib as _hl
    try:
        proof = (proof_fn or
                 (lambda: d85_gates.score_realized(registry, pid)))()
        key = d85_gates._load_key(Path(root))
        lines = (Path(root) / "approvals.jsonl").read_text().splitlines()
    except Exception as e:  # _block raises AdmissionBlock; reads may fail
        return [f"gate-d: ledger unread: {e}"]
    action_sha256 = d85._canonical_hash(action)
    realized = d85._canonical_hash(proof)
    now = int(_t.time())
    for i, line in enumerate(lines):
        if not line.strip():
            continue
        try:
            rec = json.loads(line)
        except json.JSONDecodeError:
            return [f"gate-d: approvals.jsonl line {i} corrupt"]
        sig = _h.new(key, d85._canonical_hash(
            {k: v for k, v in rec.items() if k != "signature"}).encode(),
            _hl.sha256).hexdigest()
        if not _h.compare_digest(rec.get("signature", ""), sig):
            return [f"gate-d: approvals.jsonl line {i}: bad signature"]
        if rec.get("process_id") != pid:
            continue
        if (rec.get("inventory_sha256") != proof["inventory_sha256"]
                or rec.get("classification_sha256")
                != proof["classification_sha256"]
                or rec.get("realized_sha256") != realized):
            return [f"gate-d: line {i} bound to a different proof"]
        if rec.get("action_sha256") != action_sha256:
            continue
        life = rec.get("expires_at", 0) - rec.get("issued_at", 0)
        if life <= 0 or life > d85_gates.GATE_D_MAX_LIFETIME_SECONDS:
            return [f"gate-d: line {i}: bad lifetime"]
        if now > rec.get("expires_at", 0):
            return [f"gate-d: matching approval expired (line {i})"]
        # EXACT mirror of d85_gates.py line 570 (verified on disk):
        #   f"{record['run_id'][7:23]}.{action_sha256[7:23]}"
        marker = (Path(root) / "consumed"
                  / f"{rec['run_id'][7:23]}.{action_sha256[7:23]}")
        if marker.exists():
            return [f"gate-d: approval already consumed ({marker.name}); "
                    "arm a fresh Gate-D at the effect, do not re-check"]
        return []  # live, signed, bound, unconsumed
    return [f"gate-d: no approval binds action {action_sha256[:12]}"]


def _arm_gate_d(repo: Path, r: dict, sha: str, *,
                anchor: str | None = None) -> dict:
    """THE effect-time call, once; returns the authority's ARMED verdict
    (consume marker inside). Callers must retain it as the execution
    receipt. NOT used by check(); never call it for readiness."""
    errs = _anchor_errors(repo, anchor)
    if errs:
        raise GateRefused("; ".join(errs))
    exe = _inside(repo, D85_BIN)
    af = _inside(repo, r.get("action_file", ""))
    if af is None or not af.exists():
        raise GateRefused("gate-d arm: action file missing or escapes repo")
    try:
        act = json.loads(af.read_text())
    except (json.JSONDecodeError, OSError) as e:
        raise GateRefused(f"gate-d arm: action file unreadable: {e}")
    if act.get("commit_sha") != sha:
        raise GateRefused("gate-d arm: action file does not bind this commit")
    p = subprocess.run([sys.executable, str(exe), "gate-d",
                        r["process_id"], "--action", str(af)],
                       capture_output=True, text=True, timeout=120)
    if p.returncode != 0:
        raise GateRefused(f"gate-d arm refused: {(p.stdout or p.stderr)[-240:]}")
    return json.loads(p.stdout)


def verify_verdict(repo: Path, r: dict, sha: str) -> list[str]:
    art = _inside(repo, r.get("artifact", ""))
    if art is None:
        return ["verdict: artifact path escapes the repo"]
    try:
        art.relative_to((repo / VERDICT_DIR).resolve())
    except ValueError:
        return [f"verdict: artifact outside trusted dir {VERDICT_DIR}"]
    if not art.exists():
        return [f"verdict: artifact missing ({art})"]
    try:
        v = json.loads(art.read_text())
    except (json.JSONDecodeError, OSError) as e:
        return [f"verdict: artifact unreadable: {e}"]
    errs = []
    if v.get("commit_sha") != sha:
        errs.append(f"verdict: bound to {str(v.get('commit_sha'))[:12]!r}, "
                    f"not {sha[:12]} (digest binding broken)")
    if v.get("decision") != "pass":
        errs.append(f"verdict: decision {v.get('decision')!r} != pass")
    if v.get("verifier_family") == v.get("builder_family"):
        errs.append("verdict: same-family (builder self-certification)")
    if not v.get("verifier_family"):
        errs.append("verdict: verifier family missing")
    return errs

# -- gate -------------------------------------------------------------------
def _check(repo: Path, sha: str, manifest: dict, *, anchor: str | None = None,
           gate_root: Path | None = None, proof_fn=None) -> dict:
    """TEST-ONLY core with injection seams. Production callers MUST use
    check(), which carries no seam parameters at all."""
    # ANCHOR PREFLIGHT: if the pinned certifier authority in this candidate
    # tree does not match the out-of-tree digest, NOTHING from that tree may
    # be executed or imported — including the gate-d authority modules.
    # Return before any authority import/subprocess.
    aerr = _anchor_errors(repo, anchor)
    if aerr:
        return {"commit": sha[:12], "admitted": False, "refusals": aerr}
    errs: list[str] = []
    for kind in ("d85", "joint", "gate-d", "verdict"):
        if kind not in manifest:
            errs.append(f"{kind}: missing receipt (UNKNOWN blocks)")
    if "d85" in manifest:
        errs += _verify_d85(repo, manifest["d85"], sha, anchor=anchor)
    if "joint" in manifest:
        errs += verify_joint(repo, manifest["joint"], sha)
    if "gate-d" in manifest:
        errs += _verify_gate_d(repo, manifest["gate-d"], sha,
                               gate_root=gate_root, proof_fn=proof_fn,
                               anchor=anchor)
    if "verdict" in manifest:
        errs += verify_verdict(repo, manifest["verdict"], sha)
    return {"commit": sha[:12], "admitted": not errs, "refusals": errs}


def check(repo: Path, sha: str, manifest: dict) -> dict:
    """NON-CONSUMING readiness. NO seam parameters: the anchor is read from
    the out-of-tree file, the gate root from the pinned registry, the proof
    from the live scorer. Arming is a separate effect-time call."""
    return _check(repo, sha, manifest)


def arm_gate_d(repo: Path, r: dict, sha: str) -> dict:
    """Production arming: no seams (anchor read from the out-of-tree file)."""
    return _arm_gate_d(repo, r, sha)


def check_or_raise(repo: Path, sha: str, manifest: dict) -> dict:
    v = check(repo, sha, manifest)
    if not v["admitted"]:
        raise GateRefused("; ".join(v["refusals"]))
    return v


# -- selftest ---------------------------------------------------------------
def selftest(argv=None) -> int:
    import hmac as _h
    import hashlib as _hl
    import tempfile
    import time
    import types
    errs = []
    SHA = "c" * 40
    with tempfile.TemporaryDirectory() as td:
        repo = Path(td)
        skill = repo / Path(D85_BIN).parent.parent
        (skill / "bin").mkdir(parents=True)
        exe = skill / "bin" / "rig-determinism-85"
        exe.write_text("#!/usr/bin/env python3\nimport sys\n"
                       "sys.exit(0 if sys.argv[1:2] == ['verify-cert'] else 1)\n")
        # sandbox authority modules: minimal, self-consistent stand-ins whose
        # hashing matches what verify_gate_d replays (same modules both sides).
        (skill / "d85.py").write_text(
            "import hashlib, json\n"
            "def _canonical_hash(v):\n"
            "    return hashlib.sha256(json.dumps(v, sort_keys=True, "
            "separators=(',',':')).encode()).hexdigest()\n")
        (skill / "d85_gates.py").write_text(
            "GATE_D_MAX_LIFETIME_SECONDS = 86400\n"
            "def score_realized(reg, pid):\n"
            "    raise RuntimeError('sandbox: pass proof_fn')\n"
            "def _load_key(root):\n"
            "    import pathlib\n"
            "    return pathlib.Path(root, 'key').read_bytes().strip()\n")
        anchor = certifier_digest(exe)

        # ---- gate-d: mint a signed, bound, live approval (test seam gate)
        gate_root = repo / "gate_d"
        gate_root.mkdir()
        (gate_root / "key").write_bytes(b"ab" * 32)
        (gate_root / "consumed").mkdir()
        action = {"verb": "ship", "commit_sha": SHA}
        af = repo / "actions/ship.json"
        af.parent.mkdir()
        af.write_text(json.dumps(action, sort_keys=True))
        proof = {"inventory_sha256": "i", "classification_sha256": "c"}
        # local canonical hash mirroring the sandbox stub — NO pre-import of
        # 'd85': _load_authority must genuinely load the pinned files itself.
        def CH(v):
            return _hl.sha256(json.dumps(v, sort_keys=True,
                                         separators=(",", ":")).encode()).hexdigest()
        sd85 = types.SimpleNamespace(_canonical_hash=CH)
        rec = {"schema": "x", "run_id": "sha256:" + "r" * 40,
               "process_id": "P1",
               "inventory_sha256": proof["inventory_sha256"],
               "classification_sha256": proof["classification_sha256"],
               "realized_sha256": sd85._canonical_hash(proof),
               "action_sha256": sd85._canonical_hash(action),
               "approver": "mike", "issued_at": int(time.time()),
               "expires_at": int(time.time()) + 3600}
        sig = _h.new(b"ab" * 32,
                     sd85._canonical_hash(rec).encode(), _hl.sha256).hexdigest()
        (gate_root / "approvals.jsonl").write_text(
            json.dumps({**rec, "signature": sig}, sort_keys=True) + "\n")
        seam = dict(anchor=anchor, gate_root=gate_root,
                    proof_fn=lambda: proof)

        ledger = repo / "trials.jsonl"

        def write_ledger(failures: int, bound_to: str = SHA) -> None:
            rows = [json.dumps({"trial_id": f"t{i:03d}", "cell": "C001",
                                "attempt_seq": 1,
                                "outcome": "failure" if i < failures else "success",
                                "bind": {"commit_sha": bound_to}})
                    for i in range(72)]
            ledger.write_text("\n".join(rows) + "\n")

        write_ledger(0)
        (repo / "proof/verdicts").mkdir(parents=True)
        (repo / "proof/verdicts/v.json").write_text(json.dumps(
            {"commit_sha": SHA, "decision": "pass",
             "builder_family": "claude", "verifier_family": "kimi"}))
        (repo / "build.json").write_text(json.dumps({"commit_sha": SHA}))
        (repo / "cert.json").write_text("{}")
        manifest = {
            "d85": {"build": "build.json", "cert": "cert.json"},
            "joint": {"trials": "trials.jsonl", "cells": ["C001"]},
            "gate-d": {"process_id": "P1", "action_file": "actions/ship.json"},
            "verdict": {"artifact": "proof/verdicts/v.json"},
        }
        v0 = _check(repo, SHA, manifest, **seam)
        if not v0["admitted"]:
            errs.append(f"valid manifest refused: {v0['refusals']}")
        # non-consuming: readiness twice must stay admitted
        v1 = _check(repo, SHA, manifest, **seam)
        if not v1["admitted"]:
            errs.append("readiness consumed the approval")

        def expect(name, mutate, frag, *, pre=None, post=None):
            m = json.loads(json.dumps(manifest))
            if mutate:
                mutate(m)
            if pre:
                pre()
            v = _check(repo, SHA, m, **seam)
            if post:
                post()
            if v["admitted"]:
                errs.append(f"{name}: accepted")
            elif not any(frag in r for r in v["refusals"]):
                errs.append(f"{name}: wrong refusal {v['refusals']}")

        expect("tampered ledger (71/72)", None, "recomputed lower_bound",
               pre=lambda: write_ledger(1), post=lambda: write_ledger(0))
        expect("cross-commit evidence laundering", None, "bound to",
               pre=lambda: write_ledger(0, bound_to="d" * 40),
               post=lambda: write_ledger(0))
        expect("missing receipts", lambda m: m.clear(), "missing receipt")
        # anchor mismatch exercised directly (anchor is a kwarg seam)
        if not _verify_d85(repo, manifest["d85"], SHA, anchor="0" * 64):
            errs.append("anchor mismatch admitted")
        # preflight must SHORT-CIRCUIT: one refusal, nothing else ran
        v = _check(repo, SHA, manifest, **dict(seam, anchor="0" * 64))
        if len(v["refusals"]) != 1 or "match" not in v["refusals"][0]:
            errs.append(f"anchor mismatch not short-circuited: {v['refusals']}")
        marker = gate_root / "consumed" / (
            rec["run_id"][7:23] + "." +
            sd85._canonical_hash(action)[7:23])
        marker.parent.mkdir(exist_ok=True)
        marker.write_text("{}")
        v = _check(repo, SHA, manifest, **seam)
        if v["admitted"] or not any("consumed" in r for r in v["refusals"]):
            errs.append(f"consumed approval admitted: {v['refusals']}")
        marker.unlink()
        # a certified build for ANOTHER commit must not pass
        (repo / "other-build.json").write_text(json.dumps(
            {"commit_sha": "d" * 40}))
        v = _check(repo, SHA, {**manifest, "d85": {
            "build": "other-build.json", "cert": "cert.json"}}, **seam)
        if v["admitted"] or not any("not" in r for r in v["refusals"]):
            errs.append("cross-commit certified build admitted")
        expect("build path escape",
               lambda m: m["d85"].update(build="../../etc/passwd"), "escapes")
        # a receipt-supplied binary key is inert: pinned path still used
        v = _check(repo, SHA, {**manifest, "d85": {
            "build": "build.json", "cert": "cert.json",
            "d85_bin": "/bin/echo"}}, **seam)
        if not v["admitted"]:
            errs.append(f"inert receipt key broke admission: {v['refusals']}")
        # same-family verdict
        (repo / "proof/verdicts/f.json").write_text(json.dumps(
            {"commit_sha": SHA, "decision": "pass", "builder_family": "claude",
             "verifier_family": "claude"}))
        v = _check(repo, SHA, {**manifest, "verdict": {
            "artifact": "proof/verdicts/f.json"}}, **seam)
        if v["admitted"] or not any("same-family" in r for r in v["refusals"]):
            errs.append("same-family verdict admitted")
        expect("verdict outside trusted dir",
               lambda m: m["verdict"].update(artifact="v.json"), "trusted dir")
        expect("gate-d action unbound",
               lambda m: m["gate-d"].update(
                   action_file="actions/plain.json"), "does not bind",
               pre=lambda: (repo / "actions/plain.json").write_text(
                   '{"verb": "ship"}'))
        try:
            check_or_raise(repo, SHA, {})
            errs.append("check_or_raise admitted empty")
        except GateRefused:
            pass
    # the exact advisory lesson, frozen: public entrypoints carry NO seams
    import inspect as _insp
    for fn in (check, arm_gate_d, check_or_raise):
        s = str(_insp.signature(fn))
        if any(w in s for w in ("anchor", "gate_root", "proof_fn")):
            errs.append(f"public seam leak in {fn.__name__}: {s}")
    print(json.dumps({"ok": not errs, "errors": errs}))
    return 0 if not errs else 1


if __name__ == "__main__":
    _a = sys.argv[1:]
    if _a and _a[0] not in ("selftest", "--help"):
        print("usage: commit_gate.py [selftest|--help]", file=sys.stderr)
        sys.exit(2)
    sys.exit(selftest())
