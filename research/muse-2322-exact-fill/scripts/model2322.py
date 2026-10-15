#!/usr/bin/env python3
"""Shared exact fill model for muse-2322-exact-fill (Track 3G).

Loads #2322's own package (research/t74-joint-owner-hillclimb) read-only and
reuses its literal checker: verify.actual_windows (independent source-event
chronology) and verify.owners_check (window/port/family/capacity/prefix/
profile).  Owner rows are dicts with the 11 fields of
data/OWNERS.json.gz.  Windows are contiguous time intervals under #2322's
call order (checked in analyze.py).
"""
import gzip, importlib.util, json
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
PKG = ROOT / 'research/t74-joint-owner-hillclimb'
OUT = ROOT / 'research/muse-2322-exact-fill'
WIDTHS = (4, 5, 7, 8, 9)
CAPS = (8, 16, 32, 48)
BINS_BY_CAP = {8: 49728, 16: 33152, 32: 33152, 48: 33152}
PER_CALL = {4: 33, 5: 9, 7: 38, 8: 114, 9: 240}
ITEMS = {w: PER_CALL[w] * 666 for w in WIDTHS}
PAID = {1: 2335, 2: 512, 3: 426, 4: 120, 5: 38, 8: 8}  # per call, both providers

def rd(p):
    b = Path(p).read_bytes()
    return json.loads(gzip.decompress(b) if str(p).endswith('.gz') else b)

def load_pkg_verify():
    sp = importlib.util.spec_from_file_location('pkg2322_verify', PKG / 'verify.py')
    mod = importlib.util.module_from_spec(sp)
    sp.loader.exec_module(mod)
    return mod

def load_all():
    plan = rd(PKG / 'data/PLAN.json')
    contract = rd(PKG / 'BASELINE-CONTRACT.json.gz')
    rows = rd(PKG / 'data/OWNERS.json.gz')
    claim = rd(PKG / 'CLAIM.json')
    cons = rd(PKG / 'data/CONSTRUCTION.json')
    verify = load_pkg_verify()
    windows = verify.actual_windows(contract, plan['order'])
    assert windows == plan['windows'], 'actual windows != published plan windows'
    win = {}
    for k, (cap, times) in windows.items():
        rep, child = map(int, k.split(','))
        win[(rep, child)] = (cap, tuple(times))
    pairs = {int(k): v for k, v in plan['pairs'].items()}
    sides = {int(k): v for k, v in plan['sides'].items()}
    stage_pair = {int(k): v for k, v in contract['stage_pair'].items()}
    return dict(plan=plan, contract=contract, rows=rows, claim=claim, cons=cons,
                verify=verify, win=win, pairs=pairs, sides=sides,
                stage_pair=stage_pair, order=[tuple(x) for x in plan['order']])

def fam(base, rep, child, port):
    return rep * 896 + (2 * base['pairs'][child] + base['sides'][child]) * 112 + port

def idle_from_rows(base, rows):
    """Idle histogram from row widths per bin (no legality check)."""
    used = defaultdict(int)
    for z in rows:
        used[(z['owner_replica'], z['child'], z['port'])] += z['width']
    idle = Counter()
    for (rep, child), (cap, _t) in base['win'].items():
        for port in range(112):
            rem = cap - used.get((rep, child, port), 0)
            if rem:
                idle[rem] += 1
    return idle

def H_from_idle(idle):
    H = Counter(idle)
    for r, n in PAID.items():
        H[r] += n * 666
    return H

def check_rows2322(base, rows):
    """#2322's own owner check. Returns (H, idle) Counters or raises ValueError."""
    return base['verify'].owners_check(rows, base['plan'], base['contract'])
