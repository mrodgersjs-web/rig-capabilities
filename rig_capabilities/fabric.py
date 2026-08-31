"""Discovery index layer + context fabric (the "Context Fabric" MCP tier).

Four tiers, layered deterministically:

  metadata   — okf trust / freshness / acl / kind filters (okf.py)
  sparse     — BM25 over id+description+tags (stdlib, always available)
  dense      — ollama nomic-embed-text cosine, cached in .embeddings.json
               (degrades honestly: no cache/no server => tier reports false)
  graph      — adjacency from explicit `relates_to` + shared-token Jaccard,
               built into .graph.json by build_graph()

context_pack() fuses the tiers into a task-minimal, provenance-stamped
runtime context graph artifact under .context/. Feedback: rate().
"""
from __future__ import annotations

import json
import math
import re
import urllib.request
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path

from .taxonomy import dedupe, route

_TOKEN = re.compile(r"[a-z0-9]+")
_STOP = set(("a an the and or for to in on of with by is are be it its this that"
             " when asked use using our my you your all any from as at not no").split())


def tokens(text: str) -> list:
    return [t for t in _TOKEN.findall((text or "").lower())
            if t not in _STOP and len(t) > 1]


# ------------------------------------------------------------------ sparse tier

class Corpus:
    def __init__(self, assets: list):
        self.assets = assets
        self.docs = [tokens(a["id"]) * 2 + tokens(a.get("description") or "")
                     + tokens(" ".join(a.get("tags") or []))
                     for a in assets]
        self.N = len(assets)
        self.avg = (sum(len(d) for d in self.docs) / max(1, self.N)) or 1.0
        self.df: Counter = Counter()
        for d in self.docs:
            self.df.update(set(d))

    def bm25(self, query: str, limit: int = 40) -> list:
        k1, b = 1.5, 0.75
        scores = []
        q = set(tokens(query))
        for i, d in enumerate(self.docs):
            tf = Counter(d)
            s = 0.0
            for t in q & set(tf):
                idf = math.log(1 + (self.N - self.df[t] + 0.5) / (self.df[t] + 0.5))
                s += idf * tf[t] * (k1 + 1) / (tf[t] + k1 * (1 - b + b * len(d) / self.avg))
            if s > 0:
                scores.append((s, i))
        scores.sort(key=lambda x: (-x[0], self.assets[x[1]]["id"]))
        return [(self.assets[i], round(s, 3)) for s, i in scores[:limit]]


# ----------------------------------------------------------------- graph tier

def _jaccard(a: set, b: set) -> float:
    return len(a & b) / max(1, len(a | b))


def build_graph(repo) -> dict:
    """Adjacency: explicit relates_to (exact id hits) + shared-token Jaccard
    candidates from an inverted index (rare-token pool, capped)."""
    doc = repo.load_index()
    assets = dedupe(doc["assets"])
    by_id = {a["id"]: a for a in assets}
    tset = {a["id"]: set(tokens(a["id"]) + (a.get("tags") or []))
            for a in assets}
    inv: dict = defaultdict(list)
    for aid, ts in tset.items():
        for t in ts:
            if len(inv[t]) < 60:
                inv[t].append(aid)
    df = {t: len(v) for t, v in inv.items()}
    adj: dict = defaultdict(dict)

    def link(u, v, w):
        if u == v or v not in by_id:
            return
        if adj[u].get(v, 0) < w:
            adj[u][v] = w
        if adj[v].get(u, 0) < w:
            adj[v][u] = w

    for a in assets:
        for rel in (a.get("okf") or {}).get("relates_to", []):
            link(a["id"], rel, 3.0)                     # declared edges are strong
        pool: Counter = Counter()
        for t in tset[a["id"]]:
            if df.get(t, 99) <= 50:                     # rare-token pool
                for other in inv.get(t, []):
                    if other != a["id"]:
                        pool[other] += 1
        for other, _c in pool.most_common(40):
            j = _jaccard(tset[a["id"]], tset[other])
            if j >= 0.15:
                link(a["id"], other, round(j, 3))
    out = {k: [i for i, _w in sorted(v.items(), key=lambda x: -x[1])[:12]]
           for k, v in adj.items()}
    gp = Path(repo.root) / ".graph.json"
    tmp = gp.with_suffix(".tmp")
    tmp.write_text(json.dumps(out))
    tmp.replace(gp)
    return {"nodes": len(out),
            "edges": sum(len(v) for v in out.values()) // 2}


def load_graph(repo) -> dict:
    gp = Path(repo.root) / ".graph.json"
    return json.loads(gp.read_text()) if gp.exists() else {}


def expand(repo, ids: list, depth: int = 1) -> dict:
    g = load_graph(repo)
    seen = set(ids)
    for _ in range(depth):
        nxt = set()
        for i in seen:
            nxt.update(g.get(i, []))
        seen |= nxt
    return {i: sorted(set(g.get(i, []))) for i in sorted(seen)}


# -------------------------------------------------------------- concepts tier

def build_concepts(repo) -> dict:
    doc = repo.load_index()
    conc: dict = defaultdict(list)
    for a in dedupe(doc["assets"]):
        cs = set((a.get("tags") or [])) | set(tokens(a["id"])) \
            | set(tokens((a.get("description") or ""))[:12])
        for c in list(cs)[:12]:
            if len(conc[c]) < 50 and a["id"] not in conc[c]:
                conc[c].append(a["id"])
    cp = Path(repo.root) / ".concepts.json"
    tmp = cp.with_suffix(".tmp")
    tmp.write_text(json.dumps(dict(conc)))
    tmp.replace(cp)
    return {"concepts": len(conc)}


def lookup_concept(repo, concept: str, limit: int = 20) -> list:
    """Concept index lookup. Multi-word queries union across words."""
    cp = Path(repo.root) / ".concepts.json"
    if not cp.exists():
        return []
    idx = json.loads(cp.read_text())
    key = concept.lower().strip()
    if key in idx:
        return idx[key][:limit]
    seen, out = set(), []
    for w in key.split():
        for i in idx.get(w, []):
            if i not in seen:
                seen.add(i)
                out.append(i)
    return out[:limit]


# ----------------------------------------------------------------- dense tier

def _ollama_embed(model: str, url: str, text: str) -> list | None:
    try:
        req = urllib.request.Request(
            url.rstrip("/") + "/api/embeddings",
            data=json.dumps({"model": model, "prompt": text}).encode(),
            headers={"Content-Type": "application/json"})
        with urllib.request.urlopen(req, timeout=30) as r:
            return json.loads(r.read())["embedding"]
    except Exception:
        return None


def build_embeddings(repo, model: str = "nomic-embed-text",
                     url: str = "http://127.0.0.1:11434",
                     progress=None) -> dict:
    ep = Path(repo.root) / ".embeddings.json"
    cache = json.loads(ep.read_text()) if ep.exists() else {}
    doc = repo.load_index()
    assets = dedupe(doc["assets"])
    done = skipped = failed = 0
    for n, a in enumerate(assets, 1):
        key = f"{a['id']}@{a['sha']}"
        if key in cache:
            skipped += 1
            continue
        vec = _ollama_embed(model, url,
                            f"{a['id']}. {a.get('description') or ''} "
                            f"{' '.join(a.get('tags') or [])}")
        if vec is None:
            failed += 1
            continue
        cache[key] = [round(x, 5) for x in vec]
        done += 1
        if progress and n % 250 == 0:
            progress(done, skipped, failed)
        if (n % 200) == 0:                       # checkpoint
            tmp = ep.with_suffix(".tmp")
            tmp.write_text(json.dumps(cache))
            tmp.replace(ep)
    tmp = ep.with_suffix(".tmp")
    tmp.write_text(json.dumps(cache))
    tmp.replace(ep)
    return {"embedded": done, "cached_skipped": skipped, "failed": failed,
            "total": len(assets), "model": model}


def dense_search(repo, query: str, limit: int = 40,
                 model: str = "nomic-embed-text",
                 url: str = "http://127.0.0.1:11434"):
    """Returns (results, tier_ok). tier_ok False => honest degradation."""
    ep = Path(repo.root) / ".embeddings.json"
    if not ep.exists():
        return [], False
    cache = json.loads(ep.read_text())
    doc = repo.load_index()
    assets = dedupe(doc["assets"])
    qv = _ollama_embed(model, url, query)
    if qv is None:
        return [], False
    qn = math.sqrt(sum(x * x for x in qv)) or 1.0
    scored = []
    for a in assets:
        vec = cache.get(f"{a['id']}@{a['sha']}")
        if vec is None or len(vec) != len(qv):
            continue
        d = sum(x * y for x, y in zip(qv, vec)) / (
            qn * (math.sqrt(sum(x * x for x in vec)) or 1.0))
        scored.append((d, a))
    scored.sort(key=lambda x: (-x[0], x[1]["id"]))
    return [(a, round(d, 4)) for d, a in scored[:limit]], True


# ------------------------------------------------------------- context fabric

def context_pack(repo, intent: str, budget_tokens: int = 1500,
                 max_nodes: int = 12, min_trust: float = 0.5,
                 requester_acl: list | None = None,
                 requester: str | None = None,
                 sign: bool = True) -> dict:
    from .federation import log_pack
    from .policy import (acl_allows, effective_trust, permitted_scopes,
                         record_observation, trust_tables)
    from .refresh import auto_refresh
    from .surface import load_key, sign_artifact

    auto_refresh(repo)
    doc = repo.load_index()
    assets = dedupe(doc["assets"])
    corpus = Corpus(assets)
    by_id = {a["id"]: a for a in assets}
    obs, deltas = trust_tables(repo)

    scopes = permitted_scopes(repo, requester)
    if requester_acl is not None:
        call_scopes = set(requester_acl)
        if scopes is not None:
            call_scopes &= scopes
    else:
        call_scopes = scopes

    sparse = corpus.bm25(intent, limit=60)
    dense, dense_ok = dense_search(repo, intent, limit=60)
    lanes = route(repo, intent, per=6)["lanes"]
    lane_ids = {c["id"] for l in lanes[:3] for c in l["capabilities"]}

    ranks: dict = defaultdict(dict)
    for r, (a, _s) in enumerate(sparse):
        ranks["sparse"][a["id"]] = 1.0 / (1 + r)
    for r, (a, _s) in enumerate(dense):
        ranks["dense"][a["id"]] = 1.0 / (1 + r)
    cand = set(ranks["sparse"]) | set(ranks["dense"]) | lane_ids

    def trust_of(a) -> float:
        return effective_trust((a.get("okf") or {}).get("trust", 0.7),
                               a["id"], obs, deltas)

    def okf_ok(a) -> bool:
        o = a.get("okf") or {}
        if o.get("freshness") == "Deprecated":
            return False
        if trust_of(a) < min_trust:
            return False
        if not acl_allows(o.get("acl") or [], call_scopes):
            return False
        return True

    def score(aid):
        a = by_id[aid]
        t = trust_of(a)
        s = 0.5 * ranks["sparse"].get(aid, 0.0) + 0.3 * ranks["dense"].get(aid, 0.0)
        if not dense_ok:
            s = 0.65 * ranks["sparse"].get(aid, 0.0)
        s += 0.15 * t
        if aid in lane_ids:
            s += 0.08
        return s

    seeds = [aid for aid in cand if aid in by_id and okf_ok(by_id[aid])]
    seeds.sort(key=score, reverse=True)
    chosen = seeds[:max_nodes]

    g = load_graph(repo)
    adjacent = []
    for aid in chosen[:3]:
        for nb in g.get(aid, [])[:6]:
            if nb not in chosen and nb in by_id and okf_ok(by_id[nb]):
                adjacent.append((score(nb), nb))
    extra = [nb for _s, nb in sorted(adjacent, reverse=True)][:4]
    chosen += extra

    parts = [f"# Context pack — {intent}\n"]
    used = len(parts[0]) // 4
    nodes = []
    for aid in chosen:
        a = by_id[aid]
        o = a.get("okf") or {}
        t = trust_of(a)
        head = repo.content(a.get("abs_path") or "")[:1400] or (a.get("description") or "")
        excerpt = " ".join(head.split())[:260]
        block = (f"\n## {a['kind']}: {aid}  "
                 f"[trust {t} | {o.get('freshness', 'Unknown')} | "
                 f"sha {a['sha']}]\n"
                 f"source: {a['source']}  path: {a['path']}\n"
                 f"> {excerpt}\n")
        cost = len(block) // 4
        if used + cost > budget_tokens:
            break
        parts.append(block)
        used += cost
        nodes.append({"id": aid, "kind": a["kind"], "source": a["source"],
                      "sha": a["sha"], "trust": t,
                      "freshness": o.get("freshness", "Unknown"),
                      "score": round(score(aid), 3),
                      "tier": "adjacent" if aid in extra else "core"})
    markdown = "".join(parts)

    ts = datetime.now().strftime("%Y%m%d-%H%M%S")
    pack_id = f"pack-{ts}"
    art_dir = Path(repo.root) / ".context"
    art_dir.mkdir(exist_ok=True)
    artifact = {"id": pack_id, "intent": intent, "budget_tokens": budget_tokens,
                "requester": requester or "",
                "tiers": {"metadata_filter": True, "sparse_bm25": True,
                          "dense_ollama": dense_ok, "graph": bool(g),
                          "acl_enforced": call_scopes is not None,
                          "decay": True, "ratings_trust": True},
                "lanes": [l["outcome"] for l in lanes[:3]],
                "nodes": nodes, "estimated_tokens": used}
    key = load_key(repo) if sign else None
    artifact["tiers"]["signed"] = bool(key)
    if key:
        artifact["signature"] = sign_artifact(artifact, key)
    (art_dir / f"{pack_id}.json").write_text(json.dumps(artifact, indent=1))
    record_observation(repo, pack_id, [n["id"] for n in nodes], requester)
    log_pack(repo, requester, pack_id, intent)
    from .observe import trace
    trace(repo, "context_pack",
          input={"intent": intent, "requester": requester or ""},
          output={"pack": pack_id, "nodes": [n["id"] for n in nodes],
                  "tokens": used},
          metadata={"tiers": artifact["tiers"]})
    artifact.update({"markdown": markdown, "artifact":
                     str(art_dir / f"{pack_id}.json")})
    return artifact



def rate(repo, pack_id: str, verdict: str, note: str = "") -> dict:
    if verdict not in ("useful", "partial", "wasted"):
        raise ValueError("verdict must be useful|partial|wasted")
    p = Path(repo.root) / ".context" / f"{pack_id}.json"
    if not p.exists():
        raise ValueError(f"unknown pack: {pack_id}")
    rec = {"pack": pack_id, "verdict": verdict, "note": note,
           "ids": [n["id"] for n in json.loads(p.read_text())["nodes"]],
           "ts": datetime.now().isoformat(timespec="seconds")}
    with (Path(repo.root) / ".context" / "ratings.jsonl").open("a") as f:
        f.write(json.dumps(rec) + "\n")
    from .observe import trace
    trace(repo, "rate", input={"pack": pack_id, "verdict": verdict},
          output={"ids": rec["ids"]})
    return rec
