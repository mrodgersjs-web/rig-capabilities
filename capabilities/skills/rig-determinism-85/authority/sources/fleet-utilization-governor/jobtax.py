#!/usr/bin/env python3
"""E-jobtax: extract skills/seniority/salary/ATS-keyword taxonomy from the 1,362
ApplyPilot discovered jobs via local vLLM :8201. Distinct artifact from the fit
prescore (job-taxonomy.jsonl). Resumable; append-per-job; stdlib only."""
import asyncio, json, os, sqlite3, urllib.request
from datetime import datetime, timezone

DB = os.path.expanduser("~/.applypilot/applypilot.db")
OUT = os.path.expanduser("~/.rig/jake/fleet/out/job-taxonomy.jsonl")
URL = "http://192.168.68.90:8201/v1/chat/completions"
MODEL = "mimo-v2.6-flash"
CONC = 4
MAXTOK = 900
SYS = ("Extract a hiring-ops taxonomy from the job posting. Answer ONLY compact JSON: "
       "{\"skills\":[6-10 exact skill tokens],\"seniority\":\"junior|mid|senior|staff|lead\","
       "\"years_hint\":\"e.g. 5-8\",\"remote\":\"onsite|hybrid|remote|unknown\","
       "\"salary\":\"structured band or unknown\",\"ats_keywords\":[5-8],"
       "\"domain\":\"e.g. fintech|healthtech|govtech|saas|other\"}")

def done():
    s = set()
    if os.path.exists(OUT):
        for l in open(OUT):
            try:
                d = json.loads(l)
                if "error" not in d and "url" in d:
                    s.add(d["url"])
            except Exception:
                pass
    return s

def rows():
    con = sqlite3.connect(f"file:{DB}?mode=ro", uri=True)
    con.row_factory = sqlite3.Row
    yield from con.execute("select url,title,site,location,description,full_description from jobs")

async def one(sem, item, idx):
    desc = (item["full_description"] or item["description"] or "")[:7000]
    user = f"Title: {item['title']}\nSite: {item['site']}\nLocation: {item['location']}\n{desc}"
    body = json.dumps({"model": MODEL,
                       "messages": [{"role": "system", "content": SYS},
                                    {"role": "user", "content": user}],
                       "max_tokens": MAXTOK, "temperature": 0.1}).encode()
    async with sem:
        for attempt in (1, 2, 3):
            try:
                def call():
                    req = urllib.request.Request(URL, data=body,
                                                 headers={"Content-Type": "application/json"})
                    with urllib.request.urlopen(req, timeout=600) as r:
                        return json.load(r)
                resp = await asyncio.get_running_loop().run_in_executor(None, call)
                break
            except Exception as e:
                if attempt == 3:
                    with open(OUT, "a") as f:
                        f.write(json.dumps({"url": item["url"], "error": str(e)[:200]}) + "\n")
                    return
                await asyncio.sleep(5 * attempt)
    content = resp["choices"][0]["message"].get("content") or ""
    try:
        parsed = json.loads(content[content.index("{"):content.rindex("}") + 1])
    except Exception:
        parsed = {"raw": content[:1500]}
    with open(OUT, "a") as f:
        f.write(json.dumps({"ts": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
                            "url": item["url"], "title": item["title"],
                            "taxonomy": parsed}, ensure_ascii=False) + "\n")

async def main():
    skip, todo = done(), [r for r in rows() if r["url"] not in skip]
    print(f"jobtax: {len(todo)} to do", flush=True)
    sem = asyncio.Semaphore(CONC)
    for i in range(0, len(todo), 40):
        await asyncio.gather(*[one(sem, r, i + k) for k, r in enumerate(todo[i:i + 40])])
        print(f"jobtax progress {min(i+40, len(todo))}/{len(todo)}", flush=True)
    print("jobtax COMPLETE", flush=True)

if __name__ == "__main__":
    asyncio.run(main())
