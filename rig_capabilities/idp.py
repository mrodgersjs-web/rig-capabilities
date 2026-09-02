"""Org IdP — HMAC requester tokens (stdlib).

Token format: v1.<b64url(agent)>.<exp_unix>.<b64url(hmac-sha256)>
Key: same `.signing.key` / RIG_CAPABILITIES_SIGNING_KEY as pack signatures.

No key → issue/verify fail honestly. Operator CLI may still pass a bare
`--requester` string; `--token` is the authenticated path.
"""
from __future__ import annotations

import base64
import hashlib
import hmac
import time

from .surface import generate_key, load_key


def _b64(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).decode().rstrip("=")


def _unb64(s: str) -> bytes:
    pad = "=" * (-len(s) % 4)
    return base64.urlsafe_b64decode(s + pad)


# Every way a requester can lie about a token. The verifier must refuse all of
# them; `guard_report` is the standing proof that it does.
_FORGERIES = ("expiry", "signature", "principal")


def guard_report(probe, foreign) -> dict:
    """Prove the verifier is a *guard*, not a formality.

    Lives here, beside `issue_token`/`verify_token`, for two reasons. It is the
    owning module's business what a forgery means. And `certify.self_test`
    copytrees the repo and replants per gate — a plant that edited `certify.py`
    itself would be a no-op, because the running process already holds that
    module in `sys.modules`, and a plant that is never executed reads GREEN
    forever. A plant may only edit a module that is still lazily imported.

    The three negatives are refused by construction, so the verdict ends in a
    MUST-NOT-ACCEPT posture: weaken any refusal and this returns not-ok.
    """
    iss = issue_token(probe, "jake")
    if not iss.get("ok"):
        return {"ok": False, "detail": f"issue failed: {iss.get('error')}",
                "accepted": []}
    if verify_token(probe, iss["token"]).get("ok") is not True:
        return {"ok": False, "detail": "roundtrip rejected", "accepted": []}
    parts = iss["token"].split(".")
    forged_principal = ".".join(
        [parts[0], _b64(b"jakee"), parts[2], parts[3]])
    candidates = [
        ("expiry", ".".join([parts[0], parts[1], str(int(parts[2]) + 10),
                             parts[3]])),
        ("signature", forged_principal),
        ("principal", foreign),
    ]
    accepted = []
    for name, tok in candidates:
        if name in _FORGERIES and verify_token(probe, tok).get("ok") is True:
            accepted.append(name)
    if accepted:
        return {"ok": False, "accepted": accepted,
                "detail": "accepted forged " + ",".join(accepted)}
    return {"ok": True, "accepted": [],
            "detail": f"{len(_FORGERIES)}/{len(_FORGERIES)} forgeries refused"}


def issue_token(repo, agent: str, ttl: int = 3600, *, mint_key: bool = False) -> dict:
    key = load_key(repo)
    if not key and mint_key:
        generate_key(repo)
        key = load_key(repo)
    if not key:
        return {"ok": False, "error": "no signing key"}
    agent = (agent or "").strip()
    if not agent or any(c in agent for c in " \t\n./"):
        return {"ok": False, "error": "bad agent"}
    exp = int(time.time()) + max(60, int(ttl))
    sig = hmac.new(key, f"{agent}|{exp}".encode(), hashlib.sha256).digest()
    token = f"v1.{_b64(agent.encode())}.{exp}.{_b64(sig)}"
    return {"ok": True, "token": token, "agent": agent, "exp": exp}


def verify_token(repo, token: str, now: int | None = None) -> dict:
    key = load_key(repo)
    if not key:
        return {"ok": False, "error": "no signing key", "agent": None}
    parts = (token or "").split(".")
    if len(parts) != 4 or parts[0] != "v1":
        return {"ok": False, "error": "malformed", "agent": None}
    try:
        agent = _unb64(parts[1]).decode()
        exp = int(parts[2])
        sig = _unb64(parts[3])
    except Exception:
        return {"ok": False, "error": "malformed", "agent": None}
    if exp < int(now if now is not None else time.time()):
        return {"ok": False, "error": "expired", "agent": agent}
    expect = hmac.new(key, f"{agent}|{exp}".encode(), hashlib.sha256).digest()
    if len(sig) != len(expect) or not hmac.compare_digest(sig, expect):
        return {"ok": False, "error": "bad_sig", "agent": None}
    return {"ok": True, "agent": agent, "exp": exp, "error": None}
