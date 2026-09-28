# Calling linkedin-viral from every agent

**Canonical source (edit here only):**
- `~/Developer/rig-capabilities/capabilities/skills/linkedin-viral/`
- `~/Developer/rig-capabilities/capabilities/skills/tommy-clark-doctrine/`

Installed copies are distribution targets. Never edit them; edit canonical and reinstall.

## Where it is installed (verified by checksum on 2026-09-27)

| Agent | Skill folder | Slash command |
|---|---|---|
| Claude Code | `~/.claude/skills/linkedin-viral/` | `~/.claude/commands/linkedin-viral.md` → `/linkedin-viral` |
| Codex | `~/.codex/skills/linkedin-viral/` | `~/.codex/prompts/linkedin-viral.md` → `/prompts:linkedin-viral`; `~/.codex/commands/linkedin-viral.md` |
| Hermes | `~/.hermes/skills/linkedin-viral/` | `~/.hermes/commands/linkedin-viral.md` → `/linkedin-viral` |
| Desktop Commander / agents | `~/.agents/skills/linkedin-viral/` | `~/.agents/commands/linkedin-viral.md` |
| OMP | `~/.rig/universal-skills-registry/skills/linkedin-viral/` | `~/.omp/agent/commands/linkedin-viral.md` → `/linkedin-viral` |
| Prime Agent | `~/.prime/agent/skills/linkedin-viral/` | loads as a skill |
| Aside | `~/.aside/u/0/skills/user/linkedin-viral/` | loads as an account skill |
| Eden | Eden Settings → Skills → `linkedin-viral` (imported from `eden/linkedin-viral-eden.md`) | `/linkedin-viral` in Eden chat |

The child `tommy-clark-doctrine` and the 12 stage skills (`lv-strategy`, `lv-plan`, `lv-hooks`, `lv-draft`, `lv-visuals`, `lv-gate`, `lv-launch`, `lv-engage`, `lv-outreach`, `lv-profile`, `lv-measure`, `lv-distribute`) are installed beside it in the same seven skill folders, plus the 10 creator doctrine skills `lv-creator-*` (added 2026-09-28: lara-acosta, diandra-escobar, will-mctighe, harry-long, kasey-brown, mark-firth, pierre-herubel, raise-your-visibility-online, shanee-moret, michelle-j-raymond). OMP loads them via the `lv-*` glob in includeSkills (`~/.omp/agent/config.yml`, backed up 2026-09-28). The universal command source is `~/.rig/universal-commands/linkedin-viral.md`.

## Update procedure

1. Edit the canonical files.
2. Run the gates from `~/Developer/rig-capabilities`:
   - `python3 capabilities/skills/linkedin-viral/scripts/check_routes.py` (GREEN)
   - `python3 capabilities/skills/linkedin-viral/scripts/check_routes.py capabilities/skills/linkedin-viral/SKILL.md --min 20` (GREEN)
   - `python3 capabilities/skills/linkedin-viral/scripts/check_ledger.py --all` (GREEN: every stage accounts for every asset assigned to it)
   - `python3 capabilities/skills/tommy-clark-doctrine/scripts/check_no_verbatim.py` (GREEN)
   - `python3 capabilities/skills/tommy-clark-doctrine/scripts/check_no_verbatim.py capabilities/skills/linkedin-viral --no-index` (GREEN)
   - `python3 capabilities/skills/linkedin-viral/scripts/check_routes.py --self-test` and `python3 capabilities/skills/tommy-clark-doctrine/scripts/check_no_verbatim.py --self-test` (both GREEN: each proves its gate still goes RED on a planted failure)
3. Reinstall each changed skill: `./bin/rig-capabilities install <id> --harness <h> --kind skill --force` for h in claude, codex, hermes, agents, omp, prime-agent, aside. Old copies go to a hidden `.rig-backups/` folder beside the target, so they never load as duplicates.
4. Verify by checksum: every installed `SKILL.md` must match the canonical sha256.
5. Eden: import the updated `eden/linkedin-viral-eden.md` text as a skill. Eden keeps both copies on a name collision (the new one gets a `-2` suffix), so delete the older one in Eden Settings → Skills after the new one is confirmed.
6. When a LinkedIn skill is added, renamed or retired anywhere: add its row to `references/stage-map.json` (stage + role), fold its unique content into that stage and add its ledger row, run `python3 scripts/build_routing.py`, then rerun step 2.

## Why the Eden edition is a separate file

Eden imports one markdown file per skill (no bundled references over MCP), and it cannot read local paths. So the Eden edition carries the playbook itself: lane guard, non-negotiables, the post recipe, hook levers, formats, the week, post-launch, flop diagnosis, weekly review, and the hand-back format. It is named `linkedin-viral-eden.md` rather than `SKILL.md` so harnesses that scan folders recursively (Hermes) never register it as a duplicate skill.
