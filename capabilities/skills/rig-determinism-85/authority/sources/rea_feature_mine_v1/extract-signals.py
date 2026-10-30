#!/usr/bin/env python3
"""Extract feature signals from REA scenario/inspect JSON + Aside snapshots.
Usage: extract-signals.py <name> [name2 ...]
"""
import json, os, re, sys
from html.parser import HTMLParser

WORK = "/Users/rig128gb/.rig/work/rea-feature-mine"

class TextGrab(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.skip = 0
        self.text = []
        self.links = []
        self.buttons = []
        self.headings = []
        self.metas = {}
        self.scripts = []
        self.cur_tag = None
        self.cur_href = None
        self.in_heading = False
    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag in ("script", "style", "noscript", "svg"): self.skip += 1
        elif tag == "meta":
            k = a.get("name") or a.get("property")
            if k: self.metas[k] = (a.get("content") or "")[:200]
        if tag == "a" and a.get("href"): self.links.append((a["href"], ""))
        if tag in ("button", "a", "input", "summary"):
            label = a.get("aria-label") or a.get("title") or a.get("placeholder") or a.get("value") or ""
            self.buttons.append((tag, label.strip()[:80]))
        if tag in ("h1", "h2", "h3", "h4"):
            self.in_heading = tag
            self.headings.append([tag, ""])
    def handle_endtag(self, tag):
        if tag in ("script", "style", "noscript", "svg"): self.skip = max(0, self.skip - 1)
        if tag == self.in_heading: self.in_heading = False
    def handle_data(self, data):
        t = data.strip()
        if not t: return
        if self.skip: return
        self.text.append(t)
        if self.in_heading and self.headings:
            self.headings[-1][1] = (self.headings[-1][1] + " " + t)[:160]
        if self.links and self.links[-1][1] == "" and len(t) < 80:
            h, _ = self.links[-1]
            if not h.startswith("#"): self.links[-1] = (h, t)

def grab(html):
    p = TextGrab()
    try: p.feed(html)
    except Exception: pass
    return p

def dom_texts(path):
    d = json.load(open(path))
    nr = d.get("normalized_result", d)
    out = []
    for s in nr.get("steps", []):
        dom = (s.get("artifacts") or {}).get("dom") or {}
        v = (dom.get("value") or {})
        if isinstance(v, dict) and v.get("text"):
            out.append((s.get("step_id"), v["text"]))
        acc = (s.get("artifacts") or {}).get("accessibility") or {}
        av = acc.get("value")
        if av: out.append((s.get("step_id") + ":a11y", json.dumps(av)))
    return out

for name in sys.argv[1:]:
    scen = f"{WORK}/{name}-scenario.json"
    live = f"{WORK}/aside-live"
    signals = {"urls": set(), "links": {}, "buttons": set(), "headings": [], "metas": {},
               "js_files": set(), "api_hosts": set(), "body_snippets": [], "nav_menus": []}
    files = []
    if os.path.exists(scen): files += [h for _, h in dom_texts(scen)]
    # aside-live snapshots for this site
    key = {"miro": "miro.com", "airtable": "airtable.com", "eden": "eden", "recall": "recall",
           "subframe": "subframe", "grok": "grok", "xai": "x.ai", "grok-market": "x.ai",
           "opendots": "4310"}.get(name, name)
    if os.path.isdir(live):
        for fn in os.listdir(live):
            if key in fn and fn.endswith(".json"):
                d = json.load(open(os.path.join(live, fn)))
                bt = d.get("bodyText")
                if bt: files.append(bt)
                for b in d.get("buttons", []):
                    lab = b.get("x") or b.get("n")
                    if lab: signals["buttons"].add(f"[{b.get('h') or b.get('t') or ''}] {lab}"[:100])
                for h in d.get("headings", []): signals["headings"].append(["h?", h])
                for s in d.get("scripts", []):
                    if s.startswith("http"): signals["js_files"].add(s)
    for html in files:
        p = grab(html)
        for href, label in p.links:
            signals["urls"].add(href)
            if label and not href.startswith(("#", "mailto", "javascript")):
                signals["links"].setdefault(href[:120], label[:60])
        for tag, label in p.buttons:
            if label: signals["buttons"].add(f"[{tag}] {label}"[:100])
        signals["headings"] += p.headings
        signals["metas"].update(p.metas)
        signals["js_files"] |= set(p.scripts)
        signals["body_snippets"].append(" ".join(p.text)[:1500])
    blob = "\n".join(t if isinstance(t, str) else str(t) for t in files)[:4_000_000]
    signals["api_hosts"] = {m for m in re.findall(r'https?://([a-z0-9.-]+\.(?:api|api\.|backend|graphql|rest)?[a-z0-9.-]*\.(?:com|io|app|dev|co|net|ai|so))/[a-zA-Z0-9_./-]*(?:api|graphql|v1|v2|rpc)', blob)}
    signals["integrations"] = sorted(set(m.lower() for m in re.findall(r'(slack|notion|google[ _-]?calendar|google[ _-]?drive|google meet|zoom|microsoft[ _-]?teams|jira|github|gitlab|figma|zapier|make\.com|hubspot|salesforce|atlassian|confluence|dropbox|xero|quickbooks|stripe|x\.com|twitter)', blob, re.I)))
    signals["shortcuts"] = sorted(set(re.findall(r'(?:cmd|ctrl|meta|shift|alt|option)\s*\+\s*[A-Za-z0-9]', blob, re.I)))[:120]
    out = {k: (sorted(v)[:400] if isinstance(v, set) else (dict(list(v.items())[:400]) if isinstance(v, dict) else v[:400])) for k, v in signals.items()}
    json.dump(out, open(f"{WORK}/{name}-features.json", "w"), indent=1)
    with open(f"{WORK}/{name}-digest.txt", "w") as f:
        f.write("HEADINGS:\n" + "\n".join(f"[{h}] {t}" for h, t in out["headings"][:120]))
        f.write("\n\nLINKS (href | label):\n" + "\n".join(f"{h} | {l}" for h, l in list(out["links"].items())[:250]))
        f.write("\n\nBUTTONS/LABELS:\n" + "\n".join(out["buttons"][:300]))
        f.write("\n\nINTEGRATIONS:\n" + ", ".join(out["integrations"]))
        f.write("\n\nSHORTCUTS:\n" + ", ".join(out["shortcuts"]))
        f.write("\n\nJS FILES:\n" + "\n".join(list(out["js_files"])[:120]))
        f.write("\n\nAPI HOSTS:\n" + "\n".join(list(out["api_hosts"])[:60]))
        f.write("\n\nBODY SNIPPETS:\n" + "\n---\n".join(out["body_snippets"])[:8000] + "\n")
    print(f"[{name}] headings={len(out['headings'])} links={len(out['links'])} buttons={len(out['buttons'])} js={len(out['js_files'])} integ={len(out['integrations'])} sc={len(out['shortcuts'])}")
