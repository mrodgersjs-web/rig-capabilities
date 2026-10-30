#!/usr/bin/env python3
"""Mine one web app via REA into feature evidence.
Usage: mine-app.py <name> <logged-in-url|-> [public-page-url ...]
"""
import json, os, re, shlex, subprocess, sys, time, urllib.request, urllib.parse

WORK = "/Users/rig128gb/.rig/work/rea-feature-mine"
CDP = "http://127.0.0.1:9333"
CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"

def jhttp(path, method="GET"):
    req = urllib.request.Request(CDP + path, method=method)
    with urllib.request.urlopen(req, timeout=10) as r:
        return json.load(r)

def run(cmd, timeout=300):
    p = subprocess.run(shlex.split(cmd), capture_output=True, text=True, timeout=timeout)
    return p.returncode, p.stdout, p.stderr

def nr_of(d):
    return d.get("normalized_result") or d.get("data", {}).get("normalized_result") or {}

def open_tab(url, wait=12):
    t = jhttp("/json/new?" + urllib.parse.quote(url, safe=""), "PUT")
    time.sleep(wait)
    return next((x for x in jhttp("/json/list") if x["id"] == t["id"]), t)

def write_scripts(srcdir, docs):
    """Persist every JS source text found in REA docs; return count."""
    n = 0
    def save(url, text):
        nonlocal n
        fname = re.sub(r"[^A-Za-z0-9._-]", "_", (url or f"anon-{n}").split("//", 1)[-1].split("?")[0])[-110:]
        if not fname.endswith(".js"): fname += ".js"
        p = os.path.join(srcdir, fname)
        if os.path.exists(p) and os.path.getsize(p) >= len(text): return
        open(p, "w").write(text); n += 1
    def walk(o):
        if isinstance(o, dict):
            if isinstance(o.get("text"), str) and len(o.get("text","")) > 40 and (o.get("media_type","").startswith("text/javascript") or o.get("sha256")):
                save(o.get("url") or ("sha-" + o.get("sha256","anon")[:16]), o["text"])
            for v in o.values(): walk(v)
        elif isinstance(o, list):
            for v in o: walk(v)
    for d in docs: walk(d)
    return n

def js_urls_in(docs):
    urls = set()
    for d in docs:
        for m in re.finditer(r'"(https?://[^"\\]+\.js[^"\\]*)"', json.dumps(d)):
            urls.add(m.group(1))
    return urls

def main():
    name, landing = sys.argv[1], sys.argv[2]
    public_pages = sys.argv[3:]
    os.makedirs(WORK, exist_ok=True)
    srcdir = f"{WORK}/{name}-scripts"; os.makedirs(srcdir, exist_ok=True)
    docs = []

    if landing != "-":
        try:
            t = open_tab(landing)
            tid = t["id"]
            print(f"[{name}] tab {tid[:8]} {t['url'][:80]} | {t.get('title','')[:50]}")
            rc, out, err = run(f"rea inspect-web-page {CDP} {tid} --include-accessibility-text --include-script-sources --include-storage-keys --observation-ms 5000 --json")
            if rc == 0:
                open(f"{WORK}/{name}-inspect.json", "w").write(out)
                d = json.loads(out); docs.append(d)
                nr = nr_of(d)
                print(f"[{name}] inspect dom={nr.get('dom',{}).get('total_nodes')} a11y={nr.get('accessibility',{}).get('total_nodes')} scripts={nr.get('scripts',{}).get('total')}")
            else:
                print(f"[{name}] inspect FAILED {out[:120]}")
            rc, out, err = run(f"rea analyze-web-bundle {CDP} {tid} --observation-ms 5000 --json")
            if rc == 0:
                open(f"{WORK}/{name}-bundle.json", "w").write(out)
                d = json.loads(out); docs.append(d)
                nr = nr_of(d); cap, obs = nr.get("capture", {}), nr.get("observations", {})
                print(f"[{name}] bundle scripts {cap.get('scripts_observed')}/{cap.get('scripts_analyzed')} routes={len(obs.get('routes', []))} endpoints={len(obs.get('endpoints', []))}")
            jhttp("/json/close/" + tid)
        except Exception as e:
            print(f"[{name}] stage1 error: {e}")

    if public_pages:
        urls = public_pages[:2]
        actions = []
        for i, u in enumerate(urls):
            if i > 0:
                actions.append({"step_id": f"go{i}", "action": "goto", "destination": {"url": u, "query": []}, "wait_until": "load"})
            actions.append({"step_id": f"w{i}", "action": "wait_for_timeout", "duration_ms": 5000})
        payload = {"browser": {"mode": "launch", "executable_path": CHROME, "headless": True},
                   "start_url": {"url": urls[0], "query": []}, "actions": actions,
                   "capture": {"at_end": ["url", "dom", "accessibility", "storage"], "events": ["network", "console", "workers"]}}
        ipath = f"{WORK}/{name}-scenario.json"
        if os.path.exists(ipath) and os.path.getsize(ipath) > 1000:
            d = json.load(open(ipath)); docs.append(d)
            nr = nr_of(d)
            print(f"[{name}] scenario REUSED steps={len(nr.get('steps',[]))} events={len(nr.get('events',{}).get('items',[]))}")
        else:
            ipath = f"{WORK}/{name}-scenario-input.json"
            json.dump(payload, open(ipath, "w"))
            rc, out, err = run(f"rea capture-browser-scenario {shlex.quote(ipath)} --json")
            if rc == 0:
                open(f"{WORK}/{name}-scenario.json", "w").write(out)
                d = json.loads(out); docs.append(d)
                nr = nr_of(d)
                print(f"[{name}] scenario steps={len(nr.get('steps',[]))} events={len(nr.get('events',{}).get('items',[]))}")
            else:
                print(f"[{name}] scenario FAILED {out[:150]}")

    saved = write_scripts(srcdir, docs)
    allurls = js_urls_in(docs)
    dl = 0
    for u in sorted(allurls)[:60]:
        fname = re.sub(r"[^A-Za-z0-9._-]", "_", u.split("//", 1)[-1].split("?")[0])[-110:]
        if not fname.endswith(".js"): fname += ".js"
        p = os.path.join(srcdir, fname)
        if os.path.exists(p) and os.path.getsize(p) > 0: dl += 1; continue
        rc, _, _ = run(f"curl -sL --max-time 20 -o {shlex.quote(p)} {shlex.quote(u)}", timeout=30)
        if rc == 0 and os.path.exists(p) and os.path.getsize(p) > 0: dl += 1
        else:
            try: os.remove(p)
            except Exception: pass

    blob = "".join(open(f"{WORK}/{name}{s}").read() for s in ("-inspect.json", "-scenario.json", "-bundle.json") if os.path.exists(f"{WORK}/{name}{s}"))
    signals = {}
    signals["page_urls"] = sorted(set(re.findall(r'"(https?://[^"\\]+)"', blob)))[:600]
    signals["js_urls"] = sorted(allurls)[:200]
    signals["integrations"] = sorted(set(m.lower() for m in re.findall(r'(slack|notion|google[ _-]?calendar|google[ _-]?drive|google meet|meet\.google|zoom|microsoft[ _-]?teams|jira|github|gitlab|figma|zapier|make\.com|hubspot|salesforce|atlassian|confluence|dropbox|box\.com|xero|quickbooks|stripe)', blob, re.I)))
    signals["shortcuts"] = sorted(set(re.findall(r'(?:cmd|ctrl|meta|shift|alt|option)\s*\+\s*[A-Za-z0-9]', blob, re.I)))[:150]
    names = set(re.findall(r'"(?:name|label|text|title)"\s*:\s*"([^"\\]{4,90})"', blob))
    signals["ui_texts"] = sorted(n for n in names if not re.search(r'[{}<>]|https?://|function|var |window\.|=|;|%[0-9a-f]{2}', n))[:900]
    open(f"{WORK}/{name}-signals.json", "w").write(json.dumps(signals, indent=1))
    with open(f"{WORK}/{name}-digest.txt", "w") as f:
        f.write("PAGE URLS:\n" + "\n".join(u for u in signals["page_urls"] if WORK not in u)[:20000])
        f.write("\n\nINTEGRATIONS:\n" + "\n".join(signals["integrations"]))
        f.write("\n\nSHORTCUTS:\n" + "\n".join(signals["shortcuts"]))
        f.write("\n\nUI TEXTS:\n" + "\n".join(signals["ui_texts"])[:60000] + "\n")
    print(f"[{name}] scripts inline={saved} downloaded={dl} srcdir={len(os.listdir(srcdir))} | ui={len(signals['ui_texts'])} integ={len(signals['integrations'])} sc={len(signals['shortcuts'])}")

if __name__ == "__main__":
    main()
