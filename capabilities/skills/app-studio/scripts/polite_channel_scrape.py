#!/usr/bin/env python3
"""One polite, bounded batch of the App Studio creator-channel transcript scrape.

Built after the first pass (2026-09-28): five parallel lanes got this IP answered with
HTTP 429 plus "Sign in to confirm you're not a bot" within minutes, which also blocked
Aside's built-in YouTube tool from this IP. So each run here is one small batch, designed
to be started every few hours by a routine:

  * single instance: refuses to start while another batch holds a fresh lock;
  * one request at a time, 15-30 s apart, build-style videos first, round-robin by channel;
  * stops at the FIRST throttle signal (a throttle is never recorded as "no captions");
  * never uses cookies or signs in; members-only videos are recorded, never circumvented;
  * after the batch: re-derives manifests from raw captions (no network), then regenerates
    the metadata-only registries and the deterministic channel cards.

Raw captions and transcripts stay in the gitignored corpus dir (the creators' words).
Usage:
  polite_channel_scrape.py [--corpus DIR] [--channels JSON] [--ytdlp PATH]
                           [--max-videos 40] [--sleep 15:30] [--dry-run]
Exit: 0 batch ran or nothing to do (including ALREADY_RUNNING / THROTTLED); 2 setup error.
"""
import argparse, datetime, json, os, random, re, subprocess, sys, time
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[3]
sys.path.insert(0, str(REPO / "scripts"))
import scrape_channel_corpus as S  # noqa: E402

THROTTLE = re.compile(r"(?i)(429|too many requests|not a bot|sign in to confirm|captcha)")
BUILD = re.compile(r"(?i)\b(build|clone|full[- ]?stack|project|course|tutorial|app|saas|deploy|"
                   r"next\.?js|react native|expo|mern|dashboard|platform|ai)\b")
LOCK_FRESH_S = 30 * 60


def now():
    return datetime.datetime.now().isoformat(timespec="seconds")


def alive(pid: int) -> bool:
    try:
        os.kill(pid, 0)
        return True
    except ProcessLookupError:
        return False
    except PermissionError:          # exists, but this sandbox may not signal it
        return True


def write_json(path: Path, doc):
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(doc, indent=1) + "\n", encoding="utf-8")
    tmp.replace(path)


def missing_rows(corpus: Path, slug: str, nocaps: set):
    man = corpus / slug / "manifest.json"
    if not man.exists():
        return []
    rows = json.loads(man.read_text(encoding="utf-8")).get("videos", [])
    out = [r for r in rows if r["id"] not in nocaps
           and "members_only" not in str(r.get("error") or "")
           and S.pick_caption(corpus / slug / "raw", r["id"]) is None]
    out.sort(key=lambda r: (0 if BUILD.search(r.get("title") or "") else 1, -(r.get("duration") or 0)))
    return out


def fetch(ytdlp: str, row: dict, raw: Path):
    argv = [ytdlp, "--skip-download", "--write-auto-subs", "--sub-langs", "en,en-.*,orig-.*",
            "--sub-format", "vtt", "--write-info-json", "--no-write-playlist-metafiles", "--no-part",
            "-o", str(raw / row["id"]) + "%(ext)s", row["url"]]
    r = subprocess.run(argv, capture_output=True, text=True, timeout=420)
    return r.stderr or ""


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--corpus", default=str(REPO / ".context/app-creators"))
    ap.add_argument("--channels", default=str(HERE.parent / "references/creator-channels.json"))
    ap.add_argument("--ytdlp")
    ap.add_argument("--max-videos", type=int, default=40)
    ap.add_argument("--sleep", default="15:30", help="min:max seconds between requests")
    ap.add_argument("--dry-run", action="store_true", help="print the queue, no network, no writes")
    ap.add_argument("--registry-out", default=str(REPO / "data/corpora/how-to/build-craft"),
                    help="where build_creator_registry.py writes (tests must point this elsewhere)")
    a = ap.parse_args()
    corpus = Path(a.corpus)
    channels = json.loads(Path(a.channels).read_text())["channels"]
    ytdlp = a.ytdlp or str(corpus / "ytdlp")
    lo, hi = (float(x) for x in a.sleep.split(":"))
    if a.max_videos < 1 or a.max_videos > 60:
        print(json.dumps({"verdict": "BAD_ARGS", "detail": "--max-videos must be 1..60"}))
        return 2
    if not a.dry_run and not os.access(ytdlp, os.X_OK):
        print(json.dumps({"verdict": "NO_YTDLP", "detail": ytdlp}))
        return 2
    nocaps_path = corpus / "no_captions.json"
    nocaps = json.loads(nocaps_path.read_text()) if nocaps_path.exists() else {}
    queues = {s: missing_rows(corpus, s, set(nocaps.get(s, []))) for s in channels}
    if a.dry_run:
        print(json.dumps({"verdict": "DRY_RUN", "missing": {s: len(q) for s, q in queues.items()},
                          "next": [f"{s}:{q[0]['id']}" for s, q in queues.items() if q][:10]}))
        return 0
    lock = corpus / ".scrape.lock"
    if lock.exists():
        try:
            L = json.loads(lock.read_text())
            fresh = time.time() - float(L.get("heartbeat", 0)) < LOCK_FRESH_S
            if fresh and alive(int(L.get("pid", 0))):
                print(json.dumps({"verdict": "ALREADY_RUNNING", "pid": L.get("pid"), "since": L.get("started")}))
                return 0
        except (ValueError, OSError):
            pass
    lockdoc = {"pid": os.getpid(), "started": now(), "heartbeat": time.time()}
    write_json(lock, lockdoc)
    status = {"mode": "batch", "started": now(), "state": "fetching", "fetched": 0, "no_captions": 0,
              "members_only": 0, "throttled": False, "max_videos": a.max_videos, "channels": {}}
    status_path = corpus / "status.json"
    touched, done, stop = set(), 0, False
    try:
        while done < a.max_videos and not stop and any(queues.values()):
            for slug in channels:
                if done >= a.max_videos or stop or (corpus / "PAUSE").exists():
                    stop = stop or (corpus / "PAUSE").exists()
                    break
                if not queues[slug]:
                    continue
                row = queues[slug].pop(0)
                raw = corpus / slug / "raw"
                raw.mkdir(parents=True, exist_ok=True)
                err = fetch(ytdlp, row, raw)
                done += 1
                if S.pick_caption(raw, row["id"]) is not None:
                    status["fetched"] += 1
                    touched.add(slug)
                elif THROTTLE.search(err):
                    status["throttled"] = True
                    status["throttle_detail"] = (err.strip().splitlines() or [""])[-1][:200]
                    stop = True
                    break
                elif "members" in err or "membership" in err:
                    status["members_only"] += 1
                else:
                    status["no_captions"] += 1
                    nocaps.setdefault(slug, []).append(row["id"])
                    write_json(nocaps_path, nocaps)
                lockdoc["heartbeat"] = time.time()
                write_json(lock, lockdoc)
                status["updated"] = now()
                write_json(status_path, status)
                if done < a.max_videos and not stop:
                    time.sleep(random.uniform(lo, hi))
        status["state"] = "paused" if (corpus / "PAUSE").exists() else ("throttled" if status["throttled"] else "batch_done")
        regen_errors = []

        def regen(step, argv, timeout):
            r = subprocess.run(argv, capture_output=True, text=True, timeout=timeout)
            ok = r.returncode == 0 or (step == "rederive" and r.returncode == 1)  # 1 = some videos still lack captions
            if not ok:
                regen_errors.append({"step": step, "rc": r.returncode,
                                     "tail": ((r.stderr or r.stdout).strip().splitlines() or [""])[-1][:200]})

        for slug in sorted(touched):
            regen("rederive", [sys.executable, str(REPO / "scripts/scrape_channel_corpus.py"), "--channel", channels[slug],
                               "--since-days", "100000", "--out", str(corpus / slug), "--from-raw", "--yt-dlp", ytdlp], 900)
            regen("card", [sys.executable, str(HERE / "mine_creator_corpus.py"), str(corpus / slug)], 900)
        if touched:
            regen("registry", [sys.executable, str(HERE / "build_creator_registry.py"), "--corpus", str(corpus),
                               "--out", a.registry_out], 300)
        status["regen_errors"] = regen_errors
        for slug in channels:
            man = corpus / slug / "manifest.json"
            vids = json.loads(man.read_text()).get("videos", []) if man.exists() else []
            status["channels"][slug] = {"targets": len(vids), "transcribed": sum(1 for v in vids if v.get("words")),
                                        "missing": len(missing_rows(corpus, slug, set(nocaps.get(slug, []))))}
        status["totals"] = {k: sum(c[k] for c in status["channels"].values()) for k in ("targets", "transcribed", "missing")}
        status["finished"] = now()
        write_json(status_path, status)
    finally:
        try:
            if json.loads(lock.read_text()).get("pid") == os.getpid():
                lock.unlink()
        except (OSError, ValueError):
            pass
    print(json.dumps({"verdict": status["state"].upper(), "requests": done, "fetched": status["fetched"],
                      "regen_errors": len(status.get("regen_errors", [])),
                      "no_captions": status["no_captions"], "throttled": status["throttled"],
                      "totals": status.get("totals")}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
