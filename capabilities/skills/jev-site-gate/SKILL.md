---
name: "jev-site-gate"
description: "Design and run a JEV acceptance gate for a website: vet criteria, CODE checks first, JEV noul >=0.85 for judgments, gate.py verdict, Airtable check-off. Use for site QA."
meta: "rig-design-studio"
owner: "theo-design"
status: "Candidate; production trust and rendered outcome verification pending"
done_when:
  - "cmd:python3 -m unittest tests.test_site_gate_evidence"
---

# jev-site-gate

A site is accepted by a script, not by an adjective. This capability owns `scripts/gate.py`, `scripts/evidence_contract.py` and `scripts/jev.py`. `client-mirror-site` delegates to this owner. Current acceptance contract: `references/EVIDENCE-V2.md`. The v1 criteria/vetting files remain historical evidence; their prose scores do not certify the strengthened v2 checks.

The production trust mapping is deliberately empty pending identification of an existing authorized QA trust root. A supplied public key or a builder-generated signature grants no authority. Test keys are temporary fixtures only. Keep the candidate unpromoted until real independent captures, different-family review, required build gates and source-bound skill outcome evaluations are attached.

## 1. Design the criteria

- Write each criterion as one observable sentence: a file, a DOM value, a count, a threshold. "Looks premium" is not a criterion; "hero height >= 50% of a 1440x900 viewport" is.
- Vet each with JEV: `aside-jev noul "Is this criterion objectively verifiable from a file or the served page?" --state "<criterion>"`. Store `{id, criterion, jev_verifiable, model}`.
- Route every criterion, first match wins (`jev-everywhere`):
  - **CODE** for signed artifact identity, decoded captures, actual Lighthouse reports, source/run chains, ordered Miro execution artifacts and observed browser interactions. Source regex and builder-written numbers are lint only.
  - **JEV** only for a bounded yes/no judgment on small state (does the headline name the buyer? is the text free of testimonials?).
  - **Vision critique** for taste: an independent reviewer reads actual screenshots and records structured findings, screenshot hashes, resolved blockers and retest artifacts. `SCORE:` prose cannot establish acceptance.
- Low verifiability is a rewrite signal, not a discard. v1 criteria scored 0.48-0.82 as prose; that is why most were turned into CODE checks over `probe.json`.

## 2. Run

```bash
python3 scripts/gate.py <slug> --root <workspace> --verifier-key <already-authorized-public-key>
python3 scripts/gate.py --portfolio <ten-or-more-slugs> --root <workspace> --verifier-key <already-authorized-public-key>
```

Reads the offering manifest and a signed independent receipt binding every consumed artifact to the exact build, served URL, session and captures. C00 rejects missing or untrusted evidence before Jev receives it. C06-C08 and C22 validate observed desktop/mobile interaction. C10-C11 parse actual mobile Lighthouse JSON. C24 validates Miro execution artifacts. C26 decodes PNGs. C27 validates independent findings. C28 validates client/source identity. C29 detects changes during verification. Every run invalidates prior PASS before reading inputs. Exit 0 only on PASS.

Portfolio mode reruns every gate, then counts at least ten distinct client-branded offerings. One client may have multiple source-supported mechanisms. Duplicate offering ids, solution ids, equivalent mechanism strings or identical build bytes cannot increase the count; semantic distinctness still requires independent review. Never infer ten different companies from ten offerings.

## 3. JEV rules (enforcement is ON)

- Threshold `JEV_MIN = 0.85`. Parse `answer.noul` (or `answer.confidence` for `choice`), never the top-level `verdict`.
- A JEV call error is a FAIL with the error recorded. Never a guessed pass, never a local substitute verdict.
- Nonzero exit, timeout, malformed answer, boolean, infinity or a score outside [0,1] is FAIL.
- A single boundary result is not stable; re-run once before opening a fix item.
- A PASS on a `never_auto` rubric is a recommendation only; it never sends, posts, spends or deploys to prod.

## 4. Airtable check-off

- `--airtable-record` PATCHes the DO · Today row (`app0aAXlSUFPbuTBL/tblA71jPS8Cle7DMO`) with `Evidence / notes` = verdict, score, JEV scores + model, fails, preview URL, result path.
- Status `Done` + `Done=true` only when every criterion passes; otherwise `In progress` and `Done=false`. Never flip a row by hand. Provider writes require scoped approval; these repairs execute no Airtable writes.
- PAT comes from `~/.rig/secrets/airtable-command-center.env` (`AIRTABLE_CC_PAT`). Never print it.

## Version policy

A criteria bump adds checks; it does not delete old ones silently. Record the version in the result.
