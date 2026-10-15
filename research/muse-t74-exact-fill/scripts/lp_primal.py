#!/usr/bin/env python3
"""Recover the primal pattern-LP optimum (pattern counts) from the dual
simplex tableau shadow prices, and compare with the shipped fills' pattern
counts.  Also lists tight patterns at the dual optimum."""
import json, sys
from collections import Counter, defaultdict
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from model import load_base, load_case, width_of, OUT
import patterns as P

def simplex_with_duals(c, A, b):
    m, n = len(A), len(c)
    T = [[0.0] * (n + m + 1) for _ in range(m + 1)]
    for i in range(m):
        for j in range(n):
            T[i][j] = A[i][j]
        T[i][n + i] = 1.0
        T[i][-1] = b[i]
    for j in range(n):
        T[m][j] = -c[j]
    basis = [n + i for i in range(m)]
    EPS = 1e-9
    for _ in range(200000):
        enter, best = -1, -EPS
        for j in range(n + m):
            if T[m][j] < best:
                best, enter = T[m][j], j
        if enter < 0:
            break
        leave, ratio = -1, float('inf')
        for i in range(m):
            if T[i][enter] > EPS:
                r = T[i][-1] / T[i][enter]
                if r < ratio - 1e-12:
                    ratio, leave = r, i
        if leave < 0:
            raise ValueError('unbounded')
        piv = T[leave][enter]; row = T[leave]
        for j in range(n + m + 1):
            row[j] /= piv
        for i in range(m + 1):
            if i != leave and T[i][enter] != 0.0:
                f = T[i][enter]; Ti = T[i]
                for j in range(n + m + 1):
                    Ti[j] -= f * row[j]
        basis[leave] = enter
    x = [0.0] * n
    for i, bv in enumerate(basis):
        if bv < n:
            x[bv] = T[i][-1]
    y = [T[m][n + i] for i in range(m)]  # shadow prices = primal pattern counts
    return x, y, T[m][-1]

base = load_base()
a_dec = 0.0016962471390584742
a = a_dec / (1 - a_dec)
bins_by_cap = {8: 49728, 16: 33152, 32: 33152, 48: 33152}
pats = P.all_patterns()
pat_list = []  # (cap, pat)
for cap in P.CAPS:
    for pat in pats[cap]:
        pat_list.append((cap, pat))
print('total patterns', len(pat_list), {c: len(pats[c]) for c in P.CAPS})

out = {}
for which in ('43', '48'):
    case = load_case(base, which)
    wc = Counter(case['widths']['gauge44'])
    items = {w: wc[w] * len(base['order']) for w in P.WIDTHS}
    # rebuild dual LP in same order as patterns.dual_lp
    A, b = [], []
    for cap, pat in pat_list:
        load = sum(n * w for n, w in zip(pat, P.WIDTHS))
        row = [0.0] * 18
        ci = P.CAPS.index(cap)
        row[2 * ci] += 1.0; row[2 * ci + 1] -= 1.0
        for wi, n in enumerate(pat):
            if n:
                row[2 * (4 + wi)] += n; row[2 * (4 + wi) + 1] -= n
        A.append(row); b.append(P.f_float(cap - load, a))
    cvec = [0.0] * 18
    for ci, cap in enumerate(P.CAPS):
        cvec[2 * ci] += bins_by_cap[cap]; cvec[2 * ci + 1] -= bins_by_cap[cap]
    for wi, w in enumerate(P.WIDTHS):
        cvec[2 * (4 + wi)] += items[w]; cvec[2 * (4 + wi) + 1] -= items[w]
    x, y, obj = simplex_with_duals(cvec, A, b)
    lp_counts = {(cap, pat): y[i] for i, (cap, pat) in enumerate(pat_list) if abs(y[i]) > 1e-6}
    # shipped pattern counts
    bins = defaultdict(list)
    for r in case['fill']['rows']:
        bins[(r[2], r[3], r[4])].append(width_of(base, case, r[0], r[1]))
    ship = Counter()
    for (rep, child), (cap, _t) in base['win'].items():
        for port in range(112):
            ws = bins.get((rep, child, port), [])
            cnt = tuple(ws.count(w) for w in P.WIDTHS)
            ship[(cap, cnt)] += 1
    def fmt(pat):
        return [w for n, w in zip(pat, P.WIDTHS) for _ in range(n)]
    print(f'== {which}: LP obj {obj:.6f}')
    print(' LP patterns (cap, widths, count):')
    for (cap, pat), v in sorted(lp_counts.items(), key=lambda kv: -kv[1]):
        print('   ', cap, fmt(pat), f'{v:.4f}')
    print(' diff LP - shipped (only nonzero):')
    keys = set(lp_counts) | set(ship)
    diffs = []
    for k in keys:
        d = lp_counts.get(k, 0.0) - ship.get(k, 0)
        if abs(d) > 1e-4:
            cap, pat = k
            diffs.append(dict(cap=cap, widths=fmt(pat), lp=lp_counts.get(k, 0.0),
                              shipped=float(ship.get(k, 0)), diff=d))
            print('   ', k[0], fmt(k[1]), f'LP {lp_counts.get(k,0.0):.4f} vs ship {ship.get(k,0)}  diff {d:+.4f}')
    # verify LP primal feasibility
    chk_bins = Counter(); chk_items = Counter()
    for (cap, pat), v in lp_counts.items():
        chk_bins[cap] += v
        for n, w in zip(pat, P.WIDTHS):
            chk_items[w] += v * n
    print(' LP bin check', {c: round(chk_bins[c] - bins_by_cap[c], 6) for c in P.CAPS},
          'item check', {w: round(chk_items[w] - items[w], 6) for w in P.WIDTHS})
    out[which] = dict(lp_objective=obj,
                      lp_patterns=[dict(cap=c, widths=fmt(p), count=v) for (c, p), v in lp_counts.items()],
                      diffs=diffs)
(OUT / 'LP-PRIMAL.json').write_text(json.dumps(out, indent=1) + '\n')
