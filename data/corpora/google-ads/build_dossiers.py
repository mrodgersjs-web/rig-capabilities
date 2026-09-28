#!/usr/bin/env python3
"""Cut per-stage evidence dossiers from the Google Ads transcript corpus (deterministic).

Each transcript is split into ~140-word windows. A window is scored for each stage by
counting that stage's term hits (word-boundary, case-insensitive). Per stage the top
windows are kept with diversity caps (max 3 windows per video, max 14 per channel)
until ~22k words. Output: dossiers/<stage>.md, each window headed with
[videoId | @handle | title] so every later claim can cite CLAIM(videoId).
No model, no network.
"""
import json
import re
from collections import defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
WIN, STEP, BUDGET = 140, 100, 22000

STAGES = {
    "ga-strategy": r"goal|objective|kpi|offer|who (?:is|it'?s) for|target (?:customer|audience|market)|budget|spend|plan|strategy|audit|measurement|track your|business model|unit economics|customer value|lifetime value|\bclv\b|lead value",
    "ga-structure": r"account structure|campaign structure|ad group|skag|single keyword|theme|themed|brand (?:campaign|search|terms)|segmentation|split(?:ting)? (?:campaigns|ad groups)|naming|organize|organise|hierarchy|match type|broad match|phrase match|exact match|keyword signals?",
    "ga-tracking": r"conversion track\w*|conversion action|google tag|gtag|tag manager|\bgtm\b|enhanced conversions?|call track\w*|phone (?:call|lead)|form (?:submission|fill|lead)|thank you page|google analytics|\bga4\b|offline conversion|import conversions?|consent mode|attribution|gclid|tracking template",
    "ga-keywords": r"keyword research|negative keyword|search terms? report|keyword planner|keyword ideas?|match types?|broad match|phrase match|exact match|keyword intent|search intent|query|long[- ]tail|competitor (?:keywords?|terms?)|brand terms?|keyword list|add keywords",
    "ga-campaigns": r"performance max|\bpmax\b|shopping (?:campaign|feed|ads?)|demand gen|display campaign|video campaign|youtube ads?|search campaign|smart campaign|local campaign|local services ads?|\blsa\b|asset group|audience signals?|campaign type|feed|merchant center|discovery campaign",
    "ga-bidding": r"bidding|bid strategy|smart bidding|maximize (?:clicks|conversions)|max conversions|target cpa|tcpa|target roas|troas|manual cpc|portfolio bid|bid adjustment|learning period|learning phase|automated bidding|bid simulator|seasonality adjustment|tCPA|tROAS",
    "ga-ads": r"responsive search ad|\brsa\b|headline|description|ad copy|pinning|pinned|ad strength|sitelink|callout|structured snippet|image asset|price (?:asset|extension)|promotion|ad extension|asset|ad policy|disapprov\w*|ad variations?|ad rotation",
    "ga-landing": r"landing page|message match|headline match|above the fold|call to action|\bcta\b|form fields?|conversion rate|\bcro\b|page speed|load(?:ing)? (?:time|speed)|mobile friendly|trust (?:signals?|elements?)|social proof|thank you|lead form|click to call",
    "ga-budget": r"daily budget|monthly budget|budget limited|limited by budget|budget allocation|scaling|scale(?:ing)? (?:up|budget)|shared budget|experiment|a/b test|split test|test(?:ing)? (?:budget|campaign)|roi|roas|cost per (?:lead|acquisition|conversion)|cpa|impression share|budget change",
    "ga-reporting": r"report(?:ing)?|dashboard|metrics?|analytic\w*|change history|optimi[sz]ation|search terms? report|weekly|monthly review|performance|conversion rate|cost per conversion|impressions?|clicks?|ctr|quality score|insights?|monitor\w*|audit",
    "ga-local-b2b": r"local (?:business|service|seo|ads?)|service area|small business|lead generation|lead gen|\bleads?\b|phone calls?|contractor|plumber|hvac|dentist|law firm|attorney|medical|home services|local intent|near me|radius|city|b2b|service business|quote|estimate|booking",
}
PATS = {k: re.compile(v, re.I) for k, v in STAGES.items()}


def windows(words):
    for i in range(0, max(1, len(words) - WIN + 1), STEP):
        yield i, " ".join(words[i:i + WIN])


def main():
    rows = [json.loads(l) for l in (HERE / "manifest.jsonl").open() if l.strip()]
    cand = defaultdict(list)
    for r in rows:
        body = (REPO / r["file"]).read_text(encoding="utf-8")
        words = body.split()
        for i, w in windows(words):
            for st, pat in PATS.items():
                hits = len(pat.findall(w))
                if hits >= 3:
                    cand[st].append((hits, r["video_id"], r["handle"], r["title"], i, w))
    out = HERE / "dossiers"
    out.mkdir(exist_ok=True)
    summary = {}
    for st, items in cand.items():
        items.sort(key=lambda x: -x[0])
        per_vid, per_ch, used, keep = defaultdict(int), defaultdict(int), 0, []
        for hits, vid, h, title, i, w in items:
            if per_vid[vid] >= 3 or per_ch[h] >= 14:
                continue
            if any(k[1] == vid and abs(k[4] - i) < WIN for k in keep):
                continue
            keep.append((hits, vid, h, title, i, w))
            per_vid[vid] += 1
            per_ch[h] += 1
            used += WIN
            if used >= BUDGET:
                break
        lines = [f"# Dossier: {st}", ""]
        for hits, vid, h, title, i, w in keep:
            lines += [f"## [{vid} | @{h} | {title}]", "", w, ""]
        (out / f"{st}.md").write_text("\n".join(lines), encoding="utf-8")
        summary[st] = {"windows": len(keep), "videos": len(per_vid), "channels": len(per_ch), "words": used}
    print(json.dumps(summary, indent=1))


if __name__ == "__main__":
    main()
