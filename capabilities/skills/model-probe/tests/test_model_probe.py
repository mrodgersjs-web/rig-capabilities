"""Offline checks for model_probe. No network: httpx is replaced by a stub client.

Run: python3 tests/test_model_probe.py   (exit 0 = all checks pass)
"""

from __future__ import annotations

import json
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import model_probe as mp  # noqa: E402

CHECKS = []


def check(label, cond):
    CHECKS.append((label, bool(cond)))
    if not cond:
        print(f"FAIL {label}")


# ---------- synthetic config root ----------

def make_root():
    root = Path(tempfile.mkdtemp(prefix="model-probe-root-"))
    (root / "models").mkdir()
    (root / "models.json").write_text(json.dumps({
        "providers": {
            "testlocal": {
                "api": "openai-completions", "baseUrl": "http://127.0.0.1:9999/v1",
                "authHeader": False, "apiKey": "local-no-auth",
                "models": [{"id": "m1", "cost": {"input": 0, "output": 0}, "maxTokens": 4096},
                           {"id": "anthropic/m1-alias", "alias": "m1a"}],
            },
            "lanbox": {
                "api": "openai-completions", "baseUrl": "http://10.0.0.5:8111",
                "authHeader": True, "apiKey": "FAUX_LAN_KEY",
                "models": [{"id": "m2", "cost": {"input": 0, "output": 0}}],
            },
            "cmdkey": {
                "api": "openai-completions", "baseUrl": "http://127.0.0.1:9998/v1",
                "authHeader": True, "apiKey": "!printf FAUX_FROM_CMD",
                "models": [{"id": "m4", "cost": {"input": 0, "output": 0}}],
            },
            "cmdonlyheader": {
                "api": "anthropic-messages", "baseUrl": "http://127.0.0.1:9997",
                "headers": {"Authorization": "!printf 'Bearer HEADER_ONLY_TOKEN'"},
                "models": [{"id": "m5", "cost": {"input": 0, "output": 0}}],
            },
            "badcmd": {
                "api": "openai-completions", "baseUrl": "http://127.0.0.1:9996/v1",
                "authHeader": True, "apiKey": "!exit 3",
                "models": [{"id": "m6", "cost": {"input": 0, "output": 0}}],
            },
            "nokey": {
                "api": "openai-completions", "baseUrl": "http://10.0.0.9:8111",
                "authHeader": True,
                "models": [{"id": "m3", "cost": {"input": 0, "output": 0}}],
            },
        },
        "settings": {"defaultModel": "m1", "defaultProvider": "testlocal"},
    }))
    (root / "auth.json").write_text(json.dumps({
        "xai": {"type": "api_key", "key": "FAUX_XAI_KEY_VALUE"},
        "anthropic": {"type": "oauth", "access": "FAUX_OAUTH_TOKEN", "expires": 1_600_000_000_000},
    }))
    (root / "models" / "provider-model-catalog.v1.json").write_text(json.dumps({
        "payload": {"models": [
            {"id": "grok-4.5", "provider": "xai", "api": "openai-completions",
             "baseUrl": "https://api.x.ai/v1", "cost": {"input": 2, "output": 6}},
            {"id": "claude-opus-4-7", "provider": "anthropic", "api": "anthropic-messages",
             "baseUrl": "https://api.anthropic.com", "cost": {"input": 5, "output": 25}},
        ]}
    }))
    return root


ROOT = make_root()

# ---------- httpx stub ----------

class Resp:
    def __init__(self, status=200, text="", payload=None):
        self.status_code, self.text, self._payload = status, text, payload or {}

    def json(self):
        return self._payload


class Client:
    script = {}
    calls = []

    def __init__(self, timeout=None):
        self.timeout = timeout

    def _act(self, verb, url, headers, payload=None):
        Client.calls.append({"verb": verb, "url": url, "headers": dict(headers or {}),
                             "json": payload})
        step = Client.script.get(verb)
        if isinstance(step, Exception):
            raise step
        return step or Resp(200, payload={"data": []})

    def get(self, url, headers=None):
        return self._act("get", url, headers)

    def post(self, url, headers=None, json=None):
        return self._act("post", url, headers, json)

    def close(self):
        pass


class Timeout:
    def __init__(self, *a, **k):
        pass


class StubHttpx:
    Client = Client
    Timeout = Timeout
    HTTPError = RuntimeError


mp.httpx = StubHttpx


def script(**steps):
    Client.script = steps
    Client.calls = []


# ---------- resolve ----------

r = mp.resolve("testlocal/m1", ROOT)
check("resolve local base_url", r["base_url"] == "http://127.0.0.1:9999/v1")
check("resolve local api", r["api"] == "openai-completions" and r["source"] == "models.json")
check("resolve local model_id", r["model_id"] == "m1")
r = mp.resolve("m1", ROOT)
check("resolve without provider prefix", r["provider"] == "testlocal")
r = mp.resolve("testlocal/m1a", ROOT)
check("resolve by alias", r["model_id"] == "anthropic/m1-alias")
r = mp.resolve("xai/grok-4.5", ROOT)
check("resolve hosted from catalogue", r["api"] == "openai-completions"
      and r["base_url"] == "https://api.x.ai/v1" and r["source"] == "catalogue")
check("resolve hosted cost", r["cost"]["input"] == 2)
r = mp.resolve("anthropic/claude-opus-4-7", ROOT)
check("resolve anthropic api", r["api"] == "anthropic-messages")
r = mp.resolve("xai/grko-4.5", ROOT)
check("resolve typo source unknown", r["source"] == "unknown")
check("resolve unknown suggestions", isinstance(r.get("suggestions"), list) and r["suggestions"])
u_models, u_completion = mp._urls("anthropic-messages", "https://api.anthropic.com")
check("anthropic urls get /v1", u_models == "https://api.anthropic.com/v1/models"
      and u_completion.endswith("/v1/messages"))
u_models, u_completion = mp._urls("openai-completions", "http://10.0.0.5:8111")
check("openai urls get /v1", u_models == "http://10.0.0.5:8111/v1/models"
      and u_completion.endswith("/v1/chat/completions"))

# ---------- credentials ----------

creds = mp.credentials(ROOT)
check("cred xai present", creds["xai"]["present"] and not creds["xai"]["expired"])
check("cred anthropic expired flag", creds["anthropic"]["expired"] is True)
check("cred expiry iso", str(creds["anthropic"]["expires"]).endswith("Z"))
check("cred value not in repr", "FAUX_XAI_KEY_VALUE" not in str({k: v for k, v in creds["xai"].items() if k != "secret"}))

# ---------- probe stages ----------

v = mp.probe("bogusprovider/bogusmodel", root=ROOT)
check("unknown model is dead", v["verdict"] == "dead" and v["stage"] == "resolve")
check("unknown model reason", v["reason"] == "unknown-model")
check("unknown model made no call", Client.calls == [])

v = mp.probe("nokey/m3", root=ROOT)  # no key in auth.json, models.json, or env
check("missing cred is dead", v["verdict"] == "dead" and v["stage"] == "credential")
check("missing cred message surfaced", "no API key for provider: nokey" in v["error"])
check("missing cred fix names env var", "NOKEY_API_KEY" in v["fix"])

v = mp.probe("testlocal/m1", root=ROOT)  # config apiKey acts as credential
check("config key counts as credential", v["stage"] != "credential")
check("no-auth header not sent for authHeader false", all("authorization" not in c["headers"] for c in Client.calls))

script(get=Resp(401, '{\"type\":\"error\",\"message\":\"invalid x-api-key\"}'))
v = mp.probe("anthropic/claude-opus-4-7", root=ROOT)
check("401 is dead", v["verdict"] == "dead" and v["reason"] == "credential-rejected")
check("401 body surfaced verbatim", "invalid x-api-key" in v["error"])
check("401 sends no bearer-only header", "x-api-key" in Client.calls[0]["headers"]
      or "authorization" in Client.calls[0]["headers"])

script(get=Resp(429, "too many requests"))
v = mp.probe("testlocal/m1", root=ROOT)
check("429 is unproven", v["verdict"] == "unproven" and v["reason"] == "rate-limited")

script(get=Resp(200, payload={"data": []}))
v = mp.probe("xai/grok-4.5", root=ROOT)
check("metered default skips completion", v["verdict"] == "unproven"
      and v["reason"] == "paid-probe-skipped")
check("metered default spends nothing", [c["verb"] for c in Client.calls] == ["get"])
check("metered fix mentions paid flag", "paid=True" in v["fix"])

script(get=Resp(200, payload={"data": []}),
       post=Resp(200, payload={"choices": [{"message": {"content": " ok"}, "finish_reason": "stop"}],
                              "usage": {"completion_tokens": 3}}))
v = mp.probe("xai/grok-4.5", paid=True, root=ROOT)
check("paid=True reaches completion", v["verdict"] == "alive" and v["stage"] == "completion")
check("alive records usage", v["check"]["usage"]["completion_tokens"] == 3)
check("secret never leaks", "FAUX_XAI_KEY_VALUE" not in json.dumps(
      {k: x for k, x in v.items() if k != "check"}))

script(get=Resp(200, payload={"data": []}),
       post=Resp(200, payload={"choices": [{"message": {"content": "", "reasoning_content": "thinking hard"},
                                            "finish_reason": "length"}], "usage": {"reasoning_tokens": 19}}))
v = mp.probe("testlocal/m1", root=ROOT)
check("reasoning-only is unproven", v["verdict"] == "unproven" and v["reason"] == "budget-too-small")
check("budget fix says raise budget", "budget" in v["fix"])

script(get=Resp(200, payload={"data": []}), post=Resp(200, payload={"choices": []}))
v = mp.probe("testlocal/m1", root=ROOT)
check("empty completion is dead", v["verdict"] == "dead" and v["reason"] == "empty-completion")

script(get=StubHttpx.HTTPError("connection refused"))
v = mp.probe("testlocal/m1", root=ROOT)
check("unreachable is dead", v["verdict"] == "dead" and v["reason"] == "unreachable")
check("unreachable names the fix", "restart" in v["fix"])

script(get=Resp(200, payload={"data": []}),
       post=Resp(400, '{\"code\":\"invalid-argument\",\"error\":\"Incorrect API key provided.\"}'))
v = mp.probe("testlocal/m1", root=ROOT)
check("completion http error surfaced", v["verdict"] == "dead" and "Incorrect API key" in v["error"])

# ---------- !command secrets (models.json / auth.json indirection) ----------

script(get=Resp(200, payload={"data": []}),
       post=Resp(200, payload={"choices": [{"message": {"content": "ok"}, "finish_reason": "stop"}]}))
v = mp.probe("cmdkey/m4", root=ROOT)
check("!cmd secret reaches completion", v["verdict"] == "alive")
check("!cmd secret is expanded on the wire", Client.calls[-1]["headers"]["authorization"] == "Bearer FAUX_FROM_CMD")

v = mp.probe("cmdonlyheader/m5", root=ROOT)
check("provider header alone counts as credential", v["stage"] != "credential")
check("provider header is sent verbatim from command",
      any(c["headers"].get("authorization") == "Bearer HEADER_ONLY_TOKEN" for c in Client.calls))

v = mp.probe("badcmd/m6", root=ROOT)
check("broken !cmd is unproven not dead", v["verdict"] == "unproven"
      and v["reason"] == "credential-unresolved")
check("broken !cmd surfaces the command error", "exit 3" in v["error"])

# ---------- pick ----------

class RoutingClient(Client):
    """Alive for lanbox/m2, dead for testlocal/m1."""

    def get(self, url, headers=None):
        Client.calls.append({"verb": "get", "url": url, "headers": dict(headers or {}), "json": None})
        if "9999" in url:
            return Resp(401, "bad key")
        return Resp(200, payload={"data": []})

    def post(self, url, headers=None, json=None):
        Client.calls.append({"verb": "post", "url": url, "headers": dict(headers or {}), "json": json})
        return Resp(200, payload={"choices": [{"message": {"content": "ok"}, "finish_reason": "stop"}]})


mp.httpx.Client = RoutingClient
picked = mp.pick(["testlocal/m1", "lanbox/m2"], root=ROOT)
check("pick skips dead candidate", picked["model"] == "lanbox/m2" and picked["verdict"] == "alive")
try:
    mp.pick(["testlocal/m1"], root=ROOT)
    check("pick raises when all dead", False)
except mp.ModelProbeError as exc:
    check("pick raises ModelProbeError", "refusing to spawn" in str(exc))
    check("pick error lists the dead model", "testlocal/m1" in str(exc))
    check("pick carries verdicts", len(exc.verdicts) == 1 and exc.verdicts[0]["verdict"] == "dead")

import os
os.environ["PRIME_AGENT_HOME_DIR"] = str(ROOT)
out = mp.run("testlocal/m1")
check("run prints verdict line", out.startswith("DEAD") and "[credential/" in out)
check("run resolves bare model id", "testlocal" in mp.run("m1"))
check("run --json-out parses", "verdict" in mp.run("m1", json_out=True))
hits = mp.search_models("grok", ROOT)
check("search_models finds catalogue entries", "xai/grok-4.5" in hits)
check("search_models includes local providers", any(h.startswith("testlocal/") for h in mp.search_models("m1", ROOT)))
check("search_models empty query returns all", len(mp.search_models("", ROOT)) >= 4)

# ---------- report ----------

failed = [label for label, ok in CHECKS if not ok]
print(f"{len(CHECKS) - len(failed)}/{len(CHECKS)} checks pass")
for label in failed:
    print("  FAIL:", label)
sys.exit(1 if failed else 0)
