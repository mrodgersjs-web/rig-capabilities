---
name: corpus-to-skill-family
description: "The step-by-step pipeline for turning YouTube channels, courses or documents into a meta-skill with stage skills and sub-skills: screen sources with Jev, capture transcripts, distill cited laws, build focused skills, gate them, file them into the skill surface, and add routing evals. Use when Mike says scrape these creators into skills or build a meta-skill from a corpus."
---

# corpus-to-skill-family

1. **Pick sources.** List candidate channels or documents. Screen each with `~/.rig/bin/rig-s1gate check corpus.source --file <candidate card> --subject "<source> sha256:<hash>" --json` and keep the ones that pass. Weight Mike's own subscriptions higher, as the design corpus did.
2. **Capture.** Transcripts through the builtin `youtube` skill (or `scrapers` for pages). Store raw text in the project's local corpus folder, never in a public repo. Record counts: videos targeted, captured, and why the rest were not.
3. **Distill.** One file per stage. Each law is paraphrased, cited `CLAIM(<videoId>@mm:ss)`, and marked consensus or single-source. Unverified creator numbers and dated tool tips go in their own sections.
4. **Verify citations** with a different model family from the one that wrote them, before anything ships.
5. **Build.** One meta front door, 5 to 15 stage skills, sub-skills only where a stage has real parts. Each SKILL.md stays under 500 lines, states when to use it, and ends with a done-test that can go red. Doctrine lives in a references skill that stages cite.
6. **Gate.** `rig-s1gate check` on each stage skill and the `anti-slop` pass on prose. Rewrite until clean, at most three rounds, then report what is still weak.
7. **File.** Install into the canonical repo, then `skill-surface file <skill> --meta <meta> [--parent <skill>]` for every new skill and `skill-surface build`.
8. **Evaluate.** Add three routing cases per stage to `~/.aside/u/0/skill-library/_route-evals.json` and run `skill-surface eval`; it must stay at or above 0.85.

## Done-test

`skill-surface verify` is GREEN, the new eval cases pass, and the citation check from step 4 has a report on disk.
