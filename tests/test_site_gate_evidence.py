import contextlib
import datetime
import importlib.util
import io
import json
import os
from pathlib import Path
import sys
import subprocess
import tempfile
import unittest
from unittest.mock import patch, mock_open
from PIL import Image


SCRIPTS = Path(__file__).resolve().parents[1] / 'capabilities/skills/jev-site-gate/scripts'
sys.path.insert(0, str(SCRIPTS))
SPEC = importlib.util.spec_from_file_location('site_gate_under_test', SCRIPTS / 'gate.py')
gate = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(gate)
import evidence_contract
from evidence_contract import Evidence, VERSION, BOARD_ID, build_digest, digest, distinct_offerings


def workspace_snapshot(root):
    snapshot = {}
    for path in [root, *sorted(root.rglob('*'))]:
        metadata = path.lstat()
        content = os.readlink(path) if path.is_symlink() else path.read_bytes() if path.is_file() else None
        snapshot[str(path.relative_to(root))] = (metadata.st_mode, metadata.st_mtime_ns, metadata.st_size, content)
    return snapshot


class EvidenceFixture:
    def __init__(self, parent, slug='transformfit-intake'):
        self.root = Path(parent) / slug
        self.site = self.root / 'sites' / slug
        self.slug = slug
        self.site.mkdir(parents=True)
        self.now = datetime.datetime.now(datetime.timezone.utc).replace(microsecond=0)
        self.time = self.now.isoformat()
        self.url = f'https://{slug}.example.test/'
        for phase in gate.PHASES:
            self.write(f'{phase}.md', f'{phase} executed for {slug} with linked artifacts.')
        self.write('demand.md', 'rec1 Waiting rec2 Repetition rec3 Scheduling')
        self.write('claims.md', '')
        self.write('critique.md', 'Independent rendered review. No award guarantee.')
        self.write('define.md', 'Named wow moment: wow. User-named TransformFit project.')
        self.write('discover.md', 'Observed references ' + ' '.join(f'https://reference{number}.test/' for number in range(6)))
        self.write('deliver.md', self.url)
        self.write('app/index.html', f'<h1>{slug}</h1>')
        self.write('evidence/identity.json', {'instruction': 'Mike directly names TransformFit as a project.'})
        self.write('evidence/source.json', {'pains': [{'id': f'rec{number + 1}', 'text': quote}
                   for number, quote in enumerate(['Waiting', 'Repetition', 'Scheduling'])]})
        self.write('evidence/source-run.json', {'run': {'run_id': 'run-test', 'provider': 'socialfetch',
                  'status': 'success', 'response_sha256': digest(self.site / 'evidence/source.json')}})
        self.write('evidence/pin-index.json', {'pin': 'https://www.pinterest.com/pin/123456789/'})
        self.png('evidence/hero.png', 700, 700)
        for name, width, height in [('desktop-1440', 1440, 900), ('mobile-390', 390, 844)]:
            self.png(f'evidence/{name}.png', width, height)
        for number in range(3):
            self.png(f'evidence/diverge-{number}.png', 800 + number, 500)
        for number in range(6):
            self.png(f'evidence/reference-{number}.png', 800, 500)
        self.manifest = {
            'schema': VERSION, 'offering_id': slug, 'brand_owner_id': 'transformfit',
            'client': {'id': 'transformfit', 'name': 'TransformFit', 'identity_kind': 'user-named-project',
                       'identity_source': {**self.ref('evidence/identity.json', '/instruction'), 'authority': 'mike-direct'}},
            'solution': {'id': f'{slug}-workflow', 'mechanism': f'{slug} intake workflow', 'problem': 'Slow intake',
                         'status': 'proposed', 'source_ids': ['pain-1', 'pain-2', 'pain-3']},
            'sources': [{'id': f'pain-{number + 1}', 'record_id': f'rec{number + 1}', 'run_id': 'run-test',
                         'kind': 'socialfetch', 'scope': 'category', 'quote': quote,
                         'artifact': self.ref('evidence/source.json', f'/pains/{number}/text'),
                         'record_locator': f'/pains/{number}/id',
                         'run_receipt': self.ref('evidence/source-run.json', '/run')}
                        for number, quote in enumerate(['Waiting', 'Repetition', 'Scheduling'])],
            'pinterest': [{'pin_url': 'https://www.pinterest.com/pin/123456789/', 'image_path': 'evidence/hero.png',
                           'image_sha256': digest(self.site / 'evidence/hero.png'),
                           'index_source': self.ref('evidence/pin-index.json', '/pin'),
                           'visual_decision': 'Observed ring composition supports a centered intake narrative.'}],
            'references': [{'kind': 'mirror' if number < 3 else 'award', 'url': f'https://reference{number}.test/',
                            'capture_url': f'https://reference{number}.test/', 'artifact': f'evidence/reference-{number}.png'}
                           for number in range(6)],
        }
        self.probe = {
            'url': self.url, 'vercel_url': self.url, 'pinterest_board': slug, 'buyer': 'Fitness coach',
            'hero': {'headline': 'Fitness coach intake', 'subhead': 'Waiting', 'pinterest_source': 'hero.png', 'height_ratio': 0.8},
            'cta': {'text': 'Start', 'clickable_ms': 100}, 'text': 'Start Start',
            'pain_cards': [{'record_id': f'rec{number + 1}', 'pain': quote} for number, quote in enumerate(['Waiting', 'Repetition', 'Scheduling'])],
            'wow_id': 'wow', 'wow_present': True, 'scroll_w_390': 390, 'scroll_w_1440': 1440,
            'links': {'total': 1, 'bad': 0, 'empty_href': 0}, 'images_complete': True, 'broken_images': 0, 'fonts': ['Arial'],
        }
        self.browser = {
            'url': self.url, 'build_sha256': build_digest(self.site), 'session_id': 'fixture-session', 'runtime_errors': [],
            'scroll': {'selector': '#story', 'mechanism': 'scroll-driven opacity',
                       'samples': [{'input': {'scroll_y': number * 500}, 'state': {'opacity': number}} for number in range(2)]},
            'three_d': {'selector': '#scene', 'mechanism': 'pointer-driven CSS rotateY', 'kind': 'css3d',
                        'samples': [{'input': {'pointer': [50, 50], 'scroll_y': number * 500}, 'state': {'transform': value}} for number, value in enumerate([
                            'matrix3d(1,0,0,0,0,1,0,0,0,0,1,0,0,0,0,1)',
                            'matrix3d(0.98,0,0.2,0,0,1,0,0,-0.2,0,0.98,0,0,0,0,1)'])]},
            'reduced_motion': [{'viewport_width': width, 'emulated': 'reduce', 'motion_suppressed': True,
                               'content_visible': True, 'cta_click_succeeded': True} for width in [390, 1440]],
            'cta': [{'viewport_width': width, 'visible': True, 'enabled': True, 'hit_target': True,
                     'click_succeeded': True, 'expected_effect_observed': True, 'clock_origin': 'navigationStart',
                     'clickable_ms': 100} for width in [390, 1440]],
        }
        for motion in ('scroll', 'three_d'):
            self.browser[motion]['samples'] = [dict(sample, viewport_width=width) for width in (390, 1440)
                                               for sample in self.browser[motion]['samples']]
        self.lighthouse = {'finalDisplayedUrl': self.url, 'requestedUrl': self.url, 'fetchTime': self.time,
                           'configSettings': {'formFactor': 'mobile'}, 'lighthouseVersion': 'fixture-only',
                           'audits': {'test': {'score': 1}}, 'categories': {'performance': {'score': 0.85}, 'accessibility': {'score': 0.95}}}
        self.ledger = {'offering_id': slug, 'board_id': BOARD_ID, 'phases': [],
                       'divergence': [{'artifact': f'evidence/diverge-{number}.png', 'pin_url': self.manifest['pinterest'][0]['pin_url'],
                                      'mirror_url': self.manifest['references'][0]['url']} for number in range(3)],
                       'selected_direction': 'evidence/diverge-1.png', 'selection_rationale': 'Selected the clearer intake flow for this buyer from the pinned ring composition.'}
        self.export = {'board_id': BOARD_ID, 'captured_at': self.time, 'source_tool': 'fixture-only', 'capture_id': 'fixture-export', 'items': []}
        for number, phase in enumerate(gate.PHASES):
            completed = (self.now - datetime.timedelta(minutes=20 - number)).isoformat()
            self.ledger['phases'].append({'phase': phase, 'status': 'completed', 'worker': 'test-worker',
                                         'previous': gate.PHASES[number - 1] if number else None, 'completed_at': completed,
                                         'artifacts': [f'{phase}.md'], 'item_ids': [f'item-{phase}']})
            self.export['items'].append({'id': f'item-{phase}', 'offering_id': slug, 'phase': phase,
                                         'content': f'{slug} {phase} artifact completed',
                                         'artifact_hashes': {f'{phase}.md': digest(self.site / f'{phase}.md')}})
        self.trace = {'session_id': 'fixture-session', 'events': [{'kind': name} for name in [
            'navigation', 'scroll', 'pointer', 'reduced-motion', 'cta-click', 'screenshot', 'lighthouse']]}
        self.receipt = {'schema': VERSION, 'offering_id': slug, 'url': self.url, 'captured_at': self.time,
                        'build_sha256': build_digest(self.site), 'session_id': 'fixture-session',
                        'builder': {'id': 'test-builder', 'family': 'fixture-generator'},
                        'verifier': {'id': 'test-verifier', 'family': 'fixture-verifier'}, 'artifacts': {},
                        'source_reviews': {source['id']: {'client_id': 'transformfit', 'solution_id': self.manifest['solution']['id'],
                                           'relevant': True, 'rationale': 'Category intake evidence applies to the proposed fitness intake workflow.'}
                                           for source in self.manifest['sources']},
                        'captures': {f'evidence/{name}.png': {'url': self.url, 'build_sha256': build_digest(self.site),
                                      'viewport': [width, height], 'captured_at': self.time} for name, width, height in [
                                      ('desktop-1440', 1440, 900), ('mobile-390', 390, 844)]}}
        self.critique = {'verifier_id': 'test-verifier', 'score': 8.5,
                         'screenshot_hashes': {name: digest(self.site / name) for name in self.receipt['captures']},
                         'findings': [{'area': area, 'observation': 'Fixture-only passing observation', 'severity': 'info'}
                                      for area in ['desktop', 'mobile', 'keyboard', 'images', 'reduced-motion']]}
        self.write('evidence/brief-gate.json', {'decisions': [{'criterion': criterion, 'decision_id': f'fixture-{criterion}',
                   'model': 'fixture-only', 'provider': 'hosted-jev', 'score': 0.99} for criterion in ['promise-pain', 'single-cta']]})
        self.write('evidence/build-manifest.json', {'build_sha256': build_digest(self.site)})
        self.write('evidence/deployment.json', {'url': self.url, 'build_sha256': build_digest(self.site), 'status': 200, 'capture_id': 'fixture-only'})
        pins = self.root / '_inputs/pinterest' / slug
        pins.mkdir(parents=True)
        (pins / 'hero.png').write_bytes((self.site / 'evidence/hero.png').read_bytes())

    def ref(self, name, locator):
        return {'path': name, 'sha256': digest(self.site / name), 'locator': locator}

    def png(self, name, width, height):
        path = self.site / name
        path.parent.mkdir(parents=True, exist_ok=True)
        Image.new('RGB', (width, height), (31, 45, 61)).save(path)

    def write(self, name, value):
        path = self.site / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(value, indent=2) if isinstance(value, (dict, list)) else value)

    def sign(self, private):
        for name, value in [('offering.json', self.manifest), ('evidence/probe.json', self.probe),
                            ('evidence/browser.json', self.browser), ('evidence/lighthouse.json', self.lighthouse),
                            ('evidence/phase-ledger.json', self.ledger), ('evidence/miro-export.json', self.export),
                            ('evidence/tool-trace.json', self.trace), ('evidence/critique.json', self.critique)]:
            self.write(name, value)
        required = {'discover': ['discover.md', 'offering.json', 'demand.md', 'evidence/pin-index.json'], 'define': ['define.md', 'claims.md'],
                    'gate': ['gate.md', 'evidence/brief-gate.json'],
                    'diverge': ['diverge.md', *[direction['artifact'] for direction in self.ledger['divergence']]],
                    'develop': ['develop.md', 'evidence/build-manifest.json'], 'deliver': ['deliver.md', 'evidence/deployment.json'],
                    'measure': ['measure.md', 'evidence/probe.json', 'evidence/browser.json', 'evidence/lighthouse.json',
                                'evidence/desktop-1440.png', 'evidence/mobile-390.png', 'evidence/critique.json']}
        for entry in self.ledger['phases']:
            entry['artifacts'] = required[entry['phase']]
            for item in self.export['items']:
                if item['id'] in entry['item_ids']:
                    item['artifact_hashes'] = {name: digest(self.site / name) for name in entry['artifacts']}
        self.write('evidence/phase-ledger.json', self.ledger)
        self.write('evidence/miro-export.json', self.export)
        self.receipt['artifacts'] = {str(path.relative_to(self.site)): digest(path) for path in self.site.rglob('*')
                                    if path.is_file() and not path.name.startswith(('verifier-receipt', 'gate-result'))
                                    and 'app' not in path.relative_to(self.site).parts}
        self.write('evidence/verifier-receipt.json', self.receipt)
        subprocess.run(['openssl', 'dgst', '-sha256', '-sign', str(private), '-out', str(self.site / 'evidence/verifier-receipt.sig'),
                        str(self.site / 'evidence/verifier-receipt.json')], check=True, capture_output=True)


class SignedEvidenceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.keys = tempfile.TemporaryDirectory()
        cls.private = Path(cls.keys.name) / 'fixture-private.pem'
        cls.public = Path(cls.keys.name) / 'fixture-public.pem'
        subprocess.run(['openssl', 'genrsa', '-out', str(cls.private), '2048'], check=True, capture_output=True)
        subprocess.run(['openssl', 'rsa', '-in', str(cls.private), '-pubout', '-out', str(cls.public)], check=True, capture_output=True)

    @classmethod
    def tearDownClass(cls):
        cls.keys.cleanup()

    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.fixture = EvidenceFixture(self.directory.name)
        self.addCleanup(self.directory.cleanup)
        trust = patch.object(evidence_contract, 'TRUSTED_VERIFIERS', {digest(self.public): {'id': 'test-verifier', 'family': 'fixture-verifier'}})
        trust.start()
        self.addCleanup(trust.stop)

    def evidence(self):
        return Evidence(self.fixture.root, self.fixture.slug, self.public, now=self.fixture.now)

    def reject(self, mutation, method=None, message=None):
        mutation(self.fixture)
        self.fixture.sign(self.private)
        with self.assertRaises((ValueError, KeyError, TypeError, OSError), msg=message):
            evidence = self.evidence()
            if method:
                getattr(evidence, method)()

    def test_positive_signed_fixture_and_private_project(self):
        self.fixture.sign(self.private)
        evidence = self.evidence()
        for method in ['offering', 'phases', 'reduced_motion', 'cta', 'screenshots', 'critique', 'unchanged']:
            self.assertTrue(getattr(evidence, method)())
        self.assertTrue(evidence.motion('scroll'))
        self.assertTrue(evidence.motion('three_d'))
        self.assertEqual(evidence.lighthouse(), {'performance': 85, 'accessibility': 95})

    def test_missing_operator_key(self):
        self.fixture.sign(self.private)
        with self.assertRaisesRegex(ValueError, 'verifier-key'):
            Evidence(self.fixture.root, self.fixture.slug, None)

    def test_builder_local_key(self):
        self.fixture.sign(self.private)
        with self.assertRaisesRegex(ValueError, 'outside builder'):
            Evidence(self.fixture.root, self.fixture.slug, self.fixture.root / 'key.pem')

    def test_unsigned_receipt_edit(self):
        self.fixture.sign(self.private)
        self.fixture.write('evidence/verifier-receipt.json', {})
        with self.assertRaisesRegex(ValueError, 'signature'):
            self.evidence()

    def test_artifact_changed_without_resigning(self):
        self.fixture.sign(self.private)
        self.fixture.write('evidence/probe.json', {})
        with self.assertRaisesRegex(ValueError, 'hash mismatch'):
            self.evidence()

    def test_self_review(self):
        self.reject(lambda fixture: fixture.receipt['verifier'].update(id='test-builder'))

    def test_no_production_trust_authority(self):
        self.fixture.sign(self.private)
        with patch.object(evidence_contract, 'TRUSTED_VERIFIERS', {}), self.assertRaisesRegex(ValueError, 'no authorized'):
            self.evidence()

    def test_caller_generated_signer_has_no_authority(self):
        self.fixture.sign(self.private)
        with patch.object(evidence_contract, 'TRUSTED_VERIFIERS', {'other-key': {'id': 'other', 'family': 'other'}}), \
                self.assertRaisesRegex(ValueError, 'caller-selected'):
            self.evidence()

    def test_same_family(self):
        self.reject(lambda fixture: fixture.receipt['verifier'].update(family='fixture-generator'))

    def test_wrong_offering(self):
        self.reject(lambda fixture: fixture.receipt.update(offering_id='other-offering'))

    def test_stale_capture(self):
        self.reject(lambda fixture: fixture.receipt.update(captured_at=(fixture.now - datetime.timedelta(days=2)).isoformat()))

    def test_future_capture(self):
        self.reject(lambda fixture: fixture.receipt.update(captured_at=(fixture.now + datetime.timedelta(minutes=1)).isoformat()))

    def test_build_replay(self):
        self.reject(lambda fixture: fixture.write('app/index.html', 'new build'))

    def test_wrong_served_url(self):
        self.reject(lambda fixture: fixture.probe.update(url='https://unrelated.test/'))

    def test_missing_trace_event(self):
        self.reject(lambda fixture: fixture.trace['events'].pop())

    def test_generic_category_identity(self):
        self.reject(lambda fixture: fixture.manifest['client'].update(name='Law firm category'), 'offering')

    def test_rig_brand(self):
        def mutation(fixture):
            fixture.manifest['client'].update(id='rig-ai', name='RIG')
            fixture.manifest['brand_owner_id'] = 'rig-ai'
        self.reject(mutation, 'offering')

    def test_wrong_brand_owner(self):
        self.reject(lambda fixture: fixture.manifest.update(brand_owner_id='rig'), 'offering')

    def test_unauthorized_private_identity(self):
        self.reject(lambda fixture: fixture.manifest['client']['identity_source'].update(authority='builder'), 'offering')

    def test_missing_source_locator(self):
        self.reject(lambda fixture: fixture.manifest['sources'][0]['artifact'].update(locator='/missing'), 'offering')

    def test_source_quote_not_at_locator(self):
        self.reject(lambda fixture: fixture.manifest['sources'][0].update(quote='unrelated construction pain'), 'offering')

    def test_fabricated_source_record_id(self):
        def mutation(fixture):
            fixture.manifest['sources'][0]['record_id'] = 'rec-invented'
            fixture.probe['pain_cards'][0]['record_id'] = 'rec-invented'
        self.reject(mutation, 'offering')

    def test_duplicate_raw_record_locator(self):
        def mutation(fixture):
            original = fixture.manifest['sources'][0]
            fixture.manifest['sources'][1].update(record_id=original['record_id'], quote=original['quote'],
                                                 artifact=original['artifact'], record_locator=original['record_locator'])
        self.reject(mutation, 'offering')

    def test_source_collection_locator_cannot_reuse_one_quote(self):
        def mutation(fixture):
            for source, card in zip(fixture.manifest['sources'], fixture.probe['pain_cards']):
                source['artifact']['locator'] = '/pains'
                source['quote'] = card['pain'] = 'Waiting'
        self.reject(mutation, 'offering')

    def test_source_record_index_aliases_are_rejected(self):
        for index in ('00', '+0', '-0', '-1'):
            with self.subTest(index=index):
                source = self.fixture.manifest['sources'][0]
                source['artifact']['locator'] = f'/pains/{index}/text'
                source['record_locator'] = f'/pains/{index}/id'
                self.fixture.sign(self.private)
                with self.assertRaisesRegex(ValueError, 'noncanonical array index'):
                    self.evidence().offering()

    def test_json_pointer_escape_and_object_key_rules(self):
        self.assertEqual(evidence_contract.pointer({'00': 'literal', '~1': 'escaped'}, '/00'), 'literal')
        self.assertEqual(evidence_contract.pointer({'~1': 'escaped'}, '/~01'), 'escaped')
        with self.assertRaisesRegex(ValueError, 'invalid JSON pointer escape'):
            evidence_contract.pointer({'~2': 'literal'}, '/~2')

    def test_source_quote_from_another_record(self):
        def mutation(fixture):
            fixture.manifest['sources'][1]['artifact']['locator'] = '/pains/0/text'
            fixture.manifest['sources'][1]['quote'] = fixture.probe['pain_cards'][1]['pain'] = 'Waiting'
        self.reject(mutation, 'offering')

    def test_distinct_id_fields_cannot_count_same_record_twice(self):
        def mutation(fixture):
            raw = {'pains': [{'id': 'rec1', 'alias_id': 'rec2', 'text': 'Waiting'},
                             {'id': 'rec3', 'text': 'Scheduling'}]}
            fixture.write('evidence/source.json', raw)
            fixture.write('evidence/source-run.json', {'run': {'run_id': 'run-test', 'provider': 'socialfetch',
                          'status': 'success', 'response_sha256': digest(fixture.site / 'evidence/source.json')}})
            for source, locator, record_locator in zip(fixture.manifest['sources'],
                                                       ['/pains/0/text', '/pains/0/text', '/pains/1/text'],
                                                       ['/pains/0/id', '/pains/0/alias_id', '/pains/1/id']):
                source['artifact'] = fixture.ref('evidence/source.json', locator)
                source['record_locator'] = record_locator
                source['run_receipt'] = fixture.ref('evidence/source-run.json', '/run')
            fixture.manifest['sources'][1]['quote'] = fixture.probe['pain_cards'][1]['pain'] = 'Waiting'
        self.reject(mutation, 'offering')

    def test_failed_source_run(self):
        def mutation(fixture):
            fixture.write('evidence/source-run.json', {'run': {'run_id': 'run-test', 'provider': 'socialfetch', 'status': 'blocked'}})
            for source in fixture.manifest['sources']:
                source['run_receipt'] = fixture.ref('evidence/source-run.json', '/run')
        self.reject(mutation, 'offering')

    def test_unrelated_source_review(self):
        self.reject(lambda fixture: fixture.receipt['source_reviews']['pain-1'].update(relevant=False), 'offering')

    def test_duplicate_pain_cards(self):
        self.reject(lambda fixture: fixture.probe.update(pain_cards=[fixture.probe['pain_cards'][0]] * 3), 'offering')

    def test_extra_unsupported_card(self):
        self.reject(lambda fixture: fixture.probe['pain_cards'].append({'record_id': 'rec10', 'pain': 'Other'}), 'offering')

    def test_missing_card_text(self):
        self.reject(lambda fixture: fixture.probe['pain_cards'][0].update(pain=''), 'offering')

    def test_caption_only_pin(self):
        self.reject(lambda fixture: fixture.manifest['pinterest'][0].update(visual_decision=''), 'offering')

    def test_renamed_unused_hero(self):
        self.reject(lambda fixture: fixture.probe['hero'].update(pinterest_source='index.json'), 'offering')

    def test_insufficient_mirror_set(self):
        self.reject(lambda fixture: fixture.manifest['references'].pop(0), 'offering')

    def test_empty_phase_document(self):
        self.reject(lambda fixture: fixture.write('develop.md', ''), 'phases')

    def test_missing_phase(self):
        self.reject(lambda fixture: fixture.ledger['phases'].pop(), 'phases')

    def test_reversed_phase_order(self):
        self.reject(lambda fixture: fixture.ledger['phases'].reverse(), 'phases')

    def test_wrong_miro_board(self):
        self.reject(lambda fixture: fixture.export.update(board_id='different'), 'phases')

    def test_other_offering_miro_item(self):
        self.reject(lambda fixture: fixture.export['items'][0].update(offering_id='other'), 'phases')

    def test_stale_miro_export(self):
        self.reject(lambda fixture: fixture.export.update(captured_at=(fixture.now - datetime.timedelta(days=2)).isoformat()), 'phases')

    def test_two_divergence_captures(self):
        self.reject(lambda fixture: fixture.ledger['divergence'].pop(), 'phases')

    def test_static_scroll(self):
        self.fixture.browser['scroll']['samples'][1]['state'] = self.fixture.browser['scroll']['samples'][0]['state']
        self.fixture.sign(self.private)
        with self.assertRaisesRegex(ValueError, 'does not react'):
            self.evidence().motion('scroll')

    def test_static_scroll_with_changing_capture_metadata(self):
        for number, sample in enumerate(self.fixture.browser['scroll']['samples']):
            sample['state'] = {'opacity': 0.5, 'capture_id': f'frame-{number}', 'timestamp': number}
        self.fixture.sign(self.private)
        with self.assertRaisesRegex(ValueError, 'does not react'):
            self.evidence().motion('scroll')

    def test_scroll_capture_metadata_is_not_measured_style(self):
        for number, sample in enumerate(self.fixture.browser['scroll']['samples']):
            sample['state'] = {'capture_id': f'frame-{number}', 'timestamp': number}
        self.fixture.sign(self.private)
        with self.assertRaisesRegex(ValueError, 'no measured target style'):
            self.evidence().motion('scroll')

    def test_static_scroll_numeric_encoding_is_not_motion(self):
        for number, sample in enumerate(self.fixture.browser['scroll']['samples']):
            sample['state'] = {'opacity': 0 if number % 2 == 0 else 0.0}
        self.fixture.sign(self.private)
        with self.assertRaisesRegex(ValueError, 'does not react'):
            self.evidence().motion('scroll')

    def test_scroll_measurement_fields_cannot_alternate(self):
        for number, sample in enumerate(self.fixture.browser['scroll']['samples']):
            sample['state'] = {'opacity': 0} if number % 2 == 0 else {'transform': 'none'}
        self.fixture.sign(self.private)
        with self.assertRaisesRegex(ValueError, 'fields must remain consistent'):
            self.evidence().motion('scroll')

    def test_equivalent_transform_encodings_are_not_scroll_motion(self):
        encodings = ['none', 'matrix(1,0,0,1,0,0)', 'matrix3d(1,0,0,0,0,1,0,0,0,0,1,0,0,0,0,1)']
        for number, sample in enumerate(self.fixture.browser['scroll']['samples']):
            sample['state'] = {'transform': encodings[number % len(encodings)]}
        self.fixture.sign(self.private)
        with self.assertRaisesRegex(ValueError, 'does not react'):
            self.evidence().motion('scroll')

    def test_static_perspective(self):
        self.fixture.browser['three_d']['samples'][1]['state'] = self.fixture.browser['three_d']['samples'][0]['state']
        self.fixture.sign(self.private)
        with self.assertRaisesRegex(ValueError, 'does not react'):
            self.evidence().motion('three_d')

    def test_pointer_only_css3d_does_not_prove_scroll(self):
        for number, sample in enumerate(self.fixture.browser['three_d']['samples']):
            sample['input'].pop('scroll_y', None)
            sample['input']['pointer'] = [number * 100, 50]
        self.fixture.sign(self.private)
        with self.assertRaisesRegex(ValueError, 'actual scroll positions'):
            self.evidence().motion('three_d')

    def test_changed_pointer_confounds_3d_scroll(self):
        for number, sample in enumerate(self.fixture.browser['three_d']['samples']):
            sample['input']['pointer'] = [number * 100, 50]
        self.fixture.sign(self.private)
        with self.assertRaisesRegex(ValueError, 'fixed pointer'):
            self.evidence().motion('three_d')

    def test_static_3d_depth_with_only_opacity_change_fails(self):
        transform = self.fixture.browser['three_d']['samples'][1]['state']['transform']
        for number, sample in enumerate(self.fixture.browser['three_d']['samples']):
            sample['state'] = {'transform': transform, 'opacity': number}
        self.fixture.sign(self.private)
        with self.assertRaisesRegex(ValueError, 'does not react'):
            self.evidence().motion('three_d')

    def test_webgl_scroll_positive_fixture_and_fallback(self):
        self.fixture.browser['three_d'].update(kind='webgl', rendered_frames=2, fallback_tested=True, fallback_usable=True)
        for sample in self.fixture.browser['three_d']['samples']:
            sample['state'] = {'world_matrix': list(map(float, sample['state']['transform'].removeprefix('matrix3d(').removesuffix(')').split(',')))}
        self.fixture.sign(self.private)
        self.assertTrue(self.evidence().motion('three_d'))
        self.fixture.browser['three_d']['fallback_usable'] = False
        self.fixture.sign(self.private)
        with self.assertRaisesRegex(ValueError, 'usable fallback'):
            self.evidence().motion('three_d')

    def test_static_webgl_with_changing_frame_metadata(self):
        observation = self.fixture.browser['three_d']
        observation.update(kind='webgl', rendered_frames=4, fallback_tested=True, fallback_usable=True)
        for number, sample in enumerate(observation['samples']):
            sample['state'] = {'world_matrix': [1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1], 'frame_id': number}
        self.fixture.sign(self.private)
        with self.assertRaisesRegex(ValueError, 'does not react'):
            self.evidence().motion('three_d')

    def test_static_webgl_numeric_encoding_is_not_motion(self):
        observation = self.fixture.browser['three_d']
        observation.update(kind='webgl', rendered_frames=4, fallback_tested=True, fallback_usable=True)
        for number, sample in enumerate(observation['samples']):
            sample['state'] = {'world_matrix': [0 if number % 2 == 0 else 0.0] * 16}
        self.fixture.sign(self.private)
        with self.assertRaisesRegex(ValueError, 'does not react'):
            self.evidence().motion('three_d')

    def test_webgl_measurement_fields_cannot_alternate(self):
        observation = self.fixture.browser['three_d']
        observation.update(kind='webgl', rendered_frames=4, fallback_tested=True, fallback_usable=True)
        for number, sample in enumerate(observation['samples']):
            sample['state'] = {('world_matrix' if number % 2 == 0 else 'view_projection_matrix'): [0] * 16}
        self.fixture.sign(self.private)
        with self.assertRaisesRegex(ValueError, 'fields must remain consistent'):
            self.evidence().motion('three_d')

    def test_reduced_motion_content_missing(self):
        self.reject(lambda fixture: fixture.browser['reduced_motion'][0].update(content_visible=False), 'reduced_motion')

    def test_reduced_motion_mobile_missing(self):
        self.reject(lambda fixture: fixture.browser['reduced_motion'].pop(0), 'reduced_motion')

    def test_disabled_cta(self):
        self.reject(lambda fixture: fixture.browser['cta'][0].update(enabled=False), 'cta')

    def test_occluded_cta(self):
        self.reject(lambda fixture: fixture.browser['cta'][0].update(hit_target=False), 'cta')

    def test_late_cta_clock(self):
        self.reject(lambda fixture: fixture.browser['cta'][0].update(clock_origin='after-tab-open'), 'cta')

    def test_boolean_cta_timing(self):
        self.reject(lambda fixture: fixture.browser['cta'][0].update(clickable_ms=True), 'cta')

    def test_lighthouse_other_url(self):
        self.reject(lambda fixture: fixture.lighthouse.update(finalDisplayedUrl='https://other.test/'), 'lighthouse')

    def test_stale_lighthouse(self):
        self.reject(lambda fixture: fixture.lighthouse.update(fetchTime=(fixture.now - datetime.timedelta(hours=2)).isoformat()), 'lighthouse')

    def test_desktop_lighthouse(self):
        self.reject(lambda fixture: fixture.lighthouse['configSettings'].update(formFactor='desktop'), 'lighthouse')

    def test_failed_lighthouse(self):
        self.reject(lambda fixture: fixture.lighthouse.update(runtimeError={'code': 'NO_FCP'}), 'lighthouse')

    def test_infinite_lighthouse(self):
        self.reject(lambda fixture: fixture.lighthouse['categories']['performance'].update(score=float('inf')), 'lighthouse')

    def test_padded_non_png(self):
        self.reject(lambda fixture: fixture.write('evidence/mobile-390.png', 'fake' * 10000), 'screenshots')

    def test_tiny_png(self):
        self.reject(lambda fixture: fixture.png('evidence/mobile-390.png', 2, 2), 'screenshots')

    def test_capture_other_build(self):
        self.reject(lambda fixture: fixture.receipt['captures']['evidence/mobile-390.png'].update(build_sha256='wrong'), 'screenshots')

    def test_unresolved_critique_blocker(self):
        self.reject(lambda fixture: fixture.critique['findings'][0].update(severity='blocker', resolved=False), 'critique')

    def test_missing_critique_findings(self):
        self.reject(lambda fixture: fixture.critique.update(findings=[]), 'critique')

    def test_unknown_critique_severity(self):
        self.reject(lambda fixture: fixture.critique['findings'][0].update(severity='fatal-but-ignored'), 'critique')

    def test_critique_self_review(self):
        self.reject(lambda fixture: fixture.critique.update(verifier_id='test-builder'), 'critique')

    def test_boolean_viewport(self):
        self.reject(lambda fixture: fixture.probe.update(scroll_w_390=True))

    def test_incomplete_images(self):
        self.reject(lambda fixture: fixture.probe.update(images_complete=False))

    def test_artifact_removed_after_pass(self):
        self.fixture.sign(self.private)
        evidence = self.evidence()
        self.assertTrue(evidence.unchanged())
        (self.fixture.site / 'discover.md').unlink()
        with self.assertRaisesRegex(ValueError, 'missing artifact'):
            evidence.unchanged()

    def test_entrypoint_valid_fixture_and_low_actual_lighthouse(self):
        self.fixture.sign(self.private)
        argv = ['gate.py', self.fixture.slug, '--root', str(self.fixture.root), '--verifier-key', str(self.public)]
        def run():
            with patch.object(sys, 'argv', argv), patch.object(gate, 'jev_noul', return_value=(0.99, 'fixture', {})), \
                    patch.object(gate.urllib.request, 'urlopen') as request, contextlib.redirect_stdout(io.StringIO()):
                request.return_value.status = 200
                request.return_value.geturl.return_value = self.fixture.url
                with self.assertRaises(SystemExit) as result:
                    gate.main()
                return result.exception.code, json.loads((self.fixture.site / 'evidence/gate-result.json').read_text())
        code, result = run()
        self.assertEqual(code, 0, result)
        self.fixture.lighthouse['categories']['performance']['score'] = 0.1
        self.fixture.probe['lighthouse'] = {'performance': 100, 'accessibility': 100}
        self.fixture.sign(self.private)
        code, result = run()
        self.assertEqual(code, 1)
        self.assertFalse(next(item for item in result['results'] if item['id'] == 'C10')['pass'])
        self.fixture.lighthouse['categories']['performance']['score'] = 0.85
        self.fixture.sign(self.private)
        with patch.object(sys, 'argv', argv), patch.object(gate, 'jev_noul', return_value=(0.99, 'fixture', {})), \
                patch.object(gate.urllib.request, 'urlopen') as request, contextlib.redirect_stdout(io.StringIO()):
            request.return_value.status = 200
            request.return_value.geturl.return_value = 'https://authentication.example.test/'
            with self.assertRaises(SystemExit) as redirected:
                gate.main()
        self.assertEqual(redirected.exception.code, 1)
        report = json.loads((self.fixture.site / 'evidence/gate-result.json').read_text())
        self.assertFalse(next(item for item in report['results'] if item['id'] == 'C23')['pass'])

    def test_dry_run_pass_and_failed_quality_preserve_workspace(self):
        for performance, expected_code in [(0.85, 0), (0.1, 1)]:
            with self.subTest(performance=performance):
                self.fixture.lighthouse['categories']['performance']['score'] = performance
                self.fixture.sign(self.private)
                result_path = self.fixture.site / 'evidence/gate-result.json'
                result_path.write_text('{"verdict":"PASS","criteria_version":"v1"}')
                before = workspace_snapshot(self.fixture.root)
                output = io.StringIO()
                argv = ['gate.py', self.fixture.slug, '--root', str(self.fixture.root), '--verifier-key', str(self.public), '--dry-run']
                with patch.object(sys, 'argv', argv), patch.object(gate, 'jev_noul', return_value=(0.99, 'fixture', {})), \
                        patch.object(gate.urllib.request, 'urlopen') as request, patch.object(gate, 'airtable') as provider_write, \
                        contextlib.redirect_stdout(output), self.assertRaises(SystemExit) as outcome:
                    request.return_value.status = 200
                    request.return_value.geturl.return_value = self.fixture.url
                    gate.main()
                report = json.loads(output.getvalue())
                self.assertEqual(outcome.exception.code, expected_code, report)
                self.assertEqual(report['verdict'], 'PASS' if expected_code == 0 else 'FAIL')
                self.assertEqual(report['total'], 30)
                self.assertTrue(report['dry_run'])
                provider_write.assert_not_called()
                self.assertEqual(workspace_snapshot(self.fixture.root), before)

    def test_dry_run_rejects_airtable_before_any_evaluation(self):
        before = workspace_snapshot(self.fixture.root)
        argv = ['gate.py', self.fixture.slug, '--root', str(self.fixture.root), '--dry-run', '--airtable-record', 'rec-fixture']
        with patch.object(sys, 'argv', argv), patch.object(gate, 'Evidence') as evidence, patch.object(gate, 'airtable') as provider_write, \
                contextlib.redirect_stderr(io.StringIO()), self.assertRaises(SystemExit) as outcome:
            gate.main()
        self.assertEqual(outcome.exception.code, 2)
        evidence.assert_not_called()
        provider_write.assert_not_called()
        self.assertEqual(workspace_snapshot(self.fixture.root), before)

    def test_dry_run_cli_missing_trust_and_wrapper_preserve_workspace(self):
        wrapper = SCRIPTS.parents[1] / 'client-mirror-site/scripts/gate.py'
        for entrypoint in [SCRIPTS / 'gate.py', wrapper]:
            with self.subTest(entrypoint=str(entrypoint)):
                before = workspace_snapshot(self.fixture.root)
                result = subprocess.run([sys.executable, str(entrypoint), self.fixture.slug, '--root', str(self.fixture.root), '--dry-run'],
                                        capture_output=True, text=True, timeout=20)
                self.assertEqual(result.returncode, 1, result.stderr)
                report = json.loads(result.stdout)
                self.assertEqual(report['results'][0]['id'], 'C00')
                self.assertEqual(report['verdict'], 'FAIL')
                self.assertTrue(report['dry_run'])
                self.assertEqual(workspace_snapshot(self.fixture.root), before)

    def test_dry_run_has_no_output_path_escape_hatch(self):
        target = self.fixture.site / 'evidence/gate-result.json'
        target.write_text('{"verdict":"PASS"}')
        symlink = self.fixture.root / 'output-symlink'
        symlink.symlink_to(target)
        hardlink = self.fixture.root / 'output-hardlink'
        os.link(target, hardlink)
        for destination in [target, symlink, hardlink, self.fixture.root, self.fixture.root / 'new-result.json']:
            with self.subTest(destination=str(destination)):
                before = workspace_snapshot(self.fixture.root)
                result = subprocess.run([sys.executable, str(SCRIPTS / 'gate.py'), self.fixture.slug, '--root', str(self.fixture.root),
                                         '--dry-run', '--output', str(destination)], capture_output=True, text=True, timeout=20)
                self.assertEqual(result.returncode, 2, result.stderr)
                self.assertIn('unrecognized arguments: --output', result.stderr)
                self.assertEqual(workspace_snapshot(self.fixture.root), before)

    def test_dry_run_portfolio_real_child_failure_preserves_workspace(self):
        before = workspace_snapshot(self.fixture.root)
        slugs = [self.fixture.slug, *[f'offering-{index}' for index in range(9)]]
        result = subprocess.run([sys.executable, str(SCRIPTS / 'gate.py'), '--root', str(self.fixture.root), '--verifier-key', str(self.public),
                                 '--dry-run', '--portfolio', *slugs], capture_output=True, text=True, timeout=20)
        self.assertEqual(result.returncode, 1, result.stderr)
        report = json.loads(result.stdout)
        self.assertEqual(report['verdict'], 'FAIL')
        self.assertTrue(report['dry_run'])
        self.assertIn('fresh gate failed', report['detail'])
        self.assertEqual(workspace_snapshot(self.fixture.root), before)

    def test_dry_run_portfolio_propagates_mode_to_every_child(self):
        slugs = [f'offering-{index}' for index in range(10)]
        with patch.object(gate.subprocess, 'run') as child, patch.object(gate, 'Evidence'), \
                patch.object(gate, 'distinct_offerings', return_value=10), contextlib.redirect_stdout(io.StringIO()) as output:
            child.return_value.returncode = 0
            self.assertEqual(gate.portfolio(self.fixture.root, slugs, self.public, dry_run=True), 10)
        self.assertEqual(child.call_count, 10)
        for invocation in child.call_args_list:
            self.assertIn('--dry-run', invocation.args[0])
            self.assertNotIn('--airtable-record', invocation.args[0])
        self.assertEqual(json.loads(output.getvalue())['verdict'], 'PASS')

    def test_failed_recheck_clears_airtable_done_without_provider_write(self):
        out = {'verdict': 'FAIL', 'passed': 0, 'total': 1, 'at': self.fixture.time, 'vercel_url': '',
               'results': [{'id': 'C00', 'pass': False}]}
        with patch('builtins.open', mock_open(read_data='AIRTABLE_CC_PAT=test-only-nonsecret\nAIRTABLE_CC_BASE=fixture-base\n')), \
                patch.object(gate.urllib.request, 'urlopen', return_value=io.StringIO('{"fields":{"Status":"In progress","Done":false}}')) as request, \
                contextlib.redirect_stdout(io.StringIO()):
            gate.airtable('rec-fixture', out, str(self.fixture.site))
        payload = json.loads(request.call_args.args[0].data)
        self.assertFalse(payload['fields']['Done'])
        self.assertEqual(payload['fields']['Status'], 'In progress')

    def test_same_client_distinct_offerings_and_renamed_clone(self):
        self.fixture.sign(self.private)
        second = EvidenceFixture(self.directory.name, 'transformfit-retention')
        second.sign(self.private)
        second_evidence = Evidence(second.root, second.slug, self.public)
        self.assertEqual(distinct_offerings([self.evidence(), second_evidence], minimum=2), 2)
        second.manifest['solution']['mechanism'] = self.fixture.manifest['solution']['mechanism']
        second.sign(self.private)
        with self.assertRaisesRegex(ValueError, 'duplicate/renamed'):
            distinct_offerings([self.evidence(), Evidence(second.root, second.slug, self.public)], minimum=2)


class CounterfeitRegression(unittest.TestCase):
    def test_builder_reports_empty_phases_and_padded_images_cannot_pass(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            site = root / 'sites/example'
            (site / 'evidence').mkdir(parents=True)
            (site / 'app').mkdir()
            pins = root / '_inputs/pinterest/example'
            pins.mkdir(parents=True)
            (pins / 'hero.png').write_bytes(b'not an image')
            for phase in gate.PHASES:
                (site / f'{phase}.md').write_text('')
            (site / 'demand.md').write_text('rec1 rec2 rec3 waiting')
            (site / 'define.md').write_text('wow')
            (site / 'discover.md').write_text('https://example.test/a https://example.test/b')
            (site / 'deliver.md').write_text('https://example.test/preview')
            (site / 'critique.md').write_text('SCORE: 10/10')
            (site / 'claims.md').write_text('')
            (site / 'app/index.html').write_text('<!-- ScrollTrigger perspective: prefers-reduced-motion -->')
            for name in ('desktop-1440.png', 'mobile-390.png'):
                (site / 'evidence' / name).write_bytes(b'fake' * 6000)
            probe = {
                'hero': {'pinterest_source': 'hero.png', 'height_ratio': 0.8},
                'cta': {'text': 'Start', 'clickable_ms': 1}, 'text': 'Start Start',
                'pain_cards': [{'record_id': f'rec{number}'} for number in range(1, 4)],
                'wow_id': 'wow', 'wow_present': True, 'lighthouse': {'performance': 100, 'accessibility': 100},
                'scroll_w_390': 390, 'scroll_w_1440': 1440,
                'links': {'total': 1, 'bad': 0, 'empty_href': 0}, 'broken_images': 0,
                'fonts': ['Arial'], 'vercel_url': 'https://example.test/preview',
            }
            (site / 'evidence/probe.json').write_text(json.dumps(probe))
            (site / 'evidence/gate-result.json').write_text('{"verdict":"PASS"}')
            with patch.object(gate, 'ROOT', str(root)), patch.object(sys, 'argv', ['gate.py', 'example']), \
                    patch.object(gate, 'jev_noul', return_value=(0.99, 'test-double', {})), \
                    patch.object(gate.urllib.request, 'urlopen') as request, contextlib.redirect_stdout(io.StringIO()):
                request.return_value.status = 200
                with self.assertRaises(SystemExit) as result:
                    gate.main()
            self.assertEqual(result.exception.code, 1)
            self.assertEqual(json.loads((site / 'evidence/gate-result.json').read_text())['verdict'], 'FAIL')


if __name__ == '__main__':
    unittest.main()
