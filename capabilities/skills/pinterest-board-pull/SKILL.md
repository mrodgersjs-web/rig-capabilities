---
name: "pinterest-board-pull"
description: "Pull Mike's Pinterest board pins read-only via public RSS: 736x images plus index.json, ~25 latest pins per board. Use for moodboard, pin, board or design-reference pulls."
meta: "rig-design-studio"
owner: "theo-design"
done_when:
  - grep:capabilities/skills/pinterest-board-pull/SKILL.md:RSS = latest ~25 only
  - grep:capabilities/skills/pinterest-board-pull/SKILL.md:Never promise a full-board pull
  - grep:capabilities/skills/pinterest-board-pull/scripts/pull_board.py:index\.json
---

# pinterest-board-pull

Read-only. No login, no browser, no writes.

> For a **full** board, a **private** board, a **search**, or anything that feeds design or image
> generation, use `pinterest-taste-engine` instead (`/pinterest-taste-pull`, then profile, apply, judge).
> This RSS path stays for a quick latest-25 look.

## Run

```bash
python3 scripts/pull_board.py <board-slug> [outdir]
# default outdir: /Users/rig128gb/Developer/rig-client-mirror-sites/_inputs/pinterest/<board-slug>
```

Prints `<slug> <N> pins <M> images`. Writes `NN-<hash>.jpg` files and `index.json`:
`{board, user, source:"rss", count, pins:[{file, pin, image, title, text}]}`. `file: null` means the image download failed; report it, do not hide it.

## Method

- Feed: `https://www.pinterest.com/michaelrodg0511/<board>.rss` (public, any board slug from the board URL). Send a browser `User-Agent`.
- Each `<item>` carries the pin link, title and a `<description>` with an `i.pinimg.com/236x/...` thumbnail. Swap the size segment to `736x` for a usable image (`https://i.pinimg.com/736x/<path>`).
- Yield: about 25 latest pins per board. That is the feed's window, not the board size.

## Known limits (measured 2026-10-04)

- **RSS = latest ~25 only.** Older pins are not in the feed. Never promise a full-board pull.
- **The DOM grid virtualizes.** Scrolling a board 14 times still yields ~11-13 pin links; a deep read pass got 36 pins across 3 boards of 93/109/82. A full pull needs an API token or a slow per-pin walk.
- **Reads and writes throttle differently.** Writes (saving pins, board edits) hit reCAPTCHA on 2026-10-03; reads did not. A write-timeout history is not evidence a read will fail, and a working read is no permission to write.
- Writes are out of scope here. Pinterest curation with writes is `pinterest-taste-curation` and needs Mike's approval.
- Keyword-matched boards can be the wrong purpose (the `RIG | Rodgers Intelligence` board is brochure templates, ~19% fit). Open every image and judge fit before using a board as a design reference.
- Pins showing another brand's product UI are inspiration only, never shipped imagery.

## Taste corpus note

The taste corpus (`http://127.0.0.1:8472`, per-offering `corpus.jsonl`) received 281 Pinterest items on 2026-10-04 (`source:"pinterest"`, `label:"acceptable"`, `labeled_by:"agent-seed"`). Any pin added there stays provisional until Mike confirms it (`SCHEMA.md`).
