#!/usr/bin/env python3
"""Counting (pattern) relaxation for #2322's owner fill (float, discovery).

Adapted from research/prior-muse-t74-exact-fill/scripts/patterns.py
(self-contained dense simplex, Track 3D) with #2322's item counts.
Ignoring windows/families, a fill induces pattern counts per bin capacity;
minimising idle moment over pattern counts with exact bin/item totals is an
LP whose dual (9 free variables) lower-bounds every legal fill.  Exact
rational certification is in bounds.py; nothing here is used as proof.
Writes PATTERN-LP.json (dual) and LP-PRIMAL.json (primal pattern counts).
"""
import json
from fractions import Fraction as Q
from pathlib import Path

WIDTHS = (4, 5, 7, 8, 9)
CAPS = (8, 16, 32, 48)
BINS_BY_CAP = {8: 49728, 16: 33152, 32: 33152, 48: 33152}
PER_CALL = {4: 33, 5: 9, 7: 38, 8: 114, 9: 240}
ITEMS = {w: PER_CALL[w] * 666 for w in WIDTHS}
OUT = Path(__file__).resolve().parents[1]
K2322 = Q(1697060296258836, 10**18)          # CLAIM.json kappa rational
B2322 = Q('0.0016970602962588368950279736213908681182')  # native endpoint lower
SHIPPED_IDLE = {1: 21869, 3: 8479, 4: 17, 5: 2650, 7: 87, 12: 1, 21: 1, 48: 24545}
SHIPPED_PATTERNS = {  # (cap, widths ascending) -> count
    (8, (8,)): 49728, (48, ()): 24545, (32, (4, 9, 9, 9)): 21869,
    (16, (7, 9)): 20142, (16, (8, 8)): 12923, (48, (9, 9, 9, 9, 9)): 8479,
    (32, (5, 9, 9, 9)): 5994, (32, (9, 9, 9)): 2650, (32, (7, 7, 9, 9)): 2527,
    (32, (7, 8, 8, 9)): 112, (48, (4, 8, 9, 9, 9, 9)): 109, (16, (9,)): 87,
    (48, (8, 9, 9, 9, 9)): 17, (48, (9, 9, 9)): 1, (48, (9, 9, 9, 9)): 1}

def all_patterns():
    pats = {}
    for cap in CAPS:
        lst = []
        def rec(i, rem, cur):
            if i == len(WIDTHS):
                lst.append(tuple(cur)); return
            w = WIDTHS[i]
            for n in range(rem // w + 1):
                cur.append(n); rec(i + 1, rem - n * w, cur); cur.pop()
        rec(0, cap, [])
        pats[cap] = lst
    return pats

def f_float(rem, a):
    return 0.0 if rem == 0 else (rem / 73.0) ** (1.0 - a)

def simplex_max(c, A, b, want_y=False):
    """max c^T x s.t. A x <= b, x >= 0, b >= 0 (dense tableau)."""
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
    if want_y:
        return x, [T[m][n + i] for i in range(m)], T[m][-1]
    return x, T[m][-1]

def build_dual_lp(a):
    pats = all_patterns()
    pat_list = [(cap, pat) for cap in CAPS for pat in pats[cap]]
    A, b = [], []
    for cap, pat in pat_list:
        load = sum(n * w for n, w in zip(pat, WIDTHS))
        row = [0.0] * 18
        ci = CAPS.index(cap)
        row[2 * ci] += 1.0; row[2 * ci + 1] -= 1.0
        for wi, n in enumerate(pat):
            if n:
                row[2 * (4 + wi)] += n; row[2 * (4 + wi) + 1] -= n
        A.append(row); b.append(f_float(cap - load, a))
    cvec = [0.0] * 18
    for ci, cap in enumerate(CAPS):
        cvec[2 * ci] += BINS_BY_CAP[cap]; cvec[2 * ci + 1] -= BINS_BY_CAP[cap]
    for wi, w in enumerate(WIDTHS):
        cvec[2 * (4 + wi)] += ITEMS[w]; cvec[2 * (4 + wi) + 1] -= ITEMS[w]
    return pat_list, A, b, cvec

def fmt(pat):
    return tuple(w for n, w in zip(pat, WIDTHS) for _ in range(n))

if __name__ == '__main__':
    res = {}; primal = {}
    for name, aval in [('b2322', float(B2322)), ('A2322', float(K2322 / (1 - K2322)))]:
        pat_list, A, b, cvec = build_dual_lp(aval)
        x, y, obj = simplex_max(cvec, A, b, want_y=True)
        names = [f'g{c}' for c in CAPS] + [f'p{w}' for w in WIDTHS]
        vals = {names[i]: x[2 * i] - x[2 * i + 1] for i in range(9)}
        ship = sum(n * f_float(r, aval) for r, n in SHIPPED_IDLE.items())
        res[name] = dict(a=aval, items=ITEMS, dual=dict(values=vals, objective=obj,
                                                         n_patterns=len(A)),
                         shipped_idle_moment_float=ship, gap=ship - obj)
        lp = {(cap, fmt(pat)): y[i] for i, (cap, pat) in enumerate(pat_list) if abs(y[i]) > 1e-6}
        diffs = []
        for k in sorted(set(lp) | set(SHIPPED_PATTERNS), key=str):
            d = lp.get(k, 0.0) - SHIPPED_PATTERNS.get(k, 0)
            if abs(d) > 1e-4:
                diffs.append(dict(cap=k[0], widths=list(k[1]), lp=lp.get(k, 0.0),
                                  shipped=float(SHIPPED_PATTERNS.get(k, 0)), diff=d))
        primal[name] = dict(lp_objective=obj,
                            lp_patterns=[dict(cap=c, widths=list(ws), count=v)
                                         for (c, ws), v in sorted(lp.items(), key=lambda kv: -kv[1])],
                            diffs=diffs)
        print(name, 'a', aval, 'dual LB', obj, 'shipped', ship, 'gap', ship - obj)
        print(' values', vals)
        print(' LP patterns:', primal[name]['lp_patterns'])
    (OUT / 'PATTERN-LP.json').write_text(json.dumps(res, indent=1) + '\n')
    (OUT / 'LP-PRIMAL.json').write_text(json.dumps(primal, indent=1) + '\n')
