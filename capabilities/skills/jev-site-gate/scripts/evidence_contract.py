import datetime
import hashlib
import json
import math
from pathlib import Path
import re
import subprocess
from urllib.parse import urlsplit


VERSION = 'rig.site-evidence.v2'
PHASES = ('discover', 'define', 'gate', 'diverge', 'develop', 'deliver', 'measure')
BOARD_ID = 'uXjVEez017g='
TRUSTED_VERIFIERS = {}


def require(condition, message):
    if not condition:
        raise ValueError(message)


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def build_digest(site):
    app = Path(site) / 'app'
    files = sorted(path for path in app.rglob('*') if path.is_file()
                   and not {'node_modules', '.git', '.next'}.intersection(path.relative_to(app).parts))
    require(files, 'empty build')
    require(not any(path.is_symlink() for path in app.rglob('*')), 'build symlink')
    return hashlib.sha256(json.dumps([(str(path.relative_to(app)), digest(path)) for path in files],
                                    separators=(',', ':')).encode()).hexdigest()


def local_file(root, name):
    require(isinstance(name, str) and name and not Path(name).is_absolute(), 'artifact path must be relative')
    path = Path(root) / name
    require(path.resolve().is_relative_to(Path(root).resolve()), 'artifact outside root')
    require(path.is_file() and not path.is_symlink(), f'missing artifact: {name}')
    return path


def timestamp(value):
    parsed = datetime.datetime.fromisoformat(value.replace('Z', '+00:00'))
    require(parsed.tzinfo is not None, 'timestamp needs timezone')
    return parsed


def read_json(path):
    return json.loads(Path(path).read_text())


def pointer(value, locator):
    require(isinstance(locator, str) and locator.startswith('/'), 'source needs JSON pointer')
    for part in locator[1:].split('/'):
        require(not re.search(r'~(?![01])', part), 'invalid JSON pointer escape')
        part = part.replace('~1', '/').replace('~0', '~')
        if isinstance(value, list):
            require(re.fullmatch(r'0|[1-9][0-9]*', part), 'noncanonical array index in JSON pointer')
            value = value[int(part)]
        else:
            value = value[part]
    return value


def finite_number(value):
    return type(value) in (int, float) and math.isfinite(value)


def measured_state(name, observation, sample):
    state = sample['state']
    if name == 'scroll':
        measured = {}
        if 'opacity' in state:
            require(finite_number(state['opacity']) and 0 <= state['opacity'] <= 1, 'invalid observed opacity')
            measured['opacity'] = state['opacity']
        if 'transform' in state:
            transform = state['transform']
            if transform == 'none':
                measured['transform'] = [1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1]
            else:
                match = re.fullmatch(r'(matrix|matrix3d)\(([^)]+)\)', transform)
                require(match, 'invalid observed transform')
                values = [float(value) for value in match.group(2).split(',')]
                require(len(values) == (6 if match.group(1) == 'matrix' else 16)
                        and all(math.isfinite(value) for value in values), 'invalid transform matrix')
                if len(values) == 6:
                    values = [values[0], values[1], 0, 0, values[2], values[3], 0, 0,
                              0, 0, 1, 0, values[4], values[5], 0, 1]
                measured['transform'] = values
        require(measured, 'scroll has no measured target style')
        return measured
    if observation['kind'] == 'css3d':
        match = re.fullmatch(r'matrix3d\(([^)]+)\)', state['transform'])
        require(match, 'CSS 3D needs computed matrix3d')
        values = [float(value) for value in match.group(1).split(',')]
        require(len(values) == 16 and all(math.isfinite(value) for value in values), 'invalid CSS3D matrix')
        return {'transform': values}
    measured = {key: state[key] for key in ('world_matrix', 'view_projection_matrix') if key in state}
    require(measured and all(isinstance(values, list) and len(values) == 16
                            and all(finite_number(value) for value in values) for values in measured.values()),
            'WebGL needs measured scene/camera matrix; frame metadata is not target state')
    return measured


def state_changed(first, second):
    for key in first:
        left = first[key] if isinstance(first[key], list) else [first[key]]
        right = second[key] if isinstance(second[key], list) else [second[key]]
        if any(abs(before - after) > 0.00001 for before, after in zip(left, right)):
            return True
    return False


class Evidence:
    def __init__(self, root, slug, verifier_key, now=None):
        self.root = Path(root).resolve()
        require(bool(re.fullmatch(r'[a-z0-9][a-z0-9-]*', slug)), 'invalid offering slug')
        self.site = self.root / 'sites' / slug
        require(self.site.resolve().is_relative_to(self.root / 'sites'), 'site outside root')
        require(verifier_key, 'operator-trusted --verifier-key required')
        key = Path(verifier_key).resolve()
        require(not key.is_relative_to(self.root), 'verifier key must be outside builder workspace')
        require(TRUSTED_VERIFIERS, 'no authorized site QA verifier trust root configured; candidate cannot certify')
        principal = TRUSTED_VERIFIERS.get(digest(key))
        require(principal, 'caller-selected verifier key is not an authorized trust root')
        receipt_path = local_file(self.site, 'evidence/verifier-receipt.json')
        signature = local_file(self.site, 'evidence/verifier-receipt.sig')
        verified = subprocess.run(['openssl', 'dgst', '-sha256', '-verify', str(key), '-signature',
                                   str(signature), str(receipt_path)], capture_output=True, timeout=10)
        require(verified.returncode == 0, 'invalid verifier signature')
        self.receipt = read_json(receipt_path)
        receipt = self.receipt
        require(receipt['verifier'] == principal, 'receipt verifier does not match authorized signer')
        require(receipt['schema'] == VERSION and receipt['offering_id'] == slug, 'wrong receipt schema/offering')
        require(receipt['builder']['id'] and receipt['verifier']['id']
                and receipt['builder']['id'] != receipt['verifier']['id'], 'builder self-review')
        require(receipt['builder']['family'] and receipt['verifier']['family']
                and receipt['builder']['family'] != receipt['verifier']['family'], 'verifier family must differ')
        self.captured_at = timestamp(receipt['captured_at'])
        now = now or datetime.datetime.now(datetime.timezone.utc)
        require(datetime.timedelta(0) <= now - self.captured_at <= datetime.timedelta(hours=24), 'stale/future receipt')
        require(receipt['build_sha256'] == build_digest(self.site), 'build changed after capture')
        self.key_sha256 = digest(key)
        self.receipt_sha256 = digest(receipt_path)
        self.artifacts = receipt['artifacts']
        require(isinstance(self.artifacts, dict) and self.artifacts, 'empty artifact binding')
        for name in self.artifacts:
            self.bound(name)
        for name in ('offering.json', 'demand.md', 'claims.md', 'critique.md', *[f'{phase}.md' for phase in PHASES]):
            self.bound(name)
        self.probe = self.json('evidence/probe.json')
        self.manifest = self.json('offering.json')
        require(self.probe['url'] == receipt['url'] == self.probe['vercel_url'], 'probe URL mismatch')
        require(receipt['url'].startswith(('http://', 'https://')), 'invalid served URL')
        require(all(finite_number(self.probe[name]) and self.probe[name] > 0 for name in ('scroll_w_390', 'scroll_w_1440')), 'invalid viewport measurement')
        require(finite_number(self.probe['hero']['height_ratio']) and self.probe['hero']['height_ratio'] > 0, 'invalid hero measurement')
        require(type(self.probe['broken_images']) is int and self.probe['broken_images'] >= 0, 'invalid image count')
        require(self.probe['images_complete'] is True, 'images have not loaded')
        require(all(type(self.probe['links'][name]) is int and self.probe['links'][name] >= 0 for name in ('total', 'bad', 'empty_href')), 'invalid link counts')
        self.browser = self.json('evidence/browser.json')
        require(self.browser['url'] == receipt['url'] and self.browser['build_sha256'] == receipt['build_sha256'],
                'browser URL/build mismatch')
        require(self.browser['runtime_errors'] == [], 'browser runtime errors')
        trace = self.json('evidence/tool-trace.json')
        require(trace['session_id'] == self.browser['session_id'] == receipt['session_id'], 'capture session mismatch')
        kinds = {event['kind'] for event in trace['events']}
        require({'navigation', 'scroll', 'pointer', 'reduced-motion', 'cta-click', 'screenshot', 'lighthouse'} <= kinds,
                'missing execution trace events')

    def bound(self, name):
        require(name in self.artifacts, f'unbound artifact: {name}')
        path = local_file(self.site, name)
        require(digest(path) == self.artifacts[name], f'artifact hash mismatch: {name}')
        return path

    def json(self, name):
        return read_json(self.bound(name))

    def source(self, reference):
        path = self.bound(reference['path'])
        require(digest(path) == reference['sha256'], 'source hash mismatch')
        return pointer(read_json(path), reference['locator'])

    def offering(self):
        manifest = self.manifest
        require(manifest['schema'] == VERSION and manifest['offering_id'] == self.receipt['offering_id'], 'wrong offering identity')
        client = manifest['client']
        require(client['id'].strip() and client['name'].strip(), 'missing actual client identity')
        require(manifest['brand_owner_id'] == client['id'], 'offering must use client brand')
        brand = re.sub(r'[^a-z0-9]', '', client['name'].lower())
        require(brand not in {'rig', 'ri', 'rodgersintelligence', 'rodgersintelligencegroup'}
                and not client['id'].lower().startswith(('rig-', 'ri-')), 'RIG-branded offering does not count')
        identity = self.source(client['identity_source'])
        require(client['name'] in str(identity), 'identity evidence does not name client')
        require(client['identity_kind'] in {'client', 'user-named-project'}, 'unknown identity kind')
        if client['identity_kind'] == 'user-named-project':
            require(client['identity_source']['authority'] == 'mike-direct', 'project needs direct user identity evidence')
        solution = manifest['solution']
        require(solution['id'].strip() and solution['mechanism'].strip() and solution['problem'].strip(), 'empty solution')
        require(solution['status'] in {'proposed', 'verified'}, 'preserve solution status')
        sources = manifest['sources']
        require(len(sources) >= 3 and len({source['id'] for source in sources}) == len(sources), 'three distinct pain sources required')
        reviews = self.receipt['source_reviews']
        raw_records, raw_locations = set(), set()
        for source in sources:
            value = self.source(source['artifact'])
            require(isinstance(value, str) and source['quote'].strip() and source['quote'] in value,
                    'source quote missing at string field locator')
            require(source['record_id'] and source['run_id'], 'missing source record/run')
            raw = read_json(self.bound(source['artifact']['path']))
            native_id = pointer(raw, source['record_locator'])
            require(type(native_id) in (str, int) and str(native_id) == source['record_id'], 'record ID not present in raw source')
            quote_locator = source['artifact']['locator']
            record_locator = source['record_locator'].rsplit('/', 1)[0]
            record = pointer(raw, record_locator) if record_locator else raw
            require(isinstance(record, dict) and quote_locator.startswith(record_locator + '/'),
                    'record ID and quote are from different raw records')
            raw_record = (source['kind'], str(native_id))
            raw_location = (source['artifact']['sha256'], record_locator)
            require(raw_record not in raw_records and raw_location not in raw_locations, 'duplicate raw source record/locator')
            raw_records.add(raw_record)
            raw_locations.add(raw_location)
            run = self.source(source['run_receipt'])
            require(run['run_id'] == source['run_id'] and run['provider'] == source['kind']
                    and run['status'] == 'success' and run['response_sha256'] == source['artifact']['sha256'], 'source run chain mismatch')
            review = reviews[source['id']]
            require(review['client_id'] == client['id'] and review['solution_id'] == solution['id']
                    and review['relevant'] is True and len(review['rationale'].strip()) >= 20, 'unreviewed source relevance')
            require(source['scope'] in {'client', 'category'}, 'unknown source scope')
            require(source['kind'] in {'socialfetch', 'airtable'}, 'unsupported pain source')
        source_ids = {source['id'] for source in sources}
        require(solution['source_ids'] and set(solution['source_ids']) <= source_ids, 'unbound solution sources')
        require(any(source['kind'] == 'socialfetch' for source in sources), 'SocialFetch source chain required')
        cards = self.probe['pain_cards']
        records = {source['record_id'] for source in sources}
        require(len(cards) >= 3 and len({card['record_id'] for card in cards}) >= 3
                and all(card['record_id'] in records and card['pain'].strip() for card in cards), 'pain cards lack distinct source records/text')
        for card in cards:
            source = next(source for source in sources if source['record_id'] == card['record_id'])
            require(card['pain'] == source['quote'], 'pain card differs from source quote')
        for pin in manifest['pinterest']:
            host = urlsplit(pin['pin_url']).hostname or ''
            require(pin['pin_url'].startswith('https://') and host in {'pinterest.com', 'www.pinterest.com'}, 'pin needs exact source URL')
            require(pin['image_sha256'] == digest(self.bound(pin['image_path'])), 'pin image hash mismatch')
            require(pin['pin_url'] in str(self.source(pin['index_source'])), 'pin not in source index')
            require(len(pin['visual_decision'].strip()) >= 20, 'pin needs visual observation')
        require(manifest['pinterest'], 'no Pinterest references')
        require(self.probe['hero']['pinterest_source'] in {Path(pin['image_path']).name for pin in manifest['pinterest']}, 'hero not bound to referenced image')
        references = manifest['references']
        require(3 <= sum(reference['kind'] == 'mirror' for reference in references) <= 5
                and sum(reference['kind'] == 'award' for reference in references) >= 3, 'need 3-5 mirror and 3 award captures')
        require(len({reference['url'] for reference in references}) == len(references), 'duplicate reference URLs')
        for reference in references:
            require(reference['url'].startswith('https://') and reference['capture_url'] == reference['url'], 'reference capture URL mismatch')
            self.png(reference['artifact'])
        return True

    def phases(self):
        ledger = self.json('evidence/phase-ledger.json')
        export = self.json('evidence/miro-export.json')
        require(ledger['offering_id'] == self.manifest['offering_id'], 'phase offering mismatch')
        require(ledger['board_id'] == export['board_id'] == BOARD_ID, 'wrong Miro board')
        require(export['source_tool'] and export['capture_id'], 'Miro export lacks capture provenance')
        export_at = timestamp(export['captured_at'])
        require(datetime.timedelta(0) <= self.captured_at - export_at <= datetime.timedelta(hours=24), 'stale Miro export')
        entries = ledger['phases']
        require([entry['phase'] for entry in entries] == list(PHASES), 'missing/out-of-order phases')
        previous_time = None
        items = {item['id']: item for item in export['items']}
        require(len(items) == len(export['items']), 'duplicate Miro item')
        required = {
            'discover': {'offering.json', 'demand.md', *[pin['index_source']['path'] for pin in self.manifest['pinterest']]},
            'define': {'define.md', 'claims.md'},
            'gate': {'gate.md', 'evidence/brief-gate.json'},
            'diverge': {'diverge.md', *[direction['artifact'] for direction in ledger['divergence']]},
            'develop': {'develop.md', 'evidence/build-manifest.json'},
            'deliver': {'deliver.md', 'evidence/deployment.json'},
            'measure': {'measure.md', 'evidence/probe.json', 'evidence/browser.json', 'evidence/lighthouse.json',
                        'evidence/desktop-1440.png', 'evidence/mobile-390.png', 'evidence/critique.json'},
        }
        for index, entry in enumerate(entries):
            require(entry['status'] == 'completed' and entry['worker'], 'phase not executed')
            require(entry['previous'] == (PHASES[index - 1] if index else None), 'invalid phase predecessor')
            ended = timestamp(entry['completed_at'])
            require((previous_time is None or ended > previous_time) and ended <= export_at, 'phase timestamps out of order')
            previous_time = ended
            artifact = f"{entry['phase']}.md"
            require(artifact in entry['artifacts'] and self.bound(artifact).read_text().strip(), 'empty/missing phase artifact')
            require(required[entry['phase']] <= set(entry['artifacts']), 'phase lacks execution artifacts')
            require(entry['item_ids'], 'phase has no native Miro items')
            for item_id in entry['item_ids']:
                item = items[item_id]
                require(item['offering_id'] == ledger['offering_id'] and item['phase'] == entry['phase'], 'another offering/phase Miro item')
                require(ledger['offering_id'] in item['content'] and entry['phase'] in item['content'], 'Miro item content lacks offering/phase')
                require(all(self.artifacts[name] == item['artifact_hashes'][name] for name in entry['artifacts']), 'Miro artifact mismatch')
        directions = ledger['divergence']
        require(len(directions) == 3 and len({direction['artifact'] for direction in directions}) == 3, 'three distinct rendered directions required')
        require(len({self.artifacts[direction['artifact']] for direction in directions}) == 3, 'divergence captures repeat identical image')
        for direction in directions:
            self.png(direction['artifact'])
            require(direction['pin_url'] in {pin['pin_url'] for pin in self.manifest['pinterest']}
                    and direction['mirror_url'].startswith('https://'), 'divergence lacks references')
        require(ledger['selected_direction'] in {direction['artifact'] for direction in directions}
                and len(ledger['selection_rationale'].strip()) >= 20, 'missing source-linked selection')
        decisions = self.json('evidence/brief-gate.json')['decisions']
        require({decision['criterion'] for decision in decisions} == {'promise-pain', 'single-cta'}
                and all(decision['decision_id'] and decision['model'] and decision['provider'] == 'hosted-jev'
                        and finite_number(decision['score']) and 0.85 <= decision['score'] <= 1 for decision in decisions), 'brief gate lacks executed Jev decisions')
        require(self.json('evidence/build-manifest.json')['build_sha256'] == self.receipt['build_sha256'], 'phase build identity mismatch')
        deployment = self.json('evidence/deployment.json')
        require(deployment['url'] == self.receipt['url'] and deployment['build_sha256'] == self.receipt['build_sha256']
                and deployment['status'] == 200 and deployment['capture_id'], 'phase delivery lacks bound deployment evidence')
        return True

    def motion(self, name):
        observation = self.browser[name]
        require(observation['selector'] and observation['mechanism'], 'motion target/mechanism missing')
        samples = observation['samples']
        states = {id(sample): measured_state(name, observation, sample) for sample in samples}
        require(len(samples) >= 2, 'motion does not react')
        require(all(states[id(sample)].keys() == states[id(samples[0])].keys() for sample in samples),
                'motion measurement fields must remain consistent')
        require(any(state_changed(states[id(first)], states[id(second)]) for first in samples for second in samples),
                'motion does not react')
        require(len({json.dumps(sample['input'], sort_keys=True) for sample in samples}) >= 2, 'no input interaction')
        require({sample['viewport_width'] for sample in samples} == {390, 1440}, 'motion needs desktop/mobile')
        for width in (390, 1440):
            viewport_samples = [sample for sample in samples if sample['viewport_width'] == width]
            require(len(viewport_samples) >= 2
                    and any(state_changed(states[id(first)], states[id(second)])
                            for first in viewport_samples for second in viewport_samples)
                    and len({json.dumps(sample['input'], sort_keys=True) for sample in viewport_samples}) >= 2, 'motion does not react at each viewport')
            require(all(isinstance(sample['input'], dict) and finite_number(sample['input'].get('scroll_y'))
                        and sample['input']['scroll_y'] >= 0 for sample in viewport_samples), 'motion needs actual scroll positions')
            require(len({sample['input']['scroll_y'] for sample in viewport_samples}) >= 2, 'scroll position does not change')
            if name == 'three_d':
                require(any(first['input']['scroll_y'] != second['input']['scroll_y']
                            and {key: value for key, value in first['input'].items() if key != 'scroll_y'}
                            == {key: value for key, value in second['input'].items() if key != 'scroll_y'}
                            and state_changed(states[id(first)], states[id(second)])
                            for first in viewport_samples for second in viewport_samples),
                        '3D scroll response needs fixed pointer/control state')
        if name == 'three_d':
            require(observation['kind'] in {'css3d', 'webgl'}, 'unknown 3D kind')
            if observation['kind'] == 'css3d':
                require(all('matrix3d(' in sample['state']['transform'] for sample in samples), 'CSS 3D needs computed matrix3d')
                matrices = [list(map(float, sample['state']['transform'].removeprefix('matrix3d(').removesuffix(')').split(','))) for sample in samples]
                require(all(len(matrix) == 16 and all(math.isfinite(value) for value in matrix) for matrix in matrices)
                        and any(any(abs(matrix[index]) > 0.00001 for index in (2, 3, 6, 7, 8, 9, 11, 14)) for matrix in matrices), 'matrix3d only encodes 2D')
                for width in (390, 1440):
                    require(any(first['viewport_width'] == second['viewport_width'] == width
                                and first['input']['scroll_y'] != second['input']['scroll_y']
                                and {key: value for key, value in first['input'].items() if key != 'scroll_y'}
                                == {key: value for key, value in second['input'].items() if key != 'scroll_y'}
                                and any(abs(matrices[first_index][component] - matrices[second_index][component]) > 0.00001
                                        for component in (2, 3, 6, 7, 8, 9, 10, 11, 14))
                                for first_index, first in enumerate(samples) for second_index, second in enumerate(samples)),
                            'CSS 3D depth/rotation does not change with isolated scroll')
            else:
                require(observation['rendered_frames'] >= 2 and observation['fallback_tested'] is True
                        and observation['fallback_usable'] is True, 'WebGL needs rendered frames and usable fallback')
        return True

    def reduced_motion(self):
        observations = self.browser['reduced_motion']
        require({sample['viewport_width'] for sample in observations} == {390, 1440}, 'reduced motion needs desktop/mobile')
        for sample in observations:
            require(sample['emulated'] == 'reduce' and sample['motion_suppressed'] is True
                    and sample['content_visible'] is True and sample['cta_click_succeeded'] is True, 'unusable reduced-motion alternative')
        return True

    def cta(self):
        samples = self.browser['cta']
        require({sample['viewport_width'] for sample in samples} == {390, 1440}, 'CTA needs desktop/mobile')
        require(all(sample['visible'] is True and sample['enabled'] is True and sample['hit_target'] is True
                    and sample['click_succeeded'] is True and sample['expected_effect_observed'] is True
                    and sample['clock_origin'] == 'navigationStart' and finite_number(sample['clickable_ms'])
                    and 0 <= sample['clickable_ms'] <= 1000 for sample in samples), 'CTA interaction not proven')
        return True

    def lighthouse(self):
        report = self.json('evidence/lighthouse.json')
        require(report['finalDisplayedUrl'] == report['requestedUrl'] == self.receipt['url'], 'Lighthouse URL mismatch')
        require(abs(timestamp(report['fetchTime']) - self.captured_at) <= datetime.timedelta(hours=1), 'stale Lighthouse report')
        require(report['configSettings']['formFactor'] == 'mobile' and report['lighthouseVersion'], 'not a mobile Lighthouse capture')
        require(not report.get('runtimeError') and report['audits'], 'empty/failed Lighthouse report')
        scores = {name: report['categories'][name]['score'] for name in ('performance', 'accessibility')}
        require(all(finite_number(score) and 0 <= score <= 1 for score in scores.values()), 'invalid Lighthouse score')
        return {name: value * 100 for name, value in scores.items()}

    def png(self, name, width=None, height=None):
        from PIL import Image
        path = self.bound(name)
        with Image.open(path) as image:
            require(image.format == 'PNG', 'capture is not PNG')
            dimensions = image.size
            image.verify()
        with Image.open(path) as image:
            image.load()
        require((width is None or dimensions[0] == width) and (height is None or dimensions[1] >= height), 'wrong capture dimensions')
        return True

    def screenshots(self):
        captures = self.receipt['captures']
        for name, width, height in [('evidence/desktop-1440.png', 1440, 900), ('evidence/mobile-390.png', 390, 844)]:
            capture = captures[name]
            require(capture['url'] == self.receipt['url'] and capture['build_sha256'] == self.receipt['build_sha256']
                    and capture['viewport'] == [width, height] and capture['captured_at'] == self.receipt['captured_at'], 'capture provenance mismatch')
            self.png(name, width, height)
        return True

    def critique(self):
        critique = self.json('evidence/critique.json')
        require(critique['verifier_id'] == self.receipt['verifier']['id'], 'critique self-review/unbound reviewer')
        require(critique['screenshot_hashes'] == {name: self.artifacts[name] for name in self.receipt['captures']}, 'critique screenshot mismatch')
        require(finite_number(critique['score']) and 8 <= critique['score'] <= 10, 'visual score below 8/10')
        require(critique['findings'], 'empty critique')
        require(all(finding['severity'] in {'info', 'warning', 'blocker'} and finding['area'] and finding['observation'].strip()
                    and (finding['severity'] != 'blocker' or (finding['resolved'] is True and finding['retest_artifact']
                         and self.bound(finding['retest_artifact']))) for finding in critique['findings']), 'unresolved critique blocker')
        require({'mobile', 'desktop', 'keyboard', 'images', 'reduced-motion'} <= {finding['area'] for finding in critique['findings']}, 'incomplete rendered QA')
        return True

    def unchanged(self):
        require(digest(self.site / 'evidence/verifier-receipt.json') == self.receipt_sha256, 'receipt changed during gate')
        require(build_digest(self.site) == self.receipt['build_sha256'], 'build changed during gate')
        for name in self.artifacts:
            self.bound(name)
        return True


def distinct_offerings(evidence_list, minimum=10):
    require(len(evidence_list) >= minimum, f'at least {minimum} accepted offerings required')
    ids, solutions, mechanisms, builds = set(), set(), set(), set()
    for evidence in evidence_list:
        evidence.offering()
        evidence.phases()
        evidence.motion('scroll')
        evidence.motion('three_d')
        evidence.reduced_motion()
        evidence.cta()
        evidence.screenshots()
        evidence.critique()
        scores = evidence.lighthouse()
        require(scores['performance'] >= 80 and scores['accessibility'] >= 90, 'portfolio includes failed Lighthouse evidence')
        evidence.unchanged()
        manifest = evidence.manifest
        client = manifest['client']['id']
        solution = (client, manifest['solution']['id'])
        mechanism = (client, re.sub(r'\s+', ' ', manifest['solution']['mechanism'].strip().lower()))
        require(manifest['offering_id'] not in ids and solution not in solutions and mechanism not in mechanisms
                and evidence.receipt['build_sha256'] not in builds, 'duplicate/renamed offering cannot increase count')
        ids.add(manifest['offering_id'])
        solutions.add(solution)
        mechanisms.add(mechanism)
        builds.add(evidence.receipt['build_sha256'])
    return len(ids)
