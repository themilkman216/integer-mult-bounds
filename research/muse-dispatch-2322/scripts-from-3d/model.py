#!/usr/bin/env python3
"""Shared exact fill model for muse-t74-exact-fill.

Loads the literal fill rules exactly as research/gmx-t74-borrow43/reconstruct.py
checks them: order/dispatch from inputs/, windows recomputed from the parent
template via vendor/build_parent.py actual_windows, per-helper widths and paid
profiles from the provider registries (43-alias shipped, 48-alias round-3C).
A fill is a list of rows [time, helper, owner_replica, child, port, offset].
Legality (reconstruct.py): every call uses each helper exactly once, families
distinct per call, time in the (rep,child) window, slices inside the bin cap
and non-overlapping, used cells a gap-free prefix per bin. H = idle + paid.
"""
import gzip, importlib.util, json
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
PKG = ROOT / 'research/gmx-t74-borrow43'
EXT = ROOT / 'research/muse-t74-borrow-extend'
OUT = ROOT / 'research/muse-t74-exact-fill'

def rd(p):
    b = Path(p).read_bytes()
    return json.loads(gzip.decompress(b) if str(p).endswith('.gz') else b)

def load_base():
    plan = rd(PKG / 'inputs/PLAN.json')
    parent = rd(PKG / 'inputs/GLOBAL-TEMPLATE.json.gz')
    T = plan['T']
    order = [[s, r + T * g] for s, r in plan['order'] for g in range(2)]
    dispatch0 = {(s, r + T * g): pid for s, r, pid in rd(PKG / 'inputs/DISPATCH.json') for g in range(2)}
    sp = importlib.util.spec_from_file_location('windows', PKG / 'vendor/build_parent.py')
    mod = importlib.util.module_from_spec(sp); sp.loader.exec_module(mod)
    windows, _schedule = mod.actual_windows(parent, order)
    # windows: "rep,child" -> [cap, [times]]
    win = {}
    for k, (cap, times) in windows.items():
        rep, child = map(int, k.split(','))
        win[(rep, child)] = (cap, frozenset(times))
    pairs = {int(k): v for k, v in plan['pairs'].items()}
    sides = {int(k): v for k, v in plan['sides'].items()}
    return dict(plan=plan, T=T, order=order, dispatch0=dispatch0, win=win,
                pairs=pairs, sides=sides)

def fam(base, rep, child, port):
    return rep * 896 + (2 * base['pairs'][child] + base['sides'][child]) * 112 + port

def load_case(base, which):
    """which: '43' shipped #2269 fill, '48' round-3C adapted fill."""
    if which == '43':
        prov = rd(PKG / 'new/BORROW-PROVIDERS.json')
        fill = rd(PKG / 'new/borrow-fill/FILL.json.gz')
    elif which == '48':
        prov = rd(EXT / 'BORROW-PROVIDERS48.json')
        fill = rd(EXT / 'FILL48.json.gz')
    else:
        raise ValueError(which)
    widths = {p: d['widths'] for p, d in prov.items()}
    paid = {p: {int(k): v for k, v in d['actual_paid_profile'].items()} for p, d in prov.items()}
    dispatch = dict(base['dispatch0'])
    for s_, r_, p_ in fill['dispatch_overrides']:
        dispatch[s_, r_] = p_
    R = len(next(iter(widths.values())))
    return dict(which=which, widths=widths, paid=paid, dispatch=dispatch,
                fill=fill, R=R)

def width_of(base, case, time, helper):
    stage, replica = base['order'][time]
    return case['widths'][case['dispatch'][stage, replica]][helper]

def idle_and_H(base, case, rows):
    """Compute idle histogram and H from rows (assumes legality of packing sums)."""
    used = defaultdict(int)
    for time, helper, rep, child, port, offset in rows:
        used[(rep, child, port)] += width_of(base, case, time, helper)
    idle = Counter()
    for (rep, child), (cap, _times) in base['win'].items():
        for port in range(112):
            rem = cap - used.get((rep, child, port), 0)
            if rem:
                idle[rem] += 1
    H = Counter(idle)
    for sr in base['order']:
        for r, n in case['paid'][case['dispatch'][tuple(sr)]].items():
            H[int(r)] += n
    return idle, H

def _req(cond, msg='check_rows'):
    if not cond:
        raise AssertionError(msg)

def check_rows(base, case, rows, want_prefix=True):
    """Literal legality check mirroring reconstruct.py. Returns (idle, H) or raises."""
    order, win, R = base['order'], base['win'], case['R']
    _req(len(rows) == len(order) * R, (len(rows), len(order) * R))
    helpers = defaultdict(set); fams = defaultdict(set); used = defaultdict(set)
    for time, helper, rep, child, port, offset in rows:
        stage, replica = order[time]
        w = width_of(base, case, time, helper)
        cap, allowed = win[(rep, child)]
        _req(time in allowed and 0 <= port < 112 and 0 <= helper < R, ('window', time, rep, child))
        call = (stage, replica); f = fam(base, rep, child, port)
        _req(helper not in helpers[call] and f not in fams[call], ('dup', call, helper, f))
        helpers[call].add(helper); fams[call].add(f)
        cells = set(range(offset, offset + w))
        _req(offset >= 0 and offset + w <= cap and not used[rep, child, port] & cells, ('bin', rep, child, port))
        used[rep, child, port] |= cells
    _req(set(helpers) == set(map(tuple, order)) and all(s == set(range(R)) for s in helpers.values()), 'helper inventory')
    idle = Counter()
    for (rep, child), (cap, _t) in win.items():
        for port in range(112):
            c = used[rep, child, port]
            if want_prefix:
                _req(c == set(range(len(c))), 'gap in pending prefix')
            if cap - len(c):
                idle[cap - len(c)] += 1
    H = Counter(idle)
    for sr in order:
        for r, n in case['paid'][case['dispatch'][tuple(sr)]].items():
            H[int(r)] += n
    plan = base['plan']
    _req(73 * plan['live'] * 2 - sum(r * n for r, n in H.items()) == 2 * plan['deficit'], 'rank-mass deficit')
    return idle, H

def repack_offsets(base, case, rows):
    """Reassign offsets per bin to a gap-free prefix (stable by old offset)."""
    bins = defaultdict(list)
    rows = [list(r) for r in rows]
    for row in rows:
        bins[(row[2], row[3], row[4])].append(row)
    for rs in bins.values():
        rs.sort(key=lambda x: x[5])
        off = 0
        for row in rs:
            row[5] = off
            off += width_of(base, case, row[0], row[1])
    return rows
