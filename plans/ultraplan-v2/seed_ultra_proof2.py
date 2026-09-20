#!/usr/bin/env python3
"""Round-2 ultra.proof corpus: realistic-difficulty rows.

Round 1 separated too cleanly (good ~0.8-0.95, bad ~0.05-0.5) so the certified
threshold landed in a sparse region and true single-fact claims scored like bad
ones. Labels remain ground-truth BY CONSTRUCTION: every 'good' row states exactly
one checkable fact whose done-test goes red on a named, concrete break; every
'bad' row bundles facts or asserts an unfalsifiable outcome.
"""
import sys
sys.path.insert(0, "/Users/rig128gb/Developer/rig-capabilities")
from rig_capabilities import s1gate

# (claim, done_test, evidence, label, defect-if-bad)
ROWS = [
  ("the ledger stores one event row per command_id", "cmd:python3 -m unittest tests.test_ledger.TestLedger.test_duplicate_command_id_returns_original_event_no_double_effect", "Ran 1 test OK; COUNT(*) c FROM outbox == 1", "good", ""),
  ("events and their outbox rows commit atomically", "cmd:python3 -m unittest tests.test_ledger.TestCrashPoints", "kill -9 between BEGIN and COMMIT -> 0 events, 0 outbox; between COMMIT and return -> 2 events, 1 outbox", "good", ""),
  ("parked missions reject stage.advance", "cmd:python3 -m unittest tests.test_ledger.TestLedger.test_illegal_transitions_refused", "IllegalTransition raised before INSERT; event count unchanged", "good", ""),
  ("the ui actor cannot create missions", "cmd:python3 -m unittest tests.test_commands.TestHandler.test_actor_authority_is_decided_not_claimed", "forbidden_for_actor; zero rows in events table after attempt", "good", ""),
  ("claim_atomic has a measured threshold on the live pack", "cmd:python3 -c \"import json; e=json.load(open('/Users/rig128gb/Developer/rig-capabilities/capabilities/harnesses/s1gate/rubrics/ultra.proof.json'))['calibration']['rules']['claim_atomic.noul']; assert e['threshold']>0\"", "threshold 0.4916 recorded with holdout fbr 0.0", "good", ""),
  ("the validator now sees the nine studios", "cmd:python3 -m unittest tests.test_ultra_cell.TestRefusals.test_studio_calls_must_resolve", "20 tests OK; tree of ~/Developer/ultraplan lists 7 studios", "good", ""),
  ("fencing epochs monotonically supersede old tokens", "cmd:python3 -m unittest tests.test_ledger.TestLedger.test_stale_writer_fence_refused", "StaleFence for tok-A after acquire(tok-C); epoch incremented", "good", ""),
  ("projection rebuild hashes equal the live head hash", "cmd:python3 -m unittest tests.test_ledger.TestLedger.test_rebuild_projection_matches_live_head", "rebuild hash == event hash byte-equal", "good", ""),
  ("the handler validates envelopes before touching state", "cmd:python3 -m unittest tests.test_commands.TestHandler.test_schema_rejects_before_state_touch", "schema_invalid returned, ledger never opened for the write path", "good", ""),
  ("a tampered chain hash fails verification", "cmd:python3 -m unittest tests.test_ledger.TestLedger.test_chain_detects_tampering", "UPDATE payload then verify_chain -> False", "good", ""),
  ("the JEX gate executes done-test assertions", "cmd:cd /Users/rig128gb/Developer/rig-capabilities && python3 -m unittest tests.test_ultra_gates.TestRouterOffline.test_named_but_never_run_assertion_no_longer_passes", "route=rework note='assertion exited 3 after 5ms'", "good", ""),
  ("the polarity rule fires on low noul only", "cmd:cd /Users/rig128gb/Developer/rig-capabilities && python3 -m unittest tests.test_ultra_polarity", "0.95 no trip; 0.05 ESCALATE; 0.50 boundary trips", "good", ""),
  ("certification voids when the rule text is edited", "cmd:cd /Users/rig128gb/Developer/rig-capabilities && python3 -m unittest tests.test_s1gate_calibrate.TestPerRuleCalibration.test_editing_the_rule_voids_certification", "rule_sha256 mismatch -> rule_enforces False", "good", ""),
  ("the schema refuses an event hash that is not hex", "cmd:cd /Users/rig128gb/Developer/ultraplan && python3 -m unittest tests.test_schemas.TestSchemas.test_event_hash_chain_required", "pattern violation on hash field with 'not valid under'", "good", ""),
  ("duplicate deliveries return the original event", "cmd:python3 -m unittest tests.test_ledger.TestLedger.test_idempotency_key_short_circuits_second_delivery", "same event_id both calls", "good", ""),
  ("uncalibrated rules cannot enforce a BLOCK", "cmd:cd /Users/rig128gb/Developer/rig-capabilities && python3 -m unittest tests.test_s1gate_calibrate.TestPerRuleEnforcement", "downgrade reason names the rule", "good", ""),
  ("the handler returns conflicts as results not exceptions", "cmd:python3 -m unittest tests.test_commands.TestHandler.test_sequence_conflict_is_a_result_not_an_exception", "error=sequence_conflict, no traceback", "good", ""),
  ("effects claimed once surface to exactly one worker", "cmd:python3 -m unittest tests.test_ledger.TestLedger.test_effect_claimed_exactly_once_across_two_workers", "len(a)==1, len(b)==0 across two connections", "good", ""),
  ("the mission state tour visits every legal state", "cmd:python3 -m unittest tests.test_ledger.TestLedger.test_full_legal_state_tour", "parked, running, uncertain, cancelled asserted in order", "good", ""),
  ("command results carry the event hash", "cmd:python3 -m unittest tests.test_commands.TestHandler.test_console_cli_mcp_are_the_same_function_on_the_same_ledger", "hash field present, differs per distinct command", "good", ""),
  ("the ledger is durable across process restart and the tests are green and everything works", "cmd:python3 -m unittest tests.test_ledger", "Ran 13 tests OK", "bad", "three facts bundled into one claim"),
  ("the command handler is production ready", "cmd:true", "handler exists and looks correct", "bad", "unfalsifiable outcome claim + vacuous test"),
  ("schemas validate and authority holds", "cmd:echo done", "reviewed by Jake", "bad", "compound claim, narrative evidence, vacuous test"),
  ("the W02 runtime is complete and verified", "cmd:echo ok", "manifest statuses say built", "bad", "self-narrating status as done-test"),
  ("the crash tests pass so the system cannot lose data", "cmd:python3 -m unittest tests.test_ledger", "13 OK", "bad", "extrapolates total safety from bounded tests"),
  ("the gate works well", "cmd:echo fine", "scores looked reasonable", "bad", "no fact stated at all"),
  ("events hash-chained append and verification detects edits and rebuild matches head", "cmd:python3 -m unittest tests.test_ledger.TestLedger.test_chain_detects_tampering tests.test_ledger.TestLedger.test_rebuild_projection_matches_live_head", "two tests OK", "bad", "three claims stitched"),
  ("the ui role was restricted and the forged kinds refused", "cmd:python3 -m unittest tests.test_commands", "5 tests OK", "bad", "two facts, one claim"),
]


def main(apply=True):
    rb = s1gate.load_rubric("ultra.proof")
    log = s1gate.DecisionLog()
    n = 0
    for claim, test, ev, label, defect in ROWS:
        state = "CLAIM: %s\nDONE-TEST: %s\nEVIDENCE: %s" % (claim, test, ev)
        if not apply:
            print(label, "|", claim[:70]); n += 1; continue
        res = s1gate.evaluate(rb, state, subject="seed2:%s" % label)
        if res.error:
            print("provider error:", res.error); break
        did = log.record(res, subject="seed2:%s" % label)
        log.label(did, label, by="construction")
        n += 1
        print("%2d %s %s atomic=%s vac=%s ev=%s" % (
            n, label, claim[:52], res.answers.get("claim_atomic", {}).get("noul"),
            res.answers.get("done_test_is_vacuous", {}).get("noul"),
            res.answers.get("evidence_is_command_output", {}).get("noul")))
    print("rows:", n)


if __name__ == "__main__":
    main(apply="--apply" in sys.argv)
