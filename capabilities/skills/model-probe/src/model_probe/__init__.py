"""Pre-spawn model probe for Prime Agent.

Prove a model selector can actually answer BEFORE a paid or child run depends on it.
A child spawned on a dead credential dies in ~45s with zero tokens and a stopReason
buried in its transcript; this surfaces the same fact in <1s (auth check) to ~20s
(real completion), as a typed verdict.

Verdicts: alive | dead | unproven.  `alive` only after a real completion returned
non-empty content (provider-probe-first law: a 200 from /models proves nothing).
Hosted (non-zero-cost) providers get a free authenticated /models check by default;
pass paid=True to let the probe spend one bounded completion there (Gate-D).
"""

from __future__ import annotations

import datetime
import difflib
import subprocess
import time
import json
import os
from pathlib import Path
from typing import Any

import httpx

SCHEMA = "model-probe.verdict.v1"

PROBE_TEXT = "Reply with exactly: ok"
# Reasoning models spend the budget on reasoning first; 16 tokens yields empty content
# and a false "dead" (measured 2026-10-27 on qwen3.8-flash-next-uncensored, reasoning_tokens=19).
MIN_BUDGET = 128


class ModelProbeError(RuntimeError):
    """No candidate model passed the probe. `.verdicts` carries every reason."""

    def __init__(self, message: str, verdicts: list[dict[str, Any]]) -> None:
        super().__init__(message)
        self.verdicts = verdicts


def _home() -> Path:
    return Path(os.environ.get("PRIME_AGENT_HOME_DIR", Path.home() / ".prime" / "agent"))


def local_providers(root: Path | None = None) -> dict[str, dict]:
    """Providers declared in models.json (LAN boxes, relays, custom endpoints)."""
    cfg = root or _home()
    path = cfg / "models.json"
    if not path.exists():
        return {}
    data = json.loads(path.read_text())
    provs = dict(data.get("providers") or {})
    provs.update(data.get("dormant") or {})
    return provs


def catalog_models(root: Path | None = None) -> list[dict]:
    """Hosted model catalogue shipped by the agent (provider, baseUrl, api, cost)."""
    cfg = root or _home()
    for path in sorted((cfg / "models").glob("provider-model-catalog*.json")):
        payload = json.loads(path.read_text()).get("payload") or {}
        models = payload.get("models")
        if models:
            return models
    return []


def settings_defaults(root: Path | None = None) -> tuple[str, str]:
    try:
        s = json.loads((root or _home() / "settings.json").read_text())
    except OSError:
        return ("", "")
    return (s.get("defaultProvider") or "", s.get("defaultModel") or "")


def credentials(root: Path | None = None) -> dict[str, dict]:
    """auth.json entries + matching *_API_KEY env vars, keyed by provider id."""
    path = (root or _home()) / "auth.json"
    out: dict[str, dict] = {}
    if path.exists():
        for provider, entry in json.loads(path.read_text()).items():
            kind = entry.get("type") or ""
            value = entry.get("key") or entry.get("access") or ""
            expires = entry.get("expires")
            out[provider] = {
                "present": bool(value),
                "kind": kind,
                "source": str(path),
                "expires": _iso_ms(expires),
                "expired": bool(expires) and expires < datetime.datetime.now().timestamp() * 1000,
                "secret": value,
            }
    return out


def _iso_ms(ms: Any) -> str | None:
    if not ms:
        return None
    return datetime.datetime.utcfromtimestamp(ms / 1000).strftime("%Y-%m-%dT%H:%M:%SZ")


def env_credential(provider: str) -> dict | None:
    value = os.environ.get(provider.upper().replace("-", "_") + "_API_KEY", "")
    if not value:
        return None
    return {"present": True, "kind": "env", "source": "env", "expires": None,
            "expired": False, "secret": value}


def resolve(selector: str, root: Path | None = None) -> dict:
    """Map 'provider/model' to endpoint + api. Prefers local models.json, then catalogue."""
    provider, _, model_id = selector.partition("/")
    if not model_id:
        provider, model_id = "", selector
    for name, prov in local_providers(root).items():
        if provider and name != provider:
            continue
        for m in prov.get("models") or []:
            mid = m.get("id") or ""
            if mid == model_id or mid == selector or m.get("alias") == model_id:
                return {"provider": name, "model_id": mid, "selector": f"{name}/{mid}",
                        "api": prov.get("api") or "openai-completions", "base_url": prov.get("baseUrl") or "",
                        "auth_header": prov.get("authHeader", True), "api_key": prov.get("apiKey") or "",
                        "headers": prov.get("headers") or {},
                        "cost": m.get("cost") or {"input": 0, "output": 0}, "source": "models.json"}
    models = catalog_models(root)
    exact = [m for m in models if m.get("id") == model_id and (not provider or m.get("provider") == provider)]
    if exact:
        m = exact[0]
        return {"provider": m["provider"], "model_id": m["id"], "selector": f"{m['provider']}/{m['id']}",
                "api": m.get("api") or "openai-completions", "base_url": m.get("baseUrl") or "",
                "auth_header": True, "api_key": "", "headers": {}, "cost": m.get("cost") or {}, "source": "catalogue"}
    known = [f"{m.get('provider')}/{m.get('id')}" for m in models]
    known += [f"{n}/{(m.get('id') or '')}" for n, p in local_providers(root).items() for m in p.get("models") or []]
    near = difflib.get_close_matches(selector, known, n=5, cutoff=0.4)
    return {"provider": provider, "model_id": model_id, "selector": selector, "api": "",
            "base_url": "", "auth_header": True, "api_key": "", "headers": {}, "cost": {}, "source": "unknown",
            "suggestions": near}


def _secret(value: str) -> tuple[str, str]:
    """Resolve a stored secret. A leading ! means a shell command that prints it (auth.json, models.json)."""
    if not value:
        return "", ""
    if not value.startswith("!"):
        return value, ""
    proc = subprocess.run(value[1:], shell=True, capture_output=True, text=True)
    if proc.returncode != 0:
        return "", _clip(proc.stderr or f"{value[1:]} exited {proc.returncode}")
    return proc.stdout.strip(), ""


def _urls(api: str, base_url: str) -> tuple[str, str]:
    base = base_url.rstrip("/")
    if base and not base.endswith("/v1"):
        base += "/v1"
    if api == "anthropic-messages":
        return base + "/models", base + "/messages"
    if api == "openai-responses":
        return base + "/models", base + "/responses"
    return base + "/models", base + "/chat/completions"


def _headers(res: dict, cred: dict | None) -> dict[str, str]:
    """Request headers for a probe call, with provider-declared headers taking precedence."""
    api = res["api"]
    token, secret_error = _secret((cred or {}).get("secret") or res.get("api_key") or "")
    auth = f"Bearer {token}" if token else ""
    h = {"content-type": "application/json"}
    if api == "anthropic-messages":
        h["anthropic-version"] = "2023-06-01"
        if token:
            h["x-api-key" if cred and cred.get("kind") == "api_key" else "authorization"] = auth
    elif res.get("auth_header", True) and auth:
        h["authorization"] = auth
    for name, value in (res.get("headers") or {}).items():
        resolved, err = _secret(value)
        if err:
            secret_error = secret_error or err
        h[name.lower()] = resolved if value.startswith("!") else value
    return h, secret_error


def _completion_body(api: str, model_id: str, text: str, budget: int) -> dict:
    if api == "anthropic-messages":
        return {"model": model_id, "messages": [{"role": "user", "content": text}],
                "max_tokens": budget}
    if api == "openai-responses":
        return {"model": model_id, "input": text, "max_output_tokens": budget}
    return {"model": model_id, "messages": [{"role": "user", "content": text}],
            "max_tokens": budget, "temperature": 0}


def _extract(api: str, data: dict) -> tuple[str, str]:
    """Return (content, reasoning) so an empty answer can be explained, not just reported."""
    if api == "anthropic-messages":
        parts = data.get("content") or []
        return "".join(p.get("text", "") for p in parts if p.get("type") == "text"), \
            "".join(p.get("thinking", "") for p in parts if p.get("type") == "thinking")
    if api == "openai-responses":
        return data.get("output_text") or "", ""
    choice = (data.get("choices") or [{}])[0]
    msg = choice.get("message") or {}
    return msg.get("content") or "", msg.get("reasoning_content") or ""


def _verdict(selector: str, verdict: str, stage: str, reason: str, error: str = "",
             fix: str = "", res: dict | None = None, cred: dict | None = None,
             check: dict | None = None, extra: dict | None = None) -> dict:
    res = res or {}
    out = {
        "schema": SCHEMA,
        "model": selector,
        "provider": res.get("provider", selector.partition("/")[0]),
        "resolved": res.get("selector"),
        "source": res.get("source", ""),
        "api": res.get("api", ""),
        "base_url": res.get("base_url", ""),
        "cost_per_mtok": res.get("cost") or {},
        "paid": _is_paid(res.get("cost") or {}),
        "credential": None if cred is None else {k: v for k, v in cred.items() if k != "secret"},
        "stage": stage,
        "verdict": verdict,
        "reason": reason,
        "check": check or {},
        "ts": datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"),
    }
    if error:
        out["error"] = error
    if fix:
        out["fix"] = fix
    if res.get("suggestions"):
        out["suggestions"] = res["suggestions"]
    out.update(extra or {})
    return out


def _is_paid(cost: dict) -> bool:
    return any((cost.get(k) or 0) for k in ("input", "output"))


def _clip(text: str, limit: int = 300) -> str:
    text = " ".join(str(text).split())
    return text if len(text) <= limit else text[:limit] + "..."


def probe(selector: str, paid: bool = False, timeout: float = 60.0,
          root: Path | None = None) -> dict:
    """One model selector -> one typed verdict. Never raises for a dead model."""
    res = resolve(selector, root)
    if res["source"] == "unknown" or not res["base_url"]:
        return _verdict(selector, "dead", "resolve", "unknown-model",
                        error=f"no endpoint for {selector!r} in models.json or the shipped catalogue",
                        fix="check the selector against search_models() or add the provider to models.json",
                        res=res)

    cred = credentials(root).get(res["provider"]) or env_credential(res["provider"])
    if not cred or not cred.get("secret"):
        header_secret = next((v for k, v in (res.get("headers") or {}).items()
                              if k.lower() in ("authorization", "x-api-key")), "")
        fallback = res["api_key"] or header_secret
        if fallback:
            cred = {"present": True, "kind": "config-header" if not res["api_key"] else "config",
                    "source": "models.json", "expires": None, "expired": False, "secret": fallback}
    checks: dict[str, Any] = {}
    if not cred or not cred.get("secret"):
        return _verdict(selector, "dead", "credential", "no-credential",
                        error=f"no API key for provider: {res['provider']}",
                        fix=f"run /login for {res['provider']}, add its key to auth.json, or set "
                            f"{res['provider'].upper().replace('-', '_')}_API_KEY",
                        res=res, cred=cred)
    if cred.get("expired"):
        checks["credential_expired"] = cred.get("expires")

    models_url, completions_url = _urls(res["api"], res["base_url"])
    headers, secret_error = _headers(res, cred)
    if secret_error:
        return _verdict(selector, "unproven", "credential", "credential-unresolved",
                        error=f"stored secret could not be resolved: {secret_error}",
                        fix="repair the !command in models.json or auth.json, then re-probe",
                        res=res, cred=cred)
    client = httpx.Client(timeout=httpx.Timeout(timeout, connect=5.0))
    try:
        try:
            r = client.get(models_url, headers=headers)
        except httpx.HTTPError as exc:
            return _verdict(selector, "dead", "reach", "unreachable",
                            error=f"{type(exc).__name__} on {models_url}: {_clip(exc)}",
                            fix="start or restart that endpoint before spawning children on it",
                            res=res, cred=cred, check=checks)
        checks["models_url"] = models_url
        checks["models_status"] = r.status_code
        if r.status_code in (401, 403):
            return _verdict(selector, "dead", "credential", "credential-rejected",
                            error=f"HTTP {r.status_code} on {models_url}: {_clip(r.text)}",
                            fix=f"rotate or re-login the {res['provider']} credential",
                            res=res, cred=cred, check=checks)
        if r.status_code == 429:
            return _verdict(selector, "unproven", "credential", "rate-limited",
                            error=f"HTTP 429 on {models_url}: credential accepted, rate limited",
                            fix="retry later or lower spawn concurrency",
                            res=res, cred=cred, check=checks)
        if r.status_code == 404:
            checks["models_note"] = "endpoint has no /models; proceeding to completion"
        elif r.status_code >= 400:
            return _verdict(selector, "dead", "credential", f"http-{r.status_code}",
                            error=f"HTTP {r.status_code} on {models_url}: {_clip(r.text)}",
                            fix="probe this provider again after fixing the reported error",
                            res=res, cred=cred, check=checks)

        if _is_paid(res["cost"]) and not paid:
            return _verdict(selector, "unproven", "auth", "paid-probe-skipped",
                            error=f"credential accepted; skipped a metered completion ({res['provider']} "
                                  f"costs ${res['cost'].get('input')}/${res['cost'].get('output')} per Mtok)",
                            fix="call probe(..., paid=True) once Mike authorises the spend",
                            res=res, cred=cred, check=checks)

        t0 = time.monotonic()
        r = client.post(completions_url, headers=headers,
                        json=_completion_body(res["api"], res["model_id"], PROBE_TEXT, MIN_BUDGET))
        checks["completion_url"] = completions_url
        checks["completion_status"] = r.status_code
        checks["latency_ms"] = int((time.monotonic() - t0) * 1000)
        if r.status_code >= 400:
            return _verdict(selector, "dead", "completion", f"http-{r.status_code}",
                            error=f"HTTP {r.status_code} on {completions_url}: {_clip(r.text)}",
                            fix="fix the reported provider error before spawning children here",
                            res=res, cred=cred, check=checks)
        data = r.json()
        content, reasoning = _extract(res["api"], data)
        checks["content_len"] = len(content)
        checks["reasoning_len"] = len(reasoning)
        finish = ""
        if res["api"] == "openai-completions":
            finish = (data.get("choices") or [{}])[0].get("finish_reason") or ""
        checks["finish_reason"] = finish
        checks["usage"] = data.get("usage") or {}
        if content.strip():
            return _verdict(selector, "alive", "completion", "completion-returned-content",
                            res=res, cred=cred, check=checks)
        if reasoning and finish == "length":
            return _verdict(selector, "unproven", "completion", "budget-too-small",
                            error=f"completion returned reasoning only ({len(reasoning)} chars) and hit "
                                  f"max_tokens={MIN_BUDGET}",
                            fix="raise the probe budget before calling this model broken",
                            res=res, cred=cred, check=checks)
        return _verdict(selector, "dead", "completion", "empty-completion",
                        error=f"HTTP {r.status_code} with no content: {_clip(json.dumps(data))}",
                        fix="raise the token budget or check the model id before concluding it works",
                        res=res, cred=cred, check=checks)
    finally:
        client.close()


def probe_many(selectors: list[str], paid: bool = False, timeout: float = 60.0,
               root: Path | None = None) -> list[dict]:
    return [probe(s, paid=paid, timeout=timeout, root=root) for s in selectors]


def _default_candidates(root: Path | None = None) -> list[str]:
    provider, model = settings_defaults(root)
    return [f"{provider}/{model}"] if provider and model else []


def pick(prefer: list[str] | None = None, paid: bool = False, timeout: float = 60.0,
         root: Path | None = None) -> dict:
    """First candidate with verdict alive. Raises ModelProbeError listing every reason."""
    candidates = list(prefer or _default_candidates(root))
    if not candidates:
        raise ModelProbeError("pick() got no candidates and settings.json has no default model", [])
    verdicts = probe_many(candidates, paid=paid, timeout=timeout, root=root)
    for selector, v in zip(candidates, verdicts):
        if v["verdict"] == "alive":
            return v
    lines = [f"  - {v['model']}: {v['verdict']} ({v['stage']}/{v['reason']})"
             + (f" {v['error']}" if v.get("error") else "") for v in verdicts]
    raise ModelProbeError("no probe-alive model; refusing to spawn on a dead one\n" + "\n".join(lines), verdicts)


async def spawn(prompt: str, name: str, model: str | None = None,
                prefer: list[str] | None = None, paid: bool = False,
                timeout: float = 60.0, thinking: str | None = None) -> Any:
    """rlm.spawn with a probe in front of it. Same handle, plus a surfaced reason on failure."""
    candidates = [model] if model else list(prefer or [])
    verdict = pick(candidates, paid=paid, timeout=timeout)
    import rlm

    handle = await rlm.spawn(prompt, name=name, model=verdict["resolved"] or model, thinking=thinking)
    return {"handle": handle, "probe": verdict}


def search_models(query: str = "", root: Path | None = None) -> list[str]:
    """Every known selector containing a substring (models.json providers + shipped catalogue)."""
    needle = query.lower()
    known = {f"{m.get('provider')}/{m.get('id')}" for m in catalog_models(root)}
    known |= {f"{n}/{(m.get('id') or '')}" for n, prov in local_providers(root).items()
              for m in prov.get("models") or []}
    return sorted(k for k in known if needle in k.lower())


def run(selector: str, paid: bool = False, timeout: float = 60.0,
        json_out: bool = False) -> str:
    """Probe one model selector before spawning a child or paid run on it.

    Prints `VERDICT selector [stage/reason] <provider error>` plus a fix line. Never a
    silent pass: only a real completion that returned content prints ALIVE.
    """
    v = probe(selector, paid=paid, timeout=timeout)
    if json_out:
        return json.dumps(v, indent=2, default=str)
    line = f"{v['verdict'].upper():8} {v['model']}  [{v['stage']}/{v['reason']}] {v.get('error', '')}"
    if v.get("fix"):
        line += f"\n  fix: {v['fix']}"
    if v.get("suggestions"):
        line += "\n  did you mean: " + ", ".join(v["suggestions"])
    return line

