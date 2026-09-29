#!/usr/bin/env python3
"""Deterministic first pass over an app-creator YouTube corpus (CODE before any model).

Reads a channel corpus written by scripts/scrape_channel_corpus.py
(<corpus>/manifest.json, transcripts/<id>.txt, descriptions/<id>.md) and writes a compact
"channel card" JSON that a model can read in one pass instead of millions of words:

  stats        targets, transcribed, words, date range, build-video share
  stack        per technology: videos mentioning it, share, first/last year seen
  build_order  per stage category: how often it appears as a chapter or first mention,
               and its median relative position inside build videos
  chapters     chapter titles of the longest build videos (the creator's own outline)
  gotchas      marker-scored transcript windows (error / fix / make sure / deprecated ...),
               at most 3 per video, each with video id, title and relative position
  top_videos   longest transcribed build videos (id, title, minutes, words, url)

The card quotes transcript text, so it stays next to the gitignored corpus
(default <corpus>/../_cards/<slug>.json). Committed skills cite ids and short quotes only.

Usage: mine_creator_corpus.py <corpus_dir> [--out card.json] [--windows 40]
Exit 0 with a card; exit 2 if the corpus has no transcripts (never an empty card).
"""
import argparse, collections, json, re, statistics, sys
from pathlib import Path

TECH = {
    "nextjs": r"next\.?\s?js|nextjs", "react": r"\breact\b(?!\s+native)", "react-native": r"react\s+native",
    "expo": r"\bexpo\b", "tailwind": r"tailwind", "shadcn": r"shad\s?cn|shadcn", "typescript": r"typescript",
    "clerk": r"\bclerk\b", "nextauth": r"next\s?auth|auth\.?\s?js", "better-auth": r"better\s?auth",
    "supabase": r"supa\s?base|super\s?base", "firebase": r"fire\s?base", "convex": r"\bconvex\b",
    "appwrite": r"app\s?write", "prisma": r"\bprisma\b", "drizzle": r"drizzle", "mongodb": r"mongo\s?db|mongoose",
    "postgres": r"postgres|postgresql", "neon": r"\bneon\b", "redis": r"\bredis\b|upstash",
    "stripe": r"\bstripe\b", "polar": r"\bpolar\b", "lemonsqueezy": r"lemon\s?squeezy",
    "openai": r"open\s?ai|chat\s?gpt|gpt-?4", "gemini": r"gemini", "anthropic": r"anthropic|\bclaude\b",
    "ai-sdk": r"\bai\s?sdk\b|vercel ai", "langchain": r"lang\s?chain|lang\s?graph", "pinecone": r"pinecone",
    "inngest": r"inngest|in\s?gest", "trigger-dev": r"trigger\.?\s?dev", "sentry": r"\bsentry\b",
    "vercel": r"vercel", "netlify": r"netlify", "render": r"\brender\.com|deploy (?:it )?(?:on|to) render",
    "railway": r"railway", "aws": r"\baws\b|amazon web services|\bs3\b", "docker": r"docker",
    "socketio": r"socket\.?\s?io", "liveblocks": r"live\s?blocks", "getstream": r"get\s?stream|stream (?:video|chat) sdk",
    "livekit": r"live\s?kit", "zustand": r"zustand", "redux": r"redux", "tanstack-query": r"tan\s?stack|react query",
    "trpc": r"\btrpc\b|t rpc", "hono": r"\bhono\b", "express": r"express(?:\.js| js|js)?\b", "nestjs": r"nest\s?js",
    "graphql": r"graph\s?ql", "sanity": r"\bsanity\b", "strapi": r"strapi", "cloudinary": r"cloudinary",
    "uploadthing": r"upload\s?thing", "resend": r"\bresend\b", "zod": r"\bzod\b",
    "react-hook-form": r"react hook form", "framer-motion": r"framer motion|\bmotion\.dev", "gsap": r"\bgsap\b",
    "threejs": r"three\.?\s?js|react three fiber", "nativewind": r"native\s?wind", "expo-router": r"expo router",
    "eas": r"\beas\b (?:build|submit|update)", "revenuecat": r"revenue\s?cat", "jest": r"\bjest\b",
    "vitest": r"vitest", "playwright": r"playwright", "cypress": r"cypress", "bun": r"\bbun\b",
    "vite": r"\bvite\b", "arcjet": r"arc\s?jet", "kinde": r"\bkinde\b", "turso": r"\bturso\b",
    "mux": r"\bmux\b", "twilio": r"twilio", "flutter": r"flutter", "django": r"django", "fastapi": r"fast\s?api",
}
CATEGORY = {
    "setup": r"setup|set up|install|init|getting started|project structure|folder structure|boilerplate",
    "ui": r"\bui\b|layout|navbar|sidebar|hero|landing|design|component|styling|tailwind|shadcn|theme|responsive",
    "auth": r"auth|sign ?in|sign ?up|login|clerk|session|middleware|protected",
    "data": r"database|schema|model|prisma|drizzle|mongo|postgres|supabase|convex|firebase|appwrite|crud|seed",
    "api": r"\bapi\b|route handler|server action|endpoint|backend|trpc|express|webhook",
    "ai": r"\bai\b|openai|gemini|gpt|claude|llm|prompt|agent|embedding|rag|chatbot",
    "payments": r"stripe|payment|checkout|subscription|billing|polar|pricing",
    "realtime": r"real ?time|socket|live ?blocks|websocket|notification|chat",
    "media": r"upload|image|video|cloudinary|uploadthing|storage|file",
    "testing": r"\btest|jest|vitest|playwright|cypress|debug",
    "deploy": r"deploy|vercel|netlify|production|hosting|domain|eas build|app store|play store|build and deploy",
}
MARKER = re.compile(r"\b(error|errors|bug|bugs|issue|issues|problem|doesn't work|does not work|not working|broke|"
                    r"breaks|fix|fixed|fixing|make sure|don't forget|do not forget|important|careful|gotcha|"
                    r"warning|deprecated|hydration|cors|rate limit|environment variables?|env (?:file|variables?)|"
                    r"type ?error|build failed|failed|crash|crashes|timeout|undefined|mismatch|caching|cache)\b", re.I)
STRONG = re.compile(r"(?i)\b(error|bug|doesn't work|does not work|not working|broke|breaks|fix|fixed|make sure|"
                    r"don't forget|do not forget|careful|gotcha|deprecated|hydration|cors|build failed|crash|mismatch)\b")
BUILD_TITLE = re.compile(r"(?i)\b(build|clone|full[- ]?stack|project|course|tutorial|app|saas|deploy|mern|dashboard|platform)\b")
TECH_RX = {k: re.compile(v, re.I) for k, v in TECH.items()}
CAT_RX = {k: re.compile(v, re.I) for k, v in CATEGORY.items()}


def load(corpus: Path):
    man = json.loads((corpus / "manifest.json").read_text(encoding="utf-8"))
    vids = []
    for v in man.get("videos", []):
        t = corpus / "transcripts" / f"{v['id']}.txt"
        if not v.get("words") or not t.exists():
            continue
        d = corpus / "descriptions" / f"{v['id']}.md"
        vids.append({**v, "text": t.read_text(encoding="utf-8", errors="replace"),
                     "desc": d.read_text(encoding="utf-8", errors="replace") if d.exists() else ""})
    return man, vids


def windows(words, title, vid, k=3, half=30):
    hits = [i for i, w in enumerate(words) if MARKER.match(w.lower().strip(".,!?;:\"'()"))]
    scored, used = [], set()
    for i in hits:
        if any(abs(i - u) < half * 2 for u in used):
            continue
        seg = words[max(0, i - half): i + half]
        s = " ".join(seg)
        pos = i / max(1, len(words))
        strong = len(set(m.group(0).lower() for m in STRONG.finditer(s)))
        weak = len(set(m.group(0).lower() for m in MARKER.finditer(s))) - strong
        tech = sum(1 for r in TECH_RX.values() if r.search(s))
        score = 2 * strong + weak + 0.5 * min(tech, 4) - (3 if pos < 0.03 else 0)
        if strong == 0:
            continue
        scored.append((round(score, 1), i, s))
        used.add(i)
    scored.sort(key=lambda x: -x[0])
    return [{"video": vid, "title": title[:80], "pos": round(i / max(1, len(words)), 2), "score": sc, "text": s}
            for sc, i, s in scored[:k]]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("corpus")
    ap.add_argument("--out")
    ap.add_argument("--windows", type=int, default=40)
    a = ap.parse_args()
    corpus = Path(a.corpus).resolve()
    man, vids = load(corpus)
    if not vids:
        print(json.dumps({"verdict": "NO_TRANSCRIPTS", "corpus": str(corpus)}))
        return 2
    years = [int(v["published"][:4]) for v in vids if v.get("published")]
    build = [v for v in vids if BUILD_TITLE.search(v.get("title", ""))]
    stack = {}
    for k, rx in TECH_RX.items():
        hit = [v for v in vids if rx.search(v["title"]) or rx.search(v["desc"]) or rx.search(v["text"])]
        if hit:
            ys = [int(v["published"][:4]) for v in hit if v.get("published")]
            stack[k] = {"videos": len(hit), "share": round(len(hit) / len(vids), 3),
                        "first_year": min(ys) if ys else None, "last_year": max(ys) if ys else None}
    order = collections.defaultdict(list)
    chapters_out = []
    for v in sorted(build, key=lambda v: -(v.get("words") or 0)):
        chs = [c.get("title") or "" for c in (v.get("chapters") or [])]
        if chs:
            for j, c in enumerate(chs):
                for cat, rx in CAT_RX.items():
                    if rx.search(c):
                        order[cat].append(j / max(1, len(chs) - 1))
            if len(chapters_out) < 8:
                chapters_out.append({"video": v["id"], "title": v["title"][:80], "chapters": [c[:60] for c in chs[:40]]})
        else:
            low = v["text"].lower()
            for cat, rx in CAT_RX.items():
                m = rx.search(low)
                if m:
                    order[cat].append(m.start() / max(1, len(low)))
    build_order = sorted(({"stage": c, "seen_in": len(p), "median_pos": round(statistics.median(p), 2)}
                          for c, p in order.items()), key=lambda r: r["median_pos"])
    wins = []
    for v in vids:
        wins += windows(v["text"].split(), v["title"], v["id"])
    wins.sort(key=lambda w: -w["score"])
    card = {
        "schema": "app-creator-card-v1", "channel": man.get("channel"), "channel_url": man.get("channel_url"),
        "corpus": str(corpus),
        "stats": {"targets": len(man.get("videos", [])), "transcribed": len(vids),
                  "words": sum(v.get("words") or 0 for v in vids),
                  "years": [min(years), max(years)] if years else None,
                  "build_videos": len(build), "build_share": round(len(build) / len(vids), 2)},
        "stack": dict(sorted(stack.items(), key=lambda kv: -kv[1]["videos"])),
        "build_order": build_order,
        "chapters": chapters_out,
        "top_videos": [{"id": v["id"], "title": v["title"][:90], "published": v.get("published"),
                        "minutes": int((v.get("duration") or 0) / 60), "words": v.get("words"), "url": v.get("url")}
                       for v in sorted(build, key=lambda v: -(v.get("words") or 0))[:15]],
        "gotchas": wins[:a.windows],
    }
    out = Path(a.out) if a.out else corpus.parent / "_cards" / f"{corpus.name}.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(card, indent=1), encoding="utf-8")
    print(json.dumps({"verdict": "OK", "card": str(out), **card["stats"], "stack_terms": len(stack),
                      "gotcha_windows": len(card["gotchas"])}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
