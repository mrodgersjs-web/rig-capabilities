#!/usr/bin/env python3
"""E-stage (run once, from the local Mac): copy every corpus the fleet workers
need onto the hosts that will process it. RIG/Mike-owned media only — Jacob and
personal lanes are never moved off this Mac.

Writes staging manifest to fleet/out/staging-manifest.json.
"""
import hashlib, json, os, shutil, subprocess, sys
from datetime import datetime, timezone

FLEET = os.path.expanduser("~/.rig/jake/fleet")
MEDIA_LOCAL = os.path.join(FLEET, "work/media")
HOSTS = ["rig256gb", "rig96gb", "rig36gb", "blackwell"]
SSH = ["ssh", "-o", "BatchMode=yes", "-o", "ConnectTimeout=8"]

# RIG-owned video sources (channel/site/campaign assets). Jacob/NeoMatrix/anniv excluded.
MEDIA_DIRS = [
    os.path.expanduser("~/rigintelligence-repos/rig-site-assets/reels"),
    os.path.expanduser("~/Desktop/Projects/rig-dso-demo/film/higgsfield/video"),
    os.path.expanduser("~/Desktop/Projects/RIG-Site-Assets"),
    os.path.expanduser("~/Desktop/Projects/project-make-money/06-site"),
    os.path.expanduser("~/Developer/OpenMontage/assets"),
    os.path.expanduser("~/Media"),
    os.path.expanduser("~/.rig/repos/open-compute/share/videos"),
    os.path.expanduser("~/.rig/repos/editable-design/assets"),
]
MEDIA_EXCLUDE_SUB = ("NeoMatrix", "Jacob", "anniv", "Archive")

TRANSCRIPTS = os.path.expanduser("~/.jake/youtube-howto/transcripts")
JAKESTUDIO = os.path.expanduser("~/Documents/JakeStudio")
SAVEDJD = os.path.expanduser("~/.applypilot/imports/saved-jd")
JOBSJSONL = os.path.join(FLEET, "work/discovered-jobs.jsonl")

man = {"at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"), "media": [], "transcripts": 0}


def collect_media():
    os.makedirs(MEDIA_LOCAL, exist_ok=True)
    seen = {}
    n = 0
    for d in MEDIA_DIRS:
        if not os.path.isdir(d):
            continue
        for dp, _, fns in os.walk(d):
            if any(x in dp for x in MEDIA_EXCLUDE_SUB):
                continue
            for fn in fns:
                if not fn.endswith(".mp4"):
                    continue
                p = os.path.join(dp, fn)
                try:
                    sz = os.path.getsize(p)
                except OSError:
                    continue
                if sz < 4096 or sz > 400 * 1024 * 1024:
                    continue
                # unique flat name: parent dir + file
                key = os.path.basename(dp) + "__" + fn
                key = key.replace(" ", "_")
                if key in seen:
                    h = hashlib.sha1(p.encode()).hexdigest()[:6]
                    key = os.path.basename(dp) + "__" + h + "__" + fn
                    key = key.replace(" ", "_")
                seen[key] = p
                dst = os.path.join(MEDIA_LOCAL, key)
                if not os.path.exists(dst):
                    shutil.copy2(p, dst)
                man["media"].append({"name": key, "bytes": sz, "src": p})
                n += 1
    print(f"media staged locally: {n} files", flush=True)


def rsync(src, host, dst):
    rc = subprocess.call(["rsync", "-a", "-e", "ssh -o BatchMode=yes -o ConnectTimeout=8",
                          src.rstrip("/") + "/", f"{host}:{dst.rstrip('/')}/"])
    if rc != 0:
        print(f"  rsync FAILED {src} -> {host}:{dst} rc={rc}", flush=True)
    return rc == 0


def main():
    collect_media()
    # transcripts split: first half -> rig36gb, second half -> rig96gb
    tfiles = sorted(f for f in os.listdir(TRANSCRIPTS) if not f.startswith("."))
    half = (len(tfiles) + 1) // 2
    os.makedirs(os.path.join(FLEET, "work/t36"), exist_ok=True)
    os.makedirs(os.path.join(FLEET, "work/t96"), exist_ok=True)
    for i, f in enumerate(tfiles):
        src = os.path.join(TRANSCRIPTS, f)
        dst = os.path.join(FLEET, "work/t36" if i < half else "work/t96", f)
        if not os.path.exists(dst):
            shutil.copy2(src, dst)
    man["transcripts"] = len(tfiles)
    print(f"transcripts split: {half} -> rig36gb, {len(tfiles) - half} -> rig96gb", flush=True)

    for h in HOSTS:
        subprocess.call(["ssh", "-o", "BatchMode=yes", h,
                         "mkdir -p ~/.rig/jake/fleet/work ~/.rig/jake/fleet/logs ~/.rig/jake/fleet/out"])
    jobs = []
    # media -> every host (each host owns distinct ladder rungs)
    for h in HOSTS:
        jobs.append(("media", h, MEDIA_LOCAL, "~/.rig/jake/fleet/work/media"))
    # jd corpus -> rig256gb
    jobs.append(("savedjd", "rig256gb", SAVEDJD, "~/.rig/jake/fleet/work/saved-jd", None))
    # transcripts
    jobs.append(("t36", "rig36gb", os.path.join(FLEET, "work/t36"),
                 "~/.rig/jake/fleet/work/transcripts"))
    jobs.append(("t96", "rig96gb", os.path.join(FLEET, "work/t96"),
                 "~/.rig/jake/fleet/work/transcripts"))
    # embed corpus -> rig36gb: memory pages (JakeStudio md) + transcripts + saved jd
    jobs.append(("corpus-jakestudio", "rig36gb", JAKESTUDIO,
                 "~/.rig/jake/fleet/work/corpus/jakestudio",
                 ["--include=*/", "--include=*.md", "--include=*.txt", "--exclude=*"]))
    jobs.append(("corpus-transcripts", "rig36gb",
                 os.path.join(FLEET, "work/t36"),
                 "~/.rig/jake/fleet/work/corpus/transcripts"))
    jobs.append(("corpus-savedjd", "rig36gb", SAVEDJD,
                 "~/.rig/jake/fleet/work/corpus/saved-jd"))

    for job in jobs:
        tag, host, src = job[0], job[1], job[2]
        dst = job[3]
        extra = job[4] if len(job) > 4 else None
        cmd = ["rsync", "-a", "-e", "ssh -o BatchMode=yes -o ConnectTimeout=8"]
        if extra:
            cmd += extra
        cmd += [src.rstrip("/") + "/", f"{host}:{dst.rstrip('/')}/"]
        print(f"staging {tag} -> {host} ...", flush=True)
        rc = subprocess.call(cmd)
        man.setdefault("rsync", []).append({"tag": tag, "host": host, "rc": rc})
    # single file: discovered jobs export -> rig256gb
    rc = subprocess.call(["scp", "-q", "-o", "BatchMode=yes", JOBSJSONL,
                          "rig256gb:~/.rig/jake/fleet/work/discovered-jobs.jsonl"])
    man.setdefault("rsync", []).append({"tag": "jobs-jsonl", "host": "rig256gb", "rc": rc})
    print("staging done", flush=True)
    json.dump(man, open(os.path.join(FLEET, "out/staging-manifest.json"), "w"), indent=1)


if __name__ == "__main__":
    main()
