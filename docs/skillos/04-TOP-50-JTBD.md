# Top 50 JTBD doors

Operator surface = these 50. Everything else is an **exon** (indexed, warehoused, witness-linked).
Count is a freeze: a 51st door is a Goal Card scope change.

Existing 15 JTBD packs (`~/rig-jtbd-packs/registry/jtbd-registry.json`) are **v0 genes** to fold in, not a second menu.
## Conservation rule

Universe U is keyed by `(kind,id)` (see Goal Card). Every key in `universe.jsonl` must appear in at least one door's `exons_via` (lane and/or explicit id). `misc` is door **J50** until a token rule promotes it. Hiding a name requires a restorable warehouse store (blob or git-commit recipe), not path+hash.

Lane totals (MCP `capabilities_outcomes`): agent-engineering 1250, code-engineering 656, revenue-gtm 653, design-ux 444, misc 416, content-publishing 312, infra-ops 230, research-intel 228, docs-knowledge 206, security-review 179, business-ops 119, data-analytics 118, media-production 100.

## Door table

| ID | Job (when Mike hires this) | Lane | v0 pack / canonical exons (not exhaustive) |
|---|---|---|---|
| J01 | Run a governed mission end-to-end | agent-engineering | iqrsqpi-v20, iqrsqpi-v11, iqrsqpi-v10, hermes-agent-harness |
| J02 | Lock the north star and catch drift | agent-engineering | north-star-lock-loop |
| J03 | Seal proof or refuse fake-done | agent-engineering | proof-loop, rig-proof-gates, proofpacket_seal |
| J04 | Take an outward action under Gate-D | agent-engineering | gate-d-loop, git-push-safety-loop |
| J05 | Route intent to the right capability | agent-engineering | capabilities_route, context_pack, rig-lattice-system |
| J06 | Raise the weakest capability | agent-engineering | skill-upgrades, capabilities-round, evaluator-forge-from-exemplars |
| J07 | Plant-failure certify a gate | agent-engineering | adversarial-verification-loop, capabilities-certify |
| J08 | Compose a job from exons (this OS) | agent-engineering | skillos (this folder), rig-agent-team |
| J09 | Review a code change | code-engineering | hA-01, review, differential-review, code-review |
| J10 | Debug with evidence | code-engineering | hA-04, diagnosing-bugs, debug-like-expert |
| J11 | Refactor without behavior change | code-engineering | hA-02, tac-one-pattern-per-pass, codex-refactor-migration-engineer |
| J12 | Write tests red-green | code-engineering | hA-03, tdd, test |
| J13 | Migrate or upgrade deps | code-engineering | hA-05, hA-07 |
| J14 | Ship (commit / PR / closeout) | code-engineering | hA-08, jake-ship, specops closeout, git-push-safety-loop |
| J15 | Score and prioritize leads | revenue-gtm | hermes-go-to-market, rig-gtm-operations, darius |
| J16 | Draft outbound and keep it dormant | revenue-gtm | hD-01, darius-outbound, darius-daily-outreach |
| J17 | Produce a competitive intel packet | revenue-gtm | hD-10, rig-competitor-market-intel |
| J18 | Research an ICP / account | revenue-gtm | hD-02, rig-gtm-intel |
| J19 | Prepare a launch | revenue-gtm | hD-05 |
| J20 | Clean pipeline / CRM | revenue-gtm | hD-03, rig-crm |
| J21 | Draft a LinkedIn post | content-publishing | hB-04, ralph, alfred-content-drafter, rig-yara-short-form |
| J22 | Write long-form | content-publishing | hB-01, hB-02, rig-marcus-long-form |
| J23 | Repurpose one asset to many | content-publishing | rig-repurpose-engine, rig-daily-repurpose |
| J24 | Run the content calendar | content-publishing | alfred-content-planning-cron, ralph-postiz-pipeline |
| J25 | Reply to comments inside SLA | content-publishing | alfred-comment-engagement, ralph-linkedin-comment-reply-cron |
| J26 | Design a product or marketing surface | design-ux | hC-02, hB-03, frontend-design, design-taste-frontend |
| J27 | Audit accessibility | design-ux | hC-06, accessibility |
| J28 | Extract or govern a design system | design-ux | hC-01, hC-05, extract-design |
| J29 | Generate a brand-faithful image | design-ux | rig-image-atelier, higgsfield-* |
| J30 | Make a video / motion piece | media-production | hyperframes, product-launch-video, faceless-explainer, motion-graphics |
| J31 | Caption or overlay existing footage | media-production | embedded-captions, talking-head-recut |
| J32 | Run the film-studio pipeline | media-production | rig-film-studio, higgsfield-generate |
| J33 | Research from primary sources | research-intel | research, agent-reach, hermes-research-scout |
| J34 | Scrape and ingest substrate | research-intel | scrapers, rig-dept-substrate-intake, rig-knowledge-ingestion |
| J35 | Produce the daily intel brief | research-intel | briefing, jake-governor-daily-brief, rig-daily-scraper |
| J36 | Distill video/docs into doctrine | research-intel | rig-video-doctrine-pipeline, rig-corpus-distillation-pipeline |
| J37 | Search the knowledge brain | docs-knowledge | rig-gbrain-substrate, rig-knowledge-stack, obsidian-vault |
| J38 | Write agent-facing docs / skills | docs-knowledge | writing-for-agents, create-skill, skill-creator, find-skills |
| J39 | Capture founder knowledge | docs-knowledge | rig-content-interview-pipeline |
| J40 | Security-review a change | security-review | hA-13, security-review, codeql, semgrep, sarif-parsing |
| J41 | Threat-model a system | security-review | security-threat-model, threat-mitigation-mapping |
| J42 | Guard secrets and dangerous commands | security-review | guard-dangerous-commands, guard-secret-write |
| J43 | Query CRM / analytics truthfully | data-analytics | rig-darius-data-analysis, nadia-data, rig-honest-scoring |
| J44 | Keep the evidence ledger honest | data-analytics | evidence-retrieval-citations-gate, experience-lesson-records |
| J45 | Check fleet / node health | infra-ops | rig-fleet-diagnostics, rig-control-plane-ops, rig-terminal-service-monitor |
| J46 | Heal or diagnose crons | infra-ops | jake-self-healing-monitor, rig-cron-diagnostics |
| J47 | Deploy infrastructure with Gate-D | infra-ops | hA-11, wrangler, use-railway, cloudflare |
| J48 | Plan the day / calendar physics | business-ops | jake-calendar-os, orchard |
| J49 | Finance / ops / recruiting packet | business-ops | eleanor-finance, madison-recruiting, daphne-avis |
| J50 | Catch-all / misc until promoted | misc | any id currently in `misc`; promotion = taxonomy token + move off J50 |

## How "don't lose capability" is encoded

- **Forward witness**: door → skill. A fixture in `docs/skillos/witness/<Jxx>/<skill-id>.json` runs `rig-capabilities test <id>` or a door-level done-test that must invoke that exon.
- **Reverse witness**: skill → door. Frontmatter `outcome` / lane plus an explicit `doors: [Jxx]` (added at v8). Missing `doors` on canonical assets is a witness compiler warning; missing on *all* sources is a v11 blocker.
- **Warehouse**: if a name leaves the operator menu, `examples/` + content hash stay. Restore command is part of the receipt.
- **J50** exists so `misc` (416 assets) is not silently dropped. The v20 pressure is to *empty* J50 by promoting tokens, not by deleting files.

## Fold the 15 packs

| Pack | Lands in |
|---|---|
| claude-codex-coding-os | J09–J14 |
| claude-rig-app-studio | J26 + J14 |
| claude-strategy-studio | (strategy is a *mode* on J01/J17/J18 — not a 51st door) |
| hermes-agent-harness | J01, J05 |
| hermes-design-os | J26–J29 |
| hermes-fleet-model-ops | J45–J47 |
| hermes-go-to-market | J15–J20 |
| hermes-linkedin | J21, J25 |
| hermes-research-scout | J33–J36 |
| codex-agentforge | J08 |
| codex-build-studio | J14 |
| codex-refactor-migration-engineer | J11, J13 |
| codex-repo-cartographer | J37 |
| codex-verification-lab | J03, J07, J12 |
| codex-workflow-forge | J01, J08 |

Strategy Studio is **not** door 51. It is BMS A4 overlay on research/mission doors.

## Menu freeze test

```
python3 -c "import pathlib,re; t=pathlib.Path('docs/skillos/04-TOP-50-JTBD.md').read_text();
ids=re.findall(r'^\| (J\d+) \|', t, re.M); assert ids==[f'J{i:02d}' for i in range(1,51)], ids; print('50 DOORS')"
```
