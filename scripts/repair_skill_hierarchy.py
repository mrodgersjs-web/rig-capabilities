#!/usr/bin/env python3
"""Repair routing only. Canonical-only check is read-only; installed copies are out of scope; --apply backs up changed files."""
from __future__ import annotations
import argparse
from collections import defaultdict
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import tempfile
from datetime import datetime, timezone

REPO = Path(__file__).resolve().parents[1]
SKILLS = REPO / 'capabilities/skills'
ROOTS = {'canonical': SKILLS, 'aside-user': Path.home()/'.aside/u/0/skills/user',
         'aside-builtin': Path.home()/'.aside/u/0/skills/builtin', 'hermes': Path.home()/'.hermes/skills'}
ULTRAPLAN = Path.home()/'Developer/ultraplan/SKILL.md'
BLOCKED = {'references', 'node_modules', '.git', 'vendor', '__pycache__'}
MARKER = '<!-- canonical-category-router -->'
CATEGORY_ROUTES = {
    'productivity': 'when-using-personal-tools',
    'site-specific': 'when-using-personal-tools',
    'email': 'when-using-personal-tools',
    'smart-home': 'when-using-personal-tools',
    'mobile': 'when-shipping-code',
    'devops': 'when-shipping-code',
    'mlops': 'when-working-with-data',
}
WEBSITE_FAMILIES = frozenset({
    'web-design-discovery', 'web-typography', 'web-color', 'web-layout',
    'web-motion', 'web-imagery', 'web-conversion-copy',
    'web-design-business', 'web-build-ship', 'web-design-critique',
})


META_DESCRIPTIONS = {
    'when-using-personal-tools': 'Route weekly reviews, commitments, stalled projects, next-week planning, calendar and productivity tasks, email, documents, and personal tools to their owning skill family.',
    'when-nothing-else-fits': 'Fallback only after checking the specific meta routes and finding no relevant owning family or skill; search the remaining unassigned skills.',
}


def quick_index(entries, nodes, edges):
    owned = {key: sorted(b for a,b in edges if a == key) for key in entries}
    ordered = sorted(entries, key=lambda key: (
        0 if nodes[key]['name'] == 'productivity' and owned[key] else 1 if owned[key] else 2,
        nodes[key]['name']))
    lines = []
    for key in ordered[:12]:
        summary = nodes[key]['description']
        kids = owned[key]
        if kids:
            labels = '; '.join(nodes[c]['name'] + ': ' + nodes[c]['description'][:100] for c in kids[:8])
            summary += ' Child tasks: ' + labels
            if len(kids) > 8: summary += '; see full routing table for further children.'
        lines.append(f'- [{nodes[key]["name"]}]({key}) — {summary}')
    return '\n'.join(lines)


def route_categories(assignments):
    for name, target in CATEGORY_ROUTES.items():
        if not any(name in names for names in assignments.values()):
            continue
        if target not in assignments:
            raise ValueError(f'Missing category meta target: {target}')
        for meta, names in assignments.items():
            assignments[meta] = [n for n in names if n != name]
        assignments[target].append(name)


def canonical_family_children(name, skills):
    """Return only the canonical siblings claimed by a known family router."""
    parent = skills / name / 'SKILL.md'
    if not parent.is_file():
        return []
    parent_text = parent.read_text(errors='replace')
    if name == 'rig-revenue-meta':
        if '## Routing table' not in parent_text or '## Step 1' not in parent_text:
            return []
        parent_text = parent_text.split('## Routing table', 1)[1].split('## Step 1', 1)[0]
        candidates = skills.glob('rig-revenue-*/SKILL.md')
    elif name in WEBSITE_FAMILIES:
        candidates = skills.glob(f'{name}-*/SKILL.md')
    else:
        return []
    return sorted((path for path in candidates
                   if path.parent.name != name and path.parent.name in parent_text), key=str)


def fingerprint(path):
    return (str(path.resolve()), hashlib.sha256(path.read_bytes()).hexdigest() if path.is_file() else None)


class RepairPlan(dict):
    def __init__(self, content, owned_root, sources):
        super().__init__(content)
        self.owned_root = owned_root.resolve()
        self.expected = {p: fingerprint(p) for p in set(content) | set(sources)}

    def preflight(self):
        for path in self:
            if path.is_symlink() or not path.resolve().is_relative_to(self.owned_root):
                raise ValueError(f'Destination outside owned root or symlink: {path}')
        for path, expected in self.expected.items():
            if fingerprint(path) != expected:
                raise ValueError(f'Source drift after plan: {path}')


def clean(text):
    # The old re.sub('|', ...) inserted a slash at every character boundary.
    if re.search(r'(?:/[^/]){8}', text):
        text = text.replace('/', '')
    return ' '.join(text.replace('|', ' ').split()).strip('"\'')


def description(path):
    text = path.read_text(errors='replace')
    match = re.search(r'^description:\s*(.+)$', text, re.M)
    if match and match[1].strip() not in {'>', '|', '>-', '|-'}:
        return clean(match[1])[:240]
    return 'Read this existing skill and follow its documented scope.'


def resolve(name, roots):
    for root in roots.values():
        target = root/name/'SKILL.md'
        if target.is_file():
            return target.absolute()
    raise ValueError(f'Missing skill: {name}')


def children(path, roots):
    """Nearest real skill descendants; exclude reference/resource trees and self copies."""
    result = {}
    parent_name = path.parent.name
    for base, dirs, files in os.walk(path.parent, followlinks=False):
        dirs[:] = sorted(d for d in dirs if d not in BLOCKED and not d.startswith('.'))
        base = Path(base)
        if base != path.parent and 'SKILL.md' in files:
            child = base/'SKILL.md'
            if base.name != parent_name:
                child = child.absolute()
                if child != path.absolute():
                    result.setdefault(str(child.resolve()), child)
            dirs[:] = []
    return sorted(result.values(), key=str)


def _inside(path, root):
    try:
        Path(path).resolve().relative_to(Path(root).resolve())
        return True
    except ValueError:
        return False


def normalize_graph(nodes, edges, canonical_root):
    """Collapse aliases and expose exactly meta-skill -> skill -> subskill."""
    groups = defaultdict(list)
    for key, item in nodes.items():
        groups[item['resolved_target']].append(key)

    def rank(key):
        item = nodes[key]
        source = Path(item['source'])
        return (
            source.resolve() != source.absolute(),
            0 if _inside(source, canonical_root) else 1,
            len(source.parts),
            str(source),
        )

    winner = {}
    aliases = []
    for target, keys in groups.items():
        chosen = min(keys, key=rank)
        for key in keys:
            winner[key] = chosen
            if key != chosen:
                aliases.append({
                    'alias': nodes[key]['source'],
                    'owner': nodes[chosen]['source'],
                    'resolved_target': target,
                    'reason': 'same physical skill target',
                })

    meta_ids = {winner[key] for key, item in nodes.items() if item['level'] == 1}
    non_meta_incoming = {
        winner[b] for a, b in edges
        if winner[a] not in meta_ids and winner[a] != winner[b]
    }
    normalized = set()
    shadowed_assignments = []
    for a, b in edges:
        ra, rb = winner[a], winner[b]
        if ra == rb:
            continue
        if winner[a] in meta_ids and rb in non_meta_incoming:
            shadowed_assignments.append({
                'meta_skill': nodes[winner[a]]['name'],
                'alias': nodes[b]['source'],
                'owner': nodes[rb]['source'],
                'reason': 'top-level assignment is already owned as a subskill',
            })
            continue
        normalized.add((ra, rb))

    kept = {key: dict(nodes[key]) for key in set(winner.values())}
    adjacency = defaultdict(set)
    for a, b in normalized:
        if a not in meta_ids:
            adjacency[a].add(b)
    meta_edges = {(a, b) for a, b in normalized if a in meta_ids}
    top_skills = {b for _, b in meta_edges}
    subskill_owner = {}
    flat_edges = set(meta_edges)
    for skill in sorted(top_skills):
        stack = list(adjacency[skill])
        seen = set()
        while stack:
            child = stack.pop()
            if child in seen:
                continue
            seen.add(child)
            if child in top_skills:
                raise ValueError(
                    f'Skill is both top-level and nested without an alias: {kept[child]["source"]}'
                )
            prior = subskill_owner.get(child)
            if prior is not None and prior != skill:
                raise ValueError(f'Subskill has multiple owners: {kept[child]["source"]}')
            subskill_owner[child] = skill
            stack.extend(adjacency[child])
        flat_edges.update((skill, child) for child in seen)

    reachable = set(meta_ids) | top_skills | set(subskill_owner)
    kept = {key: value for key, value in kept.items() if key in reachable}
    for key, item in kept.items():
        item['level'] = 1 if key in meta_ids else 2 if key in top_skills else 3
    return kept, flat_edges, sorted(aliases, key=lambda row: row['alias']), \
        sorted(shadowed_assignments, key=lambda row: row['alias'])


def _quality_audit(skills):
    from rig_capabilities.catalog import _quality_block
    from rig_capabilities.quality import check_asset

    repo_root = skills.parents[1]
    residuals = []
    field_full = exemplar_present = real_done_test = fully_verifiable = 0
    paths = sorted(p / 'SKILL.md' for p in skills.iterdir()
                   if p.is_dir() and (p / 'SKILL.md').is_file())
    for path in paths:
        quality = _quality_block(path.read_text(errors='replace'))
        row = check_asset({'id': path.parent.name, 'kind': 'skill', 'quality': quality})
        field_full += row['score'] == 100
        example = quality.get('great_example')
        example_path = Path(example) if example else None
        if example_path and not example_path.is_absolute():
            example_path = repo_root / example_path
        has_example = bool(example_path and example_path.is_file())
        exemplar_present += has_example
        done = quality.get('done_when') or []
        has_real = any(str(entry).startswith(('cmd:', 'grep:', 'mcp:')) for entry in done)
        real_done_test += has_real
        complete = row['score'] == 100 and has_example and has_real
        fully_verifiable += complete
        if not complete:
            residuals.append({
                'id': path.parent.name,
                'missing_fields': row['missing'],
                'great_example_exists': has_example,
                'has_real_done_test': has_real,
                'score': row['score'],
            })
    return {
        'total': len(paths),
        'field_full': field_full,
        'great_example_present': exemplar_present,
        'real_done_test': real_done_test,
        'fully_verifiable': fully_verifiable,
        'residual_count': len(residuals),
        'residuals': residuals,
    }


def _installation_audit(skills, install_roots):
    harnesses = {name: Path(os.path.expanduser(path))
                 for name, path in (install_roots or {}).items() if path}
    rows = []
    cells = defaultdict(int)
    paths = sorted(p / 'SKILL.md' for p in skills.iterdir()
                   if p.is_dir() and (p / 'SKILL.md').is_file())
    matched_skills = 0
    for source in paths:
        expected = hashlib.sha256(source.read_bytes()).hexdigest()
        states = {}
        for harness, root in harnesses.items():
            target = root / source.parent.name / 'SKILL.md'
            if not target.is_file():
                state = 'absent'
            else:
                actual = hashlib.sha256(target.read_bytes()).hexdigest()
                state = 'match' if actual == expected else 'drift'
            states[harness] = state
            cells[state] += 1
        if states and all(state == 'match' for state in states.values()):
            matched_skills += 1
        elif any(state != 'match' for state in states.values()):
            rows.append({'id': source.parent.name, 'states': states})
    return {
        'canonical_skills': len(paths),
        'harnesses': sorted(harnesses),
        'cells': dict(sorted(cells.items())),
        'all_match': matched_skills,
        'residual_count': len(rows),
        'residuals': rows,
    }


def _route_depth(nodes, edges):
    adjacency = defaultdict(list)
    for a, b in edges:
        adjacency[a].append(b)

    def walk(key, active=()):
        if key in active:
            return 999
        return 1 + max((walk(child, active + (key,))
                        for child in adjacency[key]), default=0)

    return max((walk(key) for key, item in nodes.items() if item['level'] == 1),
               default=0)


def audit_graph(skills, nodes, edges):
    """Audit the semantic graph without treating generated files as proof."""
    normalized, flat_edges, aliases, shadowed = normalize_graph(nodes, edges, skills)
    canonical = {str(path.resolve()) for path in skills.glob('*/SKILL.md')}
    covered = {item['resolved_target'] for item in normalized.values()}
    incoming = defaultdict(set)
    levels = {key: item['level'] for key, item in normalized.items()}
    bad_edges = []
    for parent, child in flat_edges:
        incoming[child].add(parent)
        if (levels[parent], levels[child]) not in {(1, 2), (2, 3)}:
            bad_edges.append([parent, child])
    multiple_owners = sorted(key for key, owners in incoming.items() if len(owners) != 1)
    orphans = sorted(canonical - covered)
    counts = {str(level): sum(item['level'] == level for item in normalized.values())
              for level in (1, 2, 3)}
    depth = _route_depth(normalized, flat_edges)
    failures = []
    if orphans:
        failures.append('canonical_orphans')
    if multiple_owners:
        failures.append('multiple_owners')
    if bad_edges or depth != 3 or not all(counts.values()):
        failures.append('invalid_three_tier_graph')
    return {
        'status': 'PASS' if not failures else 'RED',
        'failures': failures,
        'canonical_skill_total': len(canonical),
        'canonical_skill_covered': len(canonical) - len(orphans),
        'canonical_orphans': orphans,
        'levels': counts,
        'route_depth_max': depth,
        'nodes': len(normalized),
        'edges': len(flat_edges),
        'physical_aliases': aliases,
        'shadowed_assignments': shadowed,
        'multiple_owners': multiple_owners,
        'bad_edges': bad_edges,
    }


def audit_materialization(report, output):
    """A valid proposed graph is not a deployed routing surface."""
    changed = sorted(str(path) for path, text in output.items()
                     if not path.is_file() or path.read_text() != text)
    gated = dict(report)
    gated['structural_status'] = gated.pop('status')
    gated['materialized_status'] = 'PASS' if not changed else 'DRIFT'
    gated['materialized_changed_paths'] = changed
    gated['status'] = ('PASS' if gated['structural_status'] == 'PASS'
                       and not changed else 'RED')
    return gated


def protected_meta_rewrites(output):
    """Never replace an authored meta-skill just to refresh its route index."""
    return sorted(str(path) for path, text in output.items()
                  if path.name == 'SKILL.md' and path.parent.name.startswith('when-')
                  and path.is_file() and path.read_text() != text)


def _estate_audit(skills, nodes, edges, aliases, shadowed_assignments,
                  install_roots):
    canonical = sorted((p / 'SKILL.md').resolve() for p in skills.iterdir()
                       if p.is_dir() and (p / 'SKILL.md').is_file())
    covered = {Path(item['resolved_target']).resolve() for item in nodes.values()}
    orphans = [str(path) for path in canonical if path not in covered]
    levels = defaultdict(int)
    for item in nodes.values():
        levels[str(item['level'])] += 1
    hierarchy = {
        'canonical_skill_total': len(canonical),
        'canonical_skill_covered': len(canonical) - len(orphans),
        'canonical_orphans': orphans,
        'levels': dict(sorted(levels.items())),
        'route_depth_max': _route_depth(nodes, edges),
        'unique_physical_targets': len({item['resolved_target'] for item in nodes.values()}),
        'shadow_alias_count': len(aliases),
        'shadowed_top_level_assignment_count': len(shadowed_assignments),
    }
    return {
        'schema_version': 1,
        'hierarchy': hierarchy,
        'quality': _quality_audit(skills),
        'installation': _installation_audit(skills, install_roots),
        'resolved_aliases': aliases,
        'shadowed_assignments': shadowed_assignments,
    }


def validate(manifest, planned=()):
    if manifest.get('unresolved'):
        raise ValueError('Unresolved children: ' + json.dumps(manifest['unresolved']))
    nodes = manifest['nodes']; ids = [n['id'] for n in nodes]
    if len(ids) != len(set(ids)):
        raise ValueError('Duplicate nodes')
    known = set(ids); pending = {str(Path(p).absolute()) for p in planned}
    levels = {n['id']: n['level'] for n in nodes}
    if not set(levels.values()).issubset({1, 2, 3}) or not {1, 2}.issubset(set(levels.values())):
        raise ValueError('Invalid three-tier levels')
    physical = [n['resolved_target'] for n in nodes]
    if len(physical) != len(set(physical)):
        raise ValueError('Duplicate physical ownership')
    for n in nodes:
        p = Path(n['source'])
        if not p.is_absolute() or p.name != 'SKILL.md' or (not p.is_file() and str(p) not in pending):
            raise ValueError(f'Missing target: {p}')
        if re.search(r'(?:/[^/]){8}', n['description']):
            raise ValueError(f'Corrupted description: {n["id"]}')
    edges = [tuple(e) for e in manifest['edges']]
    if len(edges) != len(set(edges)):
        raise ValueError('Duplicate edges')
    graph = {n: [] for n in known}
    incoming = defaultdict(set)
    for a,b in edges:
        if a not in known or b not in known:
            raise ValueError('Missing edge target')
        graph[a].append(b)
        incoming[b].add(a)
    active=set(); done=set()
    def visit(n):
        if n in active: raise ValueError(f'Cycle: {n}')
        if n in done: return
        active.add(n)
        for child in graph[n]: visit(child)
        active.remove(n);done.add(n)
    for n in sorted(known): visit(n)
    for a, b in edges:
        if (levels[a], levels[b]) not in {(1, 2), (2, 3)}:
            raise ValueError(f'Invalid three-tier edge: {a} -> {b}')
    if any(incoming[key] for key in known if levels[key] == 1) or any(
        len(incoming[key]) != 1 for key in known if levels[key] != 1
    ):
        raise ValueError('Invalid or duplicate owner')
    if _route_depth({n['id']: n for n in nodes}, edges) > 3:
        raise ValueError('Invalid three-tier route depth')
    canonical_root = manifest.get('source_roots', {}).get('canonical')
    if canonical_root:
        canonical = {str(path.resolve()) for path in Path(canonical_root).glob('*/SKILL.md')}
        if canonical - set(physical):
            raise ValueError('Canonical orphan skills: ' + ', '.join(sorted(canonical - set(physical))))


def plan(skills=SKILLS, roots=None, ultraplan=ULTRAPLAN, inventory=None):
    roots = roots or ROOTS
    prior_manifest = skills/'when-building-or-fixing-agents/references/hierarchy.json'
    if inventory is None:
        if prior_manifest.is_file():
            inventory=json.loads(prior_manifest.read_text()).get('inventory_declarations', {})
        else:
            inventory=json.loads((Path.home()/'Desktop/Projects/skillshilp-upgrade/inventory.json').read_text())
    unresolved=[]
    old_snapshot=json.loads(prior_manifest.read_text()) if prior_manifest.is_file() else {}
    output={}; assignments={}; descriptions={}; original=[]; excluded=[]; old_children={}; source_hints={}
    preserved_rows=defaultdict(list)
    for table in sorted(skills.glob('when-*/references/routing.md')):
        meta=table.parent.parent.name
        descriptions[meta]=META_DESCRIPTIONS.get(meta, description(table.parent.parent/'SKILL.md').split(' Routes to ')[0])
        assignments[meta]=[]
        for line in table.read_text().splitlines():
            if not line.startswith('| '): continue
            fields=[v.strip() for v in line.split('|')[1:-1]]
            if fields[0]=='Skill': continue
            name=fields[0]
            if not re.fullmatch(r'[a-z0-9][a-z0-9-]*', name):
                preserved_rows[meta].append(line)
                continue
            if len(fields)>1:
                link=re.fullmatch(r'\[[^\]]+\]\((/[^)]+/SKILL\.md)\)', fields[1])
                if link:
                    hint=Path(link[1])
                    if not hint.is_file() or ('..' in hint.parts) or not (hint == ultraplan or any(hint.is_relative_to(root.absolute()) for root in roots.values())):
                        raise ValueError(f'Missing or out-of-root explicit source: {hint}')
                    source_hints[(meta,name)]=hint
            if name.startswith('when-') or name in {'references','Skill'}:
                excluded.append({'parent':meta,'name':name,'reason':'meta/self or resource reference'})
                continue
            original.append([meta,name])
            assignments[meta].append(name)
            if len(fields)>3 and fields[3] not in {'-', 'Leaf: no subskill required'}:
                old_children[name]=[v.strip() for v in fields[3].split(',') if v.strip()]
    old_children=old_snapshot.get('old_child_declarations',old_children)
    # Existing generated families must not silently disappear after a legacy
    # flat-table regeneration. Require reconciliation rather than green drift.
    declared_names={name for names in assignments.values() for name in names}
    missing_families=sorted(p.parent.name for p in skills.glob('*/SKILL.md')
                            if MARKER in p.read_text() and p.parent.name not in declared_names)
    if missing_families:
        raise ValueError('Unrouted existing categories: ' + ', '.join(missing_families))
    for name,target in {**CATEGORY_ROUTES, 'codex-fusion':'when-building-or-fixing-agents'}.items():
        hints={path for (meta,n),path in source_hints.items() if n==name}
        if len(hints)>1:
            raise ValueError(f'Conflicting explicit sources for moved skill: {name}')
        if hints: source_hints[(target,name)]=next(iter(hints))
    route_categories(assignments)
    agent='when-building-or-fixing-agents'
    if agent in assignments:
        for values in assignments.values():
            if 'codex-fusion' in values: values.remove('codex-fusion')
        assignments[agent] += ['codex-fusion','ultraplan','rig-tac-doctrine']
    nodes={}; edges=set(); expanded=set()
    def node(path, level, desc=None):
        path=path.absolute(); key=str(path)
        if key not in nodes:
            nodes[key]={'id':key,'source':key,'name':path.parent.name,'level':level,
                        'description':desc or description(path), 'resolved_target':str(path.resolve())}
        else: nodes[key]['level']=min(nodes[key]['level'],level)
        return key
    def expand(path, level):
        key=str(path.absolute())
        if key in expanded:return
        expanded.add(key)
        for child in children(path,roots):
            ck=node(child,level+1);edges.add((key,ck));expand(child,level+1)
    for meta,names in assignments.items():
        mk=node(skills/meta/'SKILL.md',1,descriptions[meta])
        for name in sorted(set(names)):
            if name=='ultraplan':
                if not ultraplan.is_file(): raise ValueError(f'Missing exact UltraPlan source: {ultraplan}')
                path=ultraplan.absolute()
            else:
                try:
                    path=source_hints.get((meta,name)) or resolve(name,roots)
                    category=MARKER in path.read_text()
                except ValueError:
                    category=True
                if category:
                    path=(skills/name/'SKILL.md').absolute()
                    category_children=[]
                    for root in roots.values():
                        directory=root/name
                        if directory.is_dir():
                            category_children+=children(directory/'SKILL.md',roots)
                    category_children=sorted(set(category_children),key=str)
                    if not category_children:raise ValueError(f'No real children for category: {name}')
                    desc=f'Route {name} tasks to an existing child skill; this router adds no capabilities.'
                    body=f'---\nname: {name}\ndescription: {json.dumps(desc)}\n---\n\n{MARKER}\n# {name}\n\nSelect the relevant child below, read its SKILL.md, and follow its instructions. Do not load unrelated children.\n\n'
                    body+='\n'.join(f'- [{c.parent.name}]({c}) — {description(c)}' for c in category_children)+'\n'
                    output[path]=body
                    node(path,2,desc)
                    for c in category_children:
                        ck=node(c,3);edges.add((str(path),ck));expand(c,3)
            pk=node(path,2,nodes.get(str(path),{}).get('description'));edges.add((mk,pk))
            if path.is_file() and MARKER not in path.read_text():expand(path,2)
            for child in canonical_family_children(name, skills):
                ck=node(child,3)
                edges.add((pk,ck))
                expand(child,3)
            info=inventory.get(name,{})
            for hint in sorted(set(info.get('children',[]))):
                parts=Path(hint).parts
                if any(part in BLOCKED for part in parts) or Path(hint).name==name:
                    excluded.append({'parent':name,'name':hint,'reason':'resource tree or self copy'})
                    continue
                candidates=[Path(info.get('path',str(path.parent))).parent/hint/'SKILL.md']
                candidates += [root/hint/'SKILL.md' for root in roots.values()]
                child=next((p.absolute() for p in candidates if p.is_file()),None)
                if child is None:
                    unresolved.append({'parent':name,'child':hint})
                    continue
                ck=node(child,3)
                if ck==pk:
                    excluded.append({'parent':name,'name':hint,'reason':'self copy'})
                    continue
                edges.add((pk,ck));expand(child,3)
            for declared in old_children.get(name,[]):
                if declared in BLOCKED or declared==name:
                    excluded.append({'parent':name,'name':declared,'reason':'old table resource or self reference'})
                    continue
                hints=info.get('children',[])
                if any(Path(hint).name==declared and any(part in BLOCKED for part in Path(hint).parts) for hint in hints):
                    excluded.append({'parent':name,'name':declared,'reason':'old table dependency/resource entry'})
                    continue
                matched=[b for a,b in edges if a==pk and nodes[b]['name']==declared]
                if not matched:unresolved.append({'parent':name,'child':declared,'source':'old routing table'})
    nodes, edges, aliases, shadowed_assignments = normalize_graph(nodes, edges, skills)
    for meta in assignments:
        mk = str((skills/meta/'SKILL.md').absolute())
        entries = sorted((child for parent, child in edges if parent == mk),
                         key=lambda key: (nodes[key]['name'], key))
        lines=['| Skill | Source | One-liner | Sub-skills |','|---|---|---|---|']
        for key in entries:
            n=nodes[key];kids=sorted(b for a,b in edges if a==key)
            kidlinks=', '.join(f'[{nodes[c]["name"]}]({c})' for c in kids) or 'Leaf: no subskill required'
            lines.append(f'| {n["name"]} | [{n["name"]}]({key}) | {n["description"]} | {kidlinks} |')
        table=skills/meta/'references/routing.md'
        output[table]='# Routing\n\nSelect one skill by task. Load its source, then select only the relevant listed subskill. The explicit links below supplement existing parent instructions without replacing doctrine. Leaves need no invented subskill.\n\n'+'\n'.join(lines)+'\n'
        if preserved_rows[meta]:
            output[table]+='\n## Preserved notes\n\n'+'\n'.join(preserved_rows[meta])+'\n'
    subindex=skills/agent/'references/subskills.md'
    sublines=['# Existing parent-to-subskill routing', '', 'After reading a parent, use its task-specific instructions first. For additional existing children, select only a relevant entry below and read its exact source. Presence in this index does not mandate invoking a child or bypass any parent gate.', '']
    for parent in sorted({a for a,b in edges if nodes[a]['level']>1}):
        sublines += [f'## [{nodes[parent]["name"]}]({parent})', '']
        sublines += [f'- [{nodes[child]["name"]}]({child}) — {nodes[child]["description"]}' for a,child in sorted(edges) if a==parent]
        sublines.append('')
    output[subindex]='\n'.join(sublines)
    contract=skills/agent/'references/meta-first.md'
    output[contract]='# Meta-first routing contract\n\nSelect the relevant meta router below, read one task-matched skill, then read its relevant existing subskill when listed. Leaves need no invented child. Use when-nothing-else-fits only after the specific routes have no relevant match. This routing contract never bypasses higher-priority doctrine or approval requirements.\n\n'+'\n'.join(f'- [{m}]({(skills/m/"SKILL.md").absolute()}) — {descriptions[m]}' for m in sorted(assignments, key=lambda name: (name == 'when-nothing-else-fits', name)))+'\n'
    final_entries=sorted([m,n] for m,ns in assignments.items() for n in set(ns))
    previous=skills/agent/'references/hierarchy.json'
    baseline=original
    if previous.is_file():
        baseline=json.loads(previous.read_text()).get('reconciliation',{}).get('original_entries',original)
    reconciliation={'original_entries':baseline,'original_count':len(baseline),'current_count':len(final_entries),'added':[x for x in final_entries if x not in baseline],'removed':[x for x in baseline if x not in final_entries],'excluded':excluded}
    manifest={'schema_version':2, 'subskill_index':str(subindex.absolute()), 'unresolved':unresolved, 'old_child_declarations':old_children, 'inventory_declarations':{n:inventory[n] for ns in assignments.values() for n in sorted(set(ns)) if n in inventory and inventory[n].get('children')}, 'reconciliation':reconciliation,'source_roots':{k:str(v.resolve()) for k,v in roots.items()},'nodes':sorted(nodes.values(),key=lambda n:n['id']),'edges':[list(e) for e in sorted(edges)], 'physical_aliases':aliases, 'shadowed_assignments':shadowed_assignments, 'parent_routing_evidence':[{'parent':a, 'child':b, 'child_named_in_parent':nodes[b]['name'] in (output.get(Path(a)) or Path(a).read_text(errors='replace')), 'routing_table_supplements_parent':True} for a,b in sorted(edges) if nodes[a]['level']>1]}
    validate(manifest,output)
    output[skills/agent/'references/hierarchy.json']=json.dumps(manifest,indent=2,sort_keys=True)+'\n'
    return RepairPlan(output,skills,[Path(n['source']) for n in manifest['nodes']]),manifest


def apply(output, backup_root):
    output.preflight()
    changed={p:t for p,t in output.items() if not p.is_file() or p.read_text()!=t}
    if not changed:return None
    backup=backup_root/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');backup.mkdir(parents=True,mode=0o700)
    records=[]
    for i,(p,text) in enumerate(sorted(changed.items(),key=lambda x:str(x[0]))):
        if p.is_symlink():raise ValueError(f'Refuse symlink write: {p}')
        old=p.read_bytes() if p.exists() else None
        if old is not None:(backup/str(i)).write_bytes(old)
        records.append({'path':str(p),'backup':str(i) if old is not None else None,'before_sha256':hashlib.sha256(old).hexdigest() if old is not None else None})
    (backup/'manifest.json').write_text(json.dumps(records,indent=2)+'\n')
    output.preflight()
    for p,text in changed.items():
        if p.is_symlink() or not p.resolve().is_relative_to(output.owned_root):
            raise ValueError(f'Destination containment changed: {p}')
        if fingerprint(p) != output.expected[p]:
            raise ValueError(f'Destination drift: {p}')
        p.parent.mkdir(parents=True,exist_ok=True)
        fd,tmp=tempfile.mkstemp(dir=p.parent)
        with os.fdopen(fd,'w') as f:f.write(text)
        os.chmod(tmp,p.stat().st_mode & 0o777 if p.exists() else 0o644);os.replace(tmp,p)
    return backup


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    modes=parser.add_mutually_exclusive_group();modes.add_argument('--apply',action='store_true');modes.add_argument('--check',action='store_true');modes.add_argument('--dry-run',action='store_true');modes.add_argument('--audit',action='store_true')
    args=parser.parse_args()
    try:
        output,manifest=plan()
    except ValueError as error:
        print(json.dumps({'status':'FAIL','unresolved':[str(error)]},indent=2))
        return 1
    report = audit_graph(SKILLS, {node['id']: node for node in manifest['nodes']},
                         {tuple(edge) for edge in manifest['edges']})
    report['physical_aliases'] = manifest['physical_aliases']
    report['shadowed_assignments'] = manifest['shadowed_assignments']
    if args.audit:
        gated = audit_materialization(report, output)
        print(json.dumps(gated, indent=2, sort_keys=True))
        return 0 if gated['status'] == 'PASS' else 1
    if report['status'] != 'PASS':
        print(json.dumps({'status': 'RED', 'failures': report['failures'],
                          'canonical_orphans': report['canonical_orphans'],
                          'route_depth_max': report['route_depth_max'],
                          'nodes': report['nodes'], 'edges': report['edges']}, indent=2))
        return 1
    protected = protected_meta_rewrites(output)
    if args.apply and protected:
        print(json.dumps({'status': 'RED', 'reason': 'protected_meta_skill_rewrite',
                          'paths': protected}, indent=2))
        return 1
    changed=[str(p) for p,t in output.items() if not p.is_file() or p.read_text()!=t]
    backup=apply(output,REPO/'.repair-backups/skill-hierarchy') if args.apply else None
    print(json.dumps({'status':'APPLIED' if args.apply else ('DRIFT' if changed else 'PASS'),'nodes':len(manifest['nodes']),'edges':len(manifest['edges']),'changed_paths':changed,'backup':str(backup) if backup else None},indent=2))
    return 0 if args.apply or args.dry_run or not changed else 1

if __name__=='__main__':raise SystemExit(main())
