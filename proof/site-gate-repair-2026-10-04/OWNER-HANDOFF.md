# Owner-safe migration handoff

Canonical source repairs are saved in `capabilities/skills/jev-site-gate` and `client-mirror-site`. The live production gate was not changed. Its current writer remains Aside mission `QC6DdpCd7rfnfiru` in `/Users/rig128gb/Developer/rig-client-mirror-sites`.

## Verified repair

- Existing canonical design router restored through `capability_install` for Codex and `Repo.install(..., 'aside', force=True)` for Aside. Authoring, canonical, Codex and Aside SKILL.md SHA-256 are all `9367dc675d8b34ca901df23ca6e27335d082230b1a2786da95055181a32fd7a9`.
- `distribution-receipt.json` proves actual hash parity/canonical resolution, detects the stale reciprocal route, verifies the current route lacks it, and tests the proposed scoped sync patch plus same-size/same-mtime drift in isolated fixtures.
- Gate source rejects unsupported client/source identity, empty or unrelated Miro phases, fake/stale capture evidence, pointer-only 3D, confounded scroll/pointer states, missing reduced-motion/mobile/CTA behavior, copied Lighthouse scores, malformed images and unsupported/self-authored review.
- Same-client distinct offerings are supported; RIG-brand entries and exact renamed/duplicate mechanisms or identical build bytes cannot inflate the count. Semantic novelty still needs independent review.
- Fresh runs invalidate previous PASS. A failed authorized Airtable recheck clears Done=false. Repairs themselves performed no provider writes.

## Canonical versus runtime

The production `_tools/gate.py` was last observed at SHA-256 `1a84261f66921226d877def40733ecb22738e6c4087ee1faf63ff36507ac5ed8`, the original weak gate. Do not report v2 runtime enforcement or accept sites through that old result as if it used this repair. The independent source/motion replay receipts do not certify client captures.

The existing production owner should first read the canonical SKILL.md files, `jev-site-gate/references/EVIDENCE-V2.md`, `criteria.v2.json`, the changed client PROBE/process/builder brief, and the final ProofPacket. Preserve its working tree, site folders and active worker lease. Review the exact canonical hashes before applying any migration.

When the owner is ready for a coordinated migration, the concrete runtime file set is:

| Canonical source | Runtime destination under the owner's tree |
| --- | --- |
| `jev-site-gate/scripts/gate.py` | `_tools/gate.py` |
| `jev-site-gate/scripts/evidence_contract.py` | `_tools/evidence_contract.py` |
| `jev-site-gate/scripts/jev.py` | `_tools/jev.py` |
| `jev-site-gate/references/EVIDENCE-V2.md` | `_tools/EVIDENCE-V2.md` with owner-reviewed local links |
| `jev-site-gate/references/criteria.v2.json` | `_gate/criteria.v2.json` |
| `client-mirror-site/references/PROBE.md` | existing runtime PROBE.md, with owner-reviewed local links |
| `client-mirror-site/references/DESIGN-PROCESS.md` | existing runtime DESIGN-PROCESS.md, with owner-reviewed local links |
| `client-mirror-site/references/BUILDER-BRIEF.md` | existing runtime builder brief, with owner-reviewed local links |

Retain a scoped pre-migration snapshot and hashes; do not delete other workers' changes. Rerun the current actual gate tests and the independent reviewer against the applied runtime bytes, and compare hashes. An alternate read-only check can invoke the canonical gate with `--root` pointing at the production workspace without replacing its files. Do not pass `--airtable-record` until the actual update is authorized and acceptance is proven.

## Trust and certification remain blocked

`TRUSTED_VERIFIERS` is deliberately empty. The script cannot certify any production site. An arbitrary `--verifier-key` argument, copied key or newly generated signer has no authority. No permanent signing credential or trust root was created, installed or enrolled. Desktop package-signing and retired Orca keys were only found by filename and were not read or borrowed.

The operator must identify an **existing authorized website-QA verifier trust root** and review the required binding of public-key hash to verifier id/family before enabling acceptance. Keep raw actual independent browser/source/Miro/Lighthouse evidence and label it unsealed/pending until that requirement is met. This handoff does not authorize fresh trust enrollment, signer creation, credential changes, source spend, deployment, publishing or provider writes.

Further required promotion work: source-hash-bound held-out skill outcomes (at least 30 tasks, above 0.90, zero hard-block failures), independently captured actual client QA, different-family GEV and applicable build certification. The synthetic behavioral tests are not these outcomes. The OpenSpec change validates with the existing pinned CLI, but the BDD wrapper fails because schema `behavior-driven` is absent. The zone guard reports pre-existing mixed spec/code changes. No clean-zone or D85 certification claim is made.

## Design authoring owner

`rig-repo-guard` blocks `/Users/rig128gb/Developer/rig-design-studio-os/tools/sync_to_capabilities.py` and its studio-skills authoring subrepository as unregistered writable roots. The exact patch is `design-sync.patch`. It adds Codex distribution and `--only design-studio-os` without installing unrelated skills/agents/harnesses, and deep byte drift checks. `git apply --check` against the real owner passed; a temporary fixture tested its actual behavior. The owner file itself remains unchanged. Apply only after that authoring source has an authorized repository-placement path; this worker does not alter registration.

No production gate propagation, client acceptance, public action, new trust enrollment, branch, commit or push was performed. The bounded source repair and existing-router restoration can be reviewed now; promotion remains blocked by the listed evidence requirements.
