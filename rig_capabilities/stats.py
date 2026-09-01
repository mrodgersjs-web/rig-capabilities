"""V21: /stats.json + /dashboard on the serve surface.

Aggregates only — source/kind counts, quality-run pass rates, round graduations,
LLM-overlay coverage, federation peers, version. No asset contents, no paths,
no requester names, so the panel can stay public while /index.json stays
Bearer-protected. The dashboard is a dependency-free HTML shell that polls
/stats.json client-side.
"""
from __future__ import annotations

import json
from collections import Counter
from pathlib import Path

from . import __version__


def compute(repo) -> dict:
    root = Path(repo.root)
    doc = repo.load_index()
    assets = doc.get("assets") or []
    by_source = Counter(a.get("source", "?") for a in assets)
    by_kind = Counter(a.get("kind", "?") for a in assets)

    runs = []
    qr = root / ".context" / "quality-runs"
    if qr.is_dir():
        for p in sorted(qr.glob("*.json"))[-5:]:
            try:
                d = json.loads(p.read_text())
                runs.append({"ts": d.get("ts"), "lane": d.get("lane"),
                             "ran": d.get("ran"), "passed": d.get("passed"),
                             "pass_rate": d.get("pass_rate")})
            except (json.JSONDecodeError, OSError):
                continue

    rounds = []
    rd = root / ".context" / "rounds"
    if rd.is_dir():
        for p in sorted(rd.glob("*.json"))[-8:]:
            try:
                d = json.loads(p.read_text())
                rounds.append({"ts": d.get("ts"), "lane": d.get("lane"),
                               "dry": d.get("dry"),
                               "graduated": d.get("graduated", 0)})
            except (json.JSONDecodeError, OSError):
                continue

    llm = root / ".concepts.llm.json"
    overlay = tagged = 0
    if llm.exists():
        try:
            d = json.loads(llm.read_text())
            overlay = len(d)
            tagged = sum(1 for v in d.values() if v)
        except (json.JSONDecodeError, OSError):
            pass

    fed = [f.get("label") for f in repo.config().get("federates") or []
           if isinstance(f, dict)]
    fed_assets = sum(1 for a in assets if str(a.get("source", "")).startswith("fed:"))

    traces = {"count": 0, "by_name": {}, "recent": []}
    tp = root / ".context" / "traces.jsonl"
    if tp.exists():
        names = Counter()
        recent = []
        n = 0
        for line in tp.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            n += 1
            try:
                ev = json.loads(line)
            except json.JSONDecodeError:
                continue
            names[ev.get("name") or "?"] += 1
            recent.append({"ts": ev.get("ts"), "name": ev.get("name")})
        traces = {"count": n, "by_name": dict(names), "recent": recent[-20:]}

    return {"version": __version__, "generated_at": doc.get("generated_at"),
            "assets": len(assets), "by_source": dict(by_source),
            "by_kind": dict(by_kind), "quality_runs": runs, "rounds": rounds,
            "concepts_llm": {"entries": overlay, "tagged": tagged},
            "federates": fed, "federated_assets": fed_assets,
            "traces": traces}


_HTML = """<!doctype html><html lang=en><meta charset=utf-8>
<meta name=viewport content="width=device-width,initial-scale=1">
<title>rig-capabilities</title>
<style>
 body{font:14px/1.5 ui-monospace,Menlo,monospace;background:#0b0e14;color:#d7dbe4;margin:0;padding:2rem}
 h1{font-size:1.1rem;letter-spacing:.06em;color:#8fb3ff}
 .grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(220px,1fr));gap:12px;max-width:960px}
 .card{background:#121724;border:1px solid #1f2637;border-radius:8px;padding:12px}
 .k{color:#6b7488;font-size:.75rem;text-transform:uppercase;letter-spacing:.08em}
 .v{font-size:1.5rem;color:#e8ecf5} table{border-collapse:collapse;margin-top:6px}
 td{padding:2px 10px 2px 0;color:#aab3c5} .ok{color:#7fd18a}.bad{color:#e0736f}
 pre{color:#8a93a8;white-space:pre-wrap}
</style><h1>RIG CAPABILITIES · <span id=v></span></h1>
<div class=grid id=g></div><script>
async function tick(){try{
 const s=await (await fetch('/stats.json')).json();
 v.textContent='v'+s.version;
 const g=document.getElementById('g');
 const rows=[
  ['assets',s.assets],['sources',Object.keys(s.by_source).length],
  ['kinds',Object.keys(s.by_kind).length],
  ['fed peers',(s.federates||[]).join(', ')||'none'],
  ['fed assets',s.federated_assets],
  ['llm overlay',s.concepts_llm.tagged+' / '+s.concepts_llm.entries],
  ['traces',(s.traces&&s.traces.count)||0],
 ];
 const last=(s.quality_runs||[]).slice(-1)[0];
 if(last) rows.push(['done-tests pass rate',(last.pass_rate*100).toFixed(0)+'% · ran '+last.ran]);
 const grad=(s.rounds||[]).filter(r=>!r.dry).reduce((a,r)=>a+(r.graduated||0),0);
 rows.push(['round graduations',grad]);
 const lastT=((s.traces&&s.traces.recent)||[]).slice(-3).map(e=>e.name).join(', ');
 if(lastT) rows.push(['last traces',lastT]);
 let h='';for(const [k,val] of rows) h+='<div class=card><div class=k>'+k+'</div><div class=v>'+val+'</div></div>';
 for(const [src,n] of Object.entries(s.by_source).sort((a,b)=>b[1]-a[1]).slice(0,8))
   h+='<div class=card><div class=k>'+src+'</div><div class=v>'+n+'</div></div>';
 g.innerHTML=h;
}catch(e){v.textContent='stats unavailable'}}
tick();setInterval(tick,5000);
</script>"""


def dashboard_html() -> str:
    return _HTML
