#!/usr/bin/env python3
"""Pattern-LP sweep over k low aliases (screen; paid side modelled).

Reuses scripts/pattern_lp.py's simplex by exec'ing its pattern enumeration
and revised_simplex (the part above the phase-1 driver).  For each k in
0..32, provider role-width totals are per call
{9:240+k, 8:116-k, 7:36, 5:4, 4:36-k} x 666 calls, and paid moment is
modelled as paid48 - 666*k*0.041319 (best-block singles saving/call;
measured joint at k=32 differs from this model by <0.6 units total).
Reports LP idle lower bound and modelled net H moment vs #2269's
66304.55288551617 (which equals the round-1 48-fill H).  Screen only:
paid profiles at intermediate k were not built as words/natives.
Output: PATTERN-LP-K.json.
"""
import json
from pathlib import Path
import numpy as np

OUT = Path('research/muse-t74-borrow-extend')
src = (OUT / 'scripts/pattern_lp.py').read_text()
head = src.split('# phase 1')[0]
# strip the top-level pattern/Amat/bvec construction that depends on ROLES
head = head.replace("ROLES = {9: 181152, 8: 55944, 7: 23976, 5: 2664, 4: 2664}",
                    "ROLES = {9: 181152, 8: 55944, 7: 23976, 5: 2664, 4: 2664}")
g = {}
exec(head, g)
Amat, cost, pats, CAPS, WS = g['Amat'], g['cost'], g['pats'], g['CAPS'], g['WS']
revised = g['revised_simplex']
m, n = Amat.shape

def solve(bvec):
    A1 = np.hstack([Amat, np.eye(m)])
    c1 = np.concatenate([np.zeros(n), np.ones(m)])
    basis1, xB1, _, _ = revised(A1, bvec, c1, list(range(n, n + m)))
    basis = list(basis1)
    for i, j in enumerate(list(basis)):
        if j >= n:
            Binv = np.linalg.inv(A1[:, basis])
            cand = [jj for jj in range(n) if jj not in basis and abs(Binv[i] @ Amat[:, jj]) > 1e-9]
            if cand: basis[i] = cand[0]
    basis, xB, y, _ = revised(Amat, bvec, cost, basis)
    viol = float(np.max(Amat.T @ y - cost))
    assert viol < 1e-6, viol
    return float(cost[basis] @ xB)

PAID48 = 49208.59367361864
H2269 = 66304.55288551617
rows = []
for k in [0, 1, 2, 4, 8, 12, 16, 20, 24, 28, 32]:
    roles = {9: (240 + k) * 666, 8: (116 - k) * 666, 7: 36 * 666, 5: 4 * 666, 4: (36 - k) * 666}
    bvec = np.array([CAPS[c] for c in CAPS] + [roles[w] for w in WS], dtype=float)
    idle = solve(bvec)
    paid = PAID48 - 666 * k * 0.041319
    net = paid + idle - H2269
    rows.append(dict(k=k, idle_lp=idle, paid_model=paid, net_vs_2269=net))
    print(f'k={k:2d} idleLP {idle:.4f} paid {paid:.4f} net vs 2269 {net:+.4f}', flush=True)
(OUT / 'PATTERN-LP-K.json').write_text(json.dumps(
    dict(paid48=PAID48, h2269=H2269, saving_per_alias_call_model=0.041319,
         caveat='Paid moment at intermediate k modelled by singles screen (joint measured error <0.6 at k=32); idle is fractional pattern LP lower bound.',
         rows=rows), indent=1) + '\n')
print('wrote PATTERN-LP-K.json')
