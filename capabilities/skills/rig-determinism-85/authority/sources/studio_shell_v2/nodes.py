"""Node implementations for studio pipelines. LLM/tool calls go through the
LiteLLM gateway as a client (crew-litellm owns the config); key from env only."""
import hashlib
import json
import os
import urllib.request
from pathlib import Path

BASE = Path(__file__).resolve().parent


def _out_path(out):
    """Relative out paths resolve against the shell dir, never the process CWD."""
    p = Path(out).expanduser()
    return p if p.is_absolute() else BASE / p


def scan_files(root, prev=None, max_files=500):
    """List files under root (bounded)."""
    root = Path(root).expanduser()
    if not root.is_dir():
        raise FileNotFoundError(f"scan root is not a directory: {root}")
    files = sorted(p for p in root.rglob("*") if p.is_file() and ".git" not in p.parts)[:max_files]
    return {"root": str(root), "files": [str(p) for p in files]}


def hash_files(prev, out=None):
    """sha256 every file from scan_files output."""
    entries = []
    for fp in prev["files"]:
        h = hashlib.sha256(Path(fp).read_bytes()).hexdigest()
        entries.append({"path": fp, "sha256": h, "bytes": Path(fp).stat().st_size})
    return {"root": prev["root"], "entries": entries,
            "out": str(_out_path(out)) if out else None}


def write_manifest(prev):
    out = _out_path(prev["out"])
    manifest = {"root": prev["root"], "count": len(prev["entries"]), "entries": prev["entries"]}
    out.write_text(json.dumps(manifest, indent=2))
    return {"manifest": str(out), "count": manifest["count"]}


def text_stats(prev, exts=None):
    """Aggregate stats over scan_files output: counts by extension, bytes, line counts for text files."""
    from collections import Counter
    by_ext = Counter()
    total_bytes = 0
    text_files = text_lines = 0
    for fp in prev["files"]:
        p = Path(fp)
        by_ext[p.suffix or "<none>"] += 1
        total_bytes += p.stat().st_size
        if p.suffix in (exts or [".md", ".txt", ".py", ".js", ".ts", ".html", ".json", ".css"]):
            try:
                text_lines += len(p.read_text(errors="ignore").splitlines())
                text_files += 1
            except OSError:
                pass
    return {"root": prev["root"], "files": len(prev["files"]), "by_ext": dict(by_ext.most_common(15)),
            "total_bytes": total_bytes, "text_files": text_files, "text_lines": text_lines}


def write_json(prev, out):
    out = _out_path(out)
    out.write_text(json.dumps(prev, indent=2))
    return {"json": str(out), "keys": sorted(prev.keys())}


def llm_complete(prev, prompt, model="rig-auto", max_tokens=256, budget_calls=1):
    """One gateway completion. Raises on auth/route failure — never fakes output."""
    if prev.get("_llm_calls", 0) >= budget_calls:
        raise RuntimeError(f"llm budget exceeded ({budget_calls} call/run)")
    base = os.environ.get("LITELLM_BASE_URL", "http://192.168.68.53:4000").rstrip("/")
    key = os.environ.get("LITELLM_API_KEY")
    if not key:
        raise RuntimeError("LITELLM_API_KEY not set — refusing to guess a gateway key")
    body = json.dumps({"model": model, "max_tokens": max_tokens,
                       "messages": [{"role": "user", "content": prompt}]}).encode()
    req = urllib.request.Request(base + "/v1/chat/completions", data=body,
                                 headers={"Authorization": f"Bearer {key}",
                                          "Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=60) as r:
        data = json.loads(r.read())
    out = dict(prev)
    out["_llm_calls"] = prev.get("_llm_calls", 0) + 1
    out["llm"] = {"model": model, "text": data["choices"][0]["message"]["content"]}
    return out
