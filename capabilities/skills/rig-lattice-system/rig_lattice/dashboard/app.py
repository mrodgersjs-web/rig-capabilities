"""FastAPI dashboard for RIG Deviator™ — read-only operator control plane.

Endpoints:
  GET  /                         → HTML index (operator dashboard)
  GET  /health                    → JSON health summary
  GET  /api/missions              → recent missions (paged)
  GET  /api/missions/{id}         → mission detail + engine scores
  GET  /api/daemon                → daemon slot status
  GET  /api/alerts                → recent alerts
  GET  /api/cost-ledger           → cost ledger summary
  GET  /api/integrations          → integration availability
  GET  /api/sli                   → SLO/SLI tracker status
  POST /api/run                   → trigger a new system run (gated, opt-in)

Auth: this is a localhost-only dashboard by default. For remote access,
front with reverse-proxy + auth (nginx/Caddy + Tailscale or OAuth proxy).
The endpoint is intentionally read-heavy — destructive actions require
explicit env opt-in (`RIG_DV_DASHBOARD_ALLOW_RUN=1`).
"""
from __future__ import annotations
import os
import sys
from pathlib import Path

ROOT = Path(__file__).parent.parent

from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import HTMLResponse, JSONResponse

app = FastAPI(
    title="RIG Deviator™ — Operator Dashboard",
    version="1.2.0",
    description="Read-only control plane for the 7-level / 28-archetype system.",
)


# ── HTML index ───────────────────────────────────────────────────────────
_INDEX_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>RIG Deviator™ — Operator Dashboard</title>
<style>
  :root {
    --bg: #0a0a0c; --fg: #e8e8ed; --muted: #8a8a93; --acc: #4ade80;
    --warn: #fbbf24; --crit: #ef4444; --panel: #14141a; --border: #2a2a33;
  }
  * { box-sizing: border-box; }
  body { margin: 0; font: 14px/1.5 ui-monospace, SF Mono, Menlo, Consolas, monospace;
         background: var(--bg); color: var(--fg); }
  header { padding: 16px 24px; border-bottom: 1px solid var(--border);
           display: flex; align-items: center; justify-content: space-between; }
  header h1 { margin: 0; font-size: 18px; font-weight: 600; }
  header .ver { color: var(--muted); font-size: 12px; }
  main { padding: 24px; max-width: 1400px; margin: 0 auto; }
  .grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
          gap: 16px; margin-bottom: 24px; }
  .card { background: var(--panel); border: 1px solid var(--border); border-radius: 8px;
          padding: 16px; }
  .card h2 { margin: 0 0 12px; font-size: 13px; text-transform: uppercase;
              letter-spacing: 0.08em; color: var(--muted); font-weight: 600; }
  .stat { display: flex; justify-content: space-between; padding: 4px 0;
          border-bottom: 1px solid var(--border); }
  .stat:last-child { border-bottom: 0; }
  .stat .k { color: var(--muted); }
  .stat .v { font-weight: 600; }
  .ok { color: var(--acc); }
  .warn { color: var(--warn); }
  .crit { color: var(--crit); }
  table { width: 100%; border-collapse: collapse; font-size: 12px; }
  th, td { padding: 6px 8px; text-align: left; border-bottom: 1px solid var(--border); }
  th { color: var(--muted); font-weight: 600; text-transform: uppercase;
        font-size: 11px; letter-spacing: 0.05em; }
  td.num { text-align: right; font-variant-numeric: tabular-nums; }
  .pill { display: inline-block; padding: 2px 8px; border-radius: 10px;
          font-size: 11px; background: var(--border); }
  .pill.ok { background: rgba(74,222,128,0.15); color: var(--acc); }
  .pill.warn { background: rgba(251,191,36,0.15); color: var(--warn); }
  .pill.crit { background: rgba(239,68,68,0.15); color: var(--crit); }
  .refresh { color: var(--muted); font-size: 11px; cursor: pointer; }
  .refresh:hover { color: var(--fg); }
  pre { font: 11px/1.4 ui-monospace, Menlo, Consolas, monospace;
        margin: 0; max-height: 220px; overflow: auto;
        background: #050507; padding: 8px; border-radius: 4px; }
</style>
</head>
<body>
<header>
  <h1>RIG Deviator™ — Operator Dashboard</h1>
  <div>
    <span class="ver">v1.2.0</span>
    <span class="refresh" onclick="loadAll()">⟳ refresh</span>
  </div>
</header>
<main>
  <div class="grid">
    <div class="card"><h2>Health</h2><div id="health">loading…</div></div>
    <div class="card"><h2>Daemon Slots</h2><div id="daemon">loading…</div></div>
    <div class="card"><h2>SLOs / SLIs</h2><div id="sli">loading…</div></div>
    <div class="card"><h2>Integrations</h2><div id="integrations">loading…</div></div>
    <div class="card"><h2>Cost Ledger</h2><div id="cost">loading…</div></div>
    <div class="card"><h2>Recent Alerts</h2><div id="alerts">loading…</div></div>
  </div>
  <div class="card">
    <h2>Recent Missions</h2>
    <div id="missions">loading…</div>
  </div>
</main>
<script>
async function fetchJSON(url) {
  try { const r = await fetch(url); return await r.json(); }
  catch (e) { return { error: e.toString() }; }
}
function pill(status) {
  const s = (status || '').toLowerCase();
  const cls = s.includes('hard') ? 'crit' :
              s.includes('strict') || s.includes('ok') || s.includes('passed') || s.includes('healthy') ? 'ok' :
              s.includes('warn') || s.includes('burning') ? 'warn' : '';
  return `<span class="pill ${cls}">${status}</span>`;
}
function renderHealth(d) {
  if (d.error) return `<div class="crit">${d.error}</div>`;
  const checks = d.checks || [];
  let html = `<div class="stat"><span class="k">Passed</span><span class="v ok">${d.passed||0}/${d.total||0}</span></div>`;
  for (const c of checks.slice(0, 6)) {
    const cls = c.ok ? 'ok' : 'crit';
    html += `<div class="stat"><span class="k">${c.name}</span><span class="v ${cls}">${c.ok ? '✓' : '✗'}</span></div>`;
  }
  return html;
}
function renderDaemon(d) {
  if (d.error) return `<div class="crit">${d.error}</div>`;
  let html = `<div class="stat"><span class="k">Total slots</span><span class="v">${d.total_slots}</span></div>`;
  html += `<div class="stat"><span class="k">Running</span><span class="v">${d.running}</span></div>`;
  html += `<div class="stat"><span class="k">Errored</span><span class="v ${d.errored ? 'crit' : 'ok'}">${d.errored}</span></div>`;
  return html;
}
function renderSLI(d) {
  if (d.error) return `<div class="crit">${d.error}</div>`;
  const keys = Object.keys(d);
  if (!keys.length) return '<div class="stat"><span class="k">No SLIs recorded yet</span></div>';
  let html = '';
  for (const k of keys.slice(0, 6)) {
    const cls = d[k].status === 'HEALTHY' ? 'ok' : d[k].status === 'BURNING' ? 'warn' : 'crit';
    html += `<div class="stat"><span class="k">${k}</span><span class="v ${cls}">${(d[k].availability*100).toFixed(2)}%</span></div>`;
  }
  return html;
}
function renderIntegrations(d) {
  if (d.error) return `<div class="crit">${d.error}</div>`;
  let html = '';
  for (const [k, v] of Object.entries(d)) {
    const ok = v.available;
    html += `<div class="stat"><span class="k">${k}</span><span class="v ${ok ? 'ok' : ''}">${ok ? 'available' : '—'}</span></div>`;
  }
  return html;
}
function renderCost(d) {
  if (d.error) return `<div class="crit">${d.error}</div>`;
  let html = `<div class="stat"><span class="k">Total entries</span><span class="v">${d.total_entries||0}</span></div>`;
  html += `<div class="stat"><span class="k">Total USD</span><span class="v">$${(d.total_usd||0).toFixed(4)}</span></div>`;
  const models = Object.entries(d.by_model || {});
  for (const [m, v] of models.slice(0, 4)) {
    html += `<div class="stat"><span class="k">${m}</span><span class="v">${v.calls} calls / $${v.usd.toFixed(4)}</span></div>`;
  }
  return html;
}
function renderAlerts(d) {
  if (d.error) return `<div class="crit">${d.error}</div>`;
  const alerts = d.alerts || [];
  if (!alerts.length) return '<div class="stat"><span class="k">No alerts</span><span class="v ok">clean</span></div>';
  let html = '';
  for (const a of alerts.slice(-6).reverse()) {
    const cls = a.severity === 'critical' ? 'crit' : a.severity === 'warn' ? 'warn' : '';
    html += `<div class="stat"><span class="k">${a.name}</span><span class="v ${cls}">${a.severity}</span></div>`;
  }
  return html;
}
function renderMissions(d) {
  if (d.error) return `<div class="crit">${d.error}</div>`;
  const missions = d.missions || [];
  if (!missions.length) return '<div class="stat"><span class="k">No missions yet</span></div>';
  let html = '<table><thead><tr><th>Mission ID</th><th>Mode</th><th>Tier</th>'
           + '<th class="num">Confidence</th><th class="num">RIG-L</th><th>Status</th>'
           + '<th>Weakest Gate</th><th>Created</th></tr></thead><tbody>';
  for (const m of missions) {
    html += `<tr>
      <td><a href="/api/missions/${m.mission_id}" style="color:var(--acc);text-decoration:none">${m.mission_id}</a></td>
      <td>${m.bms_mode||''}</td>
      <td>${m.tier||''}</td>
      <td class="num">${(m.confidence||0).toFixed(2)}</td>
      <td class="num">${(m.rig_l||0).toFixed(2)}</td>
      <td>${pill(m.status)}</td>
      <td>${m.weakest_gate||'—'}</td>
      <td>${m.created_at||''}</td>
    </tr>`;
  }
  return html + '</tbody></table>';
}
async function loadAll() {
  document.getElementById('health').innerHTML        = renderHealth(await fetchJSON('/health'));
  document.getElementById('daemon').innerHTML        = renderDaemon(await fetchJSON('/api/daemon'));
  document.getElementById('sli').innerHTML            = renderSLI(await fetchJSON('/api/sli'));
  document.getElementById('integrations').innerHTML  = renderIntegrations(await fetchJSON('/api/integrations'));
  document.getElementById('cost').innerHTML           = renderCost(await fetchJSON('/api/cost-ledger'));
  document.getElementById('alerts').innerHTML         = renderAlerts(await fetchJSON('/api/alerts'));
  document.getElementById('missions').innerHTML       = renderMissions(await fetchJSON('/api/missions'));
}
loadAll();
setInterval(loadAll, 30000);
</script>
</body>
</html>"""


@app.get("/", response_class=HTMLResponse)
async def index() -> str:
    return _INDEX_HTML


# ── Health ───────────────────────────────────────────────────────────────
@app.get("/health")
async def health() -> dict:
    try:
        from rig_lattice.enterprise.observability import health_summary
        return health_summary()
    except Exception as e:
        return {"error": f"{type(e).__name__}: {e}"}


# ── Missions ─────────────────────────────────────────────────────────────
@app.get("/api/missions")
async def missions(limit: int = Query(20, ge=1, le=200)) -> dict:
    try:
        from rig_lattice.system.persistence import recent_missions
        return {"missions": recent_missions(limit=limit)}
    except Exception as e:
        return {"error": f"{type(e).__name__}: {e}"}


@app.get("/api/missions/{mission_id}")
async def mission_detail(mission_id: str) -> dict:
    try:
        from rig_lattice.system.persistence import mission_detail as detail_fn
        d = detail_fn(mission_id)
        if not d:
            raise HTTPException(status_code=404, detail=f"mission {mission_id} not found")
        return d
    except HTTPException:
        raise
    except Exception as e:
        return {"error": f"{type(e).__name__}: {e}"}


# ── Daemon ───────────────────────────────────────────────────────────────
@app.get("/api/daemon")
async def daemon_status() -> dict:
    try:
        from rig_lattice.enterprise.daemon import Daemon
        d = Daemon()
        return d.status()
    except Exception as e:
        return {"error": f"{type(e).__name__}: {e}"}


# ── Alerts ───────────────────────────────────────────────────────────────
@app.get("/api/alerts")
async def alerts() -> dict:
    try:
        from rig_lattice.enterprise.sre import recent_alerts
        items = recent_alerts(limit=50)
        return {"alerts": [
            {
                "name": a.name,
                "severity": a.severity.value if hasattr(a.severity, "value") else str(a.severity),
                "message": a.message,
                "timestamp": a.timestamp,
            }
            for a in items
        ]}
    except Exception as e:
        return {"error": f"{type(e).__name__}: {e}"}


# ── Cost ledger ──────────────────────────────────────────────────────────
@app.get("/api/cost-ledger")
async def cost_ledger() -> dict:
    try:
        from rig_lattice.enterprise.cost_ledger import ledger_summary
        return ledger_summary()
    except Exception as e:
        return {"error": f"{type(e).__name__}: {e}"}


# ── Integrations ─────────────────────────────────────────────────────────
@app.get("/api/integrations")
async def integrations() -> dict:
    try:
        from rig_lattice.enterprise.integrations import integrations_status
        return integrations_status()
    except Exception as e:
        return {"error": f"{type(e).__name__}: {e}"}


# ── SLI/SLO ──────────────────────────────────────────────────────────────
@app.get("/api/sli")
async def sli() -> dict:
    try:
        from rig_lattice.enterprise.sre import sli_status
        return sli_status()
    except Exception as e:
        return {"error": f"{type(e).__name__}: {e}"}


# ── Notifications ────────────────────────────────────────────────────────
@app.get("/api/notifications/status")
async def notifications_status() -> dict:
    try:
        from rig_lattice.enterprise.notify import channel_status
        return channel_status()
    except Exception as e:
        return {"error": f"{type(e).__name__}: {e}"}


# ── Run trigger (opt-in only) ────────────────────────────────────────────
@app.post("/api/run")
async def run(body: dict) -> dict:
    if os.environ.get("RIG_DV_DASHBOARD_ALLOW_RUN") != "1":
        raise HTTPException(status_code=403,
                              detail="dashboard run trigger disabled. "
                                     "set RIG_DV_DASHBOARD_ALLOW_RUN=1 to enable.")
    source = body.get("source")
    if not source:
        raise HTTPException(status_code=400, detail="missing 'source'")
    try:
        from rig_lattice.system import run_system
        result = run_system(
            source=source,
            confidence=body.get("confidence", 0.85),
            tier=body.get("tier", "client"),
            stdin_text=body.get("stdin_text", ""),
        )
        return result.to_dict()
    except Exception as e:
        return JSONResponse(status_code=500,
                              content={"error": f"{type(e).__name__}: {e}"})


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "dashboard.app:app",
        host=os.environ.get("RIG_DV_DASHBOARD_HOST", "127.0.0.1"),
        port=int(os.environ.get("RIG_DV_DASHBOARD_PORT", "8088")),
        log_level="info",
    )
