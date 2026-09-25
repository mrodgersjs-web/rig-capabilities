---
name: great-tg-voice-agent-saas
lane: code-engineering
exemplar_of: tg-saas-skeleton
description: >-
  The seven-stage skeleton proven twice by the same channel in two domains -
  AI recruiter (Vapi/Supabase) and AI medical voice agent (AssemblyAI/Clerk) -
  which is the evidence that the skeleton, not the vendor, is the product.
---

# Voice-agent SaaS - what done looks like

## Corpus matches

- `zcYM_Gqoph4` - AI Recruiter Voice Agent (Vapi + Supabase, 81k views, 2025)
  - thumbnail: `data/corpora/how-to/build-craft/tubeguruji-images/zcYM_Gqoph4.jpg`
- `zjwj21wzs4U` - AI Medical Voice Agent (AssemblyAI + Clerk, 55k views, 2025)
  - thumbnail: `data/corpora/how-to/build-craft/tubeguruji-images/zjwj21wzs4U.jpg`

## The skeleton both videos share

Landing -> auth gate -> dashboard -> intake form -> generated session ->
shareable link -> live voice session -> stored report -> credits/membership gate.

| Feature | Recruiter | Medical |
|---|---|---|
| Intake | JD + duration + interview type | symptom intake -> specialist pick |
| Live layer | Vapi conducts the interview | AssemblyAI streaming STT during consult |
| Durable artifact | question set + results | background-generated report |
| Gate | `user.credits <= 0` -> toast at creation | free tier = general physician only |

## Done means

1. Intake form produces the generated session (questions/consult plan) from the
   AI layer with a JSON-spec prompt.
2. Share link minted and copied via `navigator.clipboard.writeText` + toast.
3. Join page opens the live voice layer on the candidate/patient side.
4. Report/transcript persists; the call itself does not.
5. Credits gate fires at creation (limit+1 attempt shows the toast), never at join.
6. Building the medical variant after the recruiter touches vendors only - that
   swap-cleanliness is the lesson (corpus batch-8 finding #7).
