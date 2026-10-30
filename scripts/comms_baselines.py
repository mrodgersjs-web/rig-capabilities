#!/usr/bin/env python3
"""Comms corpus baselines (v13.2) — deterministic anti-median statistics from
the writing-craft corpus (data/corpora/writing-craft/manifest.jsonl + transcripts).

Emits data/comms/baselines.json: word-count / sentence-length medians per
speaker, which the polar cards use as the 'generic median' to deviate FROM
(rig-deviate / σ rungs). No LLM, no downloads — reads the local corpus only.
If the corpus is absent, refuses with DATA_GAP rather than inventing numbers.
"""
import json
import re
import statistics
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
CORPUS = REPO / "data" / "corpora" / "writing-craft"
OUT = REPO / "data" / "comms" / "baselines.json"


def sentences(text: str) -> list[int]:
    return [len(s.split()) for s in re.split(r"[.!?]+\s", text) if len(s.split()) > 1]


def main() -> int:
    manifest = CORPUS / "manifest.jsonl"
    if not manifest.exists():
        print(json.dumps({"status": "DATA_GAP", "missing": str(manifest)}))
        return 2
    per: dict[str, dict] = {}
    for line in manifest.read_text().splitlines():
        r = json.loads(line)
        slug = re.sub(r"[^a-z0-9]+", "-", r["channel"].lower()).strip("-")
        f = CORPUS / r["surface"] / slug / f"{r['video_id']}.txt"
        if not f.exists():
            continue
        text = f.read_text(errors="replace")
        sl = sentences(text)
        e = per.setdefault(r["surface"], {"n": 0, "sent_len": [], "words": []})
        e["n"] += 1
        e["words"].append(len(text.split()))
        e["sent_len"].extend(sl)
    if not per:
        print(json.dumps({"status": "DATA_GAP", "missing": "transcript files referenced by manifest"}))
        return 2
    med = lambda xs: round(statistics.median(xs), 1) if xs else None
    baseline = {
        "generated_from": f"{sum(v['n'] for v in per.values())} transcripts, "
                          "local corpus only (YouTube IP-blocked; refresh via scripts/scrape_writing_craft.py)",
        "surfaces": {sp: {"transcripts": v["n"], "median_words": med(v["words"]),
                          "median_sentence_words": med(v["sent_len"])} for sp, v in sorted(per.items())},
        "anti_median_rule": "a draft matching these medians IS the median — deviation ladder target: "
                            "sentence-length distribution must not peak at the corpus median for its surface",
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(baseline, indent=2))
    print(json.dumps({"written": str(OUT), "surfaces": len(per)}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
