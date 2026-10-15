#!/usr/bin/env python3
"""Compute 90-digit certified complex endpoints for the candidate profile
H_cand with #2269's own fine engines, replicating assemble.py check_moment's
certify() exactly (fine_mercator + fine_moment enclosures, conservative
surcharge via the fake rank-1 entry scaled by 1e-16).  Decimal (prec 140)
proposes the endpoint; the exact engines verify accept at q/10^90 and
reject at (q+1)/10^90, searching q near the proposal.  Writes
FINE-ENDPOINTS.json and updates work/pkg/new/SPEC.json expected endpoints +
outer_refinement.endpoint_digits=90.  Usage: fine_endpoints.py"""
import json, os, sys
from decimal import Decimal, localcontext, ROUND_FLOOR
from fractions import Fraction as Q
from pathlib import Path

OUT = Path(__file__).resolve().parent.parent
W = OUT / 'work'
os.environ.setdefault('FINE_ENGINE_CACHE', str(W / 'fine-cache'))
os.environ['PYTHONINTMAXSTRDIGITS'] = '0'
sys.set_int_max_str_digits(0)
sys.path.insert(0, str(W / 'pkg' / 'code'))
import fine_cache as FC  # noqa: E402

H = {1: 1581762, 2: 338986, 3: 287057, 4: 83254, 5: 28785, 7: 150, 8: 5328, 48: 24479}
m, Wlive = 73, 66304
assert m * Wlive - sum(r * n for r, n in H.items()) == 2 * 11840

def enclosures(z, bad):
    l, u = FC.moment('fine_mercator', H, m, Wlive, z, bad)
    ll, uu = FC.moment('fine_moment', None, m, Wlive, z, False, list(H.items()))
    if bad:
        fl, fu = FC.moment('fine_moment', None, m, Wlive, z, False, [(1, 32 * m * m * sum(H.values()))])
        ll += fl / 10**16; uu += fu / 10**16
    return l, u, ll, uu

def accepted(z, bad):
    l, u, ll, uu = enclosures(z, bad)
    return u < 1 and uu < 1

def rejected(z, bad):
    l, u, ll, uu = enclosures(z, bad)
    return l > 1 and ll > 1

def propose(bad):
    with localcontext() as c:
        c.prec = 140
        terms = [(Decimal(r * n) / Decimal(m * Wlive), (Decimal(m) / Decimal(r)).ln()) for r, n in H.items()]
        fallback = Decimal(32 * m * sum(H.values())) / Decimal(10**16 * Wlive) if bad else Decimal(0)
        lm = Decimal(m).ln(); lo = Decimal(0); hi = Decimal('.003')
        for _ in range(500):
            a = (lo + hi) / 2
            if sum(p * (a * l).exp() for p, l in terms) + fallback * (a * lm).exp() < 1:
                lo = a
            else:
                hi = a
        return (lo + hi) / 2

res = {}
for name, bad in [('native', False), ('conservative', True)]:
    with localcontext() as c:
        c.prec = 140
        approx = propose(bad)
        q0 = int((approx * Decimal(10**90)).to_integral_value(rounding=ROUND_FLOOR))
    found = None
    for dq in range(-3, 4):
        q = q0 + dq
        lo = Q(q, 10**90); hi = Q(q + 1, 10**90)
        if accepted(lo, bad) and rejected(hi, bad):
            found = q; break
    assert found is not None, f'no 1e-90 bracket near proposal for {name}'
    lo = Q(found, 10**90)
    res[name] = dict(lower=str(lo), lower_dec=float(lo), bracket_width='1e-90')
    print(name, 'lower', str(lo)[:60], '...', flush=True)

spec_p = W / 'pkg' / 'new' / 'SPEC.json'
spec = json.loads(spec_p.read_text())
spec['outer_refinement']['endpoint_digits'] = 90
spec['expected']['complex_lower'] = res['native']['lower']
spec['expected']['conservative_complex_lower'] = res['conservative']['lower']
spec_p.write_text(json.dumps(spec, indent=2) + '\n')
(OUT / 'FINE-ENDPOINTS.json').write_text(json.dumps(res, indent=1) + '\n')
print('SPEC endpoints updated (90 digits)')
