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
