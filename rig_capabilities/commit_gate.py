"""Commit gate v2: four receipts; every load-bearing number is RECOMPUTED or
re-run through a PINNED canonical authority. A receipt is a pointer plus
expectations — never evidence.

  d85      -> the certifier path is pinned code (receipts cannot choose it);
              `verify-cert BUILD CERT` must exit 0 AND the build record must
              carry commit_sha == the commit under review; build/cert must
              resolve inside the repo
  joint    -> trial ledger rows re-read with the canonical attempt-key
              semantics of measure.Recorder ((cell,trial_id,attempt_seq)
              dedup; one trial = one trial_id, highest bound attempt wins);
              durable arm (bind.kind=="durable") must number >= DURABLE_MIN
              and sit >= 24h apart; Wilson LB recomputed PER ARM and the
              joint floor uses min(lb_durable, lb_repeatable); rows must
              carry a record-time bind.commit_sha == this commit; stated
              numbers in any receipt are never consulted
  gate-d   -> delegated to rig-determinism-85 gate-d (HMAC-signed,
              action-hash-bound, expiry-bounded, consume-once ledger); the
              exact action must bind the commit sha AND `git ls-remote`
              must show that sha at the receipt's remote ref; the mutable
              rig-loop run.json mirror is never consulted
  verdict  -> digest-bound artifact inside repo-trusted roots, decision=pass,
              carrying the dispatch HMAC attestation stamped by rig-loop
              verify (verifier/builder family proven by signature, not by a
              writable string); residual trust is stated honestly below

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
import hmac
import json
import os
import subprocess
import re
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
DURABLE_MIN = 10        # policy floor ONLY; statistics do the disqualifying:
                        # an all-success arm needs n >= 52 for lb >= 0.95
DURABLE_SPREAD_S = 24 * 3600  # consecutive durable trials >= 24h apart

_REMOTE_RE = re.compile(
    r"(?:[A-Za-z0-9][A-Za-z0-9._-]{0,63}"                     # named remote
    r"|(?:https?|git|ssh)://[A-Za-z0-9._~:/?#@!$&()*+,;=%-]+"  # explicit URL
    r"|[A-Za-z0-9._+-]+@[A-Za-z0-9.-]+:[A-Za-z0-9._~/-]+)")   # scp-style
_GIT_ENV = {**os.environ, "GIT_CONFIG_NOSYSTEM": "1",
            "GIT_TERMINAL_PROMPT": "0"}
VERDICT_DIR = "proof/verdicts"  # repo dir verdict artifacts must live under
ANCHOR_FILE = ".rig/d85/certifier.digest"  # out-of-tree, human-sealed
_VERDICT_VOCAB = ("PERFECT", "VERIFIED", "PARTIAL", "FEEDBACK", "FAILED")
VERDICT_PASS_DEFAULT = ("PERFECT", "VERIFIED")


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


def _ls_remote(repo: Path, remote: str, ref: str) -> tuple[str | None, str | None]:
    """(sha, error). Missing git, non-zero exit, timeout or unparsable
    output return an error — unavailable is NEVER a pass. The contract is
    <name|url>: option-like strings, ext/fd transports and control chars
    are refused by closed grammar BEFORE exec; the ref is judged by git
    itself (check-ref-format), not by a lookalike regex. argv-list exec,
    `--` terminator, ext transport disabled, no prompts, no system
    config, no credential helper."""
    if not remote or remote[0] == "-" or not _REMOTE_RE.fullmatch(remote):
        return None, f"remote {remote[:40]!r} rejected by closed grammar"
    if not ref or ref[0] == "-":
        return None, f"ref {ref[:40]!r} rejected"
    try:
        chk = subprocess.run(["git", "check-ref-format",
                              "--allow-onebranch", ref],
                             cwd=repo, capture_output=True, timeout=10,
                             env=_GIT_ENV)
        if chk.returncode != 0:
            return None, f"git rejects ref {ref[:60]!r}"
        p = subprocess.run(
            ["git", "-c", "protocol.ext.allow=never",
             "-c", "credential.helper=", "-C", str(repo),
             "ls-remote", "--", remote, ref],
            capture_output=True, text=True, timeout=30, env=_GIT_ENV)
    except (OSError, subprocess.TimeoutExpired) as e:
        return None, f"git ls-remote could not run: {e}"
    if p.returncode != 0:
        return None, f"git ls-remote exit {p.returncode}: {(p.stderr or p.stdout)[-120:].strip()}"
    lines = [ln for ln in p.stdout.splitlines() if ln.strip()]
    if len(lines) != 1:
        return None, f"git ls-remote returned {len(lines)} refs for {ref!r}"
    got = lines[0].split("\t", 1)[0].strip()
    return (got, None) if len(got) == 40 else (None, "git ls-remote sha unparsable")


def _signing_key(repo: Path) -> bytes | None:
    """Same key trust class as idp/surface (.signing.key / env)."""
    env = os.environ.get("RIG_CAPABILITIES_SIGNING_KEY")
    if env:
        return env.encode()
    try:
        raw = (repo / ".signing.key").read_bytes().strip()
    except OSError:
        return None
    return raw or None


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
    """Joint durable+repeatable receipt, canonical attempt-key semantics
    (match measure.Recorder):
    - a row counts only with valid cell/trial_id/attempt_seq/outcome AND a
      record-time bind.commit_sha == this commit; malformed or pre-s2b rows
      are never trusted;
    - dedup on (cell, trial_id, attempt_seq): one trial is one trial_id,
      its outcome the highest bound attempt_seq (a retry supersedes). One
      row duplicated 72x yields ONE trial — never TRIAL_MIN;
    - durable trials (bind.kind == "durable") must number >= DURABLE_MIN
      and sit pairwise >= 24h apart: durability is SPREAD, not volume;
    - lower bounds are recomputed per arm; the joint floor is
      min(lb_durable, lb_repeatable) — the weaker arm decides. Receipt
      stated values are never consulted."""
    art = _inside(repo, r.get("trials", ""))
    if art is None or not art.exists():
        return [f"joint: trial ledger missing or escaping ({r.get('trials')!r})"]
    want_cells = set(r.get("cells", []))
    best: dict[tuple[str, str], tuple[int, str, float, str]] = {}
    seen: dict[tuple[str, str, int], str] = {}
    unbound = malformed = 0
    try:
        for line in art.read_text().splitlines():
            if not line.strip():
                continue
            row = json.loads(line)
            cell, tid = row.get("cell"), row.get("trial_id")
            seq, out = row.get("attempt_seq"), row.get("outcome")
            if (cell not in want_cells or not isinstance(tid, str) or not tid
                    or not isinstance(seq, int) or seq < 1
                    or out not in ("success", "failure")):
                malformed += 1
                continue
            bind = row.get("bind") or {}
            if bind.get("commit_sha") != sha:
                unbound += 1
                continue
            key3 = (cell, tid, seq)
            if key3 in seen:
                if seen[key3] != out:
                    return [f"joint: LEDGER CORRUPTION — attempt {cell}/"
                            f"{tid}#{seq} carries contradictory outcomes "
                            f"({seen[key3]!r} vs {out!r}); identical replay "
                            "is safe, contradiction is not"]
                continue  # identical replay of one attempt: counts once
            seen[key3] = out
            ts = row.get("ts")
            num = float(ts) if isinstance(ts, (int, float)) and not isinstance(ts, bool) else 0.0
            kind = "durable" if bind.get("kind") == "durable" else "repeatable"
            if kind == "durable" and num <= 1_000_000_000:
                return [f"joint: durable trial {tid} carries non-epoch ts "
                        "— 24h spread is unprovable without numeric time"]
            cand = (seq, out, num, kind)
            cur = best.get((cell, tid))
            if cur is None or seq >= cur[0]:
                best[(cell, tid)] = cand
    except (json.JSONDecodeError, OSError, TypeError, ValueError) as e:
        return [f"joint: ledger unreadable: {e}"]
    n = len(best)
    if n < r.get("min_trials", TRIAL_MIN):
        return [f"joint: only {n} distinct trials bound to {sha[:12]} "
                f"(+{unbound} bound elsewhere/unbound, {malformed} malformed; "
                "duplicated attempt rows never count)"]
    arms: dict[str, list[int]] = {"durable": [0, 0], "repeatable": [0, 0]}
    dur_ts: list[float] = []
    for _, out, ts, kind in best.values():
        arms[kind][0] += out == "success"
        arms[kind][1] += 1
        if kind == "durable":
            dur_ts.append(ts)
    if arms["durable"][1] < r.get("min_durable", DURABLE_MIN):
        return [f"joint: {arms['durable'][1]} durable trials < "
                f"{r.get('min_durable', DURABLE_MIN)} (volume is not durability)"]
    if arms["repeatable"][1] == 0:
        return ["joint: no repeatable-arm trials (min(lb) over an empty "
                "arm is not evidence)"]
    dur_ts.sort()
    gaps = [b - a for a, b in zip(dur_ts, dur_ts[1:])]
    if gaps and min(gaps) < DURABLE_SPREAD_S:
        return [f"joint: durable trials not >=24h apart "
                f"(smallest gap {min(gaps) / 3600:.1f}h)"]
    lb_d = wilson_lb(arms["durable"][0], arms["durable"][1], 0.05)
    lb_r = wilson_lb(arms["repeatable"][0], arms["repeatable"][1], 0.05)
    lb = min(lb_d, lb_r)
    if lb < JOINT_FLOOR:
        return [f"joint: recomputed min(lb) {lb:.4f} < {JOINT_FLOOR} "
                f"(durable {arms['durable'][0]}/{arms['durable'][1]} "
                f"lb {lb_d:.4f}; repeatable "
                f"{arms['repeatable'][0]}/{arms['repeatable'][1]} "
                f"lb {lb_r:.4f}) — receipt stated value ignored"]
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
    att = v.get("attest")
    if not isinstance(att, dict) or not isinstance(att.get("payload"), dict):
        return errs + ["verdict: family self-asserted (unsigned) — an "
                       "artifact without the dispatch HMAC is not "
                       "cross-family evidence"]
    key = _signing_key(repo)
    if key is None:
        return errs + ["verdict: signing key unavailable — attestation "
                       "cannot be checked; fail closed"]
    want = hmac.new(key, json.dumps(att["payload"], sort_keys=True).encode(),
                    hashlib.sha256).hexdigest()
    if not hmac.compare_digest(str(att.get("sig", "")), want):
        return errs + ["verdict: attestation signature invalid — payload "
                       "edited after the verifier dispatch signed it"]
    p = att["payload"]
    # Candidate binding: an outer commit_sha is UNSIGNED claim data — a
    # verdict must cryptographically bind what the verifier reviewed, or a
    # validly signed verdict replays onto any commit by editing one field.
    # Signed: parent_head (HEAD at dispatch) + candidate_tree — the git
    # tree of HEAD plus exactly the files the verifier reviewed. Requiring
    # sha^{tree} equality means NO other content may differ anywhere in
    # the commit: same files + extra malicious change elsewhere = refusal.
    ph, ct = p.get("parent_head"), p.get("candidate_tree")
    if not (isinstance(ph, str) and re.fullmatch(r"[0-9a-f]{40}", ph)
            and isinstance(ct, str) and re.fullmatch(r"[0-9a-f]{40}", ct)):
        return errs + ["verdict: attestation carries no candidate binding "
                       "(parent_head + candidate_tree) — a verdict without "
                       "a signed candidate can be replayed onto any commit"]
    par = _git_out(repo, ["rev-parse", "--verify", "-q", f"{sha}^"])
    if par != ph:
        return errs + [f"verdict: replayed — the signed dispatch reviewed "
                       f"on top of {ph[:12]}, commit {sha[:12]} has parent "
                       f"{(par or 'unknown')[:12]}"]
    tree = _git_out(repo, ["rev-parse", "--verify", "-q",
                           f"{sha}^{{tree}}"])
    if tree != ct:
        return errs + ["verdict: candidate tree mismatch — the verifier "
                       f"signed tree {ct[:12]}, commit tree is "
                       f"{(tree or 'unknown')[:12]} (replay, extra files, "
                       "or any post-review change)"]
    if (p.get("family") != v.get("verifier_family")
            or p.get("builder_family") != v.get("builder_family")):
        errs.append("verdict: families disagree with the signed dispatch "
                    "record (claim edited after signing)")
    if not p.get("family"):
        errs.append("verdict: verifier family missing")
    if v.get("verifier_family") == p.get("builder_family"):
        errs.append("verdict: same-family (builder self-certification)")
    for k in ("run_id", "exit", "verdict", "sha256_prompt",
              "sha256_output", "at"):
        if k in v and v[k] != p.get(k):
            errs.append(f"verdict: {k} disagrees with the signed dispatch "
                        "record (artifact claim edited after signing)")
    if v.get("decision") == "pass":
        # pass claims are backed by a FIXED policy set. Manifest data may
        # not widen it — an unsigned accept:["FAILED"] would otherwise turn
        # a signed FAILED dispatch into "pass". PARTIAL acceptance is a
        # loop-gate config decision, never an unconditional commit pass.
        if p.get("verdict") not in VERDICT_PASS_DEFAULT:
            errs.append("verdict: artifact claims pass but the signed "
                        f"dispatch recorded {p.get('verdict')!r} — pass is "
                        "backed only by " + "/".join(VERDICT_PASS_DEFAULT))
        if p.get("exit") != 0:
            errs.append("verdict: artifact claims pass but the signed "
                        f"dispatch exit is {p.get('exit')!r}")
    return errs


def _verify_remote(repo: Path, r: dict, sha: str) -> list[str]:
    """spec:13 — the Gate-D approval binds the EXACT commit, which means
    nothing unless that commit is actually at the remote: `git ls-remote`
    proof, recomputed here, never taken from the receipt."""
    remote, ref = r.get("remote"), r.get("ref")
    if not remote or not ref:
        return ["gate-d: remote proof missing (receipt must carry "
                "remote + ref)"]
    got, err = _ls_remote(repo, str(remote), str(ref))
    if err:
        return [f"gate-d: remote proof unavailable — {err}"]
    if got != sha:
        return [f"gate-d: remote {remote}/{ref} shows {got[:12]}, "
                f"not {sha[:12]}"]
    return []

def _git_out(repo: Path, args: list[str]) -> str:
    """TEST-ONLY monkeypatch seam (module-level, like _ls_remote)."""
    try:
        r = subprocess.run(["git", "-C", str(repo), *args],
                           capture_output=True, text=True, timeout=15,
                           env=_GIT_ENV)
        return r.stdout.strip() if r.returncode == 0 else ""
    except (OSError, subprocess.TimeoutExpired):
        return ""



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
        errs += _verify_remote(repo, manifest["gate-d"], sha)
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
                                "attempt_seq": 1, "ts": 1_700_000_000 + i * 60,
                                "outcome": "failure" if i < failures else "success",
                                "bind": {"commit_sha": bound_to}})
                    for i in range(72)]
            rows += [json.dumps({"trial_id": f"d{i:02d}", "cell": "C001",
                                 "attempt_seq": 1, "outcome": "success",
                                 "ts": 1_600_000_000 + i * 90_000,
                                 "bind": {"commit_sha": bound_to,
                                          "kind": "durable"}})
                     for i in range(52)]
            ledger.write_text("\n".join(rows) + "\n")

        write_ledger(0)
        _REAL_LS = _ls_remote
        globals()["_ls_remote"] = lambda rp, rm, rf: (SHA, None)
        key = b"cd" * 32
        (repo / ".signing.key").write_bytes(key)
        os.environ["RIG_CAPABILITIES_SIGNING_KEY"] = key.decode()
        _PARENT = "f" * 40
        _TREE = "e" * 40
        _GO_REAL = globals()["_git_out"]

        def _go_stub(rp, args):
            t = args[-1] if args else ""
            if t == SHA + "^":
                return _PARENT
            if t == SHA + "^{tree}":
                return _TREE
            return ""
        globals()["_git_out"] = _go_stub

        def signed_v(name, *, verifier="kimi", builder="claude",
                     payload_edits=None, claim_edits=None, drop_sig=False,
                     sign_verdict="VERIFIED", sign_exit=0, sign_binding=True):
            payload = {"family": verifier, "run_id": "R",
                       "verdict": sign_verdict,
                       "exit": sign_exit, "builder_family": builder,
                       "argv0": "x",
                       "sha256_prompt": "aa", "sha256_output": "bb",
                       "at": "2026-01-01T00:00:00Z",
                       "parent_head": _PARENT,
                       "candidate_tree": _TREE}
            if not sign_binding:  # dispatch WITHOUT git binding (honest
                payload["parent_head"] = payload["candidate_tree"] = ""
            sig = _h.new(key, json.dumps(payload, sort_keys=True).encode(),
                         _hl.sha256).hexdigest()
            for k, val in (payload_edits or {}).items():
                payload[k] = val  # tamper AFTER signing — no key, no re-sign
            obj = {"commit_sha": SHA, "decision": "pass",
                   "builder_family": builder, "verifier_family": verifier,
                   "run_id": "R", "exit": 0}
            for k, val in (claim_edits or {}).items():
                obj[k] = val
            if not drop_sig:
                obj["attest"] = {"payload": payload, "sig": sig}
            (repo / "proof/verdicts" / name).write_text(json.dumps(obj))
            return "proof/verdicts/" + name
        (repo / "proof/verdicts").mkdir(parents=True)
        signed_v("v.json")
        (repo / "build.json").write_text(json.dumps({"commit_sha": SHA}))
        (repo / "cert.json").write_text("{}")
        manifest = {
            "d85": {"build": "build.json", "cert": "cert.json"},
            "joint": {"trials": "trials.jsonl", "cells": ["C001"]},
            "gate-d": {"process_id": "P1", "action_file": "actions/ship.json",
                       "remote": "origin", "ref": "refs/heads/main"},
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

        expect("tampered ledger (71/72)", None, "recomputed min(lb)",
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
        # same-family verdict — signed, so it reaches the family check
        v = _check(repo, SHA, {**manifest, "verdict": {
            "artifact": signed_v("f.json", verifier="claude")}}, **seam)
        if v["admitted"] or not any("same-family" in r for r in v["refusals"]):
            errs.append("same-family verdict admitted")
        expect("verdict outside trusted dir",
               lambda m: m["verdict"].update(artifact="v.json"), "trusted dir")
        # ---- s11: forge / spread / corruption / retry / epoch ----
        def forge(rows):
            ledger.write_text("".join(json.dumps(r) + "\n" for r in rows))

        def jrow(tid, seq=1, out="success", kind=None, ts=1_700_000_000):
            b = {"commit_sha": SHA}
            if kind:
                b["kind"] = kind
            return {"trial_id": tid, "cell": "C001", "attempt_seq": seq,
                    "outcome": out, "ts": ts, "bind": b}
        jrec = {"trials": "trials.jsonl", "cells": ["C001"]}
        forge([jrow("dup") for _ in range(72)])
        if not any("distinct trials" in e for e in verify_joint(repo, jrec, SHA)):
            errs.append("duplicated single attempt admitted as 72 trials")
        forge([jrow(f"c{i}", kind="durable", ts=1_600_000_000 + i * 3600)
               for i in range(52)] + [jrow(f"r{i}") for i in range(72)])
        if not any("24h" in e for e in verify_joint(repo, jrec, SHA)):
            errs.append("durable rows packed hourly admitted")
        forge([jrow("x1", out="success"), jrow("x1", out="failure")])
        if not any("CORRUPTION" in e for e in verify_joint(
                repo, dict(jrec, min_trials=1), SHA)):
            errs.append("contradictory attempt outcomes admitted")
        forge([jrow("rc1", seq=1, out="failure", kind="durable",
                    ts=1_600_000_000 + 52 * 90_000),
               jrow("rc1", seq=2, out="success", kind="durable",
                    ts=1_600_000_000 + 52 * 90_000)]
              + [jrow(f"d{i}", kind="durable",
                      ts=1_600_000_000 + i * 90_000) for i in range(52)]
              + [jrow(f"r{i}") for i in range(72)])
        jr = verify_joint(repo, jrec, SHA)
        if jr:
            errs.append(f"retry-supersedes healthy ledger refused: {jr}")
        forge([jrow("bad", kind="durable", ts="yesterday")]
              + [jrow(f"d{i}", kind="durable",
                      ts=1_600_000_000 + i * 90_000) for i in range(1, 53)]
              + [jrow(f"r{i}") for i in range(72)])
        if not any("non-epoch" in e for e in verify_joint(repo, jrec, SHA)):
            errs.append("non-numeric durable ts admitted")
        write_ledger(0)
        # ---- s11: remote proof + grammar (monkeypatched exec, no network)
        _orig_ls = globals()["_ls_remote"]
        try:
            globals()["_ls_remote"] = lambda rp, rm, rf: ("f" * 40, None)
            v = _check(repo, SHA, {**manifest, "gate-d": {
                **manifest["gate-d"], "remote": "origin",
                "ref": "refs/heads/main"}}, **seam)
            if v["admitted"] or not any(SHA[:12] in r for r in v["refusals"]):
                errs.append(f"wrong remote admitted: {v['refusals']}")
            globals()["_ls_remote"] = lambda rp, rm, rf: (SHA, None)
            v = _check(repo, SHA, {**manifest, "gate-d": {
                **manifest["gate-d"], "remote": "origin",
                "ref": "refs/heads/main"}}, **seam)
            if not v["admitted"]:
                errs.append(f"right remote refused: {v['refusals']}")
        finally:
            globals()["_ls_remote"] = _orig_ls
        if not _REMOTE_RE.fullmatch("https://git.example.com/r.git"):
            errs.append("valid https URL rejected by grammar")
        for bad in ("-origin", "ext::sh -c touch%20/tmp/pwn", "x y"):
            got, err = _REAL_LS(repo, bad, "refs/heads/main")
            if got or not err:
                errs.append(f"grammar hole: {bad!r}")
        got, err = _REAL_LS(repo, "https://example.invalid/a.git",
                            "refs/heads/x..y")
        if got or not err or "ref" not in err:
            errs.append(f"check-ref-format not consulted: {err!r}")
        # ---- s11: attestation (unsigned / payload-edit / claim-edit / ok)
        for nm, kw, frag in (
                ("s_unsigned.json", dict(drop_sig=True), "unsigned"),
                ("s_payload.json", dict(payload_edits={"verdict": "fail"}),
                 "signature invalid")):
            vv = _check(repo, SHA, {**manifest, "verdict": {
                "artifact": signed_v(nm, **kw)}}, **seam)
            if vv["admitted"] or not any(frag in r for r in vv["refusals"]):
                errs.append(f"{nm}: {vv['refusals']}")
        vv = _check(repo, SHA, {**manifest, "verdict": {"artifact": signed_v(
            "s_claim.json", claim_edits={"run_id": "HIJACK"})}}, **seam)
        if vv["admitted"] or not any("run_id disagrees" in r
                                     for r in vv["refusals"]):
            errs.append(f"claim-field edit admitted: {vv['refusals']}")
        vv = _check(repo, SHA, {**manifest, "verdict": {
            "artifact": signed_v("s_ok.json")}}, **seam)
        if not vv["admitted"]:
            errs.append(f"signed consistent verdict refused: {vv['refusals']}")
        # a validly SIGNED FAILED paired with an artifact "pass" must refuse
        vv = _check(repo, SHA, {**manifest, "verdict": {"artifact": signed_v(
            "s_failed.json", sign_verdict="FAILED", sign_exit=1)}}, **seam)
        if vv["admitted"] or not any("claims pass" in r
                                     for r in vv["refusals"]):
            errs.append(f"signed FAILED laundered into pass: {vv['refusals']}")
        # PARTIAL is gate-policy, never an artifact-level unconditional pass
        vv = _check(repo, SHA, {**manifest, "verdict": {"artifact": signed_v(
            "s_partial.json", sign_verdict="PARTIAL")}}, **seam)
        if vv["admitted"] or not any("claims pass" in r
                                     for r in vv["refusals"]):
            errs.append(f"signed PARTIAL admitted as unconditional pass: "
                        f"{vv['refusals']}")
        # manifest data cannot widen acceptance: vocabulary membership is
        # validation, not authorization
        vv = _check(repo, SHA, {**manifest, "verdict": {
            "artifact": signed_v("s_wide.json", sign_verdict="FAILED"),
            "accept": ["PERFECT", "VERIFIED", "PARTIAL", "FEEDBACK",
                       "FAILED"]}}, **seam)
        if vv["admitted"] or not any("claims pass" in r
                                     for r in vv["refusals"]):
            errs.append(f"unsigned accept widened acceptance: "
                        f"{vv['refusals']}")
        # PERFECT + exit 0 backs a real pass
        vv = _check(repo, SHA, {**manifest, "verdict": {"artifact": signed_v(
            "s_perfect.json", sign_verdict="PERFECT")}}, **seam)
        if not vv["admitted"]:
            errs.append(f"signed PERFECT refused: {vv['refusals']}")
        # ---- s11: candidate binding closes the replay hole
        vv = _check(repo, SHA, {**manifest, "verdict": {"artifact": signed_v(
            "s_nobind.json", sign_binding=False)}}, **seam)
        if vv["admitted"] or not any("no candidate binding" in r
                                     for r in vv["refusals"]):
            errs.append(f"unbound verdict admitted: {vv['refusals']}")
        # sibling commit: right parent, extra change anywhere in tree
        globals()["_git_out"] = lambda rp, a: (
            "d" * 40 if a[-2:] == ["-q", SHA + "^{tree}"]
            else (_PARENT if a[-2:] == ["-q", SHA + "^"] else ""))
        vv = _check(repo, SHA, {**manifest, "verdict": {"artifact": signed_v(
            "s_replay.json")}}, **seam)
        if vv["admitted"] or not any("candidate tree mismatch" in r
                                     for r in vv["refusals"]):
            errs.append(f"tree-drift replay admitted: {vv['refusals']}")
        globals()["_git_out"] = lambda rp, a: ""  # parent unresolvable
        vv = _check(repo, SHA, {**manifest, "verdict": {"artifact": signed_v(
            "s_orphan.json")}}, **seam)
        if vv["admitted"] or not any("replayed" in r for r in vv["refusals"]):
            errs.append(f"parent-drift replay admitted: {vv['refusals']}")
        globals()["_git_out"] = _go_stub
        # ---- s11: remote proof missing from receipt fails closed
        gd_nomote = {k: val for k, val in manifest["gate-d"].items()
                     if k != "remote"}
        vv = _check(repo, SHA, {**manifest, "gate-d": gd_nomote}, **seam)
        if vv["admitted"] or not any("remote proof missing" in r
                                     for r in vv["refusals"]):
            errs.append(f"missing-remote receipt admitted: {vv['refusals']}")
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
        globals()["_ls_remote"] = _REAL_LS
        globals()["_git_out"] = _GO_REAL
        os.environ.pop("RIG_CAPABILITIES_SIGNING_KEY", None)
    # vocabulary cannot drift: the runtime parser owns the states
    from rig_capabilities.loops import _VERDICT_RX
    import re as _re
    alts = _re.findall(r"\(([^)]+)\)", _VERDICT_RX.pattern)[0].split("|")
    if tuple(alts) != _VERDICT_VOCAB:
        errs.append(f"verdict vocabulary drift: loops {alts} vs "
                    f"{_VERDICT_VOCAB}")
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
