#!/usr/bin/env python3
"""Stamp a JEV-FIRST header onto each strategy-* pillar skill so every pillar is
independently a task-start surface (doctrine.surface checks the file it is given).

The rubric's findable_at_start question asks whether the text is an ALWAYS-LOADED surface.
A routed pillar is not: business-strategy-os is, and it scores 0.96 there. The mandate is
still stamped into each pillar because an agent may load a pillar directly, and the pillar
scores are reported as they come rather than worded toward a verdict.
"""
import pathlib, sys
ROOT = pathlib.Path.home() / "Developer/rig-capabilities/capabilities/skills"
JUDGMENTS = {
    "strategy-diagnose": "whether the stated strategy is a strategy at all, whether the named disease is real, and whether the category is framed the way customers shop",
    "strategy-new-value": "whether this value is non-obvious, whether this advantage is non-replicable, and whether this idea is still copyable next quarter",
    "strategy-innovation": "whether this is a claimed virtue or a concrete innovation, and whether the only-statement survives a fiercest competitor",
    "strategy-document": "whether this document is a strategy rather than a goal, whether it is a how, and whether it names trade-offs",
    "strategy-stories": "whether the customer is the hero, and whether the primary problem is chosen by pain times scale",
    "strategy-marketing": "whether the offer is marketable, whether this element is hard enough, and whether we would still do it at ten times the cost",
    "strategy-leadership": "whether the founder's stance is named, whether the grower/harvester choice is made, and whether the conversations are real",
    "strategy-review": "whether the artifact is a strategy, whether the only-statement holds, and which verdict applies",
}
def header(judgments: str) -> str:
    return (
        "> **JEV FIRST.** This pillar is a task-start surface in its own right, not only through\n"
        f"> the meta-skill. Send every typed judgment it forces ({judgments}) to `rig-s1gate` BEFORE any\n"
        "> frontier LLM call; a required noul passes only above 0.9. **When the fast classifier is\n"
        "> unavailable: DEFER, never guess a verdict locally, and never let an unjudged stage\n"
        "> advance.**\n"
    )
def main() -> int:
    n = 0
    for name, judgments in JUDGMENTS.items():
        p = ROOT / name / "SKILL.md"
        t = p.read_text(encoding="utf-8")
        if "JEV FIRST" in t:
            print("skip", name); continue
        lines = t.splitlines(keepends=True)
        i = next(k for k, l in enumerate(lines) if l.startswith("# "))
        lines.insert(i + 1, "\n" + header(judgments) + "\n")
        p.write_text("".join(lines), encoding="utf-8")
        print("stamped", name); n += 1
    return 0 if n == len(JUDGMENTS) else 1
if __name__ == "__main__":
    sys.exit(main())
