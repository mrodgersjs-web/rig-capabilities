#!/usr/bin/env python3
"""E-m03digest: chunk YouTube transcripts and extract demand-relevant observations
through the host's local model for mission M03 demand mining.
Appends ~/.rig/jake/fleet/out/m03-transcript-digest-<HOST>.jsonl (grows);
resumable by (file, chunk offset); DONE flag when the shard is exhausted.

Args: <host-tag> <ollama-url> <model> <transcript-dir>
"""
import json, os, sys, time, urllib.request

HOST, OLLAMA, MODEL, SRC = sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4]
LENS = os.environ.get("E_LENS", "")  # "" = demand signals; "tools" = tool/company mentions
JAKE = os.path.expanduser("~/.rig/jake/fleet")
OUT = os.path.join(JAKE, f"out/m03-transcript-digest-{HOST}{'-' + LENS if LENS else ''}.jsonl")
CHUNK = 12000

if LENS == "tools":
    SYS = ("You read transcripts of YouTube videos Mike Rodgers watches (AI engineering, "
           "data-center buildout, agent tooling, YouTube growth). Extract tool/company "
           "mentions and pain quotes (M03 demand-mining second lens). "
           "Compact JSON array only: [{\"quote\":\"verbatim <=30 words\","
           "\"tool_or_company\":\"...\",\"pain\":\"<=25 words\","
           "\"source_hint\":\"video topic\"}]. Empty array if nothing. No preamble.")
else:
    SYS = ("You read transcripts of YouTube videos Mike Rodgers watches (AI engineering, "
           "data-center buildout, agent tooling, YouTube growth). Extract demand signals: "
           "problems people pay to solve, tools they beg for, gaps in the market. "
           "Compact JSON array only: [{\"quote\":\"verbatim <=30 words\","
           "\"theme\":\"...\",\"why_demand\":\"<=25 words\",\"source_hint\":\"video topic\"}]. "
           "Empty array if nothing. No preamble.")


def ask(prompt):
    body = json.dumps({"model": MODEL,
                       "messages": [{"role": "system", "content": SYS},
                                    {"role": "user", "content": prompt}],
                       "stream": False,
                       "options": {"num_predict": 900, "temperature": 0.2}}).encode()
    req = urllib.request.Request(OLLAMA + "/api/chat", data=body,
                                 headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=1200) as r:
        d = json.load(r)
    return (d.get("message", {}).get("content") or "")


def done_keys():
    s = set()
    if os.path.exists(OUT):
        for l in open(OUT):
            try:
                s.add(json.loads(l)["key"])
            except Exception:
                pass
    return s


def parse(txt):
    try:
        return json.loads(txt[txt.index("["):txt.rindex("]") + 1])
    except Exception:
        return [{"raw": txt[:600]}]


def wait_ready():
    for _ in range(32):
        if os.path.isdir(SRC) and os.listdir(SRC):
            return True
        time.sleep(15)
    print(f"{HOST}: transcripts never appeared; exiting without DONE", flush=True)
    return False


def main():
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    if not wait_ready():
        sys.exit(1)
    skip = done_keys()
    files = sorted(f for f in os.listdir(SRC) if f.endswith(".txt"))
    if not files:  # fall back to any non-dot file
        files = sorted(f for f in os.listdir(SRC) if not f.startswith("."))
    jobs = []
    for fn in files:
        p = os.path.join(SRC, fn)
        try:
            text = open(p, errors="replace").read()
        except OSError:
            continue
        if len(text) > 150000:
            text = text[:150000]
        for off in range(0, max(len(text), 1), CHUNK):
            seg = text[off:off + CHUNK]
            if len(seg.strip()) < 400:
                break
            key = f"{fn}:{off}"
            if key not in skip:
                jobs.append((key, fn, seg))
    print(f"m03digest {HOST}: {len(jobs)} chunks from {len(files)} files", flush=True)
    for i, (key, fn, seg) in enumerate(jobs):
        for attempt in (1, 2, 3):
            try:
                txt = ask(f"Video: {fn}\nTranscript chunk:\n{seg}")
                break
            except Exception as e:
                if attempt == 3:
                    txt = ""
                    with open(OUT, "a") as f:
                        f.write(json.dumps({"key": key, "error": str(e)[:200]}) + "\n")
                time.sleep(15 * attempt)
        if txt:
            with open(OUT, "a") as f:
                f.write(json.dumps({"key": key, "file": fn, "model": MODEL,
                                    "signals": parse(txt)}, ensure_ascii=False) + "\n")
        if (i + 1) % 10 == 0:
            print(f"m03digest {HOST} {i+1}/{len(jobs)}", flush=True)
    open(os.path.join(JAKE, f"out/m03-digest-{HOST}{'-' + LENS if LENS else ''}.DONE"), "w").write("complete\n")
    print("m03digest COMPLETE", flush=True)


if __name__ == "__main__":
    main()
