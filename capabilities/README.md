# capabilities/

Canonical, git-versioned assets. One directory per kind:

- `skills/<id>/` — skill directory (SKILL.md + optional scripts/references)
- `agents/<id>.md|.toml|.json` — agent definitions per target harness format
- `hooks/<id>.sh|.py|.ts` — hook scripts; the settings.json wiring references the
  *installed* copy, but this is where they are edited and from where they ship
- `harnesses/<id>.yaml` — goal harnesses (hA/hB/hC/hD/mh families)
- `loops/<id>.md` — goal loops
- `commands/<id>.md` — slash commands

Rules:

1. Add via `bin/rig-capabilities add <id> --kind <kind> --path <source>` (or MCP
   `capability_add`) so the index stays fresh.
2. A canonical entry **shadows** same-named installs in `~/.claude`, `~/.codex`,
   `~/.hermes`, `~/.agents` — taking ownership is a copy here plus deleting or
   aliasing the strays.
3. Vendored OSS assets record provenance (upstream URL + license) in their
   frontmatter or a PROVENANCE.md beside them. CC-BY-SA upstreams are never
   rebranded.
4. Install with `install <id> --harness <harness>` — never hand-copy into a
   harness root, so the ledger in `.install.json` stays true.
