#!/usr/bin/env python3
"""Gate the board card we just wrote with the repo's own board.card rubric."""
import json, subprocess, sys
from pathlib import Path
BOARD = Path("/Users/rig128gb/Desktop/Projects/kanban/board.json")
TMP = Path("/Users/rig128gb/.aside/u/0/sessions/2026-09-26_FZ5G1NeEd86P2RZw/tmp/boardcard.md")
card = [c for c in json.loads(BOARD.read_text())["cards"] if c["id"] == "c128"][0]
TMP.write_text(f"# {card['title']}\n\nstream={card['stream']} col={card['col']}\n\n{card.get('state','')}\n")
print("card:", card["id"], card["stream"], card["col"], "|", len(card.get("state", "")), "chars")
r = subprocess.run(["/Users/rig128gb/.rig/bin/rig-s1gate", "check", "board.card", "--file", str(TMP),
                    "--subject", "board.card:c128", "--json"], capture_output=True, text=True)
d = json.loads(r.stdout)
print("board.card verdict:", d.get("verdict"))
for q, v in d.get("answers", {}).items():
    print("  %-22s" % q, {k: round(x, 2) for k, x in v.items() if k in ("noul", "score", "confidence") and isinstance(x, (int, float))})
