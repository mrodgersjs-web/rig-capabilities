#!/usr/bin/env python3
"""E-embed: chunk Mike's corpora and embed them with local nomic-embed-text into
a sqlite vector index under ~/.rig/jake/fleet/out/index/. Stdlib only.
Corpus root: ~/.rig/jake/fleet/work/corpus/ (staged). Grows the index on disk;
manifest.json updated every 50 chunks; DONE flag when the walk finishes.
"""
import hashlib, json, os, re, sqlite3, time, urllib.request

JAKE = os.path.expanduser("~/.rig/jake/fleet")
CORPUS = os.path.join(JAKE, "work/corpus")
IDX = os.path.join(JAKE, "out/index/index.sqlite3")
MANIFEST = os.path.join(JAKE, "out/index/manifest.json")
OLLAMA = os.environ.get("E_OLLAMA", "http://127.0.0.1:11434")
MODEL = os.environ.get("E_EMBED_MODEL", "nomic-embed-text")
CHUNK, OVERLAP, BATCH = 1400, 200, 16


def md_files(root):
    for dp, _, fns in os.walk(root):
        for fn in fns:
            if fn.endswith((".md", ".txt")):
                p = os.path.join(dp, fn)
                try:
                    if os.path.getsize(p) < 40 * 1024 * 1024:
                        yield p
                except OSError:
                    pass


def chunks(text):
    text = re.sub(r"\n{3,}", "\n\n", text)
    out, i = [], 0
    while i < len(text):
        out.append(text[i:i + CHUNK])
        i += CHUNK - OVERLAP
    return out


def embed(batch):
    body = json.dumps({"model": MODEL, "input": batch}).encode()
    req = urllib.request.Request(OLLAMA + "/api/embed", data=body,
                                 headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=600) as r:
        return json.load(r)["embeddings"]


def wait_ready():
    for _ in range(32):
        if os.path.isdir(CORPUS) and any(md_files(CORPUS)):
            return True
        time.sleep(15)
    print("embed: corpus never appeared; exiting without DONE", flush=True)
    return False


def main():
    os.makedirs(os.path.dirname(IDX), exist_ok=True)
    if not wait_ready():
        sys.exit(1)
    con = sqlite3.connect(IDX)
    con.execute("create table if not exists chunks (id integer primary key, "
                "src text, off integer, sha text, text text, embedding blob)")
    con.execute("create index if not exists idx_src on chunks(src)")
    con.commit()
    have = {r[0] for r in con.execute("select distinct src from chunks")}
    stats = {"files_seen": 0, "files_skipped": 0, "chunks": 0, "errors": 0, "started": time.time()}
    pending = []
    for path in md_files(CORPUS):
        rel = os.path.relpath(path, CORPUS)
        if rel in have:
            stats["files_skipped"] += 1
            continue
        try:
            text = open(path, errors="replace").read()
        except OSError:
            stats["errors"] += 1
            continue
        stats["files_seen"] += 1
        for off, ch in enumerate(chunks(text)):
            pending.append((rel, off, hashlib.sha256(ch.encode()).hexdigest(), ch))
        if len(pending) >= BATCH * 4:
            flush(con, pending, stats)
            pending = []
    if pending:
        flush(con, pending, stats)
    con.close()
    json.dump(stats, open(MANIFEST, "w"), indent=1)
    open(os.path.join(JAKE, "out/index/DONE"), "w").write("complete\n")
    print("embed COMPLETE", stats, flush=True)


def flush(con, pending, stats):
    for i in range(0, len(pending), BATCH):
        batch = pending[i:i + BATCH]
        try:
            vecs = embed([b[3] for b in batch])
        except Exception as e:
            stats["errors"] += len(batch)
            print(f"embed error: {e}", flush=True)
            time.sleep(5)
            continue
        for (rel, off, sha, text), v in zip(batch, vecs):
            con.execute("insert into chunks (src, off, sha, text, embedding) values (?,?,?,?,?)",
                        (rel, off, sha, text, json.dumps(v)))
        con.commit()
        stats["chunks"] += len(batch)
        if stats["chunks"] % 500 < BATCH:
            stats["elapsed_s"] = int(time.time() - stats["started"])
            json.dump(stats, open(MANIFEST, "w"), indent=1)
            print(f"embed {stats['chunks']} chunks from {stats['files_seen']} files", flush=True)


if __name__ == "__main__":
    main()
