#!/usr/bin/env python3
"""Run doctrine.surface over the strategy family and print one line per file."""
import json, subprocess, sys, pathlib
ROOT = pathlib.Path("/Users/rig128gb/Developer/rig-capabilities")
GATE = "/Users/rig128gb/.rig/bin/rig-s1gate"
def main() -> int:
    files = sorted(ROOT.glob("capabilities/skills/strategy-*/SKILL.md")) + [ROOT / "capabilities/skills/business-strategy-os/SKILL.md"]
    worst = 1
    for f in files:
        r = subprocess.run([GATE, "check", "doctrine.surface", "--file", str(f),
                            "--subject", f"doctrine.surface:{f.parent.name}", "--json"],
                           capture_output=True, text=True)
        try:
            d = json.loads(r.stdout)
        except Exception:
            print(f"{f.parent.name}: UNREADABLE {r.stdout[:80]} {r.stderr[:80]}"); worst = 2; continue
        a = d.get("answers", {})
        vals = {k: round(float(v.get("noul", v.get("score", 0))), 2) for k, v in a.items()}
        print(f"{f.parent.name}: {d.get('verdict')} | " + " ".join(f"{k}={v}" for k, v in vals.items()))
        if d.get("verdict") != "PASS":
            worst = min(worst, 2)
    return worst
if __name__ == "__main__":
    sys.exit(main())
