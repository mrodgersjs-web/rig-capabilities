"""SQLite state machine for inventory, baseline parity, queue claims, and receipts."""
import hashlib
import json
import math
import re
import sqlite3
import time
import uuid
from contextlib import contextmanager
from pathlib import Path

from .registry import ACTIVE_STATES, GLOBAL_CAPACITY, INVENTORY_TTL_SECONDS, NODE_REGISTRY, public_node

JOB_STATES = ('queued', 'launching', 'running', 'succeeded', 'failed', 'blocked', 'cancelled')
TARGETS = ('auto', *NODE_REGISTRY)
CAPABILITIES = ('planner', 'provisioner', 'replication', 'repair', 'verifier', 'rollback')
KINDS = ('interactive', 'diagnostics', 'research', 'bulk_scan')


class FleetProblem(Exception):
    def __init__(self, message, status=400):
        super().__init__(message)
        self.status = status


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'), ensure_ascii=False, allow_nan=False)


def stamp():
    return time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())


def canonical_uuid(value, name='id'):
    if not isinstance(value, str):
        raise FleetProblem(f'{name} must be a canonical UUID.')
    try:
        if str(uuid.UUID(value)) != value: raise ValueError()
    except (ValueError, AttributeError):
        raise FleetProblem(f'{name} must be a canonical UUID.')
    return value


def bounded_text(value, name, maximum, required=True):
    if not isinstance(value, str) or '\x00' in value or len(value) > maximum or (required and not value.strip()):
        raise FleetProblem(f'{name} must be text from {1 if required else 0} to {maximum} characters.')
    try: value.encode('utf-8')
    except UnicodeEncodeError: raise FleetProblem(f'{name} contains invalid Unicode.')
    return value.strip() if required else value


def exact(value, fields):
    if not isinstance(value, dict) or set(value) != set(fields):
        raise FleetProblem('Fields must match: ' + ', '.join(sorted(fields)))


def validate_task(value):
    exact(value, {'task', 'target', 'writer_scope', 'idempotency_key', 'capability', 'kind'})
    task = bounded_text(value['task'], 'task', 12000)
    target = value['target']
    if target not in TARGETS: raise FleetProblem('target must be auto, local128, rig256gb, or rig96gb.')
    writer_scope = bounded_text(value['writer_scope'], 'writer_scope', 240, required=False)
    if writer_scope and not re.fullmatch(r'[A-Za-z0-9._/-]+', writer_scope):
        raise FleetProblem('writer_scope contains unsupported characters.')
    if writer_scope.startswith('/') or '..' in writer_scope.split('/'):
        raise FleetProblem('writer_scope must be a normalized relative ownership label.')
    key = canonical_uuid(value['idempotency_key'], 'idempotency_key')
    if value['capability'] not in CAPABILITIES: raise FleetProblem('Unknown capability.')
    if value['kind'] not in KINDS: raise FleetProblem('Unknown task kind.')
    if target == 'local128' and value['kind'] != 'interactive': raise FleetProblem('local128 accepts explicit interactive work only.')
    return {'task': task, 'target': target, 'writer_scope': writer_scope, 'idempotency_key': key, 'capability': value['capability'], 'kind': value['kind']}


class FleetStore:
    def __init__(self, path, baseline_hash):
        self.path, self.baseline_hash = Path(path), baseline_hash
        self.path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
        self.path.parent.chmod(0o700)
        with self.connect() as db:
            db.executescript('''
                CREATE TABLE IF NOT EXISTS fleet_inventory(
                  node_id TEXT PRIMARY KEY, observed_at INTEGER NOT NULL, expires_at INTEGER NOT NULL,
                  payload TEXT NOT NULL, evidence_hash TEXT NOT NULL, baseline_hash TEXT,
                  ready INTEGER NOT NULL CHECK(ready IN (0,1)), blocked_reason TEXT NOT NULL);
                CREATE TABLE IF NOT EXISTS fleet_jobs(
                  id TEXT PRIMARY KEY, idempotency_key TEXT UNIQUE NOT NULL, request_hash TEXT NOT NULL,
                  task TEXT NOT NULL, kind TEXT NOT NULL, target TEXT NOT NULL, node_id TEXT, writer_scope TEXT NOT NULL,
                  capability TEXT NOT NULL, baseline_hash TEXT NOT NULL,
                  state TEXT NOT NULL CHECK(state IN ('queued','launching','running','succeeded','failed','blocked','cancelled')),
                  attempt INTEGER NOT NULL DEFAULT 0, claim_token TEXT, orca_task_id TEXT, dispatch_id TEXT, terminal_handle TEXT,
                  result_cursor TEXT,
                  created_at TEXT NOT NULL, updated_at TEXT NOT NULL, started_at TEXT, finished_at TEXT,
                  result TEXT NOT NULL DEFAULT '', error TEXT NOT NULL DEFAULT '', receipt TEXT NOT NULL DEFAULT '{}');
                CREATE INDEX IF NOT EXISTS fleet_jobs_state_idx ON fleet_jobs(state, created_at);
                CREATE INDEX IF NOT EXISTS fleet_jobs_node_idx ON fleet_jobs(node_id, state);
                CREATE TABLE IF NOT EXISTS fleet_control(key TEXT PRIMARY KEY, value TEXT NOT NULL);
            ''')
        self.path.chmod(0o600)

    @contextmanager
    def connect(self):
        db = sqlite3.connect(self.path, timeout=5)
        db.row_factory = sqlite3.Row
        try:
            with db: yield db
        finally: db.close()

    @staticmethod
    def _job(row):
        if row is None: return None
        item = dict(row)
        item['receipt'] = json.loads(item['receipt'])
        return item

    @staticmethod
    def _inventory(row):
        if row is None: return None
        item = dict(row); item['payload'] = json.loads(item['payload']); item['ready'] = bool(item['ready'])
        item['stale'] = item['expires_at'] <= int(time.time())
        if item['stale']:
            item['ready'] = False
            item['blocked_reason'] = 'Inventory evidence is stale.'
        return item

    def record_inventory(self, node_id, payload, ttl=INVENTORY_TTL_SECONDS):
        if node_id not in NODE_REGISTRY: raise FleetProblem('Unknown node.')
        if not isinstance(payload, dict): raise FleetProblem('Inventory evidence must be an object.')
        profile = NODE_REGISTRY[node_id]
        required = {'omp_version', 'node_version', 'python_version', 'orca_ready', 'baseline_hash', 'runtime_hash', 'model_route', 'capabilities', 'load', 'memory'}
        if set(payload) != required: raise FleetProblem('Inventory fields are incomplete.')
        reasons = []
        if payload['omp_version'] != profile.expected_omp: reasons.append(f'OMP {profile.expected_omp} required.')
        if payload['orca_ready'] is not True: reasons.append('Orca runtime is not ready.')
        if payload['baseline_hash'] != self.baseline_hash: reasons.append('Worker baseline is missing or drifted.')
        from .baseline import profile as worker_profile
        expected_profile = worker_profile()
        if payload['runtime_hash'] != expected_profile['runtime']['closure_sha256']: reasons.append('Worker runtime is missing or drifted.')
        route = payload['model_route']; expected_route = expected_profile['model_route']
        route_ok = (isinstance(route, dict)
            and set(route) == {'models_url', 'health_url', 'model_id', 'configured_model', 'catalog_http_status', 'health_http_status', 'catalog_available', 'runtime_healthy', 'error'}
            and route.get('models_url') == expected_route['models_url']
            and route.get('health_url') == expected_route['health_url']
            and route.get('model_id') == expected_route['model_id']
            and route.get('configured_model') == expected_profile['model']
            and route.get('catalog_http_status') == 200
            and route.get('health_http_status') == 200
            and route.get('catalog_available') is True
            and route.get('runtime_healthy') is True
            and route.get('error') == '')
        if not route_ok: reasons.append('Configured model catalog route is unavailable or mismatched.')
        capabilities = payload['capabilities']
        try:
            role_manifest = json.loads((Path(__file__).parent/'baseline/roles.json').read_text())
            declared_capabilities = json.loads((Path(__file__).parent/'baseline/capabilities.json').read_text())
            capability_ok = (isinstance(capabilities, dict) and capabilities.get('ready') is True
                and capabilities.get('parity_scope') == declared_capabilities['parity_scope']
                and capabilities.get('full_local128_session_parity') is declared_capabilities['full_local128_session_parity']
                and set(capabilities.get('roles', [])) == set(CAPABILITIES)
                and set(capabilities.get('skills', [])) == set(role_manifest['common_skills'])
                and set(capabilities.get('tools', [])) == set(role_manifest['required_tools'])
                and set(capabilities.get('executables', {})) == {'git', 'rg', 'python3'}
                and all(isinstance(value, str) and value for value in capabilities.get('executables', {}).values()))
        except (OSError, ValueError, KeyError, TypeError): capability_ok = False
        if not capability_ok: reasons.append('Required deep roles, skills, or tools are missing.')
        if not re.fullmatch(r'v\d+\.\d+\.\d+', str(payload['node_version'])): reasons.append('Node version is invalid.')
        if not re.fullmatch(r'\d+\.\d+\.\d+', str(payload['python_version'])): reasons.append('Python version is invalid.')
        try:
            if int(str(payload['node_version']).split('.')[0][1:]) < profile.minimum_node_major: reasons.append('Node version is below baseline.')
            if tuple(map(int, str(payload['python_version']).split('.')[:2])) < profile.minimum_python: reasons.append('Python version is below baseline.')
        except (ValueError, IndexError): reasons.append('Tool versions could not be parsed.')
        load, memory = payload['load'], payload['memory']
        load_ok = (isinstance(load, dict) and set(load) == {'one', 'cpu_count'}
            and isinstance(load['one'], (int, float)) and not isinstance(load['one'], bool)
            and math.isfinite(float(load['one'])) and 0 <= float(load['one']) <= 100000
            and isinstance(load['cpu_count'], int) and not isinstance(load['cpu_count'], bool) and 1 <= load['cpu_count'] <= 4096)
        memory_ok = (isinstance(memory, dict) and set(memory) == {'total_bytes', 'available_bytes'}
            and all(isinstance(memory[key], int) and not isinstance(memory[key], bool) for key in ('total_bytes', 'available_bytes'))
            and 0 < memory['total_bytes'] <= 2**60 and 0 <= memory['available_bytes'] <= memory['total_bytes'])
        if not load_ok: reasons.append('Host load evidence is invalid.')
        if not memory_ok: reasons.append('Host memory evidence is invalid.')
        now = int(time.time())
        try: encoded = canonical(payload)
        except (TypeError, ValueError): return self.record_inventory_failure(node_id, 'Inventory evidence was not finite canonical JSON.')
        evidence_hash = hashlib.sha256(encoded.encode()).hexdigest()
        with self.connect() as db:
            db.execute('''INSERT INTO fleet_inventory VALUES(?,?,?,?,?,?,?,?)
              ON CONFLICT(node_id) DO UPDATE SET observed_at=excluded.observed_at,expires_at=excluded.expires_at,payload=excluded.payload,
              evidence_hash=excluded.evidence_hash,baseline_hash=excluded.baseline_hash,ready=excluded.ready,blocked_reason=excluded.blocked_reason''',
              (node_id, now, now + ttl, encoded, evidence_hash, payload.get('baseline_hash'), not reasons, '; '.join(reasons)))
        return self.get_inventory(node_id)

    def record_inventory_failure(self, node_id, reason):
        if node_id not in NODE_REGISTRY: raise FleetProblem('Unknown node.')
        reason = bounded_text(reason, 'inventory failure', 1000)
        now = int(time.time()); payload = canonical({}); evidence_hash = hashlib.sha256(payload.encode()).hexdigest()
        with self.connect() as db:
            db.execute('''INSERT INTO fleet_inventory VALUES(?,?,?,?,?,?,?,?)
              ON CONFLICT(node_id) DO UPDATE SET observed_at=excluded.observed_at,expires_at=excluded.expires_at,payload=excluded.payload,
              evidence_hash=excluded.evidence_hash,baseline_hash=NULL,ready=0,blocked_reason=excluded.blocked_reason''',
              (node_id, now, now, payload, evidence_hash, None, 0, reason))
        return self.get_inventory(node_id)

    def get_inventory(self, node_id):
        if node_id not in NODE_REGISTRY: raise FleetProblem('Unknown node.')
        with self.connect() as db: return self._inventory(db.execute('SELECT * FROM fleet_inventory WHERE node_id=?', (node_id,)).fetchone())

    def nodes(self):
        with self.connect() as db:
            rows = {row['node_id']: self._inventory(row) for row in db.execute('SELECT * FROM fleet_inventory')}
        result = []
        for node_id, profile in NODE_REGISTRY.items():
            evidence = rows.get(node_id)
            result.append(public_node(profile) | {'inventory': evidence, 'ready': bool(evidence and evidence['ready']), 'blocked_reason': evidence['blocked_reason'] if evidence else 'No inventory evidence has been recorded.'})
        return result

    def request_inventory_refresh(self):
        value = stamp()
        with self.connect() as db: db.execute("INSERT INTO fleet_control VALUES('inventory_refresh_requested_at',?) ON CONFLICT(key) DO UPDATE SET value=excluded.value", (value,))
        return value

    def consume_inventory_refresh(self):
        with self.connect() as db:
            db.execute('BEGIN IMMEDIATE')
            row = db.execute("SELECT value FROM fleet_control WHERE key='inventory_refresh_requested_at'").fetchone()
            if row: db.execute("DELETE FROM fleet_control WHERE key='inventory_refresh_requested_at'")
            return row['value'] if row else None

    def configure_coordinator(self, handle, run_id):
        handle = bounded_text(handle, 'coordinator handle', 240)
        run_id = bounded_text(run_id, 'coordinator run id', 240)
        if not re.fullmatch(r'term_[A-Za-z0-9_-]+', handle) or not re.fullmatch(r'run_[A-Za-z0-9_-]+', run_id):
            raise FleetProblem('Coordinator identities are invalid.')
        with self.connect() as db:
            db.executemany("INSERT INTO fleet_control(key,value) VALUES(?,?) ON CONFLICT(key) DO UPDATE SET value=excluded.value",
                (('orca_sender_handle', handle), ('orca_run_id', run_id)))
        return {'handle': handle, 'run_id': run_id}

    def coordinator(self):
        with self.connect() as db:
            rows = {row['key']: row['value'] for row in db.execute("SELECT key,value FROM fleet_control WHERE key IN ('orca_sender_handle','orca_run_id')")}
        if set(rows) != {'orca_sender_handle', 'orca_run_id'}: return None
        return {'handle': rows['orca_sender_handle'], 'run_id': rows['orca_run_id']}

    def enqueue_many(self, body):
        exact(body, {'tasks'})
        if not isinstance(body['tasks'], list) or not 1 <= len(body['tasks']) <= 3: raise FleetProblem('tasks must contain one to three independent tasks.')
        tasks = [validate_task(item) for item in body['tasks']]
        if len({item['idempotency_key'] for item in tasks}) != len(tasks): raise FleetProblem('Each task needs a distinct idempotency_key.')
        return [self.enqueue(item) for item in tasks]

    def enqueue(self, item):
        item = validate_task(item)
        digest = hashlib.sha256(canonical(item).encode()).hexdigest(); job_id = str(uuid.uuid4()); now = stamp()
        node_id, state, error = (None, 'queued', '')
        if item['target'] != 'auto':
            node_id = item['target']; inventory = self.get_inventory(node_id)
            if not inventory or not inventory['ready']:
                state, error = 'blocked', inventory['blocked_reason'] if inventory else 'No inventory evidence has been recorded.'
        with self.connect() as db:
            db.execute('BEGIN IMMEDIATE')
            previous = db.execute('SELECT * FROM fleet_jobs WHERE idempotency_key=?', (item['idempotency_key'],)).fetchone()
            if previous:
                if previous['request_hash'] != digest: raise FleetProblem('idempotency_key was reused for different work.', 409)
                return self._job(previous)
            db.execute('''INSERT INTO fleet_jobs(id,idempotency_key,request_hash,task,kind,target,node_id,writer_scope,capability,baseline_hash,state,created_at,updated_at,error)
              VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?)''', (job_id, item['idempotency_key'], digest, item['task'], item['kind'], item['target'], node_id, item['writer_scope'], item['capability'], self.baseline_hash, state, now, now, error))
            return self._job(db.execute('SELECT * FROM fleet_jobs WHERE id=?', (job_id,)).fetchone())

    def list_jobs(self, limit=100):
        limit = min(max(int(limit), 1), 200)
        with self.connect() as db: return [self._job(row) for row in db.execute('SELECT * FROM fleet_jobs ORDER BY created_at DESC LIMIT ?', (limit,))]

    def get_job(self, job_id):
        canonical_uuid(job_id, 'job id')
        with self.connect() as db: return self._job(db.execute('SELECT * FROM fleet_jobs WHERE id=?', (job_id,)).fetchone())

    def _eligible_nodes(self, db, target, writer_scope, kind):
        active_global = db.execute("SELECT count(*) FROM fleet_jobs WHERE state IN ('launching','running')").fetchone()[0]
        if active_global >= GLOBAL_CAPACITY: return []
        profiles = [NODE_REGISTRY[target]] if target != 'auto' else sorted((profile for profile in NODE_REGISTRY.values() if profile.id != 'local128'), key=lambda item: item.priority)
        eligible = []
        for profile in profiles:
            row = db.execute('SELECT * FROM fleet_inventory WHERE node_id=?', (profile.id,)).fetchone()
            inventory = self._inventory(row)
            if not inventory or not inventory['ready']: continue
            payload = inventory['payload']; available = int(payload.get('memory', {}).get('available_bytes', 0)); load = float(payload.get('load', {}).get('one', 999)); cpus = max(int(payload.get('load', {}).get('cpu_count', 1)), 1)
            required = {'interactive': 8, 'diagnostics': 16, 'research': 16, 'bulk_scan': 24}[kind] * 1024**3
            if available < required or load / cpus > .90: continue
            active = db.execute("SELECT count(*) FROM fleet_jobs WHERE node_id=? AND state IN ('launching','running')", (profile.id,)).fetchone()[0]
            if active >= profile.capacity: continue
            if writer_scope and db.execute("SELECT 1 FROM fleet_jobs WHERE writer_scope=? AND state IN ('launching','running')", (writer_scope,)).fetchone(): continue
            eligible.append(profile.id)
        return eligible

    def claim_next(self, worker_id):
        worker_id = bounded_text(worker_id, 'worker_id', 120)
        if not re.fullmatch(r'[A-Za-z0-9._:-]+', worker_id): raise FleetProblem('worker_id contains unsupported characters.')
        with self.connect() as db:
            db.execute('BEGIN IMMEDIATE')
            for row in db.execute("SELECT * FROM fleet_jobs WHERE state='queued' ORDER BY created_at,id"):
                nodes = self._eligible_nodes(db, row['target'], row['writer_scope'], row['kind'])
                if not nodes: continue
                node_id, token, now = nodes[0], str(uuid.uuid4()), stamp()
                changed = db.execute("UPDATE fleet_jobs SET state='launching',node_id=?,attempt=attempt+1,claim_token=?,started_at=COALESCE(started_at,?),updated_at=? WHERE id=? AND state='queued'", (node_id, token, now, now, row['id'])).rowcount
                if changed: return self._job(db.execute('SELECT * FROM fleet_jobs WHERE id=?', (row['id'],)).fetchone())
        return None

    def mark_running(self, job_id, claim_token, task_id, dispatch_id, terminal_handle, receipt):
        return self._transition(job_id, claim_token, ('launching',), 'running',
            orca_task_id=bounded_text(task_id, 'task_id', 240), dispatch_id=bounded_text(dispatch_id, 'dispatch_id', 240),
            terminal_handle=bounded_text(terminal_handle, 'terminal_handle', 240), receipt=receipt)

    def mark_launch_ambiguous(self, job_id, claim_token, error, receipt=None):
        return self._transition(job_id, claim_token, ('launching',), 'blocked', error=bounded_text(error, 'error', 4000), receipt=receipt or {})

    def finish(self, job_id, claim_token, succeeded, result='', error='', receipt=None):
        return self._transition(job_id, claim_token, ('running',), 'succeeded' if succeeded else 'failed', result=bounded_text(result, 'result', 100000, required=False), error=bounded_text(error, 'error', 4000, required=False), receipt=receipt or {})

    def _transition(self, job_id, claim_token, allowed, state, **fields):
        canonical_uuid(job_id, 'job id'); canonical_uuid(claim_token, 'claim token')
        if state not in JOB_STATES: raise FleetProblem('Unknown state.')
        if not isinstance(fields.get('receipt', {}), dict): raise FleetProblem('receipt must be an object.')
        sets, values = ['state=?', 'updated_at=?'], [state, stamp()]
        if state in ('succeeded', 'failed', 'blocked', 'cancelled'): sets.append('finished_at=?'); values.append(stamp())
        for key in ('orca_task_id', 'dispatch_id', 'terminal_handle', 'result_cursor', 'result', 'error'):
            if key in fields: sets.append(f'{key}=?'); values.append(fields[key])
        if 'receipt' in fields: sets.append('receipt=?'); values.append(canonical(fields['receipt']))
        values.extend([job_id, claim_token, *allowed])
        with self.connect() as db:
            placeholders = ','.join('?' for _ in allowed)
            changed = db.execute(f"UPDATE fleet_jobs SET {','.join(sets)} WHERE id=? AND claim_token=? AND state IN ({placeholders})", values).rowcount
            if not changed: raise FleetProblem('Job state or claim token changed.', 409)
            return self._job(db.execute('SELECT * FROM fleet_jobs WHERE id=?', (job_id,)).fetchone())

    def cancel(self, job_id):
        canonical_uuid(job_id, 'job id'); now = stamp()
        with self.connect() as db:
            db.execute('BEGIN IMMEDIATE')
            changed = db.execute("UPDATE fleet_jobs SET state='cancelled',updated_at=?,finished_at=? WHERE id=? AND state IN ('queued','blocked')", (now, now, job_id)).rowcount
            if not changed: raise FleetProblem('Only queued or blocked work can be cancelled without stopping a live terminal.', 409)
            return self._job(db.execute('SELECT * FROM fleet_jobs WHERE id=?', (job_id,)).fetchone())
