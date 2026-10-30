#!/bin/bash
# how-to corpus recovery: probe a canary every 6h; when YouTube quota clears, run the paced full pass.
# Survives session close via nohup. Dies with the machine. 8 windows max (~48h).
cd /Users/rig128gb/Developer/rig-capabilities || exit 1
LOG=/tmp/howto-recovery.log
CANARY="https://youtu.be/S2sjyokoxeE"
for i in 1 2 3 4 5 6 7 8; do
  echo "[recovery] window $i $(date -u +%FT%TZ) canary probe..." >> "$LOG"
  rm -f /tmp/recovery-canary*
  if timeout 60 yt-dlp --write-auto-sub --sub-lang en --skip-download -o /tmp/recovery-canary "$CANARY" >> "$LOG" 2>&1 && [ -s /tmp/recovery-canary.en.vtt ]; then
    echo "[recovery] QUOTA CLEARED at window $i — running paced full pass" >> "$LOG"
    COMMS_CORPUS=how-to COMMS_SLEEP=6 python3 scripts/scrape_writing_craft.py >> "$LOG" 2>&1
    echo "[recovery] full pass exit=$? manifest=$(wc -l < data/corpora/how-to/manifest.jsonl 2>/dev/null)" >> "$LOG"
    exit 0
  fi
  sleep 21600
done
echo "[recovery] exhausted 8 windows — corpus stays blocked; escalate to Mike" >> "$LOG"
