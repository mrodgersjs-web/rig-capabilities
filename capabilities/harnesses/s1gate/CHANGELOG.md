# s1gate rubrics CHANGELOG

## 2026-10-22 call.script v1.0.0 (new)
- Author: GTM Lead (Grok Bot), Jake ruling q_3532f1d2dcb2 (linked q_cf5172485804).
- File: rubrics/call.script.json. Six noul questions: evidence_backed, one_business, single_low_cost_ask, no_price_or_hype, speakable_voice, clear_exit. BLOCK at <=0.50 on evidence/price-hype/ask/exit; ESCALATE at <=0.50 on one_business/speakable_voice. Reporting composite = min noul. calibrated:false (initial thresholds). Global Jev >= 0.9 bar unchanged.
- Known-bad controls (fixtures/call.script-controls/, run.sh): all 4 FAIL as required.
  - bad-invented-claim: BLOCK, min 0.15 (evidence_backed 0.15)
  - bad-price: BLOCK, min 0.01 (no_price_or_hype 0.01)
  - bad-generic: BLOCK, min 0.04 (evidence_backed 0.04, one_business 0.04)
  - bad-pushy-close: BLOCK, min 0.03 (ask 0.09, exit 0.08, hype 0.03)
- Candidates: 20 GTM call packs (gtm/call-packs/2026-10-22/.scored-bodies): 0 PASS, 20 ESCALATE, all on one_business (0.34-0.49); other five dims 0.74-0.98. Not tuned to pass them.
