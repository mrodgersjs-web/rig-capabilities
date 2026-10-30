#!/usr/bin/env python3
"""Run the repo's own done-test runner over every asset in the business-strategy family."""
import json, subprocess, sys
REPO = "/Users/rig128gb/Developer/rig-capabilities"
FAMILY = ["business-strategy-os", "strategy-diagnose", "strategy-new-value", "strategy-innovation",
          "strategy-document", "strategy-stories", "strategy-marketing", "strategy-leadership",
          "strategy-review", "strategy-director.md", "strategy-diagnostician.md",
          "strategy-value-architect.md", "strategy-writer.md", "strategy-marketing-realist.md",
          "strategy-board-reviewer.md", "strategy-gate.md", "strategy-corpus-miner.md",
          "strategy-competitor-sim.md", "strategy-only-statement-scorer.md",
          "strategy-document-session.yaml"]
def main() -> int:
    bad = []
    for a in FAMILY:
        r = subprocess.run([f"{REPO}/bin/rig-capabilities", "test", a], capture_output=True, text=True, cwd=REPO)
        try:
            d = json.loads(r.stdout)
        except Exception:
            print(f"{a:34} UNREADABLE {r.stdout[:60]} {r.stderr[:60]}"); bad.append(a); continue
        fails = [x for x in d.get("results", []) if not x.get("ok")]
        flag = "" if d.get("pass") else "  <-- " + "; ".join(f"{x['form'][:46]} -> {str(x.get('detail'))[:70]}" for x in fails[:2])
        print(f"{a:34} pass={d.get('pass')} ran={d.get('ran')} unrunnable={d.get('unrunnable')}{flag}")
        if not d.get("pass"): bad.append(a)
    print("\nALL PASS" if not bad else f"\nFAILING: {bad}")
    return 0 if not bad else 2
if __name__ == "__main__":
    sys.exit(main())
