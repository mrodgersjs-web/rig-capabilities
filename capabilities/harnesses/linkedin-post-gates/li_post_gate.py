#!/usr/bin/env python3
"""
li_post_gate.py — executable pre-publish gate for the LinkedIn post session.

Born from the Nintendo post post-mortem (activity 7508521427411587072):
152 impressions against a 1,000 checkpoint, 1 reaction, 0 third-party reposts,
profile viewers from the post 0, and an audience 22% London against a Denver
enterprise/healthcare buyer.

Two corrections to prior doctrine, both measured:
  - The link penalty attaches to the PREVIEW CARD, not the URL. A bare body URL
    measured BETTER than link-free. (MagicPost, 566,957 posts.)
  - Question endings do nothing. (AuthoredUp, n=417,550.)

Contract: every finding carries a VERB. A gate that only reports a score is a
dashboard, and a dashboard does not change what ships.

  exit 0 = pass
  exit 1 = blocked (a halt-tier finding)
  exit 2 = usage / internal error

Stdlib only. No network, no model.
"""

import argparse
import hashlib
import json
import re
import sys

# Buyer vocabulary. Mike sells governed AI deployment into enterprise and
# healthcare operations. Posts must speak to that buyer or they select away
# from him (LinkedIn retrieval matches on post vocabulary, arXiv:2510.14223).
BUYER_TERMS = re.compile(
    r"\b(pilot|budget|owner|owned|ops|operations|clinical|health\s?system|"
    r"CIO|CMO|ROI|governance|procurement|vendor|rollout|committee|"
    r"enterprise|adoption|metric|accountable|stakeholder|revenue|cost)\b",
    re.I,
)

# Framing that reads as entertainment/hobby and selects for a creative and
# comms audience rather than an operator audience.
NON_BUYER_TERMS = re.compile(
    r"\b(nintendo|mario|zelda|pac-?man|sega|game\s?boy|cartridge|console|"
    r"super\s?mario|world\s?1-1|nostalgia|arcade|80s|eighties|pokemon)\b",
    re.I,
)

# Promotional CTA. LinkedIn's own out-of-network criteria require content
# "not overly promotional in nature" (Help a1499047).
PROMO_CTA = re.compile(
    r"(contact me|book (a|your|my) (call|demo|time)|schedule (a|your|my) (call|demo)|"
    r"link in (my |the )?(bio|comments|comment)|DM me|send me a message|"
    r"learn more at|sign up|grab (it|this|your)|free (trial|guide|download)|"
    r"click (the |this )?link|learn more -|learn more—)",
    re.I,
)

URL_RE = re.compile(r"https?://[^\s)\]]+")
# LinkedIn renders a preview card for most bare URLs; the measured penalty is
# on the card. We cannot see the renderer from here, so a URL is flagged and
# the ACTION explains the measured distinction rather than banning it.
# Saturation trigger. Proximity-based, because the real post that motivated this
# gate said "a company that asks me about AI. They want to buy the console. They
# want the platform decision, the enterprise license" and a naive 'AI pilot'
# pattern missed it entirely. The gate must fire on the artifact it was built from.
AI_LANE = re.compile(
    r"\bAI\b.{0,140}\b(pilot|pilots|adoption|rollout|rollouts|platform|deploy|"
    r"deployment|experiment|experiments|budget|committee|vendor|license|licence|"
    r"enterprise|licence|tool|tools|model|models|implementation)\b"
    r"|\b(pilot|pilots|adoption|rollout|rollouts|experiment|experiments)\b.{0,140}\bAI\b"
    r"|\bgenerative AI\b|\bagentic AI\b|\benterprise AI\b|\bAI agent",
    re.I | re.S,
)

BOILER = re.compile(
    r"^(agree|great post|love this|so true|100%|this!|well said|thanks for sharing|"
    r"couldn'?t agree more)",
    re.I,
)


def _lines(text):
    return [ln.rstrip() for ln in text.splitlines()]


def _nonempty(text):
    return [ln.strip() for ln in text.splitlines() if ln.strip()]


def finding(fid, tier, severity, verdict, action, detail, evidence):
    """Every finding MUST carry a verb. That is the whole point of the file."""
    assert action["verb"] in ("REWRITE", "RANK", "BLOCK", "ESCALATE"), action
    return {
        "id": fid,
        "evidence_tier": tier,          # (a) platform-official (b) measured (c) opinion
        "severity": severity,           # halt | degrade
        "verdict": verdict,             # PASS | FAIL
        "action": action,
        "detail": detail,
        "evidence": evidence,
    }


def check_promo_cta(text):
    m = PROMO_CTA.search(text)
    if not m:
        return finding("CG-10", "a", "halt", "PASS",
                       {"verb": "BLOCK", "note": "no CTA"},
                       "No promotional call-to-action in body.",
                       "LinkedIn Help a1499047: out-of-network distribution requires content "
                       "'not overly promotional in nature'.")
    return finding("CG-10", "a", "halt", "FAIL",
                   {"verb": "REWRITE",
                    "rewrite": "Delete the ask. Close on a claim the buyer would argue with, "
                               "or on a concrete number. 'Contact me / learn more / book a call' "
                               "is what blocks out-of-network distribution.",
                    "target": m.group(0)},
                   f"Promotional CTA found: {m.group(0)!r}.",
                   "LinkedIn Help a1499047 ('Suggested posts in feed'): LinkedIn selects "
                   "out-of-network content that is 'not overly promotional in nature' and where "
                   "'all aspects of the post relate to one another'.")


def check_link(text):
    urls = URL_RE.findall(text)
    if not urls:
        return finding("CG-11", "b", "degrade", "PASS",
                       {"verb": "BLOCK", "note": "no URL"},
                       "No body URL.",
                       "MagicPost 566,957 posts: link-free 786 median impressions.")
    return finding("CG-11", "b", "degrade", "FAIL",
                   {"verb": "REWRITE",
                    "rewrite": "The measured penalty is on the PREVIEW CARD, not the URL. "
                               "A bare URL measured 858 median impressions vs 786 link-free, "
                               "so a bare URL is acceptable. What costs you is the rich preview "
                               "card (414, i.e. -48%). Choose: keep the URL bare and unadorned, "
                               "or move it to the first comment. Do NOT delete a URL on the "
                               "belief LinkedIn bans links - it does not.",
                    "target": urls[0]},
                   f"{len(urls)} body URL(s): {urls[0]}",
                   "MagicPost 'Do External Links Kill Your LinkedIn Reach?' (566,957 posts): "
                   "preview card 414 vs 795 median impressions (-48%); bare body URL 858 vs 786 "
                   "link-free. LinkedIn Help a1339724 publishes NO link-demotion rule.")


def check_question_close(text):
    ne = _nonempty(text)
    if not ne:
        return finding("CG-12", "b", "degrade", "PASS",
                       {"verb": "BLOCK", "note": "empty"},
                       "Empty body.", "")
    last = ne[-1]
    if last.rstrip().endswith("?"):
        return finding("CG-12", "b", "degrade", "FAIL",
                       {"verb": "REWRITE",
                        "rewrite": "End on a claim, not a question. The 'always end with a "
                                   "question' rule is folklore: n=417,550 shows 2.57% ER with "
                                   "a question ending vs 2.55% without. A confident closing "
                                   "statement is the measured-neutral option and reads as "
                                   "conviction.",
                        "target": last[:80]},
                       f"Post closes with a question: {last[:80]!r}",
                       "AuthoredUp 'LinkedIn Engagement Rate in 2026' (n=417,550): question "
                       "endings 2.57% vs 2.55% median ER. No effect.")
    return finding("CG-12", "b", "degrade", "PASS",
                   {"verb": "BLOCK", "note": "closes on a claim"},
                   "Closes on a claim.", "")


def check_icp_vocabulary(text):
    head = "\n".join(_nonempty(text)[:3])
    buyer = len(BUYER_TERMS.findall(text))
    non = len(NON_BUYER_TERMS.findall(head))
    if non > 0 and buyer == 0:
        return finding("CG-13", "b", "degrade", "FAIL",
                       {"verb": "REWRITE",
                        "rewrite": "The framing selects for a creative/comms audience, not your "
                                   "buyer. Move the buyer's stakes into the first two lines "
                                   "(budget, owner, pilot, clinical ops, ROI). Keep the metaphor "
                                   "to ONE line later in the body, or drop it. The Nintendo post "
                                   "reached 22% London and 0 Denver decision-makers with this "
                                   "exact failure mode.",
                        "target": head[:120]},
                       f"Head framing carries {non} non-buyer term(s) and the body carries 0 "
                       f"buyer terms.",
                       "LinkedIn retrieval matches posts to members by topic/vocabulary "
                       "(arXiv:2510.14223, LinkedIn-authored). Edelman-LinkedIn (n=1,300+): "
                       "30% of decision-makers REMOVED a vendor from consideration after "
                       "thought leadership they judged not relevant.")
    if non > 0:
        return finding("CG-13", "b", "degrade", "FAIL",
                       {"verb": "REWRITE",
                        "rewrite": f"Metaphor present in the head ({non} term(s)) but buyer terms "
                                   f"are present ({buyer}). Tighten: metaphor should not lead. "
                                   f"Put the operational stakes in line 1-2 and demote the "
                                   f"metaphor below the fold.",
                        "target": head[:120]},
                       f"Head leads with non-buyer framing ({non} term(s)); {buyer} buyer term(s) "
                       f"present in body.",
                       "arXiv:2510.14223 (LinkedIn); Edelman-LinkedIn B2B Thought Leadership "
                       "Impact Study 2021/2025.")
    return finding("CG-13", "b", "degrade", "PASS",
                   {"verb": "BLOCK", "note": "buyer framing present"},
                   f"Buyer framing present ({buyer} term(s)); head not dominated by "
                   f"non-buyer vocabulary.", "")


def check_saturation(text, crowding_count=None):
    """Saturation is a REWRITE trigger, not a ban. The measured advice is to
    sharpen the angle, not to change the subject."""
    is_ai_lane = bool(AI_LANE.search(text))
    if not is_ai_lane:
        return finding("CG-14", "b", "degrade", "PASS",
                       {"verb": "BLOCK", "note": "off the crowded lane"},
                       "Topic is not the AI-pilot/AI-adoption lane.",
                       "")
    if crowding_count is None:
        return finding("CG-14", "b", "degrade", "FAIL",
                       {"verb": "RANK",
                        "rewrite": "This is the crowded AI lane and the crowding was not "
                                   "measured. Run the pre-flight count: search the topic on "
                                   "LinkedIn for the past 24h and count near-identical takes. "
                                   "The Nintendo post had NINE competing 'why AI pilots fail' "
                                   "posts in the same 24h. Report the number, then sharpen the "
                                   "angle. Do NOT change the subject - the measured advice is a "
                                   "sharper angle in a saturated topic, not a new topic.",
                        "target": "AI lane, crowding uncounted"},
                       "AI-pilot/AI-adoption lane detected but pre-flight crowding not measured.",
                       "MagicPost (41,127 posts): AI is the 2nd-worst engagement topic of 44, "
                       "0.24% median ER vs followers. Pangram (1,002,627 posts): 40%+ of "
                       "longform LinkedIn posts are fully AI-generated.")
    if crowding_count >= 3:
        return finding("CG-14", "b", "degrade", "FAIL",
                       {"verb": "REWRITE",
                        "rewrite": f"{crowding_count} near-identical takes already in the window. "
                                   f"Keep the topic, kill the shared framing. Your differentiator "
                                   f"must be in line 1-2 or you are competing on volume in a lane "
                                   f"where the median post earns 0.24% ER.",
                        "target": f"crowding={crowding_count}"},
                       f"Crowding measured at {crowding_count} near-identical posts in the window.",
                       "MagicPost (41,127 posts) + Pangram (1,002,627 posts).")
    return finding("CG-14", "b", "degrade", "PASS",
                   {"verb": "BLOCK", "note": f"crowding={crowding_count}"},
                   f"Crowding measured at {crowding_count}; acceptable.", "")


def check_hook(text):
    ne = _nonempty(text)
    if len(ne) < 2:
        return finding("CG-02", "a", "halt", "FAIL",
                       {"verb": "REWRITE",
                        "rewrite": "Needs at least two lines of hook.",
                        "target": "short body"},
                       "Body has fewer than two non-empty lines.", "")
    hook = ne[0] + " " + ne[1]
    if len(hook) > 210:
        return finding("CG-02", "a", "halt", "FAIL",
                       {"verb": "REWRITE",
                        "rewrite": f"First two lines are {len(hook)} chars, over the 210 limit. "
                                   f"Compress to tension plus a number in <=210.",
                        "target": hook[:120]},
                       f"Hook is {len(hook)} chars (>210).", "")
    if not re.search(r"\d|[A-Z][a-z]{2,}", hook):
        return finding("CG-02", "a", "halt", "FAIL",
                       {"verb": "REWRITE",
                        "rewrite": "Hook has no number and no proper noun. Add a concrete figure "
                                   "or a named thing. Tension alone is not enough to earn the "
                                   "second line.",
                        "target": hook[:120]},
                       "Hook carries neither a number nor a proper noun.", "")
    return finding("CG-02", "a", "halt", "PASS",
                   {"verb": "BLOCK", "note": f"{len(hook)} chars"},
                   f"Hook {len(hook)} chars with a concrete anchor.", "")


def check_length(text, mode="text"):
    n = len(text.strip())
    lo, hi = (400, 700) if mode == "visual" else (900, 1300)
    if lo <= n <= hi:
        return finding("CG-03", "b", "degrade", "PASS",
                       {"verb": "BLOCK", "note": f"{n} chars"},
                       f"{n} chars, inside the {lo}-{hi} band.", "")
    if n < lo:
        verb = "REWRITE"
        note = (f"{n} chars, under the {lo} floor. Note the measured nuance: ER peaks at "
                f"2,001-2,500 chars and median impressions keep climbing to 3,000. The band is "
                f"a house rule, not a measured optimum. If you are under because you cut the "
                f"receipt, put the receipt back.")
    else:
        verb = "REWRITE"
        note = f"{n} chars, over the {hi} ceiling. Trim."
    return finding("CG-03", "b", "degrade", "FAIL",
                   {"verb": verb, "rewrite": note, "target": f"{n} chars"},
                   f"{n} chars, outside the {lo}-{hi} band.",
                   "AuthoredUp (372,126 posts): ER peaks 2,001-2,500 chars (2.67%), median "
                   "impressions peak at 2,501-3,000 (1,400). Band is house policy.")


def check_receipt(text):
    if re.search(r"\d+%|\d+x|v\d+\.\d+|20\d{2}-\d{2}|\$[\d,]+|\d{1,3},\d{3}", text):
        return finding("CG-04", "b", "halt", "PASS",
                       {"verb": "BLOCK", "note": "receipt present"},
                       "Concrete receipt present.", "")
    return finding("CG-04", "b", "halt", "FAIL",
                   {"verb": "REWRITE",
                    "rewrite": "No receipt. Add one measured artefact: a percentage, a multiple, "
                               "a dollar figure, a dated version, or a named tool. A lesson with "
                               "no receipt is an opinion and the harness treats it as one.",
                    "target": "body"},
                   "No metric, multiple, currency, or dated version in body.", "")


def run_checks(text, mode="text", crowding_count=None):
    out = []
    out.append(check_hook(text))
    out.append(check_receipt(text))
    out.append(check_promo_cta(text))
    out.append(check_link(text))
    out.append(check_question_close(text))
    out.append(check_icp_vocabulary(text))
    out.append(check_saturation(text, crowding_count))
    out.append(check_length(text, mode))
    return out


def rank(paths, mode="text", crowding_count=None):
    """Ranking is a VERB, not a score. Output is an ordered ship list."""
    rows = []
    for p in paths:
        text = open(p, encoding="utf-8").read()
        fs = run_checks(text, mode, crowding_count)
        halt_fails = [f for f in fs if f["severity"] == "halt" and f["verdict"] == "FAIL"]
        degrade_fails = [f for f in fs if f["severity"] == "degrade" and f["verdict"] == "FAIL"]
        rows.append({
            "path": p,
            "halt_fails": [f["id"] for f in halt_fails],
            "degrade_fails": [f["id"] for f in degrade_fails],
            "ship": "BLOCKED" if halt_fails else ("DEGRADED" if degrade_fails else "SHIP"),
            "first_action": (halt_fails + degrade_fails)[0]["action"]["rewrite"]
            if (halt_fails or degrade_fails) else None,
        })
    order = {"SHIP": 0, "DEGRADED": 1, "BLOCKED": 2}
    rows.sort(key=lambda r: (order[r["ship"]], len(r["degrade_fails"])))
    return rows


# --------------------------------------------------------------------------
# Adversarial self-test. A gate that cannot go RED is theatre.
# --------------------------------------------------------------------------
CLEAN_POST = (
    "We cut approval time 42% across 5 health systems.\n\n"
    "The rule that did it was boring: one named owner per workflow, and a kill number "
    "agreed before the pilot started.\n\n"
    "Most AI rollouts skip both. They buy the platform, hold the committee, and never "
    "run a single real workflow on real data.\n\n"
    "Here is what changed when we did run one.\n\n"
    "We picked the ugliest week of data we had, not the cleanest. Two shifts of lighting "
    "differences and part numbers that changed after an acquisition showed up in week one "
    "instead of after the budget was approved.\n\n"
    "The pilot cost us two weeks and one analyst. The alternative was a $400K platform "
    "decision made on a demo.\n\n"
    "Ninety days later the workflow was in production and the approval queue had a named "
    "owner who could actually change the rule, not just escalate it.\n\n"
    "That is the whole method. Small, real, measurable, and owned by someone with the "
    "authority to change the process when the data says the process is the problem."
)

NON_BUYER_POST = (
    "I blew into a Nintendo cartridge and Mario taught me everything about pilots.\n\n"
    "World 1-1 is the classroom: the first Goomba can kill you at zero cost.\n\n"
    "We ran it that way and rework fell 27% in the first quarter.\n\n"
    "That is the whole method."
)

# name, text, expected verdict, crowding count (None = not measured)
SELFTEST_CASES = [
    ("clean", CLEAN_POST, "SHIP", 2),
    ("clean_ai_uncounted", CLEAN_POST, "DEGRADED", None),
    ("promo_cta", "We cut approval time 42%.\n\nContact me to learn more.", "BLOCKED", 1),
    ("question_close", "We cut approval time 42% in 5 health systems.\n\n"
                       "What would you have done?", "DEGRADED", 1),
    ("hook_short", "ok", "BLOCKED", 1),
    ("nonbuyer_head", NON_BUYER_POST, "DEGRADED", 1),
]


def selftest():
    """Plant each defect, prove RED, then prove GREEN on the clean case."""
    fails = []
    for name, text, expect, crow in SELFTEST_CASES:
        fs = run_checks(text, crowding_count=crow)
        halt_fails = [f for f in fs if f["severity"] == "halt" and f["verdict"] == "FAIL"]
        degrade = [f for f in fs if f["severity"] == "degrade" and f["verdict"] == "FAIL"]
        got = "BLOCKED" if halt_fails else ("DEGRADED" if degrade else "SHIP")
        # The clean case must not be blocked; a gate that blocks good work gets
        # switched off, so this assertion matters as much as the red ones.
        if got != expect:
            fails.append(f"{name}: expected {expect}, got {got}")
        else:
            print(f"  ok  {name:18s} -> {got}")
    # Assert every finding carries a verb, always.
    for name, text, _, _ in SELFTEST_CASES:
        for f in run_checks(text):
            if f["action"]["verb"] not in ("REWRITE", "RANK", "BLOCK", "ESCALATE"):
                fails.append(f"{name}/{f['id']}: finding without a verb")
    # The rewrite-until-clean verb must appear on the uncounted AI-lane path.
    ranked = [f for f in run_checks(CLEAN_POST, crowding_count=None)
              if f["id"] == "CG-14" and f["action"]["verb"] == "RANK"]
    if not ranked:
        fails.append("clean_ai_uncounted: CG-14 did not return a RANK action")


    # PERMANENT REGRESSION: the real artefact that motivated this gate. It
    # produced 152 impressions and must stay RED here forever. If this ever
    # goes green, the gate has been softened past the failure it exists for.
    import os
    reg = os.path.join(os.path.dirname(os.path.abspath(__file__)), "nintendo_post.md")
    if os.path.exists(reg):
        body = open(reg, encoding="utf-8").read()
        fs = run_checks(body, crowding_count=9)
        ids = {f["id"] for f in fs if f["verdict"] == "FAIL"}
        need = {"CG-10", "CG-14"}
        if not need.issubset(ids):
            fails.append(f"regression/nintendo_post.md: expected {sorted(need)} to FAIL, "
                         f"got {sorted(ids)}")
        else:
            print(f"  ok  regression        -> BLOCKED ({', '.join(sorted(ids))})")
    else:
        print("  --  regression fixture nintendo_post.md absent, skipped")

    if fails:
        print("SELFTEST FAIL")
        for f in fails:
            print("   " + f)
        return 1
    print("SELFTEST PASS: every planted defect went RED, the clean case went GREEN, "
          "and every finding carries a verb.")
    return 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("post", nargs="?", help="path to post.md")
    ap.add_argument("--mode", default="text", choices=["text", "visual"])
    ap.add_argument("--crowding", type=int, default=None,
                    help="near-identical posts counted in the pre-flight window")
    ap.add_argument("--rank", nargs="+", metavar="DRAFT", help="rank several drafts")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args()

    if args.selftest:
        return selftest()

    if args.rank:
        rows = rank(args.rank, args.mode, args.crowding)
        if args.json:
            print(json.dumps(rows, indent=2))
        else:
            for i, r in enumerate(rows, 1):
                print(f"{i}. {r['ship']:9s} {r['path']}  halts={r['halt_fails']} "
                      f"degrades={r['degrade_fails']}")
                if r["first_action"]:
                    print(f"   FIRST ACTION: {r['first_action'][:160]}")
        return 0 if all(r["ship"] != "BLOCKED" for r in rows) else 1

    if not args.post:
        ap.error("post path required (or --rank / --selftest)")

    text = open(args.post, encoding="utf-8").read()
    fs = run_checks(text, args.mode, args.crowding)
    halt_fails = [f for f in fs if f["severity"] == "halt" and f["verdict"] == "FAIL"]
    verdict = "BLOCKED" if halt_fails else (
        "DEGRADED" if any(f["verdict"] == "FAIL" for f in fs) else "PASS")

    if args.json:
        print(json.dumps({"verdict": verdict,
                          "sha256": hashlib.sha256(text.encode()).hexdigest()[:12],
                          "findings": fs}, indent=2))
    else:
        print(f"VERDICT: {verdict}   (sha {hashlib.sha256(text.encode()).hexdigest()[:12]})")
        for f in fs:
            if f["verdict"] == "FAIL":
                print(f"\n[{f['severity'].upper()}] {f['id']} (evidence tier {f['evidence_tier']})")
                print(f"  {f['detail']}")
                print(f"  ACTION {f['action']['verb']}: {f['action']['rewrite']}")
                if f["evidence"]:
                    print(f"  EVIDENCE: {f['evidence']}")
        print()
        print("Every finding above carries a verb. A finding with no action is a dashboard.")
    return 1 if halt_fails else 0


if __name__ == "__main__":
    sys.exit(main())
