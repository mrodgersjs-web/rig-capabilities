#!/usr/bin/env python3
"""Worker E: batch-fit prescore of ApplyPilot discovered jobs -> vLLM :8201 (GPU0+2).

Read-only on ~/.applypilot; writes ~/.rig/jake/fleet/out/job-prescore.jsonl
append-per-job so the artifact grows under the governor. Resumable: existing
urls are skipped on restart. asyncio, N concurrent requests against the LAN
endpoint. Local models only.
"""
import asyncio, json, os, sqlite3, sys, urllib.request
from datetime import datetime, timezone

DB = os.path.expanduser("~/.applypilot/applypilot.db")
RESUME = os.path.expanduser("~/.applypilot/resume.txt")
OUT = os.path.expanduser("~/.rig/jake/fleet/out/job-prescore.jsonl")
URL = "http://192.168.68.90:8201/v1/chat/completions"
MODEL = "mimo-v2.6-flash"
CONC = 6
MAXTOK = 1600

SYS = (
    "You are a hiring-fit analyst for Mike Rodgers: 15+ yrs software/AI-engineering, "
    "built RIG (AI agent fleet + consulting), DevOps/platform + AI infra background, "
    "currently targeting senior/staff backend, platform, AI-infra and founding-engineer roles. "
    "Score fit 0-100 for THIS person and THIS job. Be calibrated: 90+ only with strong evidence. "
    "Answer ONLY compact JSON: {\"fit_score\":int,\"tier\":\"A|B|C\",\"evidence\":[4-6 short bullets quoting the JD],"
    "\"skills_gap\":[...],\"seniority_match\":\"over|match|under\",\"salary_note\":\"...\","
    "\"ats_risk\":\"...\",\"outhook\":\"one-line personalized outreach hook\"}"
)


def done_urls():
    """Only fully scored rows count as done; error rows are retried on resume."""
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
    yield from con.execute(
        "select url,title,site,location,description,full_description "
        "from jobs where fit_score is null")


async def one(sem, client, resume_txt, item, idx):
    desc = (item["full_description"] or item["description"] or "")[:7000]
    user = (f"RESUME:\n{resume_txt[:4000]}\n\n"
            f"JOB #{idx}\nTitle: {item['title']}\nSite: {item['site']}\n"
            f"Location: {item['location']}\nDescription:\n{desc}")
    body = json.dumps({"model": MODEL,
                       "messages": [{"role": "system", "content": SYS},
                                    {"role": "user", "content": user}],
                       "max_tokens": MAXTOK, "temperature": 0.2}).encode()
    async with sem:
        for attempt in (1, 2, 3):
            try:
                req = urllib.request.Request(URL, data=body,
                                             headers={"Content-Type": "application/json"})
                def call():
                    with urllib.request.urlopen(req, timeout=600) as r:
                        return json.load(r)
                resp = await asyncio.get_running_loop().run_in_executor(None, call)
                break
            except Exception as e:
                if attempt == 3:
                    rec = {"ts": now(), "url": item["url"], "title": item["title"], "error": str(e)[:200]}
                    with open(OUT, "a") as f:
                        f.write(json.dumps(rec, ensure_ascii=False) + "\n")
                    return
                await asyncio.sleep(5 * attempt)
    ch = resp["choices"][0]["message"]
    content = ch.get("content") or ""
    try:
        parsed = json.loads(content[content.index("{"):content.rindex("}") + 1])
    except Exception:
        parsed = {"raw": content[:2000]}
    rec = {"ts": now(), "url": item["url"], "title": item["title"],
           "site": item["site"], "fit": parsed.get("fit_score"),
           "result": parsed, "usage": resp.get("usage", {})}
    with open(OUT, "a") as f:
        f.write(json.dumps(rec, ensure_ascii=False) + "\n")


def now():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


async def main():
    resume_txt = open(RESUME).read() if os.path.exists(RESUME) else "resume.txt missing"
    skip = done_urls()
    todo = [r for r in rows() if r["url"] not in skip]
    print(f"{now()} prescore: {len(todo)} to score ({len(skip)} already done)", flush=True)
    sem = asyncio.Semaphore(CONC)
    async with asyncio.Semaphore(CONC) as _:
        pass
    chunk = 50
    for i in range(0, len(todo), chunk):
        part = todo[i:i + chunk]
        await asyncio.gather(*[one(sem, None, resume_txt, r, i + k + 1)
                               for k, r in enumerate(part)])
        print(f"{now()} progress {min(i + chunk, len(todo))}/{len(todo)}", flush=True)
    print(f"{now()} prescore COMPLETE", flush=True)


if __name__ == "__main__":
    asyncio.run(main())
