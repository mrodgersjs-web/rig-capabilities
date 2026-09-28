# Sub-skill: bid-strategy ladder

1. Count conversions per campaign for the trailing 30 days from the account (not from memory).
2. Assign by volume: 0-5 conversions -> manual CPC or max clicks with a CPC ceiling; 5-30 -> max conversions (no target); 30+ and stable -> tCPA; revenue-tracked and value-varied -> tROAS.
3. Move up a rung only after two stable weeks at the current rung; document the move and date in `bidding-plan.md`.
4. When moving to tCPA, set the target at trailing CPA + 10-20% headroom; tighten only after the campaign beats it for a week.
5. If delivery collapses after a move, revert to the prior rung - reverting is not failure, thrashing is.
6. Never stack a strategy change with a budget increase; the two interfere and the read is ruined.
