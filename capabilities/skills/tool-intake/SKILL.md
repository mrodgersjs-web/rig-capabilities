---
name: tool-intake
description: "Adopt an outside tool, repo, app or model safely: check what already exists, evaluate license and upkeep, install where it can actually run, wire it only into the harnesses Mike named, and prove it works with a check that can fail. Use for 'clone and install this', 'set this up for aside and omp', 'install X on the 96GB', a new GitHub repo, or a new desktop app."
---

# tool-intake

1. **Existing first.** Search before installing: `skill-surface find "<what it does>"`, `~/.rig/bin/skill-index search "<what>"`, the rig-capabilities `capabilities_search`, `~/Developer`, `/Applications`. If something already covers it, say so and stop: Mike rejects duplicates.
2. **Evaluate in one line.** `PROPOSE <tool>: fit <why> | risk <what could break> | runs on <machine> | done-test <command that can go red>`. Check license, last push, what it needs (native binaries, Docker, GPU, ports) and which machine should run it (this Mac, 96GB, 256GB, Blackwell, NAS).
3. **Install where it can run.** The Aside sandbox blocks unsigned native binaries, launchd registration and process listing. Use an Orca host terminal (see `rig-ops`) or the target machine over SSH. Install into `~/Developer/<tool>` or the tool's own channel, never inside a live skill root. For JS workspaces use `--ignore-workspace` so `~/pnpm-workspace.yaml` does not capture the install.
4. **Wire only what was asked.** Add it to the harnesses Mike named. A new skill is filed with `skill-surface file <name> --meta <meta> [--parent <skill>]`, never dropped at the top level.
5. **Prove it.** Run its smoke test, plant one failure and show the check go red, restore, show green (the `meta-install-verifier` pattern). Record the checksum of anything you planted into before and after, so a plant that never landed is caught.
6. **Report.** Where it lives, every side effect (lockfiles, launch agents, ports, disk), and the exact command that removes it.

## Gates

- Paid plans, public endpoints and new credentials stop at Gate-D.
- An unintended side effect is disclosed in the same report with its revert.

## Done-test

The report contains a smoke command and a planted failure that went red, both run in the same session, plus the removal command.
