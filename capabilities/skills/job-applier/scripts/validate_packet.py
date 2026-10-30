#!/usr/bin/env python3
"""Validate artifact completeness and bindings, never factual truth or authorization."""
import argparse
import hashlib
import json
import zipfile
from pathlib import Path

STEPS = ['posting-inventory', 'ideal-candidate-persona', 'ideal-achievement-bank',
         'evidence-alignment', 'word-review-copy', 'targeted-confirmation',
         'document-quality', 'application-approval']
PERSONA_FIELDS = ['mandate', 'decision_rights', 'operating_environment', 'industry_economics',
                  'outcomes_90_days', 'outcomes_year_one', 'capability_depth',
                  'leadership_behaviors', 'ideal_career_proof_metrics', 'hard_criteria',
                  'tradeoffs_failure_modes', 'hiring_questions', 'adjacent_vs_direct_fit']
OUTPUTS = [['inventory'], ['persona', 'persona_review'], ['achievement_bank'], ['alignment'],
           ['red_docx', 'clean_docx', 'changes'], ['confirmations'],
           ['images', 'quality'], ['approval', 'submission_receipt']]


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def validate(packet_path):
    packet_path = Path(packet_path).resolve()
    root = packet_path.parent
    packet = json.loads(packet_path.read_text())
    errors = []

    def need(condition, message):
        if not condition:
            errors.append(message)

    def ref(value):
        if not isinstance(value, dict) or not isinstance(value.get('path'), str):
            raise ValueError('artifact reference requires path and sha256')
        path = (root / value['path']).resolve()
        if not path.is_relative_to(root) or not path.is_file():
            raise ValueError('artifact missing or outside packet root: ' + value['path'])
        if sha(path) != value.get('sha256'):
            raise ValueError('artifact hash mismatch: ' + value['path'])
        return path

    artifacts = packet.get('artifacts', {})
    paths = {name: ref(value) for name, value in artifacts.items()}

    def data(name):
        if name not in paths:
            raise ValueError('missing artifact: ' + name)
        return json.loads(paths[name].read_text())

    target = packet.get('target')
    need(isinstance(target, dict) and all(target.get(k) for k in ('company', 'role', 'id', 'url')),
         'complete target identity required')
    jd = paths.get('jd')
    if jd is None:
        raise ValueError('missing artifact: jd')
    jd_text = jd.read_text()
    jd_hash = artifacts['jd']['sha256']
    inventory = data('inventory')
    persona = data('persona')
    stage = packet.get('stage')
    bank = data('achievement_bank') if stage != 'persona' else {}
    alignment = data('alignment') if stage != 'persona' else {}
    for name, value in [('inventory', inventory), ('persona', persona),
                        ('achievement_bank', bank), ('alignment', alignment)]:
        if stage == 'persona' and name in ('achievement_bank', 'alignment'):
            continue
        need(value.get('jd_sha256') == jd_hash and value.get('target') == target,
             name + ': stale JD or target binding')
    for name, value in [('achievement_bank', bank), ('alignment', alignment)]:
        if stage == 'persona':
            continue
        need(value.get('persona_sha256') == artifacts['persona']['sha256'],
             name + ': stale persona binding')
    requirements = inventory.get('requirements', [])
    need(bool(requirements), 'empty requirement inventory')
    ids = [r.get('id') for r in requirements]
    need(all(isinstance(i, str) and i.strip() for i in ids) and len(set(ids)) == len(ids),
         'requirement IDs must be nonempty and unique')
    for row in requirements:
        need(row.get('kind') in ('responsibility', 'minimum', 'preferred', 'constraint'),
             'invalid requirement kind')
        quote = row.get('jd_quote')
        need(isinstance(quote, str) and bool(quote.strip()) and quote in jd_text,
             'requirement quote absent from captured JD')
    need(inventory.get('coverage_review', {}).get('requirement_ids') == ids,
         'inventory requires explicit ordered coverage review')
    coverage_receipt = inventory.get('coverage_review', {}).get('receipt')
    coverage = json.loads(ref(coverage_receipt).read_text())
    need(coverage.get('jd_sha256') == jd_hash and coverage.get('requirement_ids') == ids
         and coverage.get('status') == 'PASS', 'coverage receipt missing current JD/IDs/PASS binding')
    need(persona.get('kind') == 'role_research_not_candidate_facts', 'persona must be role research')
    need(persona.get('requirement_ids') == ids, 'persona requirement coverage mismatch')
    for field in PERSONA_FIELDS:
        entries = persona.get(field)
        need(isinstance(entries, list) and bool(entries), 'persona incomplete: ' + field)
        for entry in entries if isinstance(entries, list) else []:
            need(isinstance(entry, dict) and isinstance(entry.get('text'), str)
                 and bool(entry['text'].strip()) and entry.get('basis') in ('jd', 'public_source', 'inference'),
                 'invalid persona field: ' + field)
            if isinstance(entry, dict):
                refs = entry.get('source_ids', [])
                need(bool(refs) and all(s in ['jd'] + packet.get('public_source_ids', []) and s in artifacts for s in refs), 'unknown persona source')
    persona_review = data('persona_review')
    need(persona_review.get('status') == 'PASS' and bool(persona_review.get('decision_id')),
         'persona semantic review missing or held')
    need(persona_review.get('jd_sha256') == jd_hash
         and persona_review.get('persona_sha256') == artifacts['persona']['sha256']
         and persona_review.get('inventory_sha256') == artifacts['inventory']['sha256'],
         'stale persona semantic review')
    provider = json.loads(ref(persona_review.get('provider_response')).read_text())
    need(all(provider.get(k) == persona_review.get(k) for k in ('status','decision_id','jd_sha256','persona_sha256','inventory_sha256')), 'persona provider response differs from summary')
    if stage != 'persona':
        examples = bank.get('examples', [])
        covered = []
        texts = set()
        for item in examples:
            coverage = item.get('requirement_ids', [])
            covered.extend(coverage)
            need(bool(coverage) and set(coverage) <= set(ids), 'unknown or empty example requirement IDs')
            need(all(isinstance(item.get(k), str) and item[k].strip() for k in ('id','result','personal_action','strategy')),
                 'ideal example requires result, personal action and strategy')
            key = tuple(item.get(k) for k in ('result', 'personal_action', 'strategy'))
            need(key not in texts, 'duplicated ideal example; consolidate with explicit shared rationale')
            texts.add(key)
            need(len(coverage) == 1 or bool(item.get('shared_rationale', '').strip()),
                 'shared example requires explicit rationale')
            need(item.get('status') == 'hypothetical_not_candidate_fact', 'ideal bank must remain hypothetical')
        need(set(covered) == set(ids), 'missing requirement-to-achievement coverage')
        example_ids = [e.get('id') for e in examples]
        need(len(example_ids) == len(set(example_ids)), 'duplicate example ID')
        need(alignment.get('achievement_bank_sha256') == artifacts['achievement_bank']['sha256'], 'stale alignment bank binding')
        claims = alignment.get('claims', [])
        claim_ids = [c.get('id') for c in claims]
        need(len(set(claim_ids)) == len(claim_ids), 'duplicate claim ID')
        need(set(r for c in claims for r in c.get('requirement_ids', [])) == set(ids),
             'alignment missing requirement coverage')
        for claim in claims:
            need(claim.get('example_id') in example_ids, 'unknown alignment example')
            example = next((e for e in examples if e.get('id') == claim.get('example_id')), {})
            need(set(claim.get('requirement_ids', [])) <= set(example.get('requirement_ids', [])), 'claim/example requirement mismatch')
            need(claim.get('status') in ('confirmed', 'adjacent', 'unconfirmed'), 'invalid evidence status')
            need(bool(claim.get('id')), 'claim ID required')
            if claim.get('status') == 'confirmed':
                need(bool(claim.get('source_ids')) and all(s in artifacts for s in claim.get('source_ids', [])),
                     'confirmed claim requires source evidence')
                need(all(claim.get(k) for k in ('employer','role','period','personal_contribution','result')),
                     'confirmed claim missing attribution')
            if claim.get('origin') == 'hypothetical' and claim.get('status') == 'confirmed':
                ref(claim.get('confirmation'))
    stage = packet.get('stage')
    need(stage in ('persona', 'working', 'final', 'submitted'), 'invalid stage')
    count = {'persona': 2, 'working': 5, 'final': 7, 'submitted': 8}.get(stage, 8)
    logs = packet.get('step_log', [])
    need([s.get('step') for s in logs] == STEPS[:count], 'skipped, repeated or unordered leaf execution')
    for index, log in enumerate(logs):
        if index >= len(STEPS):
            break
        need(log.get('leaf') == 'steps/' + STEPS[index] + '/SKILL.md', 'wrong leaf execution path')
        receipt = json.loads(ref(log.get('execution_receipt')).read_text())
        need(receipt.get('step') == STEPS[index] and bool(receipt.get('command_or_tool'))
             and bool(receipt.get('started_at')) and bool(receipt.get('completed_at')),
             'execution receipt missing actual invocation or timestamps')
        response = json.loads(ref(receipt.get('response_artifact')).read_text())
        need(response.get('step') == log.get('step') and response.get('artifact_hashes') == log.get('artifact_hashes'), 'execution response missing current step/artifact bindings')
        bindings = log.get('artifact_hashes', {})
        required = ['jd', 'inventory'] + OUTPUTS[index]
        if index >= 1:
            required += ['persona']
        for name in required:
            need(name in artifacts and bindings.get(name) == artifacts.get(name, {}).get('sha256'),
                 'step artifact binding missing/stale: ' + str(log.get('step')) + '/' + name)
        need(receipt.get('artifact_hashes') == bindings, 'execution receipt bindings differ from step log')
    if stage != 'persona':
        for name in ('red_docx', 'clean_docx'):
            with zipfile.ZipFile(paths[name]) as doc:
                need('word/document.xml' in doc.namelist() and '[Content_Types].xml' in doc.namelist(), 'invalid Word artifact: ' + name)
    if stage == 'persona':
        pass
    elif packet.get('source_only_recovery'):
        need(stage == 'working' and packet.get('tailoring_status') == 'incomplete',
             'source-only recovery cannot become completed tailoring')
    else:
        need(packet.get('tailoring_status') == 'complete', 'tailoring incomplete')
    if stage in ('final', 'submitted'):
        confirmations = data('confirmations')
        quality = data('quality')
        images = data('images')
        need(bool(images.get('pages')), 'missing rendered page images')
        for page in images.get('pages', []):
            ref(page)
        need(images.get('docx_sha256') == artifacts.get('clean_docx', {}).get('sha256'), 'stale image document binding')
        jev = json.loads(ref(quality.get('jev_receipt')).read_text())
        need(all(jev.get(k) == quality.get(k) for k in ('decision_id', 'status', 'jd_sha256', 'persona_sha256', 'criteria_ids')), 'typed Jev receipt differs from quality summary')
        for name in ('clean_docx', 'images', 'alignment', 'confirmations'):
            need(quality.get(name + '_sha256') == artifacts[name]['sha256'] and jev.get(name + '_sha256') == artifacts[name]['sha256'], 'stale quality document/review binding: ' + name)
        need(quality.get('decision_id') and quality.get('status') == 'PASS', 'missing passing typed Jev decision')
        need(quality.get('criteria_ids') == list(range(1,16)), 'missing fifteen quality criteria')
        need(quality.get('persona_sha256') == artifacts['persona']['sha256']
             and quality.get('jd_sha256') == jd_hash, 'stale quality persona/JD binding')
        approval = confirmations.get('page_approval', {})
        need(approval.get('images_sha256') == artifacts['images']['sha256']
             and approval.get('docx_sha256') == artifacts['clean_docx']['sha256'], 'missing exact-page final approval')
        ref(approval.get('human_response'))
        for claim in claims:
            decisions = confirmations.get('decisions', {})
            choice = decisions.get(claim['id'], {})
            need(choice.get('action') in ('confirm','replace','omit'), 'missing factual claim decision')
            ref(choice.get('human_response'))
            if claim['status'] != 'confirmed' and choice.get('action') != 'omit':
                need(all(choice.get(k) for k in ('employer','role','period','personal_contribution','result')),
                     'unconfirmed claim promoted without factual confirmation')
    if stage == 'submitted':
        approval = data('approval')
        receipt = data('submission_receipt')
        for name, value in [('approval', approval), ('submission_receipt', receipt)]:
            need(value.get('target') == target and value.get('docx_sha256') == artifacts['clean_docx']['sha256'],
                 name + ': wrong application/content binding')
            ref(value.get('evidence'))
        need(bool(receipt.get('provider_receipt_id')), 'actual submission receipt required')
    return {'status': 'BLOCK' if errors else 'STRUCTURALLY_VALID', 'errors': errors,
            'scope': 'Completeness and hash bindings only; not truth, semantic quality, receipt authenticity, authorization or Jev certification.'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('packet', type=Path)
    args = parser.parse_args()
    try:
        result = validate(args.packet)
    except (OSError, ValueError, TypeError, KeyError, AttributeError, zipfile.BadZipFile) as exc:
        result = {'status': 'BLOCK', 'errors': [str(exc)]}
    print(json.dumps(result, indent=2))
    return 0 if result['status'] == 'STRUCTURALLY_VALID' else 1


if __name__ == '__main__':
    raise SystemExit(main())
