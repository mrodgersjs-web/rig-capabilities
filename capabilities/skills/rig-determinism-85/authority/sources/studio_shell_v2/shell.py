"""Shared studio shell (S3): UI + module registry + run history + pipeline trigger.

stdlib only. Run: python3 shell.py [port]  (default 8791, binds 127.0.0.1)
Each studio is a module = a portable-JSON pipeline under pipelines/.
"""
import json
import sys
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

import pipeline

ROOT = Path(__file__).parent
PIPELINES = ROOT / "pipelines"


def modules():
    out = []
    for p in sorted(PIPELINES.glob("*.pipeline.json")):
        spec = json.loads(p.read_text())
        out.append({"id": spec["name"], "description": spec.get("description", ""),
                    "nodes": [n["id"] for n in spec["nodes"]], "file": p.name,
                    "rocketride": spec.get("rocketride", {})})
    return out


UI = """<!doctype html><meta charset="utf-8"><title>Studio Shell</title>
<style>
 body{font:14px/1.5 -apple-system,sans-serif;margin:0;display:grid;grid-template-columns:320px 1fr;height:100vh}
 aside{background:#111;color:#eee;padding:16px;overflow:auto}
 main{padding:16px;overflow:auto}
 .mod{padding:8px;border:1px solid #333;border-radius:6px;margin-bottom:8px}
 button{cursor:pointer}
 table{border-collapse:collapse;width:100%} td,th{border:1px solid #ccc;padding:4px 8px;text-align:left;font-size:12px}
 h2{margin-top:0}
</style>
<aside><h2>Modules</h2><div id="mods">loading…</div></aside>
<main><h2>Run history / feed</h2><div id="runs">loading…</div></main>
<script>
async function load(){
  const mods = await (await fetch('/api/modules')).json();
  document.getElementById('mods').innerHTML = mods.map(m=>`
    <div class="mod"><b>${m.id}</b><br><small>${m.description}</small><br>
    <small>nodes: ${m.nodes.join(' → ')}</small><br>
    ${m.rocketride && m.rocketride.template ? `<small>rocketride: ${m.rocketride.template}</small><br>` : ''}
    <button onclick="run('${m.id}')">Run</button></div>`).join('');
  const runs = await (await fetch('/api/runs')).json();
  document.getElementById('runs').innerHTML = '<table><tr><th>time</th><th>event</th><th>run</th><th>detail</th></tr>'+
    runs.reverse().map(r=>`<tr><td>${(r.ts||'')}</td><td>${r.event}</td><td>${r.run_id||''}</td>
    <td>${r.node||r.pipeline||r.error||JSON.stringify(r.result||r.count||'')}</td></tr>`).join('')+'</table>';
}
async function run(id){ await fetch('/api/run/'+id,{method:'POST'}); load(); }
load(); setInterval(load, 5000);
</script>"""


class Handler(BaseHTTPRequestHandler):
    def _json(self, obj, code=200):
        body = json.dumps(obj).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):  # noqa: N802
        if self.path == "/" or self.path.startswith("/index"):
            body = UI.encode()
            self.send_response(200)
            self.send_header("Content-Type", "text/html")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
        elif self.path == "/api/modules":
            self._json(modules())
        elif self.path == "/api/runs":
            self._json(pipeline.run_history())
        else:
            self._json({"error": "not found"}, 404)

    def do_POST(self):  # noqa: N802
        if self.path.startswith("/api/run/"):
            mod = self.path.rsplit("/", 1)[-1]
            spec = PIPELINES / f"{mod}.pipeline.json"
            if not spec.exists():
                self._json({"error": f"no such module: {mod}"}, 404)
                return
            self._json(pipeline.run_pipeline(spec))
        else:
            self._json({"error": "not found"}, 404)

    def log_message(self, *args):  # quiet server logs; run history is the record
        pass


def main(port=8791):
    srv = ThreadingHTTPServer(("127.0.0.1", port), Handler)
    print(f"studio-shell listening on http://127.0.0.1:{port}")
    srv.serve_forever()


if __name__ == "__main__":
    main(int(sys.argv[1]) if len(sys.argv) > 1 else 8791)
