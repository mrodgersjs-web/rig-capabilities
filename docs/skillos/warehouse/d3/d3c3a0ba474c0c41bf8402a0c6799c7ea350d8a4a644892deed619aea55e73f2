#!/bin/bash
# outcome: agent-engineering:
# done_when: cmd:python3 scripts/hook_fires.py goal-loop-startup.sh
# great_example: examples/great/agent-engineering/goal-loop-startup.md
# quality_floor: 0.6
# Goal Loop Autoload — runs at session start for every Claude Code session
# Injects goal loop context into the session

GOAL_LOOP_DIR="$HOME/.hermes/skills/goal-loop"
ENGINE_DIR="$HOME/rig-goal-engine"
DOCTRINE="$HOME/.rig/agent-doctrine/RIG_GOAL_LOOP_OPERATING_PROCEDURE.md"

# Quick status
SPECS=$(python3 -c "import yaml,pathlib; print(sum(len(yaml.safe_load(open(f)).get('goals',[])) for f in sorted(pathlib.Path('$GOAL_LOOP_DIR/yaml-specs').glob('*.yaml'))))" 2>/dev/null || echo "?")

cat << EOF

╔══════════════════════════════════════════════════════════╗
║  GOAL LOOP ACTIVE — ${SPECS:-?} loops loaded                     ║
║                                                          ║
║  SELECT A LOOP BEFORE DOING MEANINGFUL WORK:             ║
║                                                          ║
║  /goal-loop         → Run any of 73 loops                ║
║  /build-out         → Build real systems (10 loops)       ║
║  /gtm-engine        → Build full GTM stack                ║
║  /linkedin-machine  → Build LinkedIn operation            ║
║  /swarm-recon       → Multi-angle research                ║
║  /fix-this          → Fix something broken                ║
║  /connect-these     → Connect two tools                   ║
║  /command-registry  → Design new loops                    ║
║                                                          ║
║  Engine: cd ~/rig-goal-engine && python3 cli.py <cmd>    ║
╚══════════════════════════════════════════════════════════╝

EOF

# rig-capabilities session boot pack (best-effort, silent, 5s cap)
RIG_CAP_BOOT="$HOME/Developer/rig-capabilities/bin/rig-boot-pack"
if [ -x "$RIG_CAP_BOOT" ]; then
  ( command -v timeout >/dev/null 2>&1 && timeout 5 "$RIG_CAP_BOOT" || "$RIG_CAP_BOOT" ) >/dev/null 2>&1 &
fi
