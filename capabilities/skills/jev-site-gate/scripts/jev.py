#!/usr/bin/env python3
"""Thin JEV wrapper. jev_noul(question, state) -> (score, model, raw). Never guesses: on error returns (None, None, err)."""
import json, os, subprocess
def _env():
    e={k:v for k,v in os.environ.items() if k not in ('PYTHONHOME','PYTHONPATH')}
    e['PATH']='/usr/bin:/bin:/usr/sbin:/sbin:'+os.path.expanduser('~/.rig/bin')+':'+e.get('PATH','')
    return e
def jev_noul(q, state):
    try:
        r=subprocess.run([os.path.expanduser('~/.rig/bin/aside-jev'),'noul',q,'--state',state],capture_output=True,text=True,env=_env(),timeout=60)
    except (OSError, subprocess.TimeoutExpired) as error:
        return None, None, type(error).__name__
    if r.returncode != 0:
        return None, None, f'JEV exit {r.returncode}'
    try:
        v=json.loads([l for l in r.stdout.splitlines() if l.strip()][-1]); return v['answer']['noul'], v.get('model'), v
    except Exception as ex: return None, None, (r.stderr or str(ex))[-300:]
