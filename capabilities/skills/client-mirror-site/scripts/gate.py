#!/usr/bin/env python3
from pathlib import Path
import runpy
import sys


owner = Path(__file__).resolve().parents[2] / 'jev-site-gate/scripts/gate.py'
if not owner.is_file():
    raise SystemExit('FAIL: install canonical jev-site-gate beside client-mirror-site')
sys.path.insert(0, str(owner.parent))
runpy.run_path(str(owner), run_name='__main__')
