---
name: tg-ai-media-pipeline
description: >
  Sub-skill of tg-durable-ai-pipelines: the media-generation steps of the
  TubeGuruji corpus — script/LLM steps with JSON-spec prompts, TTS and voice cost
  paths, captions, image generation and URL-param transforms (ImageKit),
  Remotion/AWS rendering, two-stage config-first generation, and primary/backup
  model wiring.
tags: [rig, doctrine, media, imagekit, remotion, tts, tubeguruji]
metadata:
  source: "corpus — UgLN9O930vE (JSON-spec prompts + model constant), c9qA-uhysIY (two-stage config pipeline), O_f55bWzsik (primary/backup models, ngrok webhooks), PdVSn-w419g + lJbIs8_5aqU + WmWJNSxCiZc (ImageKit transforms), ciXiibK7Gds (Remotion AWS free render, Gemini free credits), kxM_oEMn3IM (voice cost paths), -h1O73T0jmo / 31-Qfr2Pc5Q (chain shape), 1DXV4LCWkic + 2FYlidDpFSo (Stripe cents)"
  extracted: "2026-09-25"
  parent: tg-durable-ai-pipelines
outcome: "Media generation steps that are cheap by design (free tiers, config-first regeneration, URL-param transforms) with fallback model wiring and correct money math."
activation: "Load when implementing any generation step: text/script, TTS/voice, captions, images, video composition, slides — or when generation costs or regenerations need to be cut."
instruction: >
  Pick each step's vendor by free tier first, wire a fallback model where the step
  can fail, generate structure before content (config first, render second) so
  theme/style changes never re-call the model, and do image work through
  URL-parameter transforms instead of ML code.
applies_when:
  env: "Next.js app with durable pipeline wired (tg-durable-ai-pipelines)"
  runtime: "serverless functions calling provider APIs; browser-side composition where applicable"
  deps: "Gemini/OpenRouter (text), Murf/Replicate/Deepgram (voice), ImageKit (images), Remotion (render), Stripe/PayPal (credits)"
  params: "JSON output specs in prompts; model names hoisted to constants; bucket sizes for credits"
  budget: "demo cost target ~zero (free tiers); hosted voice cloning <$1 per 45 min is the first paid line item (kxM_oEMn3IM)"
  scale: "single-product media app; hundreds of generations/day on free tiers"
permissions:
  - fs.read
  - fs.write
  - bash
  - net.api-calls
  - gate-d-required:purchase
flow:
  - Script/LLM steps: hoist the model name into a constant; write prompts that demand a JSON spec (three variants, each name + emoji + two-line description, UgLN9O930vE); render from the parsed JSON, never from raw text.
  - Generate structure first, then content: produce a screen/slide CONFIG, render from config, and apply theme swaps to the config without re-calling the model (c9qA-uhysIY two-stage pipeline; theme swap without regeneration).
  - Voice: choose by cost path — free default voice (Deepgram), hosted cloning <$1/45min via Replicate Chatterbox, or self-host that still pays cloud (kxM_oEMn3IM: "better use third party who already deployed it").
  - Images: generate or transform via ImageKit URL params — background removal, upscale, smart crop, shadow — zero ML code (PdVSn-w419g, lJbIs8_5aqU, WmWJNSxCiZc).
  - Video: compose with Remotion; render on the free AWS tier (ciXiibK7Gds).
  - Wire a fallback model per fallible step (Luma primary + optional Gemini backup, O_f55bWzsik).
  - Money math: Stripe amounts are cents — multiply by 100 or the charge is wrong (1DXV4LCWkic, 2FYlidDpFSo); local webhook testing needs ngrok and demo credits get seeded manually (O_f55bWzsik).
done_when:
  - "grep:capabilities/skills/tg-ai-media-pipeline/SKILL.md:config"
  - "grep:capabilities/skills/tg-ai-media-pipeline/SKILL.md:ImageKit"
  - "grep:data/corpora/how-to/manifest.jsonl:c9qA-uhysIY"
out_of_scope:
  - training/fine-tuning models; self-hosting GPU inference
  - the pipeline engine itself (tg-durable-ai-pipelines)
  - paid media API purchases without Gate-D
quality_floor: "A generation step is RED if a theme/style change re-calls the model, or if a provider failure has no fallback path."
---

# AI Media Pipeline Steps

## Prompt-to-JSON contract (the corpus' LLM step shape)

Model name as a shared constant; prompt demands JSON; UI renders the parsed spec.
Concrete surviving example: a recipe prompt requiring exactly three variants, each
with `name` + `emoji` + two-line description (UgLN9O930vE). Forms build on the same
shape: prompt → form schema JSON → editable form (s28yOCBVgGw). Mutating parsed JSON
requires a re-render trigger — bump a timestamp state via `useEffect` or the label
changes without the UI (s28yOCBVgGw).

## Two-stage generation (the cost-saving pattern absent from one-shot builds)

Generate the screen/slide **config** first, then render each screen from config
(c9qA-uhysIY). Consequences: theme changes apply to existing configs **without
regenerating**; per-screen regeneration by prompt; PNG export. The same
component-not-page rule shows up in AI UI editing: "make the changes to a specific
component instead of regenerating the complete page" (tJmN2XduBVk).

## Fallback model wiring

Primary + backup declared in code, not hoped for: "uses Luma AI UniOne… if it fails
for some reason, I also implemented a Gemini… but it's completely optional"
(O_f55bWzsik). Route LLM fan-outs through OpenRouter when users pick models
(fOtjNm3JoAE); one export gotcha: the OpenAI client must be exported from a util
file, not directly from the router (sXRDL-EPtrM).

## Images without ML code

All "AI image transformation" in the print-on-demand build is ImageKit URL query
params — background removal, upscale, smart crop, drop shadow (PdVSn-w419g). The
same service covers AI image generation with prompt params in the PPT generator and
the Shopify theme builder (lJbIs8_5aqU, WmWJNSxCiZc). Uploads with progress go to
S3 (-h1O73T0jmo).

## Voice: three cost paths, stated on camera

1. Free default voice (Deepgram) — zero cost.
2. Hosted voice cloning — Chatterbox via Replicate, "<$1 per 45 min".
3. Self-hosted — still pays for the cloud, so "better use third party who already
   deployed it" (kxM_oEMn3IM).

## Rendering and money

Remotion composes programmatic video; the corpus renders on the free AWS tier and
selects Gemini as the LLM explicitly because of free daily credits (ciXiibK7Gds).
Money math gotcha taught twice: Stripe amounts multiply by 100 (cents) or the
stored total is wrong — the demo shows an "8 cent" residue on $88.58
(1DXV4LCWkic, 2FYlidDpFSo). Order confirmation emails carry the download link
(React Email + Resend, sVYNEqlx3Nc; template reuse across apps, Dsw0pMnblWg).
