#!/usr/bin/env python3
"""Check the packaged meta-skill routing graph; this does not execute its steps."""
import json
from pathlib import Path


def verify(root):
    root=Path(root).resolve()
    catalog=json.loads((root/'config/meta-catalog.json').read_text())
    entries=catalog['metaskills']
    if len(entries)!=20:
        raise ValueError('exactly 20 catalog entries required')
    ids=[e['id'] for e in entries]
    source_ids={s['id'] for s in catalog['sources']}
    if len(set(ids))!=20 or not all(ids):
        raise ValueError('meta IDs must be unique and nonempty')
    routes=set()
    for e in entries:
        paths=[e['path'],*e['routes']]
        if len(set(e['routes']))<2:
            raise ValueError('each meta must route at least two substantive stages')
        if not e.get('source_ids'):
            raise ValueError('missing source provenance')
        if not set(e['source_ids']).issubset(source_ids):
            raise ValueError('unknown source provenance ID')
        for relative in paths:
            p=(root/relative).resolve()
            if not p.is_relative_to(root) or not p.is_file() or p.name!='SKILL.md':
                raise ValueError('missing/out-of-scope route: '+relative)
            text=p.read_text()
            if not text.startswith('---\n') or '\nname:' not in text or '\ndescription:' not in text:
                raise ValueError('invalid skill frontmatter: '+relative)
        routes.update(e['routes'])
    for required in ('steps/aside-cli/SKILL.md','steps/jev-decision/SKILL.md','steps/jev-image/SKILL.md'):
        if required not in routes:
            raise ValueError('required execution route absent: '+required)
    return {'status':'CATALOG_PASS','metaskills':len(entries),'distinct_step_routes':len(routes),
            'runtime_verified':False}


if __name__=='__main__':
    try:
        print(json.dumps(verify(Path(__file__).parents[1]),indent=2))
    except (OSError,ValueError,KeyError,TypeError) as e:
        print(json.dumps({'status':'BLOCK','error':str(e)}));raise SystemExit(2)
