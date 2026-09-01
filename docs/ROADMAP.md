# rig-capabilities ROADMAP — V1 through V30

Evidence table. Packet hashes are `sha256:` prefixes from sealed ProofPackets.
`—` means no packet was sealed for that increment (pre-packet era or known FALSE later superseded).

V28 zip is **DORMANT**. Tag/GitHub Release waits typed `APPROVE gd_1788227314643`.

## Ladder

| V | commit | packet (sha256 prefix) | what shipped | proof |
|---|---|---|---|---|
| 1 | — | — | catalog + MCP surface | VERSION_LADDER |
| 2 | — | — | catalog + MCP + 4-tier context fabric | VERSION_LADDER |
| 3 | — | — | drift auto-refresh + observation-decay + ACL | VERSION_LADDER |
| 4 | — | — | local federation + ratings→trust | VERSION_LADDER |
| 5 | `277df8d` | — | signed packs + public catalog + analytics | commit |
| 6 | `36a995c` | — | org-IdP HMAC + Bearer serve | commit |
| 7 | `5cc62f1` | — | skill quality contract | commit |
| 8 | `a2278b6` | — | /skill-upgrades in 5 harnesses | commit |
| 9 | `b2294e4` then `f484f29` | FALSE `b2294e4` superseded TRUE `a72d8c0a` | frontier corpus; v2 re-researched from primary sources | packet |
| 10 | `9645aae` | — | great-examples + reference injection | commit |
| 11 | `6d37ce6` | — | misc overlay 898→298 | commit |
| 12 | `aca04e7` | — | coverage matrix + agent packs + requests | commit |
| 13 | `ef50ab4` | — | session boot pack + hook frontmatter | commit |
| 14 | `9cdc1d5` | — | Supabase schema + db-sync | commit |
| 15 | `5b62282` | `7b9c8cd5` | runnable done-tests | packet TRUE |
| 16 | `6def2c2` | `db4e83b1` | 1000x round, graduate-on-green | packet TRUE |
| 17 | `975fa1e` | `5c88e805` | scraper-corpus intel | packet TRUE |
| 18 | `077a27b` | `d86c56bc` | live HTTP federation | packet TRUE |
| 19 | `b57427e` | `d4a9a8ee` | LLM concept overlay honest tiers | packet TRUE |
| 20 | `f24be8f` | `1e751026` | verified requesters | packet TRUE |
| Wave2 | — | `b179c4df` | six probes green (psql 4687, semgrep, round dry, federation, concepts, MCP pack) | packet TRUE |
| 21 | `77a13e8` | `a2517abe` | /stats.json + /dashboard | packet TRUE; live 4687 assets |
| 22 | `abab726` | `162ca8cc` | certify + plant-failure 5/5 | packet TRUE; plant caught tautological semgrep grep |
| 23 | `b5f22c3` | `fc6088e3` | agent packs + boot + pack-first context | packet TRUE; darius-gtm 5/5 ready |
| 24 | `0612377` | `7b96bb33` | 6 canonical commands + certify MCP + installer delivery | packet TRUE; quality_run hang fixed (mutating mcp re-entry) |
| 25 | `e2b303f` | `f4973c98` | OMP+Prime hook roots; live-on-presence | packet TRUE; verify hooks 6 |
| 26 | `b417015` | `f64b7245` | 8 gap harness drafts | packet TRUE; last-row-wins |
| 27 | `5918f0e` | `bf0b1edb` | traces panel aggregates, no payloads | packet TRUE; live traces 3 |
| 28 | `ff83a6f` | `4ee229eb` | public zip **builder**; zip armed=false | packet TRUE; publish blocked on `APPROVE gd_1788227314643` |
| 29 | `6fd4502` | `77169382` | Layer-Isolated certify in suite | packet TRUE |
| 30 | this file | (this increment) | ROADMAP + proof-chain | see below |

## V30 proof-chain check

Commands that must stay green on `main`:

```
python3 -m unittest tests.test_catalog
export CONFIG_GUARD_ALLOW=true; ./install.sh --verify
python3 -c "from rig_capabilities.catalog import Repo; from rig_capabilities.certify import run_gates; from rig_capabilities.certify import GATES; r=run_gates(Repo('.'), only=[k for k in GATES if k!='suite']); print({k:v['ok'] for k,v in r.items()})"
```

Open:

- LLM overlay 62/300 (background build died early; `concepts-build --llm --n 300` is checkpointed).
- Public ACL catalog count=1. Zip is honest about that.
- V28 GitHub Release / git tag: **not done**. Type `APPROVE gd_1788227314643`.
- Blanket "approve all gate d" does **not** arm unrelated pending items (TestFlight, Blackwell reboot, cancel-13-subs, Vercel prod).

## Plant-failure doctrine (earned)

1. V22: `grep:...:Semgrep` was self-referential (frontmatter carried the pattern). Rewired to `file:.../run-scans.sh`.
2. V24: `mcp:capabilities_certify` inside done_when re-entered `quality_run` (400s hang). Mutating MCP skipped; reentrancy guard.
3. V28: a zip that includes `.signing.key` fails PublicZipTests.
