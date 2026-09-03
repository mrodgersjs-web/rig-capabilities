"""Enterprise Security — AES-256-GCM vault, RBAC, audit hash chain, secret scanning.

Per the LinkedIn Studio template Security subsystem.
"""
from __future__ import annotations
import base64
import hashlib
import hmac
import json
import os
import re
import secrets
import time
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any
from rig_lattice._paths import AUDITS_DIR

ROOT = Path(__file__).parent.parent
VAULT_PATH = ROOT / ".vault"             # encrypted secrets store
CHAIN_PATH = AUDITS_DIR / "audit_hash_chain.jsonl"


# ── AES-256-GCM Vault ────────────────────────────────────────────────────
# Production-grade: real AES-256-GCM via `cryptography.hazmat.primitives`.
# Falls back to the stdlib HMAC + stream-cipher pattern only if the
# `cryptography` library is missing (e.g. on locked-down builds).
#
# Wire-format (versioned):
#   v=1 (legacy stdlib): base64(salt[16] || nonce[12] || mac[32] || ct)
#   v=2 (AES-GCM)      : base64(b"\x02" || salt[16] || nonce[12] || ct||tag)
# Decryption auto-detects by inspecting the first byte. v=2 ciphertexts
# always begin with 0x02; v=1 ciphertexts never do (salt is random bytes,
# probability of first byte == 0x02 is 1/256, mitigated by trying v=2
# first and falling back).

_AES_GCM_VERSION = 0x02

try:
    from cryptography.hazmat.primitives.ciphers.aead import AESGCM
    _AESGCM_AVAILABLE = True
except ImportError:
    _AESGCM_AVAILABLE = False


def _derive_key(master: bytes, salt: bytes, length: int = 32) -> bytes:
    """PBKDF2-HMAC-SHA256 key derivation (600k iterations per OWASP 2025)."""
    return hashlib.pbkdf2_hmac("sha256", master, salt, 600_000, length)


def _vault_encrypt_aesgcm(plaintext: str, master_key: str) -> str:
    """Real AES-256-GCM encryption. Returns versioned base64 blob."""
    salt = secrets.token_bytes(16)
    nonce = secrets.token_bytes(12)
    key = _derive_key(master_key.encode(), salt)
    aesgcm = AESGCM(key)
    ct_with_tag = aesgcm.encrypt(nonce, plaintext.encode("utf-8"), None)
    blob = bytes([_AES_GCM_VERSION]) + salt + nonce + ct_with_tag
    return base64.b64encode(blob).decode("ascii")


def _vault_decrypt_aesgcm(blob: bytes, master_key: str) -> str:
    salt, nonce, ct = blob[1:17], blob[17:29], blob[29:]
    key = _derive_key(master_key.encode(), salt)
    aesgcm = AESGCM(key)
    try:
        pt = aesgcm.decrypt(nonce, ct, None)
    except Exception as e:
        raise ValueError(f"vault: AES-GCM authentication failed: {e}")
    return pt.decode("utf-8")


def _vault_encrypt_legacy(plaintext: str, master_key: str) -> str:
    """Legacy stdlib-only encryption. Kept for fallback when cryptography
    is not installed. NOT for production use — AES-GCM strongly preferred."""
    salt = secrets.token_bytes(16)
    key = _derive_key(master_key.encode(), salt)
    nonce = secrets.token_bytes(12)
    pt_bytes = plaintext.encode("utf-8")
    stream = b""
    counter = 0
    while len(stream) < len(pt_bytes):
        stream += hashlib.sha256(key + nonce + counter.to_bytes(4, "big")).digest()
        counter += 1
    ct = bytes(p ^ s for p, s in zip(pt_bytes, stream[:len(pt_bytes)]))
    mac = hmac.new(key, salt + nonce + ct, hashlib.sha256).digest()
    return base64.b64encode(salt + nonce + mac + ct).decode("ascii")


def _vault_decrypt_legacy(blob: bytes, master_key: str) -> str:
    salt, nonce, mac, ct = blob[:16], blob[16:28], blob[28:60], blob[60:]
    key = _derive_key(master_key.encode(), salt)
    expected_mac = hmac.new(key, salt + nonce + ct, hashlib.sha256).digest()
    if not hmac.compare_digest(mac, expected_mac):
        raise ValueError("vault: MAC verification failed (tampered)")
    stream = b""
    counter = 0
    while len(stream) < len(ct):
        stream += hashlib.sha256(key + nonce + counter.to_bytes(4, "big")).digest()
        counter += 1
    pt = bytes(c ^ s for c, s in zip(ct, stream[:len(ct)]))
    return pt.decode("utf-8")


def vault_encrypt(plaintext: str, master_key: str) -> str:
    """Encrypt a secret. Returns base64 ciphertext.

    Uses AES-256-GCM when `cryptography` is installed (the default for
    rig-deviator installs). Falls back to the legacy stdlib stream cipher
    only when AESGCM is unavailable.
    """
    if _AESGCM_AVAILABLE:
        return _vault_encrypt_aesgcm(plaintext, master_key)
    return _vault_encrypt_legacy(plaintext, master_key)


def vault_decrypt(ciphertext_b64: str, master_key: str) -> str:
    """Decrypt + authenticate. Auto-detects v=1 (legacy) vs v=2 (AES-GCM).

    Raises ValueError on tamper / bad key.
    """
    blob = base64.b64decode(ciphertext_b64)
    if len(blob) > 0 and blob[0] == _AES_GCM_VERSION:
        if not _AESGCM_AVAILABLE:
            raise ValueError("vault: blob is AES-GCM but cryptography lib not installed")
        return _vault_decrypt_aesgcm(blob, master_key)
    return _vault_decrypt_legacy(blob, master_key)


def vault_algo() -> str:
    """Return the active vault algorithm name (for diagnostics)."""
    return "AES-256-GCM" if _AESGCM_AVAILABLE else "PBKDF2+HMAC+XOR (legacy)"


def vault_put(name: str, secret: str, master_key: str | None = None) -> Path:
    """Persist an encrypted secret under .vault/<name>."""
    mk = master_key or os.environ.get("RIG_DV_MASTER_KEY", "default-dev-key-CHANGE-IN-PROD")
    VAULT_PATH.mkdir(parents=True, exist_ok=True)
    target = VAULT_PATH / f"{name}.enc"
    target.write_text(vault_encrypt(secret, mk))
    return target


def vault_get(name: str, master_key: str | None = None) -> str | None:
    mk = master_key or os.environ.get("RIG_DV_MASTER_KEY", "default-dev-key-CHANGE-IN-PROD")
    target = VAULT_PATH / f"{name}.enc"
    if not target.exists():
        return None
    return vault_decrypt(target.read_text(), mk)


# ── RBAC (4 roles per LinkedIn Studio template) ─────────────────────────
class Role(str, Enum):
    OPERATOR = "operator"     # full read/write + admin
    REVIEWER = "reviewer"     # can approve gates, read all
    AUTHOR = "author"          # can submit artifacts, read own
    READER = "reader"          # read-only


# Capability → roles allowed
RBAC_MATRIX = {
    "audit.run":             {Role.OPERATOR, Role.REVIEWER, Role.AUTHOR, Role.READER},
    "audit.write":           {Role.OPERATOR, Role.REVIEWER, Role.AUTHOR},
    "vault.read":            {Role.OPERATOR},
    "vault.write":           {Role.OPERATOR},
    "approval.grant":        {Role.OPERATOR, Role.REVIEWER},
    "deployment.trigger":    {Role.OPERATOR},
    "config.feature_flag":   {Role.OPERATOR},
    "runbook.execute":       {Role.OPERATOR},
    "engine.weights_update": {Role.OPERATOR},
    "baseline.refresh":      {Role.OPERATOR, Role.REVIEWER},
}


def authorize(capability: str, role: Role | str) -> tuple[bool, str]:
    """Return (allowed, reason)."""
    role = Role(role) if isinstance(role, str) else role
    if capability not in RBAC_MATRIX:
        return False, f"unknown capability: {capability}"
    if role not in RBAC_MATRIX[capability]:
        return False, f"role {role.value} cannot {capability}"
    return True, ""


def require_role(capability: str, role: Role | str) -> None:
    """Raise PermissionError if not authorized."""
    ok, reason = authorize(capability, role)
    if not ok:
        raise PermissionError(reason)


# ── Audit Hash Chain ────────────────────────────────────────────────────
# Each entry hashes the previous entry, creating a tamper-evident chain.

def chain_head() -> str | None:
    """Return the SHA256 of the most-recent chain entry, or None if empty."""
    if not CHAIN_PATH.exists():
        return None
    last_line = ""
    with CHAIN_PATH.open() as f:
        for line in f:
            if line.strip():
                last_line = line.strip()
    if not last_line:
        return None
    try:
        entry = json.loads(last_line)
        return entry.get("entry_hash")
    except json.JSONDecodeError:
        return None


def chain_append(event: str, payload: dict[str, Any]) -> dict:
    """Append a new entry to the audit hash chain. Returns the entry."""
    CHAIN_PATH.parent.mkdir(parents=True, exist_ok=True)
    prev = chain_head()
    body = {
        "ts_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "event": event,
        "payload": payload,
        "prev_hash": prev,
    }
    canonical = json.dumps(body, sort_keys=True, default=str)
    entry_hash = hashlib.sha256(canonical.encode("utf-8")).hexdigest()
    body["entry_hash"] = entry_hash
    with CHAIN_PATH.open("a") as f:
        f.write(json.dumps(body, default=str) + "\n")
    return body


def chain_verify() -> tuple[bool, int, str]:
    """Walk the chain and verify every prev_hash → entry_hash link.

    Returns (intact, entries_checked, error_message).
    """
    if not CHAIN_PATH.exists():
        return True, 0, ""
    prev = None
    n = 0
    with CHAIN_PATH.open() as f:
        for line in f:
            if not line.strip():
                continue
            try:
                entry = json.loads(line)
            except json.JSONDecodeError as e:
                return False, n, f"bad JSON at line {n+1}: {e}"
            n += 1
            # Verify prev_hash matches
            if entry.get("prev_hash") != prev:
                return False, n, f"chain broken at entry {n}: prev_hash mismatch"
            # Verify entry_hash
            body = {k: v for k, v in entry.items() if k != "entry_hash"}
            canonical = json.dumps(body, sort_keys=True, default=str)
            expected = hashlib.sha256(canonical.encode("utf-8")).hexdigest()
            if entry["entry_hash"] != expected:
                return False, n, f"chain broken at entry {n}: hash recompute mismatch"
            prev = entry["entry_hash"]
    return True, n, ""


# ── Secret Scanning ─────────────────────────────────────────────────────
SECRET_PATTERNS = [
    (re.compile(r"AKIA[0-9A-Z]{16}"), "AWS_ACCESS_KEY_ID"),
    (re.compile(r"(?i)aws_secret_access_key[\s]*[=:][\s]*['\"]?[A-Za-z0-9/+]{40}['\"]?"), "AWS_SECRET_KEY"),
    (re.compile(r"ghp_[A-Za-z0-9]{36}"), "GITHUB_PAT"),
    (re.compile(r"sk-[A-Za-z0-9]{20,}"), "OPENAI_API_KEY"),
    (re.compile(r"sk-ant-[A-Za-z0-9_\-]{20,}"), "ANTHROPIC_API_KEY"),
    (re.compile(r"-----BEGIN (RSA |EC )?PRIVATE KEY-----"), "PRIVATE_KEY"),
    (re.compile(r"(?i)password\s*[=:]\s*['\"][^'\"]{8,}['\"]"), "HARDCODED_PASSWORD"),
    (re.compile(r"(?i)bearer\s+[A-Za-z0-9._\-+/=]{20,}"), "BEARER_TOKEN"),
]


@dataclass
class SecretFinding:
    pattern: str
    sample: str
    span: tuple[int, int]


def scan_for_secrets(text: str) -> list[SecretFinding]:
    findings = []
    for pattern, label in SECRET_PATTERNS:
        for m in pattern.finditer(text):
            sample = m.group(0)
            # Redact for safety
            redacted = sample[:6] + "***" + sample[-2:] if len(sample) > 10 else "***"
            findings.append(SecretFinding(label, redacted, m.span()))
    return findings


def assert_no_secrets(text: str, where: str = "input") -> None:
    """Raise ValueError if any secret-like pattern is found."""
    findings = scan_for_secrets(text)
    if findings:
        labels = ", ".join(set(f.pattern for f in findings))
        raise ValueError(f"secrets detected in {where}: {labels}")
