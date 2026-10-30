#!/usr/bin/env python3
"""Assemble portable instructions and local checks; no installation or network calls."""
import argparse
import hashlib
import json
import re
import shutil
import zipfile
from pathlib import Path

VERSION = '1.4.0'


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--portable-base', type=Path, required=True)
    ap.add_argument('--canonical-core', type=Path, required=True)
    ap.add_argument('--slopmonster', type=Path, required=True)
    ap.add_argument('--output', type=Path, required=True)
    args = ap.parse_args()
    source = Path(__file__).resolve().parents[1]
    output = args.output.resolve()
    output.mkdir(parents=True, exist_ok=False)
    bundle = output / ('Job-Applier-Grokbot-' + VERSION)
    bundle.mkdir()
    provenance = []

    def put(path, body):
        dest = bundle / path
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(body.rstrip() + '\n')

    def copy(src, rel):
        if src.is_symlink():
            raise ValueError('refusing symlink: ' + str(src))
        data = src.read_bytes()
        dest = bundle / rel
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_bytes(data)
        provenance.append({'path':rel,'source_name':src.name,'source_sha256':hashlib.sha256(data).hexdigest()})

    for path in sorted((args.portable_base / 'skills').rglob('*')):
        if path.is_file() and '__pycache__' not in path.parts and path.suffix != '.pyc':
            copy(path, 'skills/' + path.relative_to(args.portable_base / 'skills').as_posix())
    for path in sorted(source.rglob('*')):
        rel = path.relative_to(source)
        if path.is_file() and '__pycache__' not in path.parts and path.suffix != '.pyc' and rel.parts[0] not in ('proof','dist') and path.name != 'build_bundle.py':
            copy(path, 'skills/job-applier-daily/' + rel.as_posix())
    for rel in ['SKILL.md','LICENSE','references/principles.md','references/signs-of-ai-writing.md','references/sources.md',
                'prompts/cleanse.txt','tools/deslop.py','tools/cleanse.sh','tools/test_deslop.py','tools/test_cleanse.sh']:
        copy(args.slopmonster / rel, 'skills/slopmonster/' + rel)
    principles = bundle/'skills/slopmonster/references/principles.md'
    principles.write_text(re.sub(r'\[([^\]]+)\]\(../examples/ridgeline-roofing.md\)',
                         r'\1 (historical client example omitted from this portable distribution)', principles.read_text()))

    def generic(text):
        text = re.sub(r"\bMike(?:['’]s)?\b", lambda m: "the candidate's" if any(c in m.group() for c in "'’") else 'the candidate', text)
        # These are adaptation pointers, not instructions to load author-machine state.
        text = text.replace('/Users/rig128gb/.applypilot', '${CANDIDATE_DATA_ROOT}')
        text = text.replace('/Users/rig128gb/Developer/aside-work', '${OPTIONAL_ASIDE_WORK_ROOT}')
        text = text.replace('/Users/rig128gb/.aside/u/0/skills/user', '${SKILLS_ROOT}')
        text = text.replace('/Users/rig128gb/.omp/agent/skills', '${SKILLS_ROOT}')
        return text

    for rel in ['references/word-format-fidelity.md','references/bounded-step-execution.md',
                'references/github-portfolio-evidence.md','references/temporal-daily-workflow.md']:
        body = generic((args.canonical_core / rel).read_text())
        if rel.endswith('github-portfolio-evidence.md'):
            body = re.sub(r'The 2026-10-29 discovery snapshot.*?\n\n', '', body, flags=re.S)
            body = re.sub(r'Start with the local evidence bank.*?\n\n',
                          'Use the candidate-selected local evidence bank, if supplied. Verify relevant current HEADs and account scope before reusing findings.\n\n', body, flags=re.S)
        put('skills/job-applier/' + rel, body)
    put('skills/job-applier/references/quality-gates.md', (bundle/'skills/job-applier/references/quality.md').read_text())
    guide = bundle/'skills/job-applier/references/quality-api.md'
    guide.write_text(re.sub(r'The bounded version 3 live control check.*',
                     'No live image-quality run for this distribution is claimed. Validate the provider and actual document pages in the destination environment.\n', guide.read_text(), flags=re.S))
    main = bundle / 'skills/job-applier/SKILL.md'
    text = main.read_text().replace('version: 1.1.0','version: 1.2.2')
    text = text.replace('literal UNCONFIRMED labels and clearly marked tentative placement',
                        'UNCONFIRMED Word comments or a claim/hash-bound worksheet, and clearly marked tentative placement')
    text += '\n\n## Portable daily composition\n\nFor daily discovery, employer research, cover letters and Airtable, start with [Job Applier Daily](../job-applier-daily/SKILL.md). This core is a portable adaptation of canonical 1.2.2. Read [Word fidelity](references/word-format-fidelity.md) before editing, [bounded execution](references/bounded-step-execution.md) before dispatch, and [portfolio evidence](references/github-portfolio-evidence.md) when using code as evidence. [Temporal contract](references/temporal-daily-workflow.md) describes optional runtime requirements, not an installed scheduler. No procedure printed in this bundle is an authentic approval.\n'
    main.write_text(text)
    put('README.md', '''# Job Applier Daily 1.4.0 — Grokbot handoff

Start with `UPLOAD-START-HERE.md`. This is a complete portable skill family and local audit tooling. It is not a running application bot. No application, routine or Airtable write is performed by unpacking it.

The entry skill is `skills/job-applier-daily/SKILL.md`; it composes 20 task-specific meta-skills, the canonical Job Applier 1.2.2 workflow, Julie W2 operating guidance, Lucy source guidance, SlopMonster, employer research, resume and cover-letter writers, and Airtable tracking. Grokbot coordinates through the documented Aside CLI operator route. Hosted JEV decision and image reviews are required before release of each application packet. See [all 20 meta-skills](skills/job-applier-daily/references/meta-catalog.md).

Verify before use:

```sh
python3 verify_bundle.py .
python3 skills/job-applier-daily/scripts/verify_catalog.py
python3 skills/job-applier-daily/scripts/preflight.py
python3 -m unittest discover -s skills/job-applier-daily/tests -v
python3 -m unittest discover -s skills/job-applier/tests -v
```

No network calls are made by these commands. Synthetic tests do not authorize applications. The local auditor cannot authenticate human approvals, provider responses, claim truth, browser state or real rendering.

Provide your master Word resume, confirmed career facts, and access to your own provider accounts separately. Do not upload credentials, cookies, raw private repository sources or this machine's profile directory.

Known prerequisites: Python 3.9+, the Aside CLI on its supported host, authenticated Airtable access, hosted TypeSafe/JEV credentials from the destination secret store, Word or LibreOffice plus PDF rendering tools, and a second model family for SlopMonster where available. Missing prerequisites remain holds; no automatic software install or credential reset occurs.

Release status: staged skill package. The initial JEV build review escalated for confidence and test gaps. Independent review found and repaired link and structural validation defects. Those repairs do not turn the initial JEV hold into a PASS. No live operation is certified by this package; destination integration and authentic per-application reviews remain required.
''')
    put('UPLOAD-START-HERE.md', '''# Load this first

Upload this ZIP only if your Grokbot interface supports archives and preserves file paths. Native Grok Bot import has not been verified. If it cannot read the archive, extract it and attach `GROKBOT-INSTRUCTIONS.md`, then provide the complete `skills/` directory through its supported workspace/files mechanism. A single attached text document does not install Python helpers or provider tools.

For a Grok CLI workspace whose documented skill discovery is enabled, place the seven sibling skill directories under that workspace's `.grok/skills/`. Preview existing directories first; back them up and reconcile versions rather than overwriting edits. Grok CLI discovery documentation is not proof of the desktop app's upload behavior. Reload and require the agent to report the entry skill and version it actually read.

Use this prompt:

> Load Job Applier Daily 1.4.0 and its 20-meta-skill catalog. Run setup and verify your tools. Grokbot coordinates; use Aside CLI for browser application work. Use my specified Airtable job-search tracker. Research current official roles and each full ideal-candidate persona. Research relevant initiatives at my past employers, then ask whether I personally participated, what I did, the result, and whether to include it. Draft the tailored resume in my original Word format, show proposed additions in red, and write the cover letter. Apply Lucy guidance and SlopMonster. Show me each of the first five resumes. Preserve genuine JEV decision and image holds. Submit only after I approve the exact application packet. Record real receipts in Airtable. Start with one dry-run role; do not activate a daily schedule yet.

After the dry run, set the explicit first and last run dates, local time, timezone, and daily limits in the profile. Confirm that no existing dispatcher will duplicate the run. Use only the destination's supported scheduler; there is no invented Grokbot schedule command here. Then authorize activation for the chosen dates. Default profile is disabled.

Tracker: https://airtable.com/appjHReyFuIAyEZXI/tbl450GyKwBLxGQvK/viwQZBD5gESWLqp0I?blocks=hide

The schema is intentionally unmapped until inspected in your authenticated account. Search the complete table before creating a record; the linked view may hide existing applications. An unknown write or submission must be reconciled, not retried blindly.
''')
    put('verify_bundle.py', '''#!/usr/bin/env python3
"""Verify the package file inventory and hashes, not source trust or execution."""
import hashlib,json,sys
from pathlib import Path
root=Path(sys.argv[1] if len(sys.argv)>1 else '.').resolve()
try:
    m=json.loads((root/'MANIFEST.json').read_text())
    actual={p.relative_to(root).as_posix():p for p in root.rglob('*') if p.is_file() and p.name!='MANIFEST.json' and '__pycache__' not in p.parts and p.suffix!='.pyc'}
    if any(p.is_symlink() for p in root.rglob('*')): raise ValueError('symlink in package')
    if set(actual)!=set(m['files']): raise ValueError('package inventory changed')
    for name,h in m['files'].items():
        if Path(name).is_absolute() or '..' in Path(name).parts: raise ValueError('unsafe path')
        if hashlib.sha256(actual[name].read_bytes()).hexdigest()!=h: raise ValueError('changed: '+name)
    print(json.dumps({'status':'INTEGRITY_PASS','version':m['version'],'files':len(actual),'authenticates_source':False}))
except (OSError,ValueError,KeyError) as e:
    print(json.dumps({'status':'BLOCK','error':str(e)}));sys.exit(2)
''')
    put('SOURCES.json', json.dumps({'version':VERSION,'core':'canonical Job Applier 1.2.2 portable adaptation',
        'julie':'Adapted from canonical julie-w2-applypilot 1.1.0; historical grants and account facts excluded',
        'slopmonster':'MIT license included; instructions and checker copied without historical artifacts',
        'import':'Grok CLI skill-discovery documentation consulted; native Grok Bot upload unverified',
        'files':provenance},indent=2))
    # Upload fallback: concatenate authored instructions, never credentials or script outputs.
    docs = [bundle/'UPLOAD-START-HERE.md'] + sorted((bundle/'skills').rglob('SKILL.md'))
    docs += sorted((bundle/'skills/job-applier-daily/references').glob('*.md'))
    def flattened(p):
        def root_link(match):
            label, target = match.group(1), match.group(2)
            if target.startswith(('http:', 'https:', '#', 'mailto:')):
                return match.group(0)
            path, sep, fragment = target.partition('#')
            resolved = (p.parent / path).resolve()
            rel = resolved.relative_to(bundle.resolve()).as_posix()
            return '[' + label + '](' + rel + (sep + fragment if sep else '') + ')'
        return '<!-- ' + p.relative_to(bundle).as_posix() + ' -->\n' + re.sub(r'\[([^\]]+)\]\(([^)]+)\)', root_link, p.read_text())
    put('GROKBOT-INSTRUCTIONS.md','\n\n'.join(flattened(p) for p in docs))
    forbidden = [r'/Users/rig128gb',r'jloehr2131@',r'mrodgersjs@',r'sfk_[A-Za-z0-9]{20,}',r'gh[pousr]_[A-Za-z0-9]{20,}',r'-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----']
    problems=[]
    for p in bundle.rglob('*'):
        if not p.is_file(): continue
        content=p.read_text()
        for pattern in forbidden:
            if re.search(pattern,content): problems.append(str(p.relative_to(bundle))+': '+pattern)
    if problems: raise ValueError('Privacy scan failed: '+json.dumps(problems))
    files={p.relative_to(bundle).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(bundle.rglob('*')) if p.is_file()}
    put('MANIFEST.json',json.dumps({'version':VERSION,'files':files,'scheduler_activated':False,'native_grokbot_import_verified':False},indent=2))
    archive=output/(bundle.name+'.zip')
    with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED) as z:
        for p in sorted(bundle.rglob('*')):
            if p.is_file(): z.write(p,bundle.name+'/'+p.relative_to(bundle).as_posix())
    checksum=hashlib.sha256(archive.read_bytes()).hexdigest()
    (output/'SHA256SUMS.txt').write_text(checksum+'  '+archive.name+'\n')
    print(json.dumps({'bundle':str(bundle),'archive':str(archive),'sha256':checksum,'files':len(files)+1,'privacy_scan':'PASS'},indent=2))


if __name__=='__main__':
    main()
