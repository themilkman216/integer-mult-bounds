#!/usr/bin/env python3
"""Cheap falsification screen for porting low/high borrowing to #2322 words.

Question: after applying k low-helper aliases (delete one width-8 role,
widen one width-4 lender role to width 9, paid rank-3 child removed per
call; prior round's measured singles delta on #2269 words) and/or j
remaining high-helper aliases (delete one width-5 role, paid rank-5 child
removed per call; prior round's measured delta) to #2322's provider width
totals, can ANY owner fill in the shipped bin template (caps
{8:49728,16:33152,32:33152,48:33152}) beat #2322's actual total moment
at a2322 = kappa2322/(1-kappa2322)?

Method: fractional bin-pattern LP (1163 patterns) giving a lower bound on
idle moment for every legal fill with the given role totals (windows,
families, chronology and integrality relaxed). Candidate total lower
bound = paid moment (modelled delta) + LP idle optimum. If that bound is
>= #2322's actual total, the scenario is falsified inside this template
scope without building any word. Float64 decision aid; decisive margins
must be exactified separately (see verify.py).

Positive control: with the prior round's 80-provider role totals at
a2269 this script must reproduce PATTERN-LP.json's optimum 17978.923367.

The two-phase revised simplex below is adapted from the prior round's
research/prior-muse-t74-borrow-extend/scripts/pattern_lp.py (Meta Muse,
muse-wonder-full-1.0), generalised to arbitrary role totals / a.
Output: SCREEN-LP.json in this package.
"""
import json
from pathlib import Path
import numpy as np

PKG = Path(__file__).resolve().parent.parent
WS = Path(__file__).resolve().parents[3]
SRC2322 = WS / 'research/t74-joint-owner-hillclimb'

K2322 = 1697060296258836 / 10**18
A2322 = K2322 / (1 - K2322)
K2269 = 0.0016962471390584742
A2269 = K2269 / (1 - K2269)
CALLS = 666
CAPS = {8: 49728, 16: 33152, 32: 33152, 48: 33152}
WIDTHS = [9, 8, 7, 5, 4]

def f(r, a):
    return (r / 73) ** (1 - a) if r else 0.0

# ---- load and cross-check #2322 base facts from three independent files
constr = json.load(open(SRC2322 / 'data/CONSTRUCTION.json'))
profile = {int(k): v for k, v in json.load(open(SRC2322 / 'data/PROFILE.json')).items()}
idle = {int(k): v for k, v in constr['idle'].items()}
paid_call = {1: 2335, 2: 512, 3: 426, 4: 120, 5: 38, 8: 8}   # word report, both providers
width_call = {9: 240, 8: 114, 7: 38, 5: 9, 4: 33}           # word report width_inventory
assert constr['roles'] == CALLS * sum(width_call.values()) == 289044
recon = dict(idle)
for r, n in paid_call.items():
    recon[r] = recon.get(r, 0) + CALLS * n
assert recon == profile, 'paid+idle != global profile'
roles0 = {w: CALLS * n for w, n in width_call.items()}
cap_mass = sum(c * n for c, n in CAPS.items())
width_mass = sum(w * n for w, n in roles0.items())
idle_mass = sum(r * n for r, n in idle.items())
assert width_mass + idle_mass == cap_mass == 3580416, 'cap mass identity fails'
paid_moment0 = CALLS * sum(f(r, A2322) * n for r, n in paid_call.items())
idle_moment0 = sum(f(r, A2322) * n for r, n in idle.items())
total0 = paid_moment0 + idle_moment0
print(f'#2322 actual: paid {paid_moment0:.4f} idle {idle_moment0:.4f} total {total0:.4f} (live 66304)')

# ---- pattern enumeration (caps x width multisets)
pats = []
for cap in CAPS:
    for a in range(cap // 9 + 1):
        for b in range((cap - 9 * a) // 8 + 1):
            for c_ in range((cap - 9 * a - 8 * b) // 7 + 1):
                for d in range((cap - 9 * a - 8 * b - 7 * c_) // 5 + 1):
                    for e in range((cap - 9 * a - 8 * b - 7 * c_ - 5 * d) // 4 + 1):
                        pats.append((cap, (a, b, c_, d, e)))
print('patterns', len(pats))
cap_list = list(CAPS)
cap_idx = {c: i for i, c in enumerate(cap_list)}

def build(roles, a):
    n = len(pats)
    Amat = np.zeros((9, n)); cost = np.zeros(n)
    for j, (cap, cnt) in enumerate(pats):
        Amat[cap_idx[cap], j] = 1
        for wi in range(5):
            Amat[4 + wi, j] = cnt[wi]
        cost[j] = f(cap - sum(w * x for w, x in zip(WIDTHS, cnt)), a)
    bvec = np.array([CAPS[c] for c in cap_list] + [roles[w] for w in WIDTHS], dtype=float)
    return Amat, bvec, cost

def revised_simplex(Amat, bvec, cost, basis):
    m, n = Amat.shape
    basis = list(basis)
    for it in range(200000):
        B = Amat[:, basis]
        xB = np.linalg.solve(B, bvec)
        if (xB < -1e-7).any():
            raise RuntimeError(f'infeasible basis at iter {it}: {xB.min()}')
        y = np.linalg.solve(B.T, cost[basis])
        red = cost - Amat.T @ y
        bset = set(basis)
        enter = next((j for j in range(n) if j not in bset and red[j] < -1e-9), None)
        if enter is None:
            return basis, xB, y, it
        d = np.linalg.solve(B, Amat[:, enter])
        if (d <= 1e-12).all():
            raise RuntimeError('unbounded')
        ratios = [(xB[i] / d[i], basis[i], i) for i in range(m) if d[i] > 1e-12]
        basis[min(ratios)[2]] = enter
    raise RuntimeError('iteration limit')

def solve_lp(roles, a):
    Amat, bvec, cost = build(roles, a)
    m, n = Amat.shape
    A1 = np.hstack([Amat, np.eye(m)])
    c1 = np.concatenate([np.zeros(n), np.ones(m)])
    basis1, xB1, _, _ = revised_simplex(A1, bvec, c1, list(range(n, n + m)))
    art = sum(xB1[i] for i, j in enumerate(basis1) if j >= n)
    assert art < 1e-6, f'LP infeasible (artificial {art})'
    basis = list(basis1)
    for i, j in enumerate(list(basis)):
        if j >= n:
            Binv = np.linalg.inv(A1[:, basis])
            cand = [jj for jj in range(n) if jj not in basis and abs(Binv[i] @ Amat[:, jj]) > 1e-9]
            if cand:
                basis[i] = cand[0]
    assert all(j < n for j in basis), 'artificial stuck'
    basis, xB, y, _ = revised_simplex(Amat, bvec, cost, basis)
    obj = float(cost[basis] @ xB)
    viol = float(np.max(Amat.T @ y - cost))
    support = {}
    for i, j in enumerate(basis):
        if xB[i] > 1e-6:
            cap, cnt = pats[j]
            ws = tuple(w for w, x in zip(WIDTHS, cnt) for _ in range(x))
            support[f'{cap}:{list(ws)}'] = float(xB[i])
    duals = dict(bins={str(c): float(y[i]) for i, c in enumerate(cap_list)},
                 roles={str(w): float(y[4 + i]) for i, w in enumerate(WIDTHS)})
    return obj, viol, duals, support

# ---- positive control: prior round's 80-provider LP at a2269
ctl_roles = {9: 181152, 8: 55944, 7: 23976, 5: 2664, 4: 2664}
ctl, ctl_viol, _, _ = solve_lp(ctl_roles, A2269)
print(f'control prior-80 LP {ctl:.6f} (published 17978.923367, viol {ctl_viol:.2e})')
assert abs(ctl - 17978.923367) < 1e-3, 'positive control failed'

def scenario(name, nlow, nhigh):
    roles = dict(roles0)
    roles[9] += CALLS * nlow
    roles[8] -= CALLS * nlow
    roles[4] -= CALLS * nlow
    roles[5] -= CALLS * nhigh
    assert all(v >= 0 for v in roles.values()), roles
    paid = paid_moment0 - CALLS * nlow * f(3, A2322) - CALLS * nhigh * f(5, A2322)
    obj, viol, duals, support = solve_lp(roles, A2322)
    tot = paid + obj
    print(f'{name:34s} paid {paid:10.4f} idleLP {obj:10.4f} totalLB {tot:10.4f} '
          f'vs actual {tot - total0:+.4f} viol {viol:.1e}')
    return dict(name=name, nlow=nlow, nhigh=nhigh, roles={str(k): v for k, v in roles.items()},
                paid_model=paid, idle_lp=obj, total_lb=tot, margin_vs_actual=tot - total0,
                dual_max_violation=viol, duals=duals, support=support)

rows = []
base = scenario('base #2322 widths (LP gap check)', 0, 0)
print(f'  LP gap at base: actual idle - LP idle = {idle_moment0 - base["idle_lp"]:+.4f}')
rows.append(base)
for k in [1, 2, 4, 8, 16, 24, 32]:
    rows.append(scenario(f'low x{k}', k, 0))
for j in [1, 2, 3, 6]:
    rows.append(scenario(f'high x{j}', 0, j))
rows.append(scenario('low x32 + high x6', 32, 6))
rows.append(scenario('low x1 + high x6', 1, 6))
rows.append(scenario('low x4 + high x6', 4, 6))

def scenario_custom(name, role_delta_call, paid_delta_call):
    """Measured stage-P deltas (STAGEP-SINGLES.json) applied to #2322 totals."""
    roles = {w: roles0[w] + CALLS * role_delta_call.get(w, 0) for w in WIDTHS}
    assert all(v >= 0 for v in roles.values()), roles
    paid = paid_moment0 + CALLS * sum(f(r, A2322) * d for r, d in paid_delta_call.items())
    obj, viol, duals, support = solve_lp(roles, A2322)
    tot = paid + obj
    print(f'{name:34s} paid {paid:10.4f} idleLP {obj:10.4f} totalLB {tot:10.4f} '
          f'vs actual {tot - total0:+.4f} viol {viol:.1e}')
    return dict(name=name, nlow=None, nhigh=None,
                roles={str(k): v for k, v in roles.items()},
                role_delta_per_call={str(k): v for k, v in role_delta_call.items()},
                paid_delta_per_call={str(k): v for k, v in paid_delta_call.items()},
                paid_model=paid, idle_lp=obj, total_lb=tot, margin_vs_actual=tot - total0,
                dual_max_violation=viol, duals=duals, support=support)

rows.append(scenario_custom('653 re-alias (measured stage-P)',
                            {4: -1, 7: -1, 8: 1}, {3: -1}))
rows.append(scenario_custom('low624 class x1 (measured stage-P)',
                            {9: 1, 8: -1, 4: -1}, {1: 1, 4: -1}))
rows.append(scenario('high x9 (all width-5)', 0, 9))  # 9 live width-5 highs exist

out = dict(
    kappa2322=K2322, a2322=A2322, calls=CALLS, caps={str(k): v for k, v in CAPS.items()},
    base_roles={str(k): v for k, v in roles0.items()},
    actual_paid_moment=paid_moment0, actual_idle_moment=idle_moment0, actual_total=total0,
    control_prior80_lp=ctl, control_published=17978.923367,
    paid_delta_model='low: -f(3) per alias-call (prior singles screen); high: -f(5) per alias-call (prior round-1 measured)',
    width_delta_model='low: width9 +1, width8 -1, width4 -1 per alias-call; high: width5 -1 per alias-call (prior measured audits)',
    caveat='Float64 fractional pattern LP; paid/width deltas are prior-word measurements used as screen hypotheses for #2322 words, not #2322 audits. total_lb >= actual_total falsifies the scenario inside this bin template; total_lb < actual_total is not a construction.',
    rows=rows)
(PKG / 'SCREEN-LP.json').write_text(json.dumps(out, indent=1) + '\n')
print('wrote SCREEN-LP.json')
