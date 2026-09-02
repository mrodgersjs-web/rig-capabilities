#!/usr/bin/env python3
"""Weekly capability scout: scrape a channel, verify its citations, queue the agent pass.

Two stages, deliberately apart.

  stage   Deterministic, no model, no writes outside the corpus dir. Scrapes the
          configured channels with scripts/scrape_channel_corpus.py, harvests every
          URL the creator mentions (or that appears in the captions), then VERIFIES
          each citation: arXiv ids against the arXiv API, GitHub repos against the
          GitHub API. Anything that does not resolve is written to `week.json` as a
          rejection, because the failure mode this pipeline exists to stop is a
          plausible-looking paper number or repo slug that resolves nowhere. One
          scout this week cited a repository that the arXiv abstract it came from
          does not mention and that 404s; that is what the verifier is for.
  report  Prints what the last stage found and what is still queued.

The agent pass (mining capabilities, proposing skill/harness drafts) is NOT in this
script. It needs a model, and a model that can also write into the catalog is one
cron job away from shipping an unverified asset. So the runner emits `brief.md` and
`queue.json`, and the model runs in a terminal whose output is a DRAFT that still has
to pass `rig-capabilities test` and Gate-D before anything is installed.

Usage:
    scripts/weekly_capability_scout.py stage [--week 2026-W36] [--since-days 9]
                                             [--skip-scrape] [--candidates FILE]
    scripts/weekly_capability_scout.py report
    scripts/weekly_capability_scout.py status

Exit codes: 0 stage clean; 1 stage ran with rejections (expected most weeks — a
rejection is a finding, not a crash); 2 stage could not run at all.
"""

from __future__ import annotations

import argparse
import datetime
import json
import re
import shutil
import subprocess
import sys
import urllib.request
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
SOURCES = REPO / "data" / "capability-scout-sources.json"
DEFAULT_OUT = REPO / ".context" / "capability-scout"
UA = "rig-capabilities/1.0 (capability scouting; citation verification)"
URL_RE = re.compile(r"https?://[^\s)\]>,\"'`]+\.[^\s)\]>,\"'`]+")
ARXIV_RE = re.compile(r"\b(\d{4}\.\d{4,5})\b")
REPO_RE = re.compile(r"github\.com/([A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+)")
NOT_A_REPO = (".git", ".md", ".py", ".yaml", ".yml", ".png", ".jpg", ".svg", ".ipynb")


class NoopRun:
    """Stand-in for a scrape subprocess when --skip-scrape re-verifies a corpus."""
    returncode, stdout, stderr = -1, "", "skip_scrape"


def week_key(day: datetime.date) -> str:
    y, w, _ = day.isocalendar()
    return f"{y}-W{w:02d}"


def load_sources(path: Path = SOURCES):
    doc = json.loads(path.read_text(encoding="utf-8"))
    return [s for s in doc.get("sources", []) if s.get("enabled")]


def fetch(url: str, timeout: int = 45) -> str:
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "*/*"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read().decode("utf-8", "replace")


def verify_arxiv(ids, fetcher=fetch):
    """Resolve ids in ONE batched arXiv API call: id -> {resolved, title|reason}.

    An id the API does not return is a rejection. The id pattern accepts http AND
    https in the <id> element: requiring http:// only silently resolves nothing if
    the API changes scheme, and an empty verified-set reads exactly like a week in
    which nothing was cited.
    """
    ids = sorted({str(i) for i in ids})
    if not ids:
        return {}
    try:
        body = fetcher("https://export.arxiv.org/api/query?id_list="
                       + ",".join(ids) + f"&max_results={max(50, len(ids))}")
    except Exception as e:
        return {i: {"resolved": False, "reason": f"api_unreachable:{type(e).__name__}"}
                for i in ids}
    found = {}
    for block in re.findall(r"<entry>(.*?)</entry>", body, re.S):
        m = re.search(r"<id>https?://arxiv\.org/abs/([\d.]+)v?\d*</id>", block)
        t = re.search(r"<title>(.*?)</title>", block, re.S)
        if m:
            found[m.group(1)] = {"resolved": True,
                                 "title": re.sub(r"\s+", " ", t.group(1)).strip() if t else ""}
    return {i: found.get(i, {"resolved": False, "reason": "not_returned_by_arxiv"})
            for i in ids}


def verify_repos(repos, runner=None):
    """Existence + stars + licence + last push per repo, from the GitHub API.

    Unknown is reported as unverified, never as absent: a missing `gh` binary is not
    evidence that a repository does not exist.
    """
    repos = sorted({r.rstrip("*.") for r in repos if r})
    if not repos:
        return {}
    if runner is None:
        if shutil.which("gh") is None:
            return {r: {"verified": False, "reason": "gh_unavailable"} for r in repos}
        runner = lambda a: subprocess.run(a, capture_output=True, text=True, timeout=90)
    out = {}
    for r in repos:
        p = runner(["gh", "api", f"repos/{r}", "--jq",
                    '[.full_name,.stargazers_count,(.license.spdx_id//"none"),'
                    '(.pushed_at//"")[0:10]]|@tsv'])
        if getattr(p, "returncode", 1) == 0 and p.stdout.strip():
            fn, stars, lic, pushed = p.stdout.strip().split("\t")
            out[r] = {"verified": True, "resolved": fn, "stars": int(stars),
                      "license": lic, "pushed": pushed}
        else:
            err = (getattr(p, "stderr", "") or "").strip().splitlines()
            out[r] = {"verified": False, "reason": "not_found",
                      "detail": (err[-1] if err else "")[:80]}
    return out


def harvest(corpus: Path):
    """Every URL, bare arXiv id, and org/repo slug in transcripts + descriptions."""
    urls, ids, repos = set(), set(), set()
    for sub in ("transcripts", "descriptions"):
        d = corpus / sub
        if not d.is_dir():
            continue
        for f in sorted(p for p in d.iterdir() if p.is_file()):
            text = f.read_text(encoding="utf-8", errors="replace")
            for u in URL_RE.findall(text):
                u = u.rstrip(".:;,")
                urls.add(u)
                m = REPO_RE.search(u)
                if m:
                    repos.add(m.group(1))
            ids.update(ARXIV_RE.findall(text))
    return (sorted(urls), sorted(i for i in ids if i[:2] in ("24", "25", "26")),
            {r for r in repos if not r.endswith(NOT_A_REPO)})


def read_candidates(path: Path):
    """Analyst-discovered citations that the creator never linked.

    A creator links one paper in the description and names three out loud without a
    URL. Candidate ids get the same machine check as a creator link; without this the
    agent pass would have to ignore paper ids it found itself, or cite them unverified.
    """
    if not path.exists():
        return [], [], {"path": str(path), "present": False}
    try:
        doc = json.loads(path.read_text(encoding="utf-8"))
    except Exception as e:
        return [], [], {"path": str(path), "present": True, "error": str(e)[:120]}
    ids = [str(i) for i in doc.get("arxiv", [])]
    repos = [str(r) for r in doc.get("repos", [])]
    return ids, repos, {"path": str(path), "present": True, "arxiv": len(ids),
                        "repos": len(repos)}


def brief(week, per_source, ok_ids, ok_gh) -> str:
    lines = [f"# Capability scout — {week}", "",
             "Deterministic stage complete. This is the agent-pass brief.", ""]
    for s in per_source:
        lines.append(f"- {s['slug']}: {s['transcribed']}/{s['targets']} transcribed, "
                     f"{s['total_words']} words, {s['urls']} URLs cited"
                     + (f", excluded: {s['excluded']}" if s.get("excluded") else ""))
    lines += ["", f"## Verified sources of record ({len(ok_ids)} papers, {len(ok_gh)} repos)",
              "Only these may be cited. Anything else is a rejection and must be reported",
              "as one, not smoothed into prose.", ""]
    lines += [f"- arXiv {i}" for i in ok_ids] + [f"- repo {r}" for r in ok_gh]
    lines += ["", "## Contract for the agent pass",
              "1. Per video: capability name, mechanism (inputs -> rule -> output), the",
              "   verbatim transcript quote, the paper id from the verified set, and the",
              "   OSS repo from the verified set or `none`.",
              "2. Map each capability to a real path under capabilities/, or NEW.",
              "3. Propose assets as DRAFTS. `rig-capabilities test` must run on each;",
              "   installation is a separate Gate-D action. Never install, publish, send,",
              "   or push from the agent pass.",
              "4. A quote that is not a verbatim substring of its transcript is a",
              "   fabrication: report it as one (afproof.log_fabrication).", ""]
    return "\n".join(lines)


def stage(week: str, since_days: int, out_root: Path = DEFAULT_OUT,
          skip_scrape: bool = False, candidates_path: str = "") -> dict:
    """The deterministic half for one ISO week. Writes only under out_root/week."""
    week_dir = out_root / week
    week_dir.mkdir(parents=True, exist_ok=True)
    try:
        sources = load_sources()
    except Exception as e:
        return {"verdict": "SOURCES_UNREADABLE", "detail": f"{SOURCES}: {e}"}
    if not sources:
        return {"verdict": "NO_SOURCES", "detail": f"no enabled source in {SOURCES}"}

    per_source, all_ids, all_repos, queue_videos = [], set(), set(), []
    for s in sources:
        cdir = week_dir / s["slug"]
        if skip_scrape:
            # Re-verify a corpus already on disk (retry after a mid-scrape failure, or a
            # citation re-check after a verifier change) without scraping again.
            # rc is -1 so week.json can never read as a fresh scrape.
            r, man = NoopRun(), {}
            if (cdir / "manifest.json").exists():
                man = json.loads((cdir / "manifest.json").read_text(encoding="utf-8"))
        else:
            r = subprocess.run(
                [sys.executable, str(REPO / "scripts" / "scrape_channel_corpus.py"),
                 "--channel", s["channel"], "--since-days", str(since_days),
                 "--out", str(cdir)],
                cwd=REPO, capture_output=True, text=True, timeout=3600)
            try:
                man = json.loads((cdir / "manifest.json").read_text(encoding="utf-8"))
            except Exception:
                man = {"videos": [], "targets": 0, "transcribed": 0,
                       "error": (r.stdout or r.stderr).strip()[-200:]}
        urls, ids, repos = harvest(cdir)
        all_ids.update(ids)
        all_repos.update(repos)
        for v in man.get("videos", []):
            if v.get("words"):
                queue_videos.append({"video": v.get("id"), "title": v.get("title"),
                                     "published": v.get("published"),
                                     "transcript": str(cdir / "transcripts"
                                                       / f"{v.get('id')}.txt")})
        per_source.append({"slug": s["slug"], "channel": s["channel"], "rc": r.returncode,
                           "targets": man.get("targets", 0),
                           "transcribed": man.get("transcribed", 0),
                           "total_words": man.get("total_words", 0),
                           "excluded": [f.get("error") for f in man.get("failed", [])],
                           "urls": len(urls)})

    extra_ids, extra_repos, cand = read_candidates(
        Path(candidates_path) if candidates_path else week_dir / "candidates.json")
    all_ids.update(extra_ids)
    all_repos.update(extra_repos)

    ax = verify_arxiv(all_ids)
    gh = verify_repos(all_repos)
    ok_ids = sorted(i for i, v in ax.items() if v.get("resolved"))
    bad_ids = {i: v for i, v in ax.items() if not v.get("resolved")}
    ok_gh = sorted(r for r, v in gh.items() if v.get("verified"))
    bad_gh = {r: v for r, v in gh.items() if not v.get("verified")}
    doc = {"schema": "capability-scout-week-v1", "week": week,
           "ran_utc": datetime.datetime.now(datetime.timezone.utc)
                      .isoformat(timespec="seconds"),
           "since_days": since_days, "scraped": not skip_scrape, "sources": per_source,
           "candidates": cand,
           "arxiv_verified": {i: ax[i] for i in ok_ids}, "arxiv_rejected": bad_ids,
           "repos_verified": {r: gh[r] for r in ok_gh}, "repos_rejected": bad_gh}
    (week_dir / "week.json").write_text(json.dumps(doc, indent=1) + "\n", encoding="utf-8")
    queue = {"week": week, "status": "QUEUED_FOR_AGENT_PASS", "videos": queue_videos,
             "rule": ("agent output is a DRAFT proposal; it may not install, publish, "
                      "send, or push, and every citation it emits must appear in "
                      "week.json's verified sets")}
    (week_dir / "queue.json").write_text(json.dumps(queue, indent=1) + "\n", encoding="utf-8")
    (week_dir / "brief.md").write_text(brief(week, per_source, ok_ids, ok_gh), encoding="utf-8")
    return {"verdict": "OK", "week": week, "dir": str(week_dir),
            "videos_queued": len(queue_videos), "candidates": cand,
            "arxiv": f"{len(ok_ids)} verified / {len(bad_ids)} rejected",
            "repos": f"{len(ok_gh)} verified / {len(bad_gh)} rejected"}


def latest_week(out_root: Path = DEFAULT_OUT):
    runs = sorted(d for d in out_root.glob("*/week.json")) if out_root.is_dir() else []
    return runs[-1].parent if runs else None


def report(out_root: Path = DEFAULT_OUT) -> int:
    wd = latest_week(out_root)
    if not wd:
        print(json.dumps({"verdict": "NO_RUNS", "detail": str(out_root)}))
        return 2
    doc = json.loads((wd / "week.json").read_text(encoding="utf-8"))
    q = json.loads((wd / "queue.json").read_text(encoding="utf-8")) \
        if (wd / "queue.json").exists() else {}
    print(json.dumps({"week": doc["week"], "ran_utc": doc["ran_utc"],
                      "scraped": doc.get("scraped"), "sources": doc["sources"],
                      "candidates": doc.get("candidates"),
                      "videos_queued": len(q.get("videos", [])),
                      "arxiv_verified": len(doc["arxiv_verified"]),
                      "arxiv_rejected": sorted(doc["arxiv_rejected"]),
                      "repos_verified": len(doc["repos_verified"]),
                      "repos_rejected": sorted(doc["repos_rejected"]),
                      "brief": str(wd / "brief.md")}, indent=1))
    return 0


def status(out_root: Path = DEFAULT_OUT) -> int:
    wd = latest_week(out_root)
    try:
        enabled = [s["slug"] for s in load_sources()]
    except Exception as e:
        enabled = [f"sources_unreadable: {e}"]
    print(json.dumps({"latest_week": wd.name if wd else None,
                      "sources_file": str(SOURCES), "enabled_sources": enabled,
                      "installs_performed_by_this_script": 0,
                      "writes_only_under": str(DEFAULT_OUT)}, indent=1))
    return 0


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("cmd", choices=("stage", "report", "status"))
    ap.add_argument("--week", default="", help="ISO week key, e.g. 2026-W36")
    ap.add_argument("--since-days", type=int, default=9)
    ap.add_argument("--out", default=str(DEFAULT_OUT))
    ap.add_argument("--skip-scrape", action="store_true",
                    help="re-verify the corpus already in the week dir; no scrape")
    ap.add_argument("--candidates", default="",
                    help="JSON {arxiv:[ids],repos:[org/repo]} to verify alongside "
                         "creator-linked citations (default <week>/candidates.json)")
    a = ap.parse_args(argv)
    out_root = Path(a.out)
    if a.cmd == "stage":
        res = stage(a.week or week_key(datetime.date.today()), a.since_days, out_root,
                    skip_scrape=a.skip_scrape, candidates_path=a.candidates)
        print(json.dumps(res, indent=1))
        if res.get("verdict") == "OK":
            return 0
        return 2 if res.get("verdict") in ("NO_SOURCES", "SOURCES_UNREADABLE") else 1
    if a.cmd == "report":
        return report(out_root)
    return status(out_root)


if __name__ == "__main__":
    sys.exit(main())
