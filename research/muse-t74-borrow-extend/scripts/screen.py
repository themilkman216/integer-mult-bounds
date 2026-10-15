#!/usr/bin/env python3
"""Exact-interval price screen for extended borrowing on the T74 words.

Prices paid local profiles with the pinned engine
research/complex-local-word-ceiling/ceiling.py (Douglas Colkitt) at the T74
template (m=73, 896 families / 9 stages, centre 64, unpaid 1). Ceilings are
favourable relaxations (fractional idle packing at rank R=51); the exact
moment of a completed construction remains the acceptance test.

Profiles: unborrowed 566+554 words, #2269 borrow43 words (audited), and
projections for +5 high aliases and +5 high + N low aliases under two
per-alias saving models bracketed from observed deltas:
  model A (favourable): each extra alias removes one rank-5 child;
  model B (conservative): each extra alias removes one rank-4 child.
Also prices the #2226 selected-word 80-alias profile as a cross-check.
"""
import hashlib, json, sys, time
from fractions import Fraction as Q
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / 'research/complex-local-word-ceiling'))
import ceiling  # noqa: E402

M, FAM, ST, CEN = 73, 896, 9, 64
GRID = Q(1, 10**12)

def P(d): return {int(k): v for k, v in d.items()}
def mass(p): return sum(r * n for r, n in p.items())

UNB_BASE = P({'1': 2348, '2': 500, '3': 416, '4': 130, '5': 82, '8': 8})   # 5590
UNB_EXTRA = P({'1': 2340, '2': 508, '3': 420, '4': 126, '5': 82, '8': 8})  # 5594
B43_BASE = P({'1': 2351, '2': 501, '3': 414, '4': 129, '5': 42, '8': 8})   # 5385
B43_EXTRA = P({'1': 2339, '2': 509, '3': 418, '4': 125, '5': 42, '8': 8})  # 5385
SEL80 = P({'1': 2382, '2': 445, '3': 406, '4': 128, '5': 42, '8': 8})      # 5276 (#2226)

def project(base, n_extra, rank):
    p = dict(base)
    left = n_extra
    for r in (rank, 4, 3, 2, 1):  # fall back to lower ranks if rank exhausted
        take = min(left, p.get(r, 0))
        p[r] -= take; left -= take
        if left == 0: break
    assert left == 0
    return p

K2269 = Q(16962471390584742, 10**19)  # 0.0016962471390584742 truncated
A2269 = K2269 / (1 - K2269)
ABIT = Q(1733427039589844234749, 10**24)  # bit endpoint c (PRICE.json outer.bit_c ~0.00173342703959)

def price(name, prof):
    t = time.monotonic()
    lo, hi = ceiling.ceiling(prof, M, FAM, ST, CEN, grid=GRID)
    r2269 = ceiling.relax(prof, M, FAM, ST, CEN, A2269)
    rbit = ceiling.relax(prof, M, FAM, ST, CEN, ABIT)
    row = dict(name=name, profile={str(k): v for k, v in sorted(prof.items())},
               mass=mass(prof), a_lo=str(lo), a_hi=str(hi),
               a_hi_dec=float(hi), kappa_hi_dec=float(hi / (1 + hi)),
               relax_at_a2269=[str(x) for x in r2269],
               relax_at_a2269_dec=[float(x) for x in r2269],
               relax_at_abit_dec=[float(x) for x in rbit],
               seconds=time.monotonic() - t)
    print(f"{name:34s} mass={mass(prof)} a_hi={float(hi):.12f} "
          f"k_hi={float(hi/(1+hi)):.12f} relax(a2269)={float(r2269[1]):.6f} "
          f"relax(abit)={float(rbit[1]):.6f}", flush=True)
    return row

rows = []
rows.append(price('unborrowed base (5590)', UNB_BASE))
rows.append(price('unborrowed extra (5594)', UNB_EXTRA))
rows.append(price('#2269 borrow43 base', B43_BASE))
rows.append(price('#2269 borrow43 extra', B43_EXTRA))
rows.append(price('#2226 selected 80-alias (xcheck)', SEL80))
for extra, tag in [(5, '+5 high (48 total)'), (13, '+5h+8 low'), (21, '+5h+16 low'),
                   (29, '+5h+24 low'), (37, '+5h+32 low (80 total)')]:
    rows.append(price(f'base {tag} modelA r5', project(B43_BASE, extra, 5)))
    rows.append(price(f'base {tag} modelB r4', project(B43_BASE, extra, 4)))

# tamper/self-control: one extra rank-1 child must strictly lower a_hi
t = dict(B43_BASE); t[1] += 1
_, hi_t = ceiling.ceiling(t, M, FAM, ST, CEN, grid=GRID)
base_hi = Q(rows[2]['a_hi'])
mono = hi_t < base_hi
print('monotonicity control (+1 rank-1 lowers a_hi):', mono, float(hi_t), flush=True)
assert mono

out = dict(status='PASS_MUSE_T74_BORROW_EXTEND_SCREEN',
           engine='research/complex-local-word-ceiling/ceiling.py',
           engine_sha256=hashlib.sha256(
               (ROOT / 'research/complex-local-word-ceiling/ceiling.py').read_bytes()).hexdigest(),
           template=dict(m=M, families=FAM, stages=ST, centre=CEN, unpaid=1, grid=str(GRID)),
           a2269=str(A2269), a2269_dec=float(A2269), abit_dec=float(ABIT),
           kappa_bit_wall_dec=float(ABIT / (1 + ABIT)),
           monotonicity_control=bool(mono), rows=rows)
p = Path(__file__).resolve().parent.parent / 'SCREEN.json'
p.write_text(json.dumps(out, indent=1) + '\n')
print('wrote', p)
