"""d85_admission — universal fail-closed admission gate for production-surface
mutations and automation execution (D85 tool-selection standard, enforcement layer).

These explicit admission and automation-launcher APIs remain available to
callers that request them. Ordinary coding-agent PreToolUse no longer invokes
this classifier. D85 applies at app/solution build certification and at a
declared ``d85_certified`` loop gate; independent loop and Gate-D controls remain.

Trust model (no writable verdict state is ever trusted):
- A mutation of a path under a configured production root requires a signed
  admission approval in the append-only ledger (~/.rig/d85/admissions/
  approvals.jsonl), HMAC-SHA256 bound to {session_key, paths, build_file,
  build_digest, process_id}, with a finite positive TTL <= 24h. The production
  approval boundary acquires ``APPROVE <admission_id>`` from an interactive TTY.
- Every mutation check re-derives the HMAC, checks TTL and exact path coverage,
  and verifies unchanged approved build bytes. Request and approval require a
  bound checklist; launch additionally re-verifies the live certificate.
- Any internal failure (unreadable config/ledger, unparseable payload, CLI
  failure) DENIES the mutation. Fail closed.

Execution boundary for scheduled automations (Hermes gateway hooks cannot
block, by platform): ``d85-run <script> [args...]`` is a fail-closed launcher —
it verifies a signed admission covering the script AND a live
``verify-cert`` pass (cert bound to the script's current bytes) before exec.
The estate validator requires the launcher for jobs added/modified after the
configured launcher_epoch; legacy jobs are flagged into the retrofit backlog.

Known ceilings (documented, deliberate):
- A shell call that *executes* a script which then writes is not observable at
  hook layer; the launcher + estate sweep are the backstops.
- The ledger key lives on the same account as the agents; forging Mike's typed
  approval requires deliberate key misuse — the same residual the Gate-D
  ledger carries. Signature verification detects all post-issuance tampering.
- Tools outside the mutation set pass the D85 gate. Canonical Claude/Codex
  matchers route all pre-tool calls to this classifier, retaining read recovery.
"""
from __future__ import annotations

import hashlib
import hmac
import json
import math
import os
import re
import secrets
import subprocess
import sys
import tempfile
import time
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent


def _d85_home() -> Path:
    """Resolved per call (never frozen at import): tests and alternate homes
    must not leak into or read from another environment's ledger."""
    return Path(os.environ.get("RIG_D85_HOME") or Path.home() / ".rig" / "d85")


def _config_path() -> Path:
    return _d85_home() / "enforcement.json"


def _admissions_dir() -> Path:
    return _d85_home() / "admissions"


def _approvals_path() -> Path:
    return _admissions_dir() / "approvals.jsonl"


def _requests_path() -> Path:
    return _admissions_dir() / "requests.jsonl"


def _key_path() -> Path:
    return _admissions_dir() / "key"
D85_CLI = Path(os.environ.get("RIG_D85_CLI") or REPO_ROOT / "capabilities" / "skills" / "rig-determinism-85" / "bin" / "rig-determinism-85")

MAX_LIFETIME_SECONDS = 24 * 3600
ADMISSION_SCHEMA = "rig.d85.admission.v1"

MUTATION_TOOLS = {
    "write", "edit", "multiedit", "notebookedit", "notebook_edit",
    "bash", "shell", "apply_patch", "applypatch", "str_replace_editor",
    "eval", "python", "python_repl", "execute_code", "run_code", "code_interpreter",
}

_REDIRECT_RX = re.compile(r"(?<![0-9&<])>>?\s*([^\s;&|<>]+)")
_TEE_RX = re.compile(r"\b(?:tee|sed\s+-i(?:\s+'')?)\s+(?:-a\s+)?([^\s;&|<>]+)")

_SHELL_MUTATION_VERBS = {
    "rm", "rmdir", "mv", "cp", "install", "ln", "dd", "rsync", "touch",
    "truncate", "mkdir", "perl", "chmod", "chown", "chflags",
}
_READONLY_FIRST = {
    "cat", "ls", "head", "tail", "wc", "grep", "rg", "find", "file", "stat",
    "diff", "cmp", "sed", "echo", "printf", "true", "false", "which", "type",
    "command", "basename", "dirname", "readlink", "realpath", "sort", "uniq",
    "cut", "tr", "jq", "column", "seq", "date", "env", "printenv", "ps",
    "pgrep", "id", "uname", "whoami", "hostname", "nproc", "test", "[",
    "open", "code", "md5sum", "sha1sum", "sha256sum", "shasum", "b2sum",
}
_READONLY_GIT = {"status", "log", "diff", "show", "branch", "rev-parse", "ls-files", "blame"}
_CLAUSE_RX = re.compile(r"[;|&]{1,2}")

_JAKE_GREET_PATH = "/Users/rig128gb/.rig/bin/jake-greet"
_JAKE_GREET_SHA256 = "01b9dbdd3edc6554fbe0e1db6b6bff68482ea198ac7ff94ba1aedaaa3934df46"
_JAKE_GREET_COMMAND = re.compile(
    re.escape(_JAKE_GREET_PATH)
    + r"(?:[ \t]+--agent[ \t]+[A-Za-z0-9_-]+)?(?:[ \t]+--json)?[ \t]*"
)


def _shell_analysis(command: str, cwd: str | None) -> tuple[list[str], list[str], bool]:
    """(write_targets, unknown_tokens, has_unproven_clause) for a shell command.
    Write targets: redirects/tee/sed -i plus operands of unambiguous mutation
    verbs. unknown_tokens: non-flag tokens of clauses whose verb is neither
    read-only nor a known mutation verb. has_unproven_clause: at least one
    such clause exists. PARTIAL BOUNDARY: interpreter/build tools (python
    script.py, make, npm) can write protected roots without naming them; this
    parser cannot see those. The cwd-under-root rule in hook_check plus
    d85-run/estate backstops narrow but do not close that gap; OS-level
    sandboxing is the only universal boundary (documented ceiling)."""
    if _JAKE_GREET_COMMAND.fullmatch(command):
        try:
            if hashlib.sha256(Path(_JAKE_GREET_PATH).read_bytes()).hexdigest() == _JAKE_GREET_SHA256:
                return [], [], False
        except OSError:
            pass
    writes: list[str] = []
    unknown: list[str] = []
    has_unproven = False
    for rx in (_REDIRECT_RX, _TEE_RX):
        for raw in rx.findall(command):
            if raw not in ("/dev/null",) and not raw.startswith("&"):
                writes.append(_abs(raw, cwd))
    for clause in _CLAUSE_RX.split(command):
        tokens = clause.split()
        if not tokens:
            continue
        i = 0
        while i < len(tokens) - 1 and re.match(r"^[A-Za-z_][A-Za-z0-9_]*=", tokens[i]):
            i += 1  # skip env assignments
        verb = Path(tokens[i]).name
        if verb in _SHELL_MUTATION_VERBS or (verb == "sed" and re.search(r"(^|\s)-i", clause)):
            for tok in tokens[i + 1:]:
                if not tok.startswith("-") and not tok.startswith("$"):
                    writes.append(_abs(tok, cwd))
        elif verb == "git" and len(tokens) > i + 1 and tokens[i + 1] in _READONLY_GIT:
            continue
        elif verb in _READONLY_FIRST:
            continue
        else:
            has_unproven = True
            for tok in tokens[i:]:
                if not tok.startswith(("-", "$", "&", "(", ")")) and ("/" in tok or tok.startswith("~")):
                    unknown.append(_abs(tok, cwd))
    return writes, unknown, has_unproven


class AdmissionDenied(Exception):
    """Fail-closed denial carrying the operator-facing reason."""


# ---------------------------------------------------------------- config

def load_config() -> dict:
    try:
        raw = json.loads(_config_path().read_text(encoding="utf-8"))
        roots = [str(Path(os.path.expanduser(r))) for r in raw["roots"] if isinstance(r, str) and r]
        ttl = float(raw.get("ttl_hours", 24))
        if not math.isfinite(ttl) or ttl <= 0 or ttl * 3600 > MAX_LIFETIME_SECONDS:
            raise ValueError("ttl_hours must be finite, positive, and at most 24")
        return {"roots": roots, "ttl_hours": ttl}
    except FileNotFoundError:
        raise AdmissionDenied(
            f"[d85] enforcement config missing: {_config_path()} (needs JSON with roots[] and ttl_hours). "
            "Mutations of production surfaces are blocked until it exists — fail closed.")
    except Exception as exc:  # noqa: BLE001
        raise AdmissionDenied(f"[d85] enforcement config unreadable ({exc!r}) — mutations blocked, fail closed.")


def _under_roots(path: str, roots: list[str]) -> bool:
    resolved = Path(path).resolve(strict=False)
    for root in roots:
        canonical = Path(os.path.expanduser(root)).resolve(strict=False)
        if resolved == canonical or str(resolved).startswith(str(canonical).rstrip(os.sep) + os.sep):
            return True
    return False


# ---------------------------------------------------------------- targets

def _abs(raw: str, cwd: str | None) -> str:
    path = Path(os.path.expanduser(str(raw).strip().strip("'\"")))
    if not path.is_absolute() and cwd:
        path = Path(cwd) / path
    return str(path.resolve(strict=False))


def _inventory_root(build_file: str | Path) -> Path:
    """Convention: build.json sits beside its process inventory in root/ when
    that directory exists; otherwise the build's own directory is the root."""
    build = Path(build_file).resolve()
    candidate = build.parent / "root"
    return candidate if candidate.is_dir() else build.parent


def mutation_targets_ex(p: dict) -> tuple[list[str], list[str], bool]:
    """(write_targets, unknown_tokens, has_unproven_clause). See _shell_analysis."""
    out: list[str] = []
    for raw in p.get("paths") or []:
        if raw:
            out.append(_abs(raw, p.get("cwd")))
    unknown: list[str] = []
    has_unproven = False
    if str(p.get("tool") or "").lower() in ("bash", "shell") and p.get("command"):
        writes, unknown, has_unproven = _shell_analysis(p["command"], p.get("cwd"))
        out.extend(writes)
    seen: list[str] = []
    for t in out:
        if t not in seen:
            seen.append(t)
    unk: list[str] = []
    for t in unknown:
        if t not in unk:
            unk.append(t)
    return seen, unk, has_unproven


def mutation_targets(p: dict) -> list[str]:
    """Back-compat wrapper: write targets only."""
    return mutation_targets_ex(p)[0]


def session_key(p: dict) -> str:
    sid = (p.get("session_id") or "").strip()
    if sid:
        return "sid:" + sid
    digest = hashlib.sha256((p.get("cwd") or os.getcwd()).encode("utf-8")).hexdigest()[:16]
    return "cwd:" + digest


# ---------------------------------------------------------------- canonical hashing / ledger

def _canonical_bytes(value) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def _canonical_hash(value) -> str:
    return hashlib.sha256(_canonical_bytes(value)).hexdigest()


def _load_key() -> bytes:
    try:
        raw = _key_path().read_bytes().strip()
        return bytes.fromhex(raw.decode("ascii"))
    except Exception as exc:  # noqa: BLE001
        raise AdmissionDenied(f"[d85] admission ledger key unreadable ({exc!r}) — mutations blocked, fail closed.")


def _init_ledger() -> bytes:
    _admissions_dir().mkdir(parents=True, exist_ok=True)
    if not _key_path().exists():
        _key_path().write_text(secrets.token_hex(32), encoding="ascii")
        os.chmod(_key_path(), 0o600)
    return _load_key()


def _read_records(path: Path) -> list[dict]:
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except FileNotFoundError:
        return []
    except Exception as exc:  # noqa: BLE001
        raise AdmissionDenied(f"[d85] admission ledger unreadable ({exc!r}) — mutations blocked, fail closed.")
    records = []
    for i, line in enumerate(lines):
        if not line.strip():
            continue
        try:
            rec = json.loads(line)
        except json.JSONDecodeError as exc:
            raise AdmissionDenied(f"[d85] admission ledger corrupt ({path.name} line {i}: {exc}) — fail closed.")
        if not isinstance(rec, dict):
            raise AdmissionDenied(f"[d85] admission ledger corrupt ({path.name} line {i}: not an object) — fail closed.")
        records.append(rec)
    return records


def _verify_signature(rec: dict, key: bytes) -> None:
    body = {k: v for k, v in rec.items() if k != "signature"}
    expected = hmac.new(key, _canonical_bytes(body), hashlib.sha256).hexdigest()
    if not hmac.compare_digest(str(rec.get("signature", "")), expected):
        raise AdmissionDenied("[d85] admission approval signature mismatch (tampered or forged record) — fail closed.")


# ---------------------------------------------------------------- build compliance (fresh every check)

def _build_compliant_bound(build_file: str, process_id: str) -> dict:
    """Run the canonical checklist BOUND to the process and require a bound
    CHECKLIST_PASS (exit 0). Returns the certificate JSON (the checklist CLI
    emits it on stdout; it does NOT persist a file). Unbound results are never
    accepted: only a bound pass is an enforcement verdict. Raises
    AdmissionDenied on anything else."""
    build = Path(build_file)
    if not build.is_file():
        raise AdmissionDenied(f"[d85] bound build file no longer exists: {build} — admission stale, fail closed.")
    try:
        r = subprocess.run(
            [sys.executable, str(D85_CLI), "checklist", str(build),
             "--root", str(_inventory_root(build)), "--process-id", str(process_id)],
            capture_output=True, text=True, timeout=120,
        )
    except Exception as exc:  # noqa: BLE001
        raise AdmissionDenied(f"[d85] bound checklist failed ({exc!r}) — mutations blocked, fail closed.")
    if r.returncode != 0:
        raise AdmissionDenied(
            f"[d85] bound build checklist verdict is not a bound CHECKLIST_PASS (exit {r.returncode}) — "
            "re-run the admission flow: admit-request → APPROVE <admission_id> → admit-approve.")
    try:
        cert = json.loads((r.stdout or "").strip().splitlines()[-1])
    except Exception:  # noqa: BLE001
        raise AdmissionDenied("[d85] bound checklist exit 0 but no certificate JSON on stdout — fail closed.")
    if cert.get("verdict") != "CHECKLIST_PASS" or cert.get("inventory_binding") != "bound":
        raise AdmissionDenied("[d85] bound checklist stdout is not a bound CHECKLIST_PASS — fail closed.")
    return cert


def _build_unchanged(rec: dict) -> None:
    """Per-mutation freshness: the approved build file's bytes must still hash
    to the digest recorded in the signed approval. Cheap, deterministic, and
    deadlock-free mid-edit: the manifest (paths + build content) was approved
    up front; the enforcement verdict was the bound cert at approve time; a
    fresh bound cert is required again at promotion/execution (d85-run)."""
    build = Path(str(rec.get("build_file", "")))
    try:
        current = hashlib.sha256(build.read_bytes()).hexdigest()
    except Exception as exc:  # noqa: BLE001
        raise AdmissionDenied(f"[d85] approved build file unreadable: {build} ({exc!r}) — fail closed.")
    if current != rec.get("build_digest"):
        raise AdmissionDenied(
            f"[d85] build file changed after approval {rec.get('admission_id')} — admission stale. "
            "Re-run admit-request → APPROVE → admit-approve for the updated build.")


# ---------------------------------------------------------------- hook check

def hook_check(p: dict, *, now: float | None = None) -> dict | None:
    """None = allow. {"action": "deny", "reason": ...} = block. Fail closed."""
    try:
        tool = (p.get("tool") or "").strip()
        if not tool:
            return {"action": "deny", "reason": (
                "[d85] pre-tool payload carried no tool identity — cannot classify the call "
                "(fail closed). Re-issue the tool call through the harness hook path.")}
        if tool.lower() not in MUTATION_TOOLS:
            return None
        cfg = load_config()
        if not cfg["roots"]:
            return None  # explicitly empty roots: standard switched off (documented)
        if tool.lower() in ("eval", "python", "python_repl", "execute_code", "run_code", "code_interpreter"):
            # UNIVERSAL RULE (advisory-accepted): regex write-signature scanning cannot
            # contain arbitrary code (getattr/encoded source/imports/subprocess all bypass).
            # Under active enforcement, arbitrary-code tools are DENIED outright — no
            # session-cover unlock either, since a narrow path grant must not become
            # write authority over every root. Break-glass: RIG_D85_DISABLE=1 in the
            # PARENT environment only. Move write work into explicit write/bash calls
            # (admissible) or an admitted d85-run automation.
            return {"action": "deny", "reason": (
                "[d85] arbitrary-code tool (eval/python/repl) is denied while D85 enforcement is "
                "active: no static analysis can bound what arbitrary code writes (documented "
                "ceiling, not a convenience exception).\n"
                "Use explicit write/edit calls (admissible per exact path) or run the code as an "
                "admitted automation: admit-request --launcher <script> → APPROVE <id> → "
                "admit-approve → d85-run <script>. Break-glass: RIG_D85_DISABLE=1 in the parent "
                "environment (audited).")}
        targets, unknown, has_unproven = mutation_targets_ex(p)
        gated = [t for t in targets if _under_roots(t, cfg["roots"])]
        unknown_gated = [t for t in unknown if _under_roots(t, cfg["roots"])]
        cwd_str = _abs(".", p.get("cwd"))
        if unknown_gated:
            return {"action": "deny", "reason": (
                f"[d85] shell command references a production surface with a verb the gate cannot "
                f"statically prove read-only: {unknown_gated[0]}\n"
                "Fail closed. Either (a) admit the exact paths: admit-request → APPROVE <id> → "
                "admit-approve, or (b) express the read with a provably read-only command "
                "(cat/grep/ls/git log ...).")}
        if has_unproven and _under_roots(cwd_str, cfg["roots"]):
            return {"action": "deny", "reason": (
                f"[d85] non-read-only shell verb while the working directory is a production "
                f"surface: {cwd_str}\n"
                "Fail closed (interpreter/build tools can write without naming targets). "
                "Admit the exact paths first, or run from outside the protected root.")}
        if not gated:
            return None
        key = session_key(p)
        current = time.time() if now is None else now
        records = [r for r in _read_records(_approvals_path()) if r.get("schema") == ADMISSION_SCHEMA]
        if not records:
            return _deny_no_admission(gated, key)
        ledger_key = _load_key()
        for target in gated:
            cover = None
            for rec in reversed(records):
                _verify_signature(rec, ledger_key)
                if not (float(rec.get("issued_at", 0)) <= current < float(rec.get("expires_at", 0))):
                    continue
                if rec.get("session_key") != key:
                    continue
                if target in [str(x) for x in rec.get("paths", [])]:
                    try:
                        _build_unchanged(rec)  # newest fully-valid cover wins
                    except AdmissionDenied:
                        continue
                    cover = rec
                    break
            if cover is None:
                return _deny_no_admission([target], key)
        return None
    except AdmissionDenied as exc:
        return {"action": "deny", "reason": str(exc)}
    except Exception as exc:  # noqa: BLE001
        return {"action": "deny", "reason": f"[d85] admission gate internal failure (fail closed): {exc!r}"}


def _deny_no_admission(targets: list[str], key: str) -> dict:
    t = targets[0]
    return {"action": "deny", "reason": (
        f"[d85] MUTATION BLOCKED — production surface requires an admission: {t}\n"
        f"  session key: {key}\n"
        "  1. Author/refresh the D85 build checklist for this change (build.json with properties, "
        "archify_diagram_path, evidence).\n"
        f"  2. rig-determinism-85 admit-request <build.json> --process-id <id> --path {t} --session-key {key}\n"
        "  3. Mike types: APPROVE <admission_id>\n"
        "  4. rig-determinism-85 admit-approve (interactive TTY; --phrase is test-only)\n"
        "Until then, no mutation of production surfaces from this session — fail closed.")}


# ---------------------------------------------------------------- request / approve / status

def admit_request(build_file: str, process_id: str | None, paths: list[str],
                  session_key_: str, launchers: list[str] | None = None) -> dict:
    build = Path(build_file).resolve()
    if not build.is_file():
        raise AdmissionDenied(f"[d85] build file not found: {build}")
    if not process_id:
        try:
            process_id = str(json.loads(build.read_text(encoding="utf-8")).get("process_id") or "")
        except Exception:  # noqa: BLE001
            process_id = ""
    if not process_id:
        raise AdmissionDenied("[d85] no --process-id and build.json carries no process_id — fail closed.")
    if any(not isinstance(x, (str, os.PathLike)) or not os.fspath(x).strip()
           for values in (paths, launchers or []) for x in values):
        raise AdmissionDenied("[d85] admission paths and launchers must be nonempty paths")
    abs_paths = [_abs(x, None) for x in paths]
    launcher_abs = [_abs(x, None) for x in (launchers or [])]
    if not abs_paths and not launcher_abs:
        raise AdmissionDenied("[d85] admit-request requires at least one --path or --launcher")
    _build_compliant_bound(str(build), process_id)
    digest = hashlib.sha256(build.read_bytes()).hexdigest()
    launcher_digests = {}
    for x in launcher_abs:
        if not Path(x).is_file():
            raise AdmissionDenied(
                f"[d85] launcher does not exist at request time, cannot bind content: {x} — fail closed.")
        launcher_digests[str(x)] = hashlib.sha256(Path(x).read_bytes()).hexdigest()
    salt = secrets.token_hex(8)
    admission_id = "d85adm_" + _canonical_hash({
        "build_digest": digest, "paths": abs_paths, "session_key": session_key_,
        "process_id": process_id, "launchers": [str(x) for x in launcher_abs],
        "launcher_digests": launcher_digests,
        "salt": salt,
    })[:12]
    request = {
        "schema": ADMISSION_SCHEMA, "admission_id": admission_id, "session_key": session_key_,
        "paths": abs_paths, "launchers": [str(x) for x in launcher_abs],
        "launcher_digests": launcher_digests,
        "build_file": str(build), "build_digest": digest, "salt": salt,
        "process_id": process_id, "requested_at": int(time.time()), "status": "pending",
    }
    _admissions_dir().mkdir(parents=True, exist_ok=True)
    with _requests_path().open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(request, sort_keys=True) + "\n")
    return request


def admit_approve(phrase: str | None = None, *, approver: str = "mike", now: float | None = None) -> dict:
    test_mode = phrase is not None or now is not None
    if test_mode:
        home = _d85_home().resolve()
        temp_root = Path(tempfile.gettempdir()).resolve()
        if (os.environ.get("RIG_D85_TEST_PHRASE") != "1"
                or not os.environ.get("RIG_D85_HOME")
                or home == (Path.home() / ".rig/d85").resolve()
                or home == temp_root or not home.is_relative_to(temp_root)
                or any(not p.resolve().is_relative_to(home)
                       for p in (_requests_path(), _approvals_path(), _key_path()))):
            raise AdmissionDenied("[d85] supplied approval phrase/clock is test-only and requires an isolated temporary D85 home")
        how = "test-phrase"
    else:
        try:
            with open("/dev/tty", encoding="utf-8") as tty:
                if not tty.isatty():
                    raise AdmissionDenied("[d85] approval requires an interactive TTY")
                print("type: APPROVE <admission_id>", file=sys.stderr)
                phrase = tty.readline()
        except OSError as exc:
            raise AdmissionDenied(f"[d85] approval requires an interactive TTY: {exc}") from exc
        how = "typed-approve"
    m = re.fullmatch(r"\s*APPROVE\s+(d85adm_[0-9a-f]{12})\s*", phrase or "")
    if not m:
        raise AdmissionDenied('[d85] admit-approve requires the exact phrase "APPROVE <admission_id>"')
    admission_id = m.group(1)
    pending = [r for r in _read_records(_requests_path())
               if r.get("admission_id") == admission_id and r.get("status") == "pending"]
    if not pending:
        raise AdmissionDenied(f"[d85] no pending admission request {admission_id} — fail closed")
    req = pending[-1]
    if test_mode and any(
        not Path(str(path)).resolve().is_relative_to(temp_root)
        for path in [req.get("build_file", ""), *req.get("paths", []), *req.get("launchers", [])]
    ):
        raise AdmissionDenied("[d85] test approvals cannot cover non-temporary builds, outputs, or launchers")
    if not req.get("paths") and not req.get("launchers"):
        raise AdmissionDenied("[d85] admission requires at least one path or launcher — fail closed.")
    _ld = {str(k): v for k, v in (req.get("launcher_digests") or {}).items()}
    if req.get("launchers") and sorted(_ld) != sorted(str(x) for x in req.get("launchers", [])):
        raise AdmissionDenied(
            f"[d85] pending request {admission_id} lacks digests for every launcher — fail closed.")
    expected_id = "d85adm_" + _canonical_hash({
        "build_digest": req.get("build_digest"), "paths": req.get("paths", []),
        "session_key": req.get("session_key"), "process_id": req.get("process_id"),
        "launchers": req.get("launchers", []), "launcher_digests": _ld,
        "salt": req.get("salt", ""),
    })[:12]
    if admission_id != expected_id or not req.get("salt"):
        raise AdmissionDenied(
            f"[d85] pending request {admission_id} fails ID recomputation " "re-request, fail closed")
    req = pending[-1]
    build = Path(str(req["build_file"]))
    if not build.is_file() or hashlib.sha256(build.read_bytes()).hexdigest() != req.get("build_digest"):
        raise AdmissionDenied(f"[d85] build file changed since request {admission_id} — re-request, fail closed")
    cert = _build_compliant_bound(str(build), str(req["process_id"]))
    if not (cert.get("verdict") == "CHECKLIST_PASS" and cert.get("inventory_binding") == "bound"):
        raise AdmissionDenied("[d85] checklist did not return a bound CHECKLIST_PASS — fail closed.")
    ttl = load_config()["ttl_hours"] * 3600
    import tempfile as _tf
    fd, tmp = _tf.mkstemp(dir=str(build.parent), prefix=".certificate-", suffix=".json")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as fh:
            fh.write(json.dumps(cert, sort_keys=True) + "\n")
        os.replace(tmp, build.parent / "certificate.json")
    except BaseException:
        try:
            os.unlink(tmp)
        except OSError:
            pass
        raise
    issued = time.time() if now is None else now

    record = {
        "schema": ADMISSION_SCHEMA, "admission_id": admission_id,
        "session_key": req["session_key"], "paths": req["paths"],
        "launchers": req.get("launchers", []),
        "launcher_digests": req.get("launcher_digests", {}),
        "build_file": req["build_file"], "build_digest": req["build_digest"],
        "process_id": req["process_id"], "how": how, "by": approver,
        "issued_at": issued, "expires_at": min(issued + ttl, issued + MAX_LIFETIME_SECONDS),
    }
    key = _init_ledger()
    signature = hmac.new(key, _canonical_bytes(record), hashlib.sha256).hexdigest()
    entry = {**record, "signature": signature}
    with _approvals_path().open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(entry, sort_keys=True) + "\n")
    return entry


def admit_status() -> dict:
    cfg = {"roots": "<missing>", "ttl_hours": "<missing>"}
    try:
        cfg = load_config()
    except AdmissionDenied as exc:
        cfg = {"error": str(exc)}
    return {
        "config": cfg,
        "requests": [{"admission_id": r.get("admission_id"), "status": r.get("status"),
                      "paths": r.get("paths"), "launchers": r.get("launchers", []),
                      "launcher_digests": r.get("launcher_digests", {}), "session_key": r.get("session_key")}
                     for r in _read_records(_requests_path())][-20:],
        "approvals": [{"admission_id": r.get("admission_id"), "session_key": r.get("session_key"),
                       "paths": r.get("paths"), "launchers": r.get("launchers", []),
                       "launcher_digests": r.get("launcher_digests", {}), "expires_at": r.get("expires_at")}
                      for r in _read_records(_approvals_path())][-20:],
    }


# ---------------------------------------------------------------- execution launcher (d85-run)

def run_launcher(argv: list[str]) -> int:
    """Fail-closed launcher for scheduled automations: signed admission covering
    the script + build-digest binding + live verify-cert against the script's
    current bytes, then exec under an OS-level sandbox-exec profile that denies
    writes to every protected root except the admitted paths. The OS kernel,
    not a parser, is the boundary at execution time."""
    if not argv:
        print("usage: d85-run <script> [args...]", file=sys.stderr)
        return 2
    script = Path(os.path.expanduser(argv[0])).resolve()
    if not script.is_file():
        print(f"[d85-run] script not found: {script}", file=sys.stderr)
        return 2
    cover = None
    cfg = None
    try:
        cfg = load_config()
        if cfg["roots"]:
            # Enforcement active: EVERY launched script is gated and sandboxed,
            # regardless of its own location — a script outside the roots can
            # still write into them, so location must not weaken the boundary.
            cover = _launcher_authorized(script)
        # explicitly empty roots: standard switched off — launches run ungated
    except AdmissionDenied as exc:
        print(str(exc), file=sys.stderr)
        return 2
    try:
        if cover is not None:
            if _SANDBOX_EXEC is None:
                print("[d85-run] /usr/bin/sandbox-exec unavailable — cannot enforce the OS write "
                      "boundary for a production automation. Fail closed.", file=sys.stderr)
                return 2
            sandbox = _sandbox_argv(cfg, cover, script, argv)
            os.execv(_SANDBOX_EXEC, sandbox)
    except AdmissionDenied as exc:
        print(str(exc), file=sys.stderr)
        return 2
    os.execv(sys.executable, [sys.executable, "-B", str(script), *argv[1:]])


def _sandbox_argv(cfg: dict, cover: dict, script: Path, argv: list[str]) -> list[str]:
    """Deny writes under canonical protected roots; allow only signed output
    literals. Resolving roots matters on macOS: /var and /private/var aliases
    must describe the same sandbox boundary as the admission gate.
    The script and its parent are not implicitly writable. Reject paths that
    could alter SBPL syntax rather than interpolating escaped policy text."""
    # Writable = declared outputs only. The script itself is NOT implicitly
    # writable: it stays in the signed manifest for identity/digest, but an
    # admitted job rewriting its own launcher after live verification would
    # defeat the certified-build binding. Declare it as an explicit --path
    # output if a job legitimately rewrites itself.
    allow_literals = sorted({str(p) for p in cover.get("paths", [])})
    roots = sorted({_abs(r, None) for r in cfg["roots"]})
    for lit in allow_literals + roots:
        if not re.fullmatch(r"[A-Za-z0-9_./@+-]+", lit):
            raise AdmissionDenied(
                f"[d85-run] path contains characters outside the SBPL-safe charset and cannot be "
                f"enforced by the sandbox profile: {lit!r} — fail closed.")
    denies = "".join(f'(deny file-write* (subpath "{r}"))' for r in roots)
    allows = "".join(f'(allow file-write* (literal "{a}"))' for a in allow_literals)
    profile = f'(version 1)(allow default){denies}{allows}'
    return [_SANDBOX_EXEC, "-p", profile, sys.executable, "-B", str(script), *argv[1:]]


_SANDBOX_EXEC = "/usr/bin/sandbox-exec" if Path("/usr/bin/sandbox-exec").is_file() else None


def _launcher_authorized(script: Path) -> dict:
    current = time.time()
    ledger_key = _load_key()
    cover = None
    for rec in reversed(_read_records(_approvals_path())):
        if rec.get("schema") != ADMISSION_SCHEMA:
            continue
        _verify_signature(rec, ledger_key)
        if not (float(rec.get("issued_at", 0)) <= current < float(rec.get("expires_at", 0))):
            continue
        if str(script) in [str(x) for x in rec.get("launchers", [])]:
            # newest fully-valid cover wins: a stale build-changed approval must
            # not shadow a newer valid one (scan reversed, check build in-loop)
            want = rec.get("launcher_digests", {}).get(str(script))
            have = hashlib.sha256(script.read_bytes()).hexdigest() if script.is_file() else ""
            if not want or not re.fullmatch(r"[0-9a-f]{64}", str(want)) or want != have:
                continue  # unbound or rewritten-after-approval launcher — not this admission
            try:
                _build_unchanged(rec)
            except AdmissionDenied:
                continue
            cover = rec
            break
    if cover is None:
        raise AdmissionDenied(
            f"[d85-run] no signed admission covers {script} — register the automation: "
            "admit-request → APPROVE <admission_id> → admit-approve, then re-schedule with d85-run.")
    _build_unchanged(cover)  # re-affirm under the selected record
    cert = Path(str(cover["build_file"])).parent / "certificate.json"
    if not cert.is_file():
        raise AdmissionDenied(f"[d85-run] certificate missing beside build: {cert} — fail closed.")
    r = subprocess.run(
        [sys.executable, str(D85_CLI), "verify-cert", str(cover["build_file"]), str(cert),
         "--root", str(_inventory_root(str(cover["build_file"])))],
        capture_output=True, text=True, timeout=120,
    )
    if r.returncode != 0:
        raise AdmissionDenied(
            f"[d85-run] live verification failed (exit {r.returncode}) — script bytes no longer match the "
            f"certified state. Re-certify and re-approve before running. {(r.stdout or r.stderr)[:300]}")
    return cover
