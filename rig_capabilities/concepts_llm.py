"""V19: LLM concept overlay.

A second, semantic tier for the concept index. The IDF layer (fabric.build_concepts)
matches literal tokens; this layer asks a local model (ollama qwen3:8b) for 3-5
topic tags per asset, so a query like "guardrails" can find an asset that never says
the word. Honest tiers: lookups report which tier matched — an LLM tag is weaker
evidence than a literal token hit and is labeled as such.

Scope control: only the most-used assets get an LLM pass (analytics pack-frequency,
falling back to canonical-first index order), 10s/asset, checkpointed every 50 so a
killed run keeps its work. Never edits external files; state lives in
.concepts.llm.json. If ollama is down the build reports unavailable and changes
nothing.
"""
from __future__ import annotations

import json
import re
import urllib.error
import urllib.request
from pathlib import Path

LLM_PATH = ".concepts.llm.json"
_DEFAULT_URL = "http://127.0.0.1:11434"
_DEFAULT_MODEL = "qwen3:8b"
_ARR = re.compile(r"\[[^\[\]]*\]")


def llm_file(repo) -> Path:
    return Path(repo.root) / LLM_PATH


def load_llm(repo) -> dict:
    p = llm_file(repo)
    if not p.exists():
        return {}
    try:
        d = json.loads(p.read_text())
        return d if isinstance(d, dict) else {}
    except (json.JSONDecodeError, OSError):
        return {}


def key_of(asset) -> str:
    return f"{asset['id']}|{asset.get('kind', '')}|{asset.get('source', '')}"


def top_targets(repo, n: int = 500) -> list:
    """Analytics pack-frequency order; fallback = canonical-first."""
    doc = repo.load_index()
    by_key = {key_of(a): a for a in doc["assets"]}
    out = []
    ap = Path(repo.root) / ".context" / "analytics.json"
    if ap.exists():
        try:
            pa = json.loads(ap.read_text()).get("per_asset") or {}
            ranked = sorted(pa.items(), key=lambda kv: -int(kv[1].get("packs") or 0))
            for k, v in ranked:
                a = by_key.get(f"{k}|{v.get('kind', '')}|{v.get('source', '')}")
                if a and a not in out:
                    out.append(a)
        except (json.JSONDecodeError, OSError):
            out = []
    trust = {"canonical": 0}
    rest = sorted((a for a in doc["assets"] if a not in out),
                  key=lambda a: trust.get(a["source"], 1))
    out = out + rest
    return out[:n]


def _ask(url: str, model: str, asset, timeout: int = 10) -> list | None:
    prompt = (
        "Give 3 to 5 lowercase topic tags for this agent capability. "
        'Reply ONLY a JSON array of strings, no prose.\n'
        f"name: {asset['id']}\nkind: {asset.get('kind')}\n"
        f"description: {(asset.get('description') or '')[:300]}"
    )
    body = {"model": model, "prompt": prompt, "stream": False, "think": False,
            "options": {"temperature": 0}}
    req = urllib.request.Request(
        url.rstrip("/") + "/api/generate", data=json.dumps(body).encode(),
        headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            raw = json.loads(r.read()).get("response", "")
    except (urllib.error.URLError, TimeoutError, OSError, json.JSONDecodeError):
        return None
    m = _ARR.search(raw)
    if not m:
        return None
    try:
        tags = json.loads(m.group(0))
    except json.JSONDecodeError:
        return None
    tags = [str(t).strip().lower().replace(" ", "-")
            for t in tags if isinstance(t, str) and str(t).strip()]
    return tags[:5] or None


def _save(repo, data: dict) -> None:
    cp = llm_file(repo)
    tmp = cp.with_suffix(".tmp")
    tmp.write_text(json.dumps(data))
    tmp.replace(cp)


def build(repo, model: str = _DEFAULT_MODEL, url: str = _DEFAULT_URL,
          n: int = 500, timeout: int = 10, checkpoint: int = 50) -> dict:
    data = load_llm(repo)
    targets = top_targets(repo, n=n)
    todo = [a for a in targets if key_of(a) not in data]
    # one probe to fail fast and honestly when ollama is down
    if todo and _ask(url, model, todo[0], timeout=timeout) is None:
        if not _reachable(url):
            return {"unavailable": True, "url": url, "tagged": len(data)}
    done = since = 0
    for a in todo:
        tags = _ask(url, model, a, timeout=timeout)
        data[key_of(a)] = tags or []
        done += 1
        since += 1
        if since >= checkpoint:
            _save(repo, data)
            since = 0
    _save(repo, data)
    empty = sum(1 for k in (key_of(a) for a in targets) if not data.get(k))
    return {"tagged": done, "total_tagged": len(data), "failed": empty,
            "model": model}


def _reachable(url: str) -> bool:
    try:
        with urllib.request.urlopen(url.rstrip("/") + "/api/tags",
                                    timeout=3) as r:
            return r.status == 200
    except (urllib.error.URLError, TimeoutError, OSError):
        return False


def lookup(repo, concept: str, limit: int = 20) -> list:
    """Asset ids whose LLM tags match the concept (word-wise)."""
    key = concept.lower().strip()
    words = set(key.split()) | {key.replace(" ", "-")}
    out = []
    for k, tags in load_llm(repo).items():
        tl = set(tags or [])
        if key in tl or (tl & words):
            out.append(k.split("|", 1)[0])
    return out[:limit]
