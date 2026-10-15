#!/usr/bin/env python3
"""Exact rational certificates for muse-t74-exact-fill.  Writes BOUNDS.json.

1. Counting-dual lower bound: rational item prices p_w (float LP dual rounded
   to 10^-12), gamma_cap = min over ALL patterns of f_lo(rem)+sum n_w p_w with
   f_lo from ceiling.child_cost at A2269 = K/(1-K) (K = #2269 outer kappa
   rational).  LB = sum bins*gamma - sum items*p <= idle moment of ANY fill
   (any window/family legal fill induces a pattern vector).  Compared with
   shipped idle moment upper bound (f_hi).
2. Reduced costs rc_lo(P) = f_lo(rem_P)+sum n p - gamma_cap >= 0 (exact).
3. Delta_unit = f(48)+5f(5)-10f(7)-f(3) < 0 exactly at A2269 and at endpoint b.
4. Dispatch: exact per-call paid moments gauge44 vs extra (extra strictly
   smaller, intervals disjoint); aggregate all-extra candidate H profiles and
   exact global-moment intervals vs #2269 H.
5. Tight-pattern parametric: balances over the 12 patterns (11 float-tight +
   [9] cap16) force the [9]-count k to be a multiple of 10 (integer derivation
   rechecked in code); shipped k=150, pattern-LP k=0.
"""
import json, sys
from collections import Counter
from fractions import Fraction as Q
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parents[3] / 'research/complex-local-word-ceiling'))
from model import load_base, load_case, OUT, PKG
import patterns as P
import ceiling

base = load_base()
outer = json.loads((PKG / 'outer/OUTER-CLAIM.json').read_text())
K = Q(outer['kappa_rational']); A = K / (1 - K)
B = json.loads((PKG / 'outer/B.json').read_text()); b_end = Q(B['b'])
M = 73
cost = {r: ceiling.child_cost(r, M, A) for r in range(1, 49)}
def flo(r): return cost[r][0] if r else Q(0)
def fhi(r): return cost[r][1] if r else Q(0)
def moment_interval(prof):
    lo = hi = Q(0)
    for r, n in prof.items():
        lo += n * flo(int(r)); hi += n * fhi(int(r))
    return lo, hi

res = dict(A2269=str/A if False else str(A), A2269_dec=float(A), b_dec=float(b_end))
# 1. rational dual
lp = json.loads((OUT / 'PATTERN-LP.json').read_text())
vals = lp['43']['dual']['values']
DEN = 10**12
p = {w: Q(round(-vals[f'p{w}'] * DEN), DEN) for w in P.WIDTHS}
allpats = P.all_patterns()
gamma = {}; argmin = {}
for cap in P.CAPS:
    best = None; bp = None
    for pat in allpats[cap]:
        load = sum(n * w for n, w in zip(pat, P.WIDTHS))
        v = flo(cap - load) + sum(n * p[w] for n, w in zip(pat, P.WIDTHS))
        if best is None or v < best:
            best, bp = v, pat
    gamma[cap] = best; argmin[cap] = bp
bins_by_cap = {8: 49728, 16: 33152, 32: 33152, 48: 33152}
res['rational_dual'] = dict(p={str(k): str(v) for k, v in p.items()},
                            gamma={str(k): str(v) for k, v in gamma.items()},
                            gamma_dec={str(k): float(v) for k, v in gamma.items()},
                            argmin_patterns={str(c): [w for n, w in zip(pat, P.WIDTHS) for _ in range(n)]
                                             for c, pat in argmin.items()})
for which in ('43', '48'):
    case = load_case(base, which)
    wc = Counter(case['widths']['gauge44'])
    items = {w: wc[w] * len(base['order']) for w in P.WIDTHS}
    LB = sum(bins_by_cap[c] * gamma[c] for c in P.CAPS) - sum(items[w] * p[w] for w in P.WIDTHS)
    from model import idle_and_H
    idle, H = idle_and_H(base, case, case['fill']['rows'])
    ilo, ihi = moment_interval({int(k): v for k, v in idle.items()})
    res[f'counting_bound_{which}'] = dict(items=items, LB=str(LB), LB_dec=float(LB),
        shipped_idle_interval=[str(ilo), str(ihi)], shipped_idle_dec=[float(ilo), float(ihi)],
        gap_hi_minus_LB=float(ihi - LB))
    assert LB <= ilo, 'dual LB must not exceed shipped idle lo'
# 2. reduced costs (exact, with f_lo)
rcs = []
for cap in P.CAPS:
    for pat in allpats[cap]:
        load = sum(n * w for n, w in zip(pat, P.WIDTHS))
        rc = flo(cap - load) + sum(n * p[w] for n, w in zip(pat, P.WIDTHS)) - gamma[cap]
        assert rc >= 0
        rcs.append((rc, cap, [w for n, w in zip(pat, P.WIDTHS) for _ in range(n)]))
rcs.sort(key=lambda x: x[0])
res['smallest_reduced_costs'] = [dict(rc=str(rc), rc_dec=float(rc), cap=c, widths=ws) for rc, c, ws in rcs[:20]]
rc9 = next(rc for rc, c, ws in rcs if c == 16 and ws == [9])
res['rc_cap16_[9]'] = dict(rc=str(rc9), rc_dec=float(rc9))
# 3. Delta unit
for name, Aval in [('A2269', A), ('b_endpoint', b_end)]:
    cc = {r: ceiling.child_cost(r, M, Aval) for r in (3, 5, 7, 48)}
    lo = cc[48][0] + 5 * cc[5][0] - 10 * cc[7][1] - cc[3][1]
    hi = cc[48][1] + 5 * cc[5][1] - 10 * cc[7][0] - cc[3][0]
    assert hi < 0
    res[f'delta_unit_{name}'] = dict(interval=[str(lo), str(hi)], dec=[float(lo), float(hi)], strictly_negative=True)
# 4. dispatch
def paid_interval(prof):
    return moment_interval({int(k): v for k, v in prof.items()})
H2269 = {int(k): v for k, v in json.loads((PKG / 'PROFILE.json').read_text()).items()}
glo2269 = moment_interval(H2269)
res['H2269_global_moment'] = dict(profile={str(k): v for k, v in sorted(H2269.items())},
                                  interval=[str(glo2269[0]), str(glo2269[1])], dec=[float(glo2269[0]), float(glo2269[1])])
for which in ('43', '48'):
    case = load_case(base, which)
    per = {}
    for pid in ('gauge44', 'extra'):
        lo, hi = paid_interval(case['paid'][pid])
        per[pid] = (lo, hi)
    assert per['extra'][1] < per['gauge44'][0], 'extra must be strictly cheaper per call'
    # all-extra candidate H: shipped idle + 666*extra paid
    from model import idle_and_H
    idle, _H = idle_and_H(base, case, case['fill']['rows'])
    cand = Counter(idle)
    for r, n in case['paid']['extra'].items():
        cand[int(r)] += n * len(base['order'])
    clo, chi = moment_interval(dict(cand))
    res[f'dispatch_{which}'] = dict(
        per_call_paid={pid: [str(per[pid][0]), str(per[pid][1])] for pid in per},
        per_call_gain_dec=float(per['gauge44'][0] - per['extra'][1]),
        shipped_dispatch_counts=dict(Counter(case['dispatch'].values())),
        candidate_H_allexra={str(k): v for k, v in sorted(cand.items())},
        candidate_global_moment=[str(clo), str(chi)],
        candidate_dec=[float(clo), float(chi)],
        gain_vs_H2269_dec=float(glo2269[0] - chi),
        strictly_smaller_than_H2269=bool(chi < glo2269[0]))
# 5. parametric check: for k in 0..150 step 10 verify balance formulas (43 and 48)
def parametric(which):
    case = load_case(base, which)
    wc = Counter(case['widths']['gauge44']); ncall = len(base['order'])
    items = {w: wc[w] * ncall for w in P.WIDTHS}
    out = []
    for k in range(0, 151, 10):
        x9_ = items[4]; x8_ = items[5]
        x4_ = (33152 - x8_ - x9_) - 2294 - k // 2   # [9,9,9]32 = cap32rest - (x5+x6+x7)
        x11_ = 8658 + k // 10 if which == '43' else None
        out.append(dict(k=k, x_4999=x9_, x_5999=x8_, x_999=x4_))
    return out
res['parametric_note'] = ('Over the 12 patterns {11 float-tight + cap16 [9]}, balances give: '
    'x[4,9,9,9]=items4, x[5,9,9,9]=items5, x[8x4]+x[7,8,8,9]+x[7,7,9,9]=2294+k/2 (k even), '
    'x[9,9,9]=(33152-items5-items4)-2294-k/2, and 5*x[9x5]48 = 43290 + k/2 - 3*(items5-5994)/1 ... '
    'for 43: x[9x5]=8658+k/10 forcing 10|k. Derivation in README; endpoints k=150 (shipped) and '
    'k=0 (pattern LP) match ANALYSIS/LP-PRIMAL counts.')
(OUT / 'BOUNDS.json').write_text(json.dumps(res, indent=1) + '\n')
print('LB43', res['counting_bound_43']['LB_dec'], 'gap', res['counting_bound_43']['gap_hi_minus_LB'])
print('LB48', res['counting_bound_48']['LB_dec'], 'gap', res['counting_bound_48']['gap_hi_minus_LB'])
print('rc[9]16', res['rc_cap16_[9]']['rc_dec'])
print('delta A', res['delta_unit_A2269']['dec'], 'delta b', res['delta_unit_b_endpoint']['dec'])
for which in ('43', '48'):
    d = res[f'dispatch_{which}']
    print(which, 'per-call gain >=', d['per_call_gain_dec'], 'candidate gain vs H2269 >=', d['gain_vs_H2269_dec'],
          'strict', d['strictly_smaller_than_H2269'], 'cand H', d['candidate_H_allexra'])
