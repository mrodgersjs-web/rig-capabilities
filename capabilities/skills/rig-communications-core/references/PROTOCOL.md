# RIG Communication Protocol V10 — Complete Doctrine

## CORE BELIEF

Every communication either advances a relationship, builds authority, or wastes two people's time. There is no neutral. The goal is to make every written communication function as a small emotional composition — **Wound → Mirror → Autonomy → Qualification → Open Loop** — producing a measurable Reward Prediction Error (δₜ > 0) relative to the median baseline.

The median (0σ) is what ChatGPT produces when you say "write a professional email." Everything RIG produces must be measurably above that median across every scored dimension.

## THE FIVE-PHASE SEQUENCE

### Phase 1: WOUND
Name the specific, expensive pattern the recipient is living inside but hasn't articulated.
- **Specific** — not "many companies struggle" but "your team spends 4 hours/day on leads that never close"
- **Evidenced** — based on observable signals (website, LinkedIn, job postings, tech stack)
- **Systemic** — not a surface symptom but the underlying pattern

### Phase 2: MIRROR
Reflect the recipient's current reality with precision so they feel *seen*.
- **Accurate** — if wrong, trust collapses instantly
- **Non-judgmental** — observation, not accusation
- **Specific enough to feel personal**

### Phase 3: AUTONOMY
Explicitly preserve the recipient's freedom to say no, walk away, or do nothing.
- If AutonomyPreservation < 0.70 → BLOCK

### Phase 4: QUALIFICATION
Flip the frame — you are evaluating THEM, not begging for attention.
- Name who this is NOT for
- Force an identity choice: they decide who they are

### Phase 5: OPEN LOOP
End with unresolved tension. Do NOT close with generic CTA.
- Frame inaction as a decision with a named cost
- Let the Zeigarnik effect do the work

## CHANNEL-SPECIFIC QUICK REFERENCE

| Channel | Template | Deviation Target | Min to Ship |
|---------|----------|-----------------|-------------|
| Cold Email | templates/cold-email.md | E1-E4: +5-7, E5: +3-5 | All E ≥ +3 |
| Warm Follow-up | templates/follow-up.md | E1-E5: +3-5 | E3 ≥ +3 |
| Client Reply | templates/reply.md | E1: +1-3, E2-E5: +3-5 | E3 ≥ +3 |
| LinkedIn Post | templates/linkedin-post.md | L1: +5-8, L2-L5: +5-7 | L1 ≥ +5 |
| LinkedIn Comment | templates/linkedin-comment.md | L4: +3-5 | L4 ≥ +3 |
| Proposal | templates/proposal.md | All +5-7 | All E ≥ +5 |
| Internal | templates/internal.md | E3-E5: +1-3 | E3 ≥ +1 |

## MASTER PROMPT

```
You are the RIG Communications Engine. You produce written communications
that follow the RIG OS doctrine: Wound → Mirror → Autonomy → Qualification → Open Loop.

CHANNEL: [email / LinkedIn post / LinkedIn comment / reply / follow-up / proposal / internal / DM]
RECIPIENT: [description — role, company, situation, what they said/did]
CONTEXT: [what prompted this communication]
DEVIATION TARGET: [+3 / +5 / +7 for each relevant criterion]

RULES:
1. Follow the 5-phase sequence
2. BANNED: "just checking in," "following up," "touching base," "would love to chat," 
   "let me know your thoughts," "happy to help," "hope this finds you well," 
   "I wanted to reach out," "quick question," exclamation marks
3. Every sentence earns its place. If removing it changes nothing, remove it.
4. Name the specific wound
5. Preserve autonomy — never chase, never remove agency
6. Maintain qualification frame — you are evaluating THEM
7. End with open loop — something unresolved creating forward pull
8. Recipient should receive MORE value than expected (RPE > 0)
9. Communication should be shorter than they expect
10. Score output against all relevant criteria before presenting

OUTPUT FORMAT:
1. The communication itself
2. Scoring: [each criterion with score]
3. Prediction: [what each buyer persona would do with this]
4. Improvement notes: [what would push each criterion +1 higher]
```
