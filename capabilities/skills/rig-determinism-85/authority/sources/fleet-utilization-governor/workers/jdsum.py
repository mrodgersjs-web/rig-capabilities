#!/usr/bin/env python3
"""E-jdsum: summarize/classify ApplyPilot saved JDs + discovered jobs through the
host's local ollama. Stdlib only. Appends ~/.rig/jake/fleet/out/jd-summary.jsonl
one line per item (artifact grows); skips urls already done (resumable).
"""
import json, os, sys, time, urllib.request

JAKE = os.path.expanduser("~/.rig/jake/fleet")
SAVED = os.path.join(JAKE, "work/saved-jd")
JOBS = os.path.join(JAKE, "work/discovered-jobs.jsonl")
OUT = os.path.join(JAKE, "out/jd-summary.jsonl")
MODEL = os.environ.get("E_MODEL", "qwen3.6:35b-a3b")
OLLAMA = os.environ.get("E_OLLAMA", "http://127.0.0.1:11434")

SYS = ("You are a labor-market analyst. For the posting below produce compact JSON only: "
       "{\"kind\":\"job|jd_saved\",\"family\":\"platform|backend|devsecops|data|ml|frontend|other\","
       "\"seniority\":\"junior|mid|senior|staff|lead|unknown\",\"remote\":\"onsite|hybrid|remote|unknown\","
       "\"summary\":\"<=25 words\",\"top_skills\":[5],\"salary\":\"band or unknown\","
       "\"fit_note\":\"<=30 words for Mike (ex-staff eng, AI infra, RIG founder)\"}")


def ask(prompt):
    body = json.dumps({"model": MODEL,
                       "messages": [{"role": "system", "content": SYS},
                                    {"role": "user", "content": prompt}],
                       "stream": False, "think": False,
                       "options": {"num_predict": 700, "temperature": 0.2}}).encode()
    req = urllib.request.Request(OLLAMA + "/api/chat", data=body,
                                 headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=900) as r:
        d = json.load(r)
    msg = d.get("message", {})
    return (msg.get("content") or ""), d.get("done_reason", "")


def parse(txt):
    try:
        return json.loads(txt[txt.index("{"):txt.rindex("}") + 1])
    except Exception:
        return {"raw": txt[:800]}


def done_keys():
    s = set()
    if os.path.exists(OUT):
        for l in open(OUT):
            try:
                r = json.loads(l)
                s.add(r.get("key"))
            except Exception:
                pass
    return s


def emit(rec):
    with open(OUT, "a") as f:
        f.write(json.dumps(rec, ensure_ascii=False) + "\n")


def wait_ready():
    """Wait up to 8 min for staged inputs; never emit DONE on empty staging."""
    for _ in range(32):
        if os.path.exists(JOBS) or (os.path.isdir(SAVED) and os.listdir(SAVED)):
            return True
        time.sleep(15)
    print("jdsum: inputs never appeared; exiting without DONE", flush=True)
    return False


def main():
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    if not wait_ready():
        sys.exit(1)
    skip = done_keys()
    items = []
    for fn in sorted(os.listdir(SAVED)) if os.path.isdir(SAVED) else []:
        if not fn.endswith(".txt"):
            continue
        p = os.path.join(SAVED, fn)
        items.append(("jd_saved:" + fn, open(p, errors="replace").read()[:7000]))
    if os.path.exists(JOBS):
        for l in open(JOBS):
            try:
                j = json.loads(l)
            except ValueError:
                continue
            items.append(("job:" + j["url"],
                          f"Title: {j.get('title')}\nSite: {j.get('site')}\n"
                          f"Location: {j.get('location')}\n{j.get('text','')[:6500]}"))
    todo = [it for it in items if it[0] not in skip]
    print(f"jdsum start: {len(todo)}/{len(items)} items model={MODEL}", flush=True)
    for i, (key, text) in enumerate(todo):
        for attempt in (1, 2, 3):
            try:
                txt, reason = ask(text)
                break
            except Exception as e:
                if attempt == 3:
                    emit({"key": key, "error": str(e)[:200]})
                    txt, reason = "", "error"
                time.sleep(10 * attempt)
        if txt:
            emit({"key": key, "model": MODEL, "result": parse(txt), "done_reason": reason})
        else:
            emit({"key": key, "model": MODEL, "empty": True, "done_reason": reason})
        if (i + 1) % 10 == 0:
            print(f"jdsum {i+1}/{len(todo)}", flush=True)
    open(os.path.join(JAKE, "out/jd-summary.DONE"), "w").write("complete\n")
    print("jdsum COMPLETE", flush=True)


if __name__ == "__main__":
    main()
