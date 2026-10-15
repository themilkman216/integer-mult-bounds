#!/usr/bin/env python3
"""Exact rational counting bound for #2322's fill. Writes BOUNDS.json.

Method (Track 3D, adapted): rational item prices p_w (float LP dual rounded
to 10^-12), gamma_cap = min over ALL patterns of f_lo(rem) + sum n_w p_w with
f intervals from ceiling.child_cost.  LB = sum bins*gamma - sum items*p is a
lower bound on the idle moment of ANY fill (legal fills induce pattern
vectors).  Evaluated at b2322 (native endpoint lower, CLAIM.json) and at
A2322 = K/(1-K), K = CLAIM kappa.  Also: exact reduced-cost decomposition of
the shipped gap, the tight-pattern balance forcing k = 6 (mod 10) for the
cap-16 [9] count k, and exact idle-moment intervals for the shipped fill and
for the integral tight pattern vector at k=6 (pattern level only).
"""
import json, sys
from fractions import Fraction as Q
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parents[3] / 'research/complex-local-word-ceiling'))
import patterns as P
import ceiling

OUT = P.OUT
res = {}
lp = json.loads((OUT / 'PATTERN-LP.json').read_text())
allpats = P.all_patterns()
DEN = 10**12

for name, Aval in [('b2322', P.B2322), ('A2322', P.K2322 / (1 - P.K2322))]:
    cost = {r: ceiling.child_cost(r, 73, Aval) for r in range(1, 49)}
    def flo(r, cost=cost): return cost[r][0] if r else Q(0)
    def fhi(r, cost=cost): return cost[r][1] if r else Q(0)
    vals = lp[name]['dual']['values']
    p = {w: Q(round(-vals[f'p{w}'] * DEN), DEN) for w in P.WIDTHS}
    gamma = {}; argmin = {}
    for cap in P.CAPS:
        best = None; bp = None
        for pat in allpats[cap]:
            load = sum(n * w for n, w in zip(pat, P.WIDTHS))
            v = flo(cap - load) + sum(n * p[w] for n, w in zip(pat, P.WIDTHS))
            if best is None or v < best:
                best, bp = v, pat
        gamma[cap] = best; argmin[cap] = bp
    LB = sum(P.BINS_BY_CAP[c] * gamma[c] for c in P.CAPS) - sum(P.ITEMS[w] * p[w] for w in P.WIDTHS)
    ilo = sum(n * flo(r) for r, n in P.SHIPPED_IDLE.items())
    ihi = sum(n * fhi(r) for r, n in P.SHIPPED_IDLE.items())
    assert LB <= ilo, 'dual LB must not exceed shipped idle lo'
    # exact reduced costs and shipped decomposition
    rcs = []
    for cap in P.CAPS:
        for pat in allpats[cap]:
            load = sum(n * w for n, w in zip(pat, P.WIDTHS))
            rc = flo(cap - load) + sum(n * p[w] for n, w in zip(pat, P.WIDTHS)) - gamma[cap]
            assert rc >= 0
            rcs.append((rc, cap, P.fmt(pat)))
    rcs.sort(key=lambda x: x[0])
    decomp = []
    total_rc = Q(0)
    for (cap, ws), n in sorted(P.SHIPPED_PATTERNS.items(), key=str):
        load = sum(ws)
        rc = flo(cap - load) + sum(p[w] for w in ws) - gamma[cap]
        total_rc += n * rc
        if rc:
            decomp.append(dict(cap=cap, widths=list(ws), count=n, rc=str(rc),
                               rc_dec=float(rc), contrib_dec=float(n * rc)))
    # tight-pattern balance derivation, checked by direct substitution at k=6
    # variables: a=[7,9]16 b=[8,8]16 k=[9]16; c4,c5,d=[9,9,9],e1=[7,7,9,9],
    # e2=[7,8,8,9],e3=[8x4] (cap32); g5=[9x5]48, g0=[]48; cap8 [8] fixed.
    k6 = {}
    kk = 6; e3 = 2627 + kk // 2; e1 = e2 = 0
    a_ = 25308 - 2 * e1 - e2; b_ = 33152 - a_ - kk
    c4 = 21978; c5 = 5994; d_ = 2553 - kk // 2; g5 = (42957 + kk // 2) // 5
    assert (42957 + kk // 2) % 5 == 0 and kk % 2 == 0
    g0 = 33152 - g5
    vec = {(16, (7, 9)): a_, (16, (8, 8)): b_, (16, (9,)): kk,
           (32, (4, 9, 9, 9)): c4, (32, (5, 9, 9, 9)): c5, (32, (9, 9, 9)): d_,
           (32, (8, 8, 8, 8)): e3, (48, (9, 9, 9, 9, 9)): g5, (48, ()): g0,
           (8, (8,)): 49728}
    # verify bin/item balances of the k=6 vector exactly
    from collections import Counter
    bc = Counter(); ic = Counter()
    for (cap, ws), n in vec.items():
        bc[cap] += n
        for w in ws:
            ic[w] += n
    assert all(bc[c] == P.BINS_BY_CAP[c] for c in P.CAPS), bc
    assert all(ic[w] == P.ITEMS[w] for w in P.WIDTHS), ic
    idle6 = Counter()
    for (cap, ws), n in vec.items():
        if cap - sum(ws):
            idle6[cap - sum(ws)] += n
    k6lo = sum(n * flo(r) for r, n in idle6.items())
    k6hi = sum(n * fhi(r) for r, n in idle6.items())
    res[name] = dict(
        A=str(Aval), A_dec=float(Aval),
        rational_dual=dict(p={str(k_): str(v) for k_, v in p.items()},
                           gamma={str(k_): str(v) for k_, v in gamma.items()},
                           gamma_dec={str(k_): float(v) for k_, v in gamma.items()}),
        LB=str(LB), LB_dec=float(LB),
        shipped_idle_interval=[str(ilo), str(ihi)],
        shipped_idle_dec=[float(ilo), float(ihi)],
        gap_exact_range=[float(ilo - LB), float(ihi - LB)],
        shipped_gap_decomposition=decomp,
        sum_count_times_rc_dec=float(total_rc),
        smallest_reduced_costs=[dict(rc_dec=float(rc), cap=c, widths=list(ws))
                                for rc, c, ws in rcs[:16]],
        tight_k6_vector=dict(counts={f'{c}:{ws}': n for (c, ws), n in vec.items()},
                             idle={str(k_): v for k_, v in sorted(idle6.items())},
                             idle_interval_dec=[float(k6lo), float(k6hi)],
                             above_LB_dec=float(k6lo - LB)),
        balance_note=('Over 11 tight patterns + [9]16(count k): c4=21978, c5=5994, '
                      'a+2e1+e2=25308, b+e2+2e3=13098, a+b+k=33152 give '
                      'e1+e2+e3=2627+k/2 (k even), d=2553-k/2, and width-9 balance '
                      '5*g5=42957+k/2, forcing k=6 (mod 10) for integral g5.'))
    print(name, 'LB', float(LB), 'shipped', float(ilo), float(ihi),
          'gap', float(ilo - LB), float(ihi - LB))
    print(' decomp', [(d['cap'], d['widths'], d['count'], round(d['contrib_dec'], 6)) for d in decomp])
    print(' k6 pattern idle', float(k6lo), 'above LB', float(k6lo - LB))

(OUT / 'BOUNDS.json').write_text(json.dumps(res, indent=1) + '\n')
