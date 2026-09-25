---
name: tg-voice-agent-stack
description: >
  Sub-skill of tg-saas-skeleton: voice-agent products per the TubeGuruji corpus —
  the shared skeleton (intake form → generated session → shareable link → live
  voice call → report/membership gate) with Vapi as the conversational agent and
  AssemblyAI for streaming speech-to-text.
tags: [rig, doctrine, voice-agent, vapi, assemblyai, tubeguruji]
metadata:
  source: "corpus — zcYM_Gqoph4 (AI recruiter, Vapi+Supabase, 81k views), zjwj21wzs4U (AI medical, AssemblyAI+Clerk, 55k views), oE7bVYRFYrU (education voice agent, AssemblyAI+Convex), 5F6hpwPeUWY (medical voice agent, streaming API)"
  extracted: "2026-09-25"
  parent: tg-saas-skeleton
outcome: "A voice-agent SaaS on the shared skeleton: form → generated interview/consult → share link → live voice session → stored report, gated by credits or membership."
activation: "Load when the product conducts a live voice conversation with users (interviews, consults, tutoring, screening) or when extending an existing voice-agent app."
instruction: >
  Build the shared skeleton first; the voice vendor is the last swap. Keep the live
  session ephemeral and the artifact durable: what persists is the generated
  question set, the transcript/report, and the share link — not the call itself.
applies_when:
  env: "local repo + Vercel preview; microphone-capable browser"
  runtime: "Next.js app; vendor web/JS SDK for the live session"
  deps: "Vapi or AssemblyAI (or Murf/Deepgram/Replicate alternatives), hosted DB (Supabase/Convex), auth provider"
  params: "intake fields per domain (JD + duration + type for recruiter; symptoms for medical); quota on session creation"
  budget: "vendor free tiers carry the demo; live voice minutes are the first real cost"
  scale: "single-domain agent; one voice, one persona"
permissions:
  - fs.read
  - fs.write
  - bash
  - browser.read
  - net.api-calls
  - gate-d-required:purchase
flow:
  - Stand up the seven skeleton stages (tg-saas-skeleton).
  - Build the intake form for the domain (recruiter: job description, duration, interview type → AI generates the question set, zcYM_Gqoph4; medical: symptom intake → AI picks the specialist, zjwj21wzs4U).
  - Persist the generated session and mint a shareable candidate/patient link (copy via navigator.clipboard.writeText + toast, zcYM_Gqoph4).
  - Build the join page and wire the live voice layer (Vapi conducts the conversational interview, zcYM_Gqoph4; AssemblyAI delivers streaming speech-to-text while the user speaks, zjwj21wzs4U).
  - Generate and store the post-session artifact (report/feedback) as the durable output.
  - Gate session creation on credits (`user.credits <= 0` → toast, zcYM_Gqoph4) or membership (free tier exposes only the general physician; specialists require membership, zjwj21wzs4U).
done_when:
  - "grep:capabilities/skills/tg-voice-agent-stack/SKILL.md:Vapi"
  - "grep:capabilities/skills/tg-voice-agent-stack/SKILL.md:AssemblyAI"
  - "grep:data/corpora/how-to/manifest.jsonl:zjwj21wzs4U"
out_of_scope:
  - telephony/PSTN integration, compliance-grade medical records (HIPAA-class)
  - voice cloning (that is tg-ai-media-pipeline, cost table there)
  - multi-agent orchestration
quality_floor: "The shareable-link flow must be demonstrated end to end (create → link → join page) before the voice layer is claimed working; voice without persistence is a demo, not the skeleton."
---

# Voice-Agent Stack

## The two corpus proof-builds share one skeleton

- **AI Recruiter** (zcYM_Gqoph4, 2025, 81k views): landing → auth → dashboard →
  intake form (JD + duration + type) → AI-generated questions → unique shareable
  interview link → candidate join page → **Vapi** runs the live interview →
  credits gate on creation.
- **AI Medical voice agent** (zjwj21wzs4U, 2025, 55k views): landing → auth →
  dashboard → symptom intake → AI picks the specialist → live consult with
  **AssemblyAI** streaming STT → background report generation → membership gate
  (free tier = general physician only).

Same seven stages, different vendor and domain. That is the design lesson: build
the skeleton once, swap the voice vendor per product.

## Vendor map (as used, not as marketed)

| Job | Vendor | Evidence |
|---|---|---|
| Conversational agent that runs the call | Vapi | zcYM_Gqoph4 |
| Streaming speech-to-text during the call | AssemblyAI | zjwj21wzs4U, oE7bVYRFYrU |
| Voice-over for generated content (not live) | Murf ("Murf Falcon") | DEUi_8e7GLk |
| Voice cloning on demand | Chatterbox via Replicate, <$1 per 45 min hosted (vs self-host that still pays for cloud; free Deepgram default voice as the fallback) | kxM_oEMn3IM |
| Talking avatar for interview practice | Akool/Akul streaming avatar API | b_4Z_QpEd2Q |

## Design rules from the corpus

- **The artifact is durable; the call is not.** Persist questions, transcript,
  report, and the share link. Nothing in the corpus stores raw audio as the product.
- **Gate at creation, not at join.** Credits are checked when the interviewer
  creates the session (`user.credits <= 0` → toast, zcYM_Gqoph4 05:44) — the
  candidate joining via link is never blocked.
- **Tier the domain, not the plumbing.** The medical build's free tier limits
  *which specialist* you reach, not whether voice works (zjwj21wzs4U) — quota as
  product surface, not as infrastructure throttle.
