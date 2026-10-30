# Sub-skill: angle engine (run before every issue)

A topic is not an angle. This pipeline turns a topic into one angle with a named mechanism, then checks the draft is not generic. Every step writes its output into the issue folder so the grade can be traced.

## 1. Social analysis (Eden, read-only; research costs Eden credits, keep it to 2-3 calls)
- `eden_study_top_titles` with `platform: "substack"` on the niche (AI operations, SMB automation, governed AI). Keep the headline SKELETONS; never reuse a source's own numbers, names or story (`doNotReuse`).
- `eden_search_social_content` on the topic, `orderBy: "relevance"`, to see what angle is already saturated. Errors are not zero results.
- Output: `social.md` with 3 working title skeletons and the 2 saturated angles to avoid.

## 2. Collision (angle candidates)
- `python3 ~/Developer/rig-jtbd-packs/linkedin-studio-v2/engine/collision/collision_engine.py generate -n 3` for artifact x veteran x skeleton specs, or pick a type with `--type`.
- The engine was built for the personal-brand lane and its PREACH floor bans naming AI. For RIG B2B issues use the collision for the hook and the opening scene only; the body may name AI and must carry receipts.
- Output: `angles.md` with 3 candidates, each with its BlendValue.

## 3. Creativity gates (V3.1 Master Creativity Function)
- `~/Developer/rig-capabilities/capabilities/skills/rig-lattice-system/bin/rig-lattice idea score --title <angle> --content <one-paragraph pitch> --claims <n> --json` per candidate. The score rewards declared sources, claims and mechanisms; a bare pitch is rejected, so write the real receipt into the pitch.
- Keep `accept`, rework `revise` once, drop `reject`. Output the verdicts into `angles.md`.
- Jev `idea.solid` on the surviving card as a second opinion; DEFERRED if the classifier is down.

## 4. After drafting: deviation audit + Jev grade
- `rig-lattice audit <draft> --json`: physics-gate HARD_BLOCK stops the draft; any engine below threshold gets a patch or a named reason.
- `rig-s1gate check substack.issue --file <draft> --subject "substack-issue <date> sha256:<hash>" --json`; on ESCALATE, `rig-s1gate improve substack.issue --file <draft> --max 3` and re-grade once.
- Record every decision id in `gate.json`. Advisory: a PASS is not permission to publish.
