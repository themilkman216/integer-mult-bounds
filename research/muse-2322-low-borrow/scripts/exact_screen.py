#!/usr/bin/env python3
"""Exact rational certificates for the #2322 borrowing screen.

For each candidate scenario (floats/duals from SCREEN-LP.json, paid and
width deltas measured at stage P in STAGEP-SINGLES.json and transferred to
#2322's final totals -- assumption A, see README), this computes with
exact rational arithmetic:

  candidate_lb = paid_lo(candidate global paid profile)
               + idle_lb(candidate role totals)

where paid_lo sums count * child_cost_lo(rank, 73, a2322) with a2322 the
exact Fraction kappa/(1-kappa) from #2322's CLAIM.json (child_cost is
Douglas Colkitt's directed-arithmetic enclosure in
research/complex-local-word-ceiling/ceiling.py), and idle_lb is the LP
dual objective of floored rational duals (1e-12 grid) verified feasible
against cost_lo for every one of the 1163 bin patterns.  Any legal owner
fill of a word with those role totals in this bin template has idle
moment >= idle_lb (windows/families/integrality only increase it).

candidate_lb > actual_hi (#2322's shipped global profile, cost_hi)
falsifies the scenario inside the template scope under assumption A.
For width-5 highs the comparison that matters is candidate_lb vs
base_lb (same bound for #2322's current widths): equality says the alias
adds nothing beyond hypothetically repacking the current word to its own
fractional bound.

Output: EXACT-SCREEN.json.  Fractions are compared exactly in-process;
JSON stores 12-significant-digit decimals plus the exact booleans.
"""
import importlib.util, json, math
from fractions import Fraction as Q
from pathlib import Path

PKG = Path(__file__).resolve().parent.parent
WS = Path(__file__).resolve().parents[3]
SRC2322 = WS / 'research/t74-joint-owner-hillclimb'

spec = importlib.util.spec_from_file_location(
    'ceiling', WS / 'research/complex-local-word-ceiling/ceiling.py')
ceiling = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ceiling)

claim = json.load(open(SRC2322 / 'CLAIM.json'))
k_num, k_den = (int(x) for x in claim['kappa'].split('/'))
KAPPA = Q(k_num, k_den)
A = KAPPA / (1 - KAPPA)
CALLS = 666
CAPS = {8: 49728, 16: 33152, 32: 33152, 48: 33152}
WIDTHS = [9, 8, 7, 5, 4]
PAID_CALL = {1: 2335, 2: 512, 3: 426, 4: 120, 5: 38, 8: 8}
GLOBAL = {int(k): v for k, v in json.load(open(SRC2322 / 'data/PROFILE.json')).items()}

_cost = {}
def cost(r):
    if r not in _cost:
        _cost[r] = (Q(0), Q(0)) if r == 0 else ceiling.child_cost(r, 73, A)
    return _cost[r]

def dec(x, digits=12):
    """Decimal string of a Fraction, correctly rounded to `digits` decimals."""
    scaled = x * 10**digits
    n = scaled.numerator // scaled.denominator
    if scaled - n >= Q(1, 2):
        n += 1
    s = str(abs(n)).rjust(digits + 1, '0')
    return ('-' if n < 0 else '') + s[:-digits] + '.' + s[-digits:]

pats = []
for cap in CAPS:
    for a in range(cap // 9 + 1):
        for b in range((cap - 9 * a) // 8 + 1):
            for c_ in range((cap - 9 * a - 8 * b) // 7 + 1):
                for d in range((cap - 9 * a - 8 * b - 7 * c_) // 5 + 1):
                    for e in range((cap - 9 * a - 8 * b - 7 * c_ - 5 * d) // 4 + 1):
                        cnt = (a, b, c_, d, e)
                        rem = cap - sum(w * x for w, x in zip(WIDTHS, cnt))
                        pats.append((cap, cnt, rem))
assert len(pats) == 1163

def exact_idle_lb(roles, duals_float, extra_floor=Q(0)):
    """Floored rational duals; exact feasibility; returns (lb, min_slack, duals)."""
    def fl(v):
        return Q(math.floor(v * 10**12), 10**12) - extra_floor
    yb = {int(k): fl(v) for k, v in duals_float['bins'].items()}
    yr = {int(k): fl(v) for k, v in duals_float['roles'].items()}
    min_slack = None
    for cap, cnt, rem in pats:
        lhs = yb[cap] + sum(yr[w] * x for w, x in zip(WIDTHS, cnt))
        slack = cost(rem)[0] - lhs
        if min_slack is None or slack < min_slack:
            min_slack = slack
    obj = sum(CAPS[c] * yb[c] for c in CAPS) + sum(roles[w] * yr[w] for w in WIDTHS)
    return obj, min_slack, dict(bins=yb, roles=yr)

def paid_lo(paid_call):
    return sum(Q(CALLS * n) * cost(r)[0] for r, n in paid_call.items())

actual_hi = sum(Q(n) * cost(r)[1] for r, n in GLOBAL.items())
print(f'#2322 actual total moment <= {dec(actual_hi)} (exact hi)')

screen = json.load(open(PKG / 'SCREEN-LP.json'))
rows_by_name = {r['name']: r for r in screen['rows']}

def paid_call_for(row):
    p = dict(PAID_CALL)
    if row.get('paid_delta_per_call'):
        for r, d in row['paid_delta_per_call'].items():
            p[int(r)] = p.get(int(r), 0) + d
    else:
        p[3] -= row['nlow'] or 0
        p[5] -= row['nhigh'] or 0
    assert all(v >= 0 for v in p.values()), p
    return p

SCEN = ['base #2322 widths (LP gap check)', 'low x1',
        '653 re-alias (measured stage-P)', 'low624 class x1 (measured stage-P)',
        'high x1', 'high x9 (all width-5)', 'low x32']
out_rows = []
base_lb = None
for name in SCEN:
    row = rows_by_name[name]
    roles = {int(k): v for k, v in row['roles'].items()}
    idle_lb, slack, duals = exact_idle_lb(roles, row['duals'])
    assert slack >= 0, (name, 'dual infeasible', dec(slack))
    plo = paid_lo(paid_call_for(row))
    lb = plo + idle_lb
    if name.startswith('base'):
        base_lb = lb
    rec = dict(name=name, paid_lo=dec(plo), idle_lb=dec(idle_lb),
               candidate_lb=dec(lb), min_dual_slack=dec(slack, 15),
               falsified_vs_actual=bool(lb > actual_hi),
               margin_vs_actual=dec(lb - actual_hi),
               margin_vs_base_lb=dec(lb - base_lb) if base_lb is not None else None)
    out_rows.append(rec)
    print(f'{name:38s} lb {rec["candidate_lb"]} vs actual {rec["margin_vs_actual"]} '
          f'vs baseLB {rec["margin_vs_base_lb"]} falsified={rec["falsified_vs_actual"]}')

# low x32 with the prior round's measured JOINT paid delta (48->80, stage P)
row = rows_by_name['low x32']
roles = {int(k): v for k, v in row['roles'].items()}
idle_lb, slack, _ = exact_idle_lb(roles, row['duals'])
joint_call = dict(PAID_CALL)
for r, d in {1: -48, 2: 26, 3: -28, 4: -4}.items():
    joint_call[r] += d
lb = paid_lo(joint_call) + idle_lb
rec = dict(name='low x32 (joint paid delta variant)', paid_lo=dec(paid_lo(joint_call)),
           idle_lb=dec(idle_lb), candidate_lb=dec(lb), min_dual_slack=dec(slack, 15),
           falsified_vs_actual=bool(lb > actual_hi), margin_vs_actual=dec(lb - actual_hi),
           margin_vs_base_lb=dec(lb - base_lb),
           note='paid delta = prior round stage-P measured 48->80 profile delta per call, transferred')
out_rows.append(rec)
print(f'{"low x32 (joint paid delta variant)":38s} lb {rec["candidate_lb"]} vs actual '
      f'{rec["margin_vs_actual"]} falsified={rec["falsified_vs_actual"]}')

out = dict(kappa2322=claim['kappa'], a2322=f'{A.numerator}/{A.denominator}',
           actual_total_hi=dec(actual_hi), base_lb=dec(base_lb),
           assumption_A='stage-P measured paid/width deltas transfer unchanged through the frame refit, pivot kernels and block-616 stages to #2322 final totals',
           rows=out_rows)
(PKG / 'EXACT-SCREEN.json').write_text(json.dumps(out, indent=1) + '\n')
print('wrote EXACT-SCREEN.json')
