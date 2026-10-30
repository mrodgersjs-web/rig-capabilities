#!/bin/sh
# Rewrite c128 to what the board.card rubric actually asks for: ONE done state, ONE next
# action, owner named. The first version of this card was a build log and Jev escalated it
# (one_outcome 0.82, board_is_canonical 0.59, next_action 1.91, status 0.54), which was right.
cd /Users/rig128gb/Desktop/Projects/kanban || exit 1
python3 kanban.py state --title "Run the business-strategy family on one live RIG decision" c128 \
"Done: the business-strategy family (corpus, 9 skills, 10 agents, harness) is built, verified and installed in rig-capabilities, callable from 5 harnesses, on the canonical board at http://127.0.0.1:8913.

Next action (owner: Mike, today): pick one live RIG decision - which offer to lead with - and run the family on it, on this board. The verdict it returns is the real test of the build. It drafts and grades only: it spends nothing, sends nothing and opens no second board or tracker. Full record: data/corpora/strategy/BUILD-LOG.md."
