"""Fixed fleet registry. Browser requests can reference IDs, never transports."""
from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path

BASELINE_ROOT = Path.home() / '.rig/fleet-worker'
JOB_ROOT = Path.home() / '.rig/jake/omp-worker-jobs'
ACTIVE_STATES = ('launching', 'running')
TERMINAL_STATES = ('succeeded', 'failed', 'blocked', 'cancelled')
GLOBAL_CAPACITY = 3
INVENTORY_TTL_SECONDS = 300


@dataclass(frozen=True)
class NodeProfile:
    id: str
    label: str
    environment: str | None
    ssh_alias: str | None
    priority: int
    capacity: int
    expected_omp: str
    worktree_anchor: str
    job_root: str
    home: str
    minimum_node_major: int = 22
    minimum_python: tuple[int, int] = (3, 9)


NODE_REGISTRY = {
    'local128': NodeProfile('local128', '128 GB · local', None, None, 30, 1, '18.2.9', '/Users/rig128gb/.rig/jake', '/Users/rig128gb/.rig/jake/omp-worker-jobs', '/Users/rig128gb'),
    'rig256gb': NodeProfile('rig256gb', '256 GB · Orca', 'rig-256gb', 'rig256gb', 10, 2, '18.2.9', '/Users/rig256gb/Developer/local-ai-model-matcher', '/Users/rig256gb/.rig/jake/omp-worker-jobs', '/Users/rig256gb'),
    'rig96gb': NodeProfile('rig96gb', '96 GB · Orca', 'rig-96gb', 'rig96gb', 20, 1, '18.2.9', '/Users/rig96gb/Developer/local-ai-model-matcher', '/Users/rig96gb/.rig/jake/omp-worker-jobs', '/Users/rig96gb'),
}


def public_node(profile):
    return {
        'id': profile.id,
        'label': profile.label,
        'priority': profile.priority,
        'capacity': profile.capacity,
        'expected_omp': profile.expected_omp,
    }
