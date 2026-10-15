#!/usr/bin/env python3
"""Exact LP relaxation (fractional pattern counts) for the 80-fill idles.

Variables: one per bin pattern (cap, multiset of role widths), enumerated
exhaustively for caps {8,16,32,48} and widths {9,8,7,5,4}.  Constraints:
bins per cap and roles per width (totals for the 400-helper providers).
Objective: idle moment at a2269.  Solved by a two-phase revised simplex
(9 constraints) in numpy; the optimal dual variables are verified against
ALL patterns in-script (dual objective = primal, all dual constraints
hold to printed tolerance).  Because windows/families and integrality are
relaxed, the optimum is a lower bound for every legal fill with these
provider widths.  Float64 decision aid, not an exact-rational proof.
Output: PATTERN-LP.json.
"""
import itertools, json
from pathlib import Path
import numpy as np

OUT = Path('research/muse-t74-borrow-extend')
K = 0.0016962471390584742; A = K / (1 - K)
def F(r): return (r / 73) ** (1 - A) if r else 0.0

CAPS = {8: 49728, 16: 33152, 32: 33152, 48: 33152}
ROLES = {9: 181152, 8: 55944, 7: 23976, 5: 2664, 4: 2664}
WS = [9, 8, 7, 5, 4]

pats = []   # (cap, counts tuple over WS)
for cap in CAPS:
    for a in range(cap // 9 + 1):
        for b in range((cap - 9 * a) // 8 + 1):
            for c_ in range((cap - 9 * a - 8 * b) // 7 + 1):
                for d in range((cap - 9 * a - 8 * b - 7 * c_) // 5 + 1):
                    for e in range((cap - 9 * a - 8 * b - 7 * c_ - 5 * d) // 4 + 1):
                        pats.append((cap, (a, b, c_, d, e)))
print('patterns', len(pats))
m, n = 9, len(pats)
Amat = np.zeros((m, n)); cost = np.zeros(n)
cap_idx = {c: i for i, c in enumerate(CAPS)}
for j, (cap, cnt) in enumerate(pats):
    Amat[cap_idx[cap], j] = 1
    for wi, w in enumerate(WS):
        Amat[4 + wi, j] = cnt[wi]
    cost[j] = F(cap - sum(w * x for w, x in zip(WS, cnt)))
bvec = np.array([CAPS[c] for c in CAPS] + [ROLES[w] for w in WS], dtype=float)

def revised_simplex(Amat, bvec, cost, basis):
    """Min cost x s.t. Ax=b, x>=0 from a feasible basis. Returns (basis, xB)."""
    m, n = Amat.shape
    basis = list(basis)
    for it in range(200000):
        B = Amat[:, basis]
        xB = np.linalg.solve(B, bvec)
        if (xB < -1e-7).any(): raise RuntimeError(f'infeasible basis at iter {it}: {xB.min()}')
        y = np.linalg.solve(B.T, cost[basis])
        red = cost - Amat.T @ y
        nonb = [j for j in range(n) if j not in set(basis)]
        enter = next((j for j in nonb if red[j] < -1e-9), None)  # Bland
        if enter is None: return basis, xB, y, it
        d = np.linalg.solve(B, Amat[:, enter])
        if (d <= 1e-12).all(): raise RuntimeError('unbounded')
        ratios = [(xB[i] / d[i], basis[i], i) for i in range(m) if d[i] > 1e-12]
        leave = min(ratios)[2]   # Bland on ties via basis var order in tuple
        basis[leave] = enter
    raise RuntimeError('iteration limit')

# phase 1: artificial variables
A1 = np.hstack([Amat, np.eye(m)])
c1 = np.concatenate([np.zeros(n), np.ones(m)])
basis1, xB1, _, it1 = revised_simplex(A1, bvec, c1, list(range(n, n + m)))
art = sum(xB1[i] for i, j in enumerate(basis1) if j >= n)
print(f'phase1 iters {it1} artificial sum {art:.3e}')
assert art < 1e-6, 'LP infeasible'
basis = [j for j in basis1]
# drive any zero artificials out of the basis
for i, j in enumerate(list(basis)):
    if j >= n:
        B = Amat[:, [x if x < n else -1 for x in basis]] if False else None
        # find a non-artificial column with nonzero pivot in this row of B^{-1}A
        Bfull = A1[:, basis]
        Binv = np.linalg.inv(Bfull)
        cand = [jj for jj in range(n) if jj not in basis and abs((Binv[i] @ Amat[:, jj])) > 1e-9]
        if cand: basis[i] = cand[0]
assert all(j < n for j in basis), 'artificial stuck (dependent rows?)'
basis, xB, y, it2 = revised_simplex(Amat, bvec, cost, basis)
obj = float(cost[basis] @ xB)
dual_obj = float(bvec @ y)
viol = float(np.max(Amat.T @ y - cost))
print(f'phase2 iters {it2} LP optimum {obj:.6f} dual {dual_obj:.6f} max dual violation {viol:.3e}')
sol = {}
for i, j in enumerate(basis):
    if xB[i] > 1e-6:
        cap, cnt = pats[j]
        ws = tuple(w for w, x in zip(WS, cnt) for _ in range(x))
        sol[f'{cap}:{list(ws)}'] = float(xB[i])
print('support', sol)
budget = 17977.06775088235
out = dict(patterns=len(pats), lp_optimum=obj, dual_objective=dual_obj,
           dual_max_violation=viol, budget=budget, margin=budget - obj,
           dual_variables=dict(bins={str(c): float(y[i]) for i, c in enumerate(CAPS)},
                               roles={str(w): float(y[4 + i]) for i, w in enumerate(WS)}),
           support=sol,
           caveat='Fractional pattern-count LP lower bound (windows/families/integrality relaxed), float64 revised simplex; dual feasibility over all enumerated patterns printed as max violation.')
(OUT / 'PATTERN-LP.json').write_text(json.dumps(out, indent=1) + '\n')
print('margin', out['margin'])
