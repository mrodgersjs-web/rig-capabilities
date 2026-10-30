"""Explicit inventory probes. Nothing here runs during an HTTP render."""
import json
import re
import shlex
import subprocess
from pathlib import Path

from .baseline import profile, profile_release_id
from .registry import NODE_REGISTRY
from .store import FleetProblem


class InventoryProbe:
    def __init__(self, runner=subprocess.run):
        self.runner = runner
        self.release_id = profile_release_id()
        self.details = profile()

    def _run(self, args, timeout=20, env=None):
        result = self.runner(args, capture_output=True, text=True, timeout=timeout, env=env)
        if result.returncode: raise FleetProblem('Inventory command failed.')
        return result.stdout

    def collect(self, node_id):
        if node_id not in NODE_REGISTRY: raise FleetProblem('Unknown node.')
        node, details, release = NODE_REGISTRY[node_id], self.details, self.release_id
        probe = str(Path(node.home)/details['profile_release_root']/release/'bin/inventory_probe.py')
        command = ['python3', '-B', probe, '--release', release]
        if node.ssh_alias:
            command = ['ssh', node.ssh_alias, ' '.join(shlex.quote(part) for part in command)]
        raw = self._run(command)
        try: payload = json.loads(raw)
        except ValueError: raise FleetProblem('Inventory evidence was not JSON.')
        status = ['orca', 'status', '--json']
        if node.environment: status[2:2] = ['--environment', node.environment]
        try:
            orca = json.loads(self._run(status, timeout=15))
            payload['orca_ready'] = _orca_ready(orca, node)
        except (FleetProblem, ValueError): payload['orca_ready'] = False
        return payload


def _orca_ready(value, node):
    if not isinstance(value, dict) or value.get('ok') is not True: return False
    result = value.get('result')
    if not isinstance(result, dict): return False
    runtime, graph, target = result.get('runtime'), result.get('graph'), result.get('target')
    if not all(isinstance(item, dict) for item in (runtime, graph, target)): return False
    runtime_id, app_version = runtime.get('runtimeId'), runtime.get('appVersion')
    runtime_ok = (runtime.get('state') == 'ready' and runtime.get('reachable') is True
        and runtime.get('connectionState') == 'connected'
        and isinstance(runtime_id, str) and re.fullmatch(r'[A-Za-z0-9._:-]{4,200}', runtime_id)
        and isinstance(app_version, str) and re.fullmatch(r'\d+\.\d+\.\d+', app_version))
    target_ok = (target.get('kind') == 'local' and node.environment is None) or (
        target.get('kind') == 'environment' and node.environment is not None and target.get('environment') == node.environment)
    return bool(runtime_ok and graph.get('state') == 'ready' and target_ok)
