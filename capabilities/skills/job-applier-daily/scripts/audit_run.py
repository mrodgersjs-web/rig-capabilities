#!/usr/bin/env python3
"""Audit local evidence bindings. This is not an executor or authorization service."""
import argparse
import hashlib
import json
from pathlib import Path

TRACKER = {'base': 'appjHReyFuIAyEZXI', 'table': 'tbl450GyKwBLxGQvK', 'view': 'viwQZBD5gESWLqp0I'}
STEPS = ('setup', 'discovery', 'posting-inventory', 'ideal-candidate-persona',
         'ideal-achievement-bank', 'employer-research', 'evidence-alignment',
         'word-review-copy', 'targeted-confirmation', 'resume-writing',
         'cover-letter-writing', 'writing-review', 'document-quality',
         'airtable-sync', 'application-approval')
DOCUMENTS = ('master_docx', 'review_docx', 'resume_docx', 'resume_pdf', 'cover_letter_docx', 'cover_letter_pdf')


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(',', ':')).encode()).hexdigest()


def job_key(candidate_id, employer_id, requisition_id):
    """Caller must resolve employer aliases and ATS identity before using this key."""
    return digest([candidate_id.strip().casefold(), employer_id.strip().casefold(), requisition_id.strip().casefold()])


def audit(path):
    root = Path(path).resolve().parent
    packet = json.loads(Path(path).read_text())
    errors = []

    def need(ok, reason):
        if not ok:
            errors.append(reason)

    def read_artifact(ref):
        if not isinstance(ref, dict) or not isinstance(ref.get('path'), str):
            raise ValueError('artifact reference requires path and sha256')
        raw = root / ref['path']
        resolved = raw.resolve()
        if Path(ref['path']).is_absolute() or not resolved.is_relative_to(root) or not resolved.is_file():
            raise ValueError('artifact missing or outside packet')
        if any(p.is_symlink() for p in [raw, *raw.parents] if p != root.parent):
            raise ValueError('symlinked evidence is not accepted')
        data = resolved.read_bytes()
        if not data:
            raise ValueError('empty evidence artifact: ' + ref['path'])
        if hashlib.sha256(data).hexdigest() != ref.get('sha256'):
            raise ValueError('artifact hash mismatch: ' + ref['path'])
        return data

    def read_json(ref):
        return json.loads(read_artifact(ref))

    need(packet.get('schema') == 'job-applier-daily.packet.v1', 'unknown packet schema')
    need(packet.get('stage') in ('ready', 'submitted'), 'audit requires ready or submitted stage')
    artifacts = packet.get('artifacts', {})
    for ref in artifacts.values():
        read_artifact(ref)
    target = packet.get('target', {})
    need(all(isinstance(target.get(k), str) and target[k].strip() for k in
             ('candidate_id', 'employer_id', 'requisition_id', 'official_url', 'title')), 'target incomplete')
    expected_key = job_key(target.get('candidate_id', ''), target.get('employer_id', ''), target.get('requisition_id', ''))
    need(packet.get('job_key') == expected_key, 'job identity mismatch')
    need(packet.get('tracker') == TRACKER, 'wrong Airtable destination')
    need('jd' in artifacts and 'persona' in artifacts and 'requirements' in artifacts, 'missing JD/persona/requirements')
    need(all(k in artifacts for k in DOCUMENTS), 'missing resume or cover-letter artifact')
    page_names = packet.get('rendered_pages', [])
    need(bool(page_names) and len(set(page_names)) == len(page_names), 'page manifest empty or duplicate')
    need(all(k in artifacts for k in page_names), 'missing rendered page bytes')
    binding = digest({'job_key': packet.get('job_key'), 'target': target, 'artifacts': artifacts,
                      'rendered_pages': page_names, 'form_answers': packet.get('form_answers'),
                      'destination': packet.get('destination'), 'claims': packet.get('claims')})
    need(packet.get('binding') == binding, 'stale packet binding')
    need(isinstance(packet.get('form_answers'), dict) and bool(packet['form_answers']), 'missing form answers')
    need(isinstance(packet.get('destination'), str) and packet['destination'].startswith('https://'), 'missing submit destination')
    steps = packet.get('steps', [])
    need([s.get('id') for s in steps] == list(STEPS), 'ordered step evidence incomplete')
    for step in steps:
        receipt = read_json(step.get('receipt'))
        need(receipt.get('step') == step.get('id') and receipt.get('binding') == binding,
             'stale step: ' + str(step.get('id')))
        need(receipt.get('status') == 'PASS' and receipt.get('can_advance') is True,
             'step held: ' + str(step.get('id')))
        need(bool(receipt.get('decision_id')) and bool(receipt.get('request_id')),
             'missing Jev request/decision: ' + str(step.get('id')))

    claims = packet.get('claims')
    need(isinstance(claims, list) and bool(claims), 'claim ledger must be nonempty')
    if not isinstance(claims, list):
        claims = []
    claim_ids = [c.get('id') for c in claims]
    need(all(isinstance(i, str) and i.strip() for i in claim_ids) and len(set(claim_ids)) == len(claim_ids),
         'claim IDs must be nonempty and unique')
    need(any(c.get('included') is True for c in claims), 'no confirmed claim included')
    for claim in claims:
        need(isinstance(claim.get('text'), str) and bool(claim['text'].strip()), 'claim text required')
        need(isinstance(claim.get('included'), bool), 'claim included must be Boolean')
        need(claim.get('status') in ('confirmed', 'unconfirmed', 'omitted'), 'invalid claim status')
        if claim.get('included') is True:
            need(claim.get('status') == 'confirmed', 'included claim unconfirmed')
            confirmation = read_json(claim.get('confirmation'))
            need(confirmation.get('claim_id') == claim.get('id') and
                 confirmation.get('claim_sha256') == digest(claim.get('text')) and
                 confirmation.get('participated') is True and confirmation.get('include') is True,
                 'participation/include confirmation missing or stale')
            need(all(confirmation.get(k) for k in ('actor', 'source_message_id', 'employer', 'dates', 'personal_action', 'result')),
                 'confirmation lacks actual contribution details')
            need(bool(claim.get('sources')), 'included claim lacks provenance')
            for ref in claim.get('sources', []):
                read_artifact(ref)

    quality = read_json(packet.get('quality_receipt'))
    need(quality.get('binding') == binding and quality.get('status') == 'PASS' and quality.get('can_advance') is True,
         'quality receipt held or stale')
    criteria = quality.get('criteria', [])
    need([c.get('id') for c in criteria] == [f'c{i:02d}' for i in range(1, 16)], '15 criteria missing or duplicate')
    need(all(c.get('status') == 'PASS' for c in criteria), 'quality criterion held')
    need(quality.get('image_page_artifacts') == page_names and bool(quality.get('image_decision_id')),
         'image review missing exact pages/decision')
    need(bool(quality.get('decision_id')) and bool(quality.get('request_id')), 'quality provider receipt missing')

    tracker = read_json(packet.get('tracker_receipt'))
    need(tracker.get('tracker') == TRACKER and tracker.get('job_key') == expected_key, 'tracker identity mismatch')
    need(tracker.get('schema_verified') is True and tracker.get('full_table_scan_complete') is True,
         'tracker schema/dedupe not verified')
    need(tracker.get('matching_record_count') == 1 and tracker.get('write_readback') is True,
         'tracker record uncertain or duplicate')
    need(bool(tracker.get('record_id')) and bool(tracker.get('schema_sha256')), 'missing tracker record/schema binding')
    need(tracker.get('binding') == binding and tracker.get('prior_submission') is False, 'tracker stale or already applied')
    need(tracker.get('field_map_valid') is True and tracker.get('status_map_valid') is True, 'tracker schema mapping held')

    for kind in ('facts', 'pages', 'submission'):
        approval = read_json(packet.get('approvals', {}).get(kind))
        need(approval.get('kind') == kind and approval.get('binding') == binding and
             approval.get('approved') is True and bool(approval.get('actor')) and bool(approval.get('source_message_id')),
             'approval missing/stale: ' + kind)
    submission_state = packet.get('submission_state')
    need(submission_state in ('not_attempted', 'reserved', 'receipt_verified', 'unknown', 'attempted', 'reserved_elsewhere'), 'unknown submission state')
    need(submission_state not in ('unknown', 'attempted', 'reserved_elsewhere'), 'submission reconciliation hold')
    need((packet.get('stage') == 'ready' and submission_state in ('not_attempted', 'reserved')) or
         (packet.get('stage') == 'submitted' and submission_state == 'receipt_verified'), 'submission state/stage mismatch')
    if packet.get('stage') == 'submitted':
        receipt = read_json(packet.get('ats_receipt'))
        need(receipt.get('job_key') == expected_key and receipt.get('binding') == binding and
             receipt.get('status') == 'receipt_verified' and bool(receipt.get('provider_reference')),
             'ATS receipt missing/wrong identity')
        read_artifact(receipt.get('evidence'))
    return {'status': 'BLOCK' if errors else 'STRUCTURAL_PASS', 'errors': errors,
            'binding': binding, 'authorizes_submission': False,
            'scope': 'Local file integrity and declared evidence structure only. Host must authenticate approvals, provider receipts, facts and live state.'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('packet', type=Path)
    args = parser.parse_args()
    try:
        result = audit(args.packet)
    except (ValueError, OSError, TypeError, KeyError, AttributeError) as exc:
        result = {'status': 'BLOCK', 'errors': [str(exc)], 'authorizes_submission': False}
    print(json.dumps(result, indent=2))
    raise SystemExit(0 if result['status'] == 'STRUCTURAL_PASS' else 2)


if __name__ == '__main__':
    main()
