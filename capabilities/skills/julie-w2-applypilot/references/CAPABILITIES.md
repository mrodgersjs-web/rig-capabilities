# Required and supporting capabilities

Everything below is local; no new paid subscription or plugin installation is required merely to load this workflow.

| Capability | Existing surface | Use and verification boundary |
|---|---|---|
| Hermes operator | `hermes` with local `--rig-task` wrapper; `chat --oneshot -Q --provider rig-blackwell-qwen38-flash --model blackwell-qwen38-flash --query-file … --run-budget 180 --max-turns 10` verified in the installed parser | Use only the bounded supervised-Flash preflight from `START-HERE.md`. It is not a full application dispatch. Top-level `--oneshot` is prohibited because it enables bypass mode. No `--yolo`, `--ignore-rules` or imaginary tools required. |
| Browser | `~/.hermes/skills/ego-browser/SKILL.md` resolves to installed Ego framework; `ego-browser nodejs` | All live browser work; actual identity, taskspace and receipt evidence. |
| ApplyPilot | `~/.local/bin/applypilot`; `~/.applypilot` | Existing queue, packets and discovery data. Stock `applypilot apply` is not an Ego adapter and is not used here. |
| Julie reference | `~/.hermes/skills/julie-job-search/SKILL.md` | Existing job-search  conventions. Its scripts are draft-only; do not claim they submit. Use current canonical repo and counts. |
| Packet builder | `~/.hermes/skills/application-packet-builder/SKILL.md` | Dossier, objections, interview Q&A and concise cover letter. Verify actual JD; do not treat inferred requirements as verified. |
| Cockpit reference | `~/.hermes/skills/rig-job-cockpit/SKILL.md` | Data and UI context. Old Desktop paths and packet counts are stale; current root is `~/Developer/rig-linkedin-studio-luca`. |
| Documents | Python ZIP/XML; available document render/extraction tools | Preserve DOCX styles/history; inspect PDF/pages/text and bind review to actual bytes. Formatting proof is not ATS ranking proof. |
| Mail and LinkedIn | Signed-in Ego Gmail/LinkedIn | Check actual account identity; reconcile receipts/outcomes; authorized individual outreach. No Gmail plugin dependency. |
| Credentials | macOS Keychain `security`; approved job-account entry | Read only when required, in memory, send only to intended provider. Never print or copy secrets into prompts/proofs. |
| Models | `blackwell-qwen38-flash` supervised route from `~/.applypilot/model-routing-policy.json`, Hermes parser, shared model registry | Bounded `chat --oneshot -Q` extraction/preflight only; independent review is required. Unreliable uncensored routes are quarantined and cannot write a document, answer, message, form or ledger. Inventory/config is not a successful inference probe. |
| Delegation | Hermes's actually advertised delegation/terminal tools | At most three workers; one account/session owner; persistent output verification. Sequential fallback if delegation is unavailable. |
| Memory | `~/.hermes/skills/rig-memory-os/SKILL.md`, Obsidian memory bridge | Bounded retrieval, canonical sanitized writes; no fabricated memory or budget resets. |
| Capability registry | existing `rig-capabilities` MCP/CLI | This package is canonical, then installed to Hermes; no duplicate hand-written skill trees. |
| Traject | `~/Developer/rig-linkedin-studio-luca/cockpit-v2`; local port 3101 | Progress display and interview tooling. Full autonomous application execution is still unproven. |

Use the currently verified supervised Flash model ID from `~/.applypilot/model-routing-policy.json`; this version selects `blackwell-qwen38-flash` for the compact preflight. Do not substitute configured uncensored routes, paid plans, or a provider inventory for a successful inference probe. Current Codex worker quota errors must not become repeated retry loops.

`ego-browser-pitfalls` is historical reference only. Its old examples include file-based invocation and automatic takeover that conflict with the current framework skill. Do not preload those conflicting examples as execution instructions.

## Bounded tool loading
The launcher explicitly selects terminal,file,skills,todo,clarify,delegation (verified in the installed Hermes toolsets.py). Ego operates through terminal; native browser and unrelated MCP toolsets are not requested. A full-default smoke test loaded the skill and passed preflight but warned about oversized global startup context. The narrowed launcher is source-validated; its full application execution is not yet proven. Do not disable global rules to suppress that warning.
