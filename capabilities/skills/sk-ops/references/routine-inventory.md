# Sub-skill: routine inventory

Use when adding community automation or when reporting what runs the community.

1. List every routine touching the community: name, schedule, model lane, permission mode, and its LAST PROVEN RUN (completed + artifact path).
2. Mark each: running (proven), dormant (defined, no proven run), or blocked (last run emitted BLOCKED/errored/suspended).
3. For each automation, state the guard that makes failure loud.
4. Check for duplicate coverage before adding anything new.
5. Output `ops-map.md`; report dormant routines as dormant, never as running.
