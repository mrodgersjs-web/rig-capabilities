#!/bin/bash
# outcome: communications: no throat-clearing or fake-urgency draft reaches a send path
# done_when: cmd:printf "Hope you're doing well. Just circling back on this.\n" | bash capabilities/hooks/comms-guard-throat-clear.sh; test $? -eq 1
# done_when: cmd:printf "Your checkout drops 12%% of carts. Worth 15 minutes?\n" | bash capabilities/hooks/comms-guard-throat-clear.sh; test $? -eq 0
# quality_floor: 0.6
# Comms guard — stdin: draft text. Exit 1 = banned openings/urgency present.
# Wire: pre-send check in any comms loop, or `git` pre-commit over out/*.md drafts.

STDIN=$(cat)
BAD=0

# banned openings (rig_comms.compress THROAT_CLEARING, kept in sync)
while IFS= read -r phrase; do
  if printf '%s' "$STDIN" | grep -qiF "$phrase"; then
    echo "comms-guard: throat-clearing detected: '$phrase'" >&2
    BAD=1
  fi
done <<'PHRASES'
hope you're doing well
hope you are doing well
hope this email finds you well
just circling back
just checking in
just following up
i wanted to reach out
as you know
in today's fast-paced
per my last email
PHRASES

# fake urgency in subject lines
if printf '%s' "$STDIN" | head -1 | grep -qiE '(urgent|immediately|last chance|expires today)'; then
  echo "comms-guard: urgency theater in first line (truth over urgency theater — doctrine 9)" >&2
  BAD=1
fi

exit $BAD
