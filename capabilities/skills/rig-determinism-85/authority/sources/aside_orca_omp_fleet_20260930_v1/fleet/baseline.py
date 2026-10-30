"""Build and verify worker profiles with the existing Jake Fleet CAS engine."""
import importlib
import hashlib
import json
import re
import shutil
import sys
import tempfile
from pathlib import Path

from .store import FleetProblem

SOURCE = Path(__file__).parent / 'baseline'
JAKE_FLEET = Path.home() / '.rig/jake-fleet-control/current'
PROFILE_FILES = ('AGENTS.md', 'agent/config.yml', 'agent/models.yml', 'agent/fleet/orca-fleet-worker.ts', 'capabilities.json', 'profile.json', 'roles.json', 'bin/fleet-smoke', 'bin/inventory_probe.py', 'bin/probe_contract.py')
IMPORTS = {
    'agent/agents/planner/multi-agent-coordinator.toml': Path.home()/'Developer/awesome-codex-subagents/categories/09-meta-orchestration/multi-agent-coordinator.toml',
    'agent/agents/planner/project-manager.toml': Path.home()/'Developer/awesome-codex-subagents/categories/08-business-product/project-manager.toml',
    'agent/agents/provisioner/devops-engineer.toml': Path.home()/'Developer/awesome-codex-subagents/categories/03-infrastructure/devops-engineer.toml',
    'agent/agents/provisioner/platform-engineer.toml': Path.home()/'Developer/awesome-codex-subagents/categories/03-infrastructure/platform-engineer.toml',
    'agent/agents/repair/devops-incident-responder.toml': Path.home()/'Developer/awesome-codex-subagents/categories/03-infrastructure/devops-incident-responder.toml',
    'agent/agents/rollback/deployment-engineer.toml': Path.home()/'Developer/awesome-codex-subagents/categories/03-infrastructure/deployment-engineer.toml',
}
IMPORT_TREES = {
    'agent/agents/replication/codex-refactor-migration-engineer': Path.home()/'Developer/rig-jtbd-packs/packs/codex/codex-refactor-migration-engineer',
    'agent/agents/verifier/codex-verification-lab': Path.home()/'Developer/rig-jtbd-packs/packs/codex/codex-verification-lab',
    'agent/skills/rig-anti-fabrication-dispatch': Path.home()/'Developer/rig-capabilities/capabilities/skills/rig-anti-fabrication-dispatch',
    'agent/skills/proof-loop': Path.home()/'Developer/rig-capabilities/capabilities/skills/proof-loop',
    'agent/skills/adversarial-verification-loop': Path.home()/'Developer/rig-capabilities/capabilities/skills/adversarial-verification-loop',
    'agent/skills/done-claim-verification': Path.home()/'Developer/rig-capabilities/capabilities/skills/done-claim-verification',
    'jake-fleet/services/fleet': JAKE_FLEET/'services/fleet',
}
SANITIZE_FIXTURES = {'agent/agents/verifier/codex-verification-lab/HARNESSES.md'}
ROLE_SOURCES = {
    'planner': (
        'Plans bounded work with one writer and explicit integration gates.',
        ('agent/agents/planner/multi-agent-coordinator.toml', 'agent/agents/planner/project-manager.toml')),
    'provisioner': (
        'Builds reproducible infrastructure and checks the resulting runtime.',
        ('agent/agents/provisioner/devops-engineer.toml', 'agent/agents/provisioner/platform-engineer.toml')),
    'replication': (
        'Runs governed expand-contract replication with rollback evidence.',
        tuple('agent/agents/replication/codex-refactor-migration-engineer/'+name for name in ('AGENT.md', 'ACCESS_POLICY.md', 'PROOF_CONTRACT.md', 'HARNESSES.md'))),
    'repair': (
        'Diagnoses operational failures and produces bounded repairs.',
        ('agent/agents/repair/devops-incident-responder.toml',)),
    'verifier': (
        'Runs adversarial, non-vacuous verification and reports residual risk.',
        tuple('agent/agents/verifier/codex-verification-lab/'+name for name in ('AGENT.md', 'ACCESS_POLICY.md', 'PROOF_CONTRACT.md', 'HARNESSES.md'))),
    'rollback': (
        'Designs and proves reversible deployment rollback paths.',
        ('agent/agents/rollback/deployment-engineer.toml',)),
}


def _deploy_module():
    if not JAKE_FLEET.is_dir(): raise FleetProblem('Jake Fleet CAS engine is unavailable.')
    location = str(JAKE_FLEET)
    if location not in sys.path: sys.path.insert(0, location)
    try: return importlib.import_module('services.fleet.deploy')
    except (ImportError, OSError) as error: raise FleetProblem(f'Jake Fleet CAS engine could not load: {error}')


def profile():
    try: value = json.loads((SOURCE / 'profile.json').read_text())
    except (OSError, ValueError) as error: raise FleetProblem(f'Worker profile unavailable: {error}')
    required = {'schema_version', 'profile_id', 'runtime', 'orca_agent', 'model', 'model_route', 'profile_release_root', 'job_root', 'state_root', 'activation'}
    if not isinstance(value, dict) or set(value) != required or value['schema_version'] != 'rig.omp-worker-profile.v1':
        raise FleetProblem('Worker profile shape is invalid.')
    if value['activation'] != 'side-by-side-only': raise FleetProblem('Worker profile cannot replace a current release.')
    route = value['model_route']
    if (not isinstance(route, dict) or set(route) != {'models_url', 'health_url', 'model_id', 'timeout_seconds', 'max_response_bytes'}
            or route['models_url'] != 'http://192.168.68.90:8201/v1/models'
            or route['health_url'] != 'http://192.168.68.90:8201/health'
            or route['model_id'] != value['model'].split('/', 1)[-1]
            or route['timeout_seconds'] != 3 or route['max_response_bytes'] != 1048576):
        raise FleetProblem('Worker model route shape is invalid.')
    return value


def build_profile_bundle(output_root):
    """Return the existing CAS engine's sealed bundle; never activates it."""
    profile()
    deploy = _deploy_module()
    with tempfile.TemporaryDirectory(prefix='rig-omp-profile-stage-') as temporary:
        stage = Path(temporary)
        relative = []
        for item in PROFILE_FILES:
            target = stage/item; target.parent.mkdir(parents=True, exist_ok=True); shutil.copy2(SOURCE/item, target); relative.append(item)
        for destination, source in IMPORTS.items():
            if not source.is_file(): raise FleetProblem(f'Required worker agent is unavailable: {source.name}')
            target = stage/destination; target.parent.mkdir(parents=True, exist_ok=True); shutil.copy2(source, target); relative.append(destination)
        for destination, source in IMPORT_TREES.items():
            if not source.is_dir(): raise FleetProblem(f'Required worker capability is unavailable: {source.name}')
            for item in sorted(source.rglob('*')):
                if not item.is_file() or item.is_symlink() or '__pycache__' in item.parts or item.suffix in {'.pyc', '.db', '.sqlite', '.log'}: continue
                name = str(Path(destination)/item.relative_to(source)); target = stage/name; target.parent.mkdir(parents=True, exist_ok=True)
                if name in SANITIZE_FIXTURES:
                    data = item.read_text()
                    data = re.sub(r'AKIA[0-9A-Z]{16}', '<redacted-aws-test-fixture>', data)
                    data = re.sub(r'gh[pousr]_[A-Za-z0-9]{20,}', '<redacted-github-test-fixture>', data)
                    data = re.sub(r'sk-(?:live|proj)-[A-Za-z0-9_-]{12,}', '<redacted-provider-test-fixture>', data)
                    data = data.replace('password = "hunter2"', 'password = "<redacted-password-test-fixture>"')
                    data = data.replace('Hardcoded password:', 'Hardcoded credential fixture:')
                    target.write_text(data); target.chmod(item.stat().st_mode & 0o777)
                else: shutil.copy2(item, target)
                relative.append(name)
        for role, (description, sources) in ROLE_SOURCES.items():
            sections = []
            for name in sources:
                source = stage/name
                if not source.is_file(): raise FleetProblem(f'Role source was not staged: {name}')
                sections.append(f'## Canonical source: {name}\n\nSHA-256: `{hashlib.sha256(source.read_bytes()).hexdigest()}`\n\n{source.read_text()}')
            target = stage/'agent/agents'/f'{role}.md'
            target.write_text('---\nname: '+role+'\ndescription: '+json.dumps(description)+'\nspawns: false\n---\n\n'
                'You are the fixed RIG fleet '+role+' role. Read the applicable installed skill before acting. '
                'Stay inside the job directory, write an artifact, and report the commands that verify it.\n\n'+'\n\n'.join(sections)+'\n')
            target.chmod(0o644); relative.append(str(target.relative_to(stage)))
        bundle = deploy.build_bundle(stage, relative, Path(output_root))
        verified = deploy.verify_bundle(bundle.root)
    if verified['release_id'] != bundle.release_id: raise FleetProblem('CAS verification identity changed.')
    return {'release_id': bundle.release_id, 'root': str(bundle.root), 'manifest': verified}


def profile_release_id():
    """Calculate the exact CAS identity used by provisioning and readiness."""
    with tempfile.TemporaryDirectory(prefix='rig-omp-profile-') as temporary:
        # deploy.build_bundle requires an output root that does not exist yet.
        return build_profile_bundle(Path(temporary)/'bundle')['release_id']


def verify_profile_release(path):
    release = Path(path)
    if release.parent.name != 'releases': raise FleetProblem('Installed profile release path is invalid.')
    return _deploy_module().verify_installed_release(release.parent.parent, 'releases/'+release.name)
