#!/usr/bin/env python3
"""Deterministic lint for a business-strategy artifact. Code catches what code can catch; judgment goes to
Jev (rig-s1gate check strategy.output). Checks come from the corpus doctrine, cited in the SKILL.md.

usage: strategy_lint.py FILE [--mode document|statement] [--json]
       strategy_lint.py --selftest     red fixture must trip, green fixture must stay clean (non-vacuity proof)
exit:  0 clean | 1 findings | 3 usage"""
import json, re, sys
from pathlib import Path
HERE = Path(__file__).resolve()
FIX = HERE.parents[2] / "business-strategy-os/references/jev-fixtures"
VIRTUE = ["best-in-class", "world-class", "world class", "leading provider", "customer-focused", "customer focused",
          "customer-centric", "excellent service", "exceptional service", "high-quality", "high quality", "innovative solutions",
          "one-stop shop", "cutting-edge", "cutting edge", "passionate about", "tailored solutions", "trusted partner",
          "partner of choice", "provider of choice", "synergy", "best of breed", "state-of-the-art", "industry-leading"]
GOAL = [r"\b(grow|increase|double|triple|10x)\b[^.\n]{0,40}\b(revenue|sales|share|profit|customers|growth)\b",
        r"\bbecome\b[^.\n]{0,20}\b(the )?(number one|no\.? ?1|#1|leader|leading|market leader)\b",
        r"\b(number one|#1)\b[^.\n]{0,20}\bby 20\d\d\b", r"\b\d{1,3}\s?% (growth|increase)\b"]
BETTER = [r"\bbetter than\b", r"\bthe best\b", r"\bbest\b [a-z]+ in (the )?(market|industry|category)"]
# An only-statement is normally wrapped across lines, so the window spans newlines but
# must not cross a sentence-ending period.
ONLY = re.compile(r"\bonly\b[^.]{0,140}\b(who|that|which|to)\b[^.]{0,200}\b(so|therefore|giving|gives)\b", re.I)
SECTIONS = {"context_or_category": r"\b(context|category)\b", "argument_or_belief": r"\b(status quo|why (it|this) sucks|unique belief|we believe|disagree)",
            "change_or_tradeoffs": r"\b(how we must change|stop doing|trade-?offs?|we will not|we won't|no longer|refuse)\b",
            "statement": r"\b(strategy statement|we are the only)\b", "execution": r"\bexecution\b"}
TRADEOFF = re.compile(r"\b(stop|no longer|will not|won't|refuse|drop|kill|not (do|sell|serve|offer|compete))\b", re.I)
TRADE_HDR = re.compile(r"(trade-?offs?|how we must change|stop doing|what we will not do|we will not)", re.I)
NEG = re.compile(r"\b(no|not|never|stop|stops|drop|refuse|won't|kill|exit|cut|without)\b", re.I)
def has_tradeoffs(text):
    for m in TRADE_HDR.finditer(text):
        if NEG.search(text[m.end(): m.end() + 500]): return True
    return bool(TRADEOFF.search(text))
def lint(text, mode="document"):
    low = text.lower(); f = []
    for v in VIRTUE:
        if v in low: f.append({"rule": "virtue-claim", "severity": "high", "hit": v, "why": "claimed virtue, not an innovation (CLAIM(ElaWyEeHS1w), CLAIM(FF46sruCVpY))"})
    for g in GOAL:
        for m in re.finditer(g, low): f.append({"rule": "goal-as-strategy", "severity": "high", "hit": m.group(0), "why": "a goal is a result, not a how (CLAIM(Ikx1ECodt1M), CLAIM(rWcJOpdrbCY))"})
    for b in BETTER:
        for m in re.finditer(b, low): f.append({"rule": "better-not-different", "severity": "medium", "hit": m.group(0), "why": "better is a synonym for the same (CLAIM(PpcQFN9euao), CLAIM(dt9wpjlT-zA))"})
    if not ONLY.search(text): f.append({"rule": "no-only-statement", "severity": "high", "hit": None, "why": "no 'we are the only X who Y, so Z' statement (CLAIM(kIw__JxmbUo), CLAIM(y1-5nxulR68))"})
    if not has_tradeoffs(text): f.append({"rule": "no-tradeoffs", "severity": "high", "hit": None, "why": "nothing is stopped or refused; a strategy that changes nothing is validation (CLAIM(y1-5nxulR68))"})
    if mode == "document":
        for k, pat in SECTIONS.items():
            if not re.search(pat, low): f.append({"rule": f"missing-section:{k}", "severity": "medium", "hit": None, "why": "five-section strategy document (CLAIM(y1-5nxulR68))"})
        if not (re.search(r"\bdeliver", low) and re.search(r"\bcommunicat", low)):
            f.append({"rule": "execution-not-split", "severity": "medium", "hit": None, "why": "execution = delivery + communication (CLAIM(y1-5nxulR68))"})
    return f
def main(argv):
    if not argv: print(__doc__); return 3
    if argv[0] == "--selftest":
        red = lint((FIX / "red-boilerplate-strategy.md").read_text()); green = lint((FIX / "green-tesla-argument.md").read_text())
        red_ok = sum(1 for x in red if x["severity"] == "high") >= 3
        green_ok = not any(x["severity"] == "high" for x in green)
        print(json.dumps({"red_high_findings": sum(1 for x in red if x["severity"] == "high"), "green_high_findings": sum(1 for x in green if x["severity"] == "high"),
                          "green_all_findings": [x["rule"] for x in green], "selftest": "PASS" if red_ok and green_ok else "FAIL"}))
        return 0 if red_ok and green_ok else 1
    path = Path(argv[0]); mode = "statement" if "--mode" in argv and argv[argv.index("--mode") + 1] == "statement" else "document"
    if not path.exists(): print(f"no such file: {path}", file=sys.stderr); return 3
    f = lint(path.read_text(encoding="utf-8"), mode)
    print(json.dumps({"file": str(path), "mode": mode, "findings": f, "high": sum(1 for x in f if x["severity"] == "high")}, indent=1))
    return 1 if f else 0
if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
