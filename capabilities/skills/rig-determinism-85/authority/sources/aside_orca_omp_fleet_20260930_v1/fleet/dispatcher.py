"""Bounded adapter to Orca Tasks, terminals, and supervised Dispatches."""
import json
import hashlib
import os
import shlex
import subprocess
import time
import calendar
from pathlib import Path, PurePosixPath

from .baseline import profile
from .registry import NODE_REGISTRY
from .store import FleetProblem, canonical


PREPARE_SCRIPT = r"""import os,pathlib,shutil,sys
p=pathlib.Path(sys.argv[1]);role=pathlib.Path(sys.argv[2]);state=pathlib.Path(sys.argv[3]);agent=role.parent.parent
p.mkdir(parents=True,exist_ok=False,mode=0o700);state.mkdir(parents=True,exist_ok=False,mode=0o700)
prompt=p/'prompt.md';prompt.write_text(sys.stdin.read(),encoding='utf-8');os.chmod(prompt,0o600)
append=p/'APPEND_SYSTEM.md';append.write_text(role.read_text()+'\n\nRead the relevant installed skill and create at least one concrete artifact in this job directory. Report verification commands. For a fleet validation task, run the exact command fleet-smoke once; it writes report.md and returns a compact saved receipt. Acknowledge that artifact and finish without running fleet-smoke again or invoking Orca orchestration.\n',encoding='utf-8');os.chmod(append,0o600)
for name in ('config.yml','models.yml'):shutil.copy2(agent/name,state/name)
for name in ('agents','skills'):os.symlink(agent/name,state/name,target_is_directory=True)"""

STARTUP_WAIT_SCRIPT = r"""import json,pathlib,sys,time
p=pathlib.Path(sys.argv[1]);deadline=time.monotonic()+float(sys.argv[2])
while time.monotonic()<deadline:
 if p.is_file() and not p.is_symlink():
  print(p.read_text(encoding='utf-8'));raise SystemExit(0)
 time.sleep(0.25)
raise SystemExit(75)"""

RECEIPT_SNAPSHOT_SCRIPT = r"""import pathlib,sys
p=pathlib.Path(sys.argv[1])
if not p.is_file() or p.is_symlink():raise SystemExit(4)
print(p.read_text(encoding='utf-8'))"""

RUN_DEADLINE_SECONDS = 50 * 60


def _path(value, *paths):
    for path in paths:
        current = value
        for key in path:
            if not isinstance(current, dict) or key not in current: break
            current = current[key]
        else:
            if isinstance(current, str) and current: return current
    return None


class OrcaTransport:
    """All command choices and host names come from the fixed registry."""
    def __init__(self, runner=subprocess.run, sender_handle=None, run_id=None, startup_timeout=75, result_timeout=15):
        self.runner = runner
        self.sender_handle = sender_handle or os.environ.get('RIG_FLEET_ORCA_FROM') or os.environ.get('ORCA_TERMINAL_HANDLE')
        self.run_id = run_id or os.environ.get('RIG_FLEET_ORCA_RUN')
        self.startup_timeout = startup_timeout
        self.result_timeout = result_timeout

    def _json(self, args, timeout=60, input_text=None):
        result = self.runner(args, capture_output=True, text=True, timeout=timeout, input=input_text)
        try: body = json.loads(result.stdout)
        except ValueError: body = {'raw': result.stdout[-4000:]}
        if result.returncode: raise FleetProblem('Orca returned an uncertain outcome: ' + json.dumps(body, sort_keys=True)[:2000], 503)
        return body

    @staticmethod
    def _host_command(node, args):
        return ['ssh', node.ssh_alias, ' '.join(shlex.quote(str(part)) for part in args)] if node.ssh_alias else [str(part) for part in args]

    def prepare(self, job):
        node, details = NODE_REGISTRY[job['node_id']], profile(); job_dir = Path(node.job_root)/job['id']
        state_dir = Path(node.home)/details['state_root']/job['id']
        release = Path(node.home)/details['profile_release_root']/job['baseline_hash']; role = release/'agent/agents'/f"{job['capability']}.md"
        command = self._host_command(node, ['python3', '-c', PREPARE_SCRIPT, str(job_dir), str(role), str(state_dir)])
        result = self.runner(command, capture_output=True, text=True, timeout=20, input=job['task'])
        if result.returncode: raise FleetProblem('Isolated job directory could not be created.', 503)
        return str(job_dir)

    def create_task(self, job):
        if not self.sender_handle: raise FleetProblem('Orca sender terminal is not configured for the dispatcher.', 503)
        command = ['orca', 'orchestration', 'task-create', '--spec', job['task'], '--task-title', 'RIG fleet '+job['id'][:8], '--display-name', job['capability']+' · '+job['id'][:8], '--from', self.sender_handle, '--json']
        if self.run_id: command[-1:-1] = ['--run', self.run_id]
        body = self._json(command)
        task_id = _path(body, ('result', 'task', 'id'), ('result', 'taskId'))
        if not task_id: raise FleetProblem('Orca created no provable Task identifier.', 503)
        return task_id, body

    def create_terminal(self, job, job_dir):
        node, details = NODE_REGISTRY[job['node_id']], profile()
        release = job['baseline_hash']; profile_root = Path(node.home)/details['profile_release_root']/release
        runtime = Path(node.home)/details['runtime']['root']; extension = profile_root/'agent/fleet/orca-fleet-worker.ts'
        prompt_hash = hashlib.sha256(job['task'].encode()).hexdigest(); state_dir = Path(node.home)/details['state_root']/job['id']
        env = {'PI_CODING_AGENT_DIR': str(state_dir), 'RIG_FLEET_PROFILE_ROOT': str(profile_root), 'RIG_FLEET_STATE_DIR': str(state_dir), 'RIG_FLEET_JOB_DIR': job_dir, 'RIG_FLEET_JOB_ID': job['id'], 'RIG_FLEET_RELEASE': release, 'RIG_FLEET_ROLE': job['capability'], 'RIG_FLEET_MODEL': details['model'], 'RIG_FLEET_PROMPT_SHA256': prompt_hash}
        argv = [str(runtime/'bin/omp'), '--cwd', job_dir, '--config', str(state_dir/'config.yml'), '--model', details['model'], '--skills', ','.join(json.loads((Path(__file__).parent/'baseline/roles.json').read_text())['common_skills']), '--append-system-prompt', str(Path(job_dir)/'APPEND_SYSTEM.md'), '--no-title', '--no-prewalk', '--no-session', '--max-time', '45m', '--tools', ','.join(json.loads((Path(__file__).parent/'baseline/roles.json').read_text())['required_tools']), '--extension', str(extension), '--approval-mode', 'write']
        command_text = 'cd '+_shell_quote(job_dir)+' && env PATH='+_shell_quote(str(profile_root/'bin')+':'+str(runtime/'bin'))+':"$PATH" '+' '.join(_shell_quote(key+'='+value) for key,value in env.items())+' '+' '.join(_shell_quote(value) for value in argv)
        command = ['orca', 'terminal', 'create', '--worktree', 'path:'+node.worktree_anchor, '--title', 'RIG '+job['capability']+' '+job['id'][:8], '--command', command_text, '--json']
        if node.environment: command[3:3] = ['--environment', node.environment]
        body = self._json(command, timeout=45)
        handle = _path(body, ('result', 'terminal', 'handle'), ('result', 'handle'), ('result', 'terminalHandle'))
        if not handle: raise FleetProblem('Orca created no provable terminal handle.', 503)
        return handle, body

    def wait_startup(self, job, handle):
        node, details = NODE_REGISTRY[job['node_id']], profile()
        state_dir = Path(node.home)/details['state_root']/job['id']
        path = state_dir/'startup-receipt.json'
        command = self._host_command(node, ['python3', '-B', '-c', STARTUP_WAIT_SCRIPT, str(path), str(self.startup_timeout)])
        result = self.runner(command, capture_output=True, text=True, timeout=self.startup_timeout + 5)
        if result.returncode:
            raise FleetProblem('OMP startup did not produce a native Orca readiness receipt.', 503)
        try: receipt = json.loads(result.stdout)
        except ValueError: raise FleetProblem('OMP startup readiness receipt was not JSON.', 503)
        _verify_startup_receipt(job, receipt, details['model'])
        return receipt

    def adopt(self, job, task_id, handle, job_dir):
        node = NODE_REGISTRY[job['node_id']]
        if not self.sender_handle: raise FleetProblem('Orca sender terminal is not configured for the dispatcher.', 503)
        command = ['orca', 'orchestration', 'worker-start', '--task', task_id, '--worktree', 'path:'+node.worktree_anchor, '--terminal', handle, '--from', self.sender_handle, '--json']
        if node.environment: command[3:3] = ['--on', node.environment]
        body = self._json(command, timeout=90)
        dispatch = _path(body, ('result', 'dispatch', 'id'), ('result', 'dispatchId'))
        if not dispatch: raise FleetProblem('Orca returned no provable Dispatch identifier.', 503)
        _verify_adoption(body, dispatch, handle)
        return dispatch, body

    def bind(self, job, task_id, dispatch, handle, job_dir):
        node = NODE_REGISTRY[job['node_id']]
        binding = canonical({'job_id': job['id'], 'profile_release': job['baseline_hash'], 'role': job['capability'], 'task_id': task_id, 'dispatch_id': dispatch, 'terminal_handle': handle})
        script = "import os,pathlib,sys\np=pathlib.Path(sys.argv[1])/'dispatch-bound.json';p.write_text(sys.stdin.read(),encoding='utf-8');os.chmod(p,0o600)"
        result = self.runner(self._host_command(node, ['python3', '-c', script, job_dir]), capture_output=True, text=True, timeout=20, input=binding)
        if result.returncode: raise FleetProblem('Dispatch binding could not be written.', 503)
        return json.loads(binding)

    def show(self, dispatch): return self._json(['orca', 'orchestration', 'worker-show', '--dispatch', dispatch, '--json'])
    def read(self, dispatch, cursor=None):
        command = ['orca', 'orchestration', 'worker-read', '--dispatch', dispatch, '--source', 'auto', '--limit', '1000', '--json']
        if cursor: command[6:6] = ['--cursor', cursor]
        return self._json(command)

    def result_receipt(self, job):
        node = NODE_REGISTRY[job['node_id']]; path = str(Path(node.job_root)/job['id']/'result-receipt.json')
        script = r"""import hashlib,json,os,pathlib,stat,sys,time
p=pathlib.Path(sys.argv[1]);deadline=time.monotonic()+float(sys.argv[2])
while time.monotonic()<deadline:
 if p.is_file() and not p.is_symlink():break
 time.sleep(0.1)
else:raise SystemExit(75)
root=p.parent; data=json.loads(p.read_text())
root_stat=os.lstat(root)
if stat.S_ISLNK(root_stat.st_mode) or not stat.S_ISDIR(root_stat.st_mode):raise SystemExit(2)
rows=data.get('artifacts',[])
if not isinstance(rows,list) or not rows:raise SystemExit(4)
listed=set(); verified={}
for row in rows:
 if not isinstance(row,dict) or set(row)!={'path','sha256','size'}:raise SystemExit(4)
 raw=row['path']; pure=pathlib.PurePosixPath(raw) if isinstance(raw,str) else None
 if pure is None or not raw or pure.is_absolute() or raw!=pure.as_posix() or any(part in {'','.','..'} for part in pure.parts) or raw in listed:raise SystemExit(4)
 listed.add(raw); q=root
 for index,part in enumerate(pure.parts):
  q=q/part
  try:entry=os.lstat(q)
  except OSError:raise SystemExit(2)
  if stat.S_ISLNK(entry.st_mode):raise SystemExit(2)
  if index<len(pure.parts)-1 and not stat.S_ISDIR(entry.st_mode):raise SystemExit(2)
 if not stat.S_ISREG(entry.st_mode):raise SystemExit(2)
 if isinstance(row['size'],bool) or not isinstance(row['size'],int) or row['size']<0 or entry.st_size!=row['size']:raise SystemExit(3)
 if not isinstance(row['sha256'],str) or len(row['sha256'])!=64 or any(c not in '0123456789abcdef' for c in row['sha256']) or hashlib.sha256(q.read_bytes()).hexdigest()!=row['sha256']:raise SystemExit(3)
 verified[raw]=q
actual=set()
for current,dirs,names in os.walk(root,followlinks=False):
 for name in dirs:
  q=pathlib.Path(current)/name; entry=os.lstat(q)
  if stat.S_ISLNK(entry.st_mode) or not stat.S_ISDIR(entry.st_mode):raise SystemExit(2)
 for name in names:
  q=pathlib.Path(current)/name; entry=os.lstat(q)
  if stat.S_ISLNK(entry.st_mode) or not stat.S_ISREG(entry.st_mode):raise SystemExit(2)
  if name not in {'dispatch-bound.json','result-receipt.json','result-receipt.json.tmp'}:actual.add(q.relative_to(root).as_posix())
if listed!=actual:raise SystemExit(4)
if 'prompt.md' not in verified or 'delivered-prompt.txt' not in verified:raise SystemExit(4)
queued=verified['prompt.md'].read_text(); delivered=verified['delivered-prompt.txt'].read_text()
if hashlib.sha256(queued.encode()).hexdigest()!=data.get('prompt_sha256'):raise SystemExit(5)
if hashlib.sha256(delivered.encode()).hexdigest()!=data.get('delivered_prompt_sha256'):raise SystemExit(6)
if delivered!=queued and delivered.count(queued)!=1:raise SystemExit(7)
print(json.dumps(data,separators=(',',':'),sort_keys=True))"""
        result = self.runner(self._host_command(node, ['python3', '-B', '-c', script, path, str(self.result_timeout)]), capture_output=True, text=True, timeout=self.result_timeout + 5)
        if result.returncode: raise FleetProblem('Worker result receipt could not be read.', 503)
        try: return json.loads(result.stdout)
        except ValueError: raise FleetProblem('Worker result receipt was not JSON.', 503)

    def failure_receipt(self, job):
        node = NODE_REGISTRY[job['node_id']]; path = str(Path(node.job_root)/job['id']/'result-receipt.json')
        result = self.runner(self._host_command(node, ['python3', '-B', '-c', RECEIPT_SNAPSHOT_SCRIPT, path]), capture_output=True, text=True, timeout=5)
        if result.returncode == 4: return None
        if result.returncode: raise FleetProblem('Worker failure receipt could not be read.', 503)
        try: receipt = json.loads(result.stdout)
        except ValueError: raise FleetProblem('Worker failure receipt was not JSON.', 503)
        if receipt.get('schema_version') != 'rig.omp-worker-failure.v1': return None
        _verify_failure_receipt(job, receipt)
        return receipt


class Dispatcher:
    def __init__(self, store, transport=None, worker_id='rig-hq-fleet'):
        coordinator = store.coordinator() if transport is None else None
        self.store = store
        self.transport = transport or OrcaTransport(sender_handle=coordinator['handle'] if coordinator else None, run_id=coordinator['run_id'] if coordinator else None)
        self.worker_id = worker_id

    def launch_one(self):
        job = self.store.claim_next(self.worker_id)
        if not job: return None
        receipt = {'profile_release': job['baseline_hash'], 'node_id': job['node_id'], 'role': job['capability']}
        try:
            job_dir = self.transport.prepare(job); receipt['job_dir'] = job_dir
            handle, terminal_receipt = self.transport.create_terminal(job, job_dir); receipt['orca_terminal'] = terminal_receipt
            receipt['omp_startup'] = self.transport.wait_startup(job, handle)
            task_id, task_receipt = self.transport.create_task(job); receipt['orca_task'] = task_receipt
            dispatch, dispatch_receipt = self.transport.adopt(job, task_id, handle, job_dir); receipt['orca_dispatch'] = dispatch_receipt
            receipt['binding'] = self.transport.bind(job, task_id, dispatch, handle, job_dir)
            return self.store.mark_running(job['id'], job['claim_token'], task_id, dispatch, handle, receipt)
        except Exception as error:
            # Any lost create/adopt/bind response can leave effects. Never retry automatically.
            receipt['ambiguous_launch'] = True
            return self.store.mark_launch_ambiguous(job['id'], job['claim_token'], str(error), receipt)

    def refresh(self, job):
        if job['state'] != 'running' or not job['dispatch_id']: return job
        try: failure_receipt = self.transport.failure_receipt(job)
        except Exception as error:
            return self.store.finish(job['id'], job['claim_token'], False, error='Worker failure receipt was invalid: '+str(error))
        if failure_receipt:
            return self.store.finish(job['id'], job['claim_token'], False, error=failure_receipt['error'], receipt={'worker_failure': failure_receipt})
        try: shown = self.transport.show(job['dispatch_id'])
        except Exception: return job
        state = (_path(shown, ('result', 'projection', 'outcome'), ('result', 'dispatchStatus'), ('result', 'workerState')) or '').lower()
        if state not in {'completed', 'succeeded', 'failed', 'blocked', 'cancelled'}:
            if _run_deadline_expired(job):
                return self.store.finish(job['id'], job['claim_token'], False, error='Worker exceeded the bounded 50 minute fleet deadline.', receipt={'orca_show': shown})
            return job
        try: output = self.transport.read(job['dispatch_id'], job.get('result_cursor'))
        except Exception as error: output = {'error': str(error)}
        text = _result_text(output)
        if state in {'completed', 'succeeded'}:
            try:
                result_receipt = self.transport.result_receipt(job)
                _verify_result_receipt(job, result_receipt)
            except Exception as error:
                return self.store.finish(job['id'], job['claim_token'], False, error='Completion lacked a valid artifact receipt: '+str(error), receipt={'orca_show': shown, 'orca_output': output})
            return self.store.finish(job['id'], job['claim_token'], True, result=text, receipt={'orca_show': shown, 'orca_output': output, 'worker_result': result_receipt})
        return self.store.finish(job['id'], job['claim_token'], False, error=text or state, receipt={'orca_show': shown, 'orca_output': output})


def _shell_quote(value): return shlex.quote(str(value))


def _verify_adoption(body, dispatch, handle):
    result = body.get('result') if isinstance(body, dict) else None
    if not isinstance(result, dict) or result.get('dispatchId') != dispatch or result.get('state') != 'ready' or result.get('stage') != 'input_accepted':
        raise FleetProblem('Orca did not prove native task input acceptance.', 503)
    effects = result.get('effects')
    accepted = isinstance(effects, list) and any(isinstance(item, dict) and item.get('kind') == 'dispatch_input'
        and item.get('role') == 'agent' and item.get('id') == handle and item.get('state') == 'accepted' for item in effects)
    if not accepted: raise FleetProblem('Orca did not bind accepted input to the exact terminal.', 503)


def _verify_startup_receipt(job, receipt, model):
    exact = {'schema_version', 'job_id', 'profile_release', 'role', 'model', 'hook', 'status', 'pane_key'}
    if not isinstance(receipt, dict) or set(receipt) != exact:
        raise FleetProblem('OMP startup readiness receipt fields are invalid.', 503)
    expected = {'schema_version': 'rig.omp-worker-startup.v1', 'job_id': job['id'], 'profile_release': job['baseline_hash'],
                'role': job['capability'], 'model': model, 'hook': '/hook/omp', 'status': 'native_hook_accepted'}
    if any(receipt.get(key) != value for key, value in expected.items()):
        raise FleetProblem('OMP startup readiness receipt is not bound to this job.', 503)
    pane_key = receipt.get('pane_key')
    if not isinstance(pane_key, str) or not pane_key or len(pane_key) > 256 or any(ord(char) < 33 or ord(char) > 126 for char in pane_key):
        raise FleetProblem('OMP startup readiness receipt pane key is invalid.', 503)


def _verify_failure_receipt(job, receipt):
    exact = {'schema_version', 'job_id', 'profile_release', 'role', 'delivered_prompt_sha256', 'error'}
    if not isinstance(receipt, dict) or set(receipt) != exact:
        raise FleetProblem('Worker failure receipt fields are invalid.', 503)
    expected = {'schema_version': 'rig.omp-worker-failure.v1', 'job_id': job['id'], 'profile_release': job['baseline_hash'], 'role': job['capability']}
    if any(receipt.get(key) != value for key, value in expected.items()):
        raise FleetProblem('Worker failure receipt is not bound to this job.', 503)
    prompt_hash = receipt.get('delivered_prompt_sha256')
    if not isinstance(prompt_hash, str) or (prompt_hash and (len(prompt_hash) != 64 or any(char not in '0123456789abcdef' for char in prompt_hash))):
        raise FleetProblem('Worker failure prompt hash is invalid.', 503)
    error = receipt.get('error')
    if not isinstance(error, str) or not error or len(error) > 4000:
        raise FleetProblem('Worker failure error is invalid.', 503)


def _run_deadline_expired(job, now=None):
    started = job.get('started_at')
    if not isinstance(started, str): return False
    try: epoch = calendar.timegm(time.strptime(started, '%Y-%m-%dT%H:%M:%SZ'))
    except (OverflowError, ValueError): return True
    return (time.time() if now is None else now) - epoch > RUN_DEADLINE_SECONDS


def _verify_result_receipt(job, receipt):
    exact = {'schema_version', 'job_id', 'profile_release', 'role', 'task_id', 'dispatch_id', 'terminal_handle', 'exit_code', 'prompt_sha256', 'delivered_prompt_sha256', 'output_sha256', 'artifacts'}
    if not isinstance(receipt, dict) or set(receipt) != exact: raise FleetProblem('Result receipt fields are invalid.')
    expected = {'schema_version': 'rig.omp-worker-result.v1', 'job_id': job['id'], 'profile_release': job['baseline_hash'], 'role': job['capability'],
                'task_id': job['orca_task_id'], 'dispatch_id': job['dispatch_id'], 'terminal_handle': job['terminal_handle'], 'exit_code': 0}
    if any(receipt.get(key) != value for key, value in expected.items()): raise FleetProblem('Result receipt is not bound to this job.')
    if not all(isinstance(receipt.get(key), str) and len(receipt[key]) == 64 for key in ('prompt_sha256', 'delivered_prompt_sha256', 'output_sha256')): raise FleetProblem('Result hashes are invalid.')
    if receipt['prompt_sha256'] != hashlib.sha256(job['task'].encode()).hexdigest(): raise FleetProblem('Prompt hash does not match the queued task.')
    artifacts = receipt['artifacts']
    if not isinstance(artifacts, list) or not artifacts: raise FleetProblem('No result artifacts were recorded.')
    safe = []; delivered_artifact = None; seen = set()
    for item in artifacts:
        if not isinstance(item, dict) or set(item) != {'path', 'sha256', 'size'}: raise FleetProblem('Artifact receipt shape is invalid.')
        raw = item['path']; path = PurePosixPath(raw) if isinstance(raw, str) else None
        if (path is None or not raw or path.is_absolute() or raw != path.as_posix() or any(part in {'', '.', '..'} for part in path.parts)
                or raw in seen or not isinstance(item['sha256'], str) or len(item['sha256']) != 64
                or any(char not in '0123456789abcdef' for char in item['sha256'])
                or not isinstance(item['size'], int) or isinstance(item['size'], bool) or item['size'] < 0):
            raise FleetProblem('Artifact receipt is unsafe or duplicated.')
        seen.add(raw)
        if raw == 'delivered-prompt.txt': delivered_artifact = item
        if raw not in {'prompt.md', 'delivered-prompt.txt', 'APPEND_SYSTEM.md', 'output.txt', 'stderr.txt'} and item['size'] > 0: safe.append(item)
    if not delivered_artifact or delivered_artifact['sha256'] != receipt['delivered_prompt_sha256'] or delivered_artifact['size'] <= 0: raise FleetProblem('Delivered prompt evidence is missing or invalid.')
    if not safe: raise FleetProblem('Worker produced no concrete artifact beyond transport files.')


def _result_text(value):
    if isinstance(value, dict):
        for key in ('text', 'output', 'result'):
            if isinstance(value.get(key), str): return value[key][-100000:]
        lines = value.get('lines')
        if isinstance(lines, list): return '\n'.join(str(line) for line in lines)[-100000:]
        for child in value.values():
            found = _result_text(child)
            if found: return found
    if isinstance(value, list): return '\n'.join(filter(None, (_result_text(item) for item in value)))[-100000:]
    return ''
