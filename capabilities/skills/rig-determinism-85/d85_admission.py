"""d85_admission — universal fail-closed admission gate for production-surface
mutations and automation execution (D85 tool-selection standard, enforcement layer).

Every coding-agent harness (claude, codex, omp/prime via the pi extension, hermes)
routes PreToolUse through ``rig-loop hook pre-tool``; ``dispatch_hook`` runs
``hook_check`` above loop-skill logic so admission applies with or without an
active loop run.

Trust model (no writable verdict state is ever trusted):
- A mutation of a path under a configured production root requires a signed
  admission approval in the append-only ledger (`~/.rig/d85/admissions/
  approvals.jsonl`), HMAC-SHA256 bound to the exact session, output anchors,
  build digest, process and a TTL of at most 24 hours. The production boundary
  displays the immutable scope before accepting `APPROVE <admission_id>`.
- Launcher approvals additionally bind one canonical script, its bounded local
  dependency closure, exact argv/cwd, fixed-environment hash, invocation
  identity and runtime ceiling. The invocation is consumed once.
- Every mutation rechecks HMAC, TTL, output-anchor identity, session and build.
  Certification re-runs the current D85 scorer; launch verifies the score-bound
  v2 certificate before and after execution.
- Any internal failure (unreadable config/ledger, unparseable payload, CLI
  failure) DENIES the mutation. Fail closed.

Execution boundary for scheduled automations (Hermes gateway hooks cannot
block, by platform): `d85-run --session-key sid:<id> <script> [args...]` is a
fail-closed Python launcher. `sandbox-exec` denies network, all writes except
signed single-file output literals, and process creation. The launcher uses a
signed fixed Python binary and source-only local loader. The supervisor stops
the process at the earlier of its signed timeout or approval expiry and
rechecks protected bytes before returning.
The estate validator requires the launcher for jobs added/modified after the
configured launcher_epoch; legacy jobs are flagged into the retrofit backlog.

Known ceilings (documented, deliberate):
- Hook-layer shell admission allows only closed read-only verbs or mutation
  verbs with literal extracted targets. Dynamic expansion, nested execution,
  interpreters, build tools and unclassified clauses deny regardless of cwd.
- A host can still race a separate tool execution after the hook verdict. The
  one-use launcher closes that boundary for scheduled automation; universal
  interactive-host containment remains a platform integration requirement.
- The ledger key lives on the same account as the agents. Signatures detect
  post-issuance tampering but do not defeat same-UID key compromise.
- Canonical harness matchers route all pre-tool calls to this classifier while
  retaining read-only recovery when the gate is unavailable.
"""
from __future__ import annotations

import builtins
import ast
import fcntl
import hashlib
import importlib.machinery
import hmac
import json
import shlex
import math
import os
import pwd
import re
import secrets
import stat
import subprocess
import sys
import tempfile
import time
import unicodedata
from pathlib import Path

_FIXED_HOME = Path(pwd.getpwuid(os.getuid()).pw_dir).resolve()
_TEST_HOME: Path | None = None
_BG_REQUEST_SCHEMA = "rig.d85.break-glass-request.v1"
_BG_APPROVAL_SCHEMA = "rig.d85.break-glass-approval.v1"
BYPASS_SCHEMA = "rig.d85.bypass-audit.v2"
_BG_ACTION = "d85-self-disable"
_BG_MIN_TTL = 60
_BG_MAX_TTL = 900
_BG_REVIEW_WINDOW = 900




def _d85_home() -> Path:
    """Return the fixed operator home, or an explicitly patched test home."""
    return _TEST_HOME if _TEST_HOME is not None else _FIXED_HOME / ".rig" / "d85"


def _config_path() -> Path:
    return _d85_home() / "enforcement.json"


def _admissions_dir() -> Path:
    return _d85_home() / "admissions"


def _approvals_path() -> Path:
    return _admissions_dir() / "approvals.jsonl"


def _requests_path() -> Path:
    return _admissions_dir() / "requests.jsonl"
def _bypass_ledger_path() -> Path:
    return _admissions_dir() / "bypass-ledger.jsonl"




def _key_path() -> Path:
    return _admissions_dir() / "key"


def _executions_dir() -> Path:
    return _admissions_dir() / "executions"
D85_CLI = Path(__file__).resolve().parent / "bin" / "rig-determinism-85"
_FIXED_PYTHON = "/Users/rig128gb/.homebrew/Cellar/python@3.14/3.14.7/bin/python3"


def _clean_subprocess_env() -> dict[str, str]:
    return {
        "HOME": str(_FIXED_HOME),
        "TMPDIR": "/tmp",
        "PATH": "/usr/bin:/bin:/usr/sbin:/sbin",
        "LANG": "C",
        "LC_ALL": "C",
        "PYTHONDONTWRITEBYTECODE": "1",
    }


def _run_d85(args: list[str]) -> subprocess.CompletedProcess:
    return subprocess.run(
        [_FIXED_PYTHON, "-I", "-B", "-S", str(D85_CLI), *args],
        capture_output=True,
        text=True,
        timeout=120,
        cwd=D85_CLI.parent.parent,
        env=_clean_subprocess_env(),
    )



MAX_LIFETIME_SECONDS = 24 * 3600
MAX_LAUNCHER_SECONDS = 3600
MAX_LAUNCHER_SOURCE_BYTES = 1024 * 1024

MAX_LAUNCHER_DEPENDENCIES = 128
MAX_LAUNCHER_DEPENDENCY_BYTES = 4 * 1024 * 1024
_LAUNCHER_BOOTSTRAP = """
import hashlib
import importlib.util
import json
import pathlib
import sys

manifest = json.loads(sys.argv[1])
collisions = sorted(set(manifest["dependencies"]) & set(sys.modules))
if collisions:
    raise RuntimeError("signed dependency name already loaded: " + ",".join(collisions))
script_entry = manifest["script"]
script = script_entry["path"]
if sys.argv[2] != script:
    raise RuntimeError("signed launcher path mismatch")
sys.argv = sys.argv[2:]

def verified_source(entry):
    raw = pathlib.Path(entry["path"]).read_bytes()
    if hashlib.sha256(raw).hexdigest() != entry["sha256"]:
        raise RuntimeError("signed source digest mismatch")
    return raw

class SignedSourceLoader:
    def __init__(self, entry):
        self.entry = entry

    def create_module(self, spec):
        return None

    def exec_module(self, module):
        raw = verified_source(self.entry)
        module.__file__ = self.entry["path"]
        module.__cached__ = None
        exec(compile(raw, self.entry["path"], "exec"), module.__dict__)

class SignedSourceFinder:
    def find_spec(self, fullname, path=None, target=None):
        entry = manifest["dependencies"].get(fullname)
        if entry is None:
            return None
        return importlib.util.spec_from_loader(
            fullname,
            SignedSourceLoader(entry),
            origin=entry["path"],
        )

sys.meta_path.insert(0, SignedSourceFinder())
raw = verified_source(script_entry)
scope = {
    "__name__": "__main__",
    "__file__": script,
    "__package__": None,
    "__cached__": None,
}
exec(compile(raw, script, "exec"), scope)
"""
def _registration_security_paths() -> set[Path]:
    home = _FIXED_HOME
    harness_roots = (
        home / ".claude",
        home / ".codex",
        home / ".hermes",
        home / ".omp/agent",
        home / ".prime/agent",
    )
    paths = {
        home / ".claude/settings.json",
        home / ".codex/hooks.json",
        home / ".hermes/config.yaml",
        home / ".hermes/shell-hooks-allowlist.json",
        home / ".hermes/hooks/rig-loop-gate",
        home / ".omp/agent/config.yml",
        home / ".omp/agent/extensions/rig-loop-hooks.ts",
        home / ".prime/agent/extensions/rig-loop-hooks.ts",
    }
    for root in harness_roots:
        paths.add(root / "skills/rig-determinism-85")
        paths.add(root / "skills/rig-lattice-system")
    return paths

def _registration_identity_files() -> set[Path]:
    home = _FIXED_HOME
    harness_roots = (
        home / ".claude",
        home / ".codex",
        home / ".hermes",
        home / ".omp/agent",
        home / ".prime/agent",
    )
    files = {
        home / ".claude/settings.json",
        home / ".codex/hooks.json",
        home / ".hermes/config.yaml",
        home / ".hermes/shell-hooks-allowlist.json",
        home / ".hermes/hooks/rig-loop-gate/handler.py",
        home / ".hermes/hooks/rig-loop-gate/HOOK.yaml",
        home / ".omp/agent/config.yml",
        home / ".omp/agent/extensions/rig-loop-hooks.ts",
        home / ".prime/agent/extensions/rig-loop-hooks.ts",
    }
    for root in harness_roots:
        d85 = root / "skills/rig-determinism-85"
        lattice = root / "skills/rig-lattice-system"
        files.update({
            d85 / "d85.py",
            d85 / "d85_gates.py",
            d85 / "d85_admission.py",
            d85 / "tool_selection.py",
            d85 / "bin/rig-determinism-85",
            lattice / "bin/rig-lattice",
            lattice / "rig_lattice/system/build_contract.py",
        })
    return files



def _repository_root(skill_root: Path) -> Path:
    installed_roots = (
        _FIXED_HOME / ".claude/skills",
        _FIXED_HOME / ".codex/skills",
        _FIXED_HOME / ".hermes/skills",
        _FIXED_HOME / ".omp/agent/skills",
        _FIXED_HOME / ".prime/agent/skills",
    )
    if any(skill_root.is_relative_to(root) for root in installed_roots):
        return (_FIXED_HOME / "Developer/rig-capabilities").resolve()
    return skill_root.parents[2]
_POLICY_SKILL_ROOT = Path(__file__).resolve().parent
_POLICY_REPOSITORY = _repository_root(_POLICY_SKILL_ROOT)
_POLICY_FILES = (
    _POLICY_SKILL_ROOT / "d85.py",
    _POLICY_SKILL_ROOT / "d85_gates.py",
    _POLICY_SKILL_ROOT / "d85_admission.py",
    _POLICY_SKILL_ROOT / "tool_selection.py",
    D85_CLI,
    Path(_FIXED_PYTHON),
    _config_path,
    _POLICY_REPOSITORY / "bin/rig-loop",
    _POLICY_REPOSITORY / "rig_capabilities/__init__.py",
    _POLICY_REPOSITORY / "rig_capabilities/loops.py",
    _POLICY_REPOSITORY / "rig_capabilities/d85_admission.py",
    _POLICY_REPOSITORY / "capabilities/hooks/rig-loop-hooks.ts",
    _POLICY_REPOSITORY / "capabilities/hooks/rig-hermes-pre-tool.py",
    _POLICY_REPOSITORY / "capabilities/hooks/rig-pre-tool-guard.py",
    _POLICY_REPOSITORY / "capabilities/hooks/rig-loop-hook.sh",
)




def _static_security_roots() -> set[Path]:
    skill_root = Path(__file__).resolve().parent
    repository = _repository_root(skill_root)
    return {
        _d85_home().resolve(),
        repository / "rig_capabilities",
        skill_root,
        skill_root.parent / "rig-lattice-system",
        repository / "bin/rig-loop",
        repository / "rig_capabilities/__init__.py",
        repository / "rig_capabilities/loops.py",
        repository / "rig_capabilities/d85_admission.py",
        repository / "capabilities/hooks/rig-loop-hooks.ts",
        repository / "capabilities/hooks/rig-hermes-pre-tool.py",
        repository / "capabilities/hooks/rig-pre-tool-guard.py",
        repository / "capabilities/hooks/rig-loop-hook.sh",
        *_registration_security_paths(),
    }
ADMISSION_SCHEMA = "rig.d85.admission.v2"

_SAFE_LAUNCHER_STDLIB = frozenset({
    "__future__", "base64", "binascii", "csv", "dataclasses", "datetime",
    "decimal", "enum", "fractions", "hashlib", "hmac", "io", "itertools",
    "json", "math", "os", "pathlib", "re", "socket", "statistics", "struct",
    "subprocess", "sys", "time", "zoneinfo",
})
_SAFE_STDLIB_FROM_IMPORTS = {
    "__future__": frozenset({"annotations"}),
    "pathlib": frozenset({
        "Path", "PosixPath", "PurePath", "PurePosixPath",
        "PureWindowsPath", "WindowsPath",
    }),
}
_STDLIB_MODULE_NAMES = frozenset(
    getattr(sys, "stdlib_module_names", ())
) | frozenset(sys.builtin_module_names)
_DYNAMIC_LOADER_ROOTS = frozenset({
    "builtins", "cffi", "ctypes", "importlib", "marshal", "pkgutil", "runpy",
    "zipimport",
})

READ_ONLY_TOOLS = frozenset({"read", "read_file", "grep", "glob", "web_search", "ask", "todo"})
WRITE_TOOLS = frozenset({
    "write", "edit", "multiedit", "multi_edit", "notebookedit", "notebook_edit",
    "apply_patch", "applypatch", "str_replace_editor", "create_file", "write_file", "patch",
})
SHELL_TOOLS = frozenset({"bash", "shell", "run_command", "exec", "terminal", "execute_command"})
CODE_TOOLS = frozenset({"eval", "python", "python_repl", "execute_code", "run_code", "code_interpreter"})
NATIVE_TOOL_CAPABILITIES = {
    **dict.fromkeys(READ_ONLY_TOOLS, "read"),
    **dict.fromkeys(WRITE_TOOLS, "write"),
    **dict.fromkeys(SHELL_TOOLS, "shell"),
    **dict.fromkeys(CODE_TOOLS, "execute"),
    "task": "delegate",
    "hub": "delegate",
}
MUTATION_TOOLS = WRITE_TOOLS | SHELL_TOOLS | CODE_TOOLS

_REDIRECT_RX = re.compile(
    r"(?:\d*<>|\d*>>?|\d*>\||&>>?|>>&|>&)\s*([^\s;&|<>]+)"
)
_TEE_RX = re.compile(r"(?:^|[;&|\s])(?:/usr/bin/)?(?:tee|sed\s+-i(?:\s+'')?)\s+(?:-a\s+)?([^\s;&|<>]+)")

_SHELL_MUTATION_VERBS = {
    "rm", "rmdir", "mv", "cp", "install", "ln", "dd", "rsync", "touch",
    "truncate", "mkdir", "perl", "chmod", "chown", "chflags",
}
_READONLY_FIRST = {
    "cat", "ls", "head", "tail", "wc", "grep", "rg", "stat",
    "diff", "cmp", "echo", "printf", "true", "false", "which", "type",
    "basename", "dirname", "readlink", "realpath", "cut", "tr",
    "jq", "column", "seq", "printenv", "ps", "pgrep", "id", "uname",
    "whoami", "nproc", "test", "[", "pwd", ":", "md5sum", "sha1sum",
    "sha256sum", "shasum", "b2sum",
}
_CLAUSE_RX = re.compile(r"[;|&]{1,2}|[\r\n]+")
_SHELL_BUILTINS = {"echo", "printf", "true", "false", "pwd", "test", "[", ":", "type", "command"}
_FIXED_SYSTEM_COMMAND_DIRS = {"/bin", "/usr/bin", "/usr/sbin"}
def _fixed_shell_verb(token: str) -> str | None:
    if token in _SHELL_BUILTINS:
        return token
    candidate = Path(token)
    if (
        not candidate.is_absolute()
        or os.path.normpath(token) != token
        or str(candidate.parent) not in _FIXED_SYSTEM_COMMAND_DIRS
    ):
        return None
    return candidate.name



def _shell_analysis(command: str, cwd: str | None) -> tuple[list[str], list[str], bool]:
    """Extract exact writes; anything dynamically resolved remains unproven."""
    writes: list[str] = []
    unknown: list[str] = []
    has_unproven = False
    for rx in (_REDIRECT_RX, _TEE_RX):
        for raw in rx.findall(command):
            if raw in ("/dev/null",) or raw.startswith("&"):
                continue
            if any(marker in raw for marker in ("$", "`", "*", "?", "[", "]")):
                has_unproven = True
                continue
            writes.append(_abs(raw, cwd))
    if any(marker in command for marker in ("$(", "`", "<(", ">(", "{", "}")):
        has_unproven = True
    if ">" in command and any(marker in command for marker in ("'", '"', "\\")):
        has_unproven = True
    for clause in _CLAUSE_RX.split(command):
        try:
            tokens = shlex.split(clause, posix=True)
        except ValueError:
            has_unproven = True
            continue
        if not tokens:
            continue
        i = 0
        if re.match(r"^[A-Za-z_][A-Za-z0-9_]*=", tokens[0]):
            has_unproven = True
            continue
        verb = _fixed_shell_verb(tokens[0])
        if verb is None:
            has_unproven = True
            for token in tokens:
                if "/" in token or token.startswith("~"):
                    unknown.append(_abs(token, cwd))
            continue
        if verb == "env":
            # /usr/bin/env is read-only only when it prints the environment.
            if len(tokens) != 1:
                has_unproven = True
            continue
        if verb == "command":
            if len(tokens) == 3 and tokens[1] in {"-v", "-V"}:
                continue
            has_unproven = True
            continue
        if verb == "find":
            actions = {
                "-delete", "-exec", "-execdir", "-ok", "-okdir",
                "-fprint", "-fprint0", "-fprintf",
            }
            if any(token in actions for token in tokens[1:]):
                has_unproven = True
            continue
        if verb == "sort":
            outputs: list[str] = []
            index = 1
            while index < len(tokens):
                token = tokens[index]
                if token in {"-o", "--output"}:
                    index += 1
                    if index >= len(tokens):
                        has_unproven = True
                        break
                    outputs.append(tokens[index])
                elif token.startswith("--output="):
                    outputs.append(token.split("=", 1)[1])
                elif token.startswith("-") and "o" in token[1:]:
                    suffix = token[token.index("o") + 1:]
                    if suffix:
                        outputs.append(suffix)
                    else:
                        index += 1
                        if index >= len(tokens):
                            has_unproven = True
                            break
                        outputs.append(tokens[index])
                elif token.startswith("-"):
                    has_unproven = True
                index += 1
            if len(outputs) > 1:
                has_unproven = True
            elif outputs:
                writes.append(_abs(outputs[0], cwd))
            continue
        if verb in {"perl", "sed", "rsync"}:
            has_unproven = True
            continue
        if verb == "dd":
            outputs = [token[3:] for token in tokens[1:] if token.startswith("of=")]
            if len(outputs) != 1 or any(
                marker in outputs[0] for marker in ("$", "`", "*", "?", "[", "]")
            ):
                has_unproven = True
            else:
                writes.append(_abs(outputs[0], cwd))
            continue
        if verb in _SHELL_MUTATION_VERBS:
            operands: list[str] = []
            after_separator = False
            for token in tokens[1:]:
                if not after_separator and token == "--":
                    after_separator = True
                    continue
                if not after_separator and token.startswith("-"):
                    has_unproven = True
                    continue
                if any(marker in token for marker in ("$", "`", "*", "?", "[", "]")):
                    has_unproven = True
                    continue
                operands.append(token)
            if verb in {"cp", "install"}:
                if len(operands) != 2:
                    has_unproven = True
                elif operands:
                    writes.append(_abs(operands[-1], cwd))
            elif verb in {"mv", "ln"}:
                # ln hardlinks expose the source inode through the destination:
                # later writes through the link mutate the source bytes, so both
                # operands are write targets.
                if len(operands) != 2:
                    has_unproven = True
                else:
                    writes.extend(_abs(value, cwd) for value in operands)
            else:
                if not operands:
                    has_unproven = True
                writes.extend(_abs(value, cwd) for value in operands)
            continue
        if verb == "git":
            # Git reads can refresh the index, invoke filters/pagers, and accept
            # output-bearing options. Use the dedicated Git surface instead.
            has_unproven = True
            continue
        if verb in _READONLY_FIRST:
            continue
        has_unproven = True
        for token in tokens:
            if not token.startswith(("-", "$", "&", "(", ")")) and (
                "/" in token or token.startswith("~")
            ):
                unknown.append(_abs(token, cwd))
    return writes, unknown, has_unproven


class AdmissionDenied(Exception):
    """Fail-closed denial carrying the operator-facing reason."""
class _BypassLedgerUnreadable(AdmissionDenied):
    """Existing audit history is malformed; no later row may be appended."""





def _shell_dynamic_execution(command: str) -> bool:
    if any(marker in command for marker in ("$", "`", "<(", ">(", "{", "}")):
        return True
    if ">" in command and any(marker in command for marker in ("'", '"', "\\")):
        return True
    for clause in _CLAUSE_RX.split(command):
        try:
            tokens = shlex.split(clause, posix=True)
        except ValueError:
            return True
        if not tokens:
            continue
        if re.match(r"^[A-Za-z_][A-Za-z0-9_]*=", tokens[0]):
            return True
        verb = _fixed_shell_verb(tokens[0])
        if verb is None:
            return True
        if verb == "env" and len(tokens) != 1:
            return True
        if verb == "command" and not (
            len(tokens) == 3 and tokens[1] in {"-v", "-V"}
        ):
            return True
        if verb in {
            "sh", "bash", "zsh", "dash", "python", "python3", "perl",
            "ruby", "node",
        }:
            return True
        if verb == "find" and any(
            token in {
                "-delete", "-exec", "-execdir", "-ok", "-okdir",
                "-fprint", "-fprint0", "-fprintf",
            }
            for token in tokens[1:]
        ):
            return True
        if verb in _SHELL_MUTATION_VERBS and any(
            any(marker in token for marker in ("*", "?", "[", "]", "{", "}"))
            for token in tokens[1:]
        ):
            return True
    return False
# ---------------------------------------------------------------- config

def _config_object(pairs: list[tuple[str, object]]) -> dict:
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"duplicate configuration key: {key}")
        result[key] = value
    return result


def _validated_config(raw: object) -> dict:
    """Schema/integrity validation of a raw enforcement-config object. Raises
    ValueError on any deviation. Shared by `load_config` and the turn-gate
    approve path, so a gate can never be minted over a config the loader
    would later reject."""
    try:
        allowed_keys = {"roots", "ttl_hours", "launcher_epoch", "tool_capabilities", "turn_gate"}
        required_keys = {"roots", "ttl_hours", "launcher_epoch"}
        if not isinstance(raw, dict) or set(raw) - allowed_keys or required_keys - set(raw):
            raise ValueError(
                "config must contain exactly roots, ttl_hours, launcher_epoch, "
                "and optional tool_capabilities and turn_gate")
        if not isinstance(raw["roots"], list) or not raw["roots"]:
            raise ValueError("roots must contain at least one protected production path")
        roots: list[str] = []
        for root in raw["roots"]:
            if (
                not isinstance(root, str)
                or not root.strip()
                or any(ord(character) < 32 or ord(character) == 127 for character in root)
            ):
                raise ValueError("every protected root must be a nonempty path")
            if root == "~":
                path = _FIXED_HOME
            elif root.startswith("~/"):
                path = _FIXED_HOME / root[2:]
            else:
                path = Path(root)
                if not path.is_absolute():
                    raise ValueError("protected roots must be absolute or ~/ home-relative")
            roots.append(str(path.resolve(strict=False)))
        if len(set(roots)) != len(roots):
            raise ValueError("protected roots must be unique after canonicalization")
        ttl = raw["ttl_hours"]
        if isinstance(ttl, bool) or not isinstance(ttl, (int, float)):
            raise ValueError("ttl_hours must be a number")
        if not math.isfinite(ttl) or ttl <= 0 or ttl * 3600 > MAX_LIFETIME_SECONDS:
            raise ValueError("ttl_hours must be finite, positive, and at most 24")
        epoch = raw["launcher_epoch"]
        if (
            isinstance(epoch, bool)
            or not isinstance(epoch, (int, float))
            or not math.isfinite(float(epoch))
            or float(epoch) < 0
        ):
            raise ValueError("launcher_epoch must be a finite nonnegative Unix timestamp")
        declared = raw.get("tool_capabilities", {})
        if not isinstance(declared, dict):
            raise ValueError("tool_capabilities must be a host-owned object")
        capabilities = {}
        for name, kind in declared.items():
            if not isinstance(name, str) or not name.strip() or kind not in ("read", "write", "shell", "execute", "delegate"):
                raise ValueError("invalid tool capability declaration")
            normalized = name.strip().lower().replace("-", "_")
            if normalized in capabilities:
                raise ValueError("tool capability names collide after normalization")
            if normalized in NATIVE_TOOL_CAPABILITIES and kind != NATIVE_TOOL_CAPABILITIES[normalized]:
                raise ValueError("native tool capabilities cannot be weakened or reclassified")
            capabilities[normalized] = kind
        gate_raw = raw.get("turn_gate")
        turn_gate: dict | None = None
        if gate_raw is not None:
            if not isinstance(gate_raw, dict) or set(gate_raw) != {
                "process_id", "items_file", "items_file_sha256"
            }:
                raise ValueError(
                    "turn_gate must contain exactly process_id, items_file, items_file_sha256")
            pid = gate_raw["process_id"]
            if not isinstance(pid, str) or not re.fullmatch(r"[a-z0-9][a-z0-9_]{0,63}", pid):
                raise ValueError("turn_gate.process_id must be a lowercase process identifier")
            digest = gate_raw["items_file_sha256"]
            if not isinstance(digest, str) or not re.fullmatch(r"[0-9a-f]{64}", digest):
                raise ValueError("turn_gate.items_file_sha256 must be a lowercase digest")
            raw_file = gate_raw["items_file"]
            if not isinstance(raw_file, str) or not raw_file.strip():
                raise ValueError("turn_gate.items_file must be a nonempty path")
            gate_path = Path(raw_file)
            if not gate_path.is_absolute():
                raise ValueError("turn_gate.items_file must be absolute")
            resolved_gate = gate_path.resolve(strict=False)
            authority_home = _d85_home().resolve(strict=False)
            if not str(resolved_gate).startswith(str(authority_home).rstrip(os.sep) + os.sep):
                raise ValueError("turn_gate.items_file must live inside the D85 authority home")
            turn_gate = {
                "process_id": pid,
                "items_file": str(resolved_gate),
                "items_file_sha256": digest,
            }
        return {
            "roots": sorted(set(roots)),
            "ttl_hours": float(ttl),
            "launcher_epoch": float(epoch),
            "tool_capabilities": capabilities,
            "turn_gate": turn_gate,
        }
    except Exception as exc:
        raise ValueError(f"invalid enforcement config: {_safe_error(exc)}") from exc


def load_config() -> dict:
    try:
        raw = json.loads(
            _config_path().read_text(encoding="utf-8"),
            object_pairs_hook=_config_object,
        )
    except FileNotFoundError:
        raise AdmissionDenied(
            f"[d85] enforcement config missing: {_config_path()} (needs exact roots[], ttl_hours, and launcher_epoch fields). "
            "Mutations of production surfaces are blocked until it exists — fail closed.")
    except Exception as exc:
        raise AdmissionDenied(
            f"[d85] enforcement config unreadable ({_safe_error(exc)}) — mutations blocked, fail closed.")
    try:
        return _validated_config(raw)
    except Exception as exc:
        raise AdmissionDenied(
            f"[d85] enforcement config unreadable ({_safe_error(exc)}) — mutations blocked, fail closed.")

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


def _output_binding(path: str) -> dict:
    target = Path(path)
    if target.is_symlink():
        raise AdmissionDenied(f"[d85] output path may not be a symbolic link: {path}")
    anchor = target if target.exists() else target.parent
    while not anchor.exists() and anchor.parent != anchor:
        anchor = anchor.parent
    try:
        info = anchor.lstat()
    except OSError as exc:
        raise AdmissionDenied(f"[d85] cannot bind output path {path}: {exc}") from exc
    if anchor.is_symlink() or not anchor.resolve().is_dir() and anchor != target:
        raise AdmissionDenied(f"[d85] output anchor is not a stable directory: {anchor}")
    if target.exists() and (not target.is_file() or info.st_nlink != 1):
        raise AdmissionDenied(
            f"[d85] existing output must be one singly-linked regular file: {path}")
    return {
        "path": str(target),
        "anchor": str(anchor.resolve()),
        "anchor_device": info.st_dev,
        "anchor_inode": info.st_ino,
        "target_exists": target.exists(),
    }


def _output_bindings_unchanged(record: dict) -> None:
    expected = record.get("output_bindings")
    paths = [str(value) for value in record.get("paths", [])]
    if not isinstance(expected, dict) or sorted(expected) != sorted(paths):
        raise AdmissionDenied("[d85] signed admission lacks exact output path bindings")
    for path in paths:
        if expected[path] != _output_binding(path):
            raise AdmissionDenied(f"[d85] output path binding changed after approval: {path}")

def _launcher_dependency_digests(script: Path) -> dict[str, str]:
    root = script.parent.resolve()
    pending = [script.resolve()]
    visited: set[Path] = set()
    dependencies: dict[str, str] = {}
    total_bytes = 0
    while pending:
        path = pending.pop()
        if path in visited:
            continue
        visited.add(path)
        if len(visited) > MAX_LAUNCHER_DEPENDENCIES:
            raise AdmissionDenied("[d85] launcher dependency graph exceeds its file ceiling")
        try:
            raw = path.read_bytes()
            if len(raw) > MAX_LAUNCHER_SOURCE_BYTES:
                raise ValueError(f"source exceeds {MAX_LAUNCHER_SOURCE_BYTES} bytes")
            tree = ast.parse(raw.decode("utf-8"), filename=str(path))
            total_bytes += len(raw)
            if total_bytes > MAX_LAUNCHER_DEPENDENCY_BYTES:
                raise ValueError(
                    f"dependency graph exceeds {MAX_LAUNCHER_DEPENDENCY_BYTES} bytes")
        except (OSError, UnicodeDecodeError, SyntaxError, ValueError) as exc:
            raise AdmissionDenied(f"[d85] launcher dependency is unreadable: {path}: {exc}") from exc
        module_aliases: dict[str, str] = {}
        symbol_aliases: dict[str, str] = {}
        for import_node in ast.walk(tree):
            if isinstance(import_node, ast.Import):
                for alias in import_node.names:
                    module_aliases[
                        alias.asname or alias.name.split(".", 1)[0]
                    ] = alias.name
            elif isinstance(import_node, ast.ImportFrom) and import_node.module:
                top_level = import_node.module.split(".", 1)[0]
                if top_level in _STDLIB_MODULE_NAMES:
                    allowed_exports = _SAFE_STDLIB_FROM_IMPORTS.get(
                        import_node.module, frozenset())
                    if any(
                        alias.name not in allowed_exports
                        for alias in import_node.names
                    ):
                        raise AdmissionDenied(
                            f"[d85] launcher imports non-allowlisted stdlib symbol from {import_node.module!r}")
                for alias in import_node.names:
                    symbol_aliases[alias.asname or alias.name] = (
                        f"{import_node.module}.{alias.name}")

        def resolved_reference(expression: ast.AST) -> str:
            if isinstance(expression, ast.Name):
                return symbol_aliases.get(
                    expression.id,
                    module_aliases.get(expression.id, expression.id),
                )
            if isinstance(expression, ast.Attribute):
                prefix = resolved_reference(expression.value)
                return f"{prefix}.{expression.attr}" if prefix else ""
            return ""

        parents = {
            child: parent
            for parent in ast.walk(tree)
            for child in ast.iter_child_nodes(parent)
        }
        module_values = set(module_aliases.values())
        forbidden_references = {
            "__import__", "breakpoint", "compile", "delattr", "eval", "exec",
            "filter", "getattr", "globals", "input", "itertools.starmap",
            "locals", "map", "open", "setattr", "vars", "sys.meta_path",
            "sys.modules", "sys.path", "sys.path_hooks",
            "sys.path_importer_cache",
        }
        local_callable_names = {
            node.name
            for node in ast.walk(tree)
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef))
        }
        for node in ast.walk(tree):
            if isinstance(node, ast.Name) and node.id == "__builtins__":
                raise AdmissionDenied(
                    "[d85] launcher cannot access the dynamic builtins namespace")
            if isinstance(node, ast.Attribute) and (
                node.attr.startswith("_")
                or node.attr in {
                    "builtins", "ctypes", "importlib", "os", "posix",
                    "runpy", "subprocess", "sys",
                }
            ):
                raise AdmissionDenied(
                    f"[d85] launcher cannot use reflective/internal attribute {node.attr!r}")
            reference = resolved_reference(node)
            if isinstance(node, ast.Call):
                if isinstance(node.func, ast.Name):
                    if (
                        node.func.id not in dir(builtins)
                        and node.func.id not in local_callable_names
                        and node.func.id not in symbol_aliases
                    ):
                        raise AdmissionDenied(
                            f"[d85] launcher calls dynamically resolved value {node.func.id!r}")
                elif not isinstance(node.func, ast.Attribute):
                    raise AdmissionDenied(
                        "[d85] launcher uses dynamic callable indirection")
            if reference in forbidden_references:
                raise AdmissionDenied(
                    f"[d85] launcher references unbound execution machinery: {reference}")
            if reference in module_values:
                parent = parents.get(node)
                if not (
                    isinstance(parent, ast.Attribute)
                    and parent.value is node
                ):
                    raise AdmissionDenied(
                        f"[d85] launcher module reference escapes static attribute analysis: {reference}")
            if reference.startswith("sys.") and not reference.startswith(
                ("sys.argv", "sys.executable", "sys.stderr", "sys.stdout", "sys.version")
            ):
                raise AdmissionDenied(
                    f"[d85] launcher references unsafe interpreter state: {reference}")
            if reference.startswith("os.") and not reference.startswith(
                ("os.environ", "os.fspath", "os.PathLike")
            ):
                raise AdmissionDenied(
                    f"[d85] launcher references unsafe operating-system machinery: {reference}")
            if re.search(
                r"(?:^|\.)os\.(?:exec|fork|popen|posix_spawn|spawn|startfile|system)",
                reference,
            ):
                raise AdmissionDenied(
                    f"[d85] launcher references nested process execution machinery: {reference}")
            modules: list[str] = []
            if isinstance(node, ast.Import):
                modules = [alias.name for alias in node.names]
            elif isinstance(node, ast.ImportFrom):
                if node.level:
                    raise AdmissionDenied("[d85] launcher dependencies do not permit relative imports")
                if node.module:
                    modules = [node.module]
            for module in modules:
                top_level = module.split(".", 1)[0]
                if top_level in _DYNAMIC_LOADER_ROOTS:
                    raise AdmissionDenied(
                        f"[d85] launcher imports dynamic loader module {top_level!r}")
                if (
                    top_level in _STDLIB_MODULE_NAMES
                    and top_level not in _SAFE_LAUNCHER_STDLIB
                ):
                    raise AdmissionDenied(
                        f"[d85] launcher imports non-allowlisted stdlib module {top_level!r}")
                local_stem = root / top_level
                local_candidates = [
                    Path(str(local_stem) + ".py"),
                    Path(str(local_stem) + ".pyc"),
                ]
                local_candidates.extend(
                    Path(str(local_stem) + suffix)
                    for suffix in importlib.machinery.EXTENSION_SUFFIXES
                )
                has_local_shadow = (
                    local_stem.exists()
                    or any(candidate.exists() for candidate in local_candidates)
                    or (root / "__pycache__").exists()
                )
                if top_level in _SAFE_LAUNCHER_STDLIB:
                    if has_local_shadow:
                        raise AdmissionDenied(
                            f"[d85] launcher-local module shadows stdlib import {module!r}")
                    continue
                if "." in module:
                    raise AdmissionDenied(
                        f"[d85] dotted local import {module!r} requires unbound package initialization")
                candidate = Path(str(local_stem) + ".py")
                competing = [
                    Path(str(local_stem) + ".pyc"),
                    local_stem,
                    *(Path(str(local_stem) + suffix)
                      for suffix in importlib.machinery.EXTENSION_SUFFIXES),
                ]
                if (
                    not candidate.is_file()
                    or any(path.exists() for path in competing)
                    or (root / "__pycache__").exists()
                ):
                    raise AdmissionDenied(
                        f"[d85] launcher import {module!r} is not one exact source-only dependency")
                match = candidate.resolve()
                if not match.is_relative_to(root):
                    raise AdmissionDenied(
                        f"[d85] launcher import {module!r} escapes its launcher root")
                pending.append(match)
                if match != script.resolve():
                    dependencies[str(match)] = hashlib.sha256(
                        match.read_bytes()
                    ).hexdigest()
    return dict(sorted(dependencies.items()))

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
    tool = str(p.get("tool") or "").strip().lower().replace("-", "_")
    if (tool in SHELL_TOOLS or p.get("_capability_kind") == "shell") and p.get("command"):
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
def _assert_single_linked_targets(targets: list[str]) -> None:
    for target in targets:
        path = Path(target)
        try:
            if path.exists() and path.stat().st_nlink > 1:
                raise AdmissionDenied(
                    f"[d85] multiply-linked mutation target cannot be bound lexically: {target}")
        except OSError as exc:
            raise AdmissionDenied(
                f"[d85] mutation target identity is unreadable: {target}: {exc}") from exc
def _path_identity(path: str | os.PathLike[str]) -> tuple[int, int] | None:
    try:
        info = os.stat(path)
    except (OSError, TypeError, ValueError):
        return None
    return info.st_dev, info.st_ino


def _ancestor_identities(
    path: str | os.PathLike[str],
) -> list[tuple[int, int]]:
    """Filesystem identities, deepest existing path/ancestor first."""
    current = Path(path)
    identities: list[tuple[int, int]] = []
    found_existing = False
    while True:
        identity = _path_identity(current)
        if identity is None:
            if found_existing:
                break
        else:
            found_existing = True
            if identity not in identities:
                identities.append(identity)
        parent = current.parent
        if parent == current:
            break
        current = parent
    return identities


def _break_glass_forbidden_paths() -> set[Path]:
    return {
        *_static_security_roots(),
        _d85_home().resolve(strict=False),
        *(
            (item() if item is _config_path else item)
            for item in _POLICY_FILES
        ),
    }


def _projection_path(
    path: str | os.PathLike[str],
) -> tuple[tuple[int, int] | None, tuple[str, ...]]:
    spelling = os.path.normpath(
        os.path.abspath(os.path.expanduser(os.fspath(path))))
    current = Path(spelling)
    suffix: list[str] = []
    while True:
        identity = _path_identity(current)
        if identity is not None:
            return identity, tuple(
                unicodedata.normalize("NFC", component).casefold()
                for component in suffix
            )
        parent = current.parent
        if parent == current:
            return None, tuple(
                unicodedata.normalize("NFC", component).casefold()
                for component in suffix
            )
        suffix.insert(0, current.name)
        current = parent


def _break_glass_forbidden_projections() -> set[
    tuple[tuple[int, int], tuple[str, ...]]
]:
    projections = {
        _projection_path(path)
        for path in _break_glass_forbidden_paths()
    }
    return {
        (identity, suffix)
        for identity, suffix in projections
        if identity is not None and suffix
    }


def _break_glass_forbidden_identities() -> set[tuple[int, int]]:
    authority_paths = _break_glass_forbidden_paths()
    return {
        identity
        for path in authority_paths
        if (identity := _path_identity(path)) is not None
    }


def _identity_chain_within_roots(
    path: str | os.PathLike[str],
    roots: list[str],
) -> list[tuple[int, int]]:
    ancestors = _ancestor_identities(path)
    root_identities = {
        identity
        for root in roots
        if (identity := _path_identity(root)) is not None
    }
    for index, identity in enumerate(ancestors):
        if identity in root_identities:
            return ancestors[:index + 1]
    return []


def _break_glass_path_forbidden(
    path: str | os.PathLike[str],
    roots: list[str],
    forbidden: set[tuple[int, int]] | None = None,
) -> bool:
    if not _identity_chain_within_roots(path, roots):
        return True
    blocked = _break_glass_forbidden_identities() if forbidden is None else forbidden
    if any(identity in blocked for identity in _ancestor_identities(path)):
        return True
    target_identity, target_suffix = _projection_path(path)
    return any(
        target_identity == forbidden_identity
        and len(forbidden_suffix) <= len(target_suffix)
        and target_suffix[:len(forbidden_suffix)] == forbidden_suffix
        for forbidden_identity, forbidden_suffix
        in _break_glass_forbidden_projections()
    )


def _path_within_identity_roots(
    path: str | os.PathLike[str],
    roots: list[str],
) -> bool:
    return bool(_identity_chain_within_roots(path, roots))






def mutation_targets(p: dict) -> list[str]:
    """Back-compat wrapper: write targets only."""
    return mutation_targets_ex(p)[0]


def session_key(p: dict) -> str:
    sid = p.get("session_id")
    if not isinstance(sid, str) or not sid.strip() or any(ord(c) < 32 for c in sid):
        raise AdmissionDenied("[d85] a host-provided session_id is required; cwd is not a session identity")
    return "sid:" + sid.strip()


# ---------------------------------------------------------------- canonical hashing / ledger

def _canonical_bytes(value) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False,
                      allow_nan=False).encode("utf-8")


def _safe_error(exc: BaseException) -> str:
    """Authority-file boundary errors may echo only the exception class name.
    Exception text is attacker-influenced: UnicodeDecodeError reprs embed the
    offending bytes (private key/cert material) and decoder hooks can embed
    parsed content (e.g. duplicate configuration keys)."""
    return type(exc).__name__


def _canonical_hash(value) -> str:
    return hashlib.sha256(_canonical_bytes(value)).hexdigest()


def _fsync_directory(path: Path) -> None:
    descriptor = os.open(path, os.O_RDONLY)
    try:
        os.fsync(descriptor)
    finally:
        os.close(descriptor)


def _load_key() -> bytes:
    path = _key_path()
    try:
        info = path.lstat()
        if (
            path.is_symlink()
            or not stat.S_ISREG(info.st_mode)
            or info.st_nlink != 1
            or info.st_mode & 0o077
            or not path.resolve(strict=True).is_relative_to(_d85_home().resolve())
        ):
            raise ValueError("key must be one private, singly-linked authority file")
        flags = os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0)
        descriptor = os.open(path, flags)
        try:
            current = os.fstat(descriptor)
            if (current.st_dev, current.st_ino) != (info.st_dev, info.st_ino):
                raise ValueError("key identity changed while opening")
            raw = os.read(descriptor, 65).strip()
        finally:
            os.close(descriptor)
        if len(raw) != 64:
            raise ValueError("key must be exactly 32-byte hex")
        key = bytes.fromhex(raw.decode("ascii"))
        if len(key) != 32:
            raise ValueError("key must decode to 32 bytes")
        return key
    except Exception as exc:  # noqa: BLE001
        raise AdmissionDenied(
            f"[d85] admission ledger key unreadable ({_safe_error(exc)}) — mutations blocked, fail closed.")


def _init_ledger() -> bytes:
    directory = _admissions_dir()
    directory.mkdir(parents=True, exist_ok=True)
    if (
        directory.is_symlink()
        or not directory.is_dir()
        or not directory.resolve().is_relative_to(_d85_home().resolve())
    ):
        raise AdmissionDenied("[d85] admission ledger directory escapes authority")
    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL | getattr(os, "O_NOFOLLOW", 0)
    created = False
    try:
        descriptor = os.open(_key_path(), flags, 0o600)
    except FileExistsError:
        pass
    else:
        created = True
        with os.fdopen(descriptor, "wb") as handle:
            handle.write(secrets.token_hex(32).encode("ascii"))
            handle.flush()
            os.fsync(handle.fileno())
    if created:
        _fsync_directory(directory)
    return _load_key()
def _policy_file_identities(*, include_config: bool) -> list[dict]:
    identities = []
    for item in _POLICY_FILES:
        if item is _config_path:
            if not include_config:
                continue
            path = item()
        else:
            path = item
        try:
            resolved = path.resolve(strict=True)
            if not resolved.is_file():
                raise OSError("not a regular file")
            identities.append({
                "path": str(resolved),
                "state": "file",
                "sha256": hashlib.sha256(resolved.read_bytes()).hexdigest(),
            })
        except OSError as exc:
            raise AdmissionDenied(
                f"[d85] policy input is unavailable: {path}: {exc}") from exc
    return identities


def _policy_sha256() -> str:
    identities = _policy_file_identities(include_config=True)
    for path in sorted(_registration_identity_files()):
        if path.is_symlink():
            raise AdmissionDenied(
                f"[d85] registration identity may not be a symlink: {path}")
        if path.is_file():
            identities.append({
                "path": str(path),
                "state": "file",
                "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
            })
        elif path.exists():
            raise AdmissionDenied(
                f"[d85] registration identity has unsupported type: {path}")
        else:
            identities.append({"path": str(path), "state": "absent"})
    return _canonical_hash(identities)


def _verifier_identity_sha256() -> str:
    return _canonical_hash(_policy_file_identities(include_config=False))



def _read_records(path: Path) -> list[dict]:
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except FileNotFoundError:
        return []
    except Exception as exc:  # noqa: BLE001
        raise AdmissionDenied(f"[d85] admission ledger unreadable ({_safe_error(exc)}) — mutations blocked, fail closed.")
    records = []
    for i, line in enumerate(lines):
        if not line.strip():
            continue
        try:
            rec = json.loads(
                line,
                object_pairs_hook=_config_object,
                parse_constant=_reject_constant,
            )
        except (json.JSONDecodeError, ValueError) as exc:
            raise AdmissionDenied(
                f"[d85] admission ledger corrupt "
                f"({path.name} line {i}; {_safe_error(exc)}) — fail closed.") from exc
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
        r = _run_d85([
            "checklist", str(build),
            "--root", str(_inventory_root(build)),
            "--process-id", str(process_id),
        ])
    except Exception as exc:  # noqa: BLE001
        raise AdmissionDenied(f"[d85] bound checklist failed ({_safe_error(exc)}) — mutations blocked, fail closed.")
    if r.returncode != 0:
        raise AdmissionDenied(
            f"[d85] bound build checklist verdict is not a bound CHECKLIST_PASS (exit {r.returncode}) — "
            "re-run the admission flow: admit-request → APPROVE <admission_id> → admit-approve.")
    try:
        cert = json.loads((r.stdout or "").strip().splitlines()[-1])
        build_record = json.loads(build.read_text(encoding="utf-8"))
    except Exception:  # noqa: BLE001
        raise AdmissionDenied(
            "[d85] bound checklist exit 0 but returned no typed certificate — fail closed.")
    certificate_keys = {
        "schema", "verdict", "expected_framework", "inventory_binding",
        "inventory_sha256", "checklist_sha256", "checks",
        "classification_sha256", "realized_sha256",
    }
    if not isinstance(cert, dict) or set(cert) != certificate_keys:
        raise AdmissionDenied(
            "[d85] bound checklist stdout is not one exact v2 score-bound certificate — fail closed.")
    hashes = (
        cert.get("inventory_sha256"),
        cert.get("checklist_sha256"),
        cert.get("classification_sha256"),
        cert.get("realized_sha256"),
    )
    checks = cert.get("checks")
    if (
        cert.get("schema") != "rig.d85.build-checklist.v2"
        or cert.get("verdict") != "CHECKLIST_PASS"
        or cert.get("inventory_binding") != "bound"
        or any(not isinstance(value, str) or not re.fullmatch(r"[0-9a-f]{64}", value)
               for value in hashes)
        or not isinstance(checks, list)
        or not checks
        or any(not isinstance(item, dict) or item.get("pass") is not True for item in checks)
        or cert.get("checklist_sha256") != _canonical_hash(build_record)
    ):
        raise AdmissionDenied(
            "[d85] bound checklist stdout is not one exact v2 score-bound certificate — fail closed.")
    return cert


def _build_unchanged(rec: dict) -> None:
    """Per-mutation freshness: the approved build file's bytes must still hash
    to the digest recorded in the signed approval. Cheap, deterministic, and
    deadlock-free mid-edit: the manifest (paths + build content) was approved
    up front; the enforcement verdict was the bound cert at approve time; a
    fresh bound cert is required again at promotion/execution (d85-run)."""
    build = Path(str(rec.get("build_file", "")))
    if rec.get("policy_sha256") != _policy_sha256():
        raise AdmissionDenied(
            f"[d85] policy changed after approval {rec.get('admission_id')} — admission stale")
    try:
        current = hashlib.sha256(build.read_bytes()).hexdigest()
    except Exception as exc:  # noqa: BLE001
        raise AdmissionDenied(f"[d85] approved build file unreadable: {build} ({exc!r}) — fail closed.")
    if current != rec.get("build_digest"):
        raise AdmissionDenied(
            f"[d85] build file changed after approval {rec.get('admission_id')} — admission stale. "
            "Re-run admit-request → APPROVE → admit-approve for the updated build.")


# ---------------------------------------------------------------- turn gate (per-turn evidence banner)

TURN_ITEMS_SCHEMA = "rig.d85.turn-items.v1"
TURN_CERT_SCHEMA = "rig.d85.turn-cert.v1"
_TURN_ITEMS_KEYS = {"schema", "process_id", "items", "content_sha256"}
_TURN_CERT_KEYS = {"schema", "process_id", "content_sha256", "binding", "signature"}
_TURN_BINDING_KEYS = {
    "build_file", "build_digest", "policy_sha256", "registry_file_sha256",
    "process_file_sha256", "inventory_sha256", "classification_sha256",
    "issued_at", "expires_at",
}
_TURN_ITEM_KEYS = {"id", "text", "when", "proof"}
_TURN_WHEN = {"always", "mutation", "effect"}
_TURN_PROOF = {"none", "admission", "certificate"}
_TURN_MAX_BYTES = 64 * 1024

_SIBLING_MODULES: dict[str, object] = {}


def _sibling_module(name: str):
    """Import a same-directory authority module (d85, d85_gates) in-process.
    A name already loaded from different bytes is a denial, not a fallback."""
    cached = _SIBLING_MODULES.get(name)
    if cached is not None:
        return cached
    target = Path(__file__).resolve().parent / f"{name}.py"
    module = sys.modules.get(name)
    if module is not None:
        if str(getattr(module, "__file__", "")) != str(target):
            raise AdmissionDenied(f"[d85] module name {name} already loaded from different bytes")
    else:
        import importlib.util
        spec = importlib.util.spec_from_file_location(name, target)
        if spec is None or spec.loader is None:
            raise AdmissionDenied(f"[d85] sibling module {name} is unavailable")
        module = importlib.util.module_from_spec(spec)
        sys.modules[name] = module
        try:
            spec.loader.exec_module(module)
        except Exception as exc:  # noqa: BLE001
            sys.modules.pop(name, None)
            raise AdmissionDenied(f"[d85] sibling module {name} failed to load: {exc!r}") from exc
    _SIBLING_MODULES[name] = module
    return module


def _turn_gate_dir() -> Path:
    return _d85_home() / "turn_gate"


def _turn_gate_requests_path() -> Path:
    return _admissions_dir() / "turn_gate_requests.jsonl"


def _turn_gate_claims_dir() -> Path:
    return _turn_gate_dir() / "claims"


def _validate_turn_gate_items(items: list[dict]) -> list[dict]:
    if not isinstance(items, list) or not 1 <= len(items) <= 64:
        raise AdmissionDenied("[d85] turn-gate items must number 1..64")
    cleaned: list[dict] = []
    seen: set[str] = set()
    for item in items:
        if (
            not isinstance(item, dict) or set(item) != _TURN_ITEM_KEYS
            or not isinstance(item["id"], str) or not item["id"].strip() or len(item["id"]) > 64
            or not isinstance(item["text"], str) or not item["text"].strip() or len(item["text"]) > 240
            or item["when"] not in _TURN_WHEN or item["proof"] not in _TURN_PROOF
        ):
            raise AdmissionDenied("[d85] every turn-gate item needs exact id/text/when/proof")
        if item["id"] in seen:
            raise AdmissionDenied(f"[d85] duplicate turn-gate item id {item['id']}")
        seen.add(item["id"])
        cleaned.append({"id": item["id"], "text": item["text"],
                        "when": item["when"], "proof": item["proof"]})
    return cleaned


def _turn_gate_authority(process_id: str) -> dict:
    """Canonical authority freshness: the SAME builders the certification path
    uses — the registry-bound inventory builder (external-module locks, symlink
    and escape rules, declared source bytes) and full reclassification — plus
    raw byte digests of the registry and this process file so edits to other
    registry content cannot hide."""
    d85 = _sibling_module("d85")
    gates = _sibling_module("d85_gates")
    registry_file = d85.AUTHORITY_REGISTRY
    try:
        inventory = d85._build_inventory_from_registry(registry_file, process_id)
        classified = gates.classify_inventory(registry_file, process_id)
        registry_raw = registry_file.read_bytes()
        registry, _ = d85._load_json(registry_file, "AUTHORITY_REGISTRY_MISSING")
        process_path = d85._resolve_relative(
            registry_file.parent.resolve(),
            registry["processes"][process_id], "AUTHORITY_ROOT_ESCAPE")
    except d85.AdmissionBlock as exc:
        raise AdmissionDenied(f"[d85] turn-gate authority inputs invalid: {exc}") from exc
    except (KeyError, TypeError) as exc:
        raise AdmissionDenied(f"[d85] turn-gate authority lookup failed: {exc!r}") from exc
    except OSError as exc:
        raise AdmissionDenied(f"[d85] turn-gate authority bytes unreadable: {exc!r}") from exc
    try:
        process_sha = hashlib.sha256(process_path.read_bytes()).hexdigest()
    except OSError as exc:
        raise AdmissionDenied(f"[d85] turn-gate process file unreadable: {exc!r}") from exc
    return {
        "registry_file_sha256": hashlib.sha256(registry_raw).hexdigest(),
        "process_file_sha256": process_sha,
        "inventory_sha256": str(inventory["inventory_sha256"]),
        "classification_sha256": str(classified["classification_sha256"]),
    }


def _turn_gate_check_dir(directory: Path) -> None:
    if directory.is_symlink():
        raise AdmissionDenied("[d85] turn-gate directory may not be a symlink")
    directory.mkdir(parents=True, exist_ok=True)
    if directory.is_symlink() or not directory.resolve(strict=False).is_relative_to(
            _d85_home().resolve(strict=False)):
        raise AdmissionDenied("[d85] turn-gate directory escapes D85 authority")


def _turn_gate_write_immutable(path: Path, payload: bytes) -> None:
    """Create-only: O_EXCL on the FINAL path. Two racing writers can never
    replace each other's items artifact; the loser gets FileExistsError."""
    _turn_gate_check_dir(path.parent)
    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL | getattr(os, "O_NOFOLLOW", 0)
    try:
        fd = os.open(path, flags, 0o600)
    except FileExistsError as exc:
        raise AdmissionDenied(f"[d85] turn-gate artifact already exists: {path.name}") from exc
    try:
        with os.fdopen(fd, "wb") as handle:
            handle.write(payload)
            handle.flush()
            os.fsync(handle.fileno())
    except Exception:
        path.unlink(missing_ok=True)
        raise
    directory_fd = os.open(path.parent, os.O_RDONLY)
    try:
        os.fsync(directory_fd)
    finally:
        os.close(directory_fd)


def _turn_gate_write_replaceable(path: Path, payload: bytes) -> None:
    """Atomic tmp+replace — only for the certificate, which may be re-minted."""
    _turn_gate_check_dir(path.parent)
    temporary = path.with_name(f".{path.name}.{secrets.token_hex(6)}.tmp")
    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL | getattr(os, "O_NOFOLLOW", 0)
    try:
        fd = os.open(temporary, flags, 0o600)
        with os.fdopen(fd, "wb") as handle:
            handle.write(payload)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, path)
    finally:
        temporary.unlink(missing_ok=True)
    directory_fd = os.open(path.parent, os.O_RDONLY)
    try:
        os.fsync(directory_fd)
    finally:
        os.close(directory_fd)


def _load_turn_items(path: Path, process_id: str, expected_file_sha256: str) -> dict:
    """Immutable item list. The config binds the RAW-FILE digest (policy
    identity); the embedded content_sha256 is the canonical hash over
    {schema, process_id, items} and is checked for self-consistency."""
    if path.is_symlink():
        raise AdmissionDenied("[d85] turn-gate items file may not be a symlink")
    try:
        raw = path.read_bytes()
    except OSError as exc:
        raise AdmissionDenied(f"[d85] turn-gate items file unreadable: {_safe_error(exc)}") from exc
    if hashlib.sha256(raw).hexdigest() != expected_file_sha256:
        raise AdmissionDenied(
            "[d85] turn-gate items bytes differ from the digest bound in the enforcement config")
    if len(raw) > _TURN_MAX_BYTES:
        raise AdmissionDenied("[d85] turn-gate items file exceeds 64KiB")
    try:
        doc = json.loads(raw.decode("utf-8"), object_pairs_hook=_config_object)
    except Exception as exc:  # noqa: BLE001
        raise AdmissionDenied(f"[d85] turn-gate items file is not exact JSON: {_safe_error(exc)}") from exc
    if not isinstance(doc, dict) or set(doc) != _TURN_ITEMS_KEYS:
        raise AdmissionDenied("[d85] turn-gate items keys are not exact")
    if doc.get("schema") != TURN_ITEMS_SCHEMA or doc.get("process_id") != process_id:
        raise AdmissionDenied("[d85] turn-gate items schema or process identity mismatch")
    items = doc["items"]
    if not isinstance(items, list) or not 1 <= len(items) <= 64:
        raise AdmissionDenied("[d85] turn-gate items must number 1..64")
    for item in items:
        if not isinstance(item, dict) or set(item) != _TURN_ITEM_KEYS:
            raise AdmissionDenied("[d85] turn-gate item keys are not exact")
        for field in ("id", "text"):
            value = item[field]
            if not isinstance(value, str) or not value.strip() or len(value) > 240:
                raise AdmissionDenied(f"[d85] turn-gate item {field} is invalid")
        if item["when"] not in _TURN_WHEN or item["proof"] not in _TURN_PROOF:
            raise AdmissionDenied("[d85] turn-gate item when/proof outside closed sets")
    if doc.get("content_sha256") != _canonical_hash(
            {"schema": doc["schema"], "process_id": doc["process_id"], "items": doc["items"]}):
        raise AdmissionDenied("[d85] turn-gate items content_sha256 is not self-consistent")
    return doc


def _load_turn_cert(process_id: str) -> dict:
    path = _turn_gate_dir() / f"{process_id}.cert.json"
    if path.is_symlink():
        raise AdmissionDenied("[d85] turn-gate certificate may not be a symlink")
    try:
        raw = path.read_bytes()
    except OSError as exc:
        raise AdmissionDenied(f"[d85] turn-gate certificate unreadable: {_safe_error(exc)}") from exc
    if len(raw) > _TURN_MAX_BYTES:
        raise AdmissionDenied("[d85] turn-gate certificate exceeds 64KiB")
    try:
        doc = json.loads(raw.decode("utf-8"), object_pairs_hook=_config_object)
    except Exception as exc:  # noqa: BLE001
        raise AdmissionDenied(f"[d85] turn-gate certificate is not exact JSON: {_safe_error(exc)}") from exc
    if not isinstance(doc, dict) or set(doc) != _TURN_CERT_KEYS:
        raise AdmissionDenied("[d85] turn-gate certificate keys are not exact")
    if doc.get("schema") != TURN_CERT_SCHEMA or doc.get("process_id") != process_id:
        raise AdmissionDenied("[d85] turn-gate certificate process/schema mismatch")
    binding = doc.get("binding")
    if not isinstance(binding, dict) or set(binding) != _TURN_BINDING_KEYS:
        raise AdmissionDenied("[d85] turn-gate certificate binding keys are not exact")
    for key in ("build_digest", "policy_sha256", "registry_file_sha256",
                "process_file_sha256", "inventory_sha256", "classification_sha256"):
        value = binding[key]
        if not isinstance(value, str) or not re.fullmatch(r"[0-9a-f]{64}", value):
            raise AdmissionDenied(f"[d85] turn-gate binding {key} must be a lowercase digest")
    build_file = binding["build_file"]
    if not isinstance(build_file, str) or not build_file.strip():
        raise AdmissionDenied("[d85] turn-gate binding build_file must be a nonempty path")
    issued, expires = binding["issued_at"], binding["expires_at"]
    if (
        any(isinstance(v, bool) or not isinstance(v, (int, float)) for v in (issued, expires))
        or not math.isfinite(float(issued)) or not math.isfinite(float(expires))
        or expires <= issued or expires - issued > MAX_LIFETIME_SECONDS
    ):
        raise AdmissionDenied("[d85] turn-gate binding lifetime is invalid (max 24h)")
    _verify_signature(doc, _load_key())
    return doc


def _turn_cert_fresh(cert: dict, content_sha256: str, process_id: str, now: float) -> None:
    """Per-turn freshness, all in-process: window, policy, build bytes, and the
    full canonical authority set (registry, process file, inventory,
    classification — including external-module locks and source bytes)."""
    if cert["content_sha256"] != content_sha256:
        raise AdmissionDenied("[d85] turn-gate certificate binds different items than the config")
    binding = cert["binding"]
    if not float(binding["issued_at"]) <= now < float(binding["expires_at"]):
        raise AdmissionDenied("[d85] turn-gate certificate is outside its validity window")
    if binding["policy_sha256"] != _policy_sha256():
        raise AdmissionDenied("[d85] policy changed after turn-gate approval — re-run the ceremony")
    build = Path(str(binding["build_file"]))
    try:
        current = hashlib.sha256(build.read_bytes()).hexdigest()
    except Exception as exc:  # noqa: BLE001
        raise AdmissionDenied(f"[d85] turn-gate build file unreadable: {exc!r}") from exc
    if current != binding["build_digest"]:
        raise AdmissionDenied("[d85] build file changed after turn-gate approval — re-run the ceremony")
    live = _turn_gate_authority(process_id)
    for key in ("registry_file_sha256", "process_file_sha256",
                "inventory_sha256", "classification_sha256"):
        if binding[key] != live[key]:
            raise AdmissionDenied(
                f"[d85] authority input {key} changed after turn-gate approval — re-run the ceremony")


def _reject_constant(name: str) -> float:
    raise ValueError(f"non-JSON constant {name!r}")


_REQUEST_IDENTITY_KEYS = {
    "process_id", "build_file", "build_digest", "items_file", "content_sha256",
    "items_file_sha256", "certificate_sha256", "ttl_hours", "nonce",
}
_REQUEST_BASE_KEYS = ({"schema", "request_id", "requested_at", "expires_at", "status"}
                      | _REQUEST_IDENTITY_KEYS)
_REQUEST_CONSUMED_KEYS = _REQUEST_BASE_KEYS | {
    "consumed_at", "approver", "how", "certificate_file", "turn_certificate_sha256",
    "turn_gate_installed", "turn_gate_preinstalled", "turn_gate_replaced",
    "turn_gate_previous",
}
_HEX64_RX = re.compile(r"[0-9a-f]{64}")
_HEX16_RX = re.compile(r"[0-9a-f]{16}")
_BG_REQUEST_IDENTITY_KEYS = {
    "schema", "action", "session_key", "reason", "paths", "nonce",
    "verifier_sha256", "ttl_seconds", "requested_at", "review_expires_at",
    "salt",
}
_BG_REQUEST_KEYS = _BG_REQUEST_IDENTITY_KEYS | {"admission_id", "status"}
_BG_APPROVAL_KEYS = {
    "schema", "admission_id", "action", "session_key", "reason", "paths",
    "nonce", "verifier_sha256", "request_sha256", "by", "how",
    "issued_at", "expires_at", "signature",
}
_BYPASS_KEYS = {
    "schema", "event_id", "nonce", "occurred_at", "hook_event", "session_key",
    "tool", "request_sha256", "flag_class", "decision", "reason_code",
    "admission_id", "approval_expires_at", "finalizes", "signature",
}
_BYPASS_REASON_CODES = {
    "approved", "flag-invalid", "approval-missing", "approval-not-yet-valid",
    "approval-expired", "approval-session-mismatch", "approval-tampered",
    "ledger-unreadable", "verifier-drift", "key-unreadable",
    "audit-unavailable", "kind-not-authorizable", "target-not-authorizable",
    "runtime-input-immutable",
}




def _bounded_time(value: object) -> bool:
    return (not isinstance(value, bool) and isinstance(value, (int, float))
            and math.isfinite(float(value))
            and 1_000_000_000.0 < float(value) < 4_200_000_000.0)
def _break_glass_session_value(value: object) -> bool:
    return (
        isinstance(value, str)
        and value.startswith("sid:")
        and bool(value[4:].strip())
    )


def _break_glass_reason_value(value: object) -> bool:
    return (
        isinstance(value, str)
        and value == value.strip()
        and 1 <= len(value) <= 512
        and all(ord(char) >= 32 for char in value)
    )
def _validated_break_glass_paths(value: object, where: str) -> list[str]:
    if not isinstance(value, list) or not 1 <= len(value) <= 32:
        raise AdmissionDenied(
            f"[d85] break-glass {where}.paths must contain 1..32 exact paths")
    paths: list[str] = []
    for path in value:
        if (
            not isinstance(path, str)
            or not path
            or not Path(path).is_absolute()
            or path != _abs(path, None)
            or path in paths
        ):
            raise AdmissionDenied(
                f"[d85] break-glass {where}.paths must be unique canonical absolute paths")
        paths.append(path)
    return paths




def _validated_break_glass_request(record: object, where: str) -> dict:
    if not isinstance(record, dict):
        raise AdmissionDenied(f"[d85] break-glass {where}: expected object")
    try:
        _canonical_bytes(record)
    except (TypeError, ValueError) as exc:
        raise AdmissionDenied(
            f"[d85] break-glass {where}: non-canonical value ({_safe_error(exc)})") from exc
    if (
        set(record) != _BG_REQUEST_KEYS
        or record.get("schema") != _BG_REQUEST_SCHEMA
        or record.get("action") != _BG_ACTION
        or record.get("status") != "pending"
    ):
        raise AdmissionDenied(
            f"[d85] break-glass {where}: keys do not match the request schema")
    if not _break_glass_session_value(record["session_key"]):
        raise AdmissionDenied(f"[d85] break-glass {where}.session_key is invalid")
    if not _break_glass_reason_value(record["reason"]):
        raise AdmissionDenied(f"[d85] break-glass {where}.reason is invalid")
    _validated_break_glass_paths(record["paths"], where)
    for key in ("nonce", "salt"):
        if not isinstance(record[key], str) or not _HEX16_RX.fullmatch(record[key]):
            raise AdmissionDenied(f"[d85] break-glass {where}.{key} must be lowercase hex")
    if (
        not isinstance(record["verifier_sha256"], str)
        or not _HEX64_RX.fullmatch(record["verifier_sha256"])
    ):
        raise AdmissionDenied(
            f"[d85] break-glass {where}.verifier_sha256 must be a lowercase digest")
    ttl = record["ttl_seconds"]
    if (
        isinstance(ttl, bool)
        or not isinstance(ttl, (int, float))
        or not math.isfinite(float(ttl))
        or not _BG_MIN_TTL <= float(ttl) <= _BG_MAX_TTL
    ):
        raise AdmissionDenied(
            f"[d85] break-glass {where}.ttl_seconds must be between 60 and 900")
    if (
        not _bounded_time(record["requested_at"])
        or not _bounded_time(record["review_expires_at"])
        or float(record["review_expires_at"])
        != float(record["requested_at"]) + _BG_REVIEW_WINDOW
    ):
        raise AdmissionDenied(f"[d85] break-glass {where}: review window is invalid")
    identity = {key: record[key] for key in _BG_REQUEST_IDENTITY_KEYS}
    if record["admission_id"] != "d85bg_" + _canonical_hash(identity)[:12]:
        raise AdmissionDenied(
            f"[d85] break-glass {where}: admission_id does not match its identity")
    return record


def _validated_break_glass_approval(record: object, where: str) -> dict:
    if not isinstance(record, dict):
        raise AdmissionDenied(f"[d85] break-glass {where}: expected object")
    try:
        _canonical_bytes(record)
    except (TypeError, ValueError) as exc:
        raise AdmissionDenied(
            f"[d85] break-glass {where}: non-canonical value ({_safe_error(exc)})") from exc
    if (
        set(record) != _BG_APPROVAL_KEYS
        or record.get("schema") != _BG_APPROVAL_SCHEMA
        or record.get("action") != _BG_ACTION
    ):
        raise AdmissionDenied(
            f"[d85] break-glass {where}: keys do not match the approval schema")
    if (
        not isinstance(record["admission_id"], str)
        or not re.fullmatch(r"d85bg_[0-9a-f]{12}", record["admission_id"])
        or not _break_glass_session_value(record["session_key"])
        or not _break_glass_reason_value(record["reason"])
        or not isinstance(record["nonce"], str)
        or not _HEX16_RX.fullmatch(record["nonce"])
    ):
        raise AdmissionDenied(f"[d85] break-glass {where}: approval identity is invalid")
    _validated_break_glass_paths(record["paths"], where)
    for key in ("verifier_sha256", "request_sha256", "signature"):
        if not isinstance(record[key], str) or not _HEX64_RX.fullmatch(record[key]):
            raise AdmissionDenied(
                f"[d85] break-glass {where}.{key} must be a lowercase digest")
    if (
        not isinstance(record["by"], str)
        or not record["by"].strip()
        or record["by"] != record["by"].strip()
        or len(record["by"]) > 64
        or any(ord(char) < 32 for char in record["by"])
        or record["how"] not in {"typed-approve", "test-phrase"}
    ):
        raise AdmissionDenied(f"[d85] break-glass {where}: approval ceremony is invalid")
    if (
        not _bounded_time(record["issued_at"])
        or not _bounded_time(record["expires_at"])
        or not _BG_MIN_TTL
        <= float(record["expires_at"]) - float(record["issued_at"])
        <= _BG_MAX_TTL
    ):
        raise AdmissionDenied(f"[d85] break-glass {where}: approval window is invalid")
    return record


def _validated_bypass_row(record: object, where: str) -> dict:
    if not isinstance(record, dict):
        raise AdmissionDenied(f"[d85] break-glass {where}: expected object")
    try:
        _canonical_bytes(record)
    except (TypeError, ValueError) as exc:
        raise AdmissionDenied(
            f"[d85] break-glass {where}: non-canonical value ({_safe_error(exc)})") from exc
    if (
        set(record) != _BYPASS_KEYS
        or record.get("schema") != BYPASS_SCHEMA
        or record.get("hook_event") != "pre-tool"
        or record.get("flag_class") not in {"exact-one", "invalid"}
        or record.get("decision") not in {"enforce", "reservation", "skip"}
        or record.get("reason_code") not in _BYPASS_REASON_CODES
    ):
        raise AdmissionDenied(
            f"[d85] break-glass {where}: keys do not match the audit schema")
    if (
        not isinstance(record["nonce"], str)
        or not _HEX16_RX.fullmatch(record["nonce"])
        or not _bounded_time(record["occurred_at"])
        or not _break_glass_session_value(record["session_key"])
        or not isinstance(record["tool"], str)
        or not record["tool"]
        or record["tool"] != record["tool"].strip().lower().replace("-", "_")
        or not isinstance(record["request_sha256"], str)
        or not _HEX64_RX.fullmatch(record["request_sha256"])
        or not isinstance(record["signature"], str)
        or not _HEX64_RX.fullmatch(record["signature"])
    ):
        raise AdmissionDenied(f"[d85] break-glass {where}: audit identity is invalid")
    admission_id = record["admission_id"]
    if admission_id is not None and (
        not isinstance(admission_id, str)
        or not re.fullmatch(r"d85bg_[0-9a-f]{12}", admission_id)
    ):
        raise AdmissionDenied(f"[d85] break-glass {where}.admission_id is invalid")
    approval_expires_at = record["approval_expires_at"]
    if approval_expires_at is not None and not _bounded_time(approval_expires_at):
        raise AdmissionDenied(
            f"[d85] break-glass {where}.approval_expires_at is invalid")
    finalizes = record["finalizes"]
    if finalizes is not None and (
        not isinstance(finalizes, str)
        or not re.fullmatch(r"d85byp_[0-9a-f]{12}", finalizes)
    ):
        raise AdmissionDenied(
            f"[d85] break-glass {where}.finalizes is invalid")
    if (
        record["decision"] == "reservation"
        and (record["reason_code"] != "approved" or finalizes is not None)
    ):
        raise AdmissionDenied(
            f"[d85] break-glass {where}: reservation shape is invalid")
    if (
        record["decision"] == "skip"
        and (record["reason_code"] != "approved" or finalizes is None)
    ):
        raise AdmissionDenied(
            f"[d85] break-glass {where}: terminal skip shape is invalid")
    if record["decision"] == "enforce" and finalizes is not None:
        raise AdmissionDenied(
            f"[d85] break-glass {where}: enforce rows cannot finalize reservations")
    identity = {
        key: record[key]
        for key in _BYPASS_KEYS
        if key not in {"event_id", "signature"}
    }
    if record["event_id"] != "d85byp_" + _canonical_hash(identity)[:12]:
        raise AdmissionDenied(
            f"[d85] break-glass {where}: event_id does not match its identity")
    return record


def _validated_bypass_sequence(records: list[dict], where: str) -> None:
    reservations: set[str] = set()
    finalized: set[str] = set()
    for record in records:
        decision = record["decision"]
        if decision == "reservation":
            reservations.add(record["event_id"])
        elif decision == "skip":
            reservation_id = record["finalizes"]
            if reservation_id not in reservations or reservation_id in finalized:
                raise AdmissionDenied(
                    f"[d85] break-glass {where}: terminal skip has no unique reservation")
            finalized.add(reservation_id)




def _gate_block_value(value: object) -> bool:
    return value is None or (
        isinstance(value, dict)
        and set(value) == {"process_id", "items_file", "items_file_sha256"}
        and all(isinstance(item, str) and item for item in value.values()))


def _validated_request(record: object, where: str) -> dict:
    """Exact ledger row: exact keys per status, digests lowercase, timestamps
    finite and in range, and request_id RECOMPUTED from the row's own identity —
    an appended row under a copied ID cannot enter the ledger at all."""
    if not isinstance(record, dict):
        raise AdmissionDenied(f"[d85] turn-gate {where}: expected object")
    status = record.get("status")
    if status == "pending":
        expected = _REQUEST_BASE_KEYS
    elif status == "consumed":
        expected = _REQUEST_CONSUMED_KEYS
    else:
        raise AdmissionDenied(f"[d85] turn-gate {where}: unknown status {status!r}")
    if set(record) != expected or record.get("schema") != "rig.d85.turn-gate-request.v1":
        raise AdmissionDenied(f"[d85] turn-gate {where}: keys do not match the request schema")
    for key in ("process_id", "build_file", "items_file", "nonce"):
        if not isinstance(record[key], str) or not record[key]:
            raise AdmissionDenied(f"[d85] turn-gate {where}.{key} must be a nonempty string")
    for key in ("build_digest", "content_sha256", "items_file_sha256", "certificate_sha256"):
        if not isinstance(record[key], str) or not _HEX64_RX.fullmatch(record[key]):
            raise AdmissionDenied(f"[d85] turn-gate {where}.{key} must be a lowercase digest")
    ttl = record["ttl_hours"]
    if (isinstance(ttl, bool) or not isinstance(ttl, (int, float))
            or not math.isfinite(float(ttl))
            or not 60.0 <= float(ttl) * 3600 <= MAX_LIFETIME_SECONDS):
        raise AdmissionDenied(f"[d85] turn-gate {where}.ttl_hours must span one minute to 24 hours")
    if not _bounded_time(record["requested_at"]) or not _bounded_time(record["expires_at"]):
        raise AdmissionDenied(f"[d85] turn-gate {where}: timestamps out of range")
    if float(record["requested_at"]) >= float(record["expires_at"]):
        raise AdmissionDenied(f"[d85] turn-gate {where}: expiry precedes request")
    identity = {key: record[key] for key in _REQUEST_IDENTITY_KEYS}
    if record["request_id"] != "d85gtg_" + _canonical_hash(identity)[:12]:
        raise AdmissionDenied(f"[d85] turn-gate {where}: request_id does not match its identity")
    if status == "consumed":
        if not _bounded_time(record["consumed_at"]):
            raise AdmissionDenied(f"[d85] turn-gate {where}.consumed_at out of range")
        for key in ("approver", "how", "certificate_file"):
            if not isinstance(record[key], str) or not record[key]:
                raise AdmissionDenied(f"[d85] turn-gate {where}.{key} must be a nonempty string")
        turn_cert = record["turn_certificate_sha256"]
        if not isinstance(turn_cert, str) or not _HEX64_RX.fullmatch(turn_cert):
            raise AdmissionDenied(f"[d85] turn-gate {where}.turn_certificate_sha256 must be a digest")
        for key in ("turn_gate_installed", "turn_gate_preinstalled", "turn_gate_replaced"):
            if not isinstance(record[key], bool):
                raise AdmissionDenied(f"[d85] turn-gate {where}.{key} must be boolean")
        if not _gate_block_value(record["turn_gate_previous"]):
            raise AdmissionDenied(f"[d85] turn-gate {where}.turn_gate_previous malformed")
    return record


def _read_turn_gate_requests(*, display: bool = False) -> list[dict]:
    """Append-order ledger, every row exact. Callers get file order so ledger
    position — not wall-clock timestamps — can order supersession. Malformed
    rows are RED for every caller, including a torn final chunk. The ONLY
    exception is the pre-lock pending display (display=True), which skips —
    never truncates — one malformed no-newline tail so a torn append cannot
    blind the operator's scope view; every locked read stays strict, and
    truncation requires the signed minted claim's persisted consumed bytes."""
    try:
        data = _turn_gate_requests_path().read_bytes()
    except FileNotFoundError:
        return []
    except OSError as exc:
        raise AdmissionDenied(f"[d85] turn-gate requests unreadable: {_safe_error(exc)}") from exc
    complete = not data or data.endswith(b"\n")
    chunks = data.split(b"\n")
    torn_tail = b""
    if not complete:
        torn_tail = chunks.pop()
    records: list[dict] = []
    for index, chunk in enumerate(chunks):
        if not chunk.strip():
            continue
        try:
            record = json.loads(chunk.decode("utf-8"), object_pairs_hook=_config_object,
                                parse_constant=_reject_constant)
        except Exception as exc:  # noqa: BLE001
            raise AdmissionDenied(
                f"[d85] turn-gate requests line {index} is not exact JSON: {_safe_error(exc)}") from exc
        validated = _validated_request(record, f"line {index}")
        records.append(validated)
    if torn_tail.strip():
        if not display:
            raise AdmissionDenied(
                "[d85] turn-gate requests end in an incomplete record")
    return records


def _latest_requests_by_id(records: list[dict]) -> dict[str, dict]:
    latest: dict[str, dict] = {}
    for record in records:
        latest[str(record["request_id"])] = record
    return latest


def turn_gate_request(
    build_file: str,
    process_id: str,
    items: list[dict],
    ttl_hours: float = 24,
    *,
    now: float | None = None,
) -> dict:
    """Ceremony step 1: validate, replay the bound checklist, and create the
    immutable items artifact (create-only). Signs no certificate and binds no
    policy hash — the operator installs items_file_sha256 into config between
    request and approve, so approval binds the POST-edit policy."""
    cleaned = _validate_turn_gate_items(items)
    if (
        isinstance(ttl_hours, bool) or not isinstance(ttl_hours, (int, float))
        or not math.isfinite(float(ttl_hours))
        or not 60.0 <= float(ttl_hours) * 3600 <= MAX_LIFETIME_SECONDS
    ):
        raise AdmissionDenied("[d85] turn-gate ttl must span one minute to 24 hours")
    cert = _build_compliant_bound(str(build_file), str(process_id))
    cfg = load_config()
    current_time = time.time() if now is None else float(now)
    if not (_bounded_time(current_time)
            and _bounded_time(current_time + float(ttl_hours) * 3600)):
        raise AdmissionDenied("[d85] turn-gate request clock is out of range")
    build = Path(build_file).resolve(strict=True)
    items_doc = {
        "schema": TURN_ITEMS_SCHEMA,
        "process_id": str(process_id),
        "items": cleaned,
    }
    content_sha = _canonical_hash(items_doc)
    items_doc["content_sha256"] = content_sha
    payload = _canonical_bytes(items_doc) + b"\n"
    file_sha = hashlib.sha256(payload).hexdigest()
    # Content-addressed: a checklist update never requires deleting protected
    # authority bytes — the new items set simply gets a new immutable file, and
    # the config/certificate atomically pin the new path at approval time.
    items_file = _turn_gate_dir() / f"{process_id}.{content_sha[:16]}.items.json"
    if items_file.exists() or items_file.is_symlink():
        try:
            existing = items_file.read_bytes()
        except OSError as exc:
            raise AdmissionDenied(f"[d85] existing turn-gate items unreadable: {_safe_error(exc)}") from exc
        if existing != payload:
            raise AdmissionDenied(
                "[d85] content-addressed turn-gate items file does not match its digest")
    else:
        _turn_gate_write_immutable(items_file, payload)
    identity = {
        "process_id": str(process_id),
        "build_file": str(build),
        "build_digest": hashlib.sha256(build.read_bytes()).hexdigest(),
        "items_file": str(items_file),
        "content_sha256": content_sha,
        "items_file_sha256": file_sha,
        "certificate_sha256": cert["checklist_sha256"],
        "ttl_hours": float(ttl_hours),
        # nonce keeps re-requests of identical inputs distinct: the claim file
        # for a consumed request is permanent, so the ID must never repeat.
        "nonce": secrets.token_hex(8),
    }
    request = {
        "schema": "rig.d85.turn-gate-request.v1",
        "request_id": "d85gtg_" + _canonical_hash(identity)[:12],
        **identity,
        "requested_at": current_time,
        "expires_at": current_time + cfg["ttl_hours"] * 3600,
        "status": "pending",
    }
    _admissions_dir().mkdir(parents=True, exist_ok=True)
    lock_handle = _lock_turn_gate_approval()
    try:
        _reconcile_turn_gate_pending()
        ledger = _turn_gate_requests_path()
        if ledger.exists() and ledger.stat().st_size > 0 \
                and not ledger.read_bytes().endswith(b"\n"):
            raise AdmissionDenied(
                "[d85] ledger ends in an incomplete record — resume the interrupted approval "
                "before new requests (the displayed pending ID is the recoverable one)")
        sidecar = {
            "schema": _TURN_PENDING_SCHEMA,
            "request_id": request["request_id"],
            "payload": request,
        }
        sidecar["signature"] = _claim_signature(sidecar)
        _write_turn_gate_pending(sidecar)
        # Deliberately no cleanup on the failure path: a sidecar surviving a
        # partial append is the only proof that can later justify truncating a
        # torn tail. The next request's reconcile completes it exactly-once;
        # the success path below retires it immediately.
        _append_turn_gate_row(request)
        _unlink_turn_gate_pending(request["request_id"])
    finally:
        fcntl.flock(lock_handle.fileno(), fcntl.LOCK_UN)
        lock_handle.close()
    return request


def _turn_gate_claim_path(request_id: str) -> Path:
    return _turn_gate_claims_dir() / f"{request_id}.claimed"


_TURN_CLAIM_SCHEMA = "rig.d85.turn-gate-claim.v2"
_TURN_CLAIM_STATES = {"claimed", "minted", "sealed"}
_TURN_HOW_VALUES = {"test-phrase", "typed-approve"}
_TURN_CLAIM_BASE_KEYS = {"schema", "request_id", "state", "consumed_at", "approver",
                         "how", "ledger_count", "turn_gate_previous",
                         "turn_gate_preinstalled", "turn_gate_replaced"}
_TURN_CLAIM_SIG_KEYS = {"signature"}
_TURN_CLAIM_MINT_KEYS = {"certificate_sha256", "consumed"}


def _turn_gate_lock_path() -> Path:
    directory = _turn_gate_claims_dir_checked()
    directory.mkdir(parents=True, exist_ok=True)
    return directory / "approval.lock"


def _lock_turn_gate_approval():
    """One GLOBAL exclusive lock held across recheck → config install → mint →
    claim advance → ledger append. The enforcement config's single turn_gate key
    and the shared cert directory are global, not per-request resources. Only
    EWOULDBLOCK is contention; every other failure is fail-closed."""
    path = _turn_gate_lock_path()
    try:
        fd = os.open(path, os.O_RDWR | os.O_CREAT | getattr(os, "O_NOFOLLOW", 0), 0o600)
    except OSError as exc:
        raise AdmissionDenied(
            f"[d85] turn-gate lock path is not safely creatable: {path}: {exc!r}") from exc
    try:
        info = os.fstat(fd)
        if (not stat.S_ISREG(info.st_mode) or info.st_nlink != 1
                or stat.S_IMODE(info.st_mode) != 0o600
                or info.st_uid != os.geteuid()):
            raise AdmissionDenied(
                f"[d85] turn-gate lock file is not a private 0600 regular file: {path}")
        try:
            fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError as exc:
            raise AdmissionDenied(
                "[d85] another turn-gate approval is in progress — retry shortly") from exc
        except OSError as exc:
            raise AdmissionDenied(f"[d85] turn-gate lock failed: {exc!r}") from exc
    except BaseException:
        os.close(fd)
        raise
    return os.fdopen(fd, "a+", encoding="utf-8")


def _turn_gate_claims_dir_checked() -> Path:
    claims = _turn_gate_claims_dir()
    if claims.is_symlink():
        raise AdmissionDenied("[d85] turn-gate claims directory may not be a symlink")
    claims.mkdir(parents=True, exist_ok=True)
    if claims.is_symlink() or not claims.resolve(strict=False).is_relative_to(
            _d85_home().resolve(strict=False)):
        raise AdmissionDenied("[d85] turn-gate claims directory escapes D85 authority")
    return claims


def _turn_gate_torn_tail_present() -> bool:
    """True when the ledger is nonempty and does not end in a newline. This
    is a DISPLAY hint only: it never authorizes truncation (that requires the
    signed minted claim under the lock) and never suppresses strict reads."""
    try:
        data = _turn_gate_requests_path().read_bytes()
    except OSError:
        return False
    return bool(data) and not data.endswith(b"\n")


def _claim_signature(body: dict) -> str:
    """HMAC over the canonical claim body (everything except signature).
    Only the D85 key can mint a valid cursor/approver/consumed payload, so a
    raw writer into claims/ cannot forge supersession state."""
    return hmac.new(_load_key(), _canonical_bytes(body), hashlib.sha256).hexdigest()


def _validated_claim(doc: object, request_id: str) -> dict:
    """Strict claim: exact keys per state (minted adds the certificate digest
    AND the finalized consumed payload), bounded finite timestamps, integer
    ledger cursor, closed how-set, audited config block value, and a valid
    HMAC signature over the body. Anything else is a malformed authority
    record."""
    if not isinstance(doc, dict) or doc.get("schema") != _TURN_CLAIM_SCHEMA:
        raise AdmissionDenied(f"[d85] turn-gate claim record for {request_id} is malformed")
    state = doc.get("state")
    if state not in _TURN_CLAIM_STATES:
        raise AdmissionDenied(f"[d85] turn-gate claim record for {request_id} is malformed")
    keys = set(doc)
    claimed_set = _TURN_CLAIM_BASE_KEYS | _TURN_CLAIM_SIG_KEYS
    minted_set = _TURN_CLAIM_BASE_KEYS | _TURN_CLAIM_MINT_KEYS | _TURN_CLAIM_SIG_KEYS
    if state == "claimed":
        exact = keys == claimed_set
    elif state == "minted":
        exact = keys == minted_set
    else:
        exact = keys in (claimed_set, minted_set)
    if not exact or doc.get("request_id") != request_id:
        raise AdmissionDenied(f"[d85] turn-gate claim record for {request_id} has inexact keys")
    signature = doc["signature"]
    if not isinstance(signature, str) or not _HEX64_RX.fullmatch(signature):
        raise AdmissionDenied(f"[d85] turn-gate claim record for {request_id} is malformed")
    body = {k: v for k, v in doc.items() if k != "signature"}
    if not hmac.compare_digest(signature, _claim_signature(body)):
        raise AdmissionDenied(f"[d85] turn-gate claim signature invalid: {request_id}")
    if not _bounded_time(doc["consumed_at"]):
        raise AdmissionDenied(f"[d85] turn-gate claim timestamp out of range: {request_id}")
    cursor = doc["ledger_count"]
    if isinstance(cursor, bool) or not isinstance(cursor, int) or not 0 <= cursor <= 10_000_000:
        raise AdmissionDenied(f"[d85] turn-gate claim ledger cursor invalid: {request_id}")
    approver, how = doc["approver"], doc["how"]
    signed = (isinstance(approver, str) and approver and len(approver) <= 64
              and how in _TURN_HOW_VALUES)
    if state in ("claimed", "minted"):
        if not signed:
            raise AdmissionDenied(f"[d85] turn-gate claim approver/how invalid: {request_id}")
    elif not (signed or (approver is None and how is None)):
        raise AdmissionDenied(f"[d85] turn-gate claim approver/how invalid: {request_id}")
    if (not isinstance(doc["turn_gate_preinstalled"], bool)
            or not isinstance(doc["turn_gate_replaced"], bool)
            or not _gate_block_value(doc["turn_gate_previous"])):
        raise AdmissionDenied(f"[d85] turn-gate claim config audit fields invalid: {request_id}")
    if "certificate_sha256" in doc:
        cert_sha = doc["certificate_sha256"]
        if not isinstance(cert_sha, str) or not _HEX64_RX.fullmatch(cert_sha):
            raise AdmissionDenied(f"[d85] turn-gate claim certificate digest invalid: {request_id}")
        _validated_request(doc["consumed"], f"claim {request_id} consumed payload")
    return doc


def _read_turn_gate_claim(request_id: str) -> dict | None:
    path = _turn_gate_claim_path(request_id)
    try:
        raw = path.read_bytes()
    except FileNotFoundError:
        return None
    except OSError as exc:
        raise AdmissionDenied(f"[d85] turn-gate claim record unreadable: {_safe_error(exc)}") from exc
    try:
        doc = json.loads(raw.decode("utf-8"), object_pairs_hook=_config_object,
                         parse_constant=_reject_constant)
    except Exception as exc:  # noqa: BLE001
        raise AdmissionDenied(f"[d85] turn-gate claim record malformed: {_safe_error(exc)}") from exc
    return _validated_claim(doc, request_id)


def _claim_turn_gate_request(
    request_id: str, *, state: str = "sealed", when: float | None = None,
    approver: str | None = None, how: str | None = None,
    ledger_count: int | None = None, turn_gate_previous: object = None,
    turn_gate_preinstalled: bool = False, turn_gate_replaced: bool = False
) -> dict:
    claims = _turn_gate_claims_dir_checked()
    body = {"schema": _TURN_CLAIM_SCHEMA, "request_id": request_id, "state": state,
            "consumed_at": time.time() if when is None else float(when),
            "approver": approver, "how": how,
            "ledger_count": len(_read_turn_gate_requests()) if ledger_count is None
            else int(ledger_count),
            "turn_gate_previous": turn_gate_previous,
            "turn_gate_preinstalled": bool(turn_gate_preinstalled),
            "turn_gate_replaced": bool(turn_gate_replaced)}
    claim = _validated_claim({**body, "signature": _claim_signature(body)}, request_id)
    path = _turn_gate_claim_path(request_id)
    temporary = claims / f".{request_id}.{secrets.token_hex(6)}.claim.tmp"
    try:
        fd = os.open(temporary, os.O_WRONLY | os.O_CREAT | os.O_EXCL | getattr(os, "O_NOFOLLOW", 0), 0o600)
        with os.fdopen(fd, "wb") as handle:
            handle.write(_canonical_bytes(claim) + b"\n")
            handle.flush()
            os.fsync(handle.fileno())
        try:
            os.link(temporary, path)  # create-only publish; never a partial final file
        except FileExistsError as exc:
            raise AdmissionDenied(
                f"[d85] turn-gate request {request_id} already consumed — one approval per request") from exc
        directory_fd = os.open(claims, os.O_RDONLY)
        try:
            os.fsync(directory_fd)
        finally:
            os.close(directory_fd)
    finally:
        temporary.unlink(missing_ok=True)
    return claim


def _advance_turn_gate_claim(claim: dict, patch: dict) -> dict:
    body = {k: v for k, v in {**claim, **patch}.items() if k != "signature"}
    updated = _validated_claim({**body, "signature": _claim_signature(body)},
                               str(claim["request_id"]))
    _turn_gate_write_replaceable(
        _turn_gate_claim_path(str(claim["request_id"])), _canonical_bytes(updated) + b"\n")
    return updated


def _recover_turn_gate_consumed_tail(claim: dict) -> bool:
    """Under the global lock only: truncate a torn final ledger chunk when a
    fully signed MINTED claim proves the bytes are a strict prefix of its
    persisted consumed payload. Every other malformed tail remains RED."""
    if claim.get("state") != "minted" or not isinstance(claim.get("consumed"), dict):
        return False
    path = _turn_gate_requests_path()
    try:
        data = path.read_bytes()
    except OSError:
        return False
    if not data or data.endswith(b"\n"):
        return False
    tail = data[data.rfind(b"\n") + 1:]
    line = _canonical_bytes(claim["consumed"]) + b"\n"
    if not tail.strip() or tail == line or not line.startswith(tail):
        return False
    try:
        fd = os.open(path, os.O_WRONLY | getattr(os, "O_NOFOLLOW", 0))
    except OSError as exc:
        raise AdmissionDenied(
            f"[d85] turn-gate ledger tail unrepairable: {_safe_error(exc)}") from exc
    try:
        os.ftruncate(fd, len(data) - len(tail))
        os.fsync(fd)
    finally:
        os.close(fd)
    return True


def _append_turn_gate_row(row: dict) -> None:
    """Durable single-writer append of one COMPLETE row (pending request or
    consumed receipt): O_APPEND, one byte loop, fsync before returning.
    Publish→consumed order is preserved; the banner only goes GREEN once the
    consumed row exists, matches the cert, and binds to the signed claim."""
    line = _canonical_bytes(row) + b"\n"
    path = _turn_gate_requests_path()
    if path.is_symlink():
        raise AdmissionDenied("[d85] turn-gate requests ledger may not be a symlink")
    try:
        fd = os.open(path,
                     os.O_WRONLY | os.O_CREAT | os.O_APPEND | getattr(os, "O_NOFOLLOW", 0),
                     0o600)
    except OSError as exc:
        raise AdmissionDenied(
            f"[d85] turn-gate requests ledger unopenable: {_safe_error(exc)}") from exc
    try:
        info = os.fstat(fd)
        if not stat.S_ISREG(info.st_mode) or info.st_uid != os.getuid():
            raise AdmissionDenied(
                "[d85] turn-gate requests ledger is not a private regular file")
        written = 0
        while written < len(line):
            written += os.write(fd, line[written:])
        os.fsync(fd)
    finally:
        os.close(fd)
def _break_glass_lock_path(name: str) -> Path:
    directory = _admissions_dir()
    directory.mkdir(parents=True, exist_ok=True)
    if (
        directory.is_symlink()
        or not directory.is_dir()
        or not directory.resolve(strict=False).is_relative_to(
            _d85_home().resolve(strict=False)
        )
    ):
        raise AdmissionDenied("[d85] break-glass lock directory escapes authority")
    return directory / name


def _lock_break_glass(name: str, label: str):
    path = _break_glass_lock_path(name)
    try:
        fd = os.open(
            path,
            os.O_RDWR | os.O_CREAT | getattr(os, "O_NOFOLLOW", 0),
            0o600,
        )
    except OSError as exc:
        raise AdmissionDenied(
            f"[d85] {label} lock is not safely creatable ({_safe_error(exc)})") from exc
    try:
        info = os.fstat(fd)
        if (
            not stat.S_ISREG(info.st_mode)
            or info.st_nlink != 1
            or stat.S_IMODE(info.st_mode) != 0o600
            or info.st_uid != os.geteuid()
        ):
            raise AdmissionDenied(
                f"[d85] {label} lock is not a private 0600 regular file")
        fcntl.flock(fd, fcntl.LOCK_EX)
    except BaseException:
        os.close(fd)
        raise
    return os.fdopen(fd, "a+", encoding="utf-8")


def _lock_break_glass_mint():
    return _lock_break_glass("break-glass-mint.lock", "break-glass mint")


def _lock_break_glass_audit():
    return _lock_break_glass("break-glass-audit.lock", "break-glass audit")


def _append_private_row(path: Path, row: dict, label: str) -> None:
    line = _canonical_bytes(row) + b"\n"
    if path.is_symlink():
        raise AdmissionDenied(f"[d85] {label} may not be a symlink")
    flags = os.O_WRONLY | os.O_APPEND | getattr(os, "O_NOFOLLOW", 0)
    created = False
    try:
        try:
            fd = os.open(path, flags | os.O_CREAT | os.O_EXCL, 0o600)
            created = True
        except FileExistsError:
            fd = os.open(path, flags)
    except OSError as exc:
        raise AdmissionDenied(
            f"[d85] {label} unopenable ({_safe_error(exc)})") from exc
    try:
        info = os.fstat(fd)
        if not stat.S_ISREG(info.st_mode) or info.st_uid != os.getuid():
            raise AdmissionDenied(
                f"[d85] {label} is not an owner-controlled regular file")
        written = 0
        while written < len(line):
            count = os.write(fd, line[written:])
            if count <= 0:
                raise OSError("short append")
            written += count
        os.fsync(fd)
        if created:
            _fsync_directory(path.parent)
    except AdmissionDenied:
        raise
    except OSError as exc:
        raise AdmissionDenied(
            f"[d85] {label} append failed ({_safe_error(exc)})") from exc
    finally:
        os.close(fd)


def _append_break_glass_approval(row: dict, key: bytes) -> None:
    _validated_break_glass_approval(row, "approval append")
    _verify_signature(row, key)
    _append_private_row(_approvals_path(), row, "break-glass approval ledger")


def _append_bypass_row(row: dict) -> None:
    """Serialize, validate, append, and fsync one audit row. A torn tail is
    never repaired in-band and therefore disables the bypass."""
    lock_handle = _lock_break_glass_audit()
    try:
        _append_bypass_row_locked(row)
    finally:
        fcntl.flock(lock_handle.fileno(), fcntl.LOCK_UN)
        lock_handle.close()


def _append_bypass_row_locked(row: dict) -> None:
    key = _load_key()
    path = _bypass_ledger_path()
    existing_rows: list[dict] = []
    if not path.exists() or path.is_file():
        try:
            existing_rows = _read_records(path)
            for index, existing in enumerate(existing_rows):
                _validated_bypass_row(existing, f"audit row {index}")
                _verify_signature(existing, key)
            _validated_bypass_sequence(existing_rows, "audit ledger")
        except AdmissionDenied as exc:
            raise _BypassLedgerUnreadable(
                "[d85] break-glass audit ledger is unreadable") from exc
    _validated_bypass_row(row, "audit append")
    _verify_signature(row, key)
    _validated_bypass_sequence([*existing_rows, row], "audit append")
    _append_private_row(path, row, "break-glass audit ledger")




_TURN_PENDING_SCHEMA = "rig.d85.turn-gate-pending.v1"
_TURN_PENDING_KEYS = {"schema", "request_id", "payload", "signature"}


def _turn_gate_pending_path(request_id: str) -> Path:
    return _turn_gate_claims_dir() / f"{request_id}.pending"


def _read_turn_gate_pending(path: Path) -> dict[str, Any] | None:
    """Verified signed pending sidecar, or None when absent/unverifiable. An
    unverifiable sidecar can never prove a tail — it fails closed."""
    try:
        if path.is_symlink() or not path.is_file() or path.stat().st_size > 65536:
            return None
        raw = path.read_bytes()
    except OSError:
        return None
    try:
        doc = json.loads(raw.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError):
        return None
    if not isinstance(doc, dict) or set(doc) != _TURN_PENDING_KEYS:
        return None
    if doc.get("schema") != _TURN_PENDING_SCHEMA:
        return None
    rid = doc.get("request_id")
    if not isinstance(rid, str) or not re.fullmatch(r"d85gtg_[0-9a-f]{12}", rid):
        return None
    payload = doc.get("payload")
    if not isinstance(payload, dict) or payload.get("request_id") != rid:
        return None
    # Full request validation, symmetric with minted claims: an HMAC-valid
    # sidecar whose payload is not a structurally valid pending request is
    # unverifiable and can never prove a tail or enter the ledger.
    try:
        payload = _validated_request(payload, f"pending sidecar {rid}")
    except AdmissionDenied:
        return None
    if payload.get("status") != "pending":
        return None
    signature = doc.get("signature")
    body = {k: v for k, v in doc.items() if k != "signature"}
    if not isinstance(signature, str) or not _HEX64_RX.fullmatch(signature) \
            or not hmac.compare_digest(signature, _claim_signature(body)):
        return None
    return doc


def _write_turn_gate_pending(doc: dict[str, Any]) -> None:
    """Create-only durable write: temp+fsync, link, then fsync the claims
    directory BEFORE returning — the ledger append may not start until the
    sidecar is durable, or a crash could persist a torn tail with no proof."""
    path = _turn_gate_pending_path(str(doc["request_id"]))
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + f".tmp.{os.getpid()}")
    try:
        with tmp.open("x", encoding="utf-8") as handle:
            handle.write(_canonical_bytes(doc).decode("utf-8"))
            handle.flush()
            os.fsync(handle.fileno())
        try:
            os.link(tmp, path)
        except FileExistsError as exc:
            raise AdmissionDenied(
                f"[d85] turn-gate pending sidecar {doc['request_id']} already exists") from exc
        dir_fd = os.open(path.parent, os.O_RDONLY)
        try:
            os.fsync(dir_fd)
        finally:
            os.close(dir_fd)
    finally:
        tmp.unlink(missing_ok=True)


def _unlink_turn_gate_pending(request_id: str) -> None:
    path = _turn_gate_pending_path(request_id)
    path.unlink(missing_ok=True)
    dir_fd = os.open(path.parent, os.O_RDONLY)
    try:
        os.fsync(dir_fd)
    finally:
        os.close(dir_fd)


def _reconcile_turn_gate_pending() -> None:
    """Exactly-once completion of signed pending sidecars. The caller holds
    the approval flock.

    A torn PENDING append had nothing to prove itself against: the minted
    claim only pins the CONSUMED payload, so a crash during request append
    could strand the gate forever (requests refused, display skipped the row,
    approve found no claim). The sidecar pins every new request's complete row
    under the D85 key, making reconciliation decidable across all crash points:
      * row already fully present            -> retire the sidecar (no re-append),
      * torn tail matching exactly ONE survivor -> truncate the tail, rewrite
        the pinned row verbatim, retire the sidecar,
      * tail with zero matches               -> refuse (foreign tail stays
        fail-closed; consumed recovery belongs to approve),
      * tail matching multiple survivors     -> refuse the ambiguity,
      * row and tail both absent             -> append the pinned row, retire.
    No unconditional truncation: every removal is proven by an HMAC-signed
    payload, and the truncate happens on an O_NOFOLLOW+fstat-verified fd,
    mirroring consumed recovery."""
    try:
        raw = _turn_gate_requests_path().read_bytes()
    except FileNotFoundError:
        raw = b""
    complete = set(raw.split(b"\n")[:-1])
    tail = raw[raw.rfind(b"\n") + 1:] if raw else b""
    try:
        claims_dir = _turn_gate_claims_dir_checked()
    except AdmissionDenied:
        return  # no claims dir has ever existed — nothing to reconcile
    sidecars: dict[str, dict] = {}
    for path in sorted(claims_dir.glob("*.pending")):
        doc = _read_turn_gate_pending(path)
        if doc is not None:
            sidecars[str(doc["request_id"])] = doc
    survivors: dict[str, tuple[dict, bytes]] = {}
    for rid in sorted(sidecars):
        line = _canonical_bytes(sidecars[rid]["payload"])
        if line in complete:
            _unlink_turn_gate_pending(rid)
        else:
            survivors[rid] = (sidecars[rid]["payload"], line)
    if tail:
        matches = [(rid, line) for rid, (_payload, line) in survivors.items()
                   if line.startswith(tail)]
        if len(matches) > 1:
            raise AdmissionDenied(
                "[d85] multiple signed pending payloads match the incomplete ledger tail — "
                "retire stale sidecars under " + str(_turn_gate_claims_dir())
                + " before new requests")
        if not matches:
            raise AdmissionDenied(
                "[d85] ledger ends in an incomplete record — resume the interrupted approval "
                "before new requests (the displayed pending ID is the recoverable one)")
        rid, line = matches[0]
        path = _turn_gate_requests_path()
        try:
            fd = os.open(path,
                         os.O_RDWR | getattr(os, "O_NOFOLLOW", 0), 0o600)
        except OSError as exc:
            raise AdmissionDenied(
                f"[d85] turn-gate ledger unrepairable: {_safe_error(exc)}") from exc
        try:
            info = os.fstat(fd)
            if not stat.S_ISREG(info.st_mode) or info.st_uid != os.getuid():
                raise AdmissionDenied(
                    "[d85] turn-gate requests ledger is not a private regular file")
            if info.st_size < len(tail):
                raise AdmissionDenied("[d85] turn-gate ledger tail accounting mismatch")
            os.ftruncate(fd, info.st_size - len(tail))
            os.fsync(fd)
            os.lseek(fd, 0, os.SEEK_END)
            record = line + b"\n"
            written = 0
            while written < len(record):
                written += os.write(fd, record[written:])
            os.fsync(fd)
        finally:
            os.close(fd)
        _unlink_turn_gate_pending(rid)
    else:
        for rid in sorted(survivors):
            payload, _line = survivors[rid]
            _append_turn_gate_row(payload)
            _unlink_turn_gate_pending(rid)


def _post_claim_ledger_conflict(claim: dict) -> None:
    """Ledger-cursor supersession (never wall-clock), GLOBAL: there is exactly
    one turn_gate slot in the single enforcement config, so ANY consumed row at
    index >= the claim's persisted cursor that is not this claim's own row means
    the shared gate moved on — same process or a foreign one. OUR consumed row
    means the ceremony already completed (seal + refuse). Any OTHER consumed row
    at/after the cursor means a newer approval finished in-flight — resuming
    would rewind the shared config/cert (seal + refuse). Consumed rows before
    the cursor predate this claim and must never fire."""
    cursor = int(claim["ledger_count"])
    for index, row in enumerate(_read_turn_gate_requests()):
        if index < cursor or row["status"] != "consumed":
            continue
        if row["request_id"] == claim["request_id"]:
            if claim["state"] != "sealed":
                _advance_turn_gate_claim(claim, {"state": "sealed"})
            raise AdmissionDenied(
                f"[d85] turn-gate request {claim['request_id']} already consumed — ledger is authoritative")
        if claim["state"] != "sealed":
            _advance_turn_gate_claim(claim, {"state": "sealed"})
        raise AdmissionDenied(
            "[d85] a newer turn-gate approval completed while this one was "
            "in flight — resuming would rewind the gate; re-request")


def turn_gate_approve(
    phrase: str | None = None, *, approver: str = "mike", now: float | None = None
) -> dict:
    """Ceremony step 2: interactive typed approval. Only after the exact typed
    phrase and full revalidation does this authority path touch the enforcement
    config (a static security root no generic edit may reach). The config is
    schema-validated BEFORE install; the atomic claim (persisting the ledger
    cursor and the prior config block) is taken BEFORE minting with mint time =
    claim time; claimed→minted→sealed advances persist; supersession is
    cursor-based and timestamp-order-independent; a minted resume verifies the
    live certificate AND its policy binding before any config mutation; consumed
    rows keep the checklist identity digest and add a distinct
    turn_certificate_sha256."""
    test_mode = phrase is not None or now is not None
    displayed_digests: dict[str, str] = {}
    rows_before = _read_turn_gate_requests(display=True)
    pending_all = [r for r in rows_before if r["status"] == "pending"]
    visible = pending_all[-20:]
    visible_ids = {str(r["request_id"]) for r in visible}
    torn_tail_present = _turn_gate_torn_tail_present()
    if torn_tail_present:
        # A torn consumed-append tail also blocks new requests, so the 20-row
        # window must never hide the one request whose signed minted claim can
        # repair it: every pending row with a minted claim is surfaced.
        for candidate in pending_all:
            candidate_id = str(candidate["request_id"])
            if candidate_id in visible_ids:
                continue
            try:
                candidate_claim = _read_turn_gate_claim(candidate_id)
            except AdmissionDenied:
                continue
            if candidate_claim is not None and candidate_claim["state"] == "minted":
                visible.append(candidate)
                visible_ids.add(candidate_id)
    if test_mode:
        home = _d85_home().resolve()
        temp_root = Path(tempfile.gettempdir()).resolve()
        if (os.environ.get("RIG_D85_TEST_PHRASE") != "1"
                or _TEST_HOME is None
                or home == (_FIXED_HOME / ".rig/d85").resolve()
                or home == temp_root or not home.is_relative_to(temp_root)):
            raise AdmissionDenied(
                "[d85] supplied approval phrase/clock is test-only and requires an isolated temporary D85 home")
        how = "test-phrase"
        for pending in visible:
            displayed_digests[str(pending["request_id"])] = hashlib.sha256(
                _canonical_bytes(pending)).hexdigest()
    else:
        pending_for_display = visible
        if not pending_for_display:
            raise AdmissionDenied("[d85] no pending turn-gate requests to review")
        try:
            with open("/dev/tty", "r+", encoding="utf-8") as tty:
                if not tty.isatty():
                    raise AdmissionDenied("[d85] turn-gate approval requires an interactive TTY")
                tty.write("Pending D85 turn-gate scopes:\n")
                if torn_tail_present:
                    tty.write("(incomplete ledger tail present — minted recoveries are "
                              "listed even beyond the last 20)\n")
                for pending in pending_for_display:
                    row_bytes = _canonical_bytes(pending)
                    displayed_digests[str(pending["request_id"])] = hashlib.sha256(
                        row_bytes).hexdigest()
                    tty.write(row_bytes.decode("utf-8") + "\n")
                tty.write("type: APPROVE <request_id>\n")
                tty.flush()
                phrase = tty.readline()
        except OSError as exc:
            raise AdmissionDenied(f"[d85] turn-gate approval requires an interactive TTY: {exc}") from exc
        how = "typed-approve"
    match = re.fullmatch(r"\s*APPROVE\s+(d85gtg_[0-9a-f]{12})\s*", phrase or "")
    if not match:
        raise AdmissionDenied(
            '[d85] turn-gate-approve requires the exact phrase "APPROVE <request_id>"')
    request_id = match.group(1)
    if request_id not in displayed_digests:
        raise AdmissionDenied("[d85] request ID was not among the displayed pending scopes")
    lock_handle = _lock_turn_gate_approval()
    try:
        claim = _read_turn_gate_claim(request_id)
        if claim is not None:
            _recover_turn_gate_consumed_tail(claim)
        rows = _read_turn_gate_requests()
        latest = _latest_requests_by_id(rows)
        row = latest.get(request_id)
        if row is not None and row["status"] == "consumed":
            if claim is not None and claim["state"] != "sealed":
                _advance_turn_gate_claim(claim, {"state": "sealed"})
            raise AdmissionDenied(
                f"[d85] turn-gate request {request_id} already consumed — ledger is authoritative")
        if claim is not None and claim["state"] == "sealed":
            raise AdmissionDenied(f"[d85] turn-gate request {request_id} already consumed")
        if row is None or row["status"] != "pending":
            raise AdmissionDenied(
                f"[d85] no pending turn-gate request {request_id} — fail closed")
        if hashlib.sha256(_canonical_bytes(row)).hexdigest() != displayed_digests[request_id]:
            raise AdmissionDenied(
                "[d85] pending scope differs from the displayed row — re-request")
        req = row
        attempt_time = time.time() if now is None else float(now)
        if claim is not None and not (
            req["requested_at"] <= claim["consumed_at"] <= attempt_time
            and claim["consumed_at"] < req["expires_at"]
        ):
            _advance_turn_gate_claim(claim, {"state": "sealed"})
            raise AdmissionDenied(
                "[d85] turn-gate claim clock is outside the request window")
        config_path = _config_path()
        try:
            raw_config = json.loads(config_path.read_text(encoding="utf-8"),
                                     object_pairs_hook=_config_object,
                                     parse_constant=_reject_constant)
        except FileNotFoundError:
            raw_config = {}
        except Exception as exc:  # noqa: BLE001
            raise AdmissionDenied(f"[d85] enforcement config unreadable: {_safe_error(exc)}") from exc
        if not isinstance(raw_config, dict):
            raise AdmissionDenied("[d85] enforcement config is not an object")
        block = {"process_id": str(req["process_id"]), "items_file": str(req["items_file"]),
                 "items_file_sha256": str(req["items_file_sha256"])}
        previous = raw_config.get("turn_gate")
        if claim is None:
            if not float(req["requested_at"]) <= attempt_time < float(req["expires_at"]):
                _claim_turn_gate_request(request_id, ledger_count=len(rows))
                raise AdmissionDenied("[d85] turn-gate request is outside its review window — re-request")
            issued_at = attempt_time
            claim = _claim_turn_gate_request(
                request_id, state="claimed", when=issued_at, approver=approver, how=how,
                ledger_count=len(rows), turn_gate_previous=previous,
                turn_gate_preinstalled=previous == block,
                turn_gate_replaced=previous not in (None, {}) and previous != block)
        else:
            issued_at = float(claim["consumed_at"])
        ttl_seconds = float(req["ttl_hours"]) * 3600
        if attempt_time >= issued_at + ttl_seconds:
            _advance_turn_gate_claim(claim, {"state": "sealed"})
            raise AdmissionDenied("[d85] claimed turn-gate request expired mid-ceremony — re-request")
        _post_claim_ledger_conflict(claim)
        items_file = Path(str(req["items_file"]))
        _load_turn_items(items_file, str(req["process_id"]), str(req["items_file_sha256"]))
        build = Path(str(req["build_file"]))
        try:
            build_digest = hashlib.sha256(build.read_bytes()).hexdigest()
        except OSError as exc:
            raise AdmissionDenied(f"[d85] turn-gate build file unreadable: {exc!r}") from exc
        if build_digest != req["build_digest"]:
            raise AdmissionDenied("[d85] build file changed after the request — re-request")
        cert = _build_compliant_bound(str(req["build_file"]), str(req["process_id"]))
        if cert["checklist_sha256"] != req["certificate_sha256"]:
            raise AdmissionDenied("[d85] bound checklist certificate changed after the request — re-request")
        if raw_config.get("turn_gate") not in (claim["turn_gate_previous"], block):
            raise AdmissionDenied(
                "[d85] enforcement config changed after the claim — re-request")
        cert_file = _turn_gate_dir() / f"{req['process_id']}.cert.json"
        cert_sha = None
        if claim["state"] == "minted":
            live_cert = _load_turn_cert(str(req["process_id"]))
            cert_sha = hashlib.sha256(_canonical_bytes(live_cert)).hexdigest()
            if cert_sha != claim.get("certificate_sha256"):
                raise AdmissionDenied("[d85] certificate drifted after the claim — re-request")
            if live_cert["binding"].get("policy_sha256") != _policy_sha256():
                raise AdmissionDenied(
                    "[d85] minted certificate no longer matches the live policy binding — re-request")
            _turn_cert_fresh(live_cert, str(req["content_sha256"]),
                             str(req["process_id"]), attempt_time)
        merged = {**raw_config, "turn_gate": block}
        try:
            _validated_config(merged)
        except Exception as exc:  # noqa: BLE001
            raise AdmissionDenied(
                f"[d85] merged enforcement config would be invalid: {_safe_error(exc)}") from exc
        config_installed = False
        if raw_config.get("turn_gate") != block:
            _turn_gate_write_replaceable(
                config_path, (json.dumps(merged, indent=2, sort_keys=True) + "\n").encode("utf-8"))
            config_installed = True
        if cert_sha is None:
            _post_claim_ledger_conflict(claim)
            if time.time() >= issued_at + ttl_seconds:
                _advance_turn_gate_claim(claim, {"state": "sealed"})
                raise AdmissionDenied("[d85] claimed turn-gate request expired before mint — re-request")
            try:
                build_digest = hashlib.sha256(build.read_bytes()).hexdigest()
            except OSError as exc:
                raise AdmissionDenied(f"[d85] turn-gate build file unreadable: {exc!r}") from exc
            cert = _build_compliant_bound(str(req["build_file"]), str(req["process_id"]))
            if (build_digest != req["build_digest"]
                    or cert["checklist_sha256"] != req["certificate_sha256"]):
                raise AdmissionDenied(
                    "[d85] build or checklist drifted immediately before mint — re-request")
            if not (_bounded_time(issued_at) and _bounded_time(issued_at + ttl_seconds)):
                raise AdmissionDenied("[d85] certificate lifetime timestamps out of range")
            authority = _turn_gate_authority(str(req["process_id"]))
            doc: dict = {
                "schema": TURN_CERT_SCHEMA,
                "process_id": req["process_id"],
                "content_sha256": req["content_sha256"],
                "binding": {
                    "build_file": str(build),
                    "build_digest": build_digest,
                    "policy_sha256": _policy_sha256(),
                    **authority,
                    "issued_at": issued_at,
                    "expires_at": issued_at + ttl_seconds,
                },
            }
            doc["signature"] = hmac.new(_load_key(), _canonical_bytes(doc), hashlib.sha256).hexdigest()
            _turn_gate_write_replaceable(cert_file, _canonical_bytes(doc) + b"\n")
            cert_sha = hashlib.sha256(_canonical_bytes(doc)).hexdigest()
            consumed = {
                **req, "status": "consumed", "consumed_at": issued_at,
                "approver": claim.get("approver") or approver,
                "how": claim.get("how") or how,
                "certificate_file": str(cert_file), "turn_certificate_sha256": cert_sha,
                "turn_gate_installed": config_installed,
                "turn_gate_preinstalled": bool(claim["turn_gate_preinstalled"]),
                "turn_gate_replaced": bool(claim["turn_gate_replaced"]),
                "turn_gate_previous": claim["turn_gate_previous"],
            }
            claim = _advance_turn_gate_claim(claim, {
                "state": "minted", "certificate_sha256": cert_sha, "consumed": consumed})
        else:
            persisted = claim["consumed"]
            if (persisted.get("request_id") != request_id
                    or persisted.get("turn_certificate_sha256") != cert_sha
                    or persisted.get("process_id") != req["process_id"]
                    or persisted.get("content_sha256") != req["content_sha256"]):
                raise AdmissionDenied(
                    "[d85] persisted consumed payload differs from the revalidated scope — re-request")
            consumed = persisted
        _append_turn_gate_row(consumed)
        _advance_turn_gate_claim(claim, {"state": "sealed"})
        return consumed
    finally:
        fcntl.flock(lock_handle.fileno(), fcntl.LOCK_UN)
        lock_handle.close()


def turn_banner(*, now: float | None = None) -> str:
    """Deterministic per-turn banner for hook injection. Never raises.
    Only a successfully parsed config with an absent turn_gate key opts out;
    a configured-but-broken gate (or broken config) is always a RED banner."""
    try:
        cfg = load_config()
    except AdmissionDenied as exc:
        return (
            "[d85] TURN GATE RED — enforcement config is missing or unreadable "
            f"({exc}) — mutations remain fail-closed."
        )
    gate = cfg.get("turn_gate")
    if gate is None:
        return ""
    process_id = gate["process_id"]
    current_time = time.time() if now is None else now
    try:
        items = _load_turn_items(
            Path(gate["items_file"]), process_id, gate["items_file_sha256"]
        )
        cert = _load_turn_cert(process_id)
        _turn_cert_fresh(cert, items["content_sha256"], process_id, current_time)
    except AdmissionDenied as exc:
        return f"[d85] TURN GATE RED process={process_id} — {exc} — mutations remain fail-closed."
    except Exception as exc:  # noqa: BLE001 — the gate itself must fail visibly, not silently
        return (
            f"[d85] TURN GATE RED process={process_id} — internal failure ({_safe_error(exc)}) "
            "— mutations remain fail-closed."
        )
    cert_sha = hashlib.sha256(_canonical_bytes(cert)).hexdigest()
    try:
        consumed_rows = [row for row in _read_turn_gate_requests()
                         if row["status"] == "consumed"]
        latest = consumed_rows[-1] if consumed_rows else None
        claim = _read_turn_gate_claim(str(latest["request_id"])) if latest is not None else None
    except AdmissionDenied as exc:
        return (
            f"[d85] TURN GATE RED process={process_id} — consumed ledger unreadable ({exc}) "
            "— mutations remain fail-closed."
        )
    if (latest is None or latest["process_id"] != process_id
            or claim is None or claim["state"] not in ("minted", "sealed")
            or claim.get("certificate_sha256") != cert_sha
            or claim.get("consumed") != latest):
        return (
            f"[d85] TURN GATE RED process={process_id} — no consumed ledger row bound to a "
            "signed claim matches the active certificate — resume the approval — mutations "
            "remain fail-closed."
        )
    expires = float(cert["binding"]["expires_at"])
    lines = [
        f"[d85] TURN GATE GREEN process={process_id} "
        f"build={cert['binding']['build_digest'][:16]} items={items['content_sha256'][:16]} "
        f"expires_in={max(0, int(expires - current_time))}s — "
        "evidence freshness only; every mutation still needs its own admission."
    ]
    lines += [
        f"  [{item['when']}/{item['proof']}] {item['id']}: {item['text']}"
        for item in items["items"]
    ]
    return "\n".join(lines)


# ---------------------------------------------------------------- hook check

def _signed_runtime_inputs(
    records: list[dict],
    ledger_key: bytes,
    current: float,
    current_policy: str,
) -> set[str]:
    inputs: set[str] = set()
    for record in records:
        _verify_signature(record, ledger_key)
        active = (
            float(record.get("issued_at", 0))
            <= current
            < float(record.get("expires_at", 0))
            and record.get("policy_sha256") == current_policy
        )
        launcher_unconsumed = bool(record.get("launchers")) and not (
            _execution_claim_path(record).exists()
        )
        if not active or not (record.get("paths") or launcher_unconsumed):
            continue
        build_file = _abs(str(record.get("build_file", "")), None)
        inputs.add(build_file)
        inputs.add(
            str((Path(build_file).parent / "certificate.json").resolve(strict=False)))
        if launcher_unconsumed:
            inputs.update(
                _abs(str(value), None) for value in record.get("launchers", []))
            inputs.update(
                _abs(str(value), None)
                for value in (record.get("launcher_dependencies") or {}))
    return inputs


def _break_glass_kind(p: dict) -> tuple[str, str | None]:
    raw_tool = p.get("tool")
    tool = (
        raw_tool.strip().lower().replace("-", "_")
        if isinstance(raw_tool, str)
        else ""
    )
    kind = NATIVE_TOOL_CAPABILITIES.get(tool)
    if kind is None:
        try:
            kind = load_config()["tool_capabilities"].get(tool)
        except AdmissionDenied:
            kind = None
    return tool, kind


def _break_glass_request_sha256(p: dict, tool: str) -> str:
    command = p.get("command")
    if not isinstance(command, str):
        command = ""
    cwd = p.get("cwd")
    if not isinstance(cwd, str):
        cwd = ""
    tool_input = p.get("tool_input")
    if not isinstance(tool_input, dict):
        tool_input = {}
    targets = mutation_targets_ex(p)[0]
    return _canonical_hash({
        "tool": tool,
        "cwd": cwd,
        "command_sha256": (
            hashlib.sha256(command.encode("utf-8")).hexdigest()
            if command else None
        ),
        "paths_sha256": _canonical_hash(sorted(targets)),
        "input_sha256": hashlib.sha256(
            _canonical_bytes(tool_input)
        ).hexdigest(),
    })


def _break_glass_audit_row(
    p: dict,
    *,
    tool: str,
    current: float,
    key: bytes,
    flag_class: str,
    decision: str,
    reason_code: str,
    admission_id: str | None = None,
    approval_expires_at: float | None = None,
    finalizes: str | None = None,
) -> dict:
    identity = {
        "schema": BYPASS_SCHEMA,
        "nonce": secrets.token_hex(8),
        "occurred_at": current,
        "hook_event": "pre-tool",
        "session_key": session_key(p),
        "tool": tool,
        "request_sha256": _break_glass_request_sha256(p, tool),
        "flag_class": flag_class,
        "decision": decision,
        "reason_code": reason_code,
        "admission_id": admission_id,
        "approval_expires_at": approval_expires_at,
        "finalizes": finalizes,
    }
    body = {
        **identity,
        "event_id": "d85byp_" + _canonical_hash(identity)[:12],
    }
    return {
        **body,
        "signature": hmac.new(
            key, _canonical_bytes(body), hashlib.sha256
        ).hexdigest(),
    }


def _audit_break_glass(
    p: dict,
    *,
    tool: str,
    current: float,
    key: bytes,
    flag_class: str,
    decision: str,
    reason_code: str,
    admission_id: str | None = None,
    approval_expires_at: float | None = None,
    finalizes: str | None = None,
) -> dict:
    row = _break_glass_audit_row(
        p,
        tool=tool,
        current=current,
        key=key,
        flag_class=flag_class,
        decision=decision,
        reason_code=reason_code,
        admission_id=admission_id,
        approval_expires_at=approval_expires_at,
        finalizes=finalizes,
    )
    _append_bypass_row(row)
    return row


def _audit_break_glass_best_effort(
    p: dict,
    *,
    tool: str,
    current: float,
    flag_class: str,
    reason_code: str,
    key: bytes | None = None,
    admission_id: str | None = None,
    approval_expires_at: float | None = None,
) -> None:
    try:
        audit_key = _load_key() if key is None else key
        _audit_break_glass(
            p,
            tool=tool,
            current=current,
            key=audit_key,
            flag_class=flag_class,
            decision="enforce",
            reason_code=reason_code,
            admission_id=admission_id,
            approval_expires_at=approval_expires_at,
        )
    except Exception as exc:  # noqa: BLE001 — an unavailable audit cannot weaken enforcement
        print(
            f"[d85] break-glass audit unavailable ({_safe_error(exc)})",
            file=sys.stderr,
        )


def _break_glass_candidate_fields(record: object) -> tuple[str | None, float | None]:
    if not isinstance(record, dict):
        return None, None
    admission_id = record.get("admission_id")
    if (
        not isinstance(admission_id, str)
        or not re.fullmatch(r"d85bg_[0-9a-f]{12}", admission_id)
    ):
        admission_id = None
    expires_at = record.get("expires_at")
    if not _bounded_time(expires_at):
        expires_at = None
    return admission_id, expires_at


def _break_glass_evaluate(
    p: dict,
    flag: str,
    current: float,
) -> tuple[str, str, None]:
    """Authenticate one native-write self-disable request. Never raises.
    Authorization linearizes inside the audit-lock critical section at the
    in-lock occurred_at timestamp, revalidated there against the approval."""
    try:
        raw_tool = p.get("tool")
        tool = (
            raw_tool.strip().lower().replace("-", "_")
            if isinstance(raw_tool, str)
            else ""
        )
        if flag != "1":
            _audit_break_glass_best_effort(
                p,
                tool=tool,
                current=current,
                flag_class="invalid",
                reason_code="flag-invalid",
            )
            return "enforce", "flag-invalid", None
        tool, kind = _break_glass_kind(p)
        if kind != "write":
            _audit_break_glass_best_effort(
                p,
                tool=tool,
                current=current,
                flag_class="exact-one",
                reason_code="kind-not-authorizable",
            )
            return "enforce", "kind-not-authorizable", None
        try:
            key = _load_key()
        except AdmissionDenied as exc:
            print(
                f"[d85] break-glass ignored (key-unreadable; {_safe_error(exc)})",
                file=sys.stderr,
            )
            return "enforce", "key-unreadable", None
        try:
            caller_session = session_key(p)
        except AdmissionDenied as exc:
            _audit_break_glass_best_effort(
                p,
                tool=tool,
                current=current,
                key=key,
                flag_class="exact-one",
                reason_code="approval-session-mismatch",
            )
            print(
                f"[d85] break-glass ignored "
                f"(approval-session-mismatch; {_safe_error(exc)})",
                file=sys.stderr,
            )
            return "enforce", "approval-session-mismatch", None
        try:
            rows = [
                row
                for row in _read_records(_approvals_path())
                if row.get("schema") == _BG_APPROVAL_SCHEMA
            ]
        except AdmissionDenied:
            _audit_break_glass_best_effort(
                p,
                tool=tool,
                current=current,
                key=key,
                flag_class="exact-one",
                reason_code="ledger-unreadable",
            )
            return "enforce", "ledger-unreadable", None
        mine = [row for row in rows if row.get("session_key") == caller_session]
        if not mine:
            reason_code = (
                "approval-session-mismatch" if rows else "approval-missing"
            )
            _audit_break_glass_best_effort(
                p,
                tool=tool,
                current=current,
                key=key,
                flag_class="exact-one",
                reason_code=reason_code,
            )
            return "enforce", reason_code, None
        candidate = mine[-1]
        admission_id, expires_at = _break_glass_candidate_fields(candidate)
        try:
            approval = _validated_break_glass_approval(
                candidate, "approval ledger candidate")
            _verify_signature(approval, key)
        except Exception:  # noqa: BLE001 — malformed candidate is never skipped
            _audit_break_glass_best_effort(
                p,
                tool=tool,
                current=current,
                key=key,
                flag_class="exact-one",
                reason_code="approval-tampered",
                admission_id=admission_id,
                approval_expires_at=expires_at,
            )
            return "enforce", "approval-tampered", None
        admission_id = approval["admission_id"]
        expires_at = approval["expires_at"]
        try:
            verifier_sha256 = _verifier_identity_sha256()
        except AdmissionDenied:
            verifier_sha256 = None
        if verifier_sha256 != approval["verifier_sha256"]:
            _audit_break_glass_best_effort(
                p,
                tool=tool,
                current=current,
                key=key,
                flag_class="exact-one",
                reason_code="verifier-drift",
                admission_id=admission_id,
                approval_expires_at=expires_at,
            )
            return "enforce", "verifier-drift", None
        try:
            targets, unknown, has_unproven = mutation_targets_ex({
                **p,
                "_capability_kind": kind,
            })
            _assert_single_linked_targets(targets)
            config_roots = load_config()["roots"]
            forbidden_identities = _break_glass_forbidden_identities()
            identities_authorizable = all(
                not _break_glass_path_forbidden(
                    path, config_roots, forbidden_identities)
                for path in [*approval["paths"], *targets]
            )
            approved_paths = {
                str(Path(path).resolve(strict=False))
                for path in approval["paths"]
            }
            requested_paths = {
                str(Path(path).resolve(strict=False))
                for path in targets
            }
            targets_authorizable = (
                bool(targets)
                and not unknown
                and not has_unproven
                and identities_authorizable
                and requested_paths <= approved_paths
            )
        except Exception:  # noqa: BLE001 — malformed targets never enter the grant
            targets_authorizable = False
        if not targets_authorizable:
            _audit_break_glass_best_effort(
                p,
                tool=tool,
                current=current,
                key=key,
                flag_class="exact-one",
                reason_code="target-not-authorizable",
                admission_id=admission_id,
                approval_expires_at=expires_at,
            )
            return "enforce", "target-not-authorizable", None
        ordinary_records = [
            record
            for record in _read_records(_approvals_path())
            if record.get("schema") == ADMISSION_SCHEMA
        ]
        immutable_inputs = _signed_runtime_inputs(
            ordinary_records,
            key if ordinary_records else b"",
            current,
            _policy_sha256(),
        )
        input_ids = {
            identity
            for path in immutable_inputs
            if (identity := _path_identity(path)) is not None
        }
        if any(
            _abs(target, None) in immutable_inputs
            or _path_identity(target) in input_ids
            for target in targets
        ):
            _audit_break_glass_best_effort(
                p,
                tool=tool,
                current=current,
                key=key,
                flag_class="exact-one",
                reason_code="runtime-input-immutable",
                admission_id=admission_id,
                approval_expires_at=expires_at,
            )
            return "enforce", "runtime-input-immutable", None
        lock_handle = _lock_break_glass_audit()
        try:
            decision_at = time.time()
            if decision_at < float(approval["issued_at"]):
                reason_code = "approval-not-yet-valid"
            elif decision_at >= float(approval["expires_at"]):
                reason_code = "approval-expired"
            else:
                reason_code = None
            if reason_code is not None:
                try:
                    enforce_row = _break_glass_audit_row(
                        p,
                        tool=tool,
                        current=decision_at,
                        key=key,
                        flag_class="exact-one",
                        decision="enforce",
                        reason_code=reason_code,
                        admission_id=admission_id,
                        approval_expires_at=expires_at,
                    )
                    _append_bypass_row_locked(enforce_row)
                except Exception as exc:  # noqa: BLE001 — time denial never grants
                    print(
                        f"[d85] break-glass audit unavailable ({_safe_error(exc)})",
                        file=sys.stderr,
                    )
                    return "enforce", "audit-unavailable", None
                return "enforce", reason_code, None
            try:
                reservation = _break_glass_audit_row(
                    p,
                    tool=tool,
                    current=decision_at,
                    key=key,
                    flag_class="exact-one",
                    decision="reservation",
                    reason_code="approved",
                    admission_id=admission_id,
                    approval_expires_at=expires_at,
                )
                _append_bypass_row_locked(reservation)
            except _BypassLedgerUnreadable:
                return "enforce", "ledger-unreadable", None
            except Exception as exc:  # noqa: BLE001 — no reservation means no bypass
                print(
                    f"[d85] break-glass audit unavailable ({_safe_error(exc)})",
                    file=sys.stderr,
                )
                return "enforce", "audit-unavailable", None
            try:
                terminal = _break_glass_audit_row(
                    p,
                    tool=tool,
                    current=decision_at,
                    key=key,
                    flag_class="exact-one",
                    decision="skip",
                    reason_code="approved",
                    admission_id=admission_id,
                    approval_expires_at=expires_at,
                    finalizes=reservation["event_id"],
                )
                _append_bypass_row_locked(terminal)
            except Exception as exc:  # noqa: BLE001 — orphaned reservation is fail-closed
                print(
                    f"[d85] break-glass audit unavailable ({_safe_error(exc)})",
                    file=sys.stderr,
                )
                return "enforce", "audit-unavailable", None
            return "skip", "approved", None
        finally:
            fcntl.flock(lock_handle.fileno(), fcntl.LOCK_UN)
            lock_handle.close()
    except Exception as exc:  # noqa: BLE001 — break-glass must never weaken the core gate
        print(
            f"[d85] break-glass ignored (audit-unavailable; {_safe_error(exc)})",
            file=sys.stderr,
        )
        return "enforce", "audit-unavailable", None


def hook_check(p: dict, *, now: float | None = None) -> dict | None:
    """None = allow. {"action": "deny", "reason": ...} = block. Fail closed."""
    payload = dict(p) if isinstance(p, dict) else p
    flag = payload.pop("break_glass_flag", None) if isinstance(payload, dict) else None
    note = ""
    must_deny = False
    if isinstance(flag, str):
        _, kind = _break_glass_kind(payload)
        if kind == "read":
            return _hook_check_core(payload, now=now)
        decision, code, _ = _break_glass_evaluate(
            payload,
            flag,
            time.time() if now is None else float(now),
        )
        if decision == "skip":
            return None
        note = f"[d85] break-glass ignored ({code}); D85 enforcement remains active.\n"
        must_deny = code in {
            "target-not-authorizable", "runtime-input-immutable"}
    result = _hook_check_core(payload, now=now)
    if must_deny and result is None:
        return {"action": "deny", "reason": note.rstrip()}
    if note and isinstance(result, dict) and isinstance(result.get("reason"), str):
        result = {**result, "reason": note + result["reason"]}
    return result


def _hook_check_core(p: dict, *, now: float | None = None) -> dict | None:
    """None = allow. {"action": "deny", "reason": ...} = block. Fail closed."""
    try:
        raw_tool = p.get("tool")
        if not isinstance(raw_tool, str) or not raw_tool.strip():
            return {"action": "deny", "reason": (
                "[d85] pre-tool payload carried no valid tool identity — cannot classify the call.")}
        tool = raw_tool.strip().lower().replace("-", "_")
        kind = NATIVE_TOOL_CAPABILITIES.get(tool)
        if kind == "read":
            return None
        cfg = load_config()
        kind = kind or cfg["tool_capabilities"].get(tool)
        if kind == "read":
            return None
        if kind is None:
            return {"action": "deny", "reason": (
                f"[d85] unregistered tool {tool!r}; a host-owned capability classification is required")}
        if kind == "delegate":
            return {"action": "deny", "reason": (
                "[d85] delegation requires a guarded executor that preserves policy in every child")}
        if kind == "execute":
            # UNIVERSAL RULE (advisory-accepted): regex write-signature scanning cannot
            # contain arbitrary code (getattr/encoded source/imports/subprocess all bypass).
            # Under active enforcement, arbitrary-code tools are DENIED outright — no
            # session-cover unlock either, since a narrow path grant must not become
            # write authority over every root. Break-glass binds exact production paths
            # but permanently excludes D85 authority and verifier files; eval, shell,
            # delegation, and authority repair remain out-of-band operator work.
            return {"action": "deny", "reason": (
                "[d85] arbitrary-code tool (eval/python/repl) is denied while D85 enforcement is "
                "active: no static analysis can bound what arbitrary code writes (documented "
                "ceiling, not a convenience exception).\n"
                "Use explicit write/edit calls (admissible per exact path) or run the code as an "
                "admitted automation: admit-request --launcher <script> --launcher-cwd <cwd> "
                "--launcher-timeout-seconds <seconds> → APPROVE <id> → admit-approve → "
                "d85-run --session-key sid:<id> <script>. Break-glass authorizes ONLY "
                "the exact enumerated production paths displayed at approval, native "
                "write/edit tools only, for <=15 min, every use audited. The flag alone "
                "is ignored. It can never touch D85's own key, ledgers, configuration, "
                "or verifier files — those repair out-of-band. Request with: "
                "rig-determinism-85 break-glass-request --session-key <sid:...> "
                "--reason ... --path <exact-path> -> Mike types APPROVE <id> in a TTY "
                "-> admit-approve -> export RIG_D85_DISABLE=1.")}
        if kind == "shell" and (
            not isinstance(p.get("command"), str)
            or not p["command"].strip()
        ):
            return {"action": "deny", "reason": (
                "[d85] shell capability carried no supported command envelope — fail closed")}
        targets, unknown, has_unproven = mutation_targets_ex({
            **p,
            "_capability_kind": kind,
        })
        if kind == "write" and not targets:
            return {"action": "deny", "reason": (
                "[d85] mutation targets are unresolved; unsupported write envelopes fail closed")}
        _assert_single_linked_targets(targets)
        effective_roots = sorted(
            set(cfg["roots"]) | {str(path) for path in _static_security_roots()})
        gated = [t for t in targets if _under_roots(t, effective_roots)]
        unknown_gated = [t for t in unknown if _under_roots(t, effective_roots)]
        if unknown_gated:
            return {"action": "deny", "reason": (
                f"[d85] shell command references a production surface with a verb the gate cannot "
                f"statically prove read-only: {unknown_gated[0]}\n"
                "Fail closed. Either (a) admit the exact paths: admit-request → APPROVE <id> → "
                "admit-approve, or (b) use a dedicated read tool or an absolute "
                "fixed-system read-only command such as /bin/cat or /bin/ls.")}
        if (
            kind == "shell"
            and isinstance(p.get("command"), str)
            and _shell_dynamic_execution(p["command"])
        ):
            return {"action": "deny", "reason": (
                "[d85] shell command contains dynamic expansion or nested execution that cannot "
                "be bound to exact write targets. Use literal operands or exact d85-run.")}
        if has_unproven:
            return {"action": "deny", "reason": (
                "[d85] unclassified shell execution cannot prove exact write targets. "
                "Use a closed literal command or exact d85-run.")}
        records = [
            record for record in _read_records(_approvals_path())
            if record.get("schema") == ADMISSION_SCHEMA
        ]
        ledger_key = _load_key() if records else b""
        current = time.time() if now is None else now
        current_policy = _policy_sha256()
        signed_runtime_inputs = _signed_runtime_inputs(
            records, ledger_key, current, current_policy)
        protected_target = next(
            (target for target in targets if _abs(target, None) in signed_runtime_inputs),
            None,
        )
        if protected_target is not None:
            return {"action": "deny", "reason": (
                f"[d85] signed runtime input is immutable during its admission: {protected_target}")}
        if not gated:
            return None
        key = session_key(p)
        if not records:
            return _deny_no_admission(gated, key)
        for target in gated:
            cover = None
            for rec in reversed(records):
                _verify_signature(rec, ledger_key)
                if not (
                    float(rec.get("issued_at", 0))
                    <= current
                    < float(rec.get("expires_at", 0))
                ):
                    continue
                if rec.get("session_key") != key:
                    continue
                if target in [str(value) for value in rec.get("paths", [])]:
                    try:
                        _build_unchanged(rec)
                        _output_bindings_unchanged(rec)
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
        return {"action": "deny", "reason": f"[d85] admission gate internal failure (fail closed): {_safe_error(exc)}"}


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
def break_glass_request(
    session_key_: str,
    reason: str,
    paths: list[str],
    ttl_seconds: float = _BG_MAX_TTL,
) -> dict:
    if (
        not isinstance(session_key_, str)
        or not session_key_.startswith("sid:")
        or not session_key_[4:].strip()
    ):
        raise AdmissionDenied(
            "[d85] break-glass-request requires a real sid:<session-id>, not a cwd grant")
    cleaned_reason = reason.strip() if isinstance(reason, str) else reason
    if not _break_glass_reason_value(cleaned_reason):
        raise AdmissionDenied(
            "[d85] break-glass-request reason must be 1..512 printable characters")
    if (
        isinstance(ttl_seconds, bool)
        or not isinstance(ttl_seconds, (int, float))
        or not math.isfinite(float(ttl_seconds))
        or not _BG_MIN_TTL <= float(ttl_seconds) <= _BG_MAX_TTL
    ):
        raise AdmissionDenied(
            "[d85] break-glass-request TTL must be a finite 60..900 seconds")
    canonical_paths = _validated_break_glass_paths(paths, "request")
    try:
        config_roots = load_config()["roots"]
    except AdmissionDenied as exc:
        raise AdmissionDenied(
            "[d85] break-glass requires readable enforcement configuration "
            "to enumerate production targets") from exc
    if any(
        not _path_within_identity_roots(path, config_roots)
        for path in canonical_paths
    ):
        raise AdmissionDenied(
            "[d85] break-glass paths must be inside configured production roots "
            "by filesystem identity")
    forbidden_identities = _break_glass_forbidden_identities()
    if any(
        _break_glass_path_forbidden(
            path, config_roots, forbidden_identities)
        for path in canonical_paths
    ):
        raise AdmissionDenied(
            "[d85] break-glass paths may not touch D85 authority or verifier "
            "filesystem identities")
    requested_at = int(time.time())
    identity = {
        "schema": _BG_REQUEST_SCHEMA,
        "action": _BG_ACTION,
        "session_key": session_key_,
        "reason": cleaned_reason,
        "paths": canonical_paths,
        "nonce": secrets.token_hex(8),
        "verifier_sha256": _verifier_identity_sha256(),
        "ttl_seconds": ttl_seconds,
        "requested_at": requested_at,
        "review_expires_at": requested_at + _BG_REVIEW_WINDOW,
        "salt": secrets.token_hex(8),
    }
    request = {
        **identity,
        "admission_id": "d85bg_" + _canonical_hash(identity)[:12],
        "status": "pending",
    }
    _validated_break_glass_request(request, "request")
    _admissions_dir().mkdir(parents=True, exist_ok=True)
    _append_private_row(
        _requests_path(), request, "break-glass request ledger")
    return request


def _approve_break_glass(
    request_id: str,
    how: str,
    *,
    approver: str,
    now: float,
) -> dict:
    lock_handle = _lock_break_glass_mint()
    try:
        return _approve_break_glass_locked(
            request_id, how, approver=approver, now=now)
    finally:
        fcntl.flock(lock_handle.fileno(), fcntl.LOCK_UN)
        lock_handle.close()


def _approve_break_glass_locked(
    request_id: str,
    how: str,
    *,
    approver: str,
    now: float,
) -> dict:
    already_minted = [
        row
        for row in _read_records(_approvals_path())
        if (
            row.get("schema") == _BG_APPROVAL_SCHEMA
            and row.get("admission_id") == request_id
        )
    ]
    if already_minted:
        raise AdmissionDenied(
            "[d85] break-glass request already minted — ledger authoritative")
    pending = [
        row
        for row in _read_records(_requests_path())
        if (
            row.get("schema") == _BG_REQUEST_SCHEMA
            and row.get("admission_id") == request_id
            and row.get("status") == "pending"
        )
    ]
    if not pending:
        raise AdmissionDenied(
            f"[d85] no pending break-glass request {request_id} — fail closed")
    request = _validated_break_glass_request(pending[-1], "pending request")
    if not _bounded_time(now):
        raise AdmissionDenied("[d85] break-glass approval clock is invalid")
    if not (
        float(request["requested_at"])
        <= float(now)
        < float(request["review_expires_at"])
    ):
        raise AdmissionDenied(
            "[d85] break-glass request is outside its review window — re-request")
    if request["verifier_sha256"] != _verifier_identity_sha256():
        raise AdmissionDenied("[d85] stale verifier binding — re-request")
    body = {
        "schema": _BG_APPROVAL_SCHEMA,
        "admission_id": request_id,
        "action": _BG_ACTION,
        "session_key": request["session_key"],
        "reason": request["reason"],
        "paths": request["paths"],
        "nonce": request["nonce"],
        "verifier_sha256": request["verifier_sha256"],
        "request_sha256": _canonical_hash(request),
        "by": approver,
        "how": how,
        "issued_at": now,
        "expires_at": float(now) + float(request["ttl_seconds"]),
    }
    key = _init_ledger()
    entry = {
        **body,
        "signature": hmac.new(
            key, _canonical_bytes(body), hashlib.sha256
        ).hexdigest(),
    }
    _append_break_glass_approval(entry, key)
    return entry



def admit_request(
    build_file: str,
    process_id: str | None,
    paths: list[str],
    session_key_: str,
    launchers: list[str] | None = None,
    *,
    launcher_args: list[str] | None = None,
    launcher_cwd: str | None = None,
    launcher_timeout_seconds: float | None = None,
) -> dict:
    if not isinstance(session_key_, str) or not session_key_.startswith("sid:") or not session_key_[4:].strip():
        raise AdmissionDenied("[d85] admit-request requires a real sid:<session-id>, not a cwd grant")
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
    if any(
        not isinstance(value, (str, os.PathLike)) or not os.fspath(value).strip()
        for values in (paths, launchers or [])
        for value in values
    ):
        raise AdmissionDenied("[d85] admission paths and launchers must be nonempty paths")
    abs_paths = [_abs(value, None) for value in paths]
    launcher_abs = [_abs(value, None) for value in (launchers or [])]
    if not abs_paths and not launcher_abs:
        raise AdmissionDenied("[d85] admit-request requires at least one --path or --launcher")
    _build_compliant_bound(str(build), process_id)
    digest = hashlib.sha256(build.read_bytes()).hexdigest()
    launcher_digests = {}
    for value in launcher_abs:
        if not Path(value).is_file():
            raise AdmissionDenied(
                f"[d85] launcher does not exist at request time, cannot bind content: {value} — fail closed.")
        launcher_digests[value] = hashlib.sha256(Path(value).read_bytes()).hexdigest()
    security_roots = _static_security_roots()
    for value in [*abs_paths, *launcher_abs]:
        resolved = Path(value).resolve(strict=False)
        if any(resolved == root or resolved.is_relative_to(root) for root in security_roots):
            raise AdmissionDenied("[d85] outputs and launchers may not overlap D85 authority or release roots")
    protected_exact = {
        str(build),
        str(build.parent / "certificate.json"),
        *launcher_abs,
    }
    if any(path in protected_exact for path in abs_paths):
        raise AdmissionDenied("[d85] writable outputs may not overlap the build, certificate, or launcher")
    output_bindings = {path: _output_binding(path) for path in abs_paths}
    launcher_invocations = {}
    launcher_dependencies: dict[str, str] = {}
    environment_sha256 = _canonical_hash(_clean_subprocess_env())
    load_config()
    policy_sha256 = _policy_sha256()
    launcher_python = None
    launcher_python_sha256 = None
    if launcher_abs:
        python_path = Path(_FIXED_PYTHON)
        if not python_path.is_file() or not os.access(python_path, os.X_OK):
            raise AdmissionDenied(
                f"[d85] fixed launcher Python is unavailable: {_FIXED_PYTHON}")
        launcher_python = str(python_path)
        launcher_python_sha256 = hashlib.sha256(python_path.read_bytes()).hexdigest()
        if (
            len(launcher_abs) != 1
            or launcher_args is None
            or launcher_cwd is None
            or isinstance(launcher_timeout_seconds, bool)
            or not isinstance(launcher_timeout_seconds, (int, float))
            or not math.isfinite(float(launcher_timeout_seconds))
            or not 0 < float(launcher_timeout_seconds) <= MAX_LAUNCHER_SECONDS
        ):
            raise AdmissionDenied(
                "[d85] one launcher requires exact launcher_args, launcher_cwd, and a finite "
                f"launcher_timeout_seconds in (0, {MAX_LAUNCHER_SECONDS}]"
            )
        if not isinstance(launcher_args, list) or any(
            not isinstance(value, str) for value in launcher_args
        ):
            raise AdmissionDenied("[d85] launcher_args must be a string list")
        try:
            cwd = Path(launcher_cwd).resolve(strict=True)
        except (OSError, RuntimeError) as exc:
            raise AdmissionDenied(
                f"[d85] launcher_cwd must be one existing canonical directory: {launcher_cwd!r}"
            ) from exc
        if not cwd.is_dir():
            raise AdmissionDenied("[d85] launcher_cwd must be an existing directory")
        if any(cwd == root or cwd.is_relative_to(root) for root in security_roots):
            raise AdmissionDenied("[d85] launcher_cwd may not overlap D85 authority or release roots")
        launcher = launcher_abs[0]
        launcher_dependencies = _launcher_dependency_digests(Path(launcher))
        if set(abs_paths) & set(launcher_dependencies):
            raise AdmissionDenied(
                "[d85] writable outputs may not overlap launcher dependency inputs")
        launcher_invocations[launcher] = {
            "argv": [launcher, *launcher_args],
            "cwd": str(cwd),
        }
    elif (
        launcher_args is not None
        or launcher_cwd is not None
        or launcher_timeout_seconds is not None
    ):
        raise AdmissionDenied("[d85] launcher invocation fields require one launcher")
    salt = secrets.token_hex(8)
    invocation_id = (
        "d85run_"
        + _canonical_hash(
            {
                "session_key": session_key_,
                "policy_sha256": policy_sha256,
                "launcher_invocations": launcher_invocations,
                "launcher_dependencies": launcher_dependencies,
                "environment_sha256": environment_sha256,
                "launcher_python": launcher_python,
                "launcher_python_sha256": launcher_python_sha256,
                "timeout_seconds": launcher_timeout_seconds,
                "salt": salt,
            }
        )[:16]
        if launcher_abs
        else None
    )
    identity_payload = {
        "build_digest": digest,
        "paths": abs_paths,
        "output_bindings": output_bindings,
        "session_key": session_key_,
        "process_id": process_id,
        "launchers": launcher_abs,
        "launcher_digests": launcher_digests,
        "launcher_invocations": launcher_invocations,
        "launcher_dependencies": launcher_dependencies,
        "launcher_environment_sha256": environment_sha256,
        "policy_sha256": policy_sha256,
        "launcher_python": launcher_python,
        "launcher_python_sha256": launcher_python_sha256,
        "launcher_timeout_seconds": launcher_timeout_seconds,
        "invocation_id": invocation_id,
        "salt": salt,
    }
    admission_id = "d85adm_" + _canonical_hash(identity_payload)[:12]
    request = {
        "schema": ADMISSION_SCHEMA,
        "admission_id": admission_id,
        "session_key": session_key_,
        "paths": abs_paths,
        "output_bindings": output_bindings,
        "launchers": launcher_abs,
        "launcher_digests": launcher_digests,
        "launcher_invocations": launcher_invocations,
        "launcher_dependencies": launcher_dependencies,
        "launcher_environment_sha256": environment_sha256,
        "policy_sha256": policy_sha256,
        "launcher_python": launcher_python,
        "launcher_python_sha256": launcher_python_sha256,
        "launcher_timeout_seconds": launcher_timeout_seconds,
        "invocation_id": invocation_id,
        "build_file": str(build),
        "build_digest": digest,
        "salt": salt,
        "process_id": process_id,
        "requested_at": int(time.time()),
        "status": "pending",
    }
    _admissions_dir().mkdir(parents=True, exist_ok=True)
    with _requests_path().open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(request, sort_keys=True) + "\n")
    return request


def admit_approve(phrase: str | None = None, *, approver: str = "mike", now: float | None = None) -> dict:
    test_mode = phrase is not None or now is not None
    displayed_ids: set[str] = set()
    if test_mode:
        home = _d85_home().resolve()
        temp_root = Path(tempfile.gettempdir()).resolve()
        if (os.environ.get("RIG_D85_TEST_PHRASE") != "1"
                or _TEST_HOME is None
                or home == (_FIXED_HOME / ".rig/d85").resolve()
                or home == temp_root or not home.is_relative_to(temp_root)
                or any(not path.resolve().is_relative_to(home)
                       for path in (_requests_path(), _approvals_path(), _key_path()))):
            raise AdmissionDenied("[d85] supplied approval phrase/clock is test-only and requires an isolated temporary D85 home")
        how = "test-phrase"
    else:
        pending_for_display = [
            record
            for record in _read_records(_requests_path())
            if record.get("status") == "pending"
        ][-20:]
        if not pending_for_display:
            raise AdmissionDenied("[d85] no pending admission requests to review")
        try:
            with open("/dev/tty", "r+", encoding="utf-8") as tty:
                if not tty.isatty():
                    raise AdmissionDenied("[d85] approval requires an interactive TTY")
                tty.write("Pending D85 admission scopes:\n")
                for pending_record in pending_for_display:
                    if pending_record.get("schema") == _BG_REQUEST_SCHEMA:
                        summary_keys = (
                            "admission_id",
                            "schema",
                            "action",
                            "session_key",
                            "reason",
                            "paths",
                            "nonce",
                            "verifier_sha256",
                            "ttl_seconds",
                            "requested_at",
                            "review_expires_at",
                            "salt",
                        )
                    else:
                        summary_keys = (
                            "admission_id",
                            "session_key",
                            "process_id",
                            "build_digest",
                            "paths",
                            "launcher_digests",
                            "launcher_invocations",
                            "launcher_dependencies",
                            "launcher_environment_sha256",
                            "policy_sha256",
                            "launcher_python",
                            "launcher_python_sha256",
                            "launcher_timeout_seconds",
                            "invocation_id",
                        )
                    summary = {
                        key: pending_record.get(key)
                        for key in summary_keys
                    }
                    displayed_ids.add(str(pending_record.get("admission_id")))
                    tty.write(json.dumps(summary, sort_keys=True) + "\n")
                tty.write("type: APPROVE <admission_id>\n")
                tty.flush()
                phrase = tty.readline()
        except OSError as exc:
            raise AdmissionDenied(f"[d85] approval requires an interactive TTY: {exc}") from exc
        how = "typed-approve"
    m = re.fullmatch(r"\s*APPROVE\s+(d85adm_[0-9a-f]{12})\s*", phrase or "")
    if not m:
        bg_match = re.fullmatch(
            r"\s*APPROVE\s+(d85bg_[0-9a-f]{12})\s*", phrase or "")
        if not bg_match:
            raise AdmissionDenied(
                '[d85] admit-approve requires the exact phrase "APPROVE <admission_id>"')
        admission_id = bg_match.group(1)
        if not test_mode and admission_id not in displayed_ids:
            raise AdmissionDenied(
                "[d85] approval ID was not among the displayed pending scopes")
        return _approve_break_glass(
            admission_id,
            how,
            approver=approver,
            now=time.time() if now is None else now,
        )
    admission_id = m.group(1)
    if not test_mode and admission_id not in displayed_ids:
        raise AdmissionDenied("[d85] approval ID was not among the displayed pending scopes")
    pending = [r for r in _read_records(_requests_path())
               if r.get("admission_id") == admission_id and r.get("status") == "pending"]
    if not pending:
        raise AdmissionDenied(f"[d85] no pending admission request {admission_id} — fail closed")
    req = pending[-1]
    test_paths = [
        req.get("build_file", ""),
        *req.get("paths", []),
        *req.get("launchers", []),
        *[
            invocation.get("cwd", "")
            for invocation in (req.get("launcher_invocations") or {}).values()
            if isinstance(invocation, dict)
        ],
        *list((req.get("launcher_dependencies") or {}).keys()),
    ]
    if test_mode and any(
        not Path(str(path)).resolve().is_relative_to(temp_root)
        for path in test_paths
    ):
        raise AdmissionDenied(
            "[d85] test approvals cannot cover non-temporary builds, outputs, launchers, or cwd")
    if not req.get("paths") and not req.get("launchers"):
        raise AdmissionDenied("[d85] admission requires at least one path or launcher — fail closed.")
    launcher_digests = {str(k): v for k, v in (req.get("launcher_digests") or {}).items()}
    launcher_invocations = req.get("launcher_invocations") or {}
    launchers = [str(value) for value in req.get("launchers", [])]
    launcher_dependencies = req.get("launcher_dependencies") or {}
    if (
        not isinstance(launcher_dependencies, dict)
        or any(
            not isinstance(path, str)
            or not isinstance(digest, str)
            or not re.fullmatch(r"[0-9a-f]{64}", digest)
            for path, digest in launcher_dependencies.items()
        )
    ):
        raise AdmissionDenied("[d85] pending request has malformed launcher dependencies")
    output_bindings = req.get("output_bindings")
    if not isinstance(output_bindings, dict) or sorted(output_bindings) != sorted(req.get("paths", [])):
        raise AdmissionDenied("[d85] pending request lacks exact output path bindings")
    _output_bindings_unchanged(req)
    if launchers and sorted(launcher_digests) != sorted(launchers):
        raise AdmissionDenied(
            f"[d85] pending request {admission_id} lacks digests for every launcher — fail closed.")
    for launcher in launchers:
        path = Path(launcher)
        if (
            not path.is_file()
            or hashlib.sha256(path.read_bytes()).hexdigest()
            != launcher_digests.get(launcher)
        ):
            raise AdmissionDenied(
                f"[d85] launcher changed after request: {launcher}")
    if launchers and (
        not isinstance(launcher_invocations, dict)
        or sorted(launcher_invocations) != sorted(launchers)
    ):
        raise AdmissionDenied(
            f"[d85] pending request {admission_id} lacks exact invocation data for every launcher — fail closed.")
    environment_sha256 = req.get("launcher_environment_sha256")
    policy_sha256 = req.get("policy_sha256")
    if policy_sha256 != _policy_sha256():
        raise AdmissionDenied("[d85] pending request has a stale policy binding")
    launcher_python = req.get("launcher_python")
    launcher_python_sha256 = req.get("launcher_python_sha256")
    timeout_seconds = req.get("launcher_timeout_seconds")
    invocation_id = req.get("invocation_id")
    if environment_sha256 != _canonical_hash(_clean_subprocess_env()):
        raise AdmissionDenied("[d85] pending request has a stale launcher environment binding")
    if launchers:
        if (
            isinstance(timeout_seconds, bool)
            or not isinstance(timeout_seconds, (int, float))
            or not math.isfinite(float(timeout_seconds))
            or not 0 < float(timeout_seconds) <= MAX_LAUNCHER_SECONDS
        ):
            raise AdmissionDenied("[d85] pending request has an invalid launcher timeout")
        if launcher_dependencies != _launcher_dependency_digests(Path(launchers[0])):
            raise AdmissionDenied("[d85] launcher dependencies changed after request")
        if (
            launcher_python != _FIXED_PYTHON
            or not isinstance(launcher_python_sha256, str)
            or not re.fullmatch(r"[0-9a-f]{64}", launcher_python_sha256)
            or not Path(_FIXED_PYTHON).is_file()
            or hashlib.sha256(Path(_FIXED_PYTHON).read_bytes()).hexdigest()
            != launcher_python_sha256
        ):
            raise AdmissionDenied("[d85] pending request has a stale fixed-Python binding")
        expected_invocation_id = "d85run_" + _canonical_hash(
            {
                "session_key": req.get("session_key"),
                "launcher_invocations": launcher_invocations,
                "launcher_dependencies": launcher_dependencies,
                "environment_sha256": environment_sha256,
                "launcher_python": launcher_python,
                "launcher_python_sha256": launcher_python_sha256,
                "timeout_seconds": timeout_seconds,
                "policy_sha256": policy_sha256,
                "salt": req.get("salt", ""),
            }
        )[:16]
        if invocation_id != expected_invocation_id:
            raise AdmissionDenied("[d85] pending request has an invalid invocation identity")
    elif (
        timeout_seconds is not None
        or invocation_id is not None
        or launcher_invocations
        or launcher_dependencies
        or launcher_python is not None
        or launcher_python_sha256 is not None
    ):
        raise AdmissionDenied("[d85] path-only request contains launcher execution fields")
    expected_id = "d85adm_" + _canonical_hash({
        "build_digest": req.get("build_digest"),
        "paths": req.get("paths", []),
        "output_bindings": output_bindings,
        "session_key": req.get("session_key"),
        "process_id": req.get("process_id"),
        "launchers": launchers,
        "launcher_digests": launcher_digests,
        "launcher_invocations": launcher_invocations,
        "launcher_dependencies": launcher_dependencies,
        "launcher_environment_sha256": environment_sha256,
        "policy_sha256": policy_sha256,
        "launcher_python": launcher_python,
        "launcher_python_sha256": launcher_python_sha256,
        "launcher_timeout_seconds": timeout_seconds,
        "invocation_id": invocation_id,
        "salt": req.get("salt", ""),
    })[:12]
    if admission_id != expected_id or not req.get("salt"):
        raise AdmissionDenied(
            f"[d85] pending request {admission_id} fails ID recomputation — re-request, fail closed")
    build = Path(str(req["build_file"]))
    if not build.is_file() or hashlib.sha256(build.read_bytes()).hexdigest() != req.get("build_digest"):
        raise AdmissionDenied(f"[d85] build file changed since request {admission_id} — re-request, fail closed")
    cert = _build_compliant_bound(str(build), str(req["process_id"]))
    if not (cert.get("verdict") == "CHECKLIST_PASS" and cert.get("inventory_binding") == "bound"):
        raise AdmissionDenied("[d85] checklist did not return a bound CHECKLIST_PASS — fail closed.")
    ttl = load_config()["ttl_hours"] * 3600
    fd, temporary = tempfile.mkstemp(dir=str(build.parent), prefix=".certificate-", suffix=".json")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            handle.write(json.dumps(cert, sort_keys=True) + "\n")
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, build.parent / "certificate.json")
    except BaseException:
        try:
            os.unlink(temporary)
        except OSError:
            pass
        raise
    issued = time.time() if now is None else now
    record = {
        "schema": ADMISSION_SCHEMA,
        "admission_id": admission_id,
        "session_key": req["session_key"],
        "paths": req["paths"],
        "output_bindings": output_bindings,
        "launchers": launchers,
        "launcher_digests": launcher_digests,
        "launcher_invocations": launcher_invocations,
        "launcher_dependencies": launcher_dependencies,
        "launcher_environment_sha256": environment_sha256,
        "policy_sha256": policy_sha256,
        "launcher_python": launcher_python,
        "launcher_python_sha256": launcher_python_sha256,
        "launcher_timeout_seconds": timeout_seconds,
        "invocation_id": invocation_id,
        "build_file": req["build_file"],
        "build_digest": req["build_digest"],
        "process_id": req["process_id"],
        "how": how,
        "by": approver,
        "issued_at": issued,
        "expires_at": min(issued + ttl, issued + MAX_LIFETIME_SECONDS),
    }
    key = _init_ledger()
    signature = hmac.new(key, _canonical_bytes(record), hashlib.sha256).hexdigest()
    entry = {**record, "signature": signature}
    with _approvals_path().open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(entry, sort_keys=True) + "\n")
    return entry


def admit_status() -> dict:
    try:
        config = load_config()
    except AdmissionDenied as exc:
        config = {"error": str(exc)}
    fields = (
        "admission_id",
        "session_key",
        "paths",
        "output_bindings",
        "launchers",
        "launcher_digests",
        "launcher_invocations",
        "launcher_dependencies",
        "launcher_environment_sha256",
        "policy_sha256",
        "launcher_python",
        "launcher_python_sha256",
        "launcher_timeout_seconds",
        "invocation_id",
        "expires_at",
    )
    requests = [
        {key: record.get(key) for key in fields if key != "expires_at"}
        | {"status": record.get("status")}
        for record in _read_records(_requests_path())
    ][-20:]
    approvals = [
        {key: record.get(key) for key in fields}
        for record in _read_records(_approvals_path())
    ][-20:]
    return {
        "config": config,
        "requests": requests,
        "approvals": approvals,
    }


def _execution_claim_path(cover: dict) -> Path:
    invocation_id = cover.get("invocation_id")
    if not isinstance(invocation_id, str) or not re.fullmatch(r"d85run_[0-9a-f]{16}", invocation_id):
        raise AdmissionDenied("[d85-run] signed admission lacks a valid invocation identity")
    return _executions_dir() / f"{invocation_id}.json"


def _claim_launcher_execution(
    cover: dict,
    argv: list[str],
    cwd: str,
    session_key_: str,
) -> None:
    home = _d85_home().resolve()
    directory = _executions_dir()
    directory_was_present = directory.exists()
    directory.mkdir(parents=True, exist_ok=True)
    if not directory_was_present:
        _fsync_directory(_admissions_dir())
    if directory.is_symlink() or not directory.resolve().is_relative_to(home):
        raise AdmissionDenied("[d85-run] execution-claim directory escapes D85 authority")
    claim = _execution_claim_path(cover)
    payload = {
        "schema": "rig.d85.launcher-execution.v2",
        "admission_id": cover["admission_id"],
        "invocation_id": cover["invocation_id"],
        "session_key": session_key_,
        "argv": argv,
        "cwd": cwd,
        "environment_sha256": cover["launcher_environment_sha256"],
        "claimed_at": time.time(),
    }
    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL
    if hasattr(os, "O_NOFOLLOW"):
        flags |= os.O_NOFOLLOW
    try:
        fd = os.open(claim, flags, 0o600)
    except FileExistsError as exc:
        raise AdmissionDenied(f"[d85-run] invocation {cover['invocation_id']} was already consumed") from exc
    with os.fdopen(fd, "wb") as handle:
        handle.write(_canonical_bytes(payload) + b"\n")
        handle.flush()
        os.fsync(handle.fileno())
    directory_fd = os.open(directory, os.O_RDONLY)
    try:
        os.fsync(directory_fd)
    finally:
        os.close(directory_fd)


def _launcher_security_snapshot(cover: dict, script: Path) -> dict[str, str]:
    python_path = Path(_FIXED_PYTHON)
    if (
        cover.get("launcher_python") != _FIXED_PYTHON
        or not python_path.is_file()
        or hashlib.sha256(python_path.read_bytes()).hexdigest()
        != cover.get("launcher_python_sha256")
    ):
        raise AdmissionDenied("[d85-run] fixed Python changed after approval")
    skill_root = Path(__file__).resolve().parent
    certificate = Path(str(cover["build_file"])).parent / "certificate.json"
    paths = {
        "admission_module": Path(__file__).resolve(),
        "d85_inventory": skill_root / "d85.py",
        "d85_gates": skill_root / "d85_gates.py",
        "tool_selection": skill_root / "tool_selection.py",
        "d85_cli": D85_CLI.resolve(),
        "launcher_python": python_path.resolve(),
        "build": Path(str(cover["build_file"])).resolve(),
        "certificate": certificate.resolve(),
        "launcher": script.resolve(),
        "ledger_key": _key_path().resolve(),
    }
    for index, (dependency, expected) in enumerate(
        sorted((cover.get("launcher_dependencies") or {}).items())
    ):
        path = Path(dependency).resolve()
        actual = hashlib.sha256(path.read_bytes()).hexdigest() if path.is_file() else ""
        if actual != expected:
            raise AdmissionDenied(f"[d85-run] launcher dependency changed: {path}")
        paths[f"launcher_dependency_{index}"] = path
    snapshot = {}
    for label, path in paths.items():
        if not path.is_file():
            raise AdmissionDenied(f"[d85-run] protected {label} file is missing: {path}")
        snapshot[label] = hashlib.sha256(path.read_bytes()).hexdigest()
    return snapshot


def _terminate_launcher(process: subprocess.Popen, grace_seconds: float = 2.0) -> None:
    """Terminate the only sandbox process; process-fork is kernel-denied."""
    if process.poll() is not None:
        return
    process.terminate()
    try:
        process.wait(timeout=grace_seconds)
    except subprocess.TimeoutExpired:
        process.kill()
        process.wait()


def run_launcher(argv: list[str], *, session_key_: str) -> int:
    """Supervise one exact, signed, one-use launcher invocation."""
    if not isinstance(session_key_, str) or not session_key_.startswith("sid:") or not session_key_[4:].strip():
        print("[d85-run] a real --session-key sid:<session-id> is required", file=sys.stderr)
        return 2
    if not argv:
        print("usage: d85-run --session-key sid:<id> <script> [args...]", file=sys.stderr)
        return 2
    script = Path(os.path.expanduser(argv[0])).resolve()
    if not script.is_file():
        print(f"[d85-run] script not found: {script}", file=sys.stderr)
        return 2
    bound_argv = [str(script), *argv[1:]]
    cwd = str(Path.cwd().resolve())
    try:
        config = load_config()
        cover = _launcher_authorized(script, bound_argv, session_key_, cwd)
        if _SANDBOX_EXEC is None:
            raise AdmissionDenied(
                "[d85-run] /usr/bin/sandbox-exec unavailable — cannot enforce the OS write boundary")
        sandbox = _sandbox_argv(config, cover, script, bound_argv)
        before = _launcher_security_snapshot(cover, script)
        remaining = float(cover["expires_at"]) - time.time()
        timeout_seconds = min(float(cover["launcher_timeout_seconds"]), remaining)
        if timeout_seconds <= 0:
            raise AdmissionDenied("[d85-run] execution lease expired before launch")
        _claim_launcher_execution(cover, bound_argv, cwd, session_key_)
        process = subprocess.Popen(
            sandbox,
            cwd=cwd,
            env=_clean_subprocess_env(),
        )
        try:
            return_code = process.wait(timeout=timeout_seconds)
        except subprocess.TimeoutExpired:
            _terminate_launcher(process)
            raise AdmissionDenied(
                "[d85-run] execution exceeded its signed timeout and was terminated")
        except BaseException:
            _terminate_launcher(process)
            raise
        _terminate_launcher(process, grace_seconds=0.1)
        after = _launcher_security_snapshot(cover, script)
        if after != before:
            raise AdmissionDenied(
                "[d85-run] protected authority or executable bytes changed during execution")
        _build_unchanged(cover)
        certificate = Path(str(cover["build_file"])).parent / "certificate.json"
        result = _run_d85([
            "verify-cert",
            str(cover["build_file"]),
            str(certificate),
            "--root",
            str(_inventory_root(str(cover["build_file"]))),
        ])
        if result.returncode != 0:
            raise AdmissionDenied("[d85-run] post-execution certificate verification failed")
        return return_code
    except (AdmissionDenied, OSError) as exc:
        print(str(exc), file=sys.stderr)
        return 2


def _sandbox_argv(cfg: dict, cover: dict, script: Path, argv: list[str]) -> list[str]:
    """Deny writes to production, D85 authority, release, and bound executable state."""
    allow_literals = sorted({str(path) for path in cover.get("paths", [])})
    fixed_roots = {_abs(root, None) for root in _static_security_roots()}
    roots = sorted({_abs(root, None) for root in cfg["roots"]} | fixed_roots)
    certificate = Path(str(cover["build_file"])).parent / "certificate.json"
    protected_literals = sorted({
        _abs(script, None),
        _abs(cover["build_file"], None),
        _abs(certificate, None),
        _abs(_key_path(), None),
        _abs(_approvals_path(), None),
        _abs(_requests_path(), None),
        _abs(D85_CLI, None),
        _abs(_FIXED_PYTHON, None),
        *(_abs(value, None) for value in (cover.get("launcher_dependencies") or {})),
    })
    for allowed in allow_literals:
        resolved = Path(allowed).resolve(strict=False)
        if (
            allowed in protected_literals
            or any(resolved == Path(root) or resolved.is_relative_to(Path(root)) for root in fixed_roots)
        ):
            raise AdmissionDenied("[d85-run] outputs may not overlap protected authority or executable state")
    for literal in [*allow_literals, *roots, *protected_literals]:
        if not re.fullmatch(r"[A-Za-z0-9_./@+-]+", literal):
            raise AdmissionDenied(
                f"[d85-run] path contains characters outside the SBPL-safe charset: {literal!r}")
    allows = "".join(
        f'(allow file-write* (literal "{allowed}"))'
        for allowed in allow_literals
    )
    profile = (
        f'(version 1)(allow default)(deny network*)(deny process-fork)'
        f'(deny file-write*){allows}'
    )
    dependency_digests = cover.get("launcher_dependencies") or {}
    dependency_manifest = {
        Path(path).stem: {"path": str(path), "sha256": digest}
        for path, digest in dependency_digests.items()
    }
    if len(dependency_manifest) != len(dependency_digests) or any(
        not name.isidentifier() for name in dependency_manifest
    ):
        raise AdmissionDenied(
            "[d85-run] launcher dependencies do not form one unique top-level module manifest")
    script_digest = (cover.get("launcher_digests") or {}).get(str(script))
    if not isinstance(script_digest, str) or not re.fullmatch(r"[0-9a-f]{64}", script_digest):
        raise AdmissionDenied("[d85-run] signed launcher digest is missing")
    manifest_json = json.dumps(
        {
            "script": {"path": str(script), "sha256": script_digest},
            "dependencies": dependency_manifest,
        },
        sort_keys=True,
        separators=(",", ":"),
    )
    return [
        _SANDBOX_EXEC,
        "-p",
        profile,
        _FIXED_PYTHON,
        "-I",
        "-B",
        "-S",
        "-c",
        _LAUNCHER_BOOTSTRAP,
        manifest_json,
        str(script),
        *argv[1:],
    ]


_SANDBOX_EXEC = "/usr/bin/sandbox-exec" if Path("/usr/bin/sandbox-exec").is_file() else None


def _launcher_authorized(
    script: Path,
    argv: list[str],
    session_key_: str,
    cwd: str,
) -> dict:
    current = time.time()
    ledger_key = _load_key()
    cover = None
    for record in reversed(_read_records(_approvals_path())):
        if record.get("schema") != ADMISSION_SCHEMA:
            continue
        _verify_signature(record, ledger_key)
        if not (float(record.get("issued_at", 0)) <= current < float(record.get("expires_at", 0))):
            continue
        invocation = record.get("launcher_invocations", {}).get(str(script))
        if (
            record.get("session_key") != session_key_
            or invocation != {"argv": argv, "cwd": cwd}
            or str(script) not in [str(value) for value in record.get("launchers", [])]
            or record.get("launcher_environment_sha256")
            != _canonical_hash(_clean_subprocess_env())
            or record.get("policy_sha256") != _policy_sha256()
            or record.get("launcher_python") != _FIXED_PYTHON
            or not Path(_FIXED_PYTHON).is_file()
            or hashlib.sha256(Path(_FIXED_PYTHON).read_bytes()).hexdigest()
            != record.get("launcher_python_sha256")
        ):
            continue
        timeout_seconds = record.get("launcher_timeout_seconds")
        if (
            isinstance(timeout_seconds, bool)
            or not isinstance(timeout_seconds, (int, float))
            or not math.isfinite(float(timeout_seconds))
            or not 0 < float(timeout_seconds) <= MAX_LAUNCHER_SECONDS
        ):
            continue
        if _execution_claim_path(record).exists():
            continue
        expected_digest = record.get("launcher_digests", {}).get(str(script))
        actual_digest = hashlib.sha256(script.read_bytes()).hexdigest() if script.is_file() else ""
        if (
            not expected_digest
            or not re.fullmatch(r"[0-9a-f]{64}", str(expected_digest))
            or expected_digest != actual_digest
        ):
            continue
        try:
            _output_bindings_unchanged(record)
            if record.get("launcher_dependencies") != _launcher_dependency_digests(script):
                raise AdmissionDenied("[d85-run] launcher dependencies changed")
            _build_unchanged(record)
        except AdmissionDenied:
            continue
        cover = record
        break
    if cover is None:
        raise AdmissionDenied(
            f"[d85-run] no unconsumed signed admission covers this exact session/cwd/argv for {script}")
    certificate = Path(str(cover["build_file"])).parent / "certificate.json"
    if not certificate.is_file():
        raise AdmissionDenied(f"[d85-run] certificate missing beside build: {certificate}")
    result = _run_d85([
        "verify-cert",
        str(cover["build_file"]),
        str(certificate),
        "--root",
        str(_inventory_root(str(cover["build_file"]))),
    ])
    if result.returncode != 0:
        raise AdmissionDenied(
            f"[d85-run] live verification failed (exit {result.returncode}): "
            f"{(result.stdout or result.stderr)[:300]}")
    return cover
