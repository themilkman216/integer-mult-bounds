#!/usr/bin/env python3
"""Exact native endpoint for the candidate fill, with #2322's own engine.

Uses vendor/fine_moment.py from research/t74-joint-owner-hillclimb with the
same constants its verify.py sets (SH=256, GRID=2^256, LOG_TERMS=100,
EXP_TERMS=96).  Reproduces the shipped EXACT-MOMENT bracket first
(positive control), then bisects the candidate profile's root on the
10^-40 grid.  Writes CANDIDATE-ENDPOINT.json.
"""
import importlib.util, json, sys
from fractions import Fraction as Q
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from model2322 import load_all, OUT, PKG, rd

spec = importlib.util.spec_from_file_location('fm2322', PKG / 'vendor/fine_moment.py')
e = importlib.util.module_from_spec(spec); spec.loader.exec_module(e)
e.SH = 256; e.GRID = 1 << 256; e.LOG_TERMS = 100; e.EXP_TERMS = 96

base = load_all()
ship_H, _ = base['verify'].owners_check(base['rows'], base['plan'], base['contract'])
cand_rows = rd(OUT / 'CANDIDATE-OWNERS.json.gz')
cand_H, _ = base['verify'].owners_check(cand_rows, base['plan'], base['contract'])
claim = base['claim']
lo = Q(claim['native_endpoint_lower']); hi = Q(claim['native_endpoint_upper'])

def mom(H, b):
    return e.moment(73, 66304, sorted(H.items()), b)
def sgn(H, b):
    m = mom(H, b)
    if m[1] < 1: return -1
    if m[0] > 1: return 1
    return 0

assert sgn(ship_H, lo) == -1 and sgn(ship_H, hi) == 1, 'shipped bracket control'
ms = mom(ship_H, lo); mc = mom(cand_H, lo)
assert mc[1] < ms[0], 'candidate moment must be strictly below shipped at b_lo'
grid = Q(1, 10**40)
xlo, xhi = lo, lo + Q(1, 10**6)
assert sgn(cand_H, xlo) == -1 and sgn(cand_H, xhi) == 1
while xhi - xlo > grid:
    mid = Q(int((xlo + xhi) / 2 / grid)) * grid
    if mid <= xlo:
        mid = xlo + grid
    s = sgn(cand_H, mid)
    assert s != 0, 'grid point unresolved'
    if s == -1: xlo = mid
    else: xhi = mid
def dec40(q):
    return f'{q.numerator * 10**40 // q.denominator // 10**40}.' + \
           f'{q.numerator * 10**40 // q.denominator % 10**40:040d}'
res = dict(
    shipped_profile={str(k): v for k, v in sorted(ship_H.items())},
    candidate_profile={str(k): v for k, v in sorted(cand_H.items())},
    shipped_bracket=[claim['native_endpoint_lower'], claim['native_endpoint_upper']],
    shipped_moment_at_blo_minus1=[str(ms[0] - 1), str(ms[1] - 1)],
    candidate_moment_at_blo_minus1=[str(mc[0] - 1), str(mc[1] - 1)],
    candidate_moment_strictly_below_shipped_at_blo=True,
    candidate_bracket=[dec40(xlo), dec40(xhi)],
    candidate_bracket_rational=[str(xlo), str(xhi)],
    endpoint_gain_dec=float(xlo - hi),
    engine='research/t74-joint-owner-hillclimb/vendor/fine_moment.py '
           '(SH=256, LOG_TERMS=100, EXP_TERMS=96, as its verify.py)')
(OUT / 'CANDIDATE-ENDPOINT.json').write_text(json.dumps(res, indent=1) + '\n')
print('shipped moment-1 at b_lo', float(ms[0] - 1))
print('candidate moment-1 at b_lo', float(mc[0] - 1))
print('candidate bracket', res['candidate_bracket'])
print('endpoint gain over shipped b_hi', res['endpoint_gain_dec'])
