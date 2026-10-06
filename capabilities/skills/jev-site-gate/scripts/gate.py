#!/usr/bin/env python3
"""
RIG client-mirror site gate. CODE checks first, JEV only for bounded judgment calls.
Usage: gate.py <site-slug> [--airtable-record recXXXX]

Reads   sites/<slug>/evidence/probe.json  (written by the builder from the SERVED page)
        sites/<slug>/{discover,define,gate,diverge,develop,deliver,measure}.md, demand.md, claims.md, critique.md
Writes  sites/<slug>/evidence/gate-result.json unless --dry-run emits JSON to stdout only.
If --airtable-record is given: writes the verdict into that DO · Today row. Marks Done ONLY when every criterion passes.
JEV threshold 0.85 (enforcement is ON). A JEV call error = FAIL with the error recorded, never a guessed pass.
"""
import argparse, json, os, re, sys, subprocess, urllib.request, datetime
from pathlib import Path
sys.dont_write_bytecode = True
sys.path.insert(0, os.path.dirname(__file__))
from jev import jev_noul
from evidence_contract import Evidence, VERSION, digest, finite_number, distinct_offerings

ROOT = '/Users/rig128gb/Developer/rig-client-mirror-sites'
JEV_MIN = 0.85
BANNED = ['unlock','empower','synergy','leverage','disrupt','hustle','utilize','iterate','optimize','seamless','revolutionize']
PHASES = ['discover','define','gate','diverge','develop','deliver','measure']

def rd(p):
    try: return Path(p).read_text(encoding='utf-8', errors='replace')
    except Exception: return ''

def main():
    parser = argparse.ArgumentParser(description='Verify signed website evidence; no receipt means FAIL.')
    parser.add_argument('slug', nargs='?')
    parser.add_argument('--portfolio', nargs='+')
    parser.add_argument('--root', default=ROOT)
    parser.add_argument('--verifier-key')
    parser.add_argument('--airtable-record')
    parser.add_argument('--dry-run', action='store_true', help='Emit JSON to stdout without workspace or Airtable writes; existing read/JEV checks still run.')
    args = parser.parse_args()
    if args.dry_run and args.airtable_record:
        parser.error('dry-run forbids Airtable writes')
    if args.portfolio:
        if args.slug or args.airtable_record:
            parser.error('portfolio cannot use a single slug or Airtable writes')
        try:
            portfolio(args.root, args.portfolio, args.verifier_key, dry_run=args.dry_run)
        except Exception as error:
            if args.dry_run:
                print(json.dumps({'portfolio': args.portfolio, 'verdict': 'FAIL', 'dry_run': True, 'detail': str(error)}))
            else:
                print(f'portfolio: FAIL {error}')
            sys.exit(1)
        sys.exit(0)
    if not args.slug:
        parser.error('slug or --portfolio required')
    slug, rec = args.slug, args.airtable_record
    if not re.fullmatch(r'[a-z0-9][a-z0-9-]*', slug):
        parser.error('invalid offering slug')
    root = Path(args.root).resolve()
    if not (root / 'sites' / slug).resolve().is_relative_to(root / 'sites'):
        parser.error('site outside root')
    S = str(root / 'sites' / slug)
    if not args.dry_run:
        Path(S, 'evidence').mkdir(parents=True, exist_ok=True)
        Path(S, 'evidence/gate-result.json').write_text(json.dumps({'site': slug, 'verdict': 'FAIL', 'status': 'RUNNING'}))
    evidence = None
    try:
        evidence = Evidence(root, slug, args.verifier_key)
        evidence.offering()
        probe = evidence.probe
    except Exception as error:
        out = {'site': slug, 'criteria_version': VERSION, 'verdict': 'FAIL', 'passed': 0, 'total': 1,
               'at': datetime.datetime.now(datetime.timezone.utc).isoformat(), 'vercel_url': '',
               'results': [{'id': 'C00', 'pass': False, 'method': 'CODE', 'detail': str(error)}]}
        if args.dry_run:
            out['dry_run'] = True
            print(json.dumps(out, indent=1))
        else:
            Path(S, 'evidence').mkdir(parents=True, exist_ok=True)
            Path(S, 'evidence/gate-result.json').write_text(json.dumps(out, indent=1))
            print(f'{slug}: FAIL 0/1 C00 {error}')
        if rec:
            airtable(rec, out, S)
        sys.exit(1)
    pin_slug = probe.get('pinterest_board', slug)
    text = probe.get('text', '')
    demand, define, discover, claims = rd(f'{S}/demand.md'), rd(f'{S}/define.md'), rd(f'{S}/discover.md'), rd(f'{S}/claims.md')
    hero = probe.get('hero', {}); cta = probe.get('cta', {}); res = []

    def add(cid, ok, method, detail, jev=None):
        res.append({'id': cid, 'pass': bool(ok), 'method': method, 'detail': detail, **({'jev': jev} if jev else {})})

    def judge(cid, q, state):
        try: s, m, raw = jev_noul(q, state)
        except Exception as error:
            add(cid, False, 'JEV', f'JEV call error: {error}'); return
        if not finite_number(s) or not 0 <= s <= 1:
            add(cid, False, 'JEV', 'JEV call error or invalid numeric answer'); return
        add(cid, s >= JEV_MIN, 'JEV', f'score {s} (min {JEV_MIN})', {'model': m, 'score': s, 'question': q})

    def check(cid, function):
        try: add(cid, function(), 'CODE', 'signed artifact evidence verified')
        except Exception as error: add(cid, False, 'CODE', str(error))

    add('C00', True, 'CODE', 'trusted signature, build, source chain and capture session verified')
    pins = os.listdir(f'{root}/_inputs/pinterest/{pin_slug}') if os.path.isdir(f'{root}/_inputs/pinterest/{pin_slug}') else []
    hs = os.path.basename(hero.get('pinterest_source', '') or '')
    add('C01', hs and hs in pins, 'CODE', f'hero.pinterest_source={hs!r} in board folder ({len(pins)} files)')
    judge('C02', 'Does the hero headline or subhead explicitly name the target buyer (their role or business type)?',
          json.dumps({'headline': hero.get('headline',''), 'subhead': hero.get('subhead',''), 'target_buyer_from_brief': probe.get('buyer','')}))
    judge('C03', 'Does the hero headline or subhead express one of the buyer pains listed in the demand evidence?',
          json.dumps({'headline': hero.get('headline',''), 'subhead': hero.get('subhead',''), 'demand_evidence_pains': demand[:3000]}))
    cards = probe.get('pain_cards', [])
    ids_ok = [c for c in cards if c.get('record_id') and c['record_id'] in demand]
    add('C04', len(cards) >= 3 and len(ids_ok) >= 3, 'CODE', f'{len(cards)} pain cards, {len(ids_ok)} with record ids found in demand.md')
    urls = set(re.findall(r'https?://[^\s)>\]]+', discover))
    reference_urls = {reference['url'] for reference in evidence.manifest['references']}
    add('C05', reference_urls <= urls, 'CODE', 'all captured mirror/award references recorded in discover.md')
    check('C06', lambda: evidence.motion('scroll'))
    check('C07', lambda: evidence.motion('three_d'))
    check('C08', evidence.reduced_motion)
    wid = probe.get('wow_id', '')
    add('C09', bool(wid) and probe.get('wow_present') is True and wid in define, 'CODE', f'wow_id={wid!r} present={probe.get("wow_present")} named in define.md={wid in define}')
    try: lh = evidence.lighthouse()
    except Exception as error:
        lh = {}; add('C10-report', False, 'CODE', str(error))
    add('C10', (lh.get('performance') or 0) >= 80, 'CODE', f'lighthouse performance {lh.get("performance")}')
    add('C11', (lh.get('accessibility') or 0) >= 90, 'CODE', f'lighthouse accessibility {lh.get("accessibility")}')
    add('C12', 0 < (probe.get('scroll_w_390') or 99999) <= 390, 'CODE', f'scrollWidth@390={probe.get("scroll_w_390")}')
    add('C13', 0 < (probe.get('scroll_w_1440') or 99999) <= 1440, 'CODE', f'scrollWidth@1440={probe.get("scroll_w_1440")}')
    ct = (cta.get('text') or '').strip()
    add('C14', bool(ct) and text.count(ct) >= 2, 'CODE', f'CTA {ct!r} appears {text.count(ct) if ct else 0}x')
    lk = probe.get('links', {})
    add('C15', lk.get('total', 0) > 0 and lk.get('bad', 1) == 0 and lk.get('empty_href', 1) == 0, 'CODE', f'links {lk}')
    judge('C16', 'Is this page text free of customer testimonials, named client quotes, and customer logo claims?', text[:4000])
    nums = set(re.findall(r'\$?\d[\d,.]*\s?(?:%|x|k|K|M|B|hrs?|hours|minutes|days)?', text))
    nums = {n.strip() for n in nums if re.search(r'\d{2,}|%|\$|x$', n.strip())}
    missing = sorted(n for n in nums if n not in claims)
    add('C17', not missing, 'CODE', f'{len(nums)} numeric tokens, not in claims.md: {missing[:12]}')
    add('C18', not re.search(r'lorem|ipsum|\bTODO\b|placeholder', text, re.I), 'CODE', 'no placeholder strings')
    add('C19', probe.get('broken_images', 1) == 0, 'CODE', f'broken_images={probe.get("broken_images")}')
    add('C20', 0 < len(probe.get('fonts', [])) <= 2, 'CODE', f'fonts={probe.get("fonts")}')
    add('C21', (hero.get('height_ratio') or 0) >= 0.5, 'CODE', f'hero height ratio {hero.get("height_ratio")}')
    check('C22', evidence.cta)
    vurl = probe.get('vercel_url', ''); code = None; final_url = None
    try:
        if vurl:
            response = urllib.request.urlopen(urllib.request.Request(vurl, headers={'User-Agent': 'rig-gate'}), timeout=20)
            code, final_url = response.status, response.geturl()
            response.close()
    except Exception as e: code = str(e)[:80]
    add('C23', code == 200 and final_url == vurl and vurl in rd(f'{S}/deliver.md'), 'CODE', f'{vurl} -> {code} final={final_url}')
    check('C24', evidence.phases)
    bad = [w for w in BANNED if re.search(r'\b' + w, text, re.I)]
    add('C25', not bad, 'CODE', f'banned words found: {bad}')
    check('C26', evidence.screenshots)
    check('C27', evidence.critique)
    check('C28', evidence.offering)
    check('C29', evidence.unchanged)

    passed = sum(r['pass'] for r in res); allp = passed == len(res)
    out = {'site': slug, 'criteria_version': VERSION, 'at': datetime.datetime.now(datetime.timezone.utc).isoformat(), 'passed': passed, 'total': len(res),
           'build_sha256': evidence.receipt['build_sha256'], 'receipt_sha256': evidence.receipt_sha256,
           'verifier_key_sha256': evidence.key_sha256, 'gate_sha256': digest(__file__),
           'evidence_contract_sha256': digest(Path(__file__).with_name('evidence_contract.py')),
           'verdict': 'PASS' if allp else 'FAIL', 'vercel_url': vurl, 'results': res}
    if args.dry_run:
        out['dry_run'] = True
        print(json.dumps(out, indent=1))
    else:
        Path(S, 'evidence/gate-result.json').write_text(json.dumps(out, indent=1))
        print(f'{slug}: {out["verdict"]} {passed}/{len(res)}')
        for r in res:
            if not r['pass']: print('  FAIL', r['id'], r['method'], r['detail'][:160])
    if rec: airtable(rec, out, S)
    sys.exit(0 if allp else 1)

def portfolio(root, slugs, verifier_key, dry_run=False):
    if not verifier_key or len(slugs) < 10 or len(set(slugs)) != len(slugs):
        raise ValueError('portfolio needs trusted verifier key and at least ten distinct offering slugs')
    accepted = []
    for slug in slugs:
        command = [sys.executable, __file__, slug, '--root', str(root), '--verifier-key', str(verifier_key)]
        if dry_run:
            command.append('--dry-run')
        result = subprocess.run(command,
                                capture_output=True, text=True, timeout=240)
        if result.returncode != 0:
            raise ValueError(f'{slug}: fresh gate failed (exit {result.returncode})')
        accepted.append(Evidence(root, slug, verifier_key))
    count = distinct_offerings(accepted)
    if dry_run:
        print(json.dumps({'portfolio': slugs, 'verdict': 'PASS', 'dry_run': True, 'distinct_offerings': count}))
    else:
        print(f'portfolio: PASS {count} distinct client-branded offerings')
    return count

def airtable(rec, out, S):
    env = dict(l.strip().split('=', 1) for l in open('/Users/rig128gb/.rig/secrets/airtable-command-center.env') if '=' in l and not l.startswith('#'))
    tok, base = env['AIRTABLE_CC_PAT'].strip('"\''), env['AIRTABLE_CC_BASE'].strip('"\'')
    jevs = [f"{r['id']}={r['jev']['score']}" for r in out['results'] if r.get('jev')]
    fails = [f"{r['id']}" for r in out['results'] if not r['pass']]
    models = sorted({r['jev']['model'] for r in out['results'] if r.get('jev') and r['jev'].get('model')})
    ev = (f"GATE {out['verdict']} {out['passed']}/{out['total']} at {out['at']} | JEV {', '.join(jevs)} ({', '.join(models)}) | "
          f"fails: {fails or 'none'} | preview {out['vercel_url']} | {S}/evidence/gate-result.json")
    fields = {'Evidence / notes': ev, 'Updated': datetime.date.today().isoformat()}
    if out['verdict'] == 'PASS': fields.update({'Status': 'Done', 'Done': True})
    else: fields.update({'Status': 'In progress', 'Done': False})
    req = urllib.request.Request(f'https://api.airtable.com/v0/{base}/tblA71jPS8Cle7DMO/{rec}', method='PATCH',
        data=json.dumps({'fields': fields, 'typecast': True}).encode(), headers={'Authorization': f'Bearer {tok}', 'Content-Type': 'application/json'})
    r = json.load(urllib.request.urlopen(req, timeout=20))
    print('airtable', rec, r['fields'].get('Status'), 'Done=', r['fields'].get('Done'))

if __name__ == '__main__':
    main()
