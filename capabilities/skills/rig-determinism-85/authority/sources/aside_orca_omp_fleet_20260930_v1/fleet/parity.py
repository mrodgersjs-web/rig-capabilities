"""Build a credential-free, content-addressed OMP catalog reconstruction."""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import stat
import tempfile
from pathlib import Path, PurePosixPath

from .baseline import _deploy_module
from .store import FleetProblem, canonical


NAME_RE = re.compile(r'[A-Za-z0-9][A-Za-z0-9._-]{0,127}')
PARITY_SCHEMA = 'rig.omp-current-disk-parity.v1'
MODE_POLICY = 'strip-group-world-write.v1'


def _load(path, schema):
    source = Path(path)
    try:
        payload = source.read_bytes(); value = json.loads(payload)
    except (OSError, ValueError) as error:
        raise FleetProblem(f'Parity input could not be read: {error}')
    if not isinstance(value, dict) or value.get('schema_version') != schema:
        raise FleetProblem(f'Parity input schema must be {schema}.')
    return value, hashlib.sha256(payload).hexdigest()


def _name(value, kind):
    if not isinstance(value, str) or not NAME_RE.fullmatch(value):
        raise FleetProblem(f'Unsafe {kind} name in parity inventory.')
    return value


def _relative(value):
    if not isinstance(value, str) or not value or '\x00' in value or '\\' in value:
        raise FleetProblem('Unsafe relative path in parity inventory.')
    path = PurePosixPath(value)
    if path.is_absolute() or any(part in {'', '.', '..'} for part in path.parts) or path.as_posix() != value:
        raise FleetProblem('Unsafe relative path in parity inventory.')
    return path


def _regular_source(root, relative, digest, size):
    source = root.joinpath(*relative.parts)
    try: source.resolve(strict=True).relative_to(root.resolve(strict=True))
    except (FileNotFoundError, ValueError) as error: raise FleetProblem(f'Parity source escaped or disappeared: {relative}') from error
    if source.is_symlink() or not source.is_file(): raise FleetProblem(f'Parity source is not a regular file: {relative}')
    data = source.read_bytes()
    if len(data) != size or hashlib.sha256(data).hexdigest() != digest: raise FleetProblem(f'Parity source drifted: {relative}')
    return source, data


def _write(stage, relative, data, mode):
    target = stage.joinpath(*PurePosixPath(relative).parts)
    if target.exists():
        if target.read_bytes() != data: raise FleetProblem(f'Parity staging collision: {relative}')
        return False
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(data); target.chmod(mode & 0o777)
    return True


def _staged_mode(source_mode):
    """Preserve source permissions except group/world write in the portable copy."""
    return source_mode & ~0o022


def _validate_inputs(inventory, inventory_hash, dependencies):
    source = dependencies.get('source_inventory')
    if not isinstance(source, dict) or source.get('sha256') != inventory_hash:
        raise FleetProblem('Dependency closure is not bound to the supplied inventory.')
    winners = inventory.get('skills', {}).get('winners'); agents = inventory.get('agents', {}).get('files')
    skills = dependencies.get('skills'); dependency_agents = dependencies.get('agents')
    if not all(isinstance(value, list) for value in (winners, agents, skills, dependency_agents)):
        raise FleetProblem('Parity catalogs must be lists.')
    expected = (source.get('expected_skill_count'), source.get('expected_agent_count'))
    if expected != (len(winners), len(agents)) or len(skills) != len(winners) or len(dependency_agents) != len(agents):
        raise FleetProblem('Parity catalog counts do not match their source binding.')
    drift = dependencies.get('drift')
    if not isinstance(drift, dict) or any(drift.get(key) != 0 for key in ('agent_changed_during_scan_count', 'agent_snapshot_mismatch_count', 'skill_changed_during_scan_count', 'skill_snapshot_mismatch_count')):
        raise FleetProblem('Parity source drift is non-zero.')
    winner_map = {_name(row.get('name'), 'skill'): row for row in winners if isinstance(row, dict)}
    agent_map = {_name(row.get('name'), 'agent'): row for row in agents if isinstance(row, dict)}
    if len(winner_map) != len(winners) or len(agent_map) != len(agents): raise FleetProblem('Parity inventory names are duplicated.')
    return winner_map, agent_map


def build_parity_bundle(inventory_path, dependencies_path, output_root):
    inventory, inventory_hash = _load(inventory_path, 'omp-session-parity-inventory.v1')
    dependencies, dependencies_hash = _load(dependencies_path, 'omp-session-parity-dependencies.v1')
    winner_map, agent_map = _validate_inputs(inventory, inventory_hash, dependencies)
    deploy = _deploy_module()
    quarantined, gaps, materialized, statuses, agent_status, mode_normalizations = [], [], [], {}, {}, []
    source_file_count = staged_source_file_count = agent_source_count = copied_agent_count = cas_rejected_count = 0

    with tempfile.TemporaryDirectory(prefix='rig-omp-parity-stage-') as temporary:
        stage = Path(temporary); relative_files = []
        for skill in dependencies['skills']:
            name = _name(skill.get('name'), 'skill'); winner = winner_map.get(name)
            if not winner or skill.get('snapshot_skill_md_sha256') != winner.get('sha256'):
                raise FleetProblem(f'Skill closure is not bound to the winner: {name}')
            if not skill.get('stable_during_scan') or not skill.get('snapshot_match_pre'):
                raise FleetProblem(f'Skill closure drifted during capture: {name}')
            root = Path(skill.get('resolved_skill_dir', ''))
            if not root.is_dir(): raise FleetProblem(f'Skill source is unavailable: {name}')
            safe_entries = {}
            owner_gaps = []
            for entry in skill.get('entries', []):
                if not isinstance(entry, dict): raise FleetProblem(f'Invalid skill closure entry: {name}')
                relative = _relative(entry.get('relative_path'))
                if entry.get('type') == 'file':
                    reason = entry.get('content_hash_excluded_reason')
                    if reason:
                        quarantined.append({'owner': name, 'path': relative.as_posix(), 'reason': reason, 'size': entry.get('size_bytes')})
                        owner_gaps.append('quarantined_file'); continue
                    digest, size = entry.get('sha256'), entry.get('size_bytes')
                    if not isinstance(digest, str) or not re.fullmatch(r'[0-9a-f]{64}', digest) or not isinstance(size, int) or isinstance(size, bool):
                        raise FleetProblem(f'Invalid safe file evidence: {name}/{relative}')
                    source_file, data = _regular_source(root, relative, digest, size)
                    source_mode = stat.S_IMODE(source_file.stat().st_mode); mode = _staged_mode(source_mode)
                    destination = f'agent/skills/{name}/{relative.as_posix()}'
                    source_file_count += 1
                    try: deploy._scan_secret(destination, data)
                    except deploy.BundleError:
                        quarantined.append({'owner': name, 'path': relative.as_posix(), 'reason': 'cas_secret_scan_rejected', 'size': size})
                        owner_gaps.append('cas_secret_scan_rejected'); cas_rejected_count += 1; continue
                    if _write(stage, destination, data, mode): relative_files.append(destination)
                    if mode != source_mode:
                        mode_normalizations.append({'owner': name, 'path': relative.as_posix(), 'destination': destination, 'source_mode': f'{source_mode:04o}', 'staged_mode': f'{mode:04o}', 'sha256': digest, 'size': size})
                    safe_entries[relative.as_posix()] = (data, mode)
                    staged_source_file_count += 1
                elif entry.get('type') not in {'directory', 'symlink'}:
                    raise FleetProblem(f'Unknown skill closure entry type: {name}')
            for entry in skill.get('entries', []):
                if entry.get('type') != 'symlink': continue
                relative = _relative(entry.get('relative_path')); target_exists = entry.get('target_exists') is True
                target = Path(entry.get('resolved_target', '')); inside = False
                if target_exists:
                    try: target_relative = target.resolve(strict=True).relative_to(root.resolve(strict=True)); inside = True
                    except (FileNotFoundError, ValueError): inside = False
                if not inside:
                    reason = 'broken_external_symlink' if not target_exists else 'external_symlink_not_portable'
                    gap = {'owner': name, 'path': relative.as_posix(), 'reason': reason, 'target_class': entry.get('target_classification', {}).get('root_class', 'unknown')}
                    gaps.append(gap); owner_gaps.append(reason); continue
                prefix = target_relative.as_posix().rstrip('/')
                matches = [(path, value) for path, value in safe_entries.items() if path == prefix or path.startswith(prefix + '/')]
                if not matches:
                    gaps.append({'owner': name, 'path': relative.as_posix(), 'reason': 'internal_symlink_target_not_packaged', 'target_class': 'inside_skill'})
                    owner_gaps.append('internal_symlink_target_not_packaged'); continue
                count = 0
                for source_relative, (data, mode) in matches:
                    suffix = source_relative[len(prefix):].lstrip('/')
                    destination = f"agent/skills/{name}/{relative.as_posix()}" + (f'/{suffix}' if suffix else '')
                    if _write(stage, destination, data, mode): relative_files.append(destination); count += 1
                materialized.append({'owner': name, 'path': relative.as_posix(), 'source': prefix, 'file_count': count})
            statuses[name] = 'blocked' if 'broken_external_symlink' in owner_gaps else ('partial' if owner_gaps else 'packaged_unverified')

        for agent in dependencies['agents']:
            name = _name(agent.get('name'), 'agent'); captured = agent_map.get(name)
            if not captured or agent.get('snapshot_sha256') != captured.get('sha256'):
                raise FleetProblem(f'Agent closure is not bound to the inventory: {name}')
            if not agent.get('stable_during_scan') or not agent.get('snapshot_match_pre'):
                raise FleetProblem(f'Agent drifted during capture: {name}')
            source = Path(agent.get('path', ''))
            if source.is_symlink() or not source.is_file(): raise FleetProblem(f'Agent source is unavailable: {name}')
            data = source.read_bytes(); digest = hashlib.sha256(data).hexdigest()
            if digest != agent.get('snapshot_sha256') or len(data) != agent.get('size_bytes'): raise FleetProblem(f'Agent source drifted: {name}')
            agent_source_count += 1; destination = f'agent/agents/{name}.md'
            try: deploy._scan_secret(destination, data)
            except deploy.BundleError:
                quarantined.append({'owner': name, 'path': f'{name}.md', 'reason': 'cas_secret_scan_rejected', 'size': len(data)})
                agent_status[name] = 'partial'; cas_rejected_count += 1; continue
            source_mode = stat.S_IMODE(source.stat().st_mode); mode = _staged_mode(source_mode)
            _write(stage, destination, data, mode); relative_files.append(destination); copied_agent_count += 1; agent_status[name] = 'packaged_unverified'
            if mode != source_mode:
                mode_normalizations.append({'owner': name, 'path': f'{name}.md', 'destination': destination, 'source_mode': f'{source_mode:04o}', 'staged_mode': f'{mode:04o}', 'sha256': digest, 'size': len(data)})

        expected_safe = dependencies.get('summary', {}).get('safe_content_hashed_file_count')
        expected_excluded = dependencies.get('summary', {}).get('content_hash_excluded_file_count')
        inventory_quarantined = sum(row['reason'] != 'cas_secret_scan_rejected' for row in quarantined)
        if source_file_count != expected_safe or inventory_quarantined != expected_excluded:
            raise FleetProblem('Staged file counts do not match dependency evidence.')
        report = {
            'schema_version': PARITY_SCHEMA,
            'source_inventory_sha256': inventory_hash,
            'dependency_closure_sha256': dependencies_hash,
            'effective_skill_manifest_sha256': inventory['skills'].get('effective_manifest_sha256'),
            'current_disk_skill_count': len(statuses),
            'agent_source_count': agent_source_count,
            'agent_staged_count': copied_agent_count,
            'safe_source_file_count': source_file_count,
            'staged_safe_file_count': staged_source_file_count,
            'resolved_internal_symlink_file_count': sum(row['file_count'] for row in materialized),
            'quarantined_file_count': len(quarantined),
            'inventory_quarantined_file_count': expected_excluded,
            'cas_rejected_file_count': cas_rejected_count,
            'symlink_gap_count': len(gaps),
            'external_symlink_gap_count': sum(row['reason'] in {'external_symlink_not_portable', 'broken_external_symlink'} for row in gaps),
            'internal_symlink_gap_count': sum(row['reason'] == 'internal_symlink_target_not_packaged' for row in gaps),
            'skill_status_counts': {value: list(statuses.values()).count(value) for value in ('packaged_unverified', 'partial', 'blocked')},
            'skill_status': statuses,
            'agent_status': agent_status,
            'quarantined': quarantined,
            'symlink_materializations': materialized,
            'mode_policy': {'id': MODE_POLICY, 'rule': 'staged_mode = source_mode with group/world write bits cleared', 'bytes_unchanged': True, 'exact_source_mode_parity': False, 'normalized_file_count': len(mode_normalizations), 'normalized_files': mode_normalizations},
            'gaps': gaps,
            'claims': {'current_disk_catalog_packaged': True, 'fresh_omp_load_verified': False, 'historical_live_session_parity': False, 'full_local128_session_parity': False},
        }
        report_path = stage/'parity-report.json'; report_path.write_text(canonical(report)+'\n', encoding='utf-8'); report_path.chmod(0o600); relative_files.append('parity-report.json')
        bundle = deploy.build_bundle(stage, relative_files, Path(output_root)); verified = deploy.verify_bundle(bundle.root)
    if verified['release_id'] != bundle.release_id: raise FleetProblem('Parity CAS verification identity changed.')
    return {'release_id': bundle.release_id, 'root': str(bundle.root), 'manifest': verified, 'report': report}


def main(argv=None):
    parser = argparse.ArgumentParser(description='Build a sealed current-disk OMP catalog reconstruction.')
    parser.add_argument('--inventory', required=True); parser.add_argument('--dependencies', required=True); parser.add_argument('--output', required=True)
    args = parser.parse_args(argv)
    result = build_parity_bundle(args.inventory, args.dependencies, args.output)
    print(canonical({'release_id': result['release_id'], 'root': result['root'], 'report': result['report']}))


if __name__ == '__main__': main()
