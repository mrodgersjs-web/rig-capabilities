#!/usr/bin/env python3
"""RIG KPI collector — ~/.rig/bin/rig-kpi (Mike 2026-10-23: "a kpi and dashboard with all our daily, weekly, and monthly kpis ... use this to run rig").

Usage:
  rig-kpi collect [--registry FILE] [--out DIR] [--no-mirror]
  rig-kpi <helper> ARGS...        # deterministic value readers used by registry compute strings

collect: runs every compute in KPI-REGISTRY.yaml, writes kpi-now.json (value, target, status,
source, measured_at, stale) to the kpi control-plane dir and mirrors it into each live Aside
component rig/ folder (same convention as grokbot-util.json), and appends history to kpi.db.

Rules (from the brief): a failing/absent source reports "source down", NEVER 0. Weekly/monthly
rows are rollups of daily history computed here (rollup:sum:<id>:Nd / rollup:avg:<id>:Nd).
Exit: 0 collected (even with source-down rows), 2 bad input.
"""
import csv
import datetime as dt
import json
import os
import re
import shlex
import sqlite3
import subprocess
import sys
from pathlib import Path

KPI_DIR = Path('/Users/rig128gb/.rig/live/control-plane/kpi')
DEFAULT_REGISTRY = KPI_DIR / 'KPI-REGISTRY.yaml'
COMPONENT_ROOT = Path(os.path.expanduser('~/Library/Application Support/Aside/AsideAgentManager'))
SOURCE_DOWN = 'source down'
HELPER_TIMEOUT = 30  # seconds per compute


def out(value):
    print(value)
    return 0


def fail(msg):
    print(msg, file=sys.stderr)
    return 1


def as_num(s):
    try:
        return float(str(s).strip().replace(',', ''))
    except (TypeError, ValueError):
        return None


def fmt(v):
    if isinstance(v, float) and v.is_integer():
        return str(int(v))
    return str(v)


# ---------------- helpers (each prints exactly one value, exit 1 = source down) ----------------

def _today_rows(path):
    today = dt.date.today().isoformat()
    rows = list(csv.DictReader(open(path, newline='', encoding='utf-8', errors='replace')))
    return [r for r in rows if str(r.get('date', '')).strip().startswith(today)]


def h_read_csv(args):
    # SUM of one column over today's rows: the daily CSVs append one row per run/lane
    # (later rows carry 0 for "not measured by this lane", so last-row-wins loses data).
    path, column = Path(args[0]), args[1]
    vals = [v for v in (as_num(r.get(column)) for r in _today_rows(path)) if v is not None]
    if not vals:
        return fail(f'no numeric {column} rows for today in {path}')
    return out(fmt(sum(vals)))


def h_read_csv_max(args):
    # MAX over today's rows for cumulative gauges (followers, pipeline_usd, leads_verified).
    path, column = Path(args[0]), args[1]
    vals = [v for v in (as_num(r.get(column)) for r in _today_rows(path)) if v is not None]
    if not vals:
        return fail(f'no numeric {column} rows for today in {path}')
    return out(fmt(max(vals)))


def h_read_csv_sum(args):
    # SUM of several columns over today's rows.
    path, columns = Path(args[0]), args[1:]
    vals = []
    for r in _today_rows(path):
        vals.extend(v for v in (as_num(r.get(c)) for c in columns) if v is not None)
    if not vals:
        return fail(f'no numeric rows among {columns} for today in {path}')
    return out(fmt(sum(vals)))


def h_count_csv_today(args):
    path, datecol, statuscol, statusval = Path(args[0]), args[1], args[2], args[3]
    today = dt.date.today().isoformat()
    rows = list(csv.DictReader(open(path, newline='', encoding='utf-8', errors='replace')))
    n = sum(1 for r in rows if str(r.get(datecol, '')).startswith(today) and str(r.get(statuscol, '')) == statusval)
    return out(str(n))


def h_read_json_path(args):
    path, dotted = Path(args[0]), args[1]
    obj = json.load(open(path))
    for key in dotted.split('.'):
        obj = obj[key]
    if isinstance(obj, bool) or obj is None:
        return fail(f'{dotted} is not numeric')
    v = as_num(obj)
    if v is None:
        return fail(f'{dotted} not numeric: {obj!r}')
    return out(fmt(v))


def h_json_count(args):
    path, field, val = Path(args[0]), args[1], args[2]
    obj = json.load(open(path))
    lst_key, sub = field.split('.', 1) if '.' in field else (field, None)
    items = obj.get(lst_key) if isinstance(obj, dict) else obj
    if not isinstance(items, list):
        return fail(f'{lst_key} is not a list')
    if sub is None:
        n = sum(1 for it in items if str(it) == val)
    else:
        n = sum(1 for it in items if isinstance(it, dict) and str(it.get(sub)) == val)
    return out(str(n))


def h_grep_latest(args):
    directory, pattern = Path(args[0]), args[1]
    filerx = args[2] if len(args) > 2 else None
    files = [p for p in directory.iterdir() if p.is_file() and not p.name.endswith(('.bak', '.tmp'))
             and (not filerx or re.search(filerx, p.name))]
    if not files:
        return fail(f'no files matching {filerx or "*"} in {directory}')
    newest = max(files, key=lambda p: p.stat().st_mtime)
    m = re.search(pattern, newest.read_text(encoding='utf-8', errors='replace'))
    return out(m.group(1)) if m else fail(f'pattern {pattern!r} not found in {newest.name}')


def h_count_lines_today(args):
    path = Path(args[0])
    today = dt.date.today().isoformat()
    n = 0
    for line in open(path, encoding='utf-8', errors='replace'):
        line = line.strip()
        if not line:
            continue
        try:
            rec = json.loads(line)
        except ValueError:
            continue
        ts = str(rec.get('ts') or rec.get('at') or rec.get('occurred_at') or '')
        if ts.startswith(today):
            n += 1
    return out(str(n))


def h_events_today(args):
    return h_events_count_days([args[0], args[1], args[2], '1'])


def h_events_count_days(args):
    path, field, val, days = Path(args[0]), args[1], args[2], int(args[3])
    cutoff = dt.datetime.now().astimezone() - dt.timedelta(days=days)
    n = 0
    for line in open(path, encoding='utf-8', errors='replace'):
        line = line.strip()
        if not line:
            continue
        try:
            rec = json.loads(line)
        except ValueError:
            continue
        if str(rec.get(field)) != val:
            continue
        ts = str(rec.get('ts') or rec.get('at') or rec.get('occurred_at') or '')
        try:
            when = dt.datetime.fromisoformat(ts.replace('Z', '+00:00'))
        except ValueError:
            continue
        if when.tzinfo is None:
            when = when.astimezone()
        if when >= cutoff:
            n += 1
    return out(str(n))


def h_file_age_days(args):
    path = Path(args[0])
    if not path.exists():
        return fail(f'{path} missing')
    age = (dt.datetime.now().timestamp() - path.stat().st_mtime) / 86400.0
    return out(fmt(round(age, 2)))


def h_judge_pass(args):
    n = int(args[0])
    path = Path('/Users/rig128gb/rig-grokbot-dispatcher/logs/dispatcher.jsonl')
    verdicts = []
    for line in open(path, encoding='utf-8', errors='replace'):
        line = line.strip()
        if not line:
            continue
        try:
            rec = json.loads(line)
        except ValueError:
            continue
        if rec.get('event') == 'judge' and 'gatePass' in rec:
            verdicts.append(bool(rec['gatePass']))
    if not verdicts:
        return fail('no judge events in dispatcher.jsonl')
    tail = verdicts[-n:]
    return out(fmt(round(100.0 * sum(tail) / len(tail), 1)))


def h_fleet_hosts_up(args):
    path = KPI_DIR / 'fleet-util.jsonl'
    last = {}
    if path.exists():
        cutoff = dt.datetime.now().astimezone() - dt.timedelta(days=1)
        for line in open(path, encoding='utf-8', errors='replace'):
            line = line.strip()
            if not line:
                continue
            try:
                rec = json.loads(line)
            except ValueError:
                continue
            try:
                when = dt.datetime.fromisoformat(str(rec['ts']).replace('Z', '+00:00'))
            except (KeyError, ValueError):
                continue
            if when.tzinfo is None:
                when = when.astimezone()
            if when >= cutoff:
                last[rec.get('host')] = rec
    if last:
        return out(str(sum(1 for r in last.values() if str(r.get('up', '')).startswith('up'))))
    # fleet-util.jsonl is stale (probe not running) -> live reachability probe of the roster
    hosts = ['localhost', 'rig256gb', 'rig96gb', 'rig48gb', 'rig36gb', 'rig28gb', 'blackwell']
    r = subprocess.run(
        ['bash', '-c', 'for h in ' + ' '.join(hosts) +
         '; do (ssh -o BatchMode=yes -o ConnectTimeout=4 "$h" true 2>/dev/null && echo "$h up") & done; wait'],
        capture_output=True, text=True, timeout=40)
    n = sum(1 for ln in r.stdout.splitlines() if ln.endswith(' up'))
    return out(str(n)) if n else fail('fleet-util.jsonl stale and no roster host reachable')


def h_blackwell_lanes(args):
    cmd = ("ssh -o BatchMode=yes -o ConnectTimeout=5 blackwell "
           "'for p in 8201 8111; do curl -s -m3 -o /dev/null http://127.0.0.1:$p/health && echo up; done; true'")
    try:
        r = subprocess.run(['bash', '-c', cmd], capture_output=True, text=True, timeout=20)
    except subprocess.TimeoutExpired:
        return fail('blackwell ssh timed out')
    if r.returncode != 0:
        return fail(f'blackwell ssh failed: {r.stderr.strip()[:120]}')
    return out(str(sum(1 for ln in r.stdout.splitlines() if ln.strip() == 'up')))


def h_disk_free_gb(args):
    mount = args[0]
    r = subprocess.run(['df', '-Pk', mount], capture_output=True, text=True)
    if r.returncode != 0:
        return fail(f'df {mount} failed')
    avail_kb = int(r.stdout.splitlines()[1].split()[3])
    return out(fmt(round(avail_kb / 1048576.0, 1)))


def h_http_any_up(args):
    n = 0
    for url in args:
        r = subprocess.run(['curl', '-s', '-m', '3', '-o', '/dev/null', '-w', '%{http_code}', url],
                           capture_output=True, text=True)
        if r.returncode == 0 and r.stdout.strip()[:1] in ('2', '3'):
            n += 1
    return out(str(n))


def h_oxygen_stage(args):
    key = args[0]
    r = subprocess.run(['bash', '-c', 'oxygen dashboards summary'], capture_output=True, text=True, timeout=60)
    if r.returncode != 0:
        return fail(f'oxygen dashboards summary failed: {r.stderr.strip()[:120]}')
    try:
        data = json.loads(r.stdout)
    except ValueError:
        return fail('oxygen summary not JSON')
    for st in data.get('summary', {}).get('stages', []):
        if st.get('key') == key:
            v = as_num(st.get('count'))
            return out(fmt(v)) if v is not None else fail(f'stage {key} not numeric')
    return fail(f'stage {key} not in oxygen summary')


def h_oxygen_credits(args):
    r = subprocess.run(['bash', '-c', 'oxygen budget list'], capture_output=True, text=True, timeout=60)
    if r.returncode != 0:
        return fail(f'oxygen budget list failed: {r.stderr.strip()[:120]}')
    try:
        data = json.loads(r.stdout)
    except ValueError:
        return fail(f'oxygen budget list not JSON: {r.stdout[:120]!r}')
    for pol in data.get('policies', []):
        v = as_num(pol.get('remaining_credits'))
        if v is not None:
            return out(fmt(v))
    return fail('no policy with numeric remaining_credits')


def h_grokbot_kpi(args):
    bot, kpi = args[0], args[1]
    path = Path('/Users/rig128gb/.rig/live/control-plane/agent-company/kpi/grokbots.jsonl')
    if not path.exists():
        return fail('grokbots.jsonl missing')
    for line in reversed(open(path, encoding='utf-8', errors='replace').read().splitlines()):
        line = line.strip()
        if not line:
            continue
        try:
            rec = json.loads(line)
        except ValueError:
            continue
        if rec.get('bot') != bot:
            continue
        for k in rec.get('kpis', []):
            if k.get('name') == kpi:
                v = as_num(k.get('actual', k.get('value', k.get('actual_value'))))
                return out(fmt(v)) if v is not None else fail(f'{bot}/{kpi} has no numeric actual: {k}')
        return fail(f'{bot} row has no kpi {kpi}')
    return fail(f'no grokbots.jsonl rows for {bot}')


HELPERS = {
    'read-csv': h_read_csv,
    'read-csv-max': h_read_csv_max,
    'read-csv-sum': h_read_csv_sum,
    'count-csv-today': h_count_csv_today,
    'read-json-path': h_read_json_path,
    'json-count': h_json_count,
    'grep-latest': h_grep_latest,
    'count-lines-today': h_count_lines_today,
    'events-today': h_events_today,
    'events-count-days': h_events_count_days,
    'file-age-days': h_file_age_days,
    'judge-pass': h_judge_pass,
    'fleet-hosts-up': h_fleet_hosts_up,
    'blackwell-lanes': h_blackwell_lanes,
    'disk-free-gb': h_disk_free_gb,
    'http-any-up': h_http_any_up,
    'oxygen-stage': h_oxygen_stage,
    'oxygen-credits': h_oxygen_credits,
    'grokbot-kpi': h_grokbot_kpi,
}


# ---------------- collect ----------------

def load_registry(path):
    import yaml
    reg = yaml.safe_load(open(path))
    return reg.get('kpis', reg) if isinstance(reg, dict) else reg


def parse_cond(cond, label):
    m = re.match(rf'{label}\s*(>=|<=|>|<|=)\s*(\d+(?:\.\d+)?)', cond.strip())
    if not m:
        m = re.match(rf'{label}\s+(\d+(?:\.\d+)?)', cond.strip())
        if not m:
            return None
        op, num = '=', m.group(1)
    else:
        op, num = m.group(1), m.group(2)
    return op, float(num)


def parse_green(cond):
    return parse_cond(cond, 'green')


def classify(value, target, rag):
    if value is None:
        return SOURCE_DOWN
    segs = [s.strip() for s in str(rag or '').split(';') if s.strip()]

    def match(label):
        part = next((s for s in segs if s.startswith(label)), '')
        p = parse_cond(part, label) if part else None
        if not p:
            return None
        op, num = p
        return {'>=': value >= num, '<=': value <= num, '>': value > num, '<': value < num, '=': value == num}[op]

    if match('red') is True:
        return 'red'
    if match('green') is True:
        return 'green'
    if match('amber') is True:
        return 'amber'
    if isinstance(target, (int, float)):
        return 'green' if value >= target else ('amber' if value >= target / 2 else 'red')
    return 'amber'


def run_compute(spec, registry_path):
    spec = spec.strip()
    m = re.match(r'rollup:(sum|avg):([a-z0-9_]+):(\d+)d$', spec)
    if m:
        return rollup(m.group(1), m.group(2), int(m.group(3)))
    if spec.startswith('rig-kpi '):
        abs_self = f'{sys.executable} {os.path.abspath(__file__)}'
        spec = re.sub(r'(^|(?<=[|&; ]))rig-kpi ', lambda m: m.group(1) + abs_self + ' ', spec)
    cmd = ['bash', '-c', spec]
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=HELPER_TIMEOUT)
    except subprocess.TimeoutExpired:
        return None
    if r.returncode != 0:
        return None
    return as_num(r.stdout.strip())


def rollup(op, kpi_id, days):
    db = sqlite3.connect(KPI_DIR / 'kpi.db')
    cutoff = (dt.datetime.now() - dt.timedelta(days=days)).isoformat(timespec='seconds')
    rows = db.execute(
        'SELECT substr(ts,1,10) d, value FROM history WHERE kpi_id=? AND ts>=? AND value IS NOT NULL ORDER BY ts',
        (kpi_id, cutoff)).fetchall()
    db.close()
    if not rows:
        return None
    per_day = {}
    for d, v in rows:  # last value per observed day
        per_day[d] = v
    vals = list(per_day.values())
    return round(sum(vals) if op == 'sum' else sum(vals) / len(vals), 2)


def open_db():
    db = sqlite3.connect(KPI_DIR / 'kpi.db')
    db.execute('CREATE TABLE IF NOT EXISTS history (id INTEGER PRIMARY KEY, kpi_id TEXT, ts TEXT, value REAL, status TEXT, source TEXT)')
    db.execute('CREATE INDEX IF NOT EXISTS idx_history ON history (kpi_id, ts)')
    return db


def sparkline_json(days=30):
    """Last value per day per kpi for the strip's sparklines."""
    db = open_db()
    cutoff = (dt.datetime.now() - dt.timedelta(days=days)).isoformat(timespec='seconds')
    series = {}
    for kpi_id, ts, value in db.execute(
            'SELECT kpi_id, ts, value FROM history WHERE ts>=? AND value IS NOT NULL ORDER BY ts', (cutoff,)):
        series.setdefault(kpi_id, {})[ts[:10]] = value
    db.close()
    return json.dumps({'generated_at': dt.datetime.now().astimezone().isoformat(timespec='seconds'),
                       'days': days,
                       'series': {k: sorted(v.items()) for k, v in sorted(series.items())}}, indent=1)


def notes_today():
    return KPI_DIR / f"notes-{dt.date.today().isoformat()}.jsonl"


def h_note(args):
    """Append one why/next-move line for a red/amber KPI: rig-kpi note KPI_ID WHY NEXT_MOVE [CARD_ID]"""
    if len(args) < 3:
        return fail('usage: rig-kpi note KPI_ID WHY NEXT_MOVE [CARD_ID]')
    rec = {'ts': dt.datetime.now().astimezone().isoformat(timespec='seconds'),
           'kpi_id': args[0], 'why': args[1], 'next_move': args[2], 'card_id_if_any': args[3] if len(args) > 3 else None}
    with open(notes_today(), 'a', encoding='utf-8') as fh:
        fh.write(json.dumps(rec) + '\n')
    return out(json.dumps(rec))


def mirror(src_path, text):
    # mirrors each file into the live component rig/ under ITS OWN name (kpi-now.json etc.)
    targets = [Path(src_path)]
    if COMPONENT_ROOT.exists():
        vdirs = [d for d in COMPONENT_ROOT.iterdir() if (d / 'manifest.json').exists() and (d / 'rig').is_dir()]
        if vdirs:
            rig = max(vdirs, key=lambda d: d.name) / 'rig'  # live (newest) version only; old dirs are read-only
            targets.append(rig / Path(src_path).name)
    for t in targets:
        try:
            t.parent.mkdir(parents=True, exist_ok=True)
            t.write_text(text, encoding='utf-8')
        except OSError as e:
            print(f'WARN: mirror {t} failed: {e}', file=sys.stderr)


def source_mtime(spec, registry_path):
    """Best-effort freshness of the value: mtime of the first existing file named in compute."""
    roll = re.match(r'rollup:(?:sum|avg):([a-z0-9_]+):(\d+)d$', spec.strip())
    if roll:
        db = sqlite3.connect(KPI_DIR / 'kpi.db')
        row = db.execute('SELECT max(ts) FROM history WHERE kpi_id=?', (roll.group(1),)).fetchone()
        db.close()
        if row and row[0]:
            return dt.datetime.fromisoformat(row[0]).timestamp()
        return None
    for tok in spec.replace("'", ' ').replace('"', ' ').split():
        if tok.startswith('/') and os.path.isfile(tok):
            return os.path.getmtime(tok)
        if tok.startswith('/') and os.path.isdir(tok):
            files = [p for p in Path(tok).iterdir() if p.is_file()]
            if files:
                return max(p.stat().st_mtime for p in files)
    return None


def collect(registry_path, out_dir, do_mirror):
    rows = load_registry(registry_path)
    now = dt.datetime.now().astimezone()
    now_iso = now.isoformat(timespec='seconds')
    cadence_seconds = {'daily': 86400, 'weekly': 604800, 'monthly': 2592000}
    db = open_db()
    board = []
    for row in rows:
        value = run_compute(str(row['compute']), registry_path)
        status = classify(value, row.get('target') if isinstance(row.get('target'), (int, float)) else None, row.get('rag', ''))
        mtime = source_mtime(str(row['compute']), registry_path)
        measured_at = dt.datetime.fromtimestamp(mtime).astimezone().isoformat(timespec='seconds') if mtime else now_iso
        stale = (now.timestamp() - (mtime or now.timestamp())) > 2 * cadence_seconds.get(str(row.get('cadence')), 86400)
        if value is not None:
            db.execute('INSERT INTO history (kpi_id, ts, value, status, source) VALUES (?,?,?,?,?)',
                       (row['id'], now_iso, value, status, str(row['compute'])))
            db.commit()
        else:
            status = SOURCE_DOWN
        board.append({
            'id': row['id'], 'area': row.get('area'), 'name': row.get('name'),
            'cadence': row.get('cadence'), 'unit': row.get('unit'), 'owner_lane': row.get('owner_lane'),
            'target': row.get('target'), 'target_source': row.get('target_source'),
            'value': value if value is not None else SOURCE_DOWN,
            'status': status, 'source': str(row['compute']),
            'measured_at': measured_at, 'stale': stale,
            'stale_after_seconds': 2 * cadence_seconds.get(str(row.get('cadence')), 86400),
        })
    db.commit()
    db.close()
    payload = {'generated_at': now_iso, 'registry': str(registry_path), 'board': board}
    text = json.dumps(payload, indent=1)
    out_path = Path(out_dir) / 'kpi-now.json'
    out_path.write_text(text, encoding='utf-8')
    (Path(out_dir) / 'kpi-history.json').write_text(sparkline_json(), encoding='utf-8')
    if do_mirror:
        mirror(out_path, text)
        mirror(Path(out_dir) / 'kpi-history.json', (Path(out_dir) / 'kpi-history.json').read_text(encoding='utf-8'))
        nt = notes_today()
        if nt.exists():
            mirror(Path(out_dir) / 'kpi-notes.jsonl', nt.read_text(encoding='utf-8'))
    down = sum(1 for b in board if b['status'] == SOURCE_DOWN)
    print(f'collected {len(board)} KPIs at {now_iso}: {len(board)-down} values, {down} source-down -> {out_path}')
    return 0


def main(argv):
    if not argv:
        return fail(__doc__)
    cmd, args = argv[0], argv[1:]
    if cmd == 'collect':
        registry, out_dir, do_mirror = DEFAULT_REGISTRY, KPI_DIR, True
        while args:
            a = args.pop(0)
            if a == '--registry':
                registry = Path(args.pop(0))
            elif a == '--out':
                out_dir = Path(args.pop(0))
            elif a == '--no-mirror':
                do_mirror = False
            else:
                return fail(f'bad collect arg {a}')
        return collect(registry, out_dir, do_mirror)
    if cmd == 'note':
        return h_note(args)
    if cmd in HELPERS:
        try:
            return HELPERS[cmd](args)
        except (OSError, ValueError, KeyError, IndexError, json.JSONDecodeError) as e:
            return fail(f'{cmd} source down: {e}')
    return fail(f'unknown command {cmd}')


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
