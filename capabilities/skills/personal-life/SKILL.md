---
name: personal-life
description: "Mike's personal life, not RIG work: family and gifts, purchases, health and insurance paperwork, benefits, legal lookups, scam checks, documents and forms, personal email and calendar. Use for anything personal, household or family."
done_when:
  - grep:capabilities/skills/personal-life/SKILL.md:Never print passwords, card numbers or account numbers
  - grep:capabilities/skills/personal-life/SKILL.md:Family and health details never go to hosted models
---

# personal-life

Full map of children with paths: `LAYERS.md` next to this file. Owner: Jake directly (no agent).

## Route

| Task | Skill |
|---|---|
| Gifts, purchases, paperwork, insurance and benefits, legal lookups, scam checks, forms | `personal-admin` |
| Which personal tool to use (Gmail, Notion, docs, calendar, productivity) | `when-using-personal-tools` |
| Email, docs, PDFs, passwords, texts | builtin `google-gmail`, `google-docs`, `pdf`, `password-manager`, `imessage` |

Open slots, no skill yet, ask Mike before building one: fitness and training (his first priority), and James (words of affirmation).

## Rules

- Before buying, signing or writing as Mike, read `users/mike-rodgers-actions.md`, `users/mike-rodgers-dossier.md` and `users/mike-rodgers-voice.md` in memory.
- Committing actions (placing an order, signing, paying) get a one-line confirmation with the exact values first.
- Never print passwords, card numbers or account numbers.
- Family and health details never go to hosted models; the skill router keeps them on local OpenJev.

## Done-test

Every committing action in the transcript is preceded by Mike's confirmation of the exact values.
