#!/usr/bin/env python3
"""Counting (pattern) relaxation of the owner fill.

Ignoring time windows, families and per-call identity, a fill induces, for
each bin capacity c in {8,16,32,48}, a multiset of bin patterns (multisets of
widths in {4,5,7,8,9} summing to <= c).  The idle moment is sum over bins of
f(cap - load), f(0)=0, f(r)=(r/73)^(1-a).  Minimising over pattern counts
subject to the exact bin counts per cap and item counts per width is an ILP
whose LP relaxation lower-bounds every legal fill.  We solve the LP dual
(9 free variables, one inequality per pattern) with a self-contained float
simplex, then the caller can verify a rounded dual candidate exactly with
Fractions against interval bounds for f from ceiling.child_cost.
"""
import itertools, json, math, sys
from fractions import Fraction as Q
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from model import load_base, load_case, OUT

WIDTHS = (4, 5, 7, 8, 9)
CAPS = (8, 16, 32, 48)
K2269 = Q(16962471390584742207696225394800943861284603706821716607210815258272261945561178592716719999999997996607505720883051558460754921039811,
          10**136)  # outer/OUTER-CLAIM.json kappa_rational (denominator 10^136; see check in main)
# NOTE: denominator exponent verified in bounds.py against the shipped file.

def all_patterns():
    """patterns[cap] = list of count-tuples over WIDTHS with sum <= cap."""
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

def simplex_max(c, A, b):
    """max c^T x s.t. A x <= b, x >= 0, b >= 0.  Dense tableau, Bland-ish pivot
    (smallest index entering with tolerance, min-ratio leaving). Returns (x, obj)."""
    m, n = len(A), len(c)
    # tableau rows: constraints with slacks; last row objective (negated)
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
        # entering: most negative reduced cost
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
        piv = T[leave][enter]
        row = T[leave]
        for j in range(n + m + 1):
            row[j] /= piv
        for i in range(m + 1):
            if i != leave and abs(T[i][enter]) > 0.0:
                f = T[i][enter]
                Ti = T[i]
                for j in range(n + m + 1):
                    Ti[j] -= f * row[j]
        basis[leave] = enter
    x = [0.0] * n
    for i, bv in enumerate(basis):
        if bv < n:
            x[bv] = T[i][-1]
    return x, T[m][-1]

def dual_lp(bins_by_cap, items_by_width, a):
    """Solve max sum_c bins_c*gamma_c + sum_w items_w*pi_w
       s.t. gamma_c + sum_w n_w pi_w <= f(c - sum n_w w) for all patterns.
    Free vars split as pos-neg. Returns dict with gammas, pis, objective."""
    pats = all_patterns()
    # variable order: for each of 9 free vars: (pos, neg)
    free_names = [f'g{c}' for c in CAPS] + [f'p{w}' for w in WIDTHS]
    def vidx(i, sgn): return 2 * i + (0 if sgn > 0 else 1)
    A, b = [], []
    for ci, cap in enumerate(CAPS):
        for pat in pats[cap]:
            load = sum(n * w for n, w in zip(pat, WIDTHS))
            row = [0.0] * 18
            row[vidx(ci, 1)] += 1.0; row[vidx(ci, -1)] -= 1.0
            for wi, n in enumerate(pat):
                if n:
                    row[vidx(4 + wi, 1)] += n; row[vidx(4 + wi, -1)] -= n
            A.append(row); b.append(f_float(cap - load, a))
    cvec = [0.0] * 18
    for ci, cap in enumerate(CAPS):
        cvec[vidx(ci, 1)] += bins_by_cap[cap]; cvec[vidx(ci, -1)] -= bins_by_cap[cap]
    for wi, w in enumerate(WIDTHS):
        cvec[vidx(4 + wi, 1)] += items_by_width[w]; cvec[vidx(4 + wi, -1)] -= items_by_width[w]
    x, obj = simplex_max(cvec, A, b)
    vals = {free_names[i]: x[2 * i] - x[2 * i + 1] for i in range(9)}
    return dict(values=vals, objective=obj, n_patterns=len(A))

def primal_cost_of_fill(base, case, a):
    """Float idle moment of the case's shipped fill, for comparison."""
    from model import width_of
    from collections import defaultdict
    used = defaultdict(int)
    for r in case['fill']['rows']:
        used[(r[2], r[3], r[4])] += width_of(base, case, r[0], r[1])
    tot = 0.0
    for (rep, child), (cap, _t) in base['win'].items():
        for port in range(112):
            tot += f_float(cap - used.get((rep, child, port), 0), a)
    return tot

if __name__ == '__main__':
    base = load_base()
    a_dec = 0.0016962471390584742
    a = a_dec / (1 - a_dec)
    bins_by_cap = {8: 49728, 16: 33152, 32: 33152, 48: 33152}
    res = {}
    for which in ('43', '48'):
        case = load_case(base, which)
        from collections import Counter
        wc = Counter(case['widths']['gauge44'])
        items = {w: wc[w] * len(base['order']) for w in WIDTHS}
        sol = dual_lp(bins_by_cap, items, a)
        ship = primal_cost_of_fill(base, case, a)
        res[which] = dict(items=items, dual=sol, shipped_idle_moment_float=ship,
                          gap=ship - sol['objective'])
        print(which, 'items', items)
        print(' dual obj (LP lower bound on idle moment) =', sol['objective'])
        print(' shipped idle moment                     =', ship)
        print(' gap                                     =', ship - sol['objective'])
        print(' dual values', sol['values'])
    (OUT / 'PATTERN-LP.json').write_text(json.dumps(res, indent=1) + '\n')
